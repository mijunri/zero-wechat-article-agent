#!/usr/bin/env bash
# zero-twitter-collect reads twitter_api_key from the process environment.
# Optional: source a local file if present (gitignored).
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "${SKILL_DIR}/scripts/agent.env" ]]; then
  # shellcheck source=/dev/null
  source "${SKILL_DIR}/scripts/agent.env"
fi
