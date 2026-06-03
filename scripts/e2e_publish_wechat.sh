#!/usr/bin/env bash
# End-to-end: brief → HTML → manage.foxrouter.com (platform=wechat)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIEF="${1:-${ROOT}/examples/brief-daily-ai.json}"

if [[ -z "${ZAM_API_KEY:-}" ]]; then
  echo "Export ZAM_API_KEY first" >&2
  exit 1
fi

bash "${ROOT}/.claude/skills/zero-deliverables/scripts/verify.sh"
python3 "${ROOT}/.claude/skills/zero-wechat-article-write/scripts/write_article.py" pipeline \
  --brief-file "${BRIEF}"
