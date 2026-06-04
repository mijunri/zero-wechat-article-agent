#!/usr/bin/env python3
"""Oral / 活人感 pass — strip essay tone, add chat rhythm."""
from __future__ import annotations

import re

# 论文化 → 口语化
_SWAP = [
    (r"阶层差异一眼看穿", "阶层那味儿藏不住"),
    (r"阶层差异", "那股阶层味儿"),
    (r"两套人生坐标系", "两套话术"),
    (r"风险共担", "一块儿扛事儿"),
    (r"「匮乏」这件事本身", "「穷」这档事儿"),
    (r"匮乏", "穷日子"),
    (r"公共仪式", "这种场合"),
    (r"众生平等", "跟大家站在一边"),
    (r"潜台词", "意思"),
    (r"话术", "说法"),
    (r"语境太硬", "听着太硬"),
    (r"祝福可以是真心的", "甜可能是真的甜"),
    (r"这才是梗能传开的理由", "所以梗才传得动"),
    (r"又一次显形", "又露馅一回"),
    (r"签了合作条款", "像商务回复"),
]


def humanize(text: str) -> str:
    t = (text or "").strip()
    for pat, repl in _SWAP:
        t = re.sub(pat, repl, t)
    # 过长句子拆一点口语停顿
    t = re.sub(r"——", "，", t)
    if t.count("。") == 0 and len(t) > 40:
        t = re.sub(r"，([^，]{20,}?)([。]|$)", r"。\1", t, count=1)
    return t.strip()
