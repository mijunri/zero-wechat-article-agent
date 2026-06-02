"""CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import sys

from zero_wechat_article.client import WeChatMPClient


def cmd_token(_: argparse.Namespace) -> int:
    client = WeChatMPClient()
    token = client.get_access_token(force=True)
    print(json.dumps({"ok": True, "token_prefix": token[:8] + "..."}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="zero-wechat-article")
    sub = parser.add_subparsers(dest="command", required=True)

    p_token = sub.add_parser("token", help="Fetch and validate access_token")
    p_token.set_defaults(func=cmd_token)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
