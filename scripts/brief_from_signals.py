#!/usr/bin/env python3
"""Build WeChat article brief.json from Twitter + AttentionVC collection JSON."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")
DEFAULT_COVER = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80"
INLINE_IMG = "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=900&q=80"


def _truncate(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _topic_label_from_tweet(text: str, username: str) -> str:
    t = (text or "").lower()
    u = (username or "").lower()
    if "nvidia" in t or "microsoft" in t or u == "nvidia":
        return "英伟达联手微软推 Windows Agent"
    if u == "sama" or "executive order" in t or " eo " in f" {t} ":
        return "Sam Altman 评美国 AI 行政令"
    if "claude code" in t or "claude" in t:
        return "Claude Code 实操热度"
    return _truncate(text.split("\n")[0], 22)


def _pick_twitter(tw: dict[str, Any], limit: int = 3) -> list[dict]:
    tweets = sorted(tw.get("tweets") or [], key=lambda t: t.get("view_count") or 0, reverse=True)
    out = []
    for t in tweets[:limit]:
        text = (t.get("text") or "").strip()
        if not text:
            continue
        out.append(
            {
                "username": (t.get("author") or {}).get("username") or "?",
                "text": text,
                "url": t.get("url") or "",
                "views": t.get("view_count") or 0,
            }
        )
    return out


def _pick_attentionvc(av: dict[str, Any], limit: int = 2) -> list[dict]:
    articles = av.get("articles") or []
    out = []
    for a in articles[:limit]:
        out.append(
            {
                "title": a.get("title") or "",
                "preview": a.get("preview_text") or "",
                "handle": a.get("author_handle") or "",
                "url": a.get("tweet_url") or "",
                "views": a.get("view_count") or 0,
            }
        )
    return out


def build_brief(tw: dict[str, Any], av: dict[str, Any]) -> dict[str, Any]:
    tweets = _pick_twitter(tw, 3)
    articles = _pick_attentionvc(av, 2)

    topics: list[str] = []
    if tweets:
        topics.append(_topic_label_from_tweet(tweets[0]["text"], tweets[0]["username"]))
    if articles and len(topics) < 2:
        topics.append(_truncate(articles[0]["title"], 22))
    title_core = "、".join(topics[:2]) if topics else "AI 行业动态"
    d = datetime.now(BJ)
    today = f"{d.month}月{d.day}日"
    title = f"今日 AI 速递（{today}）：{title_core}"

    lead_parts = []
    if articles:
        lead_parts.append(f"AttentionVC 24 小时热榜显示，「{articles[0]['title']}」仍占据高关注。")
    if tweets:
        lead_parts.append(f"X 上 @{tweets[0]['username']} 的相关讨论今日浏览量领先。")
    lead = "".join(lead_parts) or "以下为过去 24 小时 AI 领域值得跟进的信号与选题角度（二次整理，非原文搬运）。"

    sections: list[dict[str, Any]] = []

    for i, a in enumerate(articles):
        paras = [
            _truncate(a["preview"], 280) if a["preview"] else f"热榜长文由 @{a['handle']} 发布，适合作为深度选题参考。",
            "公众号写法建议：提炼 3 个读者可带走的观点 + 1 张信息图，避免整段翻译原文。",
        ]
        sec: dict[str, Any] = {
            "h2": f"热榜长文 {'①' if i == 0 else '②'}：{_truncate(a['title'], 40)}",
            "paragraphs": paras,
        }
        if i == 0:
            sec["image"] = INLINE_IMG
        sections.append(sec)

    for i, t in enumerate(tweets):
        summary = _truncate(t["text"].replace("\n", " "), 320)
        sections.append(
            {
                "h2": f"X 热议 {'①' if i == 0 else '②' if i == 1 else '③'}：@{t['username']}",
                "paragraphs": [
                    summary,
                    f"原帖互动：约 {t['views']:,} 次浏览。可延伸为「一句话新闻 + 你的判断」栏目。",
                ],
            }
        )

    sections.append(
        {
            "h2": "今日可执行的选题清单",
            "paragraphs": [
                "1）产业合作稿：把「大厂联手 + 终端 Agent」写成科普向短文。",
                "2）政策解读稿：行政令/监管只用 3 段，面向开发者而非法律从业者。",
                "3）工具教程稿：延续 Claude Code / Copilot 类热度，做 10 分钟实操。",
            ],
        }
    )

    sources = []
    for a in articles:
        if a.get("url"):
            sources.append({"label": f"AttentionVC / @{a['handle']}", "url": a["url"]})
    for t in tweets:
        if t.get("url"):
            sources.append({"label": f"@{t['username']} on X", "url": t["url"]})

    return {
        "title": title,
        "cover_url": DEFAULT_COVER,
        "lead": lead,
        "sections": sections,
        "sources": sources[:6],
        "footer": f"本文由 zero-wechat-article-agent 全自动流水线生成（{datetime.now(BJ).strftime('%Y-%m-%d %H:%M')} 北京时间）。发布前请人工润色。",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--twitter-json", required=True)
    p.add_argument("--attentionvc-json", required=True)
    p.add_argument("--out", default="brief.auto.json")
    args = p.parse_args()
    tw = json.loads(Path(args.twitter_json).read_text(encoding="utf-8"))
    av = json.loads(Path(args.attentionvc_json).read_text(encoding="utf-8"))
    brief = build_brief(tw, av)
    Path(args.out).write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": args.out, "title": brief["title"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
