# Cognitive App GitHub Pages Deployment Fix

**Date**: 2026-07-18  
**Issue**: cognitive_app React application was showing only text from docs/cognitive_app.md instead of built React widgets on GitHub Pages

## Root Cause Analysis

The `pages-mkdocs.yml` workflow was responsible for building and deploying the cognitive_app, but had three critical issues:

### 1. Missing Node.js Setup
- **Problem**: The workflow did not include a `setup-node` action
- **Impact**: The build environment had an old/incompatible Node.js version
- **Evidence**: 
  - `cognitive_app/package.json` requires Node >=22.0.0
  - `deploy-cognitive-app.yml` (disabled) had a TODO comment: "TODO (node22): update node-version to '22' before re-enabling this workflow"
  - Disabled workflow used Node 20, which is incompatible

### 2. Build Failures Silently Ignored
- **Problem**: The build step used `continue-on-error: true` and `2>/dev/null` for all output
- **Impact**: Build failures were completely hidden from logs, making debugging impossible
- **Evidence**: The build never completed successfully, but no error messages were visible

### 3. Improper Error Handling
- **Problem**: Used `|| true` at the end of `npm run build`, which suppresses exit codes
- **Impact**: The workflow proceeded even if the build failed
- **Example**: `npm run build 2>/dev/null || true` would silently fail and continue

## Fixes Applied

### 1. Added Node.js 22 Setup
**File**: `.github/workflows/pages-mkdocs.yml`

```yaml
- name: Set up Node.js 22
  uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: 'npm'
    cache-dependency-path: cognitive_app/package-lock.json
```

- Uses Node.js 22 (meets >=22.0.0 requirement from package.json)
- Enables npm caching for faster builds
- Caches cognitive_app dependencies

### 2. Replaced Build Step with Transparent Error Handling
**File**: `.github/workflows/pages-mkdocs.yml`

**Before**:
```bash
run: "if [ -f cognitive_app/package.json ]; then\n  cd cognitive_app\n  npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true\n  npm run build 2>/dev/null || true\n  ...
```

**After**:
```yaml
run: |
  echo "📦 Building cognitive_app dashboard..."
  echo "   API mode: ${VITE_API_MODE} | CLI URL: ${VITE_CLI_API_URL:-<not set>}"
  
  npm ci
  npm run build
  
  if [ -d dist ]; then
    mkdir -p ../site/cognitive_app
    cp -r dist/* ../site/cognitive_app/
    echo "✅ cognitive_app built and deployed to site/cognitive_app/"
    ls -la ../site/cognitive_app/ | head -15
  else
    echo "❌ ERROR: cognitive_app build did not produce dist/ directory"
    exit 1
  fi
```

**Improvements**:
- Removes `continue-on-error: true` to fail fast on build failures
- Removes `2>/dev/null` to capture and display all output
- Removes `|| true` to fail on actual errors
- Uses `working-directory: cognitive_app` for cleaner paths
- Adds diagnostic output (API mode, CLI URL)
- Validates that dist/ directory was created before copying
- Fails with explicit error message if dist/ is missing
- Lists deployed files for verification

## Build Verification

**Local build test** (2026-07-18T07:37:21Z):
- Node version: v24.18.0 ✅
- npm version: 11.16.0 ✅
- Dependencies installed: 643 packages ✅
- Build output: Emitted 8733 modules ✅
- Dist directory created with:
  - index.html (795 B)
  - assets/ (12K) with all CSS, JS, fonts
  - proxy.js (1.5MB)
  - package.json (262 B)

## Expected Outcomes

After this fix:

1. ✅ GitHub Pages will show interactive React widgets instead of static markdown
2. ✅ The cognitive_app will be deployed to `https://aries-serpent.github.io/_codex_/cognitive_app/`
3. ✅ Build failures will be immediately visible in workflow logs
4. ✅ No more silent failures hidden by error suppression

## Files Modified

1. `.github/workflows/pages-mkdocs.yml`
   - Added Node.js 22 setup step
   - Replaced build step with improved error handling

## Related Context

- **Disabled workflow**: `.github/workflow-archive/disabled/deploy-cognitive-app.yml` (was previously used)
- **MkDocs workflow**: `.github/workflows/pages-mkdocs.yml` (now consolidates both doc and app deployment)
- **Build location**: `/home/runner/work/_codex_/_codex_/cognitive_app/`
- **Output location**: `site/cognitive_app/` (merged into GitHub Pages deployment)

## Backward Compatibility

- No breaking changes to deployment URLs
- cognitive_app still deployed to same location on GitHub Pages
- Python documentation build process unaffected
- All environment variables preserved (VITE_API_MODE, VITE_CLI_API_URL)

## Testing

The fix was validated by:
1. Local `npm ci && npm run build` - ✅ Successful
2. Verified dist/ directory structure - ✅ Correct
3. YAML syntax validation - ✅ Valid workflow
4. Node version compatibility check - ✅ v24.18.0 meets >=22 requirement
