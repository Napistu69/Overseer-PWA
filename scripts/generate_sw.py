#!/usr/bin/env python3
"""Generate versioned service worker with full URL list for offline caching."""
import os
from datetime import datetime
from urllib.parse import quote

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
SW_TEMPLATE = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'sw.js')
SW_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'sw.js')

# Max file size to precache (1 MB)
MAX_PRECACHE_SIZE = 1 * 1024 * 1024

# Files to skip (search indices)
SKIP_FILES = {'akashic-index.json', 'chroma-index.json', 'compendium-index.json'}


def url_to_path(url_path):
    """Convert a URL path back to a file path for checking existence."""
    # Reverse the conversion: /part1/the_continuum/ -> part1/the_continuum/index.html
    if url_path == '/':
        return 'index.html'
    if url_path.endswith('/'):
        return url_path.strip('/') + '/index.html'
    return url_path.lstrip('/')


def find_cacheable_files():
    """Find all files in public/ that should be cached."""
    urls = []
    seen = set()
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for f in files:
            if f in SKIP_FILES:
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in {'.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ttf', '.woff', '.woff2', '.eot', '.ico'}:
                continue

            full_path = os.path.join(root, f)
            sz = os.path.getsize(full_path)
            if sz > MAX_PRECACHE_SIZE:
                print(f'  SKIP (too large, {sz/1024/1024:.1f} MB): {f}')
                continue

            rel_path = os.path.relpath(full_path, PUBLIC_DIR).replace('\\', '/')

            # Convert file path to URL path
            if rel_path == 'index.html':
                url = '/'
            elif rel_path.endswith('/index.html'):
                url = '/' + rel_path.replace('/index.html', '/')
            else:
                url = '/' + rel_path

            # URL-encode special characters (spaces, quotes, etc.)
            # This ensures valid JS string literals in the SW
            url = quote(url, safe='/')

            if url not in seen:
                seen.add(url)
                urls.append(url)

    return sorted(urls)


def generate_sw():
    """Generate the service worker with all URLs precached."""
    with open(SW_TEMPLATE, 'r') as f:
        template = f.read()

    urls = find_cacheable_files()
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    url_list = ', '.join(f"'{url}'" for url in urls)

    sw_content = template.replace('{{VERSION}}', timestamp)
    sw_content = sw_content.replace('{{PRECACHE_URLS}}', url_list)

    with open(SW_OUTPUT, 'w') as f:
        f.write(sw_content)

    print(f'Generated service worker with {len(urls)} precached URLs')
    print(f'Cache version: tektribe-v{timestamp}')
    print(f'Output: {SW_OUTPUT}')


if __name__ == '__main__':
    generate_sw()
