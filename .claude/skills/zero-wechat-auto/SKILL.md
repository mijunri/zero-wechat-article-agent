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

入口脚本（仓库根目录）：

```bash
export twitter_api_key="..."
export ZAM_API_KEY="zam_..."    # 必须与浏览器登录账号一致
python3 scripts/auto_daily_wechat.py
```

**看不到文章？** 先 `curl -H "Authorization: Bearer $ZAM_API_KEY" $ZAM_API_BASE/api/auth/me` 核对 email。

详见仓库根目录 [`CLAUDE.md`](../../../CLAUDE.md)。
