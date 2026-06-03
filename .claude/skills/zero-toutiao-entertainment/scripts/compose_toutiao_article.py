#!/usr/bin/env python3
"""Compose Toutiao-style entertainment article from a hot topic item."""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")


def _classify(title: str) -> str:
    t = title
    if re.search(r"不想|不敢|不愿", t) and "结婚" in t:
        return "gossip"
    if re.search(r"婚礼|婚纱|婚纱照|婚礼上|办完婚|结婚照|订婚", t):
        return "wedding"
    if re.search(r"淘汰|综艺|歌手|浪姐|披荆斩棘|舞台", t):
        return "variety"
    if re.search(r"剧|剧情|杀青|路透|番|上映|票房", t):
        return "drama"
    if re.search(r"恋|分手|离婚|出轨|官宣|绯闻", t):
        return "gossip"
    return "general"


def _format_hot(hot: int | str | None) -> str:
    try:
        n = int(hot or 0)
    except (TypeError, ValueError):
        return "热度攀升"
    if n >= 10_000_000:
        return f"热度突破 {n // 10_000} 万"
    if n >= 10_000:
        return f"热度约 {n // 10_000} 万"
    return "登上热搜"


def _toutiao_title(topic: str) -> str:
    """Headline tuned for Toutiao: concrete + hook, <= 30 chars when possible."""
    topic = topic.strip()
    hooks = {
        "wedding": "婚礼细节：",
        "variety": "综艺热议：",
        "drama": "剧集热议：",
        "gossip": "娱乐观察：",
        "general": "热点速递：",
    }
    kind = _classify(topic)
    prefix = hooks[kind]
    candidate = f"{prefix}{topic}"
    if len(candidate) <= 30:
        return candidate
    if len(topic) <= 26:
        return topic
    return topic[:27] + "…"


def _paragraphs_for_kind(kind: str, topic: str, hot_line: str, platform: str) -> list[str]:
    p1 = (
        f"刚刚，「{topic}」相关话题在{platform}热榜快速发酵，{hot_line}。"
        f"不少网友表示「一打开热搜就是它」，讨论热度还在持续走高。"
    )
    p2 = (
        f"截至发稿，该词条仍停留在榜单前列，实时讨论区里既有粉丝控评，也有路人吃瓜。"
        f"从传播节奏看，这类话题往往在 2–4 小时内达到峰值，随后进入二创剪辑与观点交锋阶段。"
    )
    bodies: dict[str, list[str]] = {
        "wedding": [
            "从现场细节到嘉宾阵容，再到网友拍到的花絮，信息量很大。婚礼类话题之所以容易出圈，是因为既有仪式感，又自带「人设反差」——公众会下意识对比「台前形象」和「私下状态」。",
            "围观者最感兴趣的通常是三件事：礼服与布置是否「够体面」、亲友互动是否露出真实性格、以及当事人事后状态是否轻松。只要有一个细节能形成反差，就容易被做成短视频切片二次传播。",
            "也有理性声音提醒：过度围观私人生活，可能让当事人承受额外压力。平台侧通常会限制恶意剪辑与造谣内容，但讨论本身很难完全降温。",
            "对读者来说，更稳妥的打开方式是：把它当作娱乐资讯，而不是人生裁判。未经证实的聊天记录、所谓「知情人」爆料，都建议先打个问号。",
        ],
        "variety": [
            "综艺话题的爆点往往来自「结果意外」：淘汰、逆袭、舞台事故、嘉宾互动等，都会触发二次传播。节目方若及时放出花絮或回应，能把舆论从猜测拉回事实。",
            "节目粉与路人的关注点经常错位：前者在意舞台完成度与镜头公平，后者更在意「有没有戏剧性」。当两者在评论区相遇，就很容易吵成热搜第二梯队。",
            "对普通观众来说，这类热搜的娱乐价值在于「可讨论」——你会更在意舞台表现，还是更在意幕后关系？如果节目正在播出期，制作方通常会顺势放出预告或加更，把热度锁住。",
            "如果你要写文章或做短视频，建议抓住一个具体角度（例如「本轮淘汰为何争议」），避免泛泛而谈，否则很难在信息流里获得停留。",
        ],
        "drama": [
            "影视类热搜多与剧情走向、角色设定或演员状态有关。观众会用「是否符合逻辑」「是否尊重原著/常识」来评判，一旦触发共鸣，就容易形成大规模讨论。",
            "剧情争议并不总是坏事：对播出中的作品而言，讨论意味着存在感。但若是明显的人设崩塌或逻辑硬伤，也可能反噬口碑，影响后续招商与平台推荐。",
            "对追剧党而言，这类话题是「社交货币」：不聊两句好像就错过了同温层。制作方若能在不剧透的前提下回应争议，通常更利于口碑；若选择沉默，舆论就会被营销号接管。",
            "写稿时建议标明「含剧透」或「不含剧透」，尊重不同读者的观看进度，也能减少评论区争吵。",
        ],
        "gossip": [
            "情感向娱乐新闻的传播速度通常更快：信息不完整时，猜测会填补空白。建议读者区分「已证实事实」和「网传片段」，避免被带节奏。",
            "这类话题的评论区常见三类声音：祝福、质疑、以及「坐等反转」。在没有官方声明前，任何「内幕」都可能是断章取义。",
            "从行业角度看，艺人团队一般会采取「冷处理 / 澄清 / 法律手段」三档策略。对围观者而言，保持边界感，比急于站队更重要。",
            "对内容创作者而言，最稳妥的写法是引用公开可见的信息（节目片段、采访原话、已发布海报），少用情绪化定性词。",
        ],
        "general": [
            "该话题之所以能冲上热榜，往往因为它同时满足了「情绪价值」和「讨论空间」：有人吃瓜，有人分析，也有人单纯路过发表看法。",
            "从平台机制看，热榜条目会在搜索、推荐与话题页之间联动，形成「你刷到哪都能看见」的沉浸感，这也是娱乐新闻扩散快的原因。",
            "娱乐新闻的寿命通常不长，但若涉及作品宣发或综艺节点，团队会顺势做物料投放，把热度转化为关注度。",
            "如果你准备跟进报道，可以先列出三个问题：发生了什么、公众在争论什么、接下来可能如何发展。结构清楚，比堆形容词更有用。",
        ],
    }
    tail = [
        "需要强调的是：本文不涉及对任何个人的道德判决，仅整理公开热榜信息与常见讨论框架，方便读者快速了解「大家在聊什么」。",
        "如果你也在关注这件事，欢迎在评论区用一句话说说你的看法：更在意真相，还是更在意态度？",
        "（本文为热点资讯整理与观点评述，不构成事实认定；信息以当事人及权威媒体后续通报为准。）",
    ]
    return [p1, p2, *bodies.get(kind, bodies["general"]), *tail]


def build_article(item: dict[str, Any]) -> dict[str, Any]:
    topic = (item.get("title") or "").strip()
    platform = {"weibo": "微博", "douyin": "抖音", "toutiao": "今日头条"}.get(
        item.get("platform") or "", "社交平台"
    )
    kind = _classify(topic)
    hot_line = _format_hot(item.get("hot_value"))
    title = _toutiao_title(topic)
    paragraphs = _paragraphs_for_kind(kind, topic, hot_line, platform)

    return {
        "title": title,
        "cover_url": item.get("cover") or "",
        "lead": paragraphs[0],
        "paragraphs": paragraphs[1:],
        "source_url": item.get("url") or "",
        "source_label": f"{platform}热榜",
        "topic_raw": topic,
        "kind": kind,
        "platform": item.get("platform"),
        "meta": {
            "entertainment_score": item.get("entertainment_score"),
            "hot_value": item.get("hot_value"),
            "composed_at": datetime.now(BJ).isoformat(),
        },
    }


def article_to_html(article: dict[str, Any]) -> str:
    parts = ['<article class="toutiao-article">']
    lead = article.get("lead") or ""
    if lead:
        parts.append(f"<p><strong>{html.escape(lead)}</strong></p>")
    for para in article.get("paragraphs") or []:
        para = str(para).strip()
        if para:
            parts.append(f"<p>{html.escape(para)}</p>")
    url = article.get("source_url") or ""
    label = article.get("source_label") or "来源"
    if url:
        parts.append(
            f'<p class="source">来源：<a href="{html.escape(url, quote=True)}">'
            f"{html.escape(label)}</a></p>"
        )
    parts.append(
        f'<p class="footer">{html.escape("本文由 zero-wechat-article-agent 娱乐热点流水线生成，发布前请人工核对事实。")}</p>'
    )
    parts.append("</article>")
    return "\n".join(parts)


def plain_text_length(article: dict[str, Any]) -> int:
    text = (article.get("lead") or "") + "".join(article.get("paragraphs") or [])
    return len(text)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--topic-json", required=True, help="Single hot item JSON object")
    p.add_argument("--out", default="article.json")
    p.add_argument("--html-out", default="")
    args = p.parse_args()

    raw = json.loads(Path(args.topic_json).read_text(encoding="utf-8"))
    item = raw if isinstance(raw, dict) and "title" in raw else raw.get("item") or raw
    article = build_article(item)
    article["content_html"] = article_to_html(article)
    article["char_count"] = plain_text_length(article)

    Path(args.out).write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html_out:
        Path(args.html_out).write_text(article["content_html"], encoding="utf-8")
    print(
        json.dumps(
            {
                "out": args.out,
                "title": article["title"],
                "char_count": article["char_count"],
                "kind": article["kind"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
