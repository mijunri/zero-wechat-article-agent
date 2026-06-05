#!/usr/bin/env python3
"""Fetch hot topics from 60s.viki.moe (hot-topics skill)."""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

API_BASE = "https://60s.viki.moe/v2"

# 禁用 SSL 验证（用于 macOS 环境）
SSL_CONTEXT = ssl._create_unverified_context()

PLATFORMS = {
    "weibo": f"{API_BASE}/weibo",
    "zhihu": f"{API_BASE}/zhihu",
    "baidu": f"{API_BASE}/baidu/hot",
    "douyin": f"{API_BASE}/douyin",
    "toutiao": f"{API_BASE}/toutiao",
    "bili": f"{API_BASE}/bili",
}


def fetch(platform: str, *, timeout: int = 60) -> dict:
    if platform not in PLATFORMS:
        raise ValueError(f"platform must be one of {sorted(PLATFORMS)}")
    req = urllib.request.Request(
        PLATFORMS[platform],
        headers={"Accept": "application/json", "User-Agent": "zero-wechat-article-agent/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    items = data.get("data") or []
    normalized = []
    for i, row in enumerate(items, 1):
        normalized.append(
            {
                "rank": i,
                "platform": platform,
                "title": row.get("title") or row.get("name") or "",
                "url": row.get("link") or row.get("url") or "",
                "hot_value": row.get("hot_value") or row.get("热度") or row.get("heat") or 0,
                "cover": row.get("cover") or row.get("cover_url") or "",
            }
        )
    return {
        "platform": platform,
        "count": len(normalized),
        "items": normalized,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch platform hot list via 60s API")
    p.add_argument("platform", choices=sorted(PLATFORMS))
    p.add_argument("--json-out", default="")
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()
    result = fetch(args.platform)
    result["items"] = result["items"][: args.limit]
    result["count"] = len(result["items"])
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        from pathlib import Path

        Path(args.json_out).write_text(out, encoding="utf-8")
        print(f"Wrote {args.json_out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
