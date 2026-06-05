#!/usr/bin/env python3
"""头条号吸睛标题生成器：悬念/情绪/对比/代入/数字."""
from __future__ import annotations

import random
import re
from typing import Any

# 禁用词（会被限流）
BANNED = {
    "震惊", "曝光", "揭秘", "惊人", "不敢相信",
    "速看", "不看后悔", "炸了", "爆了", "塌房"
}


def _detect_topic_type(hot_title: str) -> str:
    """检测话题类型：恋情/婚礼/争议/其他."""
    if w := re.search(r"婚礼|婚纱|求婚|订婚", hot_title):
        return "wedding"
    if w := re.search(r"恋情|复合|约会|绯闻", hot_title):
        return "romance"
    if w := re.search(r"分手|离婚|出轨|辟谣|澄清|争议", hot_title):
        return "drama"
    return "general"


def _generate_titles_for_type(
    person: str,
    hot_title: str,
    topic_type: str,
    bundle: dict[str, Any] | None = None,
) -> list[str]:
    """根据话题类型生成标题."""

    titles = []

    # 婚礼类
    if topic_type == "wedding":
        titles.extend([
            f"{person}婚礼这事儿，现场比传言更有意思",
            f"{person}婚礼细节流出，这一幕有点真实",
            f"看完了{person}婚礼，说句实话",
            f"{person}婚礼镜头里，这几帧藏不住",
        ])

    # 恋情类
    elif topic_type == "romance":
        titles.extend([
            f"{person}这波操作，比传言还难猜",
            f"{person}恋情这事儿，换个角度捋一捋",
            f"吃明白了，{person}这事儿有点意思",
            f"{person}最新动态，这一幕有点真实",
        ])

    # 争议类
    elif topic_type == "drama":
        titles.extend([
            f"{person}这事儿，换个角度看",
            f"说句实话，{person}这事儿比传言复杂",
            f"{person}这波回应，有点意思",
            f"捋了一遍{person}这事儿，关键点在这",
        ])

    # 通用类
    else:
        titles.extend([
            f"{person}这事儿，这一幕有点真实",
            f"{person}最新动态，换个角度看",
            f"吃瓜明白了，{person}这事儿有点意思",
            f"{person}这波操作，说句实话",
        ])

    # 加上基于调研数据的数字式标题
    if bundle:
        n_facts = len(bundle.get("facts") or [])
        if n_facts >= 3:
            titles.append(f"捋了一遍{person}这事儿，3个关键点")
            titles.append(f"{person}这件事，5个细节道出真相")

    # 保留原热搜作为备选
    titles.append(f"{person}：{hot_title}"[:28])

    return titles


def generate_titles(
    person: str,
    hot_title: str,
    bundle: dict[str, Any] | None = None,
    count: int = 5,
) -> list[str]:
    """生成多个候选标题，返回过滤后的结果.

    Args:
        person: 明星人名
        hot_title: 热搜标题
        bundle: 调研数据（可选，用于生成数字式标题）
        count: 返回数量

    Returns:
        标题列表
    """
    if not person:
        return [hot_title[:28]] if hot_title else []

    topic_type = _detect_topic_type(hot_title)
    titles = _generate_titles_for_type(person, hot_title, topic_type, bundle)

    # 过滤：禁用词、长度、去重
    seen: set[str] = set()
    results: list[str] = []

    for title in titles:
        title = title.strip()
        if not title or title in seen:
            continue
        if any(banned in title for banned in BANNED):
            continue
        if 8 <= len(title) <= 28:
            seen.add(title)
            results.append(title)
        if len(results) >= count:
            break

    # 兜底
    if not results:
        base = f"{person}：{hot_title}"
        results.append(base[:28] if len(base) > 28 else base)

    return results


def best_title(person: str, hot_title: str, bundle: dict[str, Any] | None = None) -> str:
    """返回最佳标题."""
    titles = generate_titles(person, hot_title, bundle, count=1)
    return titles[0] if titles else f"{person}：{hot_title}"


# CLI 测试
if __name__ == "__main__":
    test_cases = [
        {"person": "何猷君", "hot_title": "婚礼誓词没提贫穷二字"},
        {"person": "Angelababy", "hot_title": "与黄晓明疑似复合"},
        {"person": "汪峰", "hot_title": "官宣新恋情"},
        {"person": "那英", "hot_title": "舞台摔倒"},
        {"person": "赵丽颖", "hot_title": "离婚后首现身"},
    ]

    print("=== 标题生成测试 ===\n")
    for case in test_cases:
        titles = generate_titles(case["person"], case["hot_title"], count=5)
        print(f"\n{case['person']} · {case['hot_title']}")
        for i, t in enumerate(titles, 1):
            print(f"  {i}. {t}")
