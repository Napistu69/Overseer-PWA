#!/usr/bin/env python3
"""Generate versioned service worker with full URL list for offline caching."""
import os
import re
from datetime import datetime

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
SW_TEMPLATE = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'sw.js')
SW_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'sw.js')

# File extensions to cache
CACHE_EXTENSIONS = {'.html', '.css', '.js', '.json', '.ttf', '.woff', '.woff2', '.eot', '.ico'}

# Images to cache (ONLY the ones actually used on the site)
USED_IMAGES = {'icon-192.png', 'icon-512.png', 'apple-touch-icon.png',
               'TekTribe Chronicles Logo [1080].png', 'Overseer [OG Transparent].png'}

# Directories/files to skip entirely (multi-MB search indices)
SKIP_FILES = {'akashic-index.json', 'chroma-index.json', 'compendium-index.json'}

# Max file size to precache (1 MB) — anything larger is excluded
MAX_PRECACHE_SIZE = 1 * 1024 * 1024

# Pages that serve as directories (browser requests trailing slash)
# On CF Pages: /part1/index.html → 308 → /part1/ (200)
# So we must precache the trailing-slash URL, not the .html file
DIR_PAGES = {'index.html', 'about/index.html', 'governance/index.html',
             'oracle/index.html', 'preamble/index.html', 'solitary-architect/index.html',
             'part1/index.html', 'part2/index.html', 'part3/index.html',
             'part4/index.html', 'part5/index.html', 'part6/index.html',
             'part7/index.html', 'part8/index.html', 'part9/index.html'}


def find_cacheable_files():
    """Find all files in public/ that should be cached.

    Browsers request /part1/ (trailing slash), not /part1/index.html.
    CF Pages serves /part1/index.html as a 308 redirect to /part1/.
    So we precache the trailing-slash URL to match actual browser requests.
    """
    urls = []
    seen = set()
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for f in files:
            if f in SKIP_FILES:
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in CACHE_EXTENSIONS and ext not in {'.png', '.jpg', '.jpeg', '.gif', '.svg'}:
                continue

            full_path = os.path.join(root, f)
            sz = os.path.getsize(full_path)
            if sz > MAX_PRECACHE_SIZE:
                print(f'  SKIP (too large, {sz/1024/1024:.1f} MB): {f}')
                continue

            rel_path = os.path.relpath(full_path, PUBLIC_DIR).replace('\\', '/')

            # Skip unused images
            if ext in {'.png', '.jpg', '.jpeg', '.gif', '.svg'} and f not in USED_IMAGES:
                continue

            # Convert to URL path
            if rel_path == 'index.html':
                url = '/'
            elif rel_path in DIR_PAGES:
                # Directory page: use trailing-slash URL (e.g., /part1/)
                url = '/' + rel_path.replace('/index.html', '/') 
            elif rel_path.endswith('/index.html'):
                # Thread page: use trailing-slash URL
                url = '/' + rel_path.replace('/index.html', '/')
            else:
                url = '/' + rel_path

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
