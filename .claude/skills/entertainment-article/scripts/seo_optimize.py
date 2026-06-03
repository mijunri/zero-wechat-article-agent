#!/usr/bin/env python3
"""SEO helpers for Toutiao / WeChat search — title, headings, entity density."""
from __future__ import annotations

import re
from typing import Any

HOLLOW = re.compile(r"(震惊|竟然|万万没想到|不看后悔|速看|炸了|爆了)")
HAN = re.compile(r"[\u4e00-\u9fff]")


def normalize_person(person: str, hot_title: str) -> str:
    """Fix truncated names like 何猷君婚 → 何猷君."""
    p = (person or "").strip()
    if not p:
        return p
    if hot_title and p in hot_title:
        # 人名是热搜子串且后面还有字 → 可能截断
        idx = hot_title.find(p)
        if idx == 0 and len(p) >= 3:
            rest = hot_title[len(p) :]
            if rest and rest[0] in "婚礼视频回应官宣":
                for name_len in (3, 2):
                    cand = hot_title[:name_len]
                    if len(cand) >= 2 and cand in hot_title:
                        return cand
    if len(p) > 3 and p[-1] in "婚礼视频剧":
        return p[:-1]
    return p


def seo_title(person: str, hot_title: str, bundle: dict[str, Any]) -> str:
    candidates = list(bundle.get("title_candidates") or [])
    candidates.insert(0, hot_title)
    if person and person not in hot_title:
        candidates.insert(0, f"{person}：{hot_title}")
    for t in candidates:
        t = (t or "").strip()
        if 10 <= len(t) <= 28 and person in t:
            return t
        if 8 <= len(t) <= 30:
            return t[:28]
    base = hot_title or f"{person}最新动态"
    if person and person not in base:
        base = f"{person}{base}"
    return base[:28] if len(base) > 28 else base


def seo_lead(person: str, hot_title: str, hot_value: int | None, numbers: list[str]) -> str:
    heat = ""
    if hot_value and hot_value > 30_000:
        heat = f"话题热度约 {hot_value // 10000} 万。"
    num = f"公开报道里提到{numbers[0]}。" if numbers else ""
    return (
        f"{person}因「{hot_title}」登上热搜。{heat}{num}"
        f"下面按时间线把目前能核实的公开信息捋清楚。"
    )


def seo_h2_facts(person: str) -> str:
    return f"{person}这件事：目前已知的关键信息"


def seo_h2_quotes(person: str) -> str:
    return f"{person}方面怎么说"


def count_han(text: str) -> int:
    return len(HAN.findall(text))


def score_seo(
    *,
    title: str,
    person: str,
    plain_body: str,
    h2_texts: list[str],
    char_count: int,
    min_chars: int = 800,
) -> dict[str, Any]:
    issues: list[str] = []
    score = 0

    tl = len(title)
    if 12 <= tl <= 28:
        score += 2
    elif 8 <= tl <= 30:
        score += 1
    else:
        issues.append("title_length")

    if person and person in title:
        score += 3
    else:
        issues.append("person_in_title")

    head = plain_body[:120]
    if person and person in head:
        score += 2
    else:
        issues.append("person_in_lead")

    if any(person in h for h in h2_texts if person):
        score += 2
    else:
        issues.append("person_in_h2")

    if char_count >= min_chars:
        score += 2
    else:
        issues.append("body_length")

    if person:
        n = plain_body.count(person)
        if 3 <= n <= 12:
            score += 1
        elif n < 3:
            issues.append("person_density_low")

    if not HOLLOW.search(title + plain_body[:500]):
        score += 1
    else:
        issues.append("hollow_words")

    grade = "good" if score >= 10 else "needs_work"
    return {
        "seo_score": score,
        "seo_max": 13,
        "seo_grade": grade,
        "issues": issues,
        "title_len": tl,
        "person_mentions": plain_body.count(person) if person else 0,
    }
