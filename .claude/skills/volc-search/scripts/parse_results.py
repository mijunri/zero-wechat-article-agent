"""Parse Volcano web_search JSON into structured research items."""
from __future__ import annotations

import re
from typing import Any


def parse_web_results(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in data.get("WebResults") or []:
        summary = (item.get("Summary") or item.get("Snippet") or "").strip()
        snippet = (item.get("Snippet") or "").strip()
        rows.append(
            {
                "title": (item.get("Title") or "").strip(),
                "url": (item.get("Url") or "").strip(),
                "site": (item.get("SiteName") or "").strip(),
                "summary": summary,
                "snippet": snippet,
                "publish_time": (item.get("PublishTime") or "").strip(),
                "text": summary or snippet,
            }
        )
    return [r for r in rows if r.get("text") or r.get("title")]


_NUM_PAT = re.compile(
    r"(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?:万|亿|元|岁|年|月|日|天|次|场|集|部|人|斤|克|米|公里|%|％)?"
)


def extract_numbers(text: str, *, limit: int = 12) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for m in _NUM_PAT.finditer(text or ""):
        s = m.group(0)
        if s in seen or len(s) < 2:
            continue
        seen.add(s)
        found.append(s)
        if len(found) >= limit:
            break
    return found


_QUOTE_PAT = re.compile(r"[「『\"](.{4,80}?)[」』\"]|[：:]\s*([^\n。]{8,60})")


def extract_quotes(text: str, person: str = "", *, limit: int = 6) -> list[str]:
    quotes: list[str] = []
    for block in re.split(r"[。！？\n]", text or ""):
        block = block.strip()
        if not block or len(block) < 10:
            continue
        if person and person in block and ("说" in block or "表示" in block or "回应" in block):
            quotes.append(block[:120])
        elif "：" in block and len(block) < 100:
            quotes.append(block[:120])
        if len(quotes) >= limit:
            break
    return quotes[:limit]


def merge_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for it in items:
        key = (it.get("text") or "")[:80]
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
