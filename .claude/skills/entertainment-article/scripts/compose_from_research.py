#!/usr/bin/env python3
"""
Compose entertainment article from multi-round volc research bundle.
Follows entertainment-article: 有信息、数字、原话、非评论体。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from de_ai_polish import polish
from html_render import box, h2, p, render

THEME = {
    "wedding": "#d4636a",
    "variety": "#9b59b6",
    "drama": "#e67e22",
    "gossip": "#d4636a",
    "general": "#e67e22",
}

SHORT_MIN = 650
LONG_MIN = 1800


def _classify(title: str) -> str:
    t = title
    if re.search(r"不想|不敢|不愿", t) and "结婚" in t:
        return "gossip"
    if re.search(r"婚礼|婚纱|婚纱照", t):
        return "wedding"
    if re.search(r"淘汰|综艺|歌手|浪姐", t):
        return "variety"
    if re.search(r"剧|剧情|杀青|剧透", t):
        return "drama"
    if re.search(r"恋|分手|离婚|出轨|官宣", t):
        return "gossip"
    return "general"


def _pick_title(person: str, hot_title: str, bundle: dict[str, Any]) -> str:
    # 优先用热搜原标题（含人名/事件名），避免乱拼出生年份
    if 8 <= len(hot_title) <= 28:
        return hot_title
    if person and person in hot_title and len(hot_title) <= 30:
        return hot_title[:30]
    if person and person not in hot_title:
        t = f"{person}：{hot_title}"
        return t[:28] if len(t) > 28 else t
    return hot_title[:28]


def _source_line(sources: list[dict]) -> str:
    parts = []
    for s in sources[:3]:
        site = s.get("site") or "媒体"
        parts.append(site)
    return "、".join(parts) if parts else "公开报道"


def _trim_fact(fact: str, max_len: int = 260) -> str:
    fact = re.sub(r"\s+", " ", (fact or "").strip())
    if len(fact) <= max_len:
        return fact
    parts = re.split(r"[。！？]", fact)
    out = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        chunk = part + "。"
        if len(out) + len(chunk) > max_len:
            break
        out += chunk
    return out or fact[:max_len]


def _fact_paragraph(fact: str, person: str, sites: str) -> str:
    text = _trim_fact(fact)
    if person and person not in text:
        text = f"关于{person}，{text}"
    if not text.endswith("。"):
        text += "。"
    if "据" not in text and sites:
        text = f"据{sites}报道，{text}"
    return polish(text)


def build_sections(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    hot_value: int | None,
    article_type: str,
) -> list[tuple]:
    facts: list[str] = bundle.get("facts") or []
    quotes: list[str] = bundle.get("quotes") or []
    numbers: list[str] = bundle.get("numbers") or []
    sources = bundle.get("sources") or []
    sites = _source_line(sources)

    num_hint = ""
    if numbers:
        num_hint = f"其中一个细节是{numbers[0]}。"
    heat = ""
    if hot_value and hot_value > 50_000:
        heat = f"这条话题在热榜上的热度超过 {hot_value // 10000} 万。"

    opener = polish(
        f"{person}因为「{hot_title}」这两天被刷屏。{heat}{num_hint}"
        f"我把几轮搜索下来的公开信息捋了一遍，能确认的比热搜标题里写的要多。"
    )
    sections: list[tuple] = [("p", opener)]

    if facts:
        sections.append(("h2", f"先把{person}这件事说清楚"))
        limit = 5 if article_type == "long" else 3
        for fact in facts[:limit]:
            sections.append(("p", _fact_paragraph(fact, person, sites)))
    else:
        sections.append(
            (
                "p",
                polish(
                    f"目前公开渠道的信息还集中在热搜词条本身，"
                    f"一手细节需要等{person}方或更多媒体跟进。"
                ),
            )
        )

    if quotes:
        sections.append(("h2", "当事人/身边怎么说"))
        for q in quotes[:2 if article_type == "short" else 4]:
            sections.append(("p", polish(f"有报道称：{q}。")))

    if numbers and len(numbers) > 1:
        sections.append(
            (
                "box",
                polish(f"和这件事相关的数字：{'、'.join(numbers[:5])}。具体口径以原报道为准。"),
            )
        )

    sections.append(("h2", "你咋看", "bg:#d4636a"))
    sections.append(
        (
            "p",
            polish(
                f"这事热闹归热闹，关键还是看后续还有没有更硬的证据。"
                f"你更关注{person}本人的态度，还是事件里其他人的反应？欢迎评论区聊聊。"
            ),
        )
    )
    sections.append(
        (
            "p",
            polish("（本文由公开信息整理，不含未证实爆料；发布前请人工核对。）"),
        )
    )
    return sections


def compose(
    hot_item: dict[str, Any],
    research: dict[str, Any],
    *,
    article_type: str = "short",
) -> dict[str, Any]:
    bundle = research.get("bundle") or {}
    if not bundle and research.get("bullets"):
        bundle = {
            "person": research.get("person"),
            "topic_title": research.get("topic_title"),
            "facts": research.get("bullets"),
            "numbers": [],
            "quotes": [],
            "sources": [],
            "title_candidates": [research.get("topic_title")],
        }

    person = bundle.get("person") or research.get("person") or hot_item.get("person") or ""
    hot_title = bundle.get("topic_title") or research.get("topic_title") or hot_item.get("title") or ""
    kind = _classify(hot_title)
    color = THEME.get(kind, THEME["general"])
    title = _pick_title(person, hot_title, bundle)

    sections = build_sections(
        person,
        hot_title,
        bundle,
        hot_value=int(hot_item.get("hot_value") or 0) or None,
        article_type=article_type,
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
        "bundle_file": research.get("bundle_file") or "",
        "research_rounds": research.get("rounds") or bundle.get("round_count"),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--hot-json", required=True)
    p.add_argument("--research-json", required=True)
    p.add_argument("--article-type", choices=["short", "long"], default="short")
    p.add_argument("--out", default="article.json")
    p.add_argument("--html-out", default="")
    args = p.parse_args()

    hot = json.loads(Path(args.hot_json).read_text(encoding="utf-8"))
    research = json.loads(Path(args.research_json).read_text(encoding="utf-8"))
    article = compose(hot, research, article_type=args.article_type)
    Path(args.out).write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.html_out:
        Path(args.html_out).write_text(article["content_html"], encoding="utf-8")

    min_chars = LONG_MIN if args.article_type == "long" else SHORT_MIN
    print(
        json.dumps(
            {
                "out": args.out,
                "title": article["title"],
                "char_count": article["char_count"],
                "person": article["person"],
                "rounds": article.get("research_rounds"),
                "min_chars": min_chars,
                "ok": article["char_count"] >= min_chars,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
