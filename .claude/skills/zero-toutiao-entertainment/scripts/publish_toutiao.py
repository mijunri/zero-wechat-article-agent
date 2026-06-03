#!/usr/bin/env python3
"""Publish Toutiao deliverable to zero-agent-manage."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DELIVERABLES = REPO_ROOT / ".claude" / "skills" / "zero-deliverables" / "scripts" / "deliverables.py"


def _load_env() -> None:
    env_file = REPO_ROOT / ".claude" / "skills" / "zero-deliverables" / "scripts" / "agent.env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip()
        if v:
            os.environ[k] = v


def main() -> None:
    _load_env()
    p = argparse.ArgumentParser()
    p.add_argument("--article-json", required=True)
    p.add_argument("--html-file", default="")
    args = p.parse_args()

    article = json.loads(Path(args.article_json).read_text(encoding="utf-8"))
    html_file = args.html_file
    if not html_file:
        html_file = str(Path(args.article_json).with_suffix(".html"))
        Path(html_file).write_text(article.get("content_html") or "", encoding="utf-8")

    cmd = [
        sys.executable,
        str(DELIVERABLES),
        "create",
        "--platform",
        "toutiao",
        "--title",
        article.get("title") or "娱乐热点",
        "--cover",
        article.get("cover_url") or "",
        "--html-file",
        html_file,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)
    result = json.loads(proc.stdout)
    print(json.dumps({"deliverable": result, "html": html_file}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
