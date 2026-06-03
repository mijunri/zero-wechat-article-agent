---
name: zero-wechat-article-write
description: >
  Draft WeChat Official Account HTML articles for an AI knowledge blogger: outline from
  brief JSON or collection signals, render wechat-safe HTML, optionally publish to
  manage.foxrouter.com via zero-deliverables. USE when user mentions 写公众号、生成图文、
  AI 公众号文章、wechat article HTML、上传指挥台、manage.foxrouter.com deliverables wechat.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
metadata:
  version: "1.0.0"
  argument-hint: "[write|publish|pipeline] ..."
---

# zero-wechat-article-write

为 **AI 知识博主** 生成微信公众号 **HTML 正文**（非纯 Markdown），并可选上传到 [manage.foxrouter.com 产物库](http://manage.foxrouter.com/app/deliverables?platform=wechat)。

## 工作流（默认）

```text
采集 (twitter / attentionvc) → 选题 brief.json → write → HTML
    → zero-deliverables create --platform wechat → 指挥台预览
```

## 启动

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"
bash "${SKILL_DIR}/scripts/verify.sh"
```

## CLI

```bash
# 1) 从 brief JSON 生成 HTML
python3 "${SKILL_DIR}/scripts/write_article.py" write \
  --brief-file ./brief.json \
  --out ./article.html

# 2) 上传到指挥台（需 ZAM_API_KEY）
python3 "${SKILL_DIR}/scripts/write_article.py" publish \
  --title "文章标题" \
  --html-file ./article.html \
  --cover "https://example.com/cover.jpg"

# 3) 一键：brief → HTML → 上传
python3 "${SKILL_DIR}/scripts/write_article.py" pipeline \
  --brief-file ./brief.json
```

## brief.json 格式

见 [references/brief-schema.md](references/brief-schema.md)。

## 与 zero-deliverables 的关系

- **写稿**：本 Skill（HTML 结构与中文叙事）
- **入库**：`zero-deliverables`（`platform=wechat`，`content_html` 为 HTML）

上传后打开：http://manage.foxrouter.com/app/deliverables?platform=wechat

## 原则

- 二次创作，标注参考来源；禁止整篇搬运 AttentionVC / Twitter 原文
- 发布到公众号后台仍走 `zero-wechat-article` + 人工确认
