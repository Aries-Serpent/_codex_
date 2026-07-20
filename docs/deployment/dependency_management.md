# Dependency Management Guide

**Version**: 1.0.0  
**Last Updated**: 2026-07-20  
**Status**: Production Ready

## Table of Contents

1. [Overview](#overview)
2. [Dependency Pinning Policy](#dependency-pinning-policy)
3. [Version Ranges](#version-ranges)
4. [Breaking Changes](#breaking-changes)
5. [Update Procedures](#update-procedures)
6. [Compatibility Matrix](#compatibility-matrix)
7. [Security Updates](#security-updates)
8. [Node.js Version Support](#nodejs-version-support)
9. [Dependency Audit](#dependency-audit)

## Overview

### Dependency Philosophy

The Cognitive App maintains strict dependency management to ensure:
- **Reproducibility**: Same code + same environment = same output
- **Security**: No vulnerable dependency versions in production
- **Stability**: No unexpected breaking changes between environments
- **Predictability**: Version behavior documented and tested

### Current Core Dependencies

```json
{
  "core": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "~5.7.2",
    "vite": "^7.3.6",
    "tailwindcss": "^4.1.18",
    "@github/spark": ">=0.43.1 <1"
  },
  "ui": {
    "@radix-ui/react-*": "^1.x.x",
    "@phosphor-icons/react": "^2.1.10",
    "lucide-react": "^0.484.0"
  },
  "utilities": {
    "framer-motion": "^12.24.0",
    "sonner": "^2.0.1",
    "zod": "^3.25.76",
    "marked": "^15.0.12",
    "mermaid": "^11.15.0"
  }
}
```

## Dependency Pinning Policy

### Policy Rules

| Level | Rule | Example | When to Use |
|-------|------|---------|------------|
| **Exact** | `major.minor.patch` | `"5.7.2"` | Critical deps, known issues |
| **Minor** | `~major.minor` | `"~5.7.2"` | Stable core tools |
| **Minor-Patch** | `^major.minor` | `"^5.0.0"` | Framework/UI libs |
| **Major-Minor** | `>=major <next` | `">=0.43.1 <1"` | Pre-1.0 packages |

### Pinning Decision Tree

```
Does dependency have breaking changes?
├─ YES (frequent breaking changes)
│  └─ Use Exact: "5.7.2"
│     Example: TypeScript (breaking in minor versions)
└─ NO (stable)
   └─ Does semver follow semantic versioning?
      ├─ YES (strict semver)
      │  └─ Use Minor-Patch: "^5.0.0"
      │     Example: React, Tailwind
      └─ NO (unstable semver)
         └─ Use Exact or Minor: "~5.7.2"
            Example: Beta/pre-release packages
```

### Current Pinning Strategy

```json
{
  "typescript": "~5.7.2",
  "vite": "^7.3.6",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "@github/spark": ">=0.43.1 <1",
  "@radix-ui/react-*": "^1.x.x",
  "@tailwindcss/vite": "^4.1.11",
  "tailwindcss": "^4.1.18",
  "@phosphor-icons/react": "^2.1.10"
}
```

**Reasoning**:
- `typescript ~5.7.2`: Breaking changes in minor versions, strict pinning required
- `vite ^7.3.6`: Stable semver, minor/patch updates safe
- `react ^19.0.0`: Major version stable, patch updates safe
- `@github/spark >=0.43.1 <1`: Pre-1.0, restrict to this major only
- UI libraries `^1.x.x`: Radix stable at 1.x, safe to update patches

## Version Ranges

### Understanding npm Version Syntax

| Syntax | Meaning | Example | Allows |
|--------|---------|---------|--------|
| `1.2.3` | Exact version | `"1.2.3"` | Only 1.2.3 |
| `~1.2.3` | ~Allows patch | `"~1.2.3"` | 1.2.3, 1.2.4, ..., 1.2.x |
| `^1.2.3` | Allows minor | `"^1.2.3"` | 1.2.3, 1.3.0, 1.4.0, ..., 1.x.x |
| `>=1.2.3` | Greater or equal | `">=1.2.3"` | 1.2.3, 1.2.4, 1.3.0, 2.0.0, ... |
| `1.2.3 - 1.4.0` | Range | `"1.2.3 - 1.4.0"` | 1.2.3, ..., 1.4.0 |
| `>=1.2.3 <2.0.0` | Range | `">=1.2.3 <2.0.0"` | 1.2.3, ..., 1.99.99 |

### Semantic Versioning Explained

```
MAJOR.MINOR.PATCH
│      │      │
│      │      └─ Bug fixes, no breaking changes
│      │         Example: 1.2.0 → 1.2.1 (safe to auto-update)
│      │
│      └─ New features, backward compatible
│         Example: 1.2.0 → 1.3.0 (usually safe)
│
└─ Breaking changes, incompatible API
   Example: 1.0.0 → 2.0.0 (requires review)
```

### Update Safety Guide

```
Auto-Update (lowest risk):
├─ PATCH updates: 1.2.3 → 1.2.4
│  └─ Risk: Very low (bug fixes only)
│  └─ When: Always safe (unless noted in changelog)
│  └─ Testing: Unit tests sufficient
│
├─ MINOR updates: 1.2.0 → 1.3.0
│  └─ Risk: Low (new features, backward compatible)
│  └─ When: Safe for most stable packages
│  └─ Testing: Integration tests recommended
│  └─ Review: Check changelog for deprecations
│
└─ MAJOR updates: 1.0.0 → 2.0.0
   └─ Risk: High (breaking changes)
   └─ When: Only after thorough review
   └─ Testing: Full regression testing required
   └─ Review: Mandatory code review
```

## Breaking Changes

### Tracking Breaking Changes

Create a `BREAKING_CHANGES.md` file:

```markdown
# Breaking Changes Log

## React 19 Upgrade (2026-07-20)

**Package**: react, react-dom  
**From**: 18.x → **To**: 19.0.0  
**Impact**: Major

### Changes
1. **React Compiler Integration**
   - Now available, but optional
   - Some patterns need refactoring
   - See: src/components/Widget.tsx

2. **New Hooks (useTransition, useReducer)**
   - Improved stability
   - Backward compatible
   - No changes required

3. **Automatic batching**
   - All state updates batched
   - Improves performance
   - May affect timing-dependent code

### Migration Guide
- See: `/docs/deployment/dependency_management.md`
- Related issue: #1234
- Reviewed by: @reviewer

### Testing
- [x] Unit tests pass
- [x] E2E tests pass
- [x] Performance tests pass (5% improvement)
- [x] Manual testing complete

---

## @radix-ui/react-dialog Upgrade (2026-06-15)

**Package**: @radix-ui/react-dialog  
**From**: 1.1.1 → **To**: 1.1.6  
**Impact**: Minor (breaking changes possible)

### Changes
- Improved keyboard navigation
- Better accessibility (ARIA attributes)
- Fixed memory leaks

### Notes
- Mostly compatible
- Check dialog closing behavior
- Updated in: src/components/Modal.tsx

---
```

### Identifying Breaking Changes

```bash
#!/bin/bash
# Script to check for breaking changes

PACKAGE=$1

# Get version history
npm view $PACKAGE versions

# Check changelog
npm view $PACKAGE readme | grep -A 20 "Breaking\|Breaking Changes\|Migration"

# Get release notes
npm view $PACKAGE | grep -A 5 "description\|keywords"

# Check for pre-release or major bumps
npm show $PACKAGE@latest version
npm show $PACKAGE@next version
```

### Common Breaking Changes by Package

**TypeScript**
```
Breaks often on minor version bumps
Example: 5.6.0 → 5.7.0 may have breaking changes
Action: Always test on new version
Mitigate: Use `~5.7.2` strict pinning
```

**Vite**
```
Generally stable, breaking changes rare
Example: 7.0.0 → 7.1.0 usually safe
Action: Review changelog for major versions
Mitigate: Use `^7.3.6` allows minor/patch
```

**React**
```
Follows strict semver at major versions
Example: 19.0.0 stable, minor updates safe
Action: Full testing on major bumps
Mitigate: Use `^19.0.0` safe for patches
```

**@github/spark**
```
Pre-1.0 package, treat carefully
Example: 0.43.1 → 0.44.0 may break
Action: Test before updating
Mitigate: Use `>=0.43.1 <1` restrict major only
```

## Update Procedures

### Preparing for Updates

#### 1. Create Update Branch

```bash
git checkout -b feat/dependencies-update-2026-07-20

# Document what will be updated
cat > UPDATE_PLAN.md << 'EOF'
# Dependency Update Plan

Date: 2026-07-20
Updated by: @your-username

## Target Packages
- [ ] react: 18.x → 19.0.0
- [ ] typescript: 5.6.x → 5.7.2
- [ ] @github/spark: 0.43.1 → 0.44.0

## Pre-Update Checklist
- [ ] All tests passing
- [ ] No pending changes
- [ ] Branch is current

## Post-Update Checklist
- [ ] npm ci succeeds
- [ ] npm run build succeeds
- [ ] npm run lint passes
- [ ] npm run test passes
- [ ] npm run test:e2e passes
- [ ] Manual testing complete

## Rollback Plan
If issues found:
```bash
git revert HEAD
npm ci
# Test
EOF
```

#### 2. Audit Current Dependencies

```bash
cd cognitive_app

# Check for vulnerabilities
npm audit --json > audit-before.json

# Check outdated packages
npm outdated

# Expected output shows:
# Package       Current  Latest  Location
# react         18.2.0   19.0.0  cognitive_app
```

#### 3. Understand What's Outdated

```bash
# Get details on specific package
npm view react@latest

# See changelog
npm view react@19.0.0 description

# Check tags
npm info react | grep -A 10 "version"
```

### Performing Updates

#### Safe Update (Patch/Minor)

```bash
cd cognitive_app

# Update specific package to latest minor
npm update react-dom

# Or update all packages
npm update

# Verify package-lock.json changed
git diff package-lock.json | head -30

# Install and verify
npm ci
npm run build
npm run test
```

#### Risky Update (Major Version)

```bash
cd cognitive_app

# First, understand the changes
npm view react@19.0.0 readme

# Update package.json manually
# Change: "react": "^18.0.0" → "^19.0.0"

cat > package.json << 'EOF'
{
  "dependencies": {
    "react": "^19.0.0",  // <-- Updated
    "react-dom": "^19.0.0"  // <-- Updated
  }
}
EOF

# Install new version
npm ci

# Run comprehensive tests
npm run lint
npm run build
npm run test
npm run test:e2e

# If errors, investigate and fix
# Commit changes documenting what changed
git add package.json package-lock.json

git commit -m "upgrade(deps): react 18 → 19

- Update react to 19.0.0
- Update react-dom to 19.0.0
- All tests passing
- See BREAKING_CHANGES.md for migration notes
- Fixes: component re-render performance"

# Push and create PR
git push origin feat/dependencies-update-2026-07-20
```

#### Batch Updates

```bash
#!/bin/bash
set -e

cd cognitive_app

echo "📦 Starting batch update..."

# 1. Backup current state
cp package-lock.json package-lock.json.backup

# 2. Update all dependencies
npm update

# 3. Check what changed
echo "Changes:"
npm outdated

# 4. Run test suite
echo "Testing..."
npm run lint
npm run build
npm run test

# 5. Manual verification
npm run preview &
PREVIEW_PID=$!
echo "Starting preview server (PID: $PREVIEW_PID)"
echo "Open http://localhost:4173 to verify"
read -p "Press Enter when done testing..."
kill $PREVIEW_PID

# 6. Cleanup and commit
git add package.json package-lock.json
git commit -m "chore(deps): update dependencies $(date +%Y-%m-%d)"
git push origin feat/dependencies-update

echo "✅ Batch update complete"
```

### Testing After Updates

```bash
#!/bin/bash
set -e

cd cognitive_app

echo "🧪 Running full test suite..."

# Unit tests
echo "📝 Running unit tests..."
npm run test
if [ $? -ne 0 ]; then echo "❌ Unit tests failed"; exit 1; fi

# Type check
echo "🔍 Type checking..."
npm run lint
if [ $? -ne 0 ]; then echo "❌ Lint failed"; exit 1; fi

# Build
echo "🏗️ Building..."
npm run build
if [ $? -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

# E2E tests
echo "🌐 Running E2E tests..."
npm run test:e2e
if [ $? -ne 0 ]; then echo "❌ E2E tests failed"; exit 1; fi

# Preview and manual test
echo "👀 Starting preview server..."
npm run preview &
PREVIEW_PID=$!

sleep 2
if ! curl -s http://localhost:4173 > /dev/null; then
    echo "❌ Preview server failed to start"
    kill $PREVIEW_PID 2>/dev/null
    exit 1
fi

echo "✅ All tests passed!"
kill $PREVIEW_PID 2>/dev/null
```

## Compatibility Matrix

### Tested Combinations

| Node.js | npm | Vite | React | TypeScript | Status |
|---------|-----|------|-------|-----------|--------|
| 22.11.0 | 10.8.3 | 7.3.6 | 19.0.0 | 5.7.2 | ✅ Prod |
| 22.10.0 | 10.8.0 | 7.3.5 | 19.0.0 | 5.7.1 | ✅ Supported |
| 22.8.0 | 10.5.0 | 7.3.0 | 19.0.0 | 5.7.0 | ✅ Supported |
| 21.x | 9.x | 7.x | 19.0.0 | 5.x | ❌ Not Supported |

### Creating Compatibility Matrix

```bash
#!/bin/bash
# Test multiple Node versions

VERSIONS=("22.11.0" "22.10.0" "22.8.0")

for VERSION in "${VERSIONS[@]}"; do
    echo "Testing with Node $VERSION..."
    
    nvm use $VERSION
    node --version
    npm --version
    
    cd cognitive_app
    npm ci
    npm run build
    npm run test
    
    if [ $? -eq 0 ]; then
        echo "✅ Node $VERSION: OK"
    else
        echo "❌ Node $VERSION: FAILED"
    fi
done
```

### Version Support Policy

**Active Support**:
- Node.js 22.11.0+
- npm 10.8.3+
- Latest Vite 7.x

**Legacy Support** (1 year):
- Node.js 22.0.0+
- npm 10.0.0+
- Vite 7.0.0+

**Unsupported**:
- Node.js < 22.0.0
- npm < 10.0.0
- Vite < 7.0.0

## Security Updates

### Security Policy

1. **Critical**: Apply immediately, emergency update
2. **High**: Apply within 1 week
3. **Medium**: Apply within 1 month
4. **Low**: Apply in next scheduled update

### Checking for Vulnerabilities

```bash
cd cognitive_app

# Run audit
npm audit

# Expected output:
# found 0 vulnerabilities

# Detailed JSON audit
npm audit --json | jq '.vulnerabilities'

# Get only critical/high
npm audit --json | jq '.vulnerabilities | map(select(.severity=="critical" or .severity=="high"))'
```

### Applying Security Updates

```bash
cd cognitive_app

# Check vulnerabilities
npm audit

# If vulnerabilities found:

# Option 1: Auto-fix (if available)
npm audit fix

# Option 2: Manual update
npm update [vulnerable-package]

# Option 3: Force update (use carefully)
npm install [package@latest]

# Verify fix
npm audit

# Run tests to ensure no breakage
npm ci
npm run build
npm run test
```

### Security Update Documentation

```markdown
# Security Update Log

## [Date] Critical: Node.js Security Update

**Package**: @vulnerable/package  
**CVE**: CVE-2024-XXXXX  
**Severity**: CRITICAL  
**Fix**: Update to version 1.2.4

### Impact
- Potential RCE if not updated
- All production deployments affected

### Action Taken
- Updated to @vulnerable/package@1.2.4
- All tests passing
- Deployed to production
- Monitoring for issues

### Reference
- https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX
```

## Node.js Version Support

### Current Support

- **Current**: Node.js 22.11.0 LTS
- **Minimum**: Node.js 22.0.0
- **Not Supported**: Node.js 20.x and earlier

### Why Node 22+

```
Benefits:
├─ Performance: 10-15% faster builds
├─ Stability: LTS with 3-year support
├─ Security: Latest patches
├─ Features: ES2024 support
└─ Tools: TypeScript 5.7+ requires Node 22+
```

### Upgrading Node.js

```bash
# Using nvm (recommended)
nvm install 22
nvm use 22
nvm alias default 22

# Verify
node --version  # v22.x.x
npm --version   # v10.x.x

# Update nvm tools
nvm cache clear
nvm list
```

### Enforcing Node Version

Add to package.json:

```json
{
  "engines": {
    "node": ">=22.0.0",
    "npm": ">=10.0.0"
  }
}
```

Add .nvmrc:

```bash
# .nvmrc
22.11.0
```

Add GitHub Actions check:

```yaml
- name: Check Node version
  run: |
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 22 ]; then
      echo "❌ Node.js must be 22+"
      exit 1
    fi
```

## Dependency Audit

### Regular Audit Schedule

- **Daily**: Automated security scans
- **Weekly**: Check for outdated packages
- **Monthly**: Full audit + update review
- **Quarterly**: Major version compatibility review

### Automated Audit Workflow

```yaml
# .github/workflows/dependency-audit.yml
name: Dependency Audit

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly Monday
  pull_request:
    paths:
      - 'package.json'
      - 'package-lock.json'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: 'cognitive_app/package-lock.json'
      
      - name: Run security audit
        run: npm audit --audit-level=high
        working-directory: cognitive_app
```

### Audit Checklist

- [ ] No vulnerabilities (npm audit shows 0)
- [ ] No outdated packages (npm outdated shows none)
- [ ] All critical patches applied
- [ ] License compliance verified
- [ ] Breaking changes documented
- [ ] Tests passing with new versions

### Dependency Report

```markdown
# Monthly Dependency Report

**Period**: 2026-07-01 to 2026-07-31

## Summary
- Total dependencies: 45
- Direct dependencies: 35
- Peer dependencies: 10
- Vulnerabilities found: 0
- Updates available: 12
  - Patch updates: 10
  - Minor updates: 2
  - Major updates: 0

## Changes This Month
- React: 18.2.0 → 19.0.0 (Major)
- TypeScript: 5.6.3 → 5.7.2 (Minor)
- @github/spark: 0.43.1 → 0.43.2 (Patch)

## Recommendations
- Review React 19 breaking changes
- Update TypeScript patterns
- All patches can be safely applied

## Next Month
- Schedule React testing
- Plan TypeScript migration
- Monitor for new vulnerabilities
```

---

## Reference Links

- [npm Semantic Versioning](https://docs.npmjs.com/about-semantic-versioning)
- [Node.js Release Schedule](https://nodejs.org/en/about/releases/)
- [GitHub Security Advisory Database](https://github.com/advisories)
- [Vite Migration Guide](https://vite.dev/)
- [React Upgrade Guide](https://react.dev/blog/2024/12/05/react-19)

---

**Last Updated**: 2026-07-20  
**Maintainer**: DevOps Team  
**Status**: Production Ready
