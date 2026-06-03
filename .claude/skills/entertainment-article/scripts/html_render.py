#!/usr/bin/env python3
"""WeChat/Toutiao HTML renderer (from ai-article gen_articles.py, template only)."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - {person}</title>
</head>
<body style="margin:0;padding:0;background:#fff;">
<div id="article-content" style="max-width:677px;margin:0 auto;padding:20px 16px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#333;line-height:1.8;font-size:16px;">
<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;line-height:1.4;text-align:center;margin:0 0 8px;">{title}</h1>
<p style="text-align:center;color:#999;font-size:13px;margin:0 0 28px;">异次元探险家 · {date}</p>
{body}
<div style="text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid #eee;">
  <p style="font-size:15px;color:#666;font-weight:500;margin:0 0 4px;">异次元探险家 · 深度研究</p>
  <p style="font-size:12px;color:#999;margin:0;">数据来源：公开信息整理，仅供参考</p>
</div>
</div>
</body>
</html>"""


def p(text: str) -> str:
    return (
        f'<p style="font-size:16px;color:#333;margin:0 0 16px;text-align:justify;">{text}</p>'
    )


def h2(text: str, color: str = "#1890ff", bg: str | None = None) -> str:
    if bg:
        return (
            f'<h2 style="font-size:18px;font-weight:bold;color:#fff;background-color:{bg};'
            f'margin:28px 0 12px;padding:8px 14px;border-radius:4px;">{text}</h2>'
        )
    return (
        f'<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;margin:28px 0 12px;'
        f'padding-bottom:8px;border-bottom:2px solid {color};">{text}</h2>'
    )


def box(text: str, color: str = "#d4636a") -> str:
    bg_map = {
        "#1890ff": "#f0f7ff",
        "#d4636a": "#fdf2f2",
        "#e67e22": "#fff8f0",
        "#9b59b6": "#f8f0ff",
    }
    bg = bg_map.get(color, "#f8f8f8")
    return (
        f'<p style="background-color:{bg};border-left:4px solid {color};border-radius:0 8px 8px 0;'
        f'padding:12px 16px;margin:0 0 20px;font-size:15px;color:#333;'
        f"font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB',"
        f"'Microsoft YaHei',sans-serif;\">{text}</p>"
    )


def render(
    person: str,
    title: str,
  color: str,
    sections: list[tuple],
) -> str:
    body_parts: list[str] = []
    for sec in sections:
        if sec[0] == "p":
            body_parts.append(p(sec[1]))
        elif sec[0] == "h2":
            if len(sec) > 2 and str(sec[2]).startswith("bg:"):
                body_parts.append(h2(sec[1], bg=str(sec[2])[3:]))
            else:
                body_parts.append(h2(sec[1], color=color))
        elif sec[0] == "box":
            body_parts.append(box(sec[1], color=color))
    body = "\n".join(body_parts)
    return TEMPLATE.format(
        title=title,
        person=person,
        date=datetime.now(BJ).strftime("%Y-%m-%d"),
        body=body,
    )
