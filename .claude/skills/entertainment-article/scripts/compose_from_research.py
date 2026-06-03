#!/usr/bin/env python3
"""
Compose entertainment article from multi-round volc research bundle.
Follows entertainment-article: 有信息、数字、原话、非评论体；集成 SEO 与人名校正。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from de_ai_polish import polish
from html_render import box, h2, p, render
from pipeline_meta import extract_h2_plain, inject_meta
from seo_optimize import (
    count_han,
    normalize_person,
    score_seo,
    seo_h2_facts,
    seo_h2_quotes,
    seo_lead,
    seo_title,
)

THEME = {
    "wedding": "#d4636a",
    "variety": "#9b59b6",
    "drama": "#e67e22",
    "gossip": "#d4636a",
    "general": "#e67e22",
}

SHORT_MIN = 800
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


def _filter_quotes(quotes: list[str], person: str) -> list[str]:
    out: list[str] = []
    skip = ("本文作者", "责任编辑", "版权", "扫码", "关注我")
    for q in quotes:
        q = (q or "").strip()
        if len(q) < 8 or len(q) > 120:
            continue
        if any(s in q for s in skip):
            continue
        out.append(q)
    return out


def build_sections(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    hot_value: int | None,
    article_type: str,
) -> tuple[list[tuple], int]:
    facts: list[str] = bundle.get("facts") or []
    quotes = _filter_quotes(bundle.get("quotes") or [], person)
    numbers: list[str] = bundle.get("numbers") or []
    sources = bundle.get("sources") or []
    sites = _source_line(sources)

    opener = polish(seo_lead(person, hot_title, hot_value, numbers))
    sections: list[tuple] = [("p", opener)]

    fact_limit = 8 if article_type == "long" else 6
    used = 0
    if facts:
        sections.append(("h2", seo_h2_facts(person)))
        for fact in facts[:fact_limit]:
            sections.append(("p", _fact_paragraph(fact, person, sites)))
            used += 1
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
        sections.append(("h2", seo_h2_quotes(person)))
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
    return sections, used


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

    hot_title = bundle.get("topic_title") or research.get("topic_title") or hot_item.get("title") or ""
    person = normalize_person(
        bundle.get("person") or research.get("person") or hot_item.get("person") or "",
        hot_title,
    )
    kind = _classify(hot_title)
    color = THEME.get(kind, THEME["general"])
    title = seo_title(person, hot_title, bundle)

    sections, facts_used = build_sections(
        person,
        hot_title,
        bundle,
        hot_value=int(hot_item.get("hot_value") or 0) or None,
        article_type=article_type,
    )
    html = render(person, title, color, sections)
    plain = re.sub(r"<[^>]+>", "", html)
    char_count = count_han(plain)
    min_chars = LONG_MIN if article_type == "long" else SHORT_MIN

    seo_check = score_seo(
        title=title,
        person=person,
        plain_body=plain,
        h2_texts=extract_h2_plain(html),
        char_count=char_count,
        min_chars=min_chars,
    )

    meta = {
        "pipeline": "toutiao-entertainment",
        "person": person,
        "hot_title": hot_title,
        "facts_in_bundle": len(bundle.get("facts") or []),
        "facts_used": facts_used,
        "research_rounds": research.get("rounds") or bundle.get("round_count"),
        "bundle_file": research.get("bundle_file") or "",
        "seo_check": seo_check,
        "char_count": char_count,
        "min_chars": min_chars,
    }
    html = inject_meta(html, meta)

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
        "seo_check": seo_check,
        "pipeline_meta": meta,
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
                "seo_score": article.get("seo_check", {}).get("seo_score"),
                "seo_grade": article.get("seo_check", {}).get("seo_grade"),
                "min_chars": min_chars,
                "ok": article["char_count"] >= min_chars,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
