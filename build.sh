#!/bin/bash
# Build script for TekTribe Chronicles PWA
# Generates Compendium index + API, then builds Hugo site

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   TEKTRIBE CHRONICLES - BUILD                            ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Detect script directory (works on Windows/MSYS and Linux)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Step 0: Retired-terminology gate (fail fast, before anything is generated)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 0: Retired-Terminology Gate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/check_retired_terms.py

# Step 0b: Content-shape gate (source shapes that render badly)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 0b: Content-Shape Gate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/check_content_shape.py

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

# Step 3b: Generate service worker (a build OUTPUT — everything that validates the output
# must run after all generators, or a fresh checkout fails on an artifact that simply has not
# been made yet. That ordering bug is what kept the deploy red today.)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3b: Service Worker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/generate_sw.py

# Step 4: Rendered-output shape check (post-Hugo, against the COMPLETE public/)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Rendered-Shape Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python scripts/check_rendered_shape.py

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
[ -d public/api/compendium ] && echo "  ✅ API files ($(ls public/api/compendium/*.json 2>/dev/null | wc -l) files)" || echo "  ❌ API files"
[ -f public/oracle/index.html ] && echo "  ✅ Oracle page" || echo "  ❌ Oracle page"
[ -f public/governance/index.html ] && echo "  ✅ Governance page" || echo "  ❌ Governance page"
[ -f public/manifest.json ] && echo "  ✅ PWA manifest" || echo "  ❌ PWA manifest"
[ -f public/sw.js ] && echo "  ✅ Service worker" || echo "  ❌ Service worker"
