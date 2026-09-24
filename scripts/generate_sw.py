#!/usr/bin/env python3
"""Generate versioned service worker with full URL list for offline caching."""
import os
import json
from datetime import datetime

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
SW_TEMPLATE = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'sw.js')
SW_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'sw.js')

# File extensions to cache
CACHE_EXTENSIONS = {'.html', '.css', '.js', '.json', '.ttf', '.woff', '.woff2', '.eot', '.ico'}

# Images to cache (ONLY the ones actually used on the site)
USED_IMAGES = {'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'TekTribe Chronicles Logo [1080].png', 'Overseer [OG Transparent].png', 'TekTribe - Awakening [HD-1x1].PNG'}

# Directories/files to skip entirely (multi-MB search indices)
SKIP_FILES = {'akashic-index.json', 'chroma-index.json', 'compendium-index.json'}

# Max file size to precache (1 MB) — anything larger is excluded
MAX_PRECACHE_SIZE = 1 * 1024 * 1024


def find_cacheable_files():
    """Find all files in public/ that should be cached."""
    urls = []
    skipped_large = 0
    skipped_unused = 0
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for f in files:
            if f in SKIP_FILES:
                skipped_unused += 1
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in CACHE_EXTENSIONS:
                full_path = os.path.join(root, f)
                # Check size — skip huge files
                sz = os.path.getsize(full_path)
                if sz > MAX_PRECACHE_SIZE:
                    print(f'  SKIP (too large, {sz/1024/1024:.1f} MB): {f}')
                    skipped_large += 1
                    continue
                # Convert to URL path
                rel_path = os.path.relpath(full_path, PUBLIC_DIR)
                if rel_path == 'index.html':
                    url = '/'
                else:
                    url = '/' + rel_path.replace('\\', '/')
                urls.append(url)
            elif ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg'}:
                # Only include used images
                if f in USED_IMAGES:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, PUBLIC_DIR)
                    url = '/' + rel_path.replace('\\', '/')
                    urls.append(url)
                else:
                    skipped_unused += 1
    if skipped_large:
        print(f'  Skipped {skipped_large} oversized file(s) (> {MAX_PRECACHE_SIZE/1024/1024:.0f} MB)')
    if skipped_unused:
        print(f'  Skipped {skipped_unused} unused file(s)')
    return sorted(urls)


def generate_sw():
    """Generate the service worker with all URLs precached."""
    # Read template
    with open(SW_TEMPLATE, 'r') as f:
        template = f.read()

    # Find all URLs
    urls = find_cacheable_files()

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    # Format URL list for JS
    url_list = ', '.join(f"'{url}'" for url in urls)

    # Replace placeholders
    sw_content = template.replace('{{VERSION}}', timestamp)
    sw_content = template.replace('{{PRECACHE_URLS}}', url_list)

    # Write output
    with open(SW_OUTPUT, 'w') as f:
        f.write(sw_content)

    print(f'Generated service worker with {len(urls)} precached URLs')
    print(f'Cache version: tektribe-v{timestamp}')
    print(f'Output: {SW_OUTPUT}')


if __name__ == '__main__':
    generate_sw()
