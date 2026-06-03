#!/bin/bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=/dev/null
source "${SKILL_DIR}/scripts/env.sh"
if [[ -z "${ZAM_API_KEY}" ]]; then
  echo "Missing ZAM_API_KEY in ${SKILL_DIR}/scripts/agent.env"
  exit 1
fi
python3 "${SKILL_DIR}/scripts/deliverables.py" list >/dev/null
echo "zero-deliverables OK (${ZAM_API_BASE})"
