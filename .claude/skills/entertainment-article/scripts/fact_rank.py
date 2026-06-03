#!/usr/bin/env python3
"""Rank and filter research facts — drop encyclopedia junk, prefer event-relevant snippets."""
from __future__ import annotations

import re
from typing import Any

# 百科/目录/个人资料页特征 — 成稿时直接丢弃
JUNK_MARKERS = (
    "个人资料",
    "个人介绍",
    "目录序言",
    "抖音百科",
    "搜狗百科",
    "字典网",
    "百度百科",
    "国籍是",
    "外文名",
    "毕业院校",
    "出生日期",
    "出生地是",
    "任职机构",
    "人物经历",
    "求学经历",
    "更新时间:",
    "1、何猷君",
    "2、何猷君",
    "身高 ",
    "配偶 ",
    "母校 ",
    "微博认证",
    "军事博主",
    "龙江县",
    "参考资料",
    "生活经历1.1",
)

BIO_MARKERS = (
    "出生于",
    "毕业于",
    "担任",
    "创始人",
    "董事长",
    "政协委员",
    "数学精英",
    "世界数学",
)


def event_keywords(hot_title: str, person: str) -> list[str]:
    t = (hot_title or "").replace(person, "").strip()
    t = re.sub(r"[：:，,！!？?「」\"\"'' ]+", " ", t)
    words: list[str] = []
    for w in re.findall(r"[\u4e00-\u9fff]{2,8}", t):
        if w in ("没有", "一个", "怎么", "什么", "为何", "回应", "最新"):
            continue
        if w not in words:
            words.append(w)
    if not words:
        words = [hot_title[:12]]
    return words[:6]


def is_junk(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 12:
        return True
    if any(m in t for m in JUNK_MARKERS):
        return True
    # 目录式碎片
    if t.count("1.") + t.count("1、") + t.count("2.") > 2:
        return True
    if re.search(r"[\u4e00-\u9fff]{2,4}[\u4e00-\u9fff]{2,4}[\u4e00-\u9fff]{2,4}", t) and "目录" in t:
        return True
    return False


def is_bio_heavy(text: str, person: str) -> bool:
    t = text or ""
    hits = sum(1 for m in BIO_MARKERS if m in t)
    # 纯履历堆砌：多个职位/学历且无事件动词
    event_verbs = ("婚礼", "誓词", "回应", "网友", "评论", "热搜", "曝光", "说", "称", "晒")
    has_event = any(v in t for v in event_verbs)
    if hits >= 3 and not has_event:
        return True
    if person and t.count(person) >= 2 and hits >= 2 and not has_event:
        return True
    return False


def score_fact(text: str, keywords: list[str], person: str) -> int:
    if is_junk(text) or is_bio_heavy(text, person):
        return -100
    t = text or ""
    score = 0
    for kw in keywords:
        if kw in t:
            score += 8
    if person and person in t:
        score += 2
    for v in ("婚礼", "誓词", "回应", "网友", "评论", "原话", "采访", "表示", "称", "说"):
        if v in t:
            score += 3
    # 更像人话的句子长度
    if 40 <= len(t) <= 220:
        score += 2
    if len(t) > 400:
        score -= 3
    return score


def rank_facts(facts: list[str], hot_title: str, person: str, *, limit: int = 8) -> list[str]:
    kws = event_keywords(hot_title, person)
    scored: list[tuple[int, str]] = []
    seen: set[str] = set()
    for f in facts:
        f = re.sub(r"\s+", " ", (f or "").strip())
        key = f[:60]
        if not f or key in seen:
            continue
        seen.add(key)
        s = score_fact(f, kws, person)
        if s > 0:
            scored.append((s, f))
    scored.sort(key=lambda x: -x[0])
    return [f for _, f in scored[:limit]]


def clean_snippet(text: str) -> str:
    t = (text or "").strip()
    t = re.sub(r"本文作者[：:][^\n。]*", "", t)
    t = re.sub(r"图片来源于网络[^\n。]*", "", t)
    t = re.sub(r"图片来源于微博[^\n。]*", "", t)
    t = re.sub(r"网络图片[^\n。]*", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def pick_sentences(text: str, *, min_len: int = 18, max_len: int = 100) -> list[str]:
    out: list[str] = []
    for part in re.split(r"[。！？\n]", clean_snippet(text)):
        part = re.sub(r"\s+", " ", part.strip())
        if min_len <= len(part) <= max_len and not is_junk(part):
            if not is_bio_heavy(part, ""):
                out.append(part)
    return out


def merge_facts_to_paragraphs(
    facts: list[str],
    person: str,
    *,
    max_paras: int = 3,
    sents_per_para: int = 2,
) -> list[str]:
    """Turn ranked facts into readable narrative paragraphs (not one-fact-one-block)."""
    paras: list[str] = []
    pool: list[str] = []
    for f in facts:
        pool.extend(pick_sentences(f))
    seen: set[str] = set()
    unique: list[str] = []
    for s in pool:
        k = s[:40]
        if k in seen:
            continue
        seen.add(k)
        unique.append(s)
    i = 0
    while i < len(unique) and len(paras) < max_paras:
        chunk = unique[i : i + sents_per_para]
        i += sents_per_para
        if not chunk:
            break
        body = "。".join(chunk) + "。"
        if person and person not in body:
            body = f"{person}这边，{body}"
        paras.append(body)
    return paras
