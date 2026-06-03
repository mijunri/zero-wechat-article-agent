#!/usr/bin/env bash
# Full auto (collect + write + upload). Pass a brief path only for manual override.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${1:-}" ]]; then
  export ZAM_API_KEY="${ZAM_API_KEY:?}"
  python3 "${ROOT}/.claude/skills/zero-wechat-article-write/scripts/write_article.py" pipeline \
    --brief-file "$1"
else
  exec python3 "${ROOT}/scripts/auto_daily_wechat.py"
fi
