#!/usr/bin/env bash
# Load TwitterAPI.io credentials for zero-twitter-collect.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "${SKILL_DIR}/scripts/agent.env" ]]; then
  # shellcheck source=/dev/null
  source "${SKILL_DIR}/scripts/agent.env"
fi
export TWITTERAPI_IO_KEY="${TWITTERAPI_IO_KEY:-}"
