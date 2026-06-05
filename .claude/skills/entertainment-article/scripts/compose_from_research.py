#!/usr/bin/env python3
"""
头条娱乐成稿：有梗、能扫读、有判断；禁止你咋看/据××报道/搜索残句。
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
    h2_event,
    h2_punchline,
    hook_opening,
    pick_angle,
    write_event_narrative,
    write_meme_section,
    write_punchline,
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

SHORT_MIN = 900
LONG_MIN = 1800


def _classify(title: str) -> str:
    if re.search(r"婚礼|婚纱|婚纱照|誓词", title):
        return "wedding"
    if re.search(r"恋|分手|离婚|出轨|官宣", title):
        return "gossip"
    return "general"


def _emit_para(sections: list[tuple], text: str, *, force: bool = False) -> None:
    text = guard_prose(polish(text))
    if force or paragraph_ok(text):
        sections.append(("p", text))


def _emit_meme_list(sections: list[tuple], paras: list[str]) -> None:
    """多条梗合并成一个信息框，扫读友好。"""
    if not paras:
        return
    body = "<br>".join(paras)
    sections.append(("box", body))


def build_sections_short(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    kind: str,
) -> tuple[list[tuple], int, str]:
    raw_facts: list[str] = bundle.get("facts") or []
    ranked = rank_facts(raw_facts, hot_title, person, limit=8)
    memes: list[str] = bundle.get("memes") or []
    angle = pick_angle(hot_title, person, kind)

    sections: list[tuple] = []
    _emit_para(sections, hook_opening(person, hot_title, memes))

    sections.append(("h2", h2_event(person)))
    event_paras = write_event_narrative(person, hot_title, kind, bundle)
    for para in event_paras:
        _emit_para(sections, para, force=True)

    meme_h2, meme_paras, meme_intro = write_meme_section(memes, hot_title, bundle)
    if meme_h2 and meme_paras:
        sections.append(("h2", meme_h2))
        if meme_intro:
            _emit_para(sections, meme_intro, force=True)
        _emit_meme_list(sections, meme_paras)

    sections.append(("h2", h2_punchline(), "bg:#9b59b6"))
    for para in write_punchline(person, hot_title, kind, ranked):
        _emit_para(sections, para, force=True)

    _emit_para(sections, closing_line(person, hot_title), force=True)

    used = len(event_paras) + len(meme_paras)
    return sections, used, angle


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
            "memes": [],
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

    sections, facts_used, angle = build_sections_short(person, hot_title, bundle, kind=kind)
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
        "compose_mode": "meme-editorial",
        "angle": angle,
        "meme_count": len(bundle.get("memes") or []),
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
        "angle": angle,
        "memes_used": len(bundle.get("memes") or []),
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

    min_chars = SHORT_MIN
    print(
        json.dumps(
            {
                "out": args.out,
                "title": article["title"],
                "char_count": article["char_count"],
                "memes_used": article.get("memes_used"),
                "seo_score": article.get("seo_check", {}).get("seo_score"),
                "ok": article["char_count"] >= min_chars,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
