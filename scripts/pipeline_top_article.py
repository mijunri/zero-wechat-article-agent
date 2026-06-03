#!/usr/bin/env python3
"""
Pipeline (quality):
  1. AttentionVC AI hot #1
  2. TwitterAPI full article by tweet_id
  3. Translate + compose Chinese WeChat article
  4. Publish to manage.foxrouter.com (wechat)
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
CACHE = ROOT / ".cache" / "top-article"
SKILLS = ROOT / ".claude" / "skills"
DELIVERABLES_ENV = SKILLS / "zero-deliverables" / "scripts" / "agent.env"


def _load_env() -> None:
    for env_file in (
        SKILLS / "zero-twitter-collect" / "scripts" / "agent.env",
        DELIVERABLES_ENV,
    ):
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip()
            # agent.env wins over stale cloud env (publish as mongo)
            if v:
                os.environ[k] = v
    os.environ.setdefault(
        "ZAM_API_BASE", "http://api-manage.foxrouter.com"
    )


def _die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    if p.returncode != 0:
        _die(p.stderr or p.stdout or "command failed")
    return p.stdout


def _zam_me() -> dict:
    base = os.environ["ZAM_API_BASE"].rstrip("/")
    req = urllib.request.Request(
        f"{base}/api/auth/me",
        headers={"Authorization": f"Bearer {os.environ['ZAM_API_KEY']}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        _die(f"ZAM_API_KEY invalid: {e.read().decode()}")


def _tweet_id_from_item(item: dict) -> str:
    url = item.get("tweet_url") or ""
    if "/status/" in url:
        return url.rstrip("/").split("/status/")[-1].split("?")[0]
    raise ValueError(f"No tweet id in item: {item}")


def main() -> None:
    _load_env()
    if not os.environ.get("twitter_api_key"):
        _die("Missing twitter_api_key")
    if not os.environ.get("ZAM_API_KEY"):
        _die("Missing ZAM_API_KEY")

    me = _zam_me()
    print(f"发布账号: {me.get('display_name')} <{me.get('email')}>\n")

    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d-%H%M")
    av_path = CACHE / f"attentionvc-top1-{stamp}.json"
    tw_path = CACHE / f"tweet-article-{stamp}.json"
    brief_path = CACHE / f"brief-{stamp}.json"
    html_path = CACHE / f"article-{stamp}.html"

    py = sys.executable

    _run(
        [
            py,
            str(SKILLS / "zero-attentionvc-scrape/scripts/fetch_ai_hot.py"),
            "fetch",
            "--period",
            "24h",
            "--lang",
            "en,zh",
            "--limit",
            "1",
            "--json-out",
            str(av_path),
        ]
    )
    av = json.loads(av_path.read_text(encoding="utf-8"))
    top = (av.get("articles") or [])[0]
    print(f"[1/4] AttentionVC #1: {top.get('title')}")

    tweet_id = _tweet_id_from_item(top)
    _run(
        [
            py,
            str(SKILLS / "zero-twitter-collect/scripts/get_tweet_article.py"),
            "--tweet-id",
            tweet_id,
            "--json-out",
            str(tw_path),
        ]
    )
    tw = json.loads(tw_path.read_text(encoding="utf-8"))
    print(f"[2/4] Twitter 长文: {len(tw.get('full_text',''))} 字英文, {len(tw.get('image_urls',[]))} 图")

    _run(
        [
            py,
            str(ROOT / "scripts/compose_chinese_article.py"),
            "--attentionvc-json",
            str(av_path),
            "--tweet-json",
            str(tw_path),
            "--out",
            str(brief_path),
        ]
    )
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    print(f"[3/4] 中文成稿: {brief.get('title')}")

    out = _run(
        [
            py,
            str(SKILLS / "zero-wechat-article-write/scripts/write_article.py"),
            "pipeline",
            "--brief-file",
            str(brief_path),
            "--out",
            str(html_path),
        ]
    )
    result = json.loads(out)
    did = (result.get("deliverable") or {}).get("id")
    print(f"[4/4] 已发布产物 id={did}")
    print(
        f"\n打开: http://manage.foxrouter.com/app/deliverables?platform=wechat\n"
        f"（请用 {me.get('email')} 登录）"
    )


if __name__ == "__main__":
    main()
