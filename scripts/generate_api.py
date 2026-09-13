#!/usr/bin/env python3
"""
Compendium API Generator
Generates static API endpoints for bot scraping:
- /api/compendium/manifest.json — file listing with metadata
- /api/compendium/files/{path}.json — individual file with content + frontmatter
- /api/compendium/index.json — search index (alias to compendium-index.json)
"""

import os
import re
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

CONTENT_DIR = r"C:\Users\Nefs\Projects\CompendiumPWA\content"
STATIC_DIR = r"C:\Users\Nefs\Projects\CompendiumPWA\static"
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
        "api_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "total_files": 0,
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
        file_meta = {
            "path": rel_path,
            "part": part,
            "title": fm.get('title', os.path.basename(rel_path).replace('.md', '').replace('_', ' ')),
            "description": fm.get('description', ''),
            "type": "section" if rel_path.endswith('_index.md') else "thread",
            "frontmatter": fm,
            "content_hash": hashlib.md5(body.encode()).hexdigest()[:12],
            "size_bytes": len(raw_content.encode('utf-8')),
            "url": f"/api/compendium/files/{rel_path.replace('/', '_').replace('.md', '')}.json"
        }
        manifest["files"].append(file_meta)
        
        # Individual file API endpoint
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
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Write individual file JSON
        api_filename = rel_path.replace('/', '_').replace('.md', '') + '.json'
        api_path = os.path.join(API_DIR, api_filename)
        with open(api_path, 'w', encoding='utf-8') as f:
            json.dump(file_api, f, ensure_ascii=False, indent=2)
    
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
    print(f"Total size: {sum(os.path.getsize(os.path.join(API_DIR, f)) for f in os.listdir(API_DIR)) / 1024:.1f} KB")
    print()
    print("Endpoints:")
    print(f"  GET /api/compendium/manifest.json — file listing")
    print(f"  GET /api/compendium/index.json — search index")
    print(f"  GET /api/compendium/files/{{file_id}}.json — individual file")

if __name__ == "__main__":
    generate_api()
