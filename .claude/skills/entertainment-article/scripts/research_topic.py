#!/usr/bin/env python3
"""
Round 1+2 search per entertainment-article SKILL; save data/searchdata/*.md
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[4]
VOLC_SCRIPT = REPO_ROOT / ".claude" / "skills" / "volc-search" / "scripts"
sys.path.insert(0, str(VOLC_SCRIPT))

from volc_search import format_markdown, web_search  # noqa: E402

BJ = ZoneInfo("Asia/Shanghai")
SEARCH_DIR = REPO_ROOT / "data" / "searchdata"


def _save_md(path: Path, *, query: str, person: str, topic: str, body: str) -> None:
    now = datetime.now(BJ).strftime("%Y-%m-%d %H:%M")
    content = f"""# 搜索数据

- **来源**: Volcano FeedCoop web_search
- **获取时间**: {now}
- **人物**: {person}
- **热点标题**: {topic}
- **查询关键词**: {query}

## 原始结果

{body}

## 核心信息点

（流水线自动摘录，成稿前请 Agent 按 entertainment-article 复核）

"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _bullets_from_md(md: str, limit: int = 8) -> list[str]:
    bullets: list[str] = []
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("**摘要：**"):
            bullets.append(line.replace("**摘要：**", "").strip())
        elif line.startswith("### ") and len(bullets) < limit:
            title = line[4:].split(".", 1)[-1].strip()
            if title:
                bullets.append(title)
    return bullets[:limit]


async def research(person: str, topic_title: str, *, stamp: str) -> dict:
    from extract_person import topic_keywords  # noqa: E402

    kw = topic_keywords(topic_title, person)
    q1 = f"{person} 个人经历 出道 背景"
    q2 = f"{person} {kw} 详细 回应 原话"

    files: list[str] = []
    queries = [("round1-breadth", q1), ("round2-depth", q2)]
    all_bullets: list[str] = []

    for tag, query in queries:
        data = await web_search(query, count=8, time_range="7d")
        md = format_markdown(data)
        fname = f"{stamp}_{person}_{tag}_volc.md"
        fpath = SEARCH_DIR / fname
        _save_md(fpath, query=query, person=person, topic=topic_title, body=md)
        files.append(str(fpath))
        all_bullets.extend(_bullets_from_md(md))

    return {
        "person": person,
        "topic_title": topic_title,
        "queries": [q1, q2],
        "search_files": files,
        "bullets": all_bullets[:12],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--person", required=True)
    p.add_argument("--topic", required=True, help="Hot search title")
    p.add_argument("--stamp", default=datetime.now(BJ).strftime("%Y%m%d"))
    p.add_argument("--json-out", default="")
    args = p.parse_args()

    result = asyncio.run(research(args.person, args.topic, stamp=args.stamp))
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
