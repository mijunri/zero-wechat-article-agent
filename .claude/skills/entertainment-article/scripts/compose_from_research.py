#!/usr/bin/env python3
"""
Compose entertainment article from research bundle.
短篇：事件叙事 + 编辑观点（禁止百科 fact 逐条缝合）。
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
    h2_opinion,
    h2_reader,
    hook_opening,
    pick_angle,
    write_opinion,
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

SHORT_MIN = 800
LONG_MIN = 1800


def _classify(title: str) -> str:
    t = title
    if re.search(r"不想|不敢|不愿", t) and "结婚" in t:
        return "gossip"
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
                r"(以后)?无论顺境[^。]{8,90}|无论顺境还是低谷[^。]{0,40}",
                f,
            )
            if m:
                return m.group(0).strip() + "。"
    return ""


def _filter_quotes(quotes: list[str], person: str) -> list[str]:
    out: list[str] = []
    skip = (
        "本文作者",
        "责任编辑",
        "版权",
        "目录序言",
        "个人资料",
        "抖音百科",
        "微博认证",
        "军事博主",
        "起源：",
        "：一份",
    )
    for q in quotes:
        q = (q or "").strip()
        if len(q) < 20 or len(q) > 90:
            continue
        if any(s in q for s in skip):
            continue
        if "无论" in q or "顺境" in q or "低谷" in q or "爱你" in q:
            out.append(q)
        elif person in q and ("说" in q or "表示" in q or "承诺" in q):
            out.append(q)
    return out


def _source_line(sources: list[dict]) -> str:
    parts = []
    for s in sources[:2]:
        site = s.get("site") or ""
        if site and site not in ("抖音百科", "搜狗百科", "字典网"):
            parts.append(site)
    return "、".join(parts) if parts else "多家媒体"


def build_sections_short(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    hot_value: int | None,
    kind: str,
) -> tuple[list[tuple], int, str]:
    raw_facts: list[str] = bundle.get("facts") or []
    ranked = rank_facts(raw_facts, hot_title, person, limit=10)
    quotes = _filter_quotes(bundle.get("quotes") or [], person)
    sources = bundle.get("sources") or []
    sites = _source_line(sources)
    angle = pick_angle(hot_title, person, kind)

    sections: list[tuple] = []
    sections.append(("p", hook_opening(person, hot_title, hot_value, angle)))

    if kind == "wedding" and ("誓词" in hot_title or "婚礼" in hot_title):
        sections.append(
            (
                "p",
                polish(
                    f"背景很简单：{person}和奚梦瑶在法国补办婚礼，誓词没走「无论贫穷还是富贵」那套，"
                    f"而是换成「顺境与低谷」「热闹还是安静」——热搜炸的点，就在「贫穷」二字被整段删掉了。"
                ),
            )
        )

    sections.append(("h2", h2_event(angle, person)))
    narrative = merge_facts_to_paragraphs(ranked, person, max_paras=4, sents_per_para=2)
    used = len(ranked[: max(len(narrative), 1)])

    if narrative:
        for i, para in enumerate(narrative):
            text = para
            if i == 0 and sites and "据" not in text:
                text = f"据{sites}等报道，{text}"
            sections.append(("p", polish(text)))
    else:
        sections.append(
            (
                "p",
                polish(
                    f"眼下公开渠道还在消化这条热搜，一手细节（比如誓词全文、现场原话）"
                    f"还没被权威媒体完整放出。你能确定的，主要是「{hot_title}」这条词条本身在发酵。"
                ),
            )
        )
        used = 0

    vow = _extract_vow_snippet(ranked) or (quotes[0] if quotes else "")
    if vow and len(vow) >= 15:
        sections.append(("h2", f"{person}誓词原句"))
        sections.append(("p", polish(f"能核对到的承诺大意是：{vow}")))

    nums = [n for n in (bundle.get("numbers") or []) if not re.match(r"^\d{4}年?$", n)]
    if nums:
        sections.append(("box", polish(f"和事件相关的数字：{'、'.join(nums[:4])}（口径以原报道为准）")))

    sections.append(("h2", h2_opinion(), "bg:#9b59b6"))
    sections.append(("p", write_opinion(person, hot_title, kind, ranked, quotes)))

    sections.append(("h2", h2_reader(), "bg:#d4636a"))
    sections.append(
        (
            "p",
            polish(
                f"你是站{person}这边，还是觉得誓词/表述欠考虑？"
                f"欢迎评论区说说你的理由——带细节的那种，别只扔一句「无语」。"
            ),
        )
    )
    sections.append(("p", closing_line(person, hot_title, kind)))
    sections.append(
        ("p", polish("（公开信息整理 + 编辑观点，不含未证实爆料；发布前请人工核对。）"))
    )
    return sections, used, angle


def build_sections_long(
    person: str,
    hot_title: str,
    bundle: dict[str, Any],
    *,
    hot_value: int | None,
    kind: str,
) -> tuple[list[tuple], int, str]:
    return build_sections_short(person, hot_title, bundle, hot_value=hot_value, kind=kind)


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
    sections, facts_used, angle = builder(
        person,
        hot_title,
        bundle,
        hot_value=int(hot_item.get("hot_value") or 0) or None,
        kind=kind,
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
        "compose_mode": "editorial",
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
