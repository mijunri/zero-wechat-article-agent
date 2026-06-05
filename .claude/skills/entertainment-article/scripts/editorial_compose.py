#!/usr/bin/env python3
"""
Editorial — 活人感吃瓜口吻：短句、口语、有梗；不要论文腔和互动问卷。

支持特定话题深度内容 + 通用话题 fallback 内容生成。
"""
from __future__ import annotations

import re
from typing import Any

from de_ai_polish import polish
from human_voice import humanize
from meme_harvest import fallback_memes


def _say(text: str) -> str:
    return polish(humanize(text))


def pick_angle(hot_title: str, person: str, kind: str) -> str:
    """选择内容角度."""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return "誓词里没穷字，但有钱人的浪漫和穷人的模板不是一套"
    # 通用角度：基于热搜标题
    if "官宣" in hot_title:
        return "官宣这事儿，终于来了"
    if "争议" in hot_title:
        return "这事儿，有点意思"
    if "恋情" in hot_title or "分手" in hot_title:
        return "感情这事儿，外人说不好"
    return hot_title[:12]


def hook_opening(person: str, hot_title: str, memes: list[str]) -> str:
    """开头钩子."""
    if "贫穷" in hot_title or "誓词" in hot_title:
        lines = format_meme_lines(memes, hot_title, max_items=1)
        meme_bit = ""
        if lines:
            meme_bit = f"网友已经总结好了：{lines[0]}。"
        return _say(
            f"{person}婚礼誓词我扫了一眼，整段没「贫穷」俩字。"
            f"甜可能有，但听着偏硬，那股阶层味儿藏不住。"
            f"{meme_bit}"
        )
    # 通用开头
    if "官宣" in hot_title:
        return _say(f"{hot_title}这事儿，终于有准信了。")
    if "恋情" in hot_title or "分手" in hot_title:
        return _say(f"{hot_title}这事儿，瓜不大，但话头够损。")
    if "争议" in hot_title:
        return _say(f"{hot_title}这事儿，换个角度看。")
    return _say(f"「{hot_title}」这事儿，有点意思。")


def write_event_narrative(person: str, hot_title: str, kind: str, bundle: dict[str, Any] | None = None) -> list[str]:
    """事件叙述：基于调研数据生成."""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            _say(
                f"{person}跟奚梦瑶在法国补办婚礼。"
                f"誓词那块，别人念「无论贫穷还是富贵、疾病还是健康」，"
                f"他改成「无论顺境还是低谷，热闹还是安静」。"
                f"你琢磨一下：一个聊的是油盐酱醋，一个聊的是心情和排场。"
            ),
            _say(
                f"后面大段在回答「你为什么爱我」，夸老婆是自己拼出来的，"
                f"少写「我养你」那种霸总句。"
                f"听得人一边觉得甜，一边想：行，穷字你是一字不提啊。"
            ),
        ]
    # 通用事件叙述：从 facts 提取
    if not bundle:
        return [_say(f"{person}这事儿，换个角度捋一捋。")]

    facts = bundle.get("facts") or []
    if not facts:
        return [_say(f"{person}这事儿，换个角度捋一捋。")]

    # 从 facts 中提取关键信息生成叙述
    result = []
    for fact in facts[:3]:  # 取前3条事实
        fact = fact.strip()
        if len(fact) < 20:
            continue
        # 清理过长的句子
        if len(fact) > 200:
            fact = fact[:200] + "..."
        result.append(_say(fact))

    if result:
        return result[:2]  # 最多返回2段
    return [_say(f"{person}这事儿，换个角度捋一捋。")]


def format_meme_lines(memes: list[str], hot_title: str, *, max_items: int = 6) -> list[str]:
    """格式化网友评论."""
    if "贫穷" in hot_title or "誓词" in hot_title:
        pool = fallback_memes(hot_title)
    else:
        pool = []
        for m in memes or []:
            m = re.sub(r"&#\d+;|🌟", "", m).strip()
            if 10 <= len(m) <= 44 and "引发" not in m and "热议" not in m:
                pool.append(m)
        pool.extend(fallback_memes(hot_title))
    lines: list[str] = []
    for m in pool[:max_items]:
        punch = m.rstrip("。！？").strip()
        if punch:
            lines.append(punch if punch.startswith("「") else f"「{punch}」")
    return lines


def write_meme_section(memes: list[str], hot_title: str, bundle: dict[str, Any] | None = None) -> tuple[str, list[str], str | None]:
    """网友评论 section."""
    # 如果 bundle 有 quotes，优先使用
    if bundle:
        quotes = bundle.get("quotes") or []
        if quotes:
            pool = []
            for q in quotes[:5]:
                q = q.strip()
                # 过滤掉作者信息
                if "本文作者：" in q or len(q) < 10:
                    continue
                if len(q) > 60:
                    q = q[:60] + "..."
                pool.append(q)
            if pool:
                paras = [f"· {q}" for q in pool[:3]]
                return "网友怎么说", paras, _say("摘录几条网友的评论：")

    # fallback
    items = format_meme_lines(memes, hot_title)
    if items:
        intro = _say("摘录几条反复复读的：")
        paras = [f"· {item}" for item in items]
        return "网友怎么看的", paras, intro
    return "", [], None


def write_punchline(person: str, hot_title: str, kind: str, event_facts: list[str]) -> list[str]:
    """观点输出."""
    if "贫穷" in hot_title or "誓词" in hot_title:
        return [
            _say(
                f"说白了，普通人誓词里写「贫穷」，是怕以后得一块儿扛事儿。"
                f"{person}写顺境低谷，没想着恶心谁，「穷」压根不在他的人生选项里。"
                f"你让他硬念那俩字，比让他背早鸟票还别扭。"
            ),
            _say(
                f"他把「疾病还是健康」也换成了「热闹还是安静」。"
                f"听着像文艺，其实就是：我俩的日子，不太会出现你只能在家喝粥那种剧情。"
            ),
            _say(
                f"还有个小彩蛋：奚梦瑶当年用「谢谢」回他的「我爱你」。"
                f"有人觉得克制，有人觉得像商务回复。"
                f"他俩一直就这么说话，誓词不过是又让人看见了一回。"
            ),
        ]

    # 通用观点
    results = []
    if event_facts:
        # 从 facts 中提取最后一部分作为观点素材
        for fact in event_facts[-2:]:
            fact = fact.strip()
            if len(fact) > 30:
                results.append(_say(f"说句实话，{fact[:100]}..."))
                break

    if not results:
        results.append(_say(f"{person}这事儿，最后留人的，常常是那句话怎么被读。"))
    return results


def closing_line(person: str, hot_title: str) -> str:
    """收尾."""
    if "贫穷" in hot_title:
        return _say("婚礼会结束，这句誓词八成还能当梗用好一阵。")
    if "官宣" in hot_title:
        return _say("官宣了，后续还得看物料和正片。")
    if "恋情" in hot_title or "分手" in hot_title:
        return _say("感情这事儿，冷暖自知，外人说说也就过了。")
    return _say(f"瓜吃完了，{person}下一句估计更难接。")


def h2_event(_person: str) -> str:
    return "先把事儿捋一遍"


def h2_punchline() -> str:
    return "说句难听的"
