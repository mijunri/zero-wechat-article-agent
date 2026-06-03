#!/usr/bin/env python3
"""
Multi-round Volcano search (entertainment-article §第2步):
  R1 人物广度 → R2 热点深度 → R3 聚焦线索 → R4 原话/回应 (+ 可选网页抓取)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[4]
VOLC_SCRIPT = REPO_ROOT / ".claude" / "skills" / "volc-search" / "scripts"
ENT_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(VOLC_SCRIPT))
sys.path.insert(0, str(ENT_SCRIPT))

from parse_results import parse_web_results  # noqa: E402
from research_bundle import build_bundle, save_bundle_md  # noqa: E402
from volc_search import format_markdown, web_fetch, web_search  # noqa: E402

BJ = ZoneInfo("Asia/Shanghai")
SEARCH_DIR = REPO_ROOT / "data" / "searchdata"


def _save_md(path: Path, *, query: str, person: str, topic: str, body: str, round_no: int) -> None:
    now = datetime.now(BJ).strftime("%Y-%m-%d %H:%M")
    content = f"""# 搜索数据 · 第{round_no}轮

- **来源**: Volcano FeedCoop web_search
- **获取时间**: {now}
- **人物**: {person}
- **热点标题**: {topic}
- **查询关键词**: {query}

## 原始结果

{body}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _safe_slug(s: str, max_len: int = 12) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "", s)
    return (s or "topic")[:max_len]


async def _search_round(
    *,
    person: str,
    topic: str,
    query: str,
    tag: str,
    stamp: str,
    round_no: int,
    count: int,
    time_range: str,
    fetch_top: bool,
) -> dict:
    data = await web_search(query, count=count, time_range=time_range)
    items = parse_web_results(data)
    md = format_markdown(data)
    fname = f"{stamp}_{_safe_slug(person)}_{tag}_volc.md"
    fpath = SEARCH_DIR / fname
    _save_md(fpath, query=query, person=person, topic=topic, body=md, round_no=round_no)

    if fetch_top and items and items[0].get("url"):
        try:
            fetched = await web_fetch(items[0]["url"])
            content = (
                fetched.get("Content")
                or fetched.get("Text")
                or fetched.get("Markdown")
                or ""
            )
            if isinstance(content, str) and len(content) > 100:
                items[0]["text"] = content[:2500]
                items[0]["fetched"] = True
        except Exception:
            pass

    return {
        "round": round_no,
        "tag": tag,
        "query": query,
        "file": str(fpath),
        "items": items,
    }


async def research(
    person: str,
    topic_title: str,
    *,
    stamp: str,
    rounds: int = 4,
    count: int = 8,
    broad_count: int | None = None,
    deep_count: int | None = None,
    time_range: str = "14d",
) -> dict:
    c1 = broad_count if broad_count is not None else count
    c2 = deep_count if deep_count is not None else count
    from extract_person import topic_keywords  # noqa: E402
    from fact_rank import event_keywords  # noqa: E402

    kw = topic_keywords(topic_title, person)
    ev = " ".join(event_keywords(topic_title, person)[:4])
    collected: list[dict] = []
    prior_items: list[dict] = []

    # R1 事件/热点（优先写「这件事」，不写百科履历）
    q1 = f"{person} {ev or kw} 怎么回事 细节 回应"[:40]
    r1 = await _search_round(
        person=person,
        topic=topic_title,
        query=q1,
        tag="r1-event",
        stamp=stamp,
        round_no=1,
        count=c1,
        time_range="7d",
        fetch_top=False,
    )
    collected.append(r1)
    prior_items.extend(r1["items"])

    # R2 舆论/原话/网友反应
    q2 = f"{person} {ev or kw} 网友 评论 原话 媒体"[:40]
    r2 = await _search_round(
        person=person,
        topic=topic_title,
        query=q2,
        tag="r2-hot",
        stamp=stamp,
        round_no=2,
        count=c2,
        time_range="7d",
        fetch_top=False,
    )
    collected.append(r2)
    prior_items.extend(r2["items"])

    if rounds >= 3:
        from research_bundle import _pick_followup_keywords  # noqa: E402

        focus = _pick_followup_keywords(person, kw, prior_items)
        q3 = f"{person} {focus} 经过 细节"
        r3 = await _search_round(
            person=person,
            topic=topic_title,
            query=q3[:40],
            tag="r3-focus",
            stamp=stamp,
            round_no=3,
            count=count,
            time_range="7d",
            fetch_top=False,
        )
        collected.append(r3)
        prior_items.extend(r3["items"])

    if rounds >= 4:
        q4 = f"{person} {kw} 采访 原话 媒体"
        r4 = await _search_round(
            person=person,
            topic=topic_title,
            query=q4[:40],
            tag="r4-quote",
            stamp=stamp,
            round_no=4,
            count=count,
            time_range="30d",
            fetch_top=True,
        )
        collected.append(r4)

    bundle = build_bundle(person=person, topic_title=topic_title, rounds=collected)
    bundle_path = SEARCH_DIR / f"{stamp}_{_safe_slug(person)}_bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    save_bundle_md(SEARCH_DIR / f"{stamp}_{_safe_slug(person)}_bundle.md", bundle)

    return {
        "person": person,
        "topic_title": topic_title,
        "rounds": len(collected),
        "queries": bundle["queries"],
        "search_files": [r["file"] for r in collected],
        "bundle_file": str(bundle_path),
        "bundle": bundle,
        # legacy fields for older compose
        "bullets": bundle.get("facts", [])[:12],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Multi-round volc research for entertainment articles")
    p.add_argument("--person", required=True)
    p.add_argument("--topic", required=True, help="Hot search title")
    p.add_argument("--stamp", default=datetime.now(BJ).strftime("%Y%m%d"))
    p.add_argument("--rounds", type=int, default=4, choices=[2, 3, 4])
    p.add_argument("--count", type=int, default=8, help="Per-round result count (both rounds)")
    p.add_argument("--broad-count", type=int, default=0, help="R1 count; 0 = use --count")
    p.add_argument("--deep-count", type=int, default=0, help="R2 count; 0 = use --count")
    p.add_argument("--json-out", default="")
    args = p.parse_args()

    if not __import__("os").environ.get("VOLC_SEARCH_API_KEY"):
        print("Missing VOLC_SEARCH_API_KEY", file=sys.stderr)
        sys.exit(1)

    bc = args.broad_count or None
    dc = args.deep_count or None
    result = asyncio.run(
        research(
            args.person,
            args.topic,
            stamp=args.stamp,
            rounds=args.rounds,
            count=args.count,
            broad_count=bc,
            deep_count=dc,
        )
    )
    # shrink bundle in stdout (full in bundle_file)
    slim = {k: v for k, v in result.items() if k != "bundle"}
    slim["facts_count"] = len(result.get("bundle", {}).get("facts", []))
    slim["numbers"] = result.get("bundle", {}).get("numbers", [])[:6]
    out = json.dumps(slim, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(out)


if __name__ == "__main__":
    main()
