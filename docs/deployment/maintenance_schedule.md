# Cognitive App Maintenance Schedule

**Version**: 1.0.0  
**Last Updated**: 2026-07-20  
**Status**: Production Ready

## Overview

This document defines the maintenance schedule for the Cognitive App deployment and supporting infrastructure. Regular maintenance ensures security, performance, and stability.

## Monthly Tasks

### First Monday of Month: Pages-MkDocs Workflow Review

**Time Required**: 30 minutes  
**Owners**: DevOps Team  
**Checklist**:

- [ ] Review workflow execution history
  ```bash
  gh run list --workflow pages-mkdocs.yml --limit 10
  ```

- [ ] Check for failures or timeouts
  ```bash
  gh run list --workflow pages-mkdocs.yml --limit 10 --json conclusion
  ```

- [ ] Verify build times are consistent
  ```bash
  gh run list --workflow pages-mkdocs.yml --limit 10 --json name,conclusion,durationMinutes
  ```

- [ ] Test workflow manually
  ```bash
  gh workflow run pages-mkdocs.yml
  ```

- [ ] Review workflow configuration
  ```bash
  cat .github/workflows/pages-mkdocs.yml | grep -A 5 "timeout\|cache\|Node"
  ```

- [ ] Update workflow if needed
  - Check for deprecated GitHub Actions
  - Review Node version (should be 22.x)
  - Update cache strategy if needed

- [ ] Document any issues in MAINTENANCE_LOG.md

### Maintenance Log Template

```markdown
# Maintenance Log - 2026-07-01

## Pages-MkDocs Workflow Review

**Date**: 2026-07-01  
**Reviewed by**: @reviewer  
**Status**: ✅ All Checks Passed

### Findings
- Build time: 2:45 (normal range)
- Success rate: 100% (4/4 runs)
- Latest version: v7.3.6

### Actions Taken
- None needed, all systems healthy

### Issues Found
- None

### Next Review
- 2026-08-04
```

---

## Quarterly Tasks

### Q1, Q2, Q3, Q4: Asset Structure Validation

**Time Required**: 1 hour  
**Owners**: DevOps Team  
**Schedule**: 
- Q1: January 15-31
- Q2: April 15-30
- Q3: July 15-31
- Q4: October 15-31

### Validation Checklist

```bash
#!/bin/bash
# Quarterly asset structure validation

echo "📦 Starting quarterly asset validation..."

# 1. Check deployment structure
echo "1️⃣ Checking deployment structure..."
git ls-tree origin/gh-pages -r --name-only | grep "_codex_/cognitive_app" > /tmp/deployed_files.txt

EXPECTED_FILES=(
    "_codex_/cognitive_app/index.html"
    "_codex_/cognitive_app/assets/"
)

for file in "${EXPECTED_FILES[@]}"; do
    if grep -q "$file" /tmp/deployed_files.txt; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
    fi
done

# 2. Check file sizes
echo ""
echo "2️⃣ Checking file sizes..."
git cat-file -s origin/gh-pages:_codex_/cognitive_app/index.html > /tmp/index_size.txt
INDEX_SIZE=$(cat /tmp/index_size.txt)
echo "  - index.html size: $INDEX_SIZE bytes"

if [ $INDEX_SIZE -lt 5000 ]; then
    echo "  ⚠️ index.html seems small, may be corrupted"
elif [ $INDEX_SIZE -gt 50000 ]; then
    echo "  ⚠️ index.html seems large, may be unminified"
else
    echo "  ✅ index.html size is normal"
fi

# 3. Check for required assets
echo ""
echo "3️⃣ Checking for required assets..."
ASSET_COUNT=$(git ls-tree origin/gh-pages -r --name-only | grep "_codex_/cognitive_app/assets" | wc -l)
echo "  - Total assets: $ASSET_COUNT"

if [ $ASSET_COUNT -lt 10 ]; then
    echo "  ❌ Too few assets, deployment may be incomplete"
elif [ $ASSET_COUNT -gt 100 ]; then
    echo "  ⚠️ Many assets, may need optimization"
else
    echo "  ✅ Asset count looks normal"
fi

# 4. Check for source maps
HAS_SOURCEMAPS=$(git ls-tree origin/gh-pages -r --name-only | grep "\.map" | wc -l)
if [ $HAS_SOURCEMAPS -gt 0 ]; then
    echo "  ⚠️ Source maps found ($HAS_SOURCEMAPS), should be removed for prod"
else
    echo "  ✅ No source maps (correct for production)"
fi

# 5. Test asset URLs
echo ""
echo "4️⃣ Testing asset accessibility..."
SITE_URL="https://aries-serpent.github.io"
APP_PATH="/_codex_/cognitive_app"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE_URL$APP_PATH/index.html")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ index.html accessible (HTTP $HTTP_CODE)"
else
    echo "  ❌ index.html not accessible (HTTP $HTTP_CODE)"
fi

echo ""
echo "✅ Quarterly validation complete"
```

### Validation Report

After running the validation, complete this template:

```markdown
# Quarterly Asset Validation Report - Q3 2026

**Date**: 2026-07-15  
**Reviewed by**: @reviewer  
**Deployed Version**: v0.1.2  
**Build Date**: 2026-07-13

## Deployment Structure
- [x] index.html exists at `_codex_/cognitive_app/`
- [x] assets/ directory present
- [x] All expected files deployed

## File Integrity
- [x] index.html size: 8.2 KB (normal)
- [x] Total assets: 47 files (normal)
- [x] No source maps found (✓ correct)

## Accessibility
- [x] HTTP 200 on main page
- [x] All asset URLs return 200
- [x] No 404 errors detected

## Performance Metrics
- [x] Gzip compression: 240 KB → 62 KB
- [x] Page load time: < 2s
- [x] No bandwidth issues

## Issues Found
- None

## Actions Required
- None

## Next Quarterly Review
- 2026-10-15

## Sign-off
- Reviewed: @reviewer
- Approved: @manager
```

---

## Annual Tasks

### Yearly Security Audit

**Time Required**: 4 hours  
**Owners**: Security Team + DevOps Team  
**Schedule**: January 15-31 (or after Q1 deployment)

### Annual Security Audit Checklist

```bash
#!/bin/bash
# Annual security audit for cognitive app

echo "🔒 Starting annual security audit..."
date

# 1. Dependency vulnerability scan
echo ""
echo "1️⃣ Scanning dependencies for vulnerabilities..."
cd cognitive_app
npm audit --production

VULN_COUNT=$(npm audit --production --json | jq '.metadata.vulnerabilities.total')
if [ "$VULN_COUNT" -eq 0 ]; then
    echo "  ✅ No vulnerabilities found"
else
    echo "  ⚠️ $VULN_COUNT vulnerabilities found"
    npm audit fix
fi

# 2. Check for outdated packages
echo ""
echo "2️⃣ Checking for outdated packages..."
npm outdated | grep -v "current"
OUTDATED=$(npm outdated | grep -v "current" | wc -l)
echo "  $OUTDATED packages have updates available"

# 3. Check source for secrets
echo ""
echo "3️⃣ Scanning source code for secrets..."
cd ..
# Using truffleHog or similar
echo "  Checking for hardcoded credentials..."
grep -r "password\|secret\|token\|key" src/cognit* --include="*.tsx" --include="*.ts" \
  | grep -v "localStorage\|sessionStorage\|const\|comment" || echo "  ✅ No obvious secrets found"

# 4. Review build configuration
echo ""
echo "4️⃣ Auditing build configuration..."
cd cognitive_app

# Check source maps are removed
SOURCEMAPS=$(grep -r "\.map" dist/ 2>/dev/null | wc -l)
if [ "$SOURCEMAPS" -eq 0 ]; then
    echo "  ✅ No source maps in production build"
else
    echo "  ❌ $SOURCEMAPS source maps found (should remove)"
fi

# Check for eval() usage
EVAL_USAGE=$(grep -r "eval(" src/ --include="*.tsx" --include="*.ts" | wc -l)
if [ "$EVAL_USAGE" -eq 0 ]; then
    echo "  ✅ No eval() usage found"
else
    echo "  ⚠️ $EVAL_USAGE uses of eval() found (potential security risk)"
fi

# 5. Review GitHub Actions secrets
echo ""
echo "5️⃣ Checking GitHub Actions secrets..."
echo "  Verify secrets are not logged:"
grep -r "secrets\." .github/workflows/ | grep -i "echo\|print" && echo "    ❌ Secrets may be logged" || echo "    ✅ No secrets in logs"

# 6. Check deployment encryption
echo ""
echo "6️⃣ Verifying HTTPS deployment..."
HTTPS_STATUS=$(curl -I https://aries-serpent.github.io/_codex_/cognitive_app/ 2>/dev/null | grep -i "https\|ssl")
if [ -n "$HTTPS_STATUS" ]; then
    echo "  ✅ HTTPS enabled"
else
    echo "  ❌ HTTPS may not be enabled"
fi

echo ""
echo "✅ Annual security audit complete"
date
```

### Annual Security Audit Report

```markdown
# Annual Security Audit Report - 2026

**Date**: 2026-01-15  
**Audited by**: @security-team  
**Scope**: Cognitive App v0.1.2

## Executive Summary
- **Status**: ✅ PASS
- **Vulnerabilities Found**: 0
- **Critical Issues**: 0
- **Recommendations**: 3

## Detailed Findings

### 1. Dependency Security
- [x] npm audit passed (0 vulnerabilities)
- [x] All dependencies current
- [x] No abandoned dependencies
- [x] License compliance verified

**Outdated packages**: 12 (all minor/patch updates, can be applied)

### 2. Source Code Security
- [x] No hardcoded secrets found
- [x] No eval() usage
- [x] No XSS vulnerabilities detected
- [x] CSRF protection in place

### 3. Build Security
- [x] Source maps removed in production
- [x] No debug information exposed
- [x] Environment variables not hardcoded
- [x] Build process verifiable

### 4. Deployment Security
- [x] HTTPS enforced
- [x] Security headers present
- [x] GitHub Pages protection enabled
- [x] Branch protection enabled

### 5. Third-party Components
- [x] Spark component library audit passed
- [x] Radix UI components secure
- [x] No malicious dependencies detected

## Recommendations

### Priority 1 (Implement ASAP)
1. Update TypeScript to 5.7.3 (security fix)
   - Estimated time: 1 hour
   - Risk: Low
   - Testing: Unit + E2E

### Priority 2 (Within 30 Days)
1. Update all dependencies to latest
   - Estimated time: 2 hours
   - Risk: Medium
   - Testing: Full regression

2. Add Content Security Policy (CSP) headers
   - Estimated time: 4 hours
   - Risk: Low
   - Testing: Manual verification

### Priority 3 (Q2 2026)
1. Implement subresource integrity (SRI)
   - Estimated time: 3 hours
   - Risk: Low
   - Testing: Browser compatibility

## Testing Summary

| Area | Status | Notes |
|------|--------|-------|
| Static analysis | ✅ PASS | No issues |
| Dependency audit | ✅ PASS | 0 vulnerabilities |
| Code review | ✅ PASS | No security issues |
| Deployment | ✅ PASS | HTTPS, auth enabled |

## Approval

- **Reviewed by**: @security-lead
- **Approved by**: @ciso
- **Date**: 2026-01-15
- **Next Review**: 2027-01-15

## Attachments
- audit-report.json
- dependency-audit.json
- build-analysis.md
```

---

## Automated Maintenance Scripts

### Weekly Summary Script

```bash
#!/bin/bash
# weekly-maintenance-summary.sh

echo "📊 Weekly Maintenance Summary"
echo "Generated: $(date)"
echo ""

# 1. Workflow health
echo "Workflow Status (Last 7 Days)"
gh run list --workflow pages-mkdocs.yml --limit 10 \
  --json conclusion,createdAt,durationMinutes \
  --template='{{range .}}{{.conclusion}} - {{.durationMinutes}}min ({{.createdAt}}){{"\n"}}{{end}}'

# 2. Build metrics
echo ""
echo "Recent Build Metrics"
gh run list --workflow pages-mkdocs.yml --limit 1 \
  --json status,durationMinutes,conclusion

# 3. Deployment check
echo ""
echo "Current Deployment Status"
curl -s -I https://aries-serpent.github.io/_codex_/cognitive_app/ \
  | grep -E "HTTP|Content-Length|Last-Modified"

# 4. Security status
echo ""
echo "Security Status"
cd cognitive_app
npm audit --production --json 2>/dev/null | jq '.metadata.vulnerabilities' || echo "Unable to check"

echo ""
echo "✅ Summary complete"
```

### Monthly Report Generator

```bash
#!/bin/bash
# monthly-maintenance-report.sh

MONTH=$(date +"%B %Y")
REPORT_FILE="MAINTENANCE_REPORT_$(date +%Y-%m).md"

cat > "$REPORT_FILE" << 'EOF'
# Maintenance Report - {{MONTH}}

**Generated**: {{DATE}}  
**Period**: {{MONTH}}

## Executive Summary

- Total maintenance hours: TBD
- Issues found: TBD
- Issues resolved: TBD
- Uptime: TBD

## Monthly Reviews

### Workflow Review
- Executed: {{DATE}}
- Status: {{STATUS}}
- Next review: {{NEXT_DATE}}

### Asset Validation
- Due: {{Q_DATE}}
- Status: Scheduled

### Security Audit
- Due: Q{{QUARTER}}
- Status: Scheduled

## Metrics

### Build Performance
- Average build time: TBD
- Success rate: TBD
- Failure rate: TBD

### Deployment Success
- Deployments: TBD
- Successes: TBD
- Failures: TBD

## Issues and Resolutions

### This Month
- None

### Previous Month
- None

## Recommendations

- None at this time

## Sign-off

- Reviewed by: TBD
- Approved by: TBD
- Date: {{DATE}}
EOF

echo "Report generated: $REPORT_FILE"
```

---

## Maintenance Calendar

```
2026 MAINTENANCE CALENDAR

JANUARY
┌─────────────────────────────────┐
│ 1-15: Annual Security Audit     │
│ (REQUIRED)                      │
└─────────────────────────────────┘

FEBRUARY
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

MARCH
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ 15-31: Q1 Asset Validation      │
│ (REQUIRED)                      │
└─────────────────────────────────┘

APRIL
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ 15-30: Q2 Asset Validation      │
│ (REQUIRED)                      │
└─────────────────────────────────┘

MAY
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

JUNE
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

JULY
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ 15-31: Q3 Asset Validation      │
│ (REQUIRED)                      │
└─────────────────────────────────┘

AUGUST
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

SEPTEMBER
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

OCTOBER
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ 15-31: Q4 Asset Validation      │
│ (REQUIRED)                      │
└─────────────────────────────────┘

NOVEMBER
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ (Monthly task)                  │
└─────────────────────────────────┘

DECEMBER
┌─────────────────────────────────┐
│ First Monday: Workflow Review   │
│ Year-end: Prepare for Jan audit │
│ (Monthly + Planning)            │
└─────────────────────────────────┘
```

---

## Incident Response

If issues are found during maintenance:

### Severity Levels

| Level | Response Time | Example |
|-------|---------------|---------|
| **Critical** | < 1 hour | Site down, data loss |
| **High** | < 4 hours | Features broken |
| **Medium** | < 1 day | Performance degradation |
| **Low** | < 1 week | Minor UI issues |

### Incident Procedure

```bash
#!/bin/bash
# incident-response.sh

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
SEVERITY=$1

echo "🚨 Creating incident: $INCIDENT_ID"

# 1. Create incident log
cat > "incidents/$INCIDENT_ID.md" << EOF
# Incident Report: $INCIDENT_ID

**Date**: $(date)
**Severity**: $SEVERITY
**Status**: Open

## Description
[What happened]

## Impact
[Who/what affected]

## Root Cause
[Investigation findings]

## Resolution
[Steps taken]

## Prevention
[How to prevent future]
EOF

# 2. Notify team
echo "📧 Notifying team..."
# TODO: Add notification logic

# 3. Start resolution
echo "⏱️ Incident timer started"
echo "Incident: $INCIDENT_ID"
echo "Expected resolution: $(date -d '+1 hour')"
```

---

## Support and Escalation

### Points of Contact

| Issue Type | Contact | Response Time |
|-----------|---------|----------------|
| Build failure | @devops-team | 1 hour |
| Security issue | @security-team | 30 min |
| Performance | @platform-team | 4 hours |
| General question | @dev-team | 24 hours |

### Escalation Path

```
Issue Found
    ↓
Team investigates (1 hour)
    ↓
Can fix? 
├─ YES → Fix & Test & Deploy
│        ↓
│        Update logs & close
│
└─ NO → Escalate to manager
         ↓
         Schedule meeting
         ↓
         Plan resolution
         ↓
         Execute
```

---

**Last Updated**: 2026-07-20  
**Maintainer**: DevOps Team  
**Status**: Production Ready
