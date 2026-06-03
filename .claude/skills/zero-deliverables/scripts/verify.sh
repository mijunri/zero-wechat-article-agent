#!/bin/bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=/dev/null
source "${SKILL_DIR}/scripts/env.sh"
if [[ -z "${ZAM_API_KEY:-}" ]]; then
  echo "Missing ZAM_API_KEY — export in environment or scripts/agent.env" >&2
  exit 1
fi
python3 "${SKILL_DIR}/scripts/deliverables.py" list >/dev/null
ME=$(curl -sS -H "Authorization: Bearer ${ZAM_API_KEY}" "${ZAM_API_BASE}/api/auth/me")
echo "zero-deliverables OK (${ZAM_API_BASE}) account=${ME}"
