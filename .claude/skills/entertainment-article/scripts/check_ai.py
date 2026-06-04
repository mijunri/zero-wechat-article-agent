#!/usr/bin/env python3
"""
AI浓度检测脚本
用法：
    python scripts/check_ai.py output/xxx.html
    python scripts/check_ai.py output/xxx.html --local  # 强制用本地规则检测

依赖：
    pip install tencentcloud-sdk-python

环境变量（可选，不设置则只用本地检测）：
    TENCENT_SECRET_ID
    TENCENT_SECRET_KEY
"""

import re
import sys
import os
import base64
import argparse

# ─────────────────────────────────────────
# 正文提取
# ─────────────────────────────────────────

def extract_text(html_file: str) -> str:
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    # 去掉 script / style
    html = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL)
    # 去掉 HTML 标签
    text = re.sub(r"<[^>]+>", "", html)
    # 压缩空白
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_chinese(text: str) -> int:
    # 统计中文字符+中文标点，与历史基准一致
    return len(re.findall(r'[\u4e00-\u9fff，。！？、：；""''「」【】《》…—]', text))


# ─────────────────────────────────────────
# 本地规则检测（备用方案）
# ─────────────────────────────────────────

# AI常用句式特征，每条命中+1分
AI_PATTERNS = [
    # 对仗句式
    (r"不是.{1,36}(，|,)?\s*(而是|是)", "禁止：不是…而是/不是…是"),
    # 虚词
    (r"本质上", "AI虚词「本质上」"),
    (r"归根结底", "AI虚词「归根结底」"),
    (r"值得注意的是", "AI虚词「值得注意的是」"),
    (r"从某种意义上", "AI虚词「从某种意义上」"),
    (r"不得不说", "AI虚词「不得不说」"),
    (r"毋庸置疑", "AI虚词「毋庸置疑」"),
    (r"显而易见", "AI虚词「显而易见」"),
    (r"综上所述", "AI虚词「综上所述」"),
    (r"总的来说", "AI虚词「总的来说」"),
    (r"由此可见", "AI虚词「由此可见」"),
    # 升华句式
    (r"这(背后|说明|意味着|代表着)", "升华句式「这意味着/说明」"),
    (r"折射出", "升华句式「折射出」"),
    (r"深层次(原因|逻辑)", "升华句式「深层次原因」"),
    # 模糊表达
    (r"部分(人|创始人|用户|网友).{0,5}(逐渐|开始|慢慢)", "模糊表达「部分…逐渐」"),
    (r"一定程度上", "模糊表达「一定程度上」"),
    # AI腔引导句
    (r"但(很少有人|鲜有人)(知道|认真|想过)", "AI引导句「但很少有人知道」"),
    (r"大家(都|往往)(忽略了|忽视了|没有注意到)", "AI引导句「大家都忽略了」"),
    # 时间巧合制造戏剧感
    (r"同一(天|年|时间)[，,].{0,20}(也|同样)", "时间巧合句「同一天…也」"),
    # 新闻通稿用语
    (r"正式落幕", "通稿用语「正式落幕」"),
    (r"宣告(结束|落幕|终结)", "通稿用语「宣告结束」"),
    # 排比收束
    (r"(如此|亦如此|也如此)[。，]", "排比收束「如此/亦如此」"),
    # 口号体堆叠（连续两个以上感叹句）
    (r"[！!][^！!。\n]{0,30}[！!][^！!。\n]{0,30}[！!]", "连续感叹号堆叠"),
]

def local_check(text: str) -> dict:
    """基于规则的本地AI特征检测，返回分数和命中列表"""
    hits = []
    for pattern, label in AI_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            hits.append({"label": label, "count": len(matches)})

    total_patterns = len(AI_PATTERNS)
    hit_count = len(hits)
    # 粗略估算：命中比例映射到0-100分
    # 命中0条 → 0分（很干净），命中10条以上 → 80分以上（很重）
    raw_score = min(hit_count / 10, 1.0) * 80
    # 加粗数量也是信号
    bold_count = len(re.findall(r"<strong>", open.__doc__ or ""))  # 占位，实际在调用层传入

    return {
        "method": "local_rules",
        "ai_score": round(raw_score),
        "hit_count": hit_count,
        "total_patterns": total_patterns,
        "hits": hits,
    }


def local_check_html(html_file: str) -> dict:
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    text = extract_text(html_file)
    bold_count = len(re.findall(r"<strong>", html))
    # 字数统计用去标签后的原始文本（不压缩空白），与历史基准一致
    html_no_script = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)
    raw_text = re.sub(r"<[^>]+>", "", html_no_script)

    hits = []
    for pattern, label in AI_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            hits.append({"label": label, "count": len(matches)})

    hit_count = len(hits)
    raw_score = min(hit_count / 10, 1.0) * 80

    return {
        "method": "local_rules",
        "ai_score": round(raw_score),
        "hit_count": hit_count,
        "total_patterns": len(AI_PATTERNS),
        "hits": hits,
        "bold_count": bold_count,
        "raw_char_count": count_chinese(raw_text),
    }


# ─────────────────────────────────────────
# 腾讯云 TMS 检测
# ─────────────────────────────────────────

def tencent_check(text: str, secret_id: str, secret_key: str) -> dict:
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.tms.v20201229 import tms_client, models

        # TMS 单次最大 10000 UTF-8 字符，超出截断
        MAX_LEN = 9000
        if len(text.encode("utf-8")) > MAX_LEN:
            # 按字节截断到安全长度
            encoded = text.encode("utf-8")[:MAX_LEN]
            text = encoded.decode("utf-8", errors="ignore")

        cred = credential.Credential(secret_id, secret_key)
        client = tms_client.TmsClient(cred, "ap-guangzhou")

        req = models.TextModerationRequest()
        req.Content = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        req.BizType = ""

        resp = client.TextModeration(req)

        # Suggestion: Pass / Review / Block
        suggestion = resp.Suggestion
        label = resp.Label

        # 映射到0-100分（粗略）
        score_map = {"Pass": 10, "Review": 50, "Block": 85}
        ai_score = score_map.get(suggestion, 50)

        return {
            "method": "tencent_tms",
            "ai_score": ai_score,
            "suggestion": suggestion,
            "label": label,
            "raw": resp.to_json_string(),
        }

    except ImportError:
        return {"method": "tencent_tms", "error": "tencentcloud SDK未安装，运行: pip install tencentcloud-sdk-python"}
    except Exception as e:
        return {"method": "tencent_tms", "error": str(e)}


# ─────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────

def check(html_file: str, force_local: bool = False) -> dict:
    if not os.path.exists(html_file):
        return {"error": f"文件不存在: {html_file}"}

    text = extract_text(html_file)
    char_count = count_chinese(text)

    # 本地规则检测（始终运行）
    local_result = local_check_html(html_file)

    result = {
        "file": html_file,
        "char_count": local_result.get("raw_char_count", char_count),
        "local": local_result,
        "tencent": None,
    }

    # 腾讯云检测（有key且未强制本地时运行）
    secret_id = os.environ.get("TENCENT_SECRET_ID", "")
    secret_key = os.environ.get("TENCENT_SECRET_KEY", "")

    if not force_local and secret_id and secret_key:
        result["tencent"] = tencent_check(text, secret_id, secret_key)

    return result


def print_report(result: dict):
    print("=" * 55)
    print(f"文件：{result['file']}")
    print(f"字数：{result['char_count']} 字")
    print("=" * 55)

    # 本地规则
    local = result["local"]
    print(f"\n【本地规则检测】")
    print(f"AI特征命中：{local['hit_count']}/{local['total_patterns']} 条")
    print(f"估算AI分：{local['ai_score']}/100  {'✓ 较干净' if local['ai_score'] < 30 else '⚠ 需注意' if local['ai_score'] < 60 else '✗ AI味较重'}")
    if local.get("bold_count") is not None:
        bold = local["bold_count"]
        print(f"加粗数量：{bold}  {'✓' if bold <= 6 else '✗ 超出6处'}")
    if local["hits"]:
        print("\n命中的AI特征：")
        for h in local["hits"]:
            print(f"  · {h['label']}（出现 {h['count']} 次）")

    # 腾讯云
    if result["tencent"]:
        tc = result["tencent"]
        print(f"\n【腾讯云TMS检测】")
        if "error" in tc:
            print(f"  ✗ 调用失败: {tc['error']}")
        else:
            print(f"  判定结果：{tc['suggestion']}  （Pass=通过 / Review=复审 / Block=拦截）")
            print(f"  标签：{tc['label']}")
            print(f"  AI浓度估算：{tc['ai_score']}/100")
    else:
        print(f"\n【腾讯云TMS检测】未配置（设置环境变量 TENCENT_SECRET_ID / TENCENT_SECRET_KEY 后启用）")

    # 综合结论
    print("\n" + "=" * 55)
    ai_score = result["tencent"]["ai_score"] if (result["tencent"] and "ai_score" in result["tencent"] and "error" not in result["tencent"]) else local["ai_score"]
    char_ok = result["char_count"] >= 3000

    print("【综合结论】")
    char_status = "✓ 达标" if char_ok else f"✗ 不足（当前{result['char_count']}字，需≥3000字）"
    print(f"  字数：{char_status}")
    if ai_score <= 20:
        print(f"  AI浓度：✓ 安全（{ai_score}/100）")
    elif ai_score <= 50:
        print(f"  AI浓度：⚠ 偏高（{ai_score}/100），建议再做一轮去AI味")
    else:
        print(f"  AI浓度：✗ 超标（{ai_score}/100），必须重做去AI味再发布")

    if char_ok and ai_score <= 20:
        print("\n  ✅ 可以发布")
    elif char_ok and ai_score <= 50:
        print("\n  ⚠️  建议改完再发")
    else:
        print("\n  🚫 不建议发布，请先处理上述问题")
    print("=" * 55)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="公众号文章AI浓度检测")
    parser.add_argument("file", help="HTML文件路径，如 output/xxx.html")
    parser.add_argument("--local", action="store_true", help="强制使用本地规则检测（不调用腾讯云）")
    args = parser.parse_args()

    result = check(args.file, force_local=args.local)
    if "error" in result:
        print(f"错误：{result['error']}")
        sys.exit(1)
    print_report(result)
