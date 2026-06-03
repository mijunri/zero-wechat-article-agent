"""Score and filter entertainment-only hot topics."""
from __future__ import annotations

import re
from typing import Any

# Strong entertainment signals
ENTERTAINMENT_INCLUDE = (
    "明星",
    "艺人",
    "演员",
    "歌手",
    "爱豆",
    "偶像",
    "网红",
    "综艺",
    "真人秀",
    "选秀",
    "浪姐",
    "披荆斩棘",
    "剧",
    "影视",
    "电影",
    "电视剧",
    "番剧",
    "动漫",
    "票房",
    "首映",
    "杀青",
    "官宣",
    "恋情",
    "分手",
    "离婚",
    "结婚",
    "婚礼",
    "婚纱",
    "备孕",
    "出轨",
    "八卦",
    "爆料",
    "红毯",
    "演唱会",
    "音乐节",
    "粉丝",
    "应援",
    "CP",
    "塌房",
    "热搜",
    "娱乐",
    "奚梦瑶",
    "何猷君",
    "丁程鑫",
    "张智霖",
    "文彩元",
)

# Hard exclude: politics, macro news, public safety, finance policy
ENTERTAINMENT_EXCLUDE = (
    "美国",
    "国务院",
    "外交",
    "军事",
    "战争",
    "贸易",
    "检察",
    "公诉",
    "纪委",
    "政府",
    "央行",
    "公积金",
    "高考",
    "暴雨",
    "预警",
    "运河",
    "机场",
    "辟谣",
    "足球",
    "NBA",
    "经济",
    "GDP",
    "人民币",
    "对话",
    "会晤",
    "总统",
    "总理",
    "部长",
    "省委",
    "市委",
    "调研",
    "部署",
    "强国",
    "一带一路",
)


def entertainment_score(title: str) -> int:
    t = (title or "").strip()
    if not t:
        return -99
    score = 0
    for kw in ENTERTAINMENT_INCLUDE:
        if kw in t:
            score += 2
    for kw in ENTERTAINMENT_EXCLUDE:
        if kw in t:
            score -= 8
    # Variety / celebrity gossip patterns
    if re.search(r"(恋|婚|离|孕|塌|瓜|剧透|淘汰|官宣)", t):
        score += 2
    if re.search(r"(token|AI|大模型|公司烧不起)", t, re.I):
        score -= 6
    return score


def is_entertainment(title: str, *, min_score: int = 2) -> bool:
    return entertainment_score(title) >= min_score


def rank_entertainment_items(items: list[dict[str, Any]], *, min_score: int = 2) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for item in items:
        title = str(item.get("title") or "")
        sc = entertainment_score(title)
        if sc < min_score:
            continue
        row = dict(item)
        row["entertainment_score"] = sc
        ranked.append(row)
    ranked.sort(
        key=lambda x: (x.get("entertainment_score", 0), int(x.get("hot_value") or 0)),
        reverse=True,
    )
    return ranked
