#!/usr/bin/env python3
"""
Akashic Research Index Generator
Indexes all markdown files in the Akashic Research folder for client-side search.
Run this script before Hugo build to regenerate the search index.
"""

import os
import re
import json
import hashlib
from pathlib import Path

# Configuration
AKASHIC_DIR = r"C:\TekTribe\Overseer\akashic_research"
OUTPUT_PATH = r"C:\Users\Nefs\Projects\CompendiumPWA\static\akashic-index.json"
CHUNK_SIZE = 150  # words per chunk
OVERLAP = 50      # words of overlap between chunks

def split_by_headings(text):
    """Split markdown text by ## headings, preserving heading hierarchy."""
    chunks = []
    # Split on ## headings (not # which is usually the title)
    parts = re.split(r'(?=^##\s+)', text, flags=re.MULTILINE)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Extract heading
        heading_match = re.match(r'^##\s+(.+)$', part, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else ""
        
        # Remove the heading line from content
        content = re.sub(r'^##\s+.+$', '', part, count=1, flags=re.MULTILINE).strip()
        
        if content:
            chunks.append({
                "heading": heading,
                "content": content
            })
    
    return chunks

def sliding_window_chunk(text, heading, filename, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Create overlapping chunks from text for better search precision."""
    words = text.split()
    if len(words) <= chunk_size:
        return [{
            "text": " ".join(words),
            "heading": heading,
            "source": filename,
            "word_count": len(words)
        }]
    
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunks.append({
            "text": " ".join(chunk_words),
            "heading": heading,
            "source": filename,
            "word_count": len(chunk_words)
        })
        if i + chunk_size >= len(words):
            break
    
    return chunks

def index_file(filepath):
    """Index a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return []
    
    # Remove frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Get relative path for source attribution
    rel_path = os.path.relpath(filepath, AKASHIC_DIR)
    
    # Split by headings
    sections = split_by_headings(content)
    
    chunks = []
    for section in sections:
        # Create sliding window chunks for each section
        section_chunks = sliding_window_chunk(
            section["content"],
            section["heading"],
            rel_path
        )
        chunks.extend(section_chunks)
    
    return chunks

def generate_index():
    """Generate the full search index."""
    print("Generating Akashic Research search index...")
    
    all_chunks = []
    file_count = 0
    
    # Walk through all markdown files
    for root, dirs, files in os.walk(AKASHIC_DIR):
        for filename in sorted(files):
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                print(f"  Indexing: {filename}")
                
                chunks = index_file(filepath)
                all_chunks.extend(chunks)
                file_count += 1
    
    # Create index object
    index = {
        "meta": {
            "total_files": file_count,
            "total_chunks": len(all_chunks),
            "generated": hashlib.md5(str(os.path.getmtime(AKASHIC_DIR)).encode()).hexdigest()[:8]
        },
        "chunks": all_chunks
    }
    
    # Write to output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\nIndex generated successfully!")
    print(f"  Files indexed: {file_count}")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Output: {OUTPUT_PATH}")
    
    return index

if __name__ == "__main__":
    generate_index()
