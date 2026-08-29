# Sovereign Deployment Guide
## Alternatives to Netlify for Compendium Site

## 🚨 Current Situation

**Netlify Credits Exhausted:**
- Free tier has AI credit limits
- Auto-optimization consumes credits even when disabled
- Deploys paused until credits reset

**Your Needs:**
- ✅ Hugo static site deployment
- ✅ Custom domain (overseer.ae)
- ✅ Zero AI credits consumption
- ✅ Sovereign, censorship-resistant hosting

---

## 🔮 Option 1: GitHub Pages (Recommended)

**What is GitHub Pages?**
- Free static site hosting by GitHub
- Built into your repository
- No AI credits, no hidden costs
- Perfect for Hugo sites

**Pros:**
- ✅ **Free forever** - No credits, no metered usage
- ✅ **Sovereign** - You control everything
- ✅ **No AI features** - Can't drain credits
- ✅ **Easy setup** - 5-minute configuration
- ✅ **Custom domain** - Supports overseer.ae
- ✅ **HTTPS included** - Free SSL certificates

**Cons:**
- ❌ No serverless functions (not needed for static site)
- ❌ No form handling (can use third-party forms)
- ❌ Manual builds (push to GitHub = auto-deploy)

**Setup Steps:**

### Step 1: Configure GitHub Repository

```bash
cd "C:\Users\Nefs\Projects\CompendiumSite"
git status
git add -A
git commit -m "feat: ready for GitHub Pages deployment"
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to GitHub: `https://github.com/Napistu69/Overseer`
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Select branch: **main**
5. Folder: **/ (root)**
6. Click **Save**

### Step 3: Configure Custom Domain

1. Go to **Settings → Pages → Custom domain**
2. Enter: `overseer.ae`
3. Click **Save**
4. **IMPORTANT:** Update DNS records

**DNS Configuration:**
- **Provider:** Your domain registrar (IONOS or provider)
- **Type:** `A` record
- **Name:** `@`
- **Value:** `185.199.108.153`
- **TTL:** `3600`

**Additional Records:**
- **Type:** `A`
- **Name:** `www`
- **Value:** `185.199.108.153`
- **TTL:** `3600`

- **Type:** `CNAME`
- **Name:** `*` (or `@`)
- **Value:** `overseer.github.io`
- **TTL:** `3600`

### Step 4: Wait for Propagation

- DNS changes take 15-60 minutes
- Test at: `https://overseer.ae`
- GitHub Pages URL: `https://Napistu69.github.io/Overseer` (temporary)

**Done!** Your site is now sovereign and credit-free.

---

## 🌐 Option 2: Cloudflare Pages

**What is Cloudflare Pages?**
- Fast edge network deployment
- Built-in CDN and security
- Free tier generous limits

**Pros:**
- ✅ **Free** - No credits
- ✅ **Global CDN** - Blazing fast worldwide
- ✅ **Zero-knowledge** - Privacy-focused
- ✅ **Custom domain** - Supports overseer.ae
- ✅ **Automatic HTTPS**
- ✅ **CI/CD from Git**

**Cons:**
- ❌ Slightly more complex DNS setup
- ❌ Cloudflare privacy policy concerns

**Setup:** Similar to GitHub Pages, via Cloudflare dashboard.

---

## 🌍 Option 3: IPFS/Arweave (Fully Decentralized)

**What is IPFS/Arweave?**
- Distributed storage network
- Pay-once (Arweave) or per-GiB (IPFS)
- Truly censorship-resistant

**Pros:**
- ✅ **Decentralized** - No single point of failure
- ✅ **Permanent** - Content can't be taken down
- ✅ **Sovereign** - You own the content

**Cons:**
- ❌ Slower loading (no CDN optimization)
- ❌ Cost (Arweave ~$150-300/year for 100MB)
- ❌ Complex setup
- ❌ No custom domain (needs gateway proxy)

**For your use case:** Best for the Compendium **content**, not the website itself.

---

## 🎯 Recommendation: GitHub Pages + Arweave Hybrid

**Architecture:**

```
GitHub Pages (overseer.ae)
├── Hugo site (fast, dynamic)
├── Custom domain
└── Zero costs

├── Arweave (optional)
├── Static assets (images, videos)
├── Permanent content
└── Pay-once storage
```

**Benefits:**
- ✅ Fast deployment (GitHub Pages)
- ✅ Zero ongoing costs
- ✅ No AI credits to drain
- ✅ Optional Arweave for heavy assets
- ✅ Sovereign control

---

## 📋 Migration Plan

### Phase 1: GitHub Pages Setup (1 hour)

1. ✅ Update `hugo.toml`:
```toml
baseURL = "https://overseer.github.io/Overseer"
```

2. ✅ Build site locally:
```bash
cd "C:\Users\Nefs\Projects\CompendiumSite"
hugo --gc --minify
```

3. ✅ Push to GitHub:
```bash
git add -A
git commit -m "feat: migrate to GitHub Pages"
git push origin main
```

4. ✅ Enable GitHub Pages in repo settings

5. ✅ Configure DNS (A records to 185.199.108.153)

6. ✅ Wait for propagation (15-60 min)

### Phase 2: Final DNS Update

1. Update domain registrar DNS:
   - Remove Netlify nameservers
   - Add GitHub Pages A records
   
2. Test custom domain

3. Verify SSL certificate

---

## 🔧 Technical Configuration

### 1. Update `hugo.toml`:

```toml
baseURL = "https://overseer.github.io/Overseer"
title = "TekTribe Chronicles"

[params]
  author = "TekTribe"
  description = "Compendium of the Collective"
```

### 2. Update `netlify.toml` (optional, for reference):

```toml
# Keep for reference, but won't be used
# Remove or comment out this file after migration

[build]
  publish = "public"
  command = "hugo --gc --minify"
```

### 3. Create `.github/workflows/deploy.yml` (optional, auto-deploy):

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: '0.164.0'
          extended: true
      
      - name: Build
        run: hugo --gc --minify
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 4. Remove Netlify config:

After successful deployment, you can delete `netlify.toml` or keep it commented out.

---

## 🚀 Quick Start Commands

```bash
# Build locally first
cd "C:\Users\Nefs\Projects\CompendiumSite"
hugo --gc --minify

# Check build
dir "C:\Users\Nefs\Projects\CompendiumSite\public"

# Push to GitHub
git add -A
git commit -m "feat: ready for GitHub Pages"
git push origin main

# Monitor deployment
# Visit: https://github.com/Napistu69/Overseer/settings/pages
```

---

## 📊 Comparison Table

| Feature | Netlify | GitHub Pages | Cloudflare Pages | IPFS/Arweave |
|---------|---------|--------------|------------------|--------------|
| Cost | ❌ Credits drain | ✅ Free | ✅ Free | 💰 ~$150/yr |
| AI Credits | ⚠️ Can drain | ❌ None | ❌ None | ❌ None |
| Custom Domain | ✅ | ✅ | ✅ | ❌ (needs proxy) |
| SSL | ✅ | ✅ | ✅ | ❌ (needs proxy) |
| CDN | ✅ | ✅ | ✅ | ⚠️ Variable |
| Speed | ✅ Fast | ✅ Fast | ✅✅ Fastest | ⚠️ Slower |
| Sovereignty | ⚠️ Centralized | ✅ Sovereign | ✅ Sovereign | ✅✅ Decentralized |
| Setup | ✅ Easy | ✅ Easy | ⚠️ Medium | ❌ Complex |

---

## 🎯 Final Recommendation

**Start with GitHub Pages:**
- ✅ Zero cost
- ✅ Zero AI credits
- ✅ Easy setup
- ✅ Full sovereignty
- ✅ Perfect for Hugo

**Later add Arweave:**
- For large media files
- Permanent content storage
- Optional redundancy

---

**Questions to consider:**
1. Do you want to migrate to GitHub Pages now?
2. Should I create the deployment workflow file?
3. Do you want to keep Netlify as backup?

---

**Date:** 2026-08-09
**Status:** Planning
**Next:** Deploy to GitHub Pages
