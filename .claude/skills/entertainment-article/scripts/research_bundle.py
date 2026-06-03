"""Build consolidated research bundle from multi-round volc search."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_VOLC = Path(__file__).resolve().parents[2] / "volc-search" / "scripts"
sys.path.insert(0, str(_VOLC))
from parse_results import extract_numbers, extract_quotes, merge_items  # noqa: E402


def _pick_followup_keywords(person: str, topic: str, items: list[dict[str, Any]]) -> str:
    """Choose round-3 focus from prior snippets (simple keyword harvest)."""
    blob = " ".join((i.get("text") or "") + " " + (i.get("title") or "") for i in items[:6])
    stop = {
        person,
        "的",
        "了",
        "在",
        "是",
        "与",
        "和",
        "被",
        "将",
        "已",
        "对",
        "为",
        "上",
        "下",
        "一个",
        "可以",
        "没有",
        "不是",
        "如何",
        "什么",
        "为什么",
        "怎么",
        "网友",
        "媒体",
        "报道",
        "消息",
        "官方",
        "今日",
        "近日",
        "曝光",
        "回应",
    }
    words: list[str] = []
    for w in re.findall(r"[\u4e00-\u9fff]{2,6}", blob + " " + topic):
        if w in stop or len(w) < 2:
            continue
        if w not in words:
            words.append(w)
        if len(words) >= 4:
            break
    return " ".join(words[:4]) if words else topic[:12]


def build_bundle(
    *,
    person: str,
    topic_title: str,
    rounds: list[dict[str, Any]],
) -> dict[str, Any]:
    all_items: list[dict[str, Any]] = []
    for r in rounds:
        all_items.extend(r.get("items") or [])

    merged = merge_items(all_items)
    blob = "\n".join((i.get("text") or "") for i in merged)

    numbers = extract_numbers(blob)
    quotes = extract_quotes(blob, person)
    facts = [i.get("text") for i in merged if len(i.get("text") or "") > 20][:30]
    sources = [
        {"title": i.get("title"), "site": i.get("site"), "url": i.get("url")}
        for i in merged[:8]
        if i.get("url")
    ]

    angle = ""
    if facts:
        angle = facts[0][:200]

    title_candidates: list[str] = []
    if numbers and person:
        title_candidates.append(f"{person}{numbers[0]}{topic_title[:8]}")
    title_candidates.append(topic_title)
    if person and person not in topic_title:
        title_candidates.insert(0, f"{person}{topic_title}")

    return {
        "person": person,
        "topic_title": topic_title,
        "round_count": len(rounds),
        "queries": [r.get("query") for r in rounds],
        "facts": facts,
        "numbers": numbers,
        "quotes": quotes,
        "sources": sources,
        "items": merged,
        "angle": angle,
        "title_candidates": title_candidates[:5],
    }


def save_bundle_md(path: Path, bundle: dict[str, Any]) -> None:
    lines = [
        f"# 调研汇总：{bundle.get('person')} · {bundle.get('topic_title')}",
        "",
        "## 搜索轮次",
    ]
    for i, q in enumerate(bundle.get("queries") or [], 1):
        lines.append(f"{i}. `{q}`")
    lines.extend(["", "## 核心信息点"])
    for i, f in enumerate(bundle.get("facts") or [], 1):
        lines.append(f"{i}. {f}")
    if bundle.get("numbers"):
        lines.append("\n## 数字\n" + "、".join(bundle["numbers"][:8]))
    if bundle.get("quotes"):
        lines.append("\n## 原话/回应")
        for q in bundle["quotes"]:
            lines.append(f"- {q}")
    lines.append("\n## 标题备选")
    for t in bundle.get("title_candidates") or []:
        lines.append(f"- {t}")
    lines.append("\n## 角度\n" + (bundle.get("angle") or ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_bundle_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
