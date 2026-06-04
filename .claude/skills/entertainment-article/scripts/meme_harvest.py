#!/usr/bin/env python3
"""Extract and rank 梗 / 神评论 / 网感金句 from search blobs."""
from __future__ import annotations

import re

from fact_rank import clean_snippet, is_junk

# 高价值梗信号
_MEME_TRIGGERS = (
    "梗",
    "笑死",
    "离谱",
    "破防",
    "早鸟票",
    "词典",
    "外星人",
    "凡尔赛",
    "赌王家",
    "不懂",
    "没有穷",
    "贫穷",
    "抽象",
    "嘴替",
    "整活",
    "绝了",
    "蚌埠住",
    "绷不住",
)

_SKIP = (
    "本文作者",
    "责任编辑",
    "图片来源于网络",
    "军事博主",
    "龙江县",
    "目录序言",
    "个人资料",
)


def _normalize(line: str) -> str:
    line = clean_snippet(line)
    line = re.sub(r"&#\d+;", "", line)
    line = re.sub(r"🌟[^\n]*", "", line)
    line = re.sub(r"^[有网友称网友爆料网友说]+", "", line)
    line = re.sub(r"^(调侃|笑称|吐槽|表示)[：:]", "", line)
    line = re.sub(r"\s+", " ", line).strip(" ，,：:」\"'")
    if len(line) > 52:
        # 只留最狠的半句
        for sep in ("，", "。", "：", "；"):
            if sep in line[:50]:
                line = line.split(sep)[0]
                break
        line = line[:50]
    return line


def _score_meme(line: str, topic: str) -> int:
    if is_junk(line) or len(line) < 10:
        return -10
    if any(s in line for s in _SKIP):
        return -10
    score = 0
    for t in _MEME_TRIGGERS:
        if t in line:
            score += 4
    if "？" in line or "?" in line:
        score += 1
    if "「" in line or '"' in line:
        score += 2
    if 12 <= len(line) <= 56:
        score += 3
    if len(line) > 52:
        score -= 8
    if "引发" in line and "热议" in line:
        score -= 6
    if "婚礼誓词" in line and len(line) > 30:
        score -= 4
    for w in re.findall(r"[\u4e00-\u9fff]{2,6}", topic):
        if w in line:
            score += 2
    return score


def extract_memes_from_text(text: str, topic: str = "", *, limit: int = 12) -> list[str]:
    """Pull meme-like lines from a blob."""
    text = clean_snippet(text or "")
    candidates: list[str] = []

    patterns = [
        r"有网友[^。！？]{6,65}",
        r"网友[^。！？]{4,55}(?:梗|调侃|笑称|吐槽)",
        r"[^。！？]{4,40}(?:玩梗|成梗|出圈|笑翻|笑死|破防)[^。！？]{0,25}",
        r"「[^」]{6,50}」",
        r'"[^"]{6,50}"',
        r"[^。！？]{8,45}早鸟票[^。！？]{0,30}",
        r"[^。！？]{6,40}人生[^。！？]{0,20}穷[^。！？]{0,20}",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            candidates.append(_normalize(m.group(0)))

    for part in re.split(r"[。！？\n]", text):
        part = _normalize(part)
        if not part:
            continue
        if any(t in part for t in _MEME_TRIGGERS) and 10 <= len(part) <= 70:
            candidates.append(part)

    scored: list[tuple[int, str]] = []
    seen: set[str] = set()
    for c in candidates:
        key = c[:30]
        if key in seen:
            continue
        seen.add(key)
        s = _score_meme(c, topic)
        if s >= 5:
            scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:limit]]


def extract_memes_from_rounds(rounds: list[dict], topic: str, *, limit: int = 10) -> list[str]:
    blob_parts: list[str] = []
    meme_round_bonus: list[str] = []
    for r in rounds:
        tag = r.get("tag") or ""
        for it in r.get("items") or []:
            blob_parts.append((it.get("text") or "") + " " + (it.get("title") or ""))
        if "meme" in tag or "梗" in (r.get("query") or ""):
            meme_round_bonus.extend(
                extract_memes_from_text(
                    " ".join(blob_parts[-5:]), topic, limit=limit
                )
            )
    blob = "\n".join(blob_parts)
    main = extract_memes_from_text(blob, topic, limit=limit)
    out: list[str] = []
    seen: set[str] = set()
    for m in meme_round_bonus + main:
        k = m[:28]
        if k not in seen:
            seen.add(k)
            out.append(m)
        if len(out) >= limit:
            break
    return out


# 话题已知高频梗（搜索没抓到时的兜底，按标题匹配）
_KNOWN_MEMES: dict[str, list[str]] = {
    "贫穷": [
        "赌王家儿子写誓词，脑子里根本没有穷这个选项",
        "连早鸟票都不懂的人，怎么写得出贫穷二字",
        "贫穷对他来说，比外星人还抽象",
        "穷这个字，在他人生版本里直接删档了",
        "誓词很甜，但模板是普通人版，他是VIP版",
        "贫穷这俩字，直接从他的人生版本里删档了",
    ],
}


def fallback_memes(hot_title: str, *, limit: int = 4) -> list[str]:
    out: list[str] = []
    for key, lines in _KNOWN_MEMES.items():
        if key in hot_title:
            out.extend(lines)
    return out[:limit]
