#!/usr/bin/env python3
"""
Compendium Index Generator
Indexes all markdown files in the PWA content/ folder for client-side search.
This is a COMPENDIUM-only index — not the full Akashic research archive.
Run this script before Hugo build to regenerate the search index.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Configuration — derive paths from script location for cross-platform compat
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(SCRIPT_DIR)
CONTENT_DIR = os.path.join(SITE_DIR, "content")
OUTPUT_PATH = os.path.join(SITE_DIR, "static", "compendium-index.json")
CHUNK_SIZE = 150  # words per chunk
OVERLAP = 50      # words of overlap between chunks

# Markdown markers are for rendering, not for search. Indexing them verbatim is what put
# "syntax" into search results (measured before this pass: 43% of chunks carried `**`,
# 11% carried table pipes, 7% carried `##`). Cleaned at the single choke point that every
# chunk passes through, so both the section and whole-body branches are covered.
MD_CLEAN = [
    (re.compile(r"<!--.*?-->", re.S), " "),                 # html comments
    (re.compile(r"^\s*[-*_]{3,}\s*$", re.M), " "),          # horizontal rules
    (re.compile(r"^\s{0,3}#{1,6}\s*", re.M), ""),           # heading hashes
    (re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$", re.M), " "),    # table separator rows
    (re.compile(r"\|"), " "),                               # table cell pipes
    (re.compile(r"\*\*|__|\*|`|_"), ""),                    # emphasis / code markers
    (re.compile(r"^\s*[-*+]\s+", re.M), ""),                # list bullets
    (re.compile(r"^\s*>\s?", re.M), ""),                    # blockquote markers
]


def clean_markdown(text: str) -> str:
    for rx, rep in MD_CLEAN:
        text = rx.sub(rep, text)
    # Keep LINE BREAKS. Collapsing every newline fuses the last word of one line with the
    # first of the next — in a glossary list that manufactured an "Overseer Æ" adjacency out
    # of "...the Overseer" + "Æ (Artificial Educator)", i.e. the cleaner inventing the very
    # drift the check hunts. Whitespace inside a line is collapsed; line structure is kept.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(l.split()) for l in text.split("\n")]
    return "\n".join(l for l in lines if l.strip())

def parse_frontmatter(text):
    """Extract YAML frontmatter from markdown text."""
    if not text.startswith('---'):
        return {}, text
    
    end = text.find('---', 3)
    if end == -1:
        return {}, text
    
    fm_text = text[3:end].strip()
    content = text[end+3:].strip()
    
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            val = val.strip().strip('"').strip("'")
            fm[key.strip()] = val
    
    return fm, content

def split_by_headings(text):
    """Split markdown text by ## headings, preserving heading hierarchy."""
    chunks = []
    parts = re.split(r'(?=^##\s+)', text, flags=re.MULTILINE)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        heading_match = re.match(r'^##\s+(.+)$', part, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else ""
        content = re.sub(r'^##\s+.+$', '', part, count=1, flags=re.MULTILINE).strip()
        
        if content:
            chunks.append({
                "heading": heading,
                "content": content
            })
    
    return chunks

def sliding_window_chunk(text, heading, source_path, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Create overlapping chunks from text for better search precision.

    Tokens keep their trailing whitespace and are re-joined with it, so LINE BOUNDARIES
    SURVIVE. Splitting on whitespace and joining with a single space fused a heading into the
    bullet beneath it — `### Æ, the Overseer` + `- **Æ (Artificial Educator):**` became the
    adjacency `… the Overseer Æ (Artificial Educator) …`, i.e. the index published a retired
    form the source never contained. A transformation must not invent adjacency.
    """
    text = clean_markdown(text)
    words = re.findall(r"\S+\s*", text)
    if len(words) <= chunk_size:
        return [{
            "text": "".join(words).strip(),
            "heading": heading,
            "source": source_path,
            "word_count": len(words)
        }]

    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunks.append({
            "text": "".join(chunk_words).strip(),
            "heading": heading,
            "source": source_path,
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
        return None
    
    fm, body = parse_frontmatter(content)

    # Public hold key for the site lineage: draft: true is the site's native
    # predicate (per-consumer ruling). Hugo already excludes drafts; this keeps
    # the search index and API from publishing a held page.
    if str(fm.get('draft', '')).strip().lower() == 'true':
        return None

    # Skip files with no body
    if not body.strip():
        return None
    
    # Get relative path from content dir
    rel_path = os.path.relpath(filepath, CONTENT_DIR)
    
    # Determine part/section from path
    part = os.path.dirname(rel_path).replace('\\', '/')
    if part == '.':
        part = 'root'
    
    # Build file entry
    file_entry = {
        "path": rel_path,
        "part": part,
        "title": fm.get('title', os.path.basename(rel_path).replace('.md', '').replace('_', ' ')),
        "description": fm.get('description', ''),
        "weight": int(fm.get('weight', 0)),
        "sequence": fm.get('sequence', ''),
        "status": fm.get('status', 'LIVING ARCHIVE'),
        "type": "section" if rel_path.endswith('_index.md') else "thread",
        "frontmatter": fm,
        "content": body,
        "content_hash": hashlib.md5(body.encode()).hexdigest()[:12],
        "indexed_at": datetime.now().isoformat()
    }
    
    # Build search chunks
    chunks = []
    sections = split_by_headings(body)
    
    if not sections:
        # No headings — treat entire body as one section
        chunks = sliding_window_chunk(body, "", rel_path)
    else:
        for section in sections:
            section_chunks = sliding_window_chunk(
                section["content"], 
                section["heading"], 
                rel_path
            )
            chunks.extend(section_chunks)
    
    # Add file metadata to each chunk
    for chunk in chunks:
        chunk["file_title"] = file_entry["title"]
        chunk["file_part"] = file_entry["part"]
        chunk["file_path"] = file_entry["path"]
        chunk["chunk_id"] = f"{rel_path}_{chunk.get('heading', '')[:30]}_{hashlib.md5(chunk['text'].encode()).hexdigest()[:8]}"
    
    file_entry["chunks"] = chunks
    file_entry["chunk_count"] = len(chunks)
    
    return file_entry

def main():
    """Index all markdown files in the content directory."""
    print("=== Compendium Index Generator ===")
    print(f"Source: {CONTENT_DIR}")
    print(f"Output: {OUTPUT_PATH}")
    print()
    
    content_path = Path(CONTENT_DIR)
    files = sorted(content_path.rglob("*.md"))
    
    print(f"Found {len(files)} markdown files")
    
    indexed_files = []
    all_chunks = []
    
    for filepath in files:
        filepath_str = str(filepath)
        print(f"  Indexing: {os.path.relpath(filepath_str, CONTENT_DIR)}")
        
        entry = index_file(filepath_str)
        if entry:
            indexed_files.append(entry)
            all_chunks.extend(entry["chunks"])
    
    # Build output
    output = {
        "meta": {
            "generator": "compendium-index",
            "version": "1.0",
            "total_files": len(indexed_files),
            "total_chunks": len(all_chunks),
            "indexed_at": datetime.now().isoformat(),
            "source": "PWA content/ directory"
        },
        "files": indexed_files,
        "chunks": all_chunks
    }
    
    # Write output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"=== Index Complete ===")
    print(f"Files indexed: {len(indexed_files)}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
