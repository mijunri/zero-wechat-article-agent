#!/usr/bin/env python3
"""Lint composed HTML/plain for banned contrast patterns."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from prose_guard import find_contrast_violations

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--text", default="")
    p.add_argument("--html-file", default="")
    args = p.parse_args()
    text = args.text
    if args.html_file:
        text = re.sub(r"<[^>]+>", "", Path(args.html_file).read_text(encoding="utf-8"))
    hits = find_contrast_violations(text)
    if hits:
        for h in hits:
            print(h, file=sys.stderr)
        sys.exit(1)
    print("ok")
