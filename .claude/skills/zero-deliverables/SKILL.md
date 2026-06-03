---
name: zero-deliverables
description: >
  Manage zero-agent-manage deliverables (产物): list by Beijing date, get, create, update, delete.
  USE when user mentions 产物、微信公众号文章、头条号、百家号、小红书、推特、Twitter、多图笔记、deliverable、上传文章、
  zero-agent-manage API, or managing content outputs on manage.foxrouter.com.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/*)
metadata:
  version: "1.0.0"
  argument-hint: "[list|get|create|update|delete] ..."
---

# zero-deliverables — 产物 API

调用 **zero-agent-manage** 后端 `api-manage.foxrouter.com`，鉴权为 API Key（与登录用户同等权限）。

## 启动（每次必做）

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR}"
source "${SKILL_DIR}/scripts/env.sh"
bash "${SKILL_DIR}/scripts/verify.sh"
```

凭证在 `scripts/agent.env`（已配置 `ZAM_API_KEY`，勿提交到公开仓库）。

## CLI

```bash
# 按日分组列表（可选平台 wechat|toutiao|baijiahao|xiaohongshu|twitter）
python3 "${SKILL_DIR}/scripts/deliverables.py" list
python3 "${SKILL_DIR}/scripts/deliverables.py" list --platform xiaohongshu

# 详情
python3 "${SKILL_DIR}/scripts/deliverables.py" get --id 1

# 创建（文章）
python3 "${SKILL_DIR}/scripts/deliverables.py" create \
  --platform wechat \
  --title "标题" \
  --cover "https://example.com/cover.jpg" \
  --html-file ./article.html

# 创建（小红书：纯文案 + 多图，勿用 HTML）
python3 "${SKILL_DIR}/scripts/deliverables.py" create \
  --platform xiaohongshu \
  --title "周末探店｜标题" \
  --text-file ./note.txt \
  --image-urls "https://a.jpg,https://b.jpg,https://c.jpg"

# 创建（推特：纯文案，图片可选）
python3 "${SKILL_DIR}/scripts/deliverables.py" create \
  --platform twitter \
  --title "Post headline" \
  --text-file ./post.txt

# 更新
python3 "${SKILL_DIR}/scripts/deliverables.py" update --id 1 --title "新标题"

# 删除
python3 "${SKILL_DIR}/scripts/deliverables.py" delete --id 1
```

## API 摘要

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/deliverables/grouped` | 按北京时间分组列表 |
| GET | `/api/deliverables/{id}` | 详情 |
| POST | `/api/deliverables` | 创建 |
| PUT | `/api/deliverables/{id}` | 更新 |
| DELETE | `/api/deliverables/{id}` | 删除 |

鉴权：`Authorization: Bearer $ZAM_API_KEY` 或 `X-API-Key: $ZAM_API_KEY`。

详见 [references/api.md](references/api.md)。
