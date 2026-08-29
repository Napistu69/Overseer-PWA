#!/bin/bash
# Build script for TekTribe Chronicles PWA
# Uses chroma index (5197 chunks) directly — no Python indexing

echo "=== TekTribe Chronicles PWA Build ==="

# Step 1: Copy chroma index as akashic-index.json (converting to Oracle format)
echo "Copying chroma index..."
python -c "
import json
with open('C:/TekTribe/Overseer/akashic_research/embeddings/chroma/chunks_index.json') as f:
    chroma = json.load(f)
files = set(d.get('file_name', '') for d in chroma)
output = {
    'meta': {'total_files': len(files), 'total_chunks': len(chroma)},
    'chunks': chroma
}
with open('static/akashic-index.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False)
print(f'Index: {len(chroma)} chunks, {len(files)} files')
"

# Step 2: Build Hugo site
echo "Building Hugo site..."
hugo --gc --minify

# Step 3: Generate service worker with full URL list
echo "Generating versioned service worker..."
python scripts/generate_sw.py

echo "=== Build Complete ==="
