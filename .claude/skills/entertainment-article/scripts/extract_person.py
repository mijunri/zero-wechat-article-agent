#!/usr/bin/env python3
"""Extract celebrity/person name from a hot-search title."""
from __future__ import annotations

import re

# Common 2-4 han names at start; extend as needed
_NAME_PREFIX = re.compile(
    r"^([\u4e00-\u9fff]{2,4})(?:说|称|晒|被|与|和|的|在|回应|否认|官宣|离婚|结婚|孕|塌|遭|因)"
)

_STRIP_SUFFIX = re.compile(
    r"(上热搜|引热议|冲上热搜|爆了|炸了|火了|回应|否认|官宣|最新|曝光).*$"
)


def extract_person(title: str) -> str:
    t = (title or "").strip()
    t = _STRIP_SUFFIX.sub("", t)
    m_photo = re.search(r"([\u4e00-\u9fff]{2,3})婚纱照", t)
    if m_photo:
        return m_photo.group(1)
    m_pair = re.match(r"^([\u4e00-\u9fff]{2,4})([\u4e00-\u9fff]{2,4})", t)
    if m_pair and len(m_pair.group(1)) >= 2 and len(m_pair.group(2)) >= 2:
        return m_pair.group(1)
    m = _NAME_PREFIX.match(t)
    if m:
        return m.group(1)
    # "奚梦瑶结束婚礼" → 奚梦瑶
    m2 = re.match(r"^([\u4e00-\u9fff]{2,3})(?=[不敢也被曾在与和的是])", t)
    if m2:
        return m2.group(1)
    m2 = re.match(r"^([\u4e00-\u9fff]{2,4})", t)
    if m2:
        name = m2.group(1)
        if name.endswith(("不", "也", "被", "曾", "在", "与", "和", "的", "是")):
            return name[:-1]
        return name
    return t[:3] if len(t) >= 3 else t


def topic_keywords(title: str, person: str) -> str:
    t = title.replace(person, "").strip()
    t = re.sub(r"[：:，,！!？?]", " ", t)
    parts = [p for p in t.split() if len(p) >= 2]
    return " ".join(parts[:4]) if parts else title[:12]
