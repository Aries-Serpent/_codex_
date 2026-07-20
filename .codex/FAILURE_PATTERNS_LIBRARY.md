# Failure Patterns Library

**Version**: 1.0.0  
**Last Updated**: 2026-07-20  
**Status**: Production Ready

This document catalogs recurring failure patterns observed in Cognitive App deployment and provides reusable solutions, root cause analysis, and prevention strategies.

## Pattern Index

1. [Silent Build Failures](#pattern-1-silent-build-failures)
2. [Missing Dependencies](#pattern-2-missing-dependencies)
3. [Path Configuration Issues](#pattern-3-path-configuration-issues)
4. [Deployment Timing Problems](#pattern-4-deployment-timing-problems)
5. [Node.js Version Mismatch](#pattern-5-nodejs-version-mismatch)
6. [Cache Invalidation Failures](#pattern-6-cache-invalidation-failures)

---

## Pattern 1: Silent Build Failures

### Problem Statement

Build errors are suppressed by error redirection (`2>/dev/null`) or `|| true` operators, causing build failures to go unnoticed. The workflow reports success when the build actually failed.

### Symptoms

- Workflow shows ✅ success but no new files appear in deployment
- `dist/` directory exists but is empty or incomplete
- No error messages in logs
- Previous version remains deployed

### Root Cause Analysis

```bash
# Example of silent failure pattern
npm run build 2>/dev/null || true  # WRONG: Hides all errors
# vs
npm run build  # RIGHT: Shows errors
```

**Why This Happens**:
1. Error redirection (`2>/dev/null`) sends stderr to null
2. `|| true` operator makes command always succeed
3. Build tools exit silently on some errors
4. CI/CD logs become misleading

### Real-World Example

```yaml
# ❌ WRONG: pages-mkdocs.yml (problematic)
- name: Build app
  run: |
    cd cognitive_app
    npm ci 2>/dev/null || true
    npm run build 2>/dev/null || true
    # If npm fails, we don't know it

# Actual behavior:
# 1. npm ci fails (e.g., dependency conflict)
# 2. Error suppressed, command returns true
# 3. Build step skipped
# 4. Workflow continues as if successful
# 5. Nothing deployed
```

### Solution: Remove Error Suppression

```yaml
# ✅ CORRECT: pages-mkdocs.yml (fixed)
- name: Build app
  run: |
    set -e  # Exit on any error
    cd cognitive_app
    npm ci
    npm run build
    # If any step fails, workflow stops here

# With explicit error checking:
- name: Build app
  run: |
    cd cognitive_app
    npm ci || { echo "npm ci failed"; exit 1; }
    npm run build || { echo "Build failed"; exit 1; }
    # Errors explicitly reported
```

### Prevention Strategy

**Principle: Fail Fast**

```bash
#!/bin/bash
set -e  # Exit on first error
set -o pipefail  # Fail if any command in pipe fails

# Instead of:
npm ci 2>/dev/null || true

# Use:
npm ci  # Let errors bubble up

# Explicit validation:
if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo "❌ Build failed: dist/index.html not found"
    exit 1
fi

echo "✅ Build successful"
```

### Deployment Checklist

```yaml
# Enforce explicit status checks
- name: Build app
  run: |
    cd cognitive_app
    npm ci
    npm run build
    
- name: Validate build output
  run: |
    if [ ! -f "cognitive_app/dist/index.html" ]; then
      echo "❌ Build validation failed: index.html not found"
      exit 1
    fi
    
    if [ ! -d "cognitive_app/dist/assets" ]; then
      echo "❌ Build validation failed: assets directory missing"
      exit 1
    fi
    
    FILE_COUNT=$(find cognitive_app/dist -type f | wc -l)
    if [ $FILE_COUNT -lt 5 ]; then
      echo "❌ Build validation failed: only $FILE_COUNT files (expected >5)"
      exit 1
    fi
    
    echo "✅ Build validation passed"
```

### Monitoring and Alerts

```bash
#!/bin/bash
# Detect silent failures in build logs

LOG_FILE=$1

# 1. Check for error indicators
if grep -q "error\|ERROR\|Error" "$LOG_FILE" 2>/dev/null; then
    echo "⚠️ Errors found in build log"
    grep "error\|ERROR\|Error" "$LOG_FILE" | head -10
    exit 1
fi

# 2. Check build artifacts exist
if [ ! -f "dist/index.html" ]; then
    echo "❌ Build artifact missing"
    exit 1
fi

# 3. Check artifact size (catches partial builds)
SIZE=$(stat -f%z dist/index.html 2>/dev/null || stat -c%s dist/index.html)
if [ $SIZE -lt 1000 ]; then
    echo "⚠️ Build artifact suspiciously small: $SIZE bytes"
    exit 1
fi

echo "✅ Build validation passed"
```

---

## Pattern 2: Missing Dependencies

### Problem Statement

Build fails with `npm ci` errors due to missing, incompatible, or incompletely locked dependencies. Package-lock.json is corrupted or out of sync with package.json.

### Symptoms

- `npm ERR! code ERESOLVE` - Dependency conflicts
- `npm ERR! missing: package-name` - Missing dependency
- `npm ERR! peer dep missing` - Peer dependency not installed
- Build hangs waiting for resolution
- Different results in local vs CI environment

### Root Cause Analysis

**Common Causes**:
1. **Corrupted package-lock.json**: Manual edits, merge conflicts
2. **Version mismatch**: package.json and package-lock.json out of sync
3. **Peer dependency issues**: Incompatible versions specified
4. **Network issues**: Incomplete download during `npm ci`
5. **Registry unavailable**: npm registry timeout or outage

### Real-World Example

```json
// ❌ WRONG: Conflicting versions
{
  "dependencies": {
    "react": "^19.0.0",
    "@radix-ui/react-dialog": "^1.1.1"  // Requires react 18.x!
  }
}

// Results in:
// npm ERR! code ERESOLVE
// npm ERR! ERESOLVE unable to resolve dependency tree
```

### Solution: Validate Dependencies

```bash
#!/bin/bash
# Dependency validation script

echo "🔍 Validating dependencies..."

# 1. Check for conflicts
npm ls 2>&1 | grep -i "deduped\|peer\|missing"

# 2. Attempt resolution
npm ci --dry-run

# 3. If fails, try reset
if [ $? -ne 0 ]; then
    echo "⚠️ Dependency conflict detected, attempting repair..."
    
    # Remove lock file and reinstall
    rm -f package-lock.json
    npm install --save-exact  # Use exact versions
    
    # Verify again
    npm ci --dry-run
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies fixed"
    else
        echo "❌ Could not fix dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies valid"
fi
```

### Prevention Strategy

**Principle: Lock Everything, Update Carefully**

```bash
#!/bin/bash
# Dependency safety checklist

set -e

# 1. Use npm ci (not npm install) in CI
npm ci

# 2. Validate lock file integrity
npm ls --all > /dev/null

# 3. Check for peer dependency warnings
npm ls 2>&1 | grep -i "peer" && {
    echo "⚠️ Peer dependency warnings"
    exit 1
}

# 4. Verify all dependencies installable
npm install --dry-run

echo "✅ Dependency validation passed"
```

### Compatibility Matrix

Document compatible version combinations:

```markdown
# Dependency Compatibility Matrix

## Tested Combinations

| Node.js | npm | React | TypeScript | Status |
|---------|-----|-------|-----------|--------|
| 22.11.0 | 10.8.3 | 19.0.0 | 5.7.2 | ✅ Prod |
| 22.10.0 | 10.8.0 | 19.0.0 | 5.7.1 | ✅ Tested |
| 22.0.0 | 10.0.0 | 19.0.0 | 5.7.0 | ⚠️ Minimum |

## Incompatible Combinations

| Issue | From | To | Solution |
|-------|------|-----|----------|
| React 19 + Radix 1.0 | conflicting | 1.1.x | Update Radix |
| TS 5.6 + Vite 7 | breaking | TS 5.7 | Upgrade TypeScript |
```

### Testing Procedure

```bash
#!/bin/bash
# Test dependency updates

set -e

echo "📦 Testing dependency update..."

# 1. Current state
npm ls > current-deps.txt

# 2. Attempt update
npm update

# 3. Run tests
npm run test
npm run build

# 4. Compare
npm ls > new-deps.txt
diff -u current-deps.txt new-deps.txt || true

# 5. Validate
npm audit

echo "✅ Dependency update test complete"
```

---

## Pattern 3: Path Configuration Issues

### Problem Statement

Assets not found due to incorrect base path configuration. Links, images, and API endpoints point to wrong URLs. Site works locally but fails on GitHub Pages.

### Symptoms

- Network requests show 404 for assets
- Mixed content warnings (http vs https)
- Images not loading
- CSS not applied
- API calls fail with CORS errors

### Root Cause Analysis

```javascript
// ❌ WRONG: Local path
// In vite.config.ts
base: '/',  // Works locally, breaks on GitHub Pages

// ✅ CORRECT: Environment-aware path
base: process.env.GITHUB_ACTIONS ? '/_codex_/cognitive_app/' : '/'
```

**Why This Happens**:
1. Developer tests locally with `/` base path
2. Doesn't account for GitHub Pages subdirectory: `/_codex_/cognitive_app/`
3. Environment variable `GITHUB_ACTIONS` not set during local build
4. Assets reference `/assets/` instead of `/_codex_/cognitive_app/assets/`

### Real-World Example

```
Local development:
✅ Works: http://localhost:5173/index.html
✅ Assets: http://localhost:5173/assets/index.js

GitHub Pages deployment:
❌ Breaks: https://site.github.io/_codex_/cognitive_app/index.html
❌ Assets look for: https://site.github.io/assets/index.js (404!)
✅ Should be: https://site.github.io/_codex_/cognitive_app/assets/index.js
```

### Solution: Centralize Path Configuration

```typescript
// ✅ CORRECT: vite.config.ts
export default defineConfig({
  // Environment-aware base path
  base: process.env.GITHUB_ACTIONS 
    ? '/_codex_/cognitive_app/'  // GitHub Pages
    : '/',                         // Local dev
  
  // ... rest of config
});

// Ensure GITHUB_ACTIONS is set in workflow
```

### Prevention Strategy

**Principle: Environment Variables for All Paths**

```bash
#!/bin/bash
# Build with explicit environment

# Local build
npm run build  # Uses base: '/'

# GitHub Pages build
GITHUB_ACTIONS=true npm run build  # Uses base: '/_codex_/cognitive_app/'

# Verify output
grep 'src="/' dist/index.html | head -2
# Should show paths starting with: src="/_codex_/cognitive_app/assets/...
```

### Validation

```bash
#!/bin/bash
# Validate path configuration

HTML_FILE="cognitive_app/dist/index.html"

if [ ! -f "$HTML_FILE" ]; then
    echo "❌ index.html not found"
    exit 1
fi

# Check for correct base path
if grep -q 'src="/_codex_/cognitive_app/assets/\|href="/_codex_/cognitive_app/' "$HTML_FILE"; then
    echo "✅ Base path is correct"
else
    echo "❌ Base path is incorrect"
    echo "Found paths:"
    grep -o 'src="[^"]*\|href="[^"]*' "$HTML_FILE" | grep -o '"[^"]*' | head -5
    exit 1
fi
```

---

## Pattern 4: Deployment Timing Problems

### Problem Statement

Site returns 404 due to incomplete or delayed deployment. Files not yet propagated to all GitHub Pages servers. CDN caching causes stale versions.

### Symptoms

- Site returns 404 immediately after deployment
- Refreshing fixes the issue
- Works in incognito/private mode
- Random 404 errors across different requests

### Root Cause Analysis

```
1. Workflow completes build
2. Pushes to gh-pages branch
3. GitHub Pages updates CDN
4. CDN propagation delay (5-30 seconds)
5. Browser requests with cache → 404
6. User refreshes or waits → loads correctly
```

### Solution: Add Deployment Completion Checks

```bash
#!/bin/bash
# Wait for deployment to complete

SITE_URL="https://aries-serpent.github.io/_codex_/cognitive_app"
MAX_ATTEMPTS=30
ATTEMPT=0

echo "⏳ Waiting for deployment to complete..."

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/index.html")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Deployment complete (HTTP $HTTP_CODE)"
        exit 0
    else
        echo "⏳ Deployment in progress... (HTTP $HTTP_CODE, attempt $ATTEMPT/$MAX_ATTEMPTS)"
        sleep 2
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo "❌ Deployment timeout"
exit 1
```

### Prevention Strategy

**Principle: Validate After Deployment**

```yaml
# Add to workflow after deployment
- name: Verify deployment
  run: |
    SITE_URL="https://aries-serpent.github.io/_codex_/cognitive_app"
    
    # Wait for site to respond
    for i in {1..60}; do
      HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL/index.html")
      if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Deployment verified"
        exit 0
      fi
      sleep 1
    done
    
    echo "❌ Deployment verification failed"
    exit 1
```

### Cache Management

```bash
#!/bin/bash
# Clear browser cache

# Browser cache settings
curl -H "Cache-Control: no-cache, no-store, must-revalidate" \
     -H "Pragma: no-cache" \
     -H "Expires: 0" \
     https://aries-serpent.github.io/_codex_/cognitive_app/index.html

# For local testing
# Open in private/incognito window
# or: Ctrl+Shift+Delete → Clear browsing data
```

---

## Pattern 5: Node.js Version Mismatch

### Problem Statement

Build fails with Node.js version mismatch. Code uses Node 22+ features but CI runs Node 20. TypeScript/Vite incompatibilities cause cryptic errors.

### Symptoms

- `SyntaxError: Unexpected token` for valid code
- `Cannot find module` for existing packages
- `TypeError: X is not a function`
- Build succeeds locally but fails in CI

### Root Cause Analysis

```
Scenario:
1. Developer has Node 22.11.0 locally
2. CI workflow specifies Node 20.x
3. Node 20 doesn't support TypeScript 5.7
4. Build fails in CI, works locally
5. Debugging is painful
```

### Solution: Pin Node Version

```yaml
# ✅ CORRECT: pages-mkdocs.yml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '22'  # Pin major version
    node-version-file: '.nvmrc'  # Or use .nvmrc file
```

### Prevention Strategy

**Principle: Consistent Versions Everywhere**

```bash
#!/bin/bash
# Version consistency check

# 1. Create .nvmrc
echo "22.11.0" > .nvmrc

# 2. Check in engines in package.json
cat >> package.json << 'EOF'
  "engines": {
    "node": ">=22.0.0",
    "npm": ">=10.0.0"
  }
EOF

# 3. Set up local version
nvm install $(cat .nvmrc)
nvm use $(cat .nvmrc)

# 4. Verify
node --version  # v22.11.0
```

### Compatibility Matrix

```markdown
# Node.js Version Support

## Supported
- 22.11.0+ (LTS) ✅
- 22.10.0 ✅
- 22.0.0+ ⚠️ (minimum)

## Not Supported
- 20.x ❌
- 18.x ❌
- 16.x ❌

## Why Node 22+
- TypeScript 5.7 requires Node 22+
- Vite 7 optimized for Node 22+
- React 19 builds faster on Node 22+
```

---

## Pattern 6: Cache Invalidation Failures

### Problem Statement

Stale builds deployed from cache. Build artifacts from previous run used instead of fresh build. CDN serves old versions despite deployment.

### Symptoms

- Changes not reflected in deployed site
- Old version persists after deployment
- Works after `git push --force` or cache clear
- Hash-named files have old timestamps

### Root Cause Analysis

```
1. First build: app.js (content hash: abc123)
2. Code changes: app.js (content hash: abc123) - SAME HASH!
3. Cache serves old version: app-abc123.js
4. Site doesn't update because hash didn't change
```

### Solution: Implement Cache Busting

```typescript
// ✅ CORRECT: Use content hashing in Vite
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  }
});
```

### Prevention Strategy

**Principle: Content-Based Cache Keys**

```bash
#!/bin/bash
# Verify cache busting

cd cognitive_app

# Build twice with same code
npm run build > build1.log
BUILD1_HASH=$(ls dist/assets/*.js | head -1 | grep -o '[a-f0-9]\{8\}')

npm run build > build2.log
BUILD2_HASH=$(ls dist/assets/*.js | head -1 | grep -o '[a-f0-9]\{8\}')

# Hashes should be identical for same code
if [ "$BUILD1_HASH" = "$BUILD2_HASH" ]; then
    echo "✅ Deterministic build (cache busting working)"
else
    echo "❌ Non-deterministic build (hash changed: $BUILD1_HASH → $BUILD2_HASH)"
fi

# Change a file
touch src/main.tsx

# Build again
npm run build > build3.log
BUILD3_HASH=$(ls dist/assets/*.js | head -1 | grep -o '[a-f0-9]\{8\}')

# Hash should change
if [ "$BUILD3_HASH" != "$BUILD1_HASH" ]; then
    echo "✅ Cache busting effective (hash changed)"
else
    echo "❌ Cache busting not working (hash unchanged)"
fi
```

### Deployment Validation

```yaml
# Add to workflow to verify cache busting
- name: Verify cache busting
  run: |
    # Check that asset files have content hashes
    if ls cognitive_app/dist/assets/*-*.js > /dev/null 2>&1; then
      echo "✅ Asset files have content hashes"
    else
      echo "❌ Asset files missing content hashes"
      exit 1
    fi
    
    # Verify different files have different hashes
    FILE_COUNT=$(ls cognitive_app/dist/assets/*-*.js | wc -l)
    UNIQUE_HASHES=$(ls cognitive_app/dist/assets/*-*.js | grep -o '[a-f0-9]\{8\}' | sort -u | wc -l)
    
    if [ $FILE_COUNT -eq $UNIQUE_HASHES ]; then
      echo "✅ All asset hashes are unique"
    else
      echo "⚠️ Some assets share hashes"
    fi
```

---

## Using This Library

### For Developers

1. **Encounter an issue?**
   - Search this document for matching symptoms
   - Review the real-world example
   - Apply the solution
   - Check the prevention strategy

2. **Report New Patterns**
   - Document in similar format
   - Submit PR to update library
   - Include: Problem, Symptoms, Root Cause, Solution

### For DevOps

1. **On-call Runbook**
   - Use pattern index to find issue type
   - Follow solution section step-by-step
   - Document in incident log
   - Update prevention strategy if needed

2. **Monitoring**
   - Use automated checks from patterns
   - Alert on pattern detection
   - Proactively fix before user impact

### For Teams

1. **Training**
   - Reference patterns in code reviews
   - Discuss at retrospectives
   - Link to patterns in documentation
   - Share knowledge across teams

---

## Pattern Metadata

### Contributing to This Library

When adding new patterns, include:

```markdown
## Pattern X: [Short Name]

### Problem Statement
[1-2 sentence description]

### Symptoms
[Bulleted list]

### Root Cause Analysis
[Technical explanation with examples]

### Real-World Example
[Code or scenario showing the issue]

### Solution
[Step-by-step fix]

### Prevention Strategy
[Process to prevent recurrence]

### Monitoring and Alerts
[How to detect automatically]
```

---

## Pattern Library Statistics

- **Total Patterns**: 6
- **Created**: 2026-07-20
- **Last Updated**: 2026-07-20
- **Coverage**: Cognitive App deployment
- **Severity Distribution**: 
  - Critical: 2
  - High: 3
  - Medium: 1

---

**Last Updated**: 2026-07-20  
**Maintainer**: DevOps Team  
**Status**: Production Ready

For issues or improvements, contact the DevOps team or submit a PR.
