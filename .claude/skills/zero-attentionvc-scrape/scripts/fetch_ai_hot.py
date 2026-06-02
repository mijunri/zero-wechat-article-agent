#!/usr/bin/env python3
"""Fetch hot AI articles from AttentionVC leaderboard API."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.attentionvc.ai/v1/articles/leaderboard"
VALID_PERIODS = frozenset({"24h", "7d", "14d", "all"})


def _fetch(category: str, period: str, lang: str) -> dict:
    params = urllib.parse.urlencode({"category": category, "period": period, "lang": lang})
    url = f"{API_URL}?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "zero-wechat-article-agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def _normalize_entry(raw: dict) -> dict:
    author = raw.get("author") or {}
    tweet_id = raw.get("tweetId", "")
    return {
        "rank": raw.get("rank"),
        "title": raw.get("title"),
        "preview_text": raw.get("previewText"),
        "view_count": raw.get("viewCount"),
        "like_count": raw.get("likeCount"),
        "retweet_count": raw.get("retweetCount"),
        "tweet_created_at": raw.get("tweetCreatedAt"),
        "tweet_url": f"https://x.com/i/status/{tweet_id}" if tweet_id else None,
        "author_handle": author.get("handle"),
        "author_name": author.get("name"),
        "author_followers": author.get("followers"),
        "cover_image_url": raw.get("coverImageUrl"),
        "tags": raw.get("tags") or [],
        "trending_topics": raw.get("trendingTopics") or [],
        "subcategory": raw.get("subcategory"),
        "reading_time_minutes": raw.get("readingTimeMinutes"),
    }


def fetch_hot(*, period: str, lang: str, limit: int, category: str = "ai") -> dict:
    if period not in VALID_PERIODS:
        raise ValueError(f"period must be one of {sorted(VALID_PERIODS)}")
    data = _fetch(category, period, lang)
    entries = data.get("entries") or []
    articles = [_normalize_entry(e) for e in entries[:limit]]
    return {
        "category": category,
        "period": period,
        "lang": lang,
        "count": len(articles),
        "total_count": data.get("totalCount"),
        "updated_at": data.get("updatedAt"),
        "articles": articles,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="AttentionVC AI hot articles")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--period", default="7d", choices=sorted(VALID_PERIODS))
    f.add_argument("--lang", default="en,zh")
    f.add_argument("--limit", type=int, default=30)
    f.add_argument("--category", default="ai")
    f.add_argument("--json-out", default="")
    args = p.parse_args()

    result = fetch_hot(period=args.period, lang=args.lang, limit=args.limit, category=args.category)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"Wrote {result['count']} articles to {args.json_out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
