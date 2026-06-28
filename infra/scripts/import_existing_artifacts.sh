#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntu/projects/eg-addressing"
mkdir -p "$ROOT/docs/source-proposals" "$ROOT/artifacts/legacy"

cp -f /home/ubuntu/national-addressing-pack/* "$ROOT/docs/source-proposals/" 2>/dev/null || true
cp -f /home/ubuntu/national-addressing-proposal/* "$ROOT/artifacts/legacy/" 2>/dev/null || true
cp -f /home/ubuntu/generate_addressing_proposal.py "$ROOT/artifacts/legacy/" 2>/dev/null || true

echo "Imported existing addressing artifacts into isolated workspace."
