#!/bin/bash
# Build script for TekTribe Chronicles PWA
# Runs the Akashic Research indexer, generates versioned SW, then Hugo build

echo "=== TekTribe Chronicles PWA Build ==="

# Step 1: Index Akashic Research
echo "Indexing Akashic Research..."
python scripts/index_akashic.py

# Step 2: Generate versioned service worker
echo "Generating versioned service worker..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
sed "s/{{VERSION}}/$TIMESTAMP/g" static/js/sw.js > static/js/sw-versioned.js
mv static/js/sw-versioned.js static/js/sw.js

# Step 3: Build Hugo site
echo "Building Hugo site..."
hugo --gc --minify

echo "=== Build Complete ==="
