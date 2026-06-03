#!/usr/bin/env python3
"""
Daily Toutiao ×3 — entertainment-article + volc 多轮搜索 → 成稿 → publish
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BJ = ZoneInfo("Asia/Shanghai")
CACHE = ROOT / ".cache" / "toutiao-entertainment"
SKILLS = ROOT / ".claude" / "skills"
ENT = SKILLS / "entertainment-article" / "scripts"
TT = SKILLS / "zero-toutiao-entertainment" / "scripts"
DELIVERABLES_ENV = SKILLS / "zero-deliverables" / "scripts" / "agent.env"
VOLC_ENV = SKILLS / "volc-search" / "scripts" / "agent.env"
DAILY_COUNT = 5
VOLC_ROUNDS = 4
ARTICLE_TYPE = "short"  # toutiao 短篇快讯；公众号可用 long


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


def _die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def _run(cmd: list[str]) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ENT), str(TT), str(SKILLS / "hot-topics" / "scripts"), env.get("PYTHONPATH", "")]
    )
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        _die(p.stderr or p.stdout or "command failed")
    return p.stdout


def _zam_me() -> dict:
    req = urllib.request.Request(
        f"{os.environ['ZAM_API_BASE'].rstrip('/')}/api/auth/me",
        headers={"Authorization": f"Bearer {os.environ['ZAM_API_KEY']}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        _die(f"ZAM_API_KEY invalid: {e.read().decode()}")


def main() -> None:
    _load_env()
    if not os.environ.get("ZAM_API_KEY"):
        _die("Missing ZAM_API_KEY")
    if not os.environ.get("VOLC_SEARCH_API_KEY"):
        _die(
            "Missing VOLC_SEARCH_API_KEY — copy from ai-article to "
            "data/auth/volc_search.json or .claude/skills/volc-search/scripts/agent.env"
        )

    me = _zam_me()
    print(f"发布账号: {me.get('display_name')} <{me.get('email')}>")
    print(f"写作: entertainment-article · 火山搜索 {VOLC_ROUNDS} 轮 · 体裁 {ARTICLE_TYPE}\n")

    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d-%H%M")
    py = sys.executable

    hot_path = CACHE / f"hot-{stamp}.json"
    _run([py, str(TT / "fetch_entertainment_hot.py"), "--limit", "20", "--json-out", str(hot_path)])
    hot = json.loads(hot_path.read_text(encoding="utf-8"))
    items = hot.get("items") or []
    if len(items) < DAILY_COUNT:
        _die(f"Not enough entertainment topics: {len(items)}")

    sys.path.insert(0, str(ENT))
    from compose_from_research import _classify  # noqa: E402
    from extract_person import extract_person  # noqa: E402

    used: set[str] = set()
    used_kinds: set[str] = set()
    published: list[dict] = []

    for idx in range(DAILY_COUNT):
        item = None
        for c in items:
            key = (c.get("title") or "")[:50]
            if key in used:
                continue
            kind = _classify(c.get("title") or "")
            if kind in used_kinds:
                continue
            item = c
            break
        if not item:
            for c in items:
                key = (c.get("title") or "")[:50]
                if key not in used:
                    item = c
                    break
        if not item:
            _die("No unique topics left")

        title = item.get("title") or ""
        used.add(title[:50])
        used_kinds.add(_classify(title))
        person = extract_person(title)
        item["person"] = person

        topic_path = CACHE / f"topic-{stamp}-{idx+1}.json"
        research_path = CACHE / f"research-{stamp}-{idx+1}.json"
        article_path = CACHE / f"article-{stamp}-{idx+1}.json"
        html_path = CACHE / f"article-{stamp}-{idx+1}.html"
        topic_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"[{idx+1}/{DAILY_COUNT}] 火山搜索×{VOLC_ROUNDS} → 成稿 · {person} · {title[:20]}…")
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
                str(VOLC_ROUNDS),
                "--json-out",
                str(research_path),
            ]
        )

        research = json.loads(research_path.read_text(encoding="utf-8"))
        n_facts = len((research.get("bundle") or {}).get("facts") or [])
        print(f"    调研完成: {n_facts} 条信息点 · bundle={research.get('bundle_file', '')}")

        _run(
            [
                py,
                str(ENT / "compose_from_research.py"),
                "--hot-json",
                str(topic_path),
                "--research-json",
                str(research_path),
                "--article-type",
                ARTICLE_TYPE,
                "--out",
                str(article_path),
                "--html-out",
                str(html_path),
            ]
        )

        art = json.loads(article_path.read_text(encoding="utf-8"))
        min_chars = 650 if ARTICLE_TYPE == "short" else 1800
        if art.get("char_count", 0) < min_chars:
            _die(
                f"Article too short ({art.get('char_count')} < {min_chars}), "
                f"check volc rounds / bundle"
            )

        out = _run([py, str(TT / "publish_toutiao.py"), "--article-json", str(article_path)])
        result = json.loads(out)
        did = (result.get("deliverable") or {}).get("id")
        published.append({"id": did, "title": art.get("title"), "person": person})
        print(f"    → 已发布 id={did} · {art.get('title')}\n")

    print(
        f"完成 {len(published)} 篇（entertainment-article 流程）。\n"
        f"预览: http://manage.foxrouter.com/app/deliverables?platform=toutiao\n"
        f"搜索数据: data/searchdata/\n"
        f"登录: {me.get('email')}"
    )


if __name__ == "__main__":
    main()
