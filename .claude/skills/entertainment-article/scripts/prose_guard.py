#!/usr/bin/env python3
"""Strip forbidden news-desk phrasing from entertainment copy."""
from __future__ import annotations

import re

# 成稿硬性禁用 — 同步维护 entertainment-article/SKILL.md
_FORBIDDEN = [
    (re.compile(r"据[^，。！？\n]{1,28}?(?:报道|消息|透露|称)[，,]?\s*"), ""),
    (re.compile(r"据报道[，,]?\s*"), ""),
    (re.compile(r"有媒体(?:报道|称)[，,]?\s*"), ""),
    (re.compile(r"#[\u4e00-\u9fff\w]+#"), ""),
    (re.compile(r"登上热议[，,]?\s*"), ""),
    (re.compile(r"引发全网热议[，,]?\s*"), ""),
    (re.compile(r"口径以原报道为准[。.]?"), ""),
    (re.compile(r"报道里(?:还)?提到[，,]?\s*"), ""),
    (re.compile(r"公开信息整理\s*\+\s*编辑判断"), "编辑整理"),
    (re.compile(r"你咋看[？?]?"), ""),
    (re.compile(r"欢迎评论区[^。]*[。.]?"), ""),
    (re.compile(r"评论区见[^。]*[。.]?"), ""),
    (re.compile(r"你品品[，,]"), ""),
    (re.compile(r"评论区[^。]{0,20}(?:一句话|总结)[，,]?"), ""),
]

_BROKEN_TAIL = re.compile(r"[，,]?\s*[\"\"」』]\s*$")
_BROKEN_HEAD = re.compile(r'^[\s，,。\"\"「『]+')

# 全文禁止：不是 A，而是/是 B（对仗腔）
_CONTRAST_PATTERNS = [
    re.compile(r"不是[^，。！？\n]{1,36}?，\s*而是"),
    re.compile(r"不是[^，。！？\n]{1,36}?，\s*是(?!说|否|吗|吧|呀|啊|呢|的|人)"),
    re.compile(r"往往不是[^，。！？\n]{1,24}?，\s*是"),
    re.compile(r"删的不是[^，。！？\n]{1,20}?，\s*是"),
]


def find_contrast_violations(text: str) -> list[str]:
    hits: list[str] = []
    for pat in _CONTRAST_PATTERNS:
        for m in pat.finditer(text or ""):
            hits.append(m.group(0))
    return hits


def ban_contrast_rhythm(text: str) -> str:
    """Rewrite or strip 不是…而是/不是…是."""
    t = text or ""
    subs = [
        (r"不是说不甜，是听着太硬", "甜可能有，但听着太硬"),
        (r"不是故意恶心谁，是", "没想着恶心谁，"),
        (r"往往不是真相，是", "留人的常常是"),
        (r"删的不是一个词，是", "删掉的是"),
        (r"不是([^，。]{1,20})，而是", r"\1，"),
        (r"不是([^，。]{1,20})，是(?!说)", r"\1，"),
    ]
    for pat, repl in subs:
        t = re.sub(pat, repl, t)
    return t


def guard_prose(text: str) -> str:
    t = (text or "").strip()
    t = ban_contrast_rhythm(t)
    for pat, repl in _FORBIDDEN:
        t = pat.sub(repl, t)
    t = re.sub(r"\s+", " ", t).strip()
    t = _BROKEN_HEAD.sub("", t)
    t = _BROKEN_TAIL.sub("。", t)
    t = re.sub(r"。{2,}", "。", t)
    return t


def paragraph_ok(text: str) -> bool:
    t = text or ""
    if len(t) < 15:
        return False
    if "据" in t and "报道" in t:
        return False
    if t.count("“") != t.count("”"):
        return False
    if "#" in t and t.count("#") >= 2:
        return False
    if re.search(r"[，,]\s*[\"\"」』]\s*$", t):
        return False
    if find_contrast_violations(t):
        return False
    return True
