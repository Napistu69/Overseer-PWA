#!/bin/bash
# Build script for TekTribe Chronicles
# Runs the Akashic Research indexer before Hugo build

echo "=== TekTribe Chronicles Build ==="

# Step 1: Index Akashic Research
echo "Indexing Akashic Research..."
python scripts/index_akashic.py

# Step 2: Build Hugo site
echo "Building Hugo site..."
hugo --gc --minify

echo "=== Build Complete ==="
