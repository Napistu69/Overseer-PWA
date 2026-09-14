#!/usr/bin/env python3
"""
Compendium API Generator
Generates static API endpoints for bot scraping:
- /api/compendium/manifest.json — file listing with metadata
- /api/compendium/files/{path}.json — individual file with content + frontmatter
- /api/compendium/files/{path}.md — raw markdown (content negotiation)
- /api/compendium/index.json — search index (alias to compendium-index.json)
"""

import os
import re
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

# Configuration — derive paths from script location for cross-platform compat
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(SCRIPT_DIR)
CONTENT_DIR = os.path.join(SITE_DIR, "content")
STATIC_DIR = os.path.join(SITE_DIR, "static")
API_DIR = os.path.join(STATIC_DIR, "api", "compendium")

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

def generate_api():
    """Generate static API endpoints for bot scraping."""
    print("=== Compendium API Generator ===")
    
    # Clean and create API directory
    if os.path.exists(API_DIR):
        shutil.rmtree(API_DIR)
    os.makedirs(API_DIR, exist_ok=True)
    
    content_path = Path(CONTENT_DIR)
    files = sorted(content_path.rglob("*.md"))
    
    print(f"Processing {len(files)} files...")
    
    manifest = {
        "api_version": "1.1",
        "generated_at": datetime.now().isoformat(),
        "total_files": 0,
        "content_negotiation": {
            "json": "/api/compendium/files/{file_id}.json",
            "markdown": "/api/compendium/files/{file_id}.md",
            "note": "Append .md extension for raw markdown, .json for structured data"
        },
        "files": []
    }
    
    for filepath in files:
        filepath_str = str(filepath)
        rel_path = os.path.relpath(filepath_str, CONTENT_DIR).replace('\\', '/')
        
        print(f"  Processing: {rel_path}")
        
        try:
            with open(filepath_str, 'r', encoding='utf-8') as f:
                raw_content = f.read()
        except Exception as e:
            print(f"    Warning: Could not read: {e}")
            continue
        
        fm, body = parse_frontmatter(raw_content)
        
        # Determine part/section from path
        part = os.path.dirname(rel_path).replace('\\', '/')
        if part == '.':
            part = 'root'
        
        # File metadata for manifest
        file_id = rel_path.replace('/', '_').replace('.md', '')
        file_meta = {
            "path": rel_path,
            "part": part,
            "title": fm.get('title', os.path.basename(rel_path).replace('.md', '').replace('_', ' ')),
            "description": fm.get('description', ''),
            "type": "section" if rel_path.endswith('_index.md') else "thread",
            "frontmatter": fm,
            "content_hash": hashlib.md5(body.encode()).hexdigest()[:12],
            "size_bytes": len(raw_content.encode('utf-8')),
            "endpoints": {
                "json": f"/api/compendium/files/{file_id}.json",
                "markdown": f"/api/compendium/files/{file_id}.md"
            }
        }
        manifest["files"].append(file_meta)
        
        # Individual file API endpoint (JSON)
        file_api = {
            "path": rel_path,
            "part": part,
            "title": file_meta["title"],
            "description": file_meta["description"],
            "type": file_meta["type"],
            "frontmatter": fm,
            "content": body,
            "raw_markdown": raw_content,
            "metadata": {
                "content_hash": file_meta["content_hash"],
                "size_bytes": file_meta["size_bytes"],
                "generated_at": datetime.now().isoformat(),
                "content_negotiation": {
                    "markdown_url": f"/api/compendium/files/{file_id}.md",
                    "json_url": f"/api/compendium/files/{file_id}.json"
                }
            }
        }
        
        # Write individual file JSON
        api_filename = file_id + '.json'
        api_path = os.path.join(API_DIR, api_filename)
        with open(api_path, 'w', encoding='utf-8') as f:
            json.dump(file_api, f, ensure_ascii=False, indent=2)
        
        # Write raw markdown file for content negotiation
        md_filename = file_id + '.md'
        md_path = os.path.join(API_DIR, md_filename)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
    
    manifest["total_files"] = len(manifest["files"])
    
    # Write manifest
    manifest_path = os.path.join(API_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    # Copy search index as index.json
    index_src = os.path.join(STATIC_DIR, "compendium-index.json")
    index_dst = os.path.join(API_DIR, "index.json")
    if os.path.exists(index_src):
        shutil.copy2(index_src, index_dst)
        print(f"  Copied search index to {index_dst}")
    
    # Print summary
    print()
    print(f"=== API Generation Complete ===")
    print(f"Total files: {manifest['total_files']}")
    print(f"Manifest: {manifest_path}")
    print(f"API directory: {API_DIR}")
    total_size = sum(os.path.getsize(os.path.join(API_DIR, f)) for f in os.listdir(API_DIR))
    print(f"Total size: {total_size / 1024:.1f} KB")
    print()
    print("Endpoints:")
    print(f"  GET /api/compendium/manifest.json — file listing")
    print(f"  GET /api/compendium/index.json — search index")
    print(f"  GET /api/compendium/files/{{file_id}}.json — structured data + raw markdown")
    print(f"  GET /api/compendium/files/{{file_id}}.md — raw markdown with frontmatter")
    print()
    print("Content negotiation:")
    print("  JSON:    curl https://overseer.ae/api/compendium/files/part1__index.json")
    print("  Markdown: curl https://overseer.ae/api/compendium/files/part1__index.md")

if __name__ == "__main__":
    generate_api()
