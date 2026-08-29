#!/bin/bash
# Build script for TekTribe Chronicles PWA
# Runs the Akashic Research indexer, generates versioned SW with full URL list, then Hugo build

echo "=== TekTribe Chronicles PWA Build ==="

# Step 1: Index Akashic Research
echo "Indexing Akashic Research..."
python scripts/index_akashic.py

# Step 2: Build Hugo site
echo "Building Hugo site..."
hugo --gc --minify

# Step 3: Generate service worker with full URL list
echo "Generating versioned service worker..."
python scripts/generate_sw.py

echo "=== Build Complete ==="
