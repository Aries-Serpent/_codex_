# GitHub Pages Status Dashboard

> **Last Updated**: 2026-04-06T20:30:00Z
> **Updated by**: Copilot Coding Agent — Session S304 (PR #3901)
> **Deployment**: MkDocs Material — sole authorised deployer

## 🚀 Deployment Status

| Metric | Status | Details |
|--------|--------|---------|
| **Build Status** | ![Build](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-mkdocs.yml/badge.svg) | Latest deployment |
| **Site Status** | ✅ LIVE | https://aries-serpent.github.io/_codex_/ |
| **Last Deploy** | Check workflow | [Latest run](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-mkdocs.yml) |
| **Sole Deployer** | ✅ MkDocs only | `unified-deployment.yml` Pages job removed 2026-03-14 |
| **Theme** | Material with Dark Mode | ✅ Toggle enabled |
| **Cache Hit Rate** | Monitor in workflow | MkDocs plugins cached |
| **Jekyll suppressed** | ✅ `.nojekyll` present | `docs/_config.yml` disabled; `_layouts/` disabled |
| **Cost Dashboard** | ✅ LIVE | [💰 Cost Estimator Dashboard](../ops/cost-dashboard.md) |
| **Pre-Merge Validation** | ![Validation](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-pre-merge-validation.yml/badge.svg) | Blocks merge on errors |
| **Scheduled Validation** | ![Scheduled](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-scheduled-validation.yml/badge.svg) | Daily + weekly deep scan |

## 📊 Documentation Health

| Area | Status | Notes |
|------|--------|-------|
| **Theme Configuration** | ✅ CURRENT | Dark/light/auto mode toggle — 3-way |
| **Navigation** | ✅ COMPLETE | All pages accessible via nav |
| **cognitive_app** | ✅ LIVE | vite bumped 7.2.6→7.3.2 + esbuild 0.25.12→0.27.7 (PR #3901/S304) |
| **README.md conflict** | ✅ FIXED | `exclude_docs: README.md _config.yml _layouts/` in mkdocs.yml |
| **MkDocs Warnings** | ⚠️ 1 REMAINING | Mermaid CDN URL check (network-only, non-blocking) |
| **Search** | ✅ ENABLED | Search with suggestions |
| **Code Blocks** | ✅ ENHANCED | Copy button enabled |
| **Markdown Extensions** | ✅ FULL | Mermaid, tabs, task lists |
| **Link Validation** | 🔄 AUTOMATED | Pre-merge + scheduled checks |
| **Auto-Remediation** | ✅ ENABLED | Issues/PRs created automatically |
| **yamllint gate** | ✅ FIXED | `[colons]` error-level violations removed from `auto-approve-workflows.yml` (S304) |
| **sync-tracked-files** | ✅ FIXED | `.secrets.baseline` CODEX_MANIFEST entry re-synced (S304) |

## 📋 Recent Validation (2026-04-06T20:18Z)

| Check | Status | Notes |
|-------|--------|-------|
| `ruff check src/ tests/` | ✅ 0 violations | No regressions post PR #3897 merge |
| `mypy_baseline.py --require-baseline` | ✅ 104 errors = baseline | No regressions |
| `.secrets.baseline` | ✅ 6 pre-existing | No new flags; CODEX_MANIFEST hash re-synced |
| `yamllint .github/workflows/ .github/misc/` | ✅ Exit 0 | Colons error-level violations fixed |
| `sync_tracked_files.py --check` | ✅ All consistent | Stale `.secrets.baseline` hash repaired |
| E→D Transition Readiness | ✅ 5/5 | D_CAPABLE unlocked 🟢 |
| Branch Rebase Gate | ✅ Up-to-date | `0D_base_` is current with `main` |
| CI Monitor | ✅ Passing | Code Quality & Coverage Suite green |
| GitHub Pages Validation | ⚠️ Non-critical | Warnings only — no errors |

## 🔄 Recent Changes (S304 — 2026-04-06)

### PR #3901 — Post-Merge Hotfix Sweep (Session S304)
- ✅ `docs/ROADMAP.md` "Last Updated" bumped to 2026-04-06
- ✅ `AGENT_ACCOUNTABILITY_REPORT.md` updated with S304 session summary
- ✅ `CHANGELOG.md` updated with S304 entry
- ✅ `.github/copilot-prompts/active/PR-3901-followup.md` — duplicate PR ref fixed; "Files Modified" corrected
- ✅ `cognitive_app/package.json` — vite bumped `^7.2.6` → `^7.3.2` (closes PR #3902)
- ✅ `cognitive_app/package-lock.json` — esbuild `0.25.12` → `0.27.7` + vite `7.2.6` → `7.3.2` (27 packages)
- ✅ `.github/workflows/auto-approve-workflows.yml` — `[colons]` yamllint error-level violations fixed
- ✅ `CODEX_MANIFEST.json` + `.secrets.baseline` CODEX_MANIFEST entry re-synced (P22 drift)
- ✅ `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` impact score corrected to 7 files

### PR #3897 — Merged 2026-04-06 (Session S302/S303)
- ✅ `auto-approve-workflows.yml` — schedule `*/20 * * * *` sweep + `wec:auto-approve-once` one-session label
- ✅ `wec_enforcer.py` — HTTP-204 fix for `workflow_dispatch` empty body (line 87)
- ✅ E→D Transition Readiness: 5/5 gates passed

### 2026-03-14: MkDocs-only deployment enforced + Cost Dashboard (PR #3575 Session 27)
- ✅ `unified-deployment.yml` competing Pages deploy job removed
- ✅ `docs/_config.yml` and `_layouts/` disabled (Jekyll suppression)
- ✅ `docs/.nojekyll` added
- ✅ **Cost Estimator Dashboard** live at [`/ops/cost-dashboard/`](../ops/cost-dashboard.md)
- ✅ `pages-mkdocs.yml` updated: cost-data generation step
- ✅ `pr-cost-check.yml` created — T-003 required status check workflow

## 🎨 Theme Features

### Dark/Light Mode Toggle
✅ **Enabled** — Three-way toggle:
- 🌓 Auto (system preference)
- ☀️ Light mode
- 🌙 Dark mode

### Navigation Features
- ✅ Instant loading (XHR)
- ✅ URL tracking
- ✅ Top-level tabs
- ✅ Section grouping
- ✅ Expand/collapse
- ✅ Back to top button

### Content Features
- ✅ Search with suggestions
- ✅ Syntax highlighting
- ✅ Code copy button
- ✅ Mermaid diagrams
- ✅ Tabbed content
- ✅ Task lists

## 🔗 Quick Links

- [📖 Production Site](https://aries-serpent.github.io/_codex_/)
- [💰 Cost Estimator Dashboard](https://aries-serpent.github.io/_codex_/ops/cost-dashboard/)
- [⚙️ Workflow Configuration](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/pages-mkdocs.yml)
- [📝 Documentation Source](https://github.com/Aries-Serpent/_codex_/tree/main/docs)
- [🎨 Theme Config](https://github.com/Aries-Serpent/_codex_/blob/main/mkdocs.yml)
- [💼 Cost Governance Policy](../ops/COST_GOVERNANCE.md)
- [🤖 GitHub Pages Manager Agent](https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/github-pages-manager.md)
- [📊 CI Triage Report](https://github.com/Aries-Serpent/_codex_/issues/3875)

## 📋 Documentation Checklist

### Theme & Configuration
- [x] Enable dark mode toggle
- [x] Configure Material theme features
- [x] Add enhanced markdown extensions
- [x] Test theme on multiple devices
- [ ] Add theme customization (colors, fonts)
- [ ] Create dark mode screenshots

### Content & Quality
- [x] Create link validation script
- [x] Set up pre-merge validation
- [x] Set up scheduled validation
- [x] Run comprehensive link validation
- [ ] Check for stale documentation (>30 iterations old)
- [x] Validate all navigation entries
- [ ] Test search functionality
- [ ] Add missing API documentation
- [ ] Create interactive tutorials

### Deployment & Monitoring
- [x] Set up automated link checking
- [x] Configure deployment notifications (via issues)
- [ ] Monitor build performance
- [ ] Track documentation freshness
- [x] Implement automated fixes for common issues

### cognitive_app Integration
- [x] Validate cognitive_app documentation exists
- [x] Verify cognitive_app in navigation
- [x] Check cognitive_app source files
- [x] Automated accessibility checks
- [x] vite + esbuild security-patched (7.3.2 / 0.27.7) — S304
- [ ] Monitor cognitive_app build status

### CI Gate Health
- [x] yamllint — all error-level violations resolved (S304)
- [x] sync-tracked-files — `.secrets.baseline` CODEX_MANIFEST hash consistent (S304)
- [x] ruff — 0 violations (S304)
- [x] mypy baseline — 104 = baseline (S304)
- [x] detect-secrets — 6 pre-existing, no new flags (S304)

## 🎯 Continuation Prompts

```
@copilot Use github-pages-manager to check if deployed documentation matches source files
```

```
@copilot Use github-pages-manager to find and fix broken links in documentation
```

```
@copilot Use github-pages-manager to update the status dashboard with latest metrics
```

## 📈 Metrics to Track

### Deployment Metrics
- Build success rate (target: >99%)
- Build duration (target: <5min)
- Deployment frequency (daily)
- Cache hit rate (target: >80%)

### Content Metrics
- Link validity (target: >98%)
- Content freshness (target: >95%)
- Documentation sync (target: 100%)
- Navigation coverage (target: 100%)

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `mkdocs.yml` | Theme, features, extensions, navigation |
| `.github/workflows/pages-mkdocs.yml` | Deployment workflow |
| `.github/workflows/pages-pre-merge-validation.yml` | Pre-merge link + build validation |
| `.github/workflows/pages-scheduled-validation.yml` | Daily/weekly deep scan |
| `.github/agents/github-pages-manager.md` | Agent spec |
| `scripts/validate_docs_links.py` | Link validation script |

## 🐛 Known Issues & Patterns

| Pattern | Status | Notes |
|---------|--------|-------|
| Mermaid CDN URL check | ⚠️ Non-blocking | Network-only check; not a code failure |
| yamllint `[truthy]` / `[line-length]` | ✅ Warnings only | `.yamllint.yml` sets these to `warning` level — exit 0 |
| `detect-secrets` P23 plugin mismatch | ✅ Documented | `auto_fix_common_issues.py --pattern 23` |
| `sync-tracked-files` P22 drift | ✅ Auto-repaired | Run `sync_tracked_files.py --fix` after CODEX_MANIFEST changes |

## 📞 Support

- **Agent Issues**: `@copilot` activate github-pages-manager agent
- **Theme Problems**: [MkDocs Material docs](https://squidfunk.github.io/mkdocs-material/)
- **Deployment Failures**: [GitHub Actions logs](https://github.com/Aries-Serpent/_codex_/actions)
- **CI Triage**: [Issue #3875](https://github.com/Aries-Serpent/_codex_/issues/3875)
- **General Questions**: Contact @mbaetiong

---

**Dashboard Version**: 2.0.0
**Agent**: Copilot Coding Agent — S304 (PR #3901)
**Last Updated**: 2026-04-06T20:30:00Z
**Auto-Update**: Scheduled daily via `pages-scheduled-validation.yml`

## 🚀 Deployment Status

| Metric | Status | Details |
|--------|--------|---------|
| **Build Status** | ![Build](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-mkdocs.yml/badge.svg) | Latest deployment |
| **Site Status** | ✅ LIVE | https://aries-serpent.github.io/_codex_/ |
| **Last Deploy** | Check workflow | [Latest run](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-mkdocs.yml) |
| **Sole Deployer** | ✅ MkDocs only | `unified-deployment.yml` Pages job removed 2026-03-14 |
| **Theme** | Material with Dark Mode | ✅ Toggle enabled |
| **Cache Hit Rate** | Monitor in workflow | MkDocs plugins cached |
| **Jekyll suppressed** | ✅ `.nojekyll` present | `docs/_config.yml` disabled; `_layouts/` disabled |
| **Cost Dashboard** | ✅ LIVE | [💰 Cost Estimator Dashboard](../ops/cost-dashboard.md) |
| **Pre-Merge Validation** | ![Validation](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-pre-merge-validation.yml/badge.svg) | Blocks merge on errors |
| **Scheduled Validation** | ![Scheduled](https://github.com/Aries-Serpent/_codex_/actions/workflows/pages-scheduled-validation.yml/badge.svg) | Daily + weekly deep scan |

## 📊 Documentation Health

| Area | Status | Notes |
|------|--------|-------|
| **Theme Configuration** | ✅ UPDATED | Dark/light mode toggle enabled |
| **Navigation** | ✅ COMPLETE | All pages accessible via nav |
| **cognitive_app** | ✅ FIXED | Added to mkdocs.yml navigation (was missing) |
| **README.md conflict** | ✅ FIXED | `exclude_docs: README.md _config.yml _layouts/` in mkdocs.yml |
| **MkDocs Warnings** | ⚠️ 1 REMAINING | Mermaid CDN URL check (network-only, non-blocking) |
| **Search** | ✅ ENABLED | Search with suggestions |
| **Code Blocks** | ✅ ENHANCED | Copy button enabled |
| **Markdown Extensions** | ✅ FULL | Mermaid, tabs, task lists |
| **Link Validation** | 🔄 AUTOMATED | Pre-merge + scheduled checks |
| **Auto-Remediation** | ✅ ENABLED | Issues/PRs created automatically |

## 📋 Recent Validation (2026-02-25T01:47:12Z)

| Check | Before Fix | After Fix |
|-------|-----------|-----------|
| Link Validation | ✅ 0 errors | ✅ 0 errors |
| MkDocs Build Warnings | ⚠️ 2 warnings | ⚠️ 1 warning (mermaid CDN) |
| cognitive_app accessibility | ❌ 1 error | ✅ Fixed (added to nav) |

## 🎨 Theme Features

### Dark/Light Mode Toggle
✅ **Enabled** - Three-way toggle implemented:
- 🌓 Auto (system preference)
- ☀️ Light mode
- 🌙 Dark mode

### Navigation Features
- ✅ Instant loading (XHR)
- ✅ URL tracking
- ✅ Top-level tabs
- ✅ Section grouping
- ✅ Expand/collapse
- ✅ Back to top button

### Content Features
- ✅ Search with suggestions
- ✅ Syntax highlighting
- ✅ Code copy button
- ✅ Mermaid diagrams
- ✅ Tabbed content
- ✅ Task lists

## 🔗 Quick Links

- [📖 Production Site](https://aries-serpent.github.io/_codex_/)
- [💰 Cost Estimator Dashboard](https://aries-serpent.github.io/_codex_/ops/cost-dashboard/)
- [⚙️ Workflow Configuration](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/pages-mkdocs.yml)
- [📝 Documentation Source](https://github.com/Aries-Serpent/_codex_/tree/main/docs)
- [🎨 Theme Config](https://github.com/Aries-Serpent/_codex_/blob/main/mkdocs.yml)
- [💼 Cost Governance Policy](../ops/COST_GOVERNANCE.md)
- [🤖 GitHub Pages Manager Agent](https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/github-pages-manager.md)

## ✅ Recent Updates

### 2026-03-14: MkDocs-only deployment enforced + Cost Dashboard (PR #3575 Session 27)
- ✅ `unified-deployment.yml` competing Pages deploy job removed — MkDocs is now the **sole** Pages deployer
- ✅ `docs/_config.yml` disabled (Jekyll config was in the MkDocs source tree)
- ✅ `docs/_layouts/default.html` disabled (Jekyll layout stub)
- ✅ `docs/.nojekyll` added — belt-and-suspenders Jekyll suppression
- ✅ `mkdocs.yml` `exclude_docs` updated to exclude Jekyll artefacts
- ✅ `pages-static.yml.alt` hardened with "PERMANENTLY DISABLED" header
- ✅ **Cost Estimator Dashboard** live at [`/ops/cost-dashboard/`](../ops/cost-dashboard.md)
- ✅ `scripts/ci/generate_cost_dashboard_data.py` — generates `cost-data.json` at Pages build time via GitHub API
- ✅ `pages-mkdocs.yml` updated: cost-data generation step added before `mkdocs build`
- ✅ `pr-cost-check.yml` created — T-003 required status check workflow (`💰 PR Cost Check`)

### 2026-02-11: Evolution Center & Documentation Alignment
- ✅ Created Evolution Center (`docs/evolution/`) with 7 documents
- ✅ Added Evolution Timeline with verified phase statuses (Phases 1-18)
- ✅ Added Planset Registry (PS-01 → PS-10 queryable catalog)
- ✅ Added Cognitive Evolution Tree (4 Mermaid diagrams)
- ✅ Added AI Emergence Storyboard (biographical narrative)
- ✅ Added AI Agency Intuitiveness Score V3.0 (93.2/100, ACE-aligned 6-layer scoring)
- ✅ Added Cognitive Codebase Map (35 components scored for AI intuitiveness)
- ✅ Updated Roadmap — Phases 7-10 marked ✅ Complete (verified against codebase)
- ✅ Added Evolution Center to mkdocs.yml navigation (7 pages)
- ✅ Updated Cognitive Brain Index with evolution tracking links
- ✅ cognitive_app dashboard linked as human-visibility interface for AI agency

### 2026-02-10: Validation & Automation
- ✅ Created link validation script (`scripts/validate_docs_links.py`)
- ✅ Implemented pre-merge validation workflow
- ✅ Implemented scheduled validation workflow (daily + weekly)
- ✅ Auto-creates issues for documentation problems
- ✅ Validates cognitive_app accessibility
- ✅ Automated documentation sync checks

### 2026-02-10: Dark Mode Theme Implementation
- ✅ Added dark/light/auto mode toggle
- ✅ Enhanced navigation features (instant loading, tabs, sections)
- ✅ Improved search (suggestions, highlighting)
- ✅ Enhanced code blocks (copy button, annotations)
- ✅ Added advanced markdown extensions (mermaid, tabs, task lists)
- ✅ Created GitHub Pages Manager Agent
- ✅ Created status dashboard

## 📋 Documentation Checklist

### Theme & Configuration
- [x] Enable dark mode toggle
- [x] Configure Material theme features
- [x] Add enhanced markdown extensions
- [x] Test theme on multiple devices
- [ ] Add theme customization (colors, fonts)
- [ ] Create dark mode screenshots

### Content & Quality
- [x] Create link validation script
- [x] Set up pre-merge validation
- [x] Set up scheduled validation
- [ ] Run comprehensive link validation
- [ ] Check for stale documentation (>30 iterations old)
- [ ] Validate all navigation entries
- [ ] Test search functionality
- [ ] Add missing API documentation
- [ ] Create interactive tutorials

### Deployment & Monitoring
- [x] Set up automated link checking
- [x] Configure deployment notifications (via issues)
- [ ] Monitor build performance
- [ ] Track documentation freshness
- [x] Implement automated fixes for common issues

### cognitive_app Integration
- [x] Validate cognitive_app documentation exists
- [x] Verify cognitive_app in navigation
- [x] Check cognitive_app source files
- [x] Automated accessibility checks
- [ ] Test cognitive_app deployment
- [ ] Monitor cognitive_app build status

### Documentation Sync
- [x] Ensure all docs source from actual files (not copies)
- [x] Set up automated sync validation
- [ ] Configure rebuild triggers for source changes
- [ ] Monitor for documentation drift

## 🎯 Continuation Prompts

### Validate Documentation Sync
```
@copilot Use github-pages-manager to check if deployed documentation matches source files
```

### Check Link Integrity
```
@copilot Use github-pages-manager to find and fix broken links in documentation
```

### Verify Dark Mode
```
@copilot Use github-pages-manager to validate dark/light mode theme toggle is working
```

### Update Dashboard
```
@copilot Use github-pages-manager to update the status dashboard with latest metrics
```

### Run Full Health Check
```
@copilot Use github-pages-manager to run a comprehensive health check on GitHub Pages
```

## 📈 Metrics to Track

### Deployment Metrics
- Build success rate (target: >99%)
- Build duration (target: <5min)
- Deployment frequency (daily)
- Cache hit rate (target: >80%)

### Content Metrics
- Link validity (target: >98%)
- Content freshness (target: >95%)
- Documentation sync (target: 100%)
- Navigation coverage (target: 100%)

### User Experience Metrics
- Page load time (target: <2s)
- Search response time (target: <500ms)
- Mobile responsiveness (target: 100%)
- Theme functionality (target: 100%)

## 🔧 Configuration Files

### Primary Configuration
- **mkdocs.yml**: Main configuration file
  - Theme: Material with dark mode
  - Features: Navigation, search, code blocks
  - Extensions: Mermaid, tabs, task lists

### Workflow Configuration
- **.github/workflows/pages-mkdocs.yml**: Deployment workflow
  - Triggers: Push to main (docs changes)
  - Cache: MkDocs plugins and built site
  - Deployment: GitHub Pages (Actions)

### Agent Configuration
- **.github/agents/github-pages-manager.md**: Agent specification
  - Capabilities: Sync validation, theme management, link validation
  - Auto-fixes: Broken links, stale content, missing nav entries

## 💡 Best Practices

### Documentation Maintenance
1. **Source from actual files**: Always reference repository files, never copy content
2. **Keep navigation current**: Update mkdocs.yml nav when adding/moving files
3. **Validate links regularly**: Use automated link checking on every commit
4. **Monitor freshness**: Flag documentation older than 30 iterations
5. **Test theme changes**: Validate dark mode on desktop and mobile

### Deployment Workflow
1. **Use caching**: Enable MkDocs plugin and site caching
2. **Validate before deploy**: Run mkdocs build --strict locally
3. **Monitor builds**: Check GitHub Actions for failures
4. **Review logs**: Investigate warnings and errors
5. **Rollback if needed**: Keep deployment history for quick reverts

### Theme Customization
1. **Use theme features**: Prefer built-in features over custom CSS
2. **Test accessibility**: Ensure WCAG 2.1 AA compliance
3. **Optimize images**: Keep images under 500KB
4. **Test responsive**: Verify mobile and tablet layouts
5. **Document changes**: Update this dashboard after modifications

## 🐛 Troubleshooting

### Build Failures
1. Check workflow logs in GitHub Actions
2. Test build locally: `mkdocs build --verbose`
3. Validate mkdocs.yml syntax
4. Check for missing dependencies
5. Review recent commits for breaking changes

### Theme Issues
1. Clear browser cache
2. Verify Material theme version: `pip show mkdocs-material`
3. Check theme configuration in mkdocs.yml
4. Test in incognito/private browsing mode
5. Review browser console for JavaScript errors

### Link Issues
1. Run link validation: Use github-pages-manager agent
2. Check file existence for internal links
3. Verify external URLs return 200 status
4. Update navigation in mkdocs.yml
5. Re-build and deploy to test fixes

## 📞 Support

For issues or questions:
- **Agent Issues**: Use `@copilot` to activate github-pages-manager agent
- **Theme Problems**: Check [MkDocs Material documentation](https://squidfunk.github.io/mkdocs-material/)
- **Deployment Failures**: Review [GitHub Actions logs](https://github.com/Aries-Serpent/_codex_/actions)
- **General Questions**: Contact @mbaetiong

---

**Dashboard Version**: 1.0.0  
**Agent**: GitHub Pages Manager Agent v1.0.0  
**Last Manual Update**: 2026-02-10  
**Auto-Update**: Scheduled daily

## 🤖 Automated Validation

### Pre-Merge Validation
**Workflow:** `.github/workflows/pages-pre-merge-validation.yml`

Runs automatically on PRs that modify:
- `docs/**` - Documentation files
- `mkdocs.yml` - Configuration
- `cognitive_app/**` - cognitive_app source
- `.github/workflows/pages-*.yml` - Pages workflows

**Checks:**
- ✅ Link validation (internal links, navigation references)
- ✅ MkDocs build test (strict mode)
- ✅ cognitive_app accessibility
- ✅ Documentation sync

**Actions:**
- 🔴 **Blocks merge** if critical errors found (MkDocs build failure)
- 🟡 **Warns** if non-critical issues found (broken links)
- ✅ **Passes** if all checks successful
- 💬 **Comments** on PR with results and fix commands

### Scheduled Validation
**Workflow:** `.github/workflows/pages-scheduled-validation.yml`

Runs automatically on schedule:
- **Daily at 00:00 UTC** - Quick validation (internal links only)
- **Weekly on Monday 00:00 UTC** - Deep validation (includes external links)
- **Manual trigger** - Available via workflow_dispatch

**Features:**
- 🔍 Comprehensive link validation
- 📊 MkDocs build warnings tracking
- 🧠 cognitive_app health checks
- 🎯 Auto-creates GitHub issues for problems
- 📦 Uploads validation artifacts (90-day retention)
- 🔄 Updates status dashboard automatically

**Issue Management:**
- Creates/updates issue: "🔍 GitHub Pages Validation Issues"
- Labels: `documentation`, `pages-validation`, `automated`
- Prioritizes issues: Critical vs Improvements
- Provides fix commands for GitHub Pages Manager agent

### Validation Script
**Script:** `scripts/validate_docs_links.py`

Can be run locally or in CI:
```bash
# Quick validation
python scripts/validate_docs_links.py

# Include external links
python scripts/validate_docs_links.py --external

# Auto-fix broken links
python scripts/validate_docs_links.py --fix
```

**Validates:**
- Internal markdown links
- Navigation references in mkdocs.yml
- Image paths
- External URLs (optional)
- Anchor links
- cognitive_app accessibility

**Features:**
- 🔍 Finds broken links
- 💡 Suggests similar files for auto-fix
- 📊 Comprehensive reporting
- ✅ Auto-fix capability (>90% confidence)

### Manual Validation Commands

Run validation manually using GitHub Pages Manager agent:

```bash
# Validate documentation sync
@copilot Use github-pages-manager to check if deployed documentation matches source files

# Find and fix broken links
@copilot Use github-pages-manager to find and fix broken links in documentation

# Validate cognitive_app
@copilot Use github-pages-manager to validate cognitive_app accessibility

# Update status dashboard
@copilot Use github-pages-manager to update the status dashboard with latest metrics

# Run comprehensive health check
@copilot Use github-pages-manager to run a comprehensive health check on GitHub Pages
```
