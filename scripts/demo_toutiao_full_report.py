#!/usr/bin/env python3
"""
Demo: one Toutiao entertainment article — hot → volc 广10+深10 → compose+SEO → manage.

Default uploads to manage.foxrouter.com (platform=toutiao) for review.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BJ = ZoneInfo("Asia/Shanghai")
CACHE = ROOT / ".cache" / "demo-toutiao"
SKILLS = ROOT / ".claude" / "skills"
ENT = SKILLS / "entertainment-article" / "scripts"
TT = SKILLS / "zero-toutiao-entertainment" / "scripts"
DELIVERABLES_ENV = SKILLS / "zero-deliverables" / "scripts" / "agent.env"
VOLC_ENV = SKILLS / "volc-search" / "scripts" / "agent.env"


def _load_env() -> None:
    for env_file in (DELIVERABLES_ENV, VOLC_ENV, ROOT / "data" / "auth" / "volc_search.json"):
        if env_file.suffix == ".json" and env_file.is_file():
            cfg = json.loads(env_file.read_text(encoding="utf-8"))
            if cfg.get("api_key"):
                os.environ["VOLC_SEARCH_API_KEY"] = cfg["api_key"]
            continue
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip()
            if v:
                os.environ[k] = v
    os.environ.setdefault("ZAM_API_BASE", "http://api-manage.foxrouter.com")


def _run(cmd: list[str]) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ENT), str(TT), str(SKILLS / "hot-topics" / "scripts"), env.get("PYTHONPATH", "")]
    )
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        print(p.stderr or p.stdout, file=sys.stderr)
        sys.exit(p.returncode)
    return p.stdout


def main() -> None:
    _load_env()
    ap = argparse.ArgumentParser(description="Toutiao entertainment demo with SEO + manage publish")
    ap.add_argument("--no-publish", action="store_true", help="Skip upload to manage")
    ap.add_argument("--topic-index", type=int, default=0, help="Pick hot list item index")
    args = ap.parse_args()

    if not os.environ.get("VOLC_SEARCH_API_KEY"):
        print("Missing VOLC_SEARCH_API_KEY", file=sys.stderr)
        sys.exit(1)
    if not args.no_publish and not os.environ.get("ZAM_API_KEY"):
        print("Missing ZAM_API_KEY for publish", file=sys.stderr)
        sys.exit(1)

    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d-%H%M")
    py = sys.executable

    hot_path = CACHE / f"hot-{stamp}.json"
    _run([py, str(TT / "fetch_entertainment_hot.py"), "--limit", "15", "--json-out", str(hot_path)])
    hot = json.loads(hot_path.read_text(encoding="utf-8"))
    items = hot.get("items") or []
    if not items:
        print("No hot topics", file=sys.stderr)
        sys.exit(1)

    idx = min(args.topic_index, len(items) - 1)
    item = items[idx]
    title = item.get("title") or ""

    sys.path.insert(0, str(ENT))
    from extract_person import extract_person  # noqa: E402

    person = extract_person(title)
    item["person"] = person

    topic_path = CACHE / f"topic-{stamp}.json"
    research_path = CACHE / f"research-{stamp}.json"
    article_path = CACHE / f"article-{stamp}.json"
    html_path = CACHE / f"article-{stamp}.html"
    topic_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"选题: {title}")
    print(f"人名: {person}")
    print("搜索: R1 广度×10 + R2 深度×10 + R3/R4 聚焦与原话\n")

    _run(
        [
            py,
            str(ENT / "research_topic.py"),
            "--person",
            person,
            "--topic",
            title,
            "--stamp",
            stamp.replace("-", "")[:8],
            "--rounds",
            "4",
            "--broad-count",
            "10",
            "--deep-count",
            "10",
            "--json-out",
            str(research_path),
        ]
    )

    research = json.loads(research_path.read_text(encoding="utf-8"))
    n_facts = len((research.get("bundle") or {}).get("facts") or [])
    print(f"调研: {n_facts} 条 facts · bundle={research.get('bundle_file', '')}\n")

    out = _run(
        [
            py,
            str(ENT / "compose_from_research.py"),
            "--hot-json",
            str(topic_path),
            "--research-json",
            str(research_path),
            "--article-type",
            "short",
            "--out",
            str(article_path),
            "--html-out",
            str(html_path),
        ]
    )
    summary = json.loads(out)
    art = json.loads(article_path.read_text(encoding="utf-8"))

    print(
        json.dumps(
            {
                "compose": summary,
                "logic_doc": "docs/PIPELINE-LOGIC.md",
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if args.no_publish:
        print("\n[--no-publish] 未上传 manage。预览 HTML:", html_path)
        return

    pub = _run([py, str(TT / "publish_toutiao.py"), "--article-json", str(article_path)])
    result = json.loads(pub)
    did = (result.get("deliverable") or {}).get("id")
    print(
        f"\n已上传 manage · id={did}\n"
        f"预览: http://manage.foxrouter.com/app/deliverables?platform=toutiao\n"
        f"评估: 打开详情 → 查看标题/正文；源码末尾 pipeline-meta 含 seo_check 与 facts_used"
    )


if __name__ == "__main__":
    main()
