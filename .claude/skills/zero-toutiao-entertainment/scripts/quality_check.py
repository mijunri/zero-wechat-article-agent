#!/usr/bin/env python3
"""Quality gate before publishing Toutiao entertainment articles."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from entertainment_filter import ENTERTAINMENT_EXCLUDE, entertainment_score

MIN_CHARS = 500
MAX_CHARS = 2200
MIN_TITLE = 8
MAX_TITLE = 32


def check_article(article: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    title = (article.get("title") or "").strip()
    if not (MIN_TITLE <= len(title) <= MAX_TITLE):
        issues.append(f"title length {len(title)} not in [{MIN_TITLE},{MAX_TITLE}]")
    if entertainment_score(title) < 1:
        issues.append("title looks non-entertainment or blocked")
    for bad in ENTERTAINMENT_EXCLUDE:
        if bad in title:
            issues.append(f"title contains blocked keyword: {bad}")

    chars = int(article.get("char_count") or 0)
    if chars < MIN_CHARS:
        issues.append(f"body too short: {chars} < {MIN_CHARS}")
    if chars > MAX_CHARS:
        issues.append(f"body too long: {chars} > {MAX_CHARS}")

    html_body = article.get("content_html") or ""
    if "<p>" not in html_body:
        issues.append("missing HTML paragraphs")
    if not article.get("source_url"):
        issues.append("missing source_url")

    # Avoid empty hype-only titles
    if re.fullmatch(r"[！!？?…\s]+", title):
        issues.append("title is punctuation only")

    return (len(issues) == 0, issues)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--article-json", required=True)
    args = p.parse_args()
    article = json.loads(Path(args.article_json).read_text(encoding="utf-8"))
    ok, issues = check_article(article)
    result = {"ok": ok, "issues": issues}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
