#!/usr/bin/env bash
set -euo pipefail

TARGET_DEFAULT="$HOME/.openclaw/skills/openclaw-council"
TARGET="${1:-$TARGET_DEFAULT}"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$TARGET"
rsync -a --delete \
  --exclude '.git' \
  --exclude 'council.config.json' \
  --exclude 'run.json' \
  --exclude 'report.md' \
  "$SRC_DIR/" "$TARGET/"

echo "Installed to: $TARGET"
echo "Next: cp $TARGET/examples/council.config.example.json $TARGET/council.config.json"
echo "Then set env vars OPENAI_API_KEY and GEMINI_API_KEY"
