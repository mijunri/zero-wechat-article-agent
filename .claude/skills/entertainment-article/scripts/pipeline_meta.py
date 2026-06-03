#!/usr/bin/env python3
"""Embed pipeline + SEO metadata in HTML for manage.foxrouter.com review."""
from __future__ import annotations

import json
import re
from typing import Any


def inject_meta(html: str, meta: dict[str, Any]) -> str:
    payload = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    comment = f"<!-- pipeline-meta:{payload} -->"
    if "</body>" in html:
        return html.replace("</body>", f"{comment}\n</body>", 1)
    return html + "\n" + comment


def extract_h2_plain(html: str) -> list[str]:
    return re.findall(r"<h2[^>]*>([^<]+)</h2>", html)
