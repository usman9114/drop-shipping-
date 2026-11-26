#!/usr/bin/env bash
# Owner-approved install of OpenAI Codex CLI (Apache-2.0, github.com/openai/codex).
# Pinned version; installs into tools/codex (gitignored), not globally.
# Decision: docs/decisions/0019-chatgpt-lane.md
set -euo pipefail
CODEX_VERSION="0.169.0"   # released 2026-11-13; bump only after reading the changelog
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
npm install --prefix "$ROOT/tools/codex" --no-fund --no-audit "@openai/codex@${CODEX_VERSION}"
"$ROOT/tools/codex/node_modules/.bin/codex" --version
echo "Next: tools/codex/node_modules/.bin/codex login --device-auth   (sign in with your ChatGPT account)"
