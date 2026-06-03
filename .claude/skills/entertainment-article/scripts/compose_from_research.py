#!/usr/bin/env python3
"""
Compose entertainment article — 厚信息 + 潜台词观点（禁止热度套话、百科缝合）。
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
    extract_netizen_lines,
    h2_debate,
    h2_event,
    h2_reader,
    h2_unsaid,
    hook_opening,
    pick_angle,
    wedding_facts_block,
    write_debate_layer,
    write_unsaid_truth,
)
from fact_rank import merge_facts_to_paragraphs, rank_facts
from html_render import box, render
from pipeline_meta import extract_h2_plain, inject_meta
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


def _extract_vow_snippet(facts: list[str]) -> str:
    for f in facts:
        if "无论顺境" in f or "低谷" in f:
            m = re.search(
                r"以后[^。]{0,20}无论顺境[^。]{8,120}|无论顺境还是低谷[^。]{0,80}",
                f,
            )
            if m:
                s = m.group(0).strip()
                if not s.endswith("。"):
                    s += "。"
                return s
    return ""


def _source_line(sources: list[dict]) -> str:
    parts = []
    for s in sources[:2]:
        site = s.get("site") or ""
        if site and site not in ("抖音百科", "搜狗百科", "字典网"):
            parts.append(site)
    return "、".join(parts) if parts else "多家媒体"


def _meaningful_numbers(numbers: list[str]) -> list[str]:
    keep: list[str] = []
    for n in numbers or []:
        if re.match(r"^\d{4}年?$", n):
            continue
        if n in ("4.2", "2次", "06", "03", "22", "43"):
            continue
        if "月" in n or "日" in n or "小时" in n or "年" in n or "亿" in n or "万" in n:
            keep.append(n)
    return keep[:5]


def build_sections_short(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    kind: str,
) -> tuple[list[tuple], int, str]:
    raw_facts: list[str] = bundle.get("facts") or []
    ranked = rank_facts(raw_facts, hot_title, person, limit=12)
    sources = bundle.get("sources") or []
    sites = _source_line(sources)
    angle = pick_angle(hot_title, person, kind)
    netizen = extract_netizen_lines(ranked)

    sections: list[tuple] = []
    sections.append(("p", hook_opening(person, hot_title, angle)))

    sections.append(("h2", h2_event(person)))
    if kind == "wedding" and ("誓词" in hot_title or "婚礼" in hot_title):
        bg = wedding_facts_block(person)
        if sites:
            bg = f"据{sites}等报道，{bg}"
        sections.append(("p", bg))

    narrative = merge_facts_to_paragraphs(ranked, person, max_paras=3, sents_per_para=2)
    used = len(ranked[: max(len(narrative), 1)])
    for i, para in enumerate(narrative):
        text = para
        if not narrative and i == 0 and sites:
            text = f"据{sites}等报道，{text}"
        sections.append(("p", polish(text)))

    vow = _extract_vow_snippet(ranked)
    if vow:
        sections.append(
            (
                "box",
                polish(f"誓词里能核对到的关键句：{vow}对照模板，缺的是「贫穷/富贵」那一整段。"),
            )
        )

    debate = write_debate_layer(person, hot_title, netizen)
    if debate:
        sections.append(("h2", h2_debate()))
        for para in debate:
            sections.append(("p", para))

    unsaid = write_unsaid_truth(person, hot_title, kind, ranked)
    sections.append(("h2", h2_unsaid(), "bg:#9b59b6"))
    for para in unsaid:
        sections.append(("p", para))

    nums = _meaningful_numbers(bundle.get("numbers") or [])
    if nums and ("婚礼" in hot_title or "誓词" in hot_title):
        sections.append(
            (
                "p",
                polish(
                    f"几个常被提起的数字：{'、'.join(nums)}。"
                    f"数字本身不是结论，但能和「补办」「高定」「耗时」这些细节对上线。"
                ),
            )
        )

    sections.append(("h2", h2_reader(), "bg:#d4636a"))
    sections.append(
        (
            "p",
            polish(
                f"你更在意{person}删词，还是在意他夸妻子那套话术？"
                f"或者你觉得誓词本来就该私人化、不该被全网审判？"
                f"带一句你自己的判断来聊，比复制梗图有用。"
            ),
        )
    )
    sections.append(("p", closing_line(person, hot_title)))
    sections.append(
        ("p", polish("（公开信息整理 + 编辑判断，不含未证实爆料；发布前请人工核对。）"))
    )
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
        "compose_mode": "editorial-unsaid",
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
