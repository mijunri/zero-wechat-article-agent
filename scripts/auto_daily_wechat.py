#!/usr/bin/env python3
"""
Full automation: collect signals → brief → HTML → upload to manage.foxrouter.com (wechat).

Requires:
  twitter_api_key  — TwitterAPI.io
  ZAM_API_KEY      — from manage.foxrouter.com → API Key (same login as browser!)
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
CACHE = ROOT / ".cache" / "auto-daily"
SKILLS = ROOT / ".claude" / "skills"


def _die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def _run(cmd: list[str], env: dict | None = None) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env or os.environ)
    if proc.returncode != 0:
        _die(proc.stderr or proc.stdout or f"failed: {' '.join(cmd)}")
    return proc.stdout


def _zam_me() -> dict:
    base = os.environ.get("ZAM_API_BASE", "http://api-manage.foxrouter.com").rstrip("/")
    key = os.environ.get("ZAM_API_KEY", "").strip()
    req = urllib.request.Request(
        f"{base}/api/auth/me",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        _die(f"ZAM_API_KEY invalid: HTTP {e.code} {e.read().decode()}")


def main() -> None:
    if not os.environ.get("twitter_api_key", "").strip():
        _die("Missing env twitter_api_key")
    if not os.environ.get("ZAM_API_KEY", "").strip():
        _die("Missing env ZAM_API_KEY — create at http://manage.foxrouter.com/app/api-keys while logged in")

    me = _zam_me()
    print(f"Upload target account: {me.get('email')} (id={me.get('id')})")
    print(">>> 请用同一账号登录浏览器查看产物，否则看不到新文章 <<<\n")

    CACHE.mkdir(parents=True, exist_ok=True)
    today = datetime.now(BJ).strftime("%Y-%m-%d")
    tw_path = CACHE / f"twitter-{today}.json"
    av_path = CACHE / f"attentionvc-{today}.json"
    brief_path = CACHE / f"brief-{today}.json"
    html_path = CACHE / f"article-{today}.html"

    py = sys.executable
    _run(
        [
            py,
            str(SKILLS / "zero-twitter-collect" / "scripts" / "search_tweets.py"),
            "search",
            "--query",
            f"(AI OR LLM OR Claude OR GPT OR 人工智能 OR 大模型) since:{today} -is:retweet",
            "--query-type",
            "Top",
            "--limit",
            "15",
            "--json-out",
            str(tw_path),
        ]
    )
    print(f"Twitter: {tw_path}")

    _run(
        [
            py,
            str(SKILLS / "zero-attentionvc-scrape" / "scripts" / "fetch_ai_hot.py"),
            "fetch",
            "--period",
            "24h",
            "--lang",
            "en,zh",
            "--limit",
            "10",
            "--json-out",
            str(av_path),
        ]
    )
    print(f"AttentionVC: {av_path}")

    _run(
        [
            py,
            str(ROOT / "scripts" / "brief_from_signals.py"),
            "--twitter-json",
            str(tw_path),
            "--attentionvc-json",
            str(av_path),
            "--out",
            str(brief_path),
        ]
    )
    brief_meta = json.loads(brief_path.read_text(encoding="utf-8"))
    print(f"Brief: {brief_path} — {brief_meta.get('title', '')}")

    out = _run(
        [
            py,
            str(SKILLS / "zero-wechat-article-write" / "scripts" / "write_article.py"),
            "pipeline",
            "--brief-file",
            str(brief_path),
            "--out",
            str(html_path),
        ]
    )
    result = json.loads(out)
    did = (result.get("deliverable") or {}).get("id")
    email = me.get("email", "")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"\n✅ 完成 — 请用 {email} 登录后打开：\n"
        f"   http://manage.foxrouter.com/app/deliverables?platform=wechat\n"
        f"   产物 id={did}，日期应为今天（北京时间）"
    )


if __name__ == "__main__":
    main()
