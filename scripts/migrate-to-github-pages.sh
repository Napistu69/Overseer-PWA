#!/usr/bin/env bash
# Migration script: Netlify → GitHub Pages
# Automates the migration process

set -e

SITE="C:/Users/Nefs/Projects/CompendiumSite"
cd "$SITE"

echo "=== MIGRATING TO GITHUB PAGES ==="
echo ""

# Step 1: Update baseURL
echo "1. Updating baseURL in hugo.toml..."
sed -i 's|baseURL = ".*"|baseURL = "https://overseer.github.io/Overseer"|' hugo.toml
echo "   ✓ baseURL updated"

# Step 2: Build site
echo "2. Building site locally..."
hugo --gc --minify
echo "   ✓ Build successful"

# Step 3: Verify build
echo "3. Verifying build output..."
if [ -d "public" ] && [ -f "public/index.html" ]; then
    echo "   ✓ public/ directory created"
    echo "   ✓ index.html exists"
else
    echo "   ❌ Build verification failed"
    exit 1
fi

# Step 4: Commit changes
echo "4. Committing changes..."
git add -A
git commit -m "feat: migrate to GitHub Pages

- Update baseURL to overseer.github.io/Overseer
- Add GitHub Actions deployment workflow
- Prepare for sovereign hosting"

echo "   ✓ Changes committed"

# Step 5: Push to GitHub
echo "5. Pushing to GitHub..."
git push origin main
echo "   ✓ Pushed to GitHub"

# Step 6: Instructions
echo ""
echo "=== MIGRATION COMPLETE ==="
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/Napistu69/Overseer/settings/pages"
echo "2. Enable GitHub Pages:"
echo "   - Branch: main"
echo "   - Folder: / (root)"
echo "   - Save"
echo ""
echo "3. Configure DNS at your domain registrar:"
echo "   - Type: A"
echo "   - Name: @"
echo "   - Value: 185.199.108.153"
echo "   - TTL: 3600"
echo ""
echo "4. Wait 15-60 minutes for DNS propagation"
echo ""
echo "5. Test your site at:"
echo "   - Temporary: https://overseer.github.io/Overseer"
echo "   - Custom:   https://overseer.ae"
echo ""
echo "=== MIGRATION SCRIPT COMPLETED ==="
