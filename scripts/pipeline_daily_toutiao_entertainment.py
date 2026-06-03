#!/usr/bin/env python3
"""
Daily Toutiao entertainment pipeline (3 articles):
  hot-topics (weibo/douyin/toutiao) → filter 娱乐 → compose → quality → publish
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
TT_SKILL = SKILLS / "zero-toutiao-entertainment" / "scripts"
DELIVERABLES_ENV = SKILLS / "zero-deliverables" / "scripts" / "agent.env"
DAILY_COUNT = 3


def _load_env() -> None:
    if DELIVERABLES_ENV.is_file():
        for line in DELIVERABLES_ENV.read_text(encoding="utf-8").splitlines():
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
    p = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
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
        _die("Missing ZAM_API_KEY in zero-deliverables/scripts/agent.env")

    me = _zam_me()
    print(f"发布账号: {me.get('display_name')} <{me.get('email')}>\n")

    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d-%H%M")
    hot_path = CACHE / f"hot-{stamp}.json"
    py = sys.executable

    _run([py, str(TT_SKILL / "fetch_entertainment_hot.py"), "--limit", "20", "--json-out", str(hot_path)])
    hot = json.loads(hot_path.read_text(encoding="utf-8"))
    items = hot.get("items") or []
    if len(items) < DAILY_COUNT:
        _die(f"Not enough entertainment topics: {len(items)} < {DAILY_COUNT}")

    # Import classify for diverse picks (wedding / variety / drama / gossip)
    sys.path.insert(0, str(TT_SKILL))
    from compose_toutiao_article import _classify  # noqa: E402

    published: list[dict] = []
    used_topics: set[str] = set()
    used_kinds: set[str] = set()

    def _pick_item() -> dict | None:
        for candidate in items:
            key = (candidate.get("title") or "")[:50]
            if key in used_topics:
                continue
            kind = _classify(candidate.get("title") or "")
            if kind in used_kinds:
                continue
            return candidate
        for candidate in items:
            key = (candidate.get("title") or "")[:50]
            if key not in used_topics:
                return candidate
        return None

    for idx in range(DAILY_COUNT):
        item = _pick_item()
        if not item:
            _die("Ran out of unique entertainment topics")
        used_topics.add((item.get("title") or "")[:50])
        used_kinds.add(_classify(item.get("title") or ""))

        topic_path = CACHE / f"topic-{stamp}-{idx+1}.json"
        article_path = CACHE / f"article-{stamp}-{idx+1}.json"
        html_path = CACHE / f"article-{stamp}-{idx+1}.html"
        topic_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")

        _run(
            [
                py,
                str(TT_SKILL / "compose_toutiao_article.py"),
                "--topic-json",
                str(topic_path),
                "--out",
                str(article_path),
                "--html-out",
                str(html_path),
            ]
        )
        qc = subprocess.run(
            [py, str(TT_SKILL / "quality_check.py"), "--article-json", str(article_path)],
            capture_output=True,
            text=True,
        )
        if qc.returncode != 0:
            _die(f"Quality check failed for article {idx+1}: {qc.stdout or qc.stderr}")

        out = _run([py, str(TT_SKILL / "publish_toutiao.py"), "--article-json", str(article_path)])
        result = json.loads(out)
        did = (result.get("deliverable") or {}).get("id")
        title = json.loads(article_path.read_text(encoding="utf-8")).get("title")
        published.append({"id": did, "title": title})
        print(f"[{idx+1}/{DAILY_COUNT}] 已发布 id={did} · {title}")

    print(
        f"\n完成 {len(published)} 篇头条号娱乐稿。\n"
        f"预览: http://manage.foxrouter.com/app/deliverables?platform=toutiao\n"
        f"登录: {me.get('email')}"
    )


if __name__ == "__main__":
    main()
