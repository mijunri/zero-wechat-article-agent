#!/usr/bin/env python3
"""
Compose short entertainment article (头条短篇) from research JSON + hot item.
Follows entertainment-article SKILL: 有信息、具体数字、人物全名、去评论体。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from html_render import render

THEME = {
    "wedding": ("#d4636a", "0a0a1a", "rgba(212,99,106,0.2)"),
    "variety": ("#9b59b6", "0d0d1a", "rgba(155,89,182,0.2)"),
    "drama": ("#e67e22", "0d0d1a", "rgba(230,126,34,0.2)"),
    "gossip": ("#d4636a", "1a1a2e", "rgba(212,99,106,0.18)"),
    "general": ("#e67e22", "1a1a2e", "rgba(230,126,34,0.15)"),
}


def _classify(title: str) -> str:
    t = title
    if re.search(r"不想|不敢|不愿", t) and "结婚" in t:
        return "gossip"
    if re.search(r"婚礼|婚纱|婚纱照|婚礼上", t):
        return "wedding"
    if re.search(r"淘汰|综艺|歌手|浪姐|舞台", t):
        return "variety"
    if re.search(r"剧|剧情|杀青|剧透|上映", t):
        return "drama"
    if re.search(r"恋|分手|离婚|出轨|官宣", t):
        return "gossip"
    return "general"


def _title_for(person: str, hot_title: str, bullets: list[str]) -> str:
    """Concrete title with person full name, <= 22 chars when possible."""
    base = hot_title.strip()
    if person and person not in base:
        base = f"{person}{base}"
    if len(base) <= 22:
        return base
    for sep in ("：", ":", "，", ","):
        if sep in hot_title:
            part = hot_title.split(sep)[0]
            if person in part and 8 <= len(part) <= 22:
                return part
    return base[:21] + "…"


def _expand_fact(bullet: str, person: str, hot: str) -> str:
    b = bullet.strip()
    if not b:
        return ""
    if person not in b:
        b = f"{person}方面，{b}"
    return (
        f"{b}。多家媒体在跟进报道，网友讨论的焦点集中在「{hot}」到底意味着什么。"
        f"目前能确认的是公开信息仍在更新，具体以当事人或工作室后续回应为准。"
    )


def build_sections(
    person: str,
    hot_title: str,
    bullets: list[str],
    *,
    hot_value: int | None,
    source_url: str,
) -> list[tuple]:
    heat = ""
    if hot_value and hot_value > 10000:
        heat = f"微博等平台热度一度超过 {hot_value // 10000} 万。"

    opener = (
        f"{person}最近因为「{hot_title}」冲上热搜。{heat}"
        f"这事看起来是八卦，但仔细翻一下公开报道，细节比标题里写的要多。"
    )
    sections: list[tuple] = [("p", opener)]

    usable = [b for b in bullets if len(b) > 12][:5]
    if usable:
        sections.append(("h2", f"公开信息里能确认的几件事"))
        for b in usable[:3]:
            sections.append(("p", _expand_fact(b, person, hot_title)))
    else:
        sections.append(
            (
                "p",
                f"目前能查到的公开信息主要集中在「{hot_title}」本身。"
                f"网友讨论热度很高，但一手细节还需要等更多媒体跟进。",
            )
        )

    sections.append(
        (
            "h2",
            "你怎么看待这件事？",
            "bg:#d4636a",
        )
    )
    sections.append(
        (
            "p",
            f"说实话，{person}这条热搜能起来，说明大家关心的不只是八卦本身，"
            f"而是背后那个人到底经历了什么。你更在意的是事实，还是态度？评论区可以聊聊。",
        )
    )
    if source_url:
        sections.append(
            (
                "box",
                f"热榜来源链接已收录，发布前请核对：<br>{source_url}",
            )
        )
    return sections


def compose(
    hot_item: dict[str, Any],
    research: dict[str, Any],
    *,
    article_type: str = "short",
) -> dict[str, Any]:
    person = research.get("person") or hot_item.get("person") or ""
    hot_title = research.get("topic_title") or hot_item.get("title") or ""
    bullets = research.get("bullets") or []
    kind = _classify(hot_title)
    color, _, _ = THEME.get(kind, THEME["general"])
    title = _title_for(person, hot_title, bullets)
    sections = build_sections(
        person,
        hot_title,
        bullets,
        hot_value=int(hot_item.get("hot_value") or 0) or None,
        source_url=str(hot_item.get("url") or ""),
    )
    html = render(person, title, color, sections)
    plain = re.sub(r"<[^>]+>", "", html)
    char_count = len(re.findall(r"[\u4e00-\u9fff]", plain))

    return {
        "title": title,
        "person": person,
        "cover_url": hot_item.get("cover") or "",
        "content_html": html,
        "char_count": char_count,
        "kind": kind,
        "article_type": article_type,
        "source_url": hot_item.get("url") or "",
        "search_files": research.get("search_files") or [],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--hot-json", required=True, help="Single hot list item")
    p.add_argument("--research-json", required=True)
    p.add_argument("--out", default="article.json")
    p.add_argument("--html-out", default="")
    args = p.parse_args()

    hot = json.loads(Path(args.hot_json).read_text(encoding="utf-8"))
    research = json.loads(Path(args.research_json).read_text(encoding="utf-8"))
    article = compose(hot, research)
    Path(args.out).write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html_out:
        Path(args.html_out).write_text(article["content_html"], encoding="utf-8")
    print(
        json.dumps(
            {
                "out": args.out,
                "title": article["title"],
                "char_count": article["char_count"],
                "person": article["person"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
