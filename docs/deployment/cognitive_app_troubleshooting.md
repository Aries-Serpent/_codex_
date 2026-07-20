# Cognitive App Troubleshooting Runbook

**Version**: 1.0.0  
**Last Updated**: 2026-07-20  
**Status**: Production Ready

## Quick Reference

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| App not loading | dist/ not deployed | Check GitHub Pages build logs |
| Widgets not rendering | React root div missing | Verify index.html has `<div id="root">` |
| 404 errors | Incorrect base path | Check GITHUB_ACTIONS env var in build |
| Build failures | Node version mismatch | Upgrade to Node.js 22+ |
| API issues | Missing env variables | Set VITE_API_URL in build |
| Blank page | CSS not loading | Verify base path in vite.config.ts |

## Problem: "Cognitive App Not Loading"

### Symptoms
- Site shows blank page
- Browser console shows "Failed to fetch" or "Module not found"
- Entire site (including MkDocs) returns 404

### Diagnostic Steps

#### Step 1: Check GitHub Pages Status
```bash
# 1. Verify workflow succeeded
gh workflow view pages-mkdocs.yml --json status

# Expected output: "status": "completed"

# 2. Check latest workflow run
gh run list --workflow pages-mkdocs.yml --limit 1

# Expected: "✓" status, not "✗"

# 3. Get detailed logs
gh run view <RUN_ID> --log | grep -A 5 "Build"

# Should show: "✅ Build successful" or similar
```

#### Step 2: Check Deployment Status
```bash
# 1. Verify files exist in gh-pages branch
git ls-remote origin gh-pages | head -5

# 2. Check if cognitive_app directory exists
git show origin/gh-pages:_codex_/cognitive_app/index.html | head -20

# Expected: Should show HTML with <div id="root"></div>

# 3. If not found, re-run workflow
gh workflow run pages-mkdocs.yml
```

#### Step 3: Verify Site Configuration
```bash
# 1. Check GitHub Pages settings
gh repo view --json repositoryTopics

# 2. Verify branch is set to gh-pages
gh repo view | grep -i pages

# Expected: "Branch: gh-pages" or "Branch: main (docs folder)"

# 3. Check if custom domain is configured
gh api repos/{owner}/{repo}/pages | jq '.custom_domain'
```

### Resolution Steps

**For build failure**:
```bash
# 1. Check workflow logs for errors
gh run view <RUN_ID> --log | tail -100

# 2. Common errors:
# - "Cannot find Node.js 22" → Update setup-node version
# - "npm ci failed" → Check package-lock.json for corruption
# - "vite build failed" → Check for TypeScript errors

# 3. Manual rebuild
git log --oneline -1  # Note the commit
git push origin main --force  # Trigger workflow again

# 4. If manual fix needed:
cd cognitive_app
npm ci
npm run build
# Check dist/ directory exists and has index.html
```

**For file location issue**:
```bash
# 1. Verify deployment script is copying files correctly
# In workflow: cognitive_app/dist/* should go to public/_codex_/cognitive_app/

# 2. Check file structure
git show origin/gh-pages:_codex_/cognitive_app/index.html | head -1

# Should show: <!doctype html> or <!DOCTYPE html>

# 3. If wrong location, manually deploy:
# Add to workflow or run locally:
cp -r cognitive_app/dist/* /path/to/pages/_codex_/cognitive_app/
git add .
git commit -m "Deploy cognitive app"
git push
```

### Prevention

- ✅ Enable branch protection for main
- ✅ Require workflow checks to pass before merge
- ✅ Monitor workflow status in CI dashboard
- ✅ Set up alerts for failed deployments

---

## Problem: "Widgets Not Rendering"

### Symptoms
- App loads but React components show as blank
- Console shows React warnings/errors
- JavaScript execution errors in DevTools

### Diagnostic Steps

#### Step 1: Check React Root Element
```bash
# 1. Open browser DevTools → Inspector
# 2. Look for: <div id="root"></div>
# 3. Check if it has content under it

# If missing, check index.html:
curl https://site.github.io/_codex_/cognitive_app/index.html | grep 'id="root"'

# Expected output:
# <div id="root"></div>
# <script type="module" src="/_codex_/cognitive_app/assets/..."></script>
```

#### Step 2: Check JavaScript Bundle
```bash
# 1. DevTools → Network tab
# 2. Filter by: JS
# 3. Check for errors (red entries)
# 4. Verify bundle loads: /_codex_/cognitive_app/assets/index-*.js

# If 404, likely base path issue

# 2. Manual check:
curl -s 'https://site.github.io/_codex_/cognitive_app/assets/' \
  | grep -o '.js"' | wc -l

# Should return: 2+ (main bundle + vendor bundle)
```

#### Step 3: Check React Errors
```javascript
// In browser console:
console.log(window.__REACT_DEVTOOLS_GLOBAL_HOOK__)  // Should be object

// Check for errors
// Look for red text in console, typically:
// - "Cannot find module..."
// - "Unexpected token"
// - "is not a function"
```

### Common Causes and Solutions

**Cause 1: Base Path Mismatch**
```bash
# In vite.config.ts:
base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/',

# Solution:
# 1. Verify GITHUB_ACTIONS=true in build environment
# 2. Check built HTML:
grep 'src="/' dist/index.html | head -3

# Should show: src="/_codex_/cognitive_app/assets/..."
# NOT: src="/assets/..."
```

**Cause 2: React Root Div Missing**
```html
<!-- Expected in index.html: -->
<div id="root"></div>

<!-- Check with: -->
grep 'id="root"' index.html

<!-- If missing, update index.html:
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
```

**Cause 3: JavaScript Bundle Loading**
```javascript
// In console:
// 1. Check if main script loaded
fetch('/_codex_/cognitive_app/assets/index-abc123.js')
  .then(r => r.text())
  .then(t => console.log(t.substring(0, 100)))

// 2. If 404, base path is wrong
// 3. If loads, check for runtime errors in console
```

**Cause 4: Missing Dependencies**
```bash
# Ensure all dependencies installed correctly:
cd cognitive_app

# Check for missing packages
npm ls 2>&1 | grep "missing\|deduped"

# Reinstall if needed
rm -rf node_modules package-lock.json
npm ci
npm run build
```

### Resolution Process

```bash
# Step 1: Verify build configuration
cat cognitive_app/vite.config.ts | grep "base:"

# Step 2: Rebuild with debug output
cd cognitive_app
npm ci
npm run build -- --logLevel=debug 2>&1 | tee build.log

# Step 3: Check output
grep -i "error\|warn" build.log

# Step 4: Redeploy
git add .
git commit -m "Rebuild cognitive app"
git push origin main

# Step 5: Wait for workflow to complete
sleep 60
# Check status
gh run view <RUN_ID> --json status
```

### Prevention

- ✅ Test build locally before pushing: `npm run build && npm run preview`
- ✅ Validate base path in every build: `grep 'base:' vite.config.ts`
- ✅ Use `npm ci` not `npm install` for reproducibility
- ✅ Run TypeScript check: `tsc -b --noCheck`
- ✅ Set up E2E tests to verify widgets render

---

## Problem: "404 Errors for API/Resources"

### Symptoms
- Network tab shows failed requests
- URLs look like: `GET /assets/file-abc123.js 404`
- Resources fail to load but paths look correct

### Diagnostic Steps

#### Step 1: Examine Network Requests
```javascript
// In browser DevTools → Network tab:
// 1. Right-click on failed request
// 2. Copy full URL
// 3. Check for patterns:

// ❌ WRONG: http://site.github.io/assets/index-abc123.js
// ✅ RIGHT: http://site.github.io/_codex_/cognitive_app/assets/index-abc123.js

// 4. Check request headers
// Request URL should include base path
```

#### Step 2: Verify Base Path Configuration
```bash
# 1. Check GitHub Actions environment
# In workflow: pages-mkdocs.yml
grep "GITHUB_ACTIONS\|base" .github/workflows/pages-mkdocs.yml

# Should show:
# - GITHUB_ACTIONS=true (set by GitHub automatically)
# - base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/'

# 2. Verify in built HTML
grep -o 'href="[^"]*\|src="[^"]*"' dist/index.html \
  | grep -v 'http' | head -10

# All relative paths should start with: /_codex_/cognitive_app/
```

#### Step 3: Check GitHub Pages Deployment Structure
```bash
# View deployed file structure
git ls-tree origin/gh-pages -r --name-only | grep cognitive_app | head -20

# Should show:
# _codex_/cognitive_app/index.html
# _codex_/cognitive_app/assets/index-*.js
# _codex_/cognitive_app/assets/index-*.css
```

### Resolution Steps

**Solution 1: Fix Base Path in Build**
```bash
cd cognitive_app

# Option A: Set environment variable
export GITHUB_ACTIONS=true
npm run build

# Option B: Modify vite.config.ts temporarily for testing
# Change: base: '/_codex_/cognitive_app/'

# Verify output
grep 'src="/_codex_' dist/index.html | head -2

# Should show base path in all asset URLs
```

**Solution 2: Deploy to Correct Location**
```bash
# Ensure workflow copies files to correct path
# In workflow or manual deploy:

mkdir -p public/_codex_/cognitive_app
cp -r cognitive_app/dist/* public/_codex_/cognitive_app/

# Verify structure
ls -la public/_codex_/cognitive_app/
# Should show: index.html, assets/, etc.

git add public/
git commit -m "Deploy cognitive app to correct path"
git push
```

**Solution 3: Clear CDN Cache**
```bash
# GitHub Pages doesn't use CDN but browser caches
# 1. Force refresh in browser: Ctrl+Shift+R (or Cmd+Shift+R)
# 2. Clear site data:
#    - DevTools → Application → Storage → Clear site data
# 3. Hard refresh and reload

# For testing in private/incognito window:
# - Open site in Incognito mode
# - No cache = fresh load
```

### Prevention

- ✅ Test locally: `npm run build && npm run preview`
- ✅ Verify base path before commit: `grep base vite.config.ts`
- ✅ Check built HTML: `grep -o 'src="[^"]*' dist/index.html | sort | uniq`
- ✅ Set up URL validation in CI/CD
- ✅ Use absolute paths in all asset references

---

## Problem: "Build Failures"

### Symptoms
- Workflow shows ✗ (failed)
- `npm run build` errors locally
- TypeScript compilation errors

### Diagnostic Steps

#### Step 1: Check Node.js Version
```bash
# 1. Verify version
node --version

# Expected: v22.x.x or higher
# If lower: npm install -g n && n 22

# 2. Check npm version
npm --version

# Expected: v10.x.x or higher

# 3. Set correct Node version
cd cognitive_app
cat .nvmrc  # If exists, shows required version

# 4. If using nvm:
nvm use 22  # Switch to Node 22
```

#### Step 2: Check Dependencies
```bash
# 1. Verify package-lock.json integrity
npm ci --dry-run

# 2. Check for duplicate packages
npm ls --duplicates

# 3. Look for peer dependency warnings
npm ls 2>&1 | grep "peer"

# 4. Check for conflicting versions
npm ls react react-dom vite
```

#### Step 3: Rebuild from Scratch
```bash
cd cognitive_app

# 1. Clean build
rm -rf node_modules package-lock.json dist

# 2. Fresh install
npm install  # Create new lock file

# 3. Type check
npm run lint

# 4. Build with verbose output
npm run build -- --logLevel=debug 2>&1 | tee build-debug.log

# 5. Check for errors
grep -i "error\|fail" build-debug.log
```

### Common Build Errors and Solutions

**Error: "Cannot find module '@github/spark'**
```bash
# Solution:
cd cognitive_app

# 1. Check if installed
npm ls @github/spark

# 2. If missing, install
npm install

# 3. Verify version
npm ls @github/spark | head -1
# Should show: >=0.43.1 <1

# 4. Check package-lock.json
grep "@github/spark" package-lock.json | head -1
```

**Error: "TypeScript compilation error"**
```bash
# Solution:
cd cognitive_app

# 1. Run type check
npm run lint

# 2. Show specific errors
tsc --noEmit

# 3. Fix errors (usually in src/*.tsx)
# Common: wrong prop types, missing returns, etc.

# 4. Type check passes after fixes
npm run lint
```

**Error: "vite build: ENOENT: no such file or directory"**
```bash
# Usually: missing entry file or config

# Solution:
# 1. Verify file exists
ls src/main.tsx

# 2. Check vite.config.ts for correct paths
grep "entry\|input" cognitive_app/vite.config.ts

# 3. Ensure dist/ directory can be written
touch dist/.test && rm dist/.test

# 4. Try build again
npm run build
```

**Error: "npm ERR! code ERESOLVE" (dependency conflict)**
```bash
# Solution:
cd cognitive_app

# 1. Try npm ci (uses exact lock file)
npm ci

# 2. If still fails, update package-lock.json
npm install --save-exact

# 3. Alternative: Use npm legacy resolver
npm install --legacy-peer-deps

# 4. Verify build works
npm run build
```

### Build Validation Checklist

```bash
#!/bin/bash
set -e

echo "🔍 Validating build..."

cd cognitive_app

# 1. Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 22 ]; then
    echo "✅ Node.js version OK (v$(node -v))"
else
    echo "❌ Node.js must be v22+"
    exit 1
fi

# 2. Dependencies
npm ci
echo "✅ Dependencies installed"

# 3. Type check
npm run lint
echo "✅ TypeScript compilation passed"

# 4. Build
npm run build
echo "✅ Build completed"

# 5. Output verification
if [ -f "dist/index.html" ] && [ -d "dist/assets" ]; then
    echo "✅ Build artifacts valid"
else
    echo "❌ Build artifacts incomplete"
    exit 1
fi

echo ""
echo "✅ All build checks passed!"
```

### Prevention

- ✅ Lock Node.js version: Use `.nvmrc` or `engines` in package.json
- ✅ Update dependencies regularly: `npm update`
- ✅ Test builds locally before pushing
- ✅ Use `npm ci` not `npm install` in CI/CD
- ✅ Run full test suite: `npm run test`

---

## Problem: "API Integration Issues"

### Symptoms
- API calls fail with CORS errors
- Authentication fails
- API returns wrong data

### Diagnostic Steps

#### Step 1: Verify API URL
```bash
# 1. Check environment variable
echo $VITE_API_URL

# For local dev, should be: http://localhost:8765
# For production: https://api.example.com

# 2. Set if missing
export VITE_API_URL=http://localhost:8765

# 3. Verify in built app
grep -r "VITE_API_URL" src/ --include="*.tsx"

# 4. Check .env.local
cat cognitive_app/.env.local | grep VITE_API_URL
```

#### Step 2: Check CORS Configuration
```javascript
// In browser console:
// 1. Make test request
fetch('http://localhost:8765/health')
  .then(r => r.json())
  .then(d => console.log('API health:', d))
  .catch(e => console.error('API error:', e.message))

// 2. Check error in Network tab
// CORS error: Response has wrong Access-Control headers

// 3. Check if API server running
// curl http://localhost:8765/health
```

#### Step 3: Verify Authentication
```javascript
// In browser console:
// 1. Check for auth token
console.log(localStorage.getItem('auth_token'))
console.log(sessionStorage.getItem('auth_token'))

// 2. Check if token valid
// Parse JWT if applicable
const token = localStorage.getItem('auth_token')
console.log('Token:', token ? 'present' : 'missing')

// 3. Check API response
fetch('http://localhost:8765/api/user', {
  headers: { 'Authorization': `****** }
})
```

### Common API Issues

**Issue: CORS Error**
```
Error: Access to XMLHttpRequest at 'http://localhost:8765/api/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:**
```bash
# 1. Ensure API server allows origin
# API must have: Access-Control-Allow-Origin header

# 2. Check API CORS config (if available)
curl -i http://localhost:8765/api/test \
  -H "Origin: http://localhost:5173"

# Should include:
# Access-Control-Allow-Origin: http://localhost:5173

# 3. If API is running elsewhere
# Update VITE_API_URL to correct location
# Rebuild if needed
```

**Issue: 404 on API Endpoint**
```
Error: POST /api/endpoint 404 (Not Found)
```

**Solution:**
```bash
# 1. Verify endpoint exists
curl http://localhost:8765/api/endpoint

# 2. Check API documentation
# Usually in /api/docs or /openapi.json

# 3. Verify correct method (POST, GET, etc)
curl -X GET http://localhost:8765/api/endpoint

# 4. Check request body
# Log in DevTools Network tab
```

**Issue: Authentication Fails**
```
Error: 401 Unauthorized
```

**Solution:**
```bash
# 1. Check if logged in
# Look for auth token in localStorage

# 2. Verify token format
# JWT should have 3 parts: header.payload.signature

# 3. Check token expiry
# Decode JWT and check `exp` claim

# 4. Re-authenticate if needed
# Click login button or call login endpoint
```

### Prevention

- ✅ Start API server before dev: `npm run dev` + `python -m cognitive_brain`
- ✅ Check API health on startup
- ✅ Set up request/response logging
- ✅ Monitor browser Network tab for failures
- ✅ Test API endpoints with curl before developing

---

## Comprehensive Troubleshooting Flowchart

```
┌──────────────────────────────────┐
│ Issue Reported                   │
└──────────────┬───────────────────┘
               │
        ┌──────▼──────┐
        │ Is it visible│
        │ in browser?  │
        └──┬────────┬──┘
     YES┌──┘        └──┐NO
       │               │
       ▼               ▼
  ┌─────────────┐  ┌──────────────┐
  │Widgets not  │  │App not       │
  │rendering or │  │loading/404   │
  │showing blank│  │              │
  └─────┬───────┘  └──────┬───────┘
        │                 │
        │ See: Widgets    │ See: App Not
        │ Not Rendering   │ Loading
        │                 │
        ▼                 ▼
  ┌──────────────────────────┐
  │ Check browser console    │
  │ for errors               │
  └──────┬───────────────────┘
         │
    ┌────▼──────┬────────────┐
    │            │            │
    ▼            ▼            ▼
 404 errs   API errs   Component errs
    │            │            │
    │            │            │
  See:        See:         Rebuild
  404 Errors  API Issues   See: Build
              │            Failures
              ▼
        Set VITE_API_URL
        Rebuild
        Restart dev server

┌─────────────────────────────────┐
│ Issue Resolved?                 │
└────┬────────────────────────┬───┘
     │ YES                    │ NO
     │                        │
     ▼                        ▼
  ✅ Document          ❌ Escalate
  (if new issue)       & Log Details
```

---

## Support Resources

### Gathering Debug Information

```bash
#!/bin/bash
# Run this to collect debug info for support

echo "=== System Info ===" > debug-info.txt
node --version >> debug-info.txt
npm --version >> debug-info.txt
uname -a >> debug-info.txt

echo "" >> debug-info.txt
echo "=== Build Log ===" >> debug-info.txt
cd cognitive_app
npm ci >> debug-info.txt 2>&1
npm run build >> debug-info.txt 2>&1

echo "" >> debug-info.txt
echo "=== Package Info ===" >> debug-info.txt
npm ls --all >> debug-info.txt 2>&1

echo "" >> debug-info.txt
echo "=== Workflow Status ===" >> debug-info.txt
gh run list --workflow pages-mkdocs.yml --limit 1 >> debug-info.txt

cat debug-info.txt
```

### Escalation Procedure

1. **Collect Information**
   - Run debug script above
   - Capture screenshots of console errors
   - Note exact reproduction steps

2. **Check Documentation**
   - Review troubleshooting guide above
   - Check GitHub Issues for similar problems
   - Search error messages online

3. **Contact Support**
   - File issue with debug info
   - Include reproduction steps
   - Provide expected vs actual behavior

---

**Last Updated**: 2026-07-20  
**Maintainer**: DevOps Team  
**Status**: Production Ready
