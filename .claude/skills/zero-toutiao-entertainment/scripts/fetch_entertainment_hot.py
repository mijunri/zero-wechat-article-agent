#!/usr/bin/env python3
"""Aggregate entertainment hot topics from weibo + douyin (+ toutiao fallback)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR / "hot-topics" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from entertainment_filter import rank_entertainment_items  # noqa: E402
from fetch_platform import fetch  # noqa: E402


def aggregate(*, limit: int = 30) -> dict:
    merged: list[dict] = []
    seen_titles: set[str] = set()
    for platform in ("weibo", "douyin", "toutiao"):
        batch = fetch(platform)["items"]
        for item in batch:
            title = (item.get("title") or "").strip()
            key = title[:40]
            if not title or key in seen_titles:
                continue
            seen_titles.add(key)
            merged.append(item)

    ranked = rank_entertainment_items(merged)
    return {
        "sources": ["weibo", "douyin", "toutiao"],
        "total_scanned": len(merged),
        "entertainment_count": len(ranked),
        "items": ranked[:limit],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--json-out", default="")
    args = p.parse_args()
    result = aggregate(limit=args.limit)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(out, encoding="utf-8")
        print(f"Wrote {len(result['items'])} items to {args.json_out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
