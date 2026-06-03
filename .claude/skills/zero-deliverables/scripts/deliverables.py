#!/usr/bin/env python3
"""CLI for zero-agent-manage deliverables API."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def api_base() -> str:
    return os.environ.get("ZAM_API_BASE", "http://api-manage.foxrouter.com").rstrip("/")


def api_key() -> str:
    key = os.environ.get("ZAM_API_KEY", "")
    if not key:
        print("Set ZAM_API_KEY in scripts/agent.env", file=sys.stderr)
        sys.exit(1)
    return key


def request(method: str, path: str, body: dict | None = None) -> dict | list | None:
    url = f"{api_base()}{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {api_key()}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    path = "/api/deliverables/grouped"
    if args.platform:
        path += f"?platform={args.platform}"
    print(json.dumps(request("GET", path), ensure_ascii=False, indent=2))


def cmd_get(args: argparse.Namespace) -> None:
    print(json.dumps(request("GET", f"/api/deliverables/{args.id}"), ensure_ascii=False, indent=2))


def _parse_image_urls(raw: str | None) -> list[str]:
    if not raw:
        return []
    raw = raw.strip()
    if raw.startswith("["):
        return [u for u in json.loads(raw) if u]
    return [u.strip() for u in raw.split(",") if u.strip()]


def cmd_create(args: argparse.Namespace) -> None:
    html = args.html
    if args.html_file:
        html = Path(args.html_file).read_text(encoding="utf-8")
    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    image_urls = _parse_image_urls(args.image_urls)
    if args.platform in ("xiaohongshu", "twitter"):
        if args.platform == "xiaohongshu" and not image_urls:
            print("xiaohongshu requires --image-urls (comma-separated or JSON array)", file=sys.stderr)
            sys.exit(1)
        copy = (text or html or "").strip()
        if not copy:
            print(f"{args.platform} requires --text or --text-file (plain copy, not HTML)", file=sys.stderr)
            sys.exit(1)
        html = copy
    elif not html:
        print("Provide --html or --html-file", file=sys.stderr)
        sys.exit(1)
    body: dict = {
        "platform": args.platform,
        "title": args.title,
        "cover_url": args.cover or "",
        "content_html": html or "",
        "image_urls": image_urls,
    }
    if args.published_at:
        body["published_at"] = args.published_at
    print(json.dumps(request("POST", "/api/deliverables", body), ensure_ascii=False, indent=2))


def cmd_update(args: argparse.Namespace) -> None:
    body: dict = {}
    if args.platform:
        body["platform"] = args.platform
    if args.title:
        body["title"] = args.title
    if args.cover is not None:
        body["cover_url"] = args.cover
    if args.html_file:
        body["content_html"] = Path(args.html_file).read_text(encoding="utf-8")
    elif args.html:
        body["content_html"] = args.html
    if args.text_file:
        body["content_html"] = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text:
        body["content_html"] = args.text
    if args.published_at:
        body["published_at"] = args.published_at
    if args.image_urls is not None:
        body["image_urls"] = _parse_image_urls(args.image_urls)
    if not body:
        print("No fields to update", file=sys.stderr)
        sys.exit(1)
    print(
        json.dumps(request("PUT", f"/api/deliverables/{args.id}", body), ensure_ascii=False, indent=2)
    )


def cmd_delete(args: argparse.Namespace) -> None:
    request("DELETE", f"/api/deliverables/{args.id}")
    print(f"Deleted deliverable {args.id}")


def main() -> None:
    p = argparse.ArgumentParser(description="zero-agent-manage deliverables")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="Grouped list by Beijing date")
    ls.add_argument("--platform", choices=["wechat", "toutiao", "baijiahao", "xiaohongshu", "twitter"])
    ls.set_defaults(func=cmd_list)

    gt = sub.add_parser("get")
    gt.add_argument("--id", type=int, required=True)
    gt.set_defaults(func=cmd_get)

    cr = sub.add_parser("create")
    cr.add_argument("--platform", required=True, choices=["wechat", "toutiao", "baijiahao", "xiaohongshu", "twitter"])
    cr.add_argument("--title", required=True)
    cr.add_argument("--cover", default="")
    cr.add_argument("--html", default="", help="HTML body (article platforms)")
    cr.add_argument("--html-file")
    cr.add_argument("--text", default="", help="Plain copy (xiaohongshu / twitter)")
    cr.add_argument("--text-file", dest="text_file")
    cr.add_argument(
        "--image-urls",
        dest="image_urls",
        help="Comma-separated or JSON array; required for xiaohongshu; optional for twitter",
    )
    cr.add_argument("--published-at", dest="published_at")
    cr.set_defaults(func=cmd_create)

    up = sub.add_parser("update")
    up.add_argument("--id", type=int, required=True)
    up.add_argument("--platform", choices=["wechat", "toutiao", "baijiahao", "xiaohongshu", "twitter"])
    up.add_argument("--text", default="")
    up.add_argument("--text-file", dest="text_file")
    up.add_argument("--image-urls", dest="image_urls")
    up.add_argument("--title")
    up.add_argument("--cover", default=None)
    up.add_argument("--html", default="")
    up.add_argument("--html-file")
    up.add_argument("--published-at", dest="published_at")
    up.set_defaults(func=cmd_update)

    dl = sub.add_parser("delete")
    dl.add_argument("--id", type=int, required=True)
    dl.set_defaults(func=cmd_delete)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
