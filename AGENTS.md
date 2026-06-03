# AGENTS.md — zero-wechat-article-agent

以 [`CLAUDE.md`](./CLAUDE.md) 为准。

## Skills

| Skill | 路径 |
|-------|------|
| `zero-twitter-collect` | `.claude/skills/zero-twitter-collect/SKILL.md` |
| `zero-attentionvc-scrape` | `.claude/skills/zero-attentionvc-scrape/SKILL.md` |
| `zero-wechat-article-write` | `.claude/skills/zero-wechat-article-write/SKILL.md` |
| `zero-deliverables` | `.claude/skills/zero-deliverables/SKILL.md` |
| `zero-wechat-article` | `.claude/skills/zero-wechat-article/SKILL.md` |
| `hot-topics` | `.claude/skills/hot-topics/SKILL.md` |
| `entertainment-article` | `.claude/skills/entertainment-article/SKILL.md`（来自 `ai-article`） |
| `volc-search` | `.claude/skills/volc-search/SKILL.md` |
| `zero-toutiao-entertainment` | `.claude/skills/zero-toutiao-entertainment/SKILL.md` |

## 默认交付

- 公众号：`platform=wechat`（`pipeline_top_article.py`）
- 头条号娱乐：`platform=toutiao`，每日 3 篇（`pipeline_daily_toutiao_entertainment.py`）

`hot-topics` 安装：`npx skills add https://github.com/vikiboss/60s-skills --skill hot-topics`（仓库已同步至 `.claude/skills/hot-topics`）。
