#!/bin/bash
# Load API credentials for zero-deliverables skill.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "${SKILL_DIR}/scripts/agent.env" ]]; then
  # shellcheck source=/dev/null
  source "${SKILL_DIR}/scripts/agent.env"
fi
export ZAM_API_BASE="${ZAM_API_BASE:-http://api-manage.foxrouter.com}"
export ZAM_API_KEY="${ZAM_API_KEY:-}"
