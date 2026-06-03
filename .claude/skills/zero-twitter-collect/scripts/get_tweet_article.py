#!/usr/bin/env python3
"""Fetch full X/Twitter article (long post) by tweet id via TwitterAPI.io."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://api.twitterapi.io/twitter/article"


def _api_key() -> str:
    key = os.environ.get("twitter_api_key", "").strip()
    if not key:
        print("Set twitter_api_key in scripts/agent.env", file=sys.stderr)
        sys.exit(1)
    return key


def _request(tweet_id: str) -> dict:
    url = f"{API_URL}?{urllib.parse.urlencode({'tweet_id': tweet_id})}"
    req = urllib.request.Request(url, headers={"X-API-Key": _api_key()})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def _contents_to_text(contents: list[dict]) -> str:
    parts: list[str] = []
    for block in contents or []:
        btype = block.get("type") or ""
        text = (block.get("text") or "").strip()
        if btype == "header-two" and text:
            parts.append(f"\n## {text}\n")
        elif btype == "header-three" and text:
            parts.append(f"\n### {text}\n")
        elif btype in ("unordered-list-item", "ordered-list-item") and text:
            parts.append(f"- {text}")
        elif btype == "blockquote" and text:
            parts.append(f"> {text}")
        elif btype == "image":
            continue
        elif text:
            parts.append(text)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip()


def _extract_images(contents: list[dict]) -> list[str]:
    urls: list[str] = []
    for block in contents or []:
        if block.get("type") == "image" and block.get("url"):
            urls.append(str(block["url"]))
    return urls


def normalize_article(raw: dict) -> dict:
    article = raw.get("article") or raw
    contents = article.get("contents") or []
    author = article.get("author") or {}
    tweet_id = ""
    if article.get("id"):
        pass
    return {
        "tweet_id": article.get("tweet_id") or "",
        "title": article.get("title") or "",
        "preview_text": article.get("preview_text") or "",
        "full_text": _contents_to_text(contents),
        "image_urls": _extract_images(contents),
        "cover_url": article.get("cover_media_img_url") or "",
        "author_username": author.get("userName") or author.get("username") or "",
        "author_name": author.get("name") or "",
        "view_count": article.get("viewCount"),
        "like_count": article.get("likeCount"),
        "reply_count": article.get("replyCount"),
        "created_at": article.get("createdAt"),
        "contents_blocks": len(contents),
    }


def fetch_article(tweet_id: str) -> dict:
    data = _request(tweet_id.strip())
    out = normalize_article(data)
    out["tweet_id"] = tweet_id.strip()
    out["tweet_url"] = f"https://x.com/i/status/{tweet_id.strip()}"
    if not out["full_text"] and out["preview_text"]:
        out["full_text"] = out["preview_text"]
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Get Twitter/X article by tweet id")
    p.add_argument("--tweet-id", required=True)
    p.add_argument("--json-out", default="")
    args = p.parse_args()
    result = fetch_article(args.tweet_id)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(out, encoding="utf-8")
        print(f"Wrote article ({len(result.get('full_text',''))} chars) to {args.json_out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
