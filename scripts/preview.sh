#!/usr/bin/env bash
# Compendium Preview Workflow
# Starts Hugo dev server with hot-reload

set -e

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HUGO="$SITE_DIR/hugo.exe"

echo "=== COMPENDIUM PREVIEW ==="
echo "Starting Hugo dev server..."
echo "Open: http://localhost:1313"
echo "Press Ctrl+C to stop"
echo ""

cd "$SITE_DIR"
$HUGO server -D --disableLiveReload=false
