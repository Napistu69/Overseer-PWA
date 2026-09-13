#!/bin/bash
# Build script for TekTribe Chronicles PWA
# Generates Compendium index + API, then builds Hugo site

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   TEKTRIBE CHRONICLES - BUILD                            ║"
echo "╚══════════════════════════════════════════════════════════╝"

SITE_DIR="/c/Users/Nefs/Projects/CompendiumPWA"
cd "$SITE_DIR"

# Step 1: Generate Compendium search index
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Compendium Search Index"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/index_compendium.py

# Step 2: Generate Compendium API endpoints
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Compendium API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/generate_api.py

# Step 3: Build Hugo site
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Hugo Build"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
hugo --gc --minify

# Step 4: Generate service worker
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Service Worker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/generate_sw.py

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   BUILD COMPLETE                                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Output: public/"
echo ""

# Verify key files
echo "Verification:"
[ -f public/index.html ] && echo "  ✅ Home page" || echo "  ❌ Home page"
[ -f public/compendium-index.json ] && echo "  ✅ Compendium index" || echo "  ❌ Compendium index"
[ -f public/api/compendium/manifest.json ] && echo "  ✅ API manifest" || echo "  ❌ API manifest"
[ -d public/api/compendium/files ] && echo "  ✅ API files ($(ls public/api/compendium/files/*.json 2>/dev/null | wc -l) files)" || echo "  ❌ API files"
[ -f public/oracle/index.html ] && echo "  ✅ Oracle page" || echo "  ❌ Oracle page"
[ -f public/governance/index.html ] && echo "  ✅ Governance page" || echo "  ❌ Governance page"
[ -f public/manifest.json ] && echo "  ✅ PWA manifest" || echo "  ❌ PWA manifest"
[ -f public/sw.js ] && echo "  ✅ Service worker" || echo "  ❌ Service worker"
