#!/usr/bin/env python3
"""Generate versioned service worker with full URL list for offline caching."""
import os
import json
from datetime import datetime

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
SW_TEMPLATE = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'sw.js')
SW_OUTPUT = os.path.join(os.path.join(os.path.dirname(__file__), '..', 'public', 'js', 'sw.js'))

# File extensions to cache
CACHE_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json', '.ttf', '.woff', '.woff2', '.eot', '.ico'}

def find_cacheable_files():
    """Find all files in public/ that should be cached."""
    urls = []
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in CACHE_EXTENSIONS:
                full_path = os.path.join(root, f)
                # Convert to URL path
                rel_path = os.path.relpath(full_path, PUBLIC_DIR)
                if rel_path == 'index.html':
                    url = '/'
                else:
                    url = '/' + rel_path.replace('\\', '/')
                urls.append(url)
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
    sw_content = template.replace('{{VERSION}}', f'tektribe-v{timestamp}')
    sw_content = sw_content.replace('{{PRECACHE_URLS}}', url_list)
    
    # Write output
    with open(SW_OUTPUT, 'w') as f:
        f.write(sw_content)
    
    print(f"Generated service worker with {len(urls)} precached URLs")
    print(f"Cache version: tektribe-v{timestamp}")
    print(f"Output: {SW_OUTPUT}")

if __name__ == '__main__':
    generate_sw()
