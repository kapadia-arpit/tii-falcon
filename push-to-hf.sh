#!/bin/bash
# Usage: HF_TOKEN=hf_xxx bash push-to-hf.sh
# Requires: git, curl
# Run this AFTER creating the Space at https://huggingface.co/new-space

set -e

HF_USER="kapadiaarpit"
SPACE_NAME="falcon3-chat"
SPACE_URL="https://${HF_USER}:${HF_TOKEN}@huggingface.co/spaces/${HF_USER}/${SPACE_NAME}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$(mktemp -d)"

echo "→ Cloning HF Space repo..."
git clone "$SPACE_URL" "$TMP_DIR/space"

echo "→ Copying backend files..."
cp "$SCRIPT_DIR/backend/main.py"          "$TMP_DIR/space/"
cp "$SCRIPT_DIR/backend/requirements.txt" "$TMP_DIR/space/"
cp "$SCRIPT_DIR/backend/Dockerfile"       "$TMP_DIR/space/"

# HF Spaces needs a README with specific frontmatter to configure the space
cat > "$TMP_DIR/space/README.md" <<'EOF'
---
title: Falcon3 Chat
emoji: 🦅
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

FastAPI + Falcon3-1B-Instruct streaming chat backend.
Source: https://github.com/kapadia-arpit/tii-falcon
EOF

echo "→ Pushing to HuggingFace Spaces..."
cd "$TMP_DIR/space"
git add .
git commit -m "deploy: Falcon3-1B-Instruct FastAPI backend"
git push

echo ""
echo "✓ Done. Space URL: https://huggingface.co/spaces/${HF_USER}/${SPACE_NAME}"
echo "  Backend will be live at: https://${HF_USER}-${SPACE_NAME}.hf.space"
echo "  (First build takes ~5 min — watch logs in the Space UI)"

rm -rf "$TMP_DIR"
