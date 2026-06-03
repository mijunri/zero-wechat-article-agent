#!/usr/bin/env python3
"""
Translate source article to Chinese and compose a WeChat brief (commentary style).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _translate_zh(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator
    except ImportError as e:
        raise SystemExit(
            "Install deep-translator: pip install deep-translator"
        ) from e

    translator = GoogleTranslator(source="auto", target="zh-CN")
    chunks: list[str] = []
    # Google translate limit ~5000; use smaller chunks
    size = 3500
    for i in range(0, len(text), size):
        part = text[i : i + size]
        chunks.append(translator.translate(part))
    return "\n".join(chunks)


def _clean_markdown_line(line: str) -> str:
    line = line.strip()
    if line.startswith("## "):
        return line[3:].strip()
    if line.startswith("### "):
        return line[4:].strip()
    if line.startswith("> "):
        return line[2:].strip()
    if line.startswith("- "):
        return line[2:].strip()
    return line


def _split_paragraphs(text: str, max_paras: int = 12) -> list[str]:
    paras: list[str] = []
    for block in re.split(r"\n\n+", text):
        block = block.strip()
        if not block:
            continue
        lines = [_clean_markdown_line(ln) for ln in block.splitlines() if ln.strip()]
        if len(lines) == 1:
            paras.append(lines[0])
        else:
            paras.append("\n".join(lines))
    return paras[:max_paras]


def _metrics_line(av: dict, tw: dict) -> str:
    views = av.get("view_count") or tw.get("view_count") or 0
    likes = tw.get("like_count") or av.get("like_count") or 0
    return f"原文约 {views:,} 次浏览、{likes:,} 点赞（AttentionVC / X 统计）。"


def build_brief(attentionvc_item: dict, tweet_article: dict, *, chinese_full: str) -> dict[str, Any]:
    title_en = attentionvc_item.get("title") or tweet_article.get("title") or "AI 热榜长文"
    handle = attentionvc_item.get("author_handle") or tweet_article.get("author_username") or ""
    title_zh = _translate_zh(title_en) if re.search(r"[A-Za-z]", title_en) else title_en
    wechat_title = f"深度解读｜{title_zh}"
    if len(wechat_title) > 64:
        wechat_title = wechat_title[:61] + "…"

    cover = (
        attentionvc_item.get("cover_image_url")
        or tweet_article.get("cover_url")
        or (tweet_article.get("image_urls") or [None])[0]
        or ""
    )

    preview_src = (
        attentionvc_item.get("preview_text")
        or tweet_article.get("preview_text")
        or ""
    )
    preview_zh = _translate_zh(preview_src) if preview_src else ""
    paras = _split_paragraphs(chinese_full, max_paras=12)

    lead = (
        f"AttentionVC AI 热榜第 1 名长文，作者 @{handle}。"
        f"{_metrics_line(attentionvc_item, tweet_article)}"
        f"下文为原文要点的中文理解，并附上 AI 知识博主视角的解读。"
    )

    sections: list[dict[str, Any]] = [
        {
            "h2": "原文在讲什么",
            "paragraphs": [preview_zh] if preview_zh else [paras[0] if paras else "（暂无摘要）"],
        },
    ]

    # Main body: group paragraphs
    body_paras = paras[1:7] if len(paras) > 1 else paras
    if body_paras:
        sections.append(
            {
                "h2": "核心内容（中文理解）",
                "paragraphs": body_paras[:5],
            }
        )

    tags = attentionvc_item.get("tags") or []
    topics = attentionvc_item.get("trending_topics") or []
    insight_bits = []
    if tags:
        insight_bits.append(f"话题标签：{', '.join(tags[:6])}。")
    if topics:
        insight_bits.append(f"相关热词：{', '.join(topics[:6])}。")
    insight_bits.append(
        "对公众号读者的价值：不必追英文原文，抓住「模型对比 + 测试方法论 + 结论」即可做二次创作；"
        "避免整段搬运，建议结合你自己的实验或国内产品做对照。"
    )
    sections.append({"h2": "AI 博主怎么看", "paragraphs": insight_bits})

    sections.append(
        {
            "h2": "今日可执行动作",
            "paragraphs": [
                "1）用同一组 prompt 复现文内测试，截图对比国内可用模型。",
                "2）写「一张表看懂：ChatGPT / Gemini / Grok 立场差异」。",
                "3）在文末引导读者留言：你最常用哪家模型？",
            ],
        }
    )

    images = tweet_article.get("image_urls") or []
    if images:
        target = sections[1] if len(sections) > 1 else sections[0]
        target["image"] = images[0]

    return {
        "title": wechat_title,
        "cover_url": cover,
        "lead": lead,
        "sections": sections,
        "sources": [
            {
                "label": f"AttentionVC 热榜 · @{handle}",
                "url": attentionvc_item.get("tweet_url") or tweet_article.get("tweet_url") or "",
            },
            {
                "label": f"X 原文 @{handle}",
                "url": tweet_article.get("tweet_url") or "",
            },
        ],
        "footer": "本文由 zero-wechat-article-agent 根据热榜第 1 名自动采集、翻译并改写，发布前请人工审核。",
        "_meta": {
            "source_title_en": title_en,
            "tweet_id": tweet_article.get("tweet_id"),
            "chinese_chars": len(chinese_full),
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--attentionvc-json", required=True, help="JSON with single article in articles[0]")
    p.add_argument("--tweet-json", required=True, help="Output of get_tweet_article.py")
    p.add_argument("--out", default="brief.json")
    args = p.parse_args()

    av = json.loads(Path(args.attentionvc_json).read_text(encoding="utf-8"))
    tw = json.loads(Path(args.tweet_json).read_text(encoding="utf-8"))
    item = (av.get("articles") or [av])[0]

    english = tw.get("full_text") or item.get("preview_text") or ""
    chinese_full = _translate_zh(english)
    brief = build_brief(item, tw, chinese_full=chinese_full)
    Path(args.out).write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {"out": args.out, "title": brief["title"], "chinese_chars": len(chinese_full)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
