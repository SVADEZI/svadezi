#!/bin/bash
set -euo pipefail

# Install the headroom package (with dev + mcp extras) so tests and the MCP
# server work in Claude Code on the web sessions.
#
# A dedicated virtualenv is used because the [mcp] dependency chain conflicts
# with Debian-managed system packages when installed into the global site.
# Idempotent (safe to re-run) and non-interactive.

cd "$CLAUDE_PROJECT_DIR"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

./.venv/bin/pip install --quiet -e ".[dev,mcp]"

# Put the venv on PATH for the rest of the session so `headroom`, `pytest`, and
# `python` resolve to it. CLAUDE_ENV_FILE is only present in the hook runtime.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
  echo "export VIRTUAL_ENV=\"$CLAUDE_PROJECT_DIR/.venv\"" >> "$CLAUDE_ENV_FILE"
fi
