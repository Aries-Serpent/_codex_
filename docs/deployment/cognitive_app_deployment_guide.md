# Cognitive App Deployment Guide

**Version**: 1.0.0  
**Last Updated**: 2026-07-20  
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Build Process](#build-process)
3. [Environment Variables](#environment-variables)
4. [Node.js Requirements](#nodejs-requirements)
5. [Vite Configuration](#vite-configuration)
6. [Local Development Setup](#local-development-setup)
7. [Production Deployment](#production-deployment)
8. [Workflow Diagram](#workflow-diagram)
9. [Deployment Validation](#deployment-validation)

## Overview

The Cognitive App is a React-based frontend application built with:
- **Build Tool**: Vite (v7.3.6+)
- **Runtime**: React 19.0.0
- **Framework**: Spark (GitHub's component library)
- **Styling**: Tailwind CSS 4.1.18+
- **Deployment Target**: GitHub Pages

### Architecture
```
Source Code (src/)
    ↓
TypeScript Compilation (tsc)
    ↓
Vite Build (vite build)
    ↓
Output (dist/)
    ↓
GitHub Pages Deployment
    ↓
Live Site (/_codex_/cognitive_app/)
```

## Build Process

### Prerequisites

Before building, ensure you have:

```bash
# Check Node.js version (must be >= 22.0.0)
node --version
# Expected output: v22.x.x or higher

# Check npm version (must be >= 10.0.0)
npm --version
# Expected output: v10.x.x or higher
```

### Build Steps

#### 1. Install Dependencies

```bash
cd cognitive_app

# Clean install with lock file
npm ci

# Or with npm install if lock file needs updating
npm install
```

**Why `npm ci`**: 
- Uses exact versions from package-lock.json
- Prevents version drift between environments
- Faster and more reproducible than `npm install`

#### 2. Type Check (Optional but Recommended)

```bash
# TypeScript build check
tsc -b --noCheck

# This validates TypeScript without emitting files
# Output: Any type errors will be reported
```

**Purpose**: Early detection of TypeScript errors before build

#### 3. Build with Vite

```bash
# Development build (faster, larger output)
npm run build

# Production build (minified, optimized)
# This is what runs in CI/CD
vite build
```

**Build Output**:
```
dist/
├── index.html          # Main entry point
├── assets/
│   ├── index-*.js      # Main JavaScript bundle
│   ├── vendor-*.js     # Vendor code (React, Spark, etc.)
│   ├── index-*.css     # Compiled Tailwind styles
│   └── [other assets]
└── vite.svg            # Favicon/assets
```

#### 4. Build Artifact Size

**Expected sizes**:
- `index-*.js`: 150-200 KB (minified)
- `vendor-*.js`: 300-400 KB (minified)
- `index-*.css`: 50-100 KB (minified)
- **Total**: ~500-700 KB (compressed ~150-250 KB)

### Complete Build Command

```bash
#!/bin/bash
set -e  # Exit on any error

cd cognitive_app

# Step 1: Install dependencies
npm ci

# Step 2: Type check
tsc -b --noCheck

# Step 3: Build
vite build

# Step 4: Verify output
if [ -d "dist" ] && [ -f "dist/index.html" ]; then
    echo "✅ Build successful"
    du -sh dist/
else
    echo "❌ Build failed: dist/ not found"
    exit 1
fi
```

## Environment Variables

### Build-Time Variables

These variables are set during the build and embedded in the output:

```bash
# .env or CI/CD environment
GITHUB_ACTIONS=true          # Set automatically in GitHub Actions
VITE_BASE_PATH=/codex/       # Base path for Vite
```

### Base Path Configuration

The `base` path controls where assets are loaded from:

```javascript
// vite.config.ts
export default defineConfig({
  // In GitHub Actions: /_codex_/cognitive_app/
  // In local dev: /
  base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/',
  // ... rest of config
});
```

**Why This Matters**:
- Local development: Assets served from `/` (root)
- GitHub Pages: Assets served from `/_codex_/cognitive_app/` (subdirectory)
- Mismatch causes: 404 errors, missing stylesheets, broken images

### Runtime Environment Variables

Create `.env.local` for local development:

```bash
# cognitive_app/.env.local

# API endpoint for cognitive brain
VITE_API_URL=http://localhost:8765

# Feature flags
VITE_ENABLE_DEBUG_MODE=false
VITE_ENABLE_ANALYTICS=true

# Theme configuration
VITE_DEFAULT_THEME=system

# Feature toggles
VITE_ENABLE_ADVANCED_WIDGETS=true
```

### Variable Reference

| Variable | Type | Default | Required | Purpose |
|----------|------|---------|----------|---------|
| `GITHUB_ACTIONS` | boolean | false | No | Triggers GitHub Pages path config |
| `VITE_API_URL` | string | http://localhost:8765 | Dev only | API endpoint for cognitive brain |
| `VITE_ENABLE_DEBUG_MODE` | boolean | false | No | Enable dev tools and logging |
| `VITE_ENABLE_ANALYTICS` | boolean | true | No | Enable usage analytics |
| `VITE_DEFAULT_THEME` | string | system | No | Theme: light, dark, system |

## Node.js Requirements

### Minimum Version

- **Minimum**: Node.js 22.0.0
- **Recommended**: Node.js 22.11.0 or later
- **Not Supported**: Node.js 20.x and earlier

### Why Node 22+

- **async/await improvements**: Better performance and memory efficiency
- **TypeScript 5.7 compatibility**: Required for new language features
- **Vite 7.x support**: Built-in optimizations for newer Node versions
- **Security**: Latest security patches and vulnerability fixes

### Version Check and Installation

```bash
# Check current version
node --version

# If version < 22, upgrade using nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Load nvm
source ~/.bashrc

# Install Node 22
nvm install 22

# Set as default
nvm alias default 22

# Verify
node --version  # Should output v22.x.x
```

### Version in CI/CD

GitHub Actions workflow configuration:

```yaml
- name: Set up Node.js 22
  uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: npm
    cache-dependency-path: cognitive_app/package-lock.json
```

## Vite Configuration

### Base Configuration

The Vite configuration is in `cognitive_app/vite.config.ts`:

```typescript
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig, PluginOption } from "vite";
import sparkPlugin from "@github/spark/spark-vite-plugin";
import createIconImportProxy from "@github/spark/vitePhosphorIconProxyPlugin";
import { resolve } from 'path'

const projectRoot = process.env.PROJECT_ROOT || import.meta.dirname

export default defineConfig({
  // ⚠️ CRITICAL: Base path varies by environment
  base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/',
  
  plugins: [
    react(),
    tailwindcss(),
    // Icon proxy for Phosphor icons
    createIconImportProxy() as PluginOption,
    // Spark component library
    sparkPlugin() as PluginOption,
  ],
  
  resolve: {
    alias: {
      '@': resolve(projectRoot, 'src')
    }
  },
  
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Output report for bundle analysis
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          'vendor-react': ['react', 'react-dom'],
          'vendor-ui': ['@github/spark', '@radix-ui/react-*'],
        }
      }
    }
  },

  // Development server
  server: {
    port: 5173,
    strictPort: false,
    open: true,
  },
  
  // Preview server
  preview: {
    port: 4173,
  }
});
```

### Key Configuration Points

#### 1. Base Path (Most Critical)

```typescript
base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/',
```

**Impact**:
- Controls where Vite looks for assets
- Must match GitHub Pages deployment path
- Trailing slash is REQUIRED

**Testing Base Path**:
```bash
# Build and check the generated HTML
npm run build
grep '<script' dist/index.html | head -2
# Should show: <script type="module" src="/_codex_/cognitive_app/assets/..."></script>
```

#### 2. Plugin Configuration

| Plugin | Purpose | Critical |
|--------|---------|----------|
| `react()` | JSX/TSX compilation | ✅ Yes |
| `tailwindcss()` | Tailwind CSS compilation | ✅ Yes |
| `createIconImportProxy()` | Phosphor icon imports | ✅ Yes |
| `sparkPlugin()` | Spark component support | ✅ Yes |

#### 3. Build Optimization

```typescript
build: {
  outDir: 'dist',
  emptyOutDir: true,  // Clean dist/ before each build
  // Optional: Enable source maps for debugging
  sourcemap: process.env.NODE_ENV !== 'production' ? 'inline' : false,
}
```

## Local Development Setup

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/codex.git
cd codex

# 2. Install Node.js 22 (if not already installed)
nvm install 22
nvm use 22

# 3. Navigate to cognitive app
cd cognitive_app

# 4. Install dependencies
npm ci

# 5. Create .env.local for local development
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8765
VITE_ENABLE_DEBUG_MODE=true
VITE_DEFAULT_THEME=system
EOF

# 6. Start development server
npm run dev
```

### Development Commands

```bash
# Start Vite dev server (with hot reload)
npm run dev
# Output: Local: http://localhost:5173/
# Changes auto-refresh in browser

# Type check only (no build)
tsc -b --noCheck

# Lint code
npm run lint

# Fix lint errors
npm run lint -- --fix

# Run unit tests
npm run test

# Run unit tests in watch mode
npm run test:watch

# Run unit tests with UI
npm run test:ui

# Run E2E tests
npm run test:e2e

# Preview production build (after npm run build)
npm run preview
```

### Hot Module Replacement (HMR)

Vite automatically enables HMR in development:

```typescript
// Changes to .tsx files are reflected instantly
// No full page refresh needed
// State is preserved during reload

// Example: Changing component styles
// 1. Edit a component
// 2. Save file
// 3. Browser automatically updates
// 4. Component state preserved (if using React hooks)
```

### Debugging

#### Browser DevTools

```javascript
// Enable debug mode in .env.local
VITE_ENABLE_DEBUG_MODE=true

// In console:
window.__DEBUG__ = true
window.__DEBUG_LEVEL__ = 'verbose'
```

#### TypeScript Errors

```bash
# Full type check
npm run lint

# Watch for TypeScript errors
tsc --watch

# Compile with detailed output
tsc -b --listFilesOnly
```

## Production Deployment

### Automated Deployment (GitHub Actions)

The `pages-mkdocs.yml` workflow handles automatic deployment:

```yaml
- name: Set up Node.js 22
  uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: npm
    cache-dependency-path: cognitive_app/package-lock.json

- name: Build Cognitive App
  run: |
    cd cognitive_app
    npm ci
    npm run build
```

### Manual Deployment

If manual deployment is needed:

```bash
# 1. Build the app
cd cognitive_app
npm ci
npm run build

# 2. Copy built files to GitHub Pages source
# GitHub Pages path: /_codex_/cognitive_app/
mkdir -p ../public/_codex_/cognitive_app/
cp -r dist/* ../public/_codex_/cognitive_app/

# 3. Commit and push
git add public/
git commit -m "Deploy cognitive app build $(date +%Y-%m-%d)"
git push origin main
```

### Production Deployment Checklist

- [ ] Node.js version is 22.0.0 or higher
- [ ] All dependencies installed with `npm ci`
- [ ] TypeScript types checked: `tsc -b --noCheck`
- [ ] Build successful: `npm run build`
- [ ] `dist/index.html` exists
- [ ] Asset files generated in `dist/assets/`
- [ ] Bundle size within limits (~700 KB uncompressed)
- [ ] Base path set to `/_codex_/cognitive_app/`
- [ ] No hardcoded absolute paths in code
- [ ] Environment variables configured correctly
- [ ] API endpoints point to production servers
- [ ] CDN cache headers properly set

### Performance Optimization

```bash
# Analyze bundle size
npm run build -- --report

# Expected output shows:
# - Main bundle: ~200 KB
# - Vendor bundle: ~400 KB
# - CSS: ~100 KB
# - Total: ~700 KB (before gzip)
# - Gzipped: ~200-250 KB
```

## Workflow Diagram

```
┌─────────────────────────────────────────┐
│  Developer commits to main branch        │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  GitHub Actions: pages-mkdocs workflow  │
│  - Checkout code                        │
│  - Setup Node.js 22                     │
│  - Setup Python 3.12                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Build Steps                             │
│  1. npm ci (install dependencies)       │
│  2. tsc -b --noCheck (type check)       │
│  3. npm run build (vite build)          │
│  4. Verify dist/ exists                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  MkDocs Documentation Build              │
│  - Install mkdocs-material               │
│  - Generate API docs                    │
│  - Build site/                          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Deploy to GitHub Pages                  │
│  - Upload to gh-pages branch            │
│  - Available at: codex.github.io        │
│  - Cognitive app at: /_codex_/cognitive │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  ✅ Deployment Complete                  │
│  Live at: https://codex.github.io/...   │
└─────────────────────────────────────────┘
```

## Deployment Validation

### Post-Deployment Checks

```bash
#!/bin/bash
# Script to validate deployment

SITE_URL="https://aries-serpent.github.io"
APP_PATH="/_codex_/cognitive_app"

echo "🔍 Validating deployment..."

# 1. Check index.html exists
echo "1. Checking index.html..."
if curl -s "$SITE_URL$APP_PATH/index.html" | grep -q "React"; then
    echo "   ✅ index.html is accessible"
else
    echo "   ❌ index.html not found or invalid"
    exit 1
fi

# 2. Check main bundle loads
echo "2. Checking JavaScript bundles..."
if curl -s "$SITE_URL$APP_PATH/assets/" | grep -q ".js"; then
    echo "   ✅ JavaScript bundles are present"
else
    echo "   ❌ JavaScript bundles missing"
    exit 1
fi

# 3. Check CSS loads
echo "3. Checking CSS stylesheets..."
if curl -s "$SITE_URL$APP_PATH/index.html" | grep -q "css"; then
    echo "   ✅ CSS is linked"
else
    echo "   ❌ CSS links missing"
    exit 1
fi

# 4. Check response headers
echo "4. Checking HTTP headers..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL$APP_PATH/index.html")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ HTTP 200 OK"
else
    echo "   ❌ HTTP $HTTP_CODE (expected 200)"
    exit 1
fi

echo ""
echo "✅ Deployment validation successful!"
```

### Manual Verification Checklist

1. **Visual Verification**
   - [ ] Site loads without errors in browser
   - [ ] No 404 errors in browser console
   - [ ] No network errors in DevTools
   - [ ] Styles load correctly (no unstyled content flash)

2. **Functional Verification**
   - [ ] Navigation works
   - [ ] Widgets render correctly
   - [ ] API calls succeed (check Network tab)
   - [ ] Forms submit successfully

3. **Performance Verification**
   - [ ] Page load time < 3 seconds
   - [ ] Lighthouse score > 80
   - [ ] Network requests < 2 MB total

4. **Browser Compatibility**
   - [ ] Chrome/Edge: Latest version
   - [ ] Firefox: Latest version
   - [ ] Safari: Latest version (12+)

## Troubleshooting

### Common Issues

#### Issue: "Cannot find dist directory after build"
**Solution**:
```bash
# 1. Check Node version
node --version  # Must be >= 22.0.0

# 2. Clean and rebuild
rm -rf node_modules package-lock.json
npm ci
npm run build

# 3. Check for errors in output
# If build fails silently, run with verbose output
npm run build -- --logLevel=debug
```

#### Issue: "404 error on deployed site"
**Solution**:
```bash
# 1. Check base path in vite.config.ts
grep "base:" cognitive_app/vite.config.ts

# 2. Verify build process set GITHUB_ACTIONS environment
echo $GITHUB_ACTIONS  # Should output 'true' in CI/CD

# 3. Rebuild with correct environment
GITHUB_ACTIONS=true npm run build
```

#### Issue: "Styles not loading on GitHub Pages"
**Solution**:
```bash
# 1. Check index.html has correct CSS paths
grep -o 'href="[^"]*css' dist/index.html

# 2. Ensure CSS files exist
ls -la dist/assets/*.css

# 3. Verify server headers allow CSS (usually not an issue with GitHub Pages)
# Contact GitHub Support if issue persists
```

## Reference Links

- [Vite Documentation](https://vite.dev/)
- [React 19 Migration Guide](https://react.dev/blog/2024/12/05/react-19)
- [Tailwind CSS 4 Docs](https://tailwindcss.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Spark Component Library](https://github.com/github/spark)

---

**Last Updated**: 2026-07-20  
**Maintainer**: DevOps Team  
**Status**: Production Ready
