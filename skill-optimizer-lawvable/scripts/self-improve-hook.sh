#!/bin/bash

# Self-Improve Hook Script (original Claude Code design)
# -------------------------------------------------------
# This script was written for Claude Code "stop" hooks.
# It is NOT executed by Grok.
#
# On Grok, automatic mode is advisory only:
# - Controlled by the presence/absence of
#   /home/workdir/.grok/skills/skill-optimizer-lawvable/.disabled
# - The agent proactively offers self-improve after skill usage
#   when the flag is enabled; it never silently rewrites skills.
#
# Kept for reference and for any future Claude Code compatibility.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DISABLED_FILE="${SKILL_DIR}/.disabled"

# Check if disabled (automatic mode off)
if [ -f "$DISABLED_FILE" ]; then
  exit 0
fi

# Automatic mode is enabled — emit the advisory system message
# (only relevant if this script is ever wired into a stop hook)
cat << 'EOF'
{"systemMessage": "AUTOMATIC SELF-IMPROVE MODE ENABLED (advisory). Before ending this session or after significant skill usage, analyze the conversation for potential skill improvements. Follow the workflow in the skill-optimizer-lawvable skill: detect corrections, evaluate against the 4 criteria, and propose any improvements to the user for approval. Never edit skills without explicit approval. If no improvements detected, say so briefly."}
EOF
