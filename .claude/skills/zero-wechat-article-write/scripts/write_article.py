#!/usr/bin/env python3
"""Write WeChat HTML articles and publish to zero-agent-manage deliverables."""
from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
DELIVERABLES_SCRIPT = (
    REPO_ROOT / ".claude" / "skills" / "zero-deliverables" / "scripts" / "deliverables.py"
)


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def build_html(brief: dict[str, Any]) -> str:
    parts: list[str] = ['<section class="wechat-article">']
    lead = (brief.get("lead") or "").strip()
    if lead:
        parts.append(f"<p class=\"lead\"><strong>{_esc(lead)}</strong></p>")

    for sec in brief.get("sections") or []:
        h2 = (sec.get("h2") or "").strip()
        if h2:
            parts.append(f"<h2>{_esc(h2)}</h2>")
        for para in sec.get("paragraphs") or []:
            para = str(para).strip()
            if para:
                parts.append(f"<p>{_esc(para)}</p>")
        img = (sec.get("image") or "").strip()
        if img:
            parts.append(
                f'<figure><img src="{_esc(img)}" alt="" '
                f'style="max-width:100%;border-radius:8px;" /></figure>'
            )

    sources = brief.get("sources") or []
    if sources:
        parts.append("<h2>参考与延伸阅读</h2><ul>")
        for s in sources:
            label = _esc(str(s.get("label") or s.get("url") or ""))
            url = _esc(str(s.get("url") or ""))
            if url:
                parts.append(f'<li><a href="{url}">{label}</a></li>')
        parts.append("</ul>")

    footer = (brief.get("footer") or "").strip()
    if footer:
        parts.append(f"<p class=\"muted\">{_esc(footer)}</p>")

    parts.append("</section>")
    return "\n".join(parts)


def cmd_write(args: argparse.Namespace) -> None:
    brief = json.loads(Path(args.brief_file).read_text(encoding="utf-8"))
    out_html = build_html(brief)
    Path(args.out).write_text(out_html, encoding="utf-8")
    title = brief.get("title") or "(no title)"
    print(json.dumps({"title": title, "out": args.out, "bytes": len(out_html)}, ensure_ascii=False))


def _run_deliverables_create(title: str, cover: str, html_file: str) -> dict:
    if not DELIVERABLES_SCRIPT.is_file():
        print(f"Missing {DELIVERABLES_SCRIPT}", file=sys.stderr)
        sys.exit(1)
    cmd = [
        sys.executable,
        str(DELIVERABLES_SCRIPT),
        "create",
        "--platform",
        "wechat",
        "--title",
        title,
        "--cover",
        cover,
        "--html-file",
        html_file,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)
    return json.loads(proc.stdout)


def cmd_publish(args: argparse.Namespace) -> None:
    result = _run_deliverables_create(args.title, args.cover or "", args.html_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    did = result.get("id")
    if did:
        print(
            f"\nView: http://manage.foxrouter.com/app/deliverables?platform=wechat (id={did})",
            file=sys.stderr,
        )


def cmd_pipeline(args: argparse.Namespace) -> None:
    brief_path = Path(args.brief_file)
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    title = brief.get("title") or "Untitled"
    cover = brief.get("cover_url") or args.cover or ""
    out = args.out or str(brief_path.with_suffix(".html"))
    Path(out).write_text(build_html(brief), encoding="utf-8")
    result = _run_deliverables_create(title, cover, out)
    print(json.dumps({"brief": str(brief_path), "html": out, "deliverable": result}, ensure_ascii=False, indent=2))
    did = result.get("id")
    if did:
        print(
            f"\nOK — http://manage.foxrouter.com/app/deliverables?platform=wechat (id={did})",
            file=sys.stderr,
        )


def main() -> None:
    p = argparse.ArgumentParser(description="WeChat article write & publish")
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("write", help="brief.json → HTML file")
    w.add_argument("--brief-file", required=True)
    w.add_argument("--out", default="article.html")
    w.set_defaults(func=cmd_write)

    pub = sub.add_parser("publish", help="Upload HTML to manage deliverables")
    pub.add_argument("--title", required=True)
    pub.add_argument("--html-file", required=True)
    pub.add_argument("--cover", default="")
    pub.set_defaults(func=cmd_publish)

    pl = sub.add_parser("pipeline", help="brief → HTML → upload")
    pl.add_argument("--brief-file", required=True)
    pl.add_argument("--out", default="")
    pl.add_argument("--cover", default="")
    pl.set_defaults(func=cmd_pipeline)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
