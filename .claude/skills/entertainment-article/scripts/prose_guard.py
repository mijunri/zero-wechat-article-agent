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
]

_BROKEN_TAIL = re.compile(r"[，,]?\s*[\"\"」』]\s*$")
_BROKEN_HEAD = re.compile(r'^[\s，,。\"\"「『]+')


def guard_prose(text: str) -> str:
    t = (text or "").strip()
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
    return True
