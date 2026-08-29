#!/usr/bin/env bash
# Compendium Deployment to IPFS/Arweave
# Sovereign, decentralized hosting

set -e

SITE_DIR="C:/Users/Nefs/Projects/CompendiumSite"
PUBLIC_DIR="$SITE_DIR/public"

echo "=== SOVEREIGN DEPLOYMENT TO IPFS/ARWEAVE ==="
echo ""

# Build site first
echo "1. Building site..."
cd "$SITE_DIR"
hugo --gc --minify
echo "   ✓ Site built"
echo ""

# Check build
if [ ! -d "$PUBLIC_DIR" ]; then
    echo "   ❌ Build failed - public/ directory not found"
    exit 1
fi

# Count files
FILE_COUNT=$(find "$PUBLIC_DIR" -type f | wc -l)
echo "2. Files to deploy: $FILE_COUNT"
echo ""

# Deploy to IPFS
echo "3. Deploying to IPFS..."
echo "   (Install IPFS first: npm install -g ipfs)"
echo "   (Or use IPFS Desktop app)"

# Try to upload
if command -v ipfs &> /dev/null; then
    echo "   Uploading to IPFS..."
    ipfs add -r "$PUBLIC_DIR"
    echo ""
    echo "   IPFS Hash will appear above"
else
    echo "   ⚠ IPFS not installed"
    echo "   Install via: npm install -g ipfs"
    echo "   Or download from: https://dist.ipfs.tech/ipfs-desktop/"
fi
echo ""

# Deploy to Arweave
echo "4. Deploying to Arweave..."
echo "   (Install Arweave CLI first)"
echo "   (https://arweave.app/)"

if command -v ar &> /dev/null; then
    echo "   Uploading to Arweave..."
    ar upload -t "$PUBLIC_DIR"
    echo ""
    echo "   Arweave Transaction ID will appear above"
else
    echo "   ⚠ Arweave CLI not installed"
    echo "   Install via: npm install -g arweave-init-auth arweave-cli"
fi
echo ""

echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "Next steps:"
echo "1. Copy your IPFS hash or Arweave TX ID"
echo "2. Add custom domain via DNS:"
echo "   - Type: CNAME"
echo "   - Name: @"
echo "   - Value: your-hash.ipfs.dweb.link (IPFS)"
echo "   - Value: your-tx.arweave.net (Arweave)"
echo "   - TTL: 3600"
echo "3. Test at your custom domain"
