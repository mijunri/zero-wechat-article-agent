#!/usr/bin/env python3
"""Entry: AttentionVC #1 → Twitter article → 中文成稿 → 发布指挥台."""
from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "pipeline_top_article.py"
    runpy.run_path(str(script), run_name="__main__")
