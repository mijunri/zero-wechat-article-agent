#!/usr/bin/env python3
"""
Compose entertainment article — 编辑重述 + 潜台词观点。
硬性禁止：据××报道、百科缝合、搜索残句直贴。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from de_ai_polish import polish
from editorial_compose import (
    closing_line,
    h2_debate,
    h2_event,
    h2_reader,
    h2_unsaid,
    hook_opening,
    pick_angle,
    vow_highlight_box,
    write_debate_layer,
    write_event_narrative,
    write_unsaid_truth,
)
from fact_rank import rank_facts
from html_render import box, render
from pipeline_meta import extract_h2_plain, inject_meta
from prose_guard import guard_prose, paragraph_ok
from seo_optimize import count_han, normalize_person, score_seo, seo_title

THEME = {
    "wedding": "#d4636a",
    "variety": "#9b59b6",
    "drama": "#e67e22",
    "gossip": "#d4636a",
    "general": "#e67e22",
}

SHORT_MIN = 1000
LONG_MIN = 1800


def _classify(title: str) -> str:
    t = title
    if re.search(r"婚礼|婚纱|婚纱照|誓词", t):
        return "wedding"
    if re.search(r"淘汰|综艺|歌手|浪姐", t):
        return "variety"
    if re.search(r"剧|剧情|杀青|剧透", t):
        return "drama"
    if re.search(r"恋|分手|离婚|出轨|官宣", t):
        return "gossip"
    return "general"


def _emit_para(sections: list[tuple], text: str) -> None:
    text = guard_prose(polish(text))
    if paragraph_ok(text):
        sections.append(("p", text))


def build_sections_short(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    kind: str,
) -> tuple[list[tuple], int, str]:
    raw_facts: list[str] = bundle.get("facts") or []
    ranked = rank_facts(raw_facts, hot_title, person, limit=12)
    angle = pick_angle(hot_title, person, kind)

    sections: list[tuple] = []
    _emit_para(sections, hook_opening(person, hot_title, angle))

    sections.append(("h2", h2_event(person)))
    event_paras = write_event_narrative(person, hot_title, kind)
    for para in event_paras:
        _emit_para(sections, para)

    if "誓词" in hot_title or "贫穷" in hot_title:
        sections.append(("box", vow_highlight_box(person)))

    debate = write_debate_layer(person, hot_title, [])
    if debate:
        sections.append(("h2", h2_debate()))
        for para in debate:
            _emit_para(sections, para)

    unsaid = write_unsaid_truth(person, hot_title, kind, ranked)
    sections.append(("h2", h2_unsaid(), "bg:#9b59b6"))
    for para in unsaid:
        _emit_para(sections, para)

    sections.append(("h2", h2_reader(), "bg:#d4636a"))
    _emit_para(
        sections,
        f"你更在意{person}删词，还是在意他夸妻子那套话术？"
        f"或者你觉得誓词本来就该私人化、不该被全网审判？"
        f"带一句你自己的判断来聊，比复制梗图有用。",
    )
    _emit_para(sections, closing_line(person, hot_title))
    _emit_para(sections, "（编辑整理，不含未证实爆料；发布前请人工核对。）")

    used = len(event_paras)
    return sections, used, angle


def build_sections_long(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    kind: str,
) -> tuple[list[tuple], int, str]:
    return build_sections_short(person, hot_title, bundle, kind=kind)


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

    builder = build_sections_long if article_type == "long" else build_sections_short
    sections, facts_used, angle = builder(person, hot_title, bundle, kind=kind)
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
        "compose_mode": "editorial-rewrite",
        "angle": angle,
        "person": person,
        "hot_title": hot_title,
        "facts_in_bundle": len(bundle.get("facts") or []),
        "facts_used": facts_used,
        "research_rounds": research.get("rounds") or bundle.get("round_count"),
        "bundle_file": research.get("bundle_file") or "",
        "seo_check": seo_check,
        "char_count": char_count,
        "min_chars": min_chars,
        "forbidden": "no_据xx报道",
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
        "angle": angle,
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
                "angle": article.get("angle"),
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
