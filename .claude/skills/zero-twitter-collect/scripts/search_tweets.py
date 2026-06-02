#!/usr/bin/env python3
"""Search tweets via TwitterAPI.io advanced_search."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"


def _api_key() -> str:
    key = os.environ.get("twitter_api_key", "").strip()
    if not key:
        print("Set environment variable twitter_api_key", file=sys.stderr)
        sys.exit(1)
    return key


def _request(query: str, query_type: str, cursor: str = "") -> dict:
    params = {"query": query, "queryType": query_type}
    if cursor:
        params["cursor"] = cursor
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"X-API-Key": _api_key()})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def _normalize_tweet(raw: dict) -> dict:
    author = raw.get("author") or {}
    return {
        "id": raw.get("id"),
        "url": raw.get("url") or raw.get("twitterUrl"),
        "text": raw.get("text"),
        "created_at": raw.get("createdAt"),
        "lang": raw.get("lang"),
        "like_count": raw.get("likeCount"),
        "retweet_count": raw.get("retweetCount"),
        "reply_count": raw.get("replyCount"),
        "view_count": raw.get("viewCount"),
        "author": {
            "username": author.get("userName"),
            "name": author.get("name"),
            "followers": author.get("followers"),
        },
    }


def search(query: str, query_type: str, limit: int) -> dict:
    tweets: list[dict] = []
    cursor = ""
    while len(tweets) < limit:
        data = _request(query, query_type, cursor)
        batch = data.get("tweets") or []
        if not batch:
            break
        for t in batch:
            tweets.append(_normalize_tweet(t))
            if len(tweets) >= limit:
                break
        if not data.get("has_next_page") or not data.get("next_cursor"):
            break
        cursor = data["next_cursor"]
    return {
        "query": query,
        "query_type": query_type,
        "count": len(tweets),
        "tweets": tweets[:limit],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="TwitterAPI.io topic search")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="Advanced search tweets")
    s.add_argument("--query", required=True)
    s.add_argument("--query-type", default="Top", choices=["Top", "Latest"])
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json-out", default="")
    args = p.parse_args()

    result = search(args.query, args.query_type, args.limit)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        path = args.json_out
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {result['count']} tweets to {path}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
