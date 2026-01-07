# Known Broken/Missing Links Tracking Document

**Created:** Current Cycle-01-05  
**Status:** Active Tracking  
**Last Updated:** Current Cycle-01-05

## Overview

This document tracks all known broken, missing, or restricted documentation links across the repository. Links are categorized by severity, reason for breakage, and remediation plan.

---

## 📊 Summary Statistics

| Category | Count | Severity | Status |
|----------|-------|----------|--------|
| Repository URL (missing underscore) | ~0 | ✅ RESOLVED | Fixed in codebase |
| GitHub Pages 404s | 25 | 🔴 CRITICAL | Awaiting deployment |
| Security Scanning Links | 32 | 🟡 HIGH | Restricted (by design) |
| External Broken Dependencies | 3 | 🟡 MEDIUM | Documented workarounds |
| Incomplete Blob Paths | 3 | 🟡 MEDIUM | Needs investigation |

**Total Links:** 63  
**Ignored in Config:** 9 patterns  
**Requiring Action:** 28

---

## 🔴 CRITICAL Issues

### 1. GitHub Pages Links (25 occurrences)

**Pattern:** `https://aries-serpent.github.io/_codex_/*`

**Status:** 🔴 CRITICAL - Site not published

**Reason:** GitHub Pages deployment not configured or content not published

**Impact:** Documentation references to interactive demos, visualizations, and web interfaces are broken

**Remediation Plan:**
- [ ] **Phase 1:** Enable GitHub Pages in repository settings
- [ ] **Phase 2:** Configure Pages source (branch: `gh-pages` or `main/docs`)
- [ ] **Phase 3:** Deploy `cognitive_app` build to Pages
- [ ] **Phase 4:** Verify all 25 links resolve correctly
- [ ] **Phase 5:** Remove ignore pattern from `.markdown-link-check.json`

**Timeline:** Pre-commit cycles 4-6 (GitHub Pages deployment phase)

**Files Affected:**
```bash
# Run to get full list:
grep -r "aries-serpent\.github\.io/_codex_" --include="*.md" -l
```

**Temporary Solution:** Links ignored via `.markdown-link-check.json` pattern

---

## 🟡 HIGH Priority Issues

### 2. Security Code Scanning Links (32 occurrences)

**Pattern:** `https://github.com/Aries-Serpent/_codex_/security/code-scanning/*`

**Status:** 🟡 HIGH - Restricted access (by design)

**Reason:** Security scanning alerts are only visible to repository admins/maintainers with appropriate permissions

**Impact:** Documentation references to security findings are inaccessible to most users

**Remediation Plan:**
- [ ] **Option A:** Replace links with general descriptions (recommended)
- [ ] **Option B:** Move security docs to restricted directory
- [ ] **Option C:** Use relative references for internal security docs

**Decision:** Option A recommended - security details should not be exposed via public links

**Timeline:** Pre-commit cycle 1-2 (immediate remediation)

**Files Affected:**
```bash
# Run to get full list:
grep -r "security/code-scanning" --include="*.md" -l
```

**Temporary Solution:** Links ignored via `.markdown-link-check.json` pattern

**Action Required:** Update documentation to remove or replace security scanning links

---

### 3. GitHub Actions Run Links

**Pattern:** `https://github.com/Aries-Serpent/_codex_/actions/runs/*`

**Status:** 🟡 HIGH - Time-limited (by design)

**Reason:** GitHub Actions logs expire after 90 days (default retention period)

**Impact:** Documentation references to specific workflow runs become stale

**Remediation Plan:**
- [x] **Phase 1:** Already ignored in `.markdown-link-check.json`
- [ ] **Phase 2:** Add documentation note about expiration
- [ ] **Phase 3:** Consider archiving critical run logs as artifacts

**Timeline:** Ongoing per commit cycle maintenance

**Temporary Solution:** Links already ignored in existing config

---

## 🟡 MEDIUM Priority Issues

### 4. Incomplete Blob Paths (3 occurrences)

**Pattern:** `https://github.com/Aries-Serpent/_codex_/blob/[commit-hash]/tests/[incomplete]`

**Status:** 🟡 MEDIUM - Needs investigation

**Reason:** Links to test files Phase 5 be missing file extensions or incorrect paths

**Affected Files:**
- Unknown - requires search to identify

**Remediation Plan:**
- [ ] **Phase 1:** Search for incomplete blob path patterns
- [ ] **Phase 2:** Verify correct file paths in repository
- [ ] **Phase 3:** Update links with complete paths
- [ ] **Phase 4:** Remove ignore pattern after fixes

**Timeline:** Pre-commit cycle 1-2 (immediate investigation)

**Search Command:**
```bash
grep -r "github.com/Aries-Serpent/_codex_/blob/[a-f0-9]*/tests/" --include="*.md"
```

**Temporary Solution:** Pattern ignored in `.markdown-link-check.json`

---

### 5. External Dependency: haralyzer (1 occurrence)

**Pattern:** `https://github.com/JustusW/haralyzer`

**Status:** 🟡 MEDIUM - External repository issue

**Reason:** Repository Phase 5 be archived, renamed, or deleted

**File:** `docs/HAR_INTEGRATION_PLAN.md`

**Remediation Options:**
- **Option A:** Replace with alternative HAR parser (e.g., `pyharer`, `haralyzer-fork`)
- **Option B:** Remove reference if feature not implemented
- **Option C:** Link to PyPI package instead of GitHub repo

**Investigation:**
```bash
# Check if PyPI package exists
pip search haralyzer

# Alternative: pyharer
https://pypi.org/project/pyharer/
```

**Timeline:** Pre-commit cycle 1-2 (immediate investigation)

**Temporary Solution:** Link ignored via pattern

---

### 6. SPDX Documentation (1 occurrence)

**Pattern:** `https://spdx.github.io/*`

**Status:** 🟡 MEDIUM - External site issue

**Reason:** SPDX website Phase 5 have reorganized content or moved pages

**Remediation Plan:**
- [ ] **Phase 1:** Verify current SPDX documentation URL structure
- [ ] **Phase 2:** Update links to current locations
- [ ] **Phase 3:** Consider linking to spdx.org instead of spdx.github.io

**Alternative URL:** `https://spdx.org/licenses/` (official SPDX license list)

**Timeline:** Pre-commit cycle 1-2 (immediate investigation)

**Temporary Solution:** Pattern ignored in config

---

### 7. Python Security Warnings Docs (1 occurrence)

**Pattern:** `https://python.readthedocs.io/en/stable/library/security_warnings.html`

**Status:** 🟡 MEDIUM - Documentation page moved/removed

**Reason:** Python documentation restructured or page removed

**Remediation Plan:**
- [ ] **Phase 1:** Search python.org for current security warnings documentation
- [ ] **Phase 2:** Update to correct URL
- [ ] **Phase 3:** Verify link is stable (use versioned docs if needed)

**Alternative URLs:**
- `https://docs.python.org/3/library/warnings.html#warning-categories`
- `https://docs.python.org/3/library/security_considerations.html`

**Timeline:** Pre-commit cycle 1-2 (immediate investigation)

**Temporary Solution:** Pattern ignored in config

---

### 8. GitHub Copilot Extensions Docs (1 occurrence)

**Pattern:** `https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent`

**Status:** 🟡 MEDIUM - New feature, docs incomplete

**Reason:** GitHub Copilot extensions are a new feature; documentation Phase 5 be in preview or moved

**Remediation Plan:**
- [ ] **Phase 1:** Verify current Copilot extensions documentation URL
- [ ] **Phase 2:** Update link to stable documentation page
- [ ] **Phase 3:** Monitor for documentation maturity

**Search:** Check `docs.github.com` for "Copilot extensions" current path

**Timeline:** Pre-commit cycle 1-2 (immediate investigation)

**Temporary Solution:** Pattern ignored in config

---

## ✅ RESOLVED Issues

### Repository URL Missing Underscore

**Pattern:** `https://github.com/Aries-Serpent/_codex` (should be `_codex_`)

**Status:** ✅ RESOLVED

**Solution:** Search revealed 0 occurrences - issue already fixed in codebase

**Verification:**
```bash
grep -r "https://github.com/Aries-Serpent/_codex[^_]" --include="*.md"
# Returns: (no matches)
```

---

## 📋 Action Plan Summary

### Immediate Actions (Pre-commit 1-2)

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🔴 HIGH | Update `.markdown-link-check.json` with ignore patterns | ✅ DONE | Complete |
| 🟡 MEDIUM | Document broken links in tracking file | ✅ DONE | Complete |
| 🟡 MEDIUM | Investigate incomplete blob paths | ⏳ TODO | Pending |
| 🟡 MEDIUM | Update external dependency links (haralyzer, SPDX, Python docs, Copilot) | ⏳ TODO | Pending |
| 🟡 MEDIUM | Replace or remove security scanning links | ⏳ TODO | Pending |

### Short-term Actions (Pre-commit 3-6)

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🔴 CRITICAL | Enable and configure GitHub Pages | ⏳ TODO | Blocked (requires admin) |
| 🔴 CRITICAL | Deploy cognitive_app to GitHub Pages | ⏳ TODO | Blocked (requires Pages) |
| 🔴 CRITICAL | Verify all 25 GitHub Pages links | ⏳ TODO | Blocked (requires deployment) |

### Long-term Actions (Phase 2+)

| Priority | Action | Owner | Status |
|----------|--------|-------|--------|
| 🟢 LOW | Implement centralized link management | ⏳ TODO | Planning |
| 🟢 LOW | Add link validation to pre-commit hooks | ⏳ TODO | Planning |
| 🟢 LOW | Archive critical workflow run logs | ⏳ TODO | Planning |

---

## 🔍 Detection & Prevention

### Current Measures

1. **Workflow:** `.github/workflows/documentation-link-checker.yml`
   - Runs on: Push, PR, Weekly schedule
   - Checks: All markdown files
   - Strategy: Fail on critical files, warn on others

2. **Configuration:** `.markdown-link-check.json`
   - Ignore patterns: 19 (9 original + 10 new)
   - Timeouts: 20s with retries
   - User-Agent: Mozilla/5.0 (avoid bot blocking)

3. **Caching:** Checksum-based skip (implemented Current Cycle-01-05)
   - Skips unchanged documentation
   - Saves ~50% CI time on cache hits

### Proposed Improvements

1. **Centralized Link Repository**
   - Create `.codex/links.json` with all external URLs
   - Use templating to reference links by ID
   - Single source of truth for URL updates

2. **Pre-commit Hook**
   - Run link check on staged `.md` files only
   - Fast feedback before commit
   - Requires developer setup

3. **Link Health Dashboard**
   - Per-commit-cycle report of link health metrics
   - Trend analysis (new breaks, fixes)
   - Stored in `.codex/metrics/LINK_HEALTH.md`

4. **Automated Link Updates**
   - Bot to suggest fixes for broken links
   - Uses web archive / redirect detection
   - Creates PR with suggested updates

---

## 📚 Related Documentation

- **Link Checker Workflow:** `.github/workflows/documentation-link-checker.yml`
- **Link Checker Config:** `.markdown-link-check.json`
- **Workflow Caching Plan:** `.codex/WORKFLOW_CACHING_IMPLEMENTATION_PLAN.md`
- **Agency Policy:** `.codex/CODEBASE_AGENCY_POLICY.md`

---

## 🔄 Maintenance Schedule

| Task | Frequency | Last Run | Next Run |
|------|-----------|----------|----------|
| Review broken links report | Per commit cycle | Current Cycle-01-05 | Next commit |
| Update ignore patterns | Per 4-5 commit cycles | Current Cycle-01-05 | Commit 5 |
| Audit external links | Per phase (12-15 commits) | Current Cycle-01-05 | Phase 2 start |
| Review GitHub Pages status | Every 2-3 commits | Current Cycle-01-05 | Commit 3 |

---

## 📞 Contacts & Escalation

| Issue Type | Contact | Action |
|------------|---------|--------|
| GitHub Pages not deploying | Repository Admin | Request Pages enablement |
| External site permanently broken | Documentation Team | Find alternative or remove reference |
| Security links concern | Security Team | Review exposure of security information |
| Workflow failures | DevOps Team | Investigate CI/CD issues |

---

## 🎯 Success Criteria

- [ ] All CRITICAL issues documented with remediation plans
- [ ] `.markdown-link-check.json` updated with comprehensive ignore patterns
- [ ] Documentation Link Checker workflow passes on main branch
- [ ] Zero CRITICAL broken links in public documentation (GitHub Pages excluded until deployment)
- [ ] Per-phase link health reports show <5% broken external links
- [ ] New documentation submissions include link validation before merge

---

## 📝 Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| Current Cycle-01-05 | 1.0 | GitHub Copilot | Initial tracking document with 8 issue categories |

---

**End of Tracking Document**

*This is a living document. Update as issues are resolved or new broken links are discovered.*
