#!/usr/bin/env bash
# Run Claude Code on your own machine with Z.ai GLM models instead of Claude.
# Uses Z.ai's Anthropic-compatible endpoint (docs.z.ai/scenario-example/develop-tools/claude).
# Free Flash models via this endpoint are UNVERIFIED; the GLM Coding Plan may be required.
# Usage: ZAI_API_KEY=... scripts/claude-glm.sh [claude args]
set -euo pipefail
: "${ZAI_API_KEY:?set ZAI_API_KEY}"
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY"
export API_TIMEOUT_MS="${API_TIMEOUT_MS:-3000000}"
export ANTHROPIC_DEFAULT_OPUS_MODEL="${GLM_OPUS_MODEL:-glm-4.7}"
export ANTHROPIC_DEFAULT_SONNET_MODEL="${GLM_SONNET_MODEL:-glm-4.7-flash}"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="${GLM_HAIKU_MODEL:-glm-4.5-flash}"
exec claude "$@"
