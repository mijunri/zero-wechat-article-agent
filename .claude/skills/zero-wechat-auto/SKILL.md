---
name: zero-wechat-auto
description: >
  Run the full AI blogger WeChat pipeline in one command: Twitter + AttentionVC collect,
  auto brief, HTML, upload to manage.foxrouter.com platform=wechat. USE when user says
  全自动、每日推送、跑一遍流水线、auto daily wechat, or cannot see articles on deliverables page.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/../../scripts/*)
metadata:
  version: "1.0.0"
---

# zero-wechat-auto

标准流程（AttentionVC #1 → Twitter 长文 → 中文理解 → 发布）：

```bash
pip install -e .
source .claude/skills/zero-twitter-collect/scripts/env.sh
source .claude/skills/zero-deliverables/scripts/env.sh
python3 scripts/auto_daily_wechat.py
# 等同 scripts/pipeline_top_article.py
```

**看不到文章？** `agent.env` 中的 `ZAM_API_KEY` 须为 **mongo**；`curl -H "Authorization: Bearer $ZAM_API_KEY" $ZAM_API_BASE/api/auth/me` 核对 email。

详见仓库根目录 [`CLAUDE.md`](../../../CLAUDE.md)。
