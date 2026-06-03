---
name: zero-toutiao-entertainment
description: >
  Daily Toutiao (头条号) entertainment news workflow: fetch Chinese hot topics via hot-topics/60s API,
  filter 娱乐-only, compose 3 publish-ready articles, upload to manage.foxrouter.com platform=toutiao.
  USE when user mentions 头条号、娱乐新闻、每日三篇、hot-topics、热搜写稿、toutiao deliverable,
  or wants entertainment-only content pipeline (not politics/tech macro news).
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
metadata:
  version: "1.0.0"
  argument-hint: "[pipeline | fetch | compose | publish]"
---

# zero-toutiao-entertainment

头条号 **娱乐新闻** 日产线（每日 3 篇）。**成稿规范以 [`entertainment-article`](../entertainment-article/SKILL.md) 为准**（来自 `ai-article` 仓库），本 Skill 负责编排与发布。

依赖：[`hot-topics`](../hot-topics/SKILL.md) 拉热榜 → [`entertainment-article`](../entertainment-article/SKILL.md) 搜索+写作 → [`zero-deliverables`](../zero-deliverables/SKILL.md) 上传。

## 依赖

| 组件 | 说明 |
|------|------|
| `hot-topics` | `60s.viki.moe` 微博/抖音/头条热榜 |
| `zero-deliverables` | `platform=toutiao` 上传指挥台 |

```bash
source .claude/skills/zero-deliverables/scripts/env.sh
pip install -e .   # 可选，流水线用 stdlib + deliverables
```

## 一键（每日 3 篇）

```bash
python3 scripts/pipeline_daily_toutiao_entertainment.py
```

流程：

```text
weibo + douyin + toutiao 热榜
  → entertainment_filter
  → volc-search 两轮（research_topic.py → data/searchdata/）
  → compose_from_research.py（entertainment-article 短篇）
  → publish_toutiao → platform=toutiao
```

预览：http://manage.foxrouter.com/app/deliverables?platform=toutiao

## 分步

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"

# 1) 娱乐热点池
python3 "${SKILL_DIR}/scripts/fetch_entertainment_hot.py" --limit 20 --json-out /tmp/hot.json

# 2) 单条成稿（从 hot.json 取 items[0] 存为 topic.json）
python3 "${SKILL_DIR}/scripts/compose_toutiao_article.py" \
  --topic-json /tmp/topic.json --out /tmp/article.json --html-out /tmp/article.html

# 3) 质量门禁
python3 "${SKILL_DIR}/scripts/quality_check.py" --article-json /tmp/article.json

# 4) 发布
python3 "${SKILL_DIR}/scripts/publish_toutiao.py" --article-json /tmp/article.json
```

## 成稿规范（头条号）

详见 [references/toutiao-style.md](references/toutiao-style.md)。

- 标题 8–30 字，信息具体，避免空洞「震惊」
- 正文 550–2200 字（汉字），短段落
- 结构：导语 → 背景解读 → 网友/行业视角 → 互动收尾
- 必须附热榜来源链接；文末注明待人工核对

## 过滤规则

- **保留**：明星、综艺、影视、情感八卦、婚礼红毯等
- **排除**：时政、外交、军事、宏观经济、灾害通报、考试政策等

脚本：`entertainment_filter.py`（可随业务调关键词）。

## 与 hot-topics 关系

- `hot-topics`：通用热榜拉取（多平台）
- 本 Skill：在热榜之上做 **娱乐筛选 + 头条成稿 + 发布**

安装 upstream skill：

```bash
npx skills add https://github.com/vikiboss/60s-skills --skill hot-topics
# 本仓库已同步至 .claude/skills/hot-topics
```
