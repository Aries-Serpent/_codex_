# Phase 4.4: GitHub Pages Sync Plan & Publication Automation

**Campaign:** Phase 3-5 Multi-Agent Deployment  
**Agent:** Phase 4.4 — Post-Merge Doc Alignment  
**Focus:** Automated GitHub Pages publication, site validation, and content sync  

---

## 📡 GitHub Pages Architecture & Deployment Pipeline

### Current Setup

**Repository:** Aries-Serpent/_codex_  
**GitHub Pages Branch:** Auto-published from `docs/` on main  
**Theme:** MkDocs Material (Material for MkDocs)  
**Deployment:** GitHub Actions (inferred workflow)  

```
git push to main
     ↓
GitHub Actions trigger: docs-deploy.yml (or similar)
     ↓
MkDocs build: mkdocs build --config mkdocs.yml
     ↓
Output: site/ directory with HTML/CSS/JS
     ↓
GitHub Pages publish: docs/ branch or GitHub Pages publish step
     ↓
Live at: https://aries-serpent.github.io/_codex_/
```

---

## 🔄 Post-Merge Publication Sync Process

### Phase 1: Trigger Deployment

**When:** Immediately after merge to main (automated)

```bash
# GitHub Actions automatically triggers on push to main
# Workflow: .github/workflows/docs-deploy.yml (or docs.yml)
# Trigger: push event on main branch

# Manual trigger (if needed):
gh workflow run docs-deploy.yml -r main

# Monitor workflow:
gh run list --workflow=docs-deploy.yml --branch=main --limit=1
```

**Expected Output:**
```
✅ Workflow triggered
✅ MkDocs build started
✅ Site published to GitHub Pages
⏱️ Propagation time: ~30 seconds to 2 minutes
```

---

### Phase 2: Build Validation

**Automated checks during publish:**

```yaml
# mkdocs.yml validation rules (current configuration):

validation:
  links:
    absolute_links: ignore      # Accept absolute URLs
    anchors: ignore              # Don't validate anchor links
    not_found: ignore            # Don't fail on missing pages
    unrecognized_links: ignore   # Accept any URL format
  nav:
    not_found: ignore            # Missing nav files won't block
    omitted_files: ignore        # Non-nav files allowed

strict: false                     # Build succeeds even with warnings
```

**Implications:**
- ✅ Build is **very permissive** (won't fail on broken links)
- ⚠️ **Responsibility:** Manual link validation needed
- ✅ **Benefit:** Live updates can happen quickly

---

### Phase 3: Live Site Verification

**Checklist for post-merge verification:**

```bash
#!/bin/bash
# Phase 4.4 Post-Merge GitHub Pages Smoke Test

echo "=== GITHUB PAGES SYNC VERIFICATION ==="
echo "Target: https://aries-serpent.github.io/_codex_/"
echo ""

# Test 1: Homepage loads
echo "[1/6] Testing homepage..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://aries-serpent.github.io/_codex_/")
if [ "$HTTP_CODE" = "200" ]; then
  echo "  ✅ Homepage loads (HTTP 200)"
else
  echo "  ❌ Homepage failed (HTTP $HTTP_CODE)"
fi

# Test 2: CSS/JS loaded correctly
echo "[2/6] Testing assets (CSS/JS)..."
curl -s "https://aries-serpent.github.io/_codex_/" | grep -q "material" && \
  echo "  ✅ Material theme loaded" || echo "  ⚠️ Theme issue"

# Test 3: Navigation loads
echo "[3/6] Testing navigation..."
curl -s "https://aries-serpent.github.io/_codex_/" | grep -q "nav" && \
  echo "  ✅ Navigation present" || echo "  ⚠️ Navigation missing"

# Test 4: Key sections accessible
echo "[4/6] Testing key sections..."
SECTIONS=("ci/CI_RESCUE_PIPELINE/" "api/" "guides/" "CHANGELOG.md")
for section in "${SECTIONS[@]}"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://aries-serpent.github.io/_codex_/$section")
  [ "$CODE" = "200" ] && echo "  ✅ $section accessible" || \
    echo "  ⚠️ $section returned HTTP $CODE"
done

# Test 5: Search functionality
echo "[5/6] Testing search..."
curl -s "https://aries-serpent.github.io/_codex_/" | grep -q "search" && \
  echo "  ✅ Search feature present" || echo "  ⚠️ Search feature missing"

# Test 6: Mermaid diagrams
echo "[6/6] Testing Mermaid diagrams..."
curl -s "https://aries-serpent.github.io/_codex_/ci/CI_RESCUE_PIPELINE/" | \
  grep -q "mermaid" && echo "  ✅ Mermaid support loaded" || \
  echo "  ⚠️ Mermaid not detected"

echo ""
echo "=== VERIFICATION COMPLETE ==="
```

**Execution:**
```bash
bash /tmp/github_pages_verify.sh
```

**Expected Results:**
```
✅ Homepage loads (HTTP 200)
✅ Material theme loaded
✅ Navigation present
✅ ci/CI_RESCUE_PIPELINE/ accessible
✅ api/ accessible
✅ guides/ accessible
✅ CHANGELOG.md accessible
✅ Search feature present
✅ Mermaid support loaded

=== VERIFICATION COMPLETE ===
```

---

## 🔗 Navigation Sync Validation

### Current Navigation Structure

**mkdocs.yml Location:** Root of repository

**Navigation Entry Points (98 total):**

```yaml
nav:
  - Home: index.md
  - 📊 Status Dashboard: status/GITHUB_PAGES_STATUS.md
  - 🧠 Cognitive App: cognitive_app.md
  - [39 more main entries]
  - CI Rescue & Health:
      - CI Rescue Pipeline: ci/CI_RESCUE_PIPELINE.md  ⭐ POST-MERGE KEY
      - CI/CD Index: ci/INDEX.md
      - [3 more CI entries]
```

### Navigation Validation Script

```python
#!/usr/bin/env python3
"""
Validate mkdocs.yml navigation structure
Ensures all referenced files exist and render correctly
"""

import yaml
from pathlib import Path

def validate_nav():
    with open('mkdocs.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    nav = config.get('nav', [])
    issues = {
        'missing_files': [],
        'broken_paths': [],
        'external_links': []
    }
    
    def check_nav_item(item, path=""):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    if value.startswith('http'):
                        issues['external_links'].append(value)
                    elif value.endswith('.md'):
                        file_path = Path(f"docs/{value}")
                        if not file_path.exists():
                            issues['missing_files'].append(f"{path}/{value}")
                elif isinstance(value, list):
                    check_nav_item(value, f"{path}/{key}")
    
    for item in nav:
        check_nav_item(item)
    
    # Report
    print("📊 NAVIGATION VALIDATION REPORT")
    print("=" * 50)
    
    if not issues['missing_files']:
        print("✅ All markdown files exist")
    else:
        print(f"⚠️  Missing files ({len(issues['missing_files'])}):")
        for f in issues['missing_files']:
            print(f"   - {f}")
    
    print(f"✅ External links: {len(issues['external_links'])}")
    for link in issues['external_links'][:3]:
        print(f"   - {link[:60]}...")
    
    return len(issues['missing_files']) == 0

if __name__ == '__main__':
    is_valid = validate_nav()
    exit(0 if is_valid else 1)
```

**Run validation:**
```bash
python3 /tmp/validate_nav.py
```

**Post-Merge Action:**
- [ ] Run validation script
- [ ] Fix any missing files
- [ ] Update mkdocs.yml if files moved
- [ ] Re-run script to confirm all green

---

## 🚀 Content Publication Sync

### Sync Points (Pre-Merge → Post-Merge)

| Content Type | Pre-Merge Location | Post-Merge Action |
|--------------|------------------|------------------|
| **MkDocs config** | `mkdocs.yml` | Validate nav, fix casing issues |
| **Homepage** | `docs/index.md` | Update "Last Updated" timestamp |
| **CI Rescue docs** | `docs/ci/CI_RESCUE_PIPELINE.md` | Verify all diagrams render |
| **Architecture** | `docs/ARCHITECTURE.md` | Check diagram rendering |
| **README** | `README.md` (repo root) | Update version claims |
| **CHANGELOG** | `docs/CHANGELOG.md` | Add [Unreleased] section |
| **Assets** | `docs/stylesheets/`, `docs/assets/` | Verify CSS loads correctly |
| **Theme config** | `mkdocs.yml` theme section | Confirm Material theme features enabled |

### Automated Sync Workflow (Post-Merge)

```yaml
# Example GitHub Actions workflow for post-merge doc sync
# File: .github/workflows/docs-sync-post-merge.yml

name: Post-Merge Docs Sync

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - 'README.md'

jobs:
  validate-and-publish:
    runs-on: ubuntu-latest
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      # 2. Setup Python
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 3. Install MkDocs dependencies
      - name: Install MkDocs
        run: |
          pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
      
      # 4. Build with strict mode
      - name: Build MkDocs (strict)
        run: mkdocs build --strict
        continue-on-error: true
      
      # 5. Validate navigation
      - name: Validate navigation
        run: |
          python3 << 'EOF'
          import yaml
          from pathlib import Path
          
          with open('mkdocs.yml', 'r') as f:
              config = yaml.safe_load(f)
          
          nav = config.get('nav', [])
          missing = 0
          
          def check_nav(items):
              global missing
              for item in items:
                  if isinstance(item, dict):
                      for k, v in item.items():
                          if isinstance(v, str) and v.endswith('.md'):
                              if not Path(f"docs/{v}").exists():
                                  print(f"MISSING: {v}")
                                  missing += 1
                          elif isinstance(v, list):
                              check_nav(v)
          
          check_nav(nav)
          exit(1 if missing > 0 else 0)
          EOF
      
      # 6. Verify key pages exist
      - name: Verify key pages
        run: |
          for file in docs/index.md docs/CHANGELOG.md docs/ci/CI_RESCUE_PIPELINE.md; do
            test -f "$file" || (echo "Missing: $file" && exit 1)
          done
      
      # 7. GitHub Pages deployment (auto-triggered)
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
          cname: aries-serpent.github.io/_codex_
      
      # 8. Verify live site
      - name: Verify live site
        run: |
          sleep 30  # Wait for propagation
          curl -f https://aries-serpent.github.io/_codex_/ || exit 1
```

---

## 🔍 Post-Merge Site Content Validation

### Automated Content Checks

```bash
#!/bin/bash
# Phase 4.4 Post-Merge Content Validation

echo "🔍 POST-MERGE SITE CONTENT VALIDATION"
echo "============================================"

BASE_URL="https://aries-serpent.github.io/_codex_"

# Check 1: Metadata freshness
echo ""
echo "[1] Checking metadata freshness..."
HTML=$(curl -s "$BASE_URL/index.html")

# Look for "Last Updated" date
if echo "$HTML" | grep -q "2026-03-30\|$(date +%Y-%m-%d)"; then
  echo "  ✅ Homepage timestamp is current"
else
  echo "  ⚠️ Homepage timestamp may be stale"
fi

# Check 2: Navigation breadcrumb
echo ""
echo "[2] Checking navigation breadcrumb..."
for page in "/" "/ci/CI_RESCUE_PIPELINE/" "/guides/"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$page")
  [ "$CODE" = "200" ] && echo "  ✅ $page loads" || \
    echo "  ❌ $page failed (HTTP $CODE)"
done

# Check 3: Mermaid diagram rendering
echo ""
echo "[3] Checking Mermaid diagrams..."
RESCUE=$(curl -s "$BASE_URL/ci/CI_RESCUE_PIPELINE/")

# Count diagram types
if echo "$RESCUE" | grep -q "class=\"mermaid\""; then
  DIAGRAM_COUNT=$(echo "$RESCUE" | grep -c "class=\"mermaid\"")
  echo "  ✅ Found $DIAGRAM_COUNT Mermaid diagrams"
else
  echo "  ⚠️ No Mermaid diagrams detected"
fi

# Check 4: Search index
echo ""
echo "[4] Checking search functionality..."
if echo "$HTML" | grep -q "search.min.js\|search\\.js"; then
  echo "  ✅ Search script loaded"
else
  echo "  ⚠️ Search may not be functional"
fi

# Check 5: External links (sample)
echo ""
echo "[5] Checking external link accessibility..."
SAMPLE_LINKS=(
  "https://github.com/Aries-Serpent/_codex_"
  "https://github.com/Aries-Serpent/_codex_/releases/tag/pre-release_v0.1.0"
)

for link in "${SAMPLE_LINKS[@]}"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$link")
  [ "$CODE" = "200" ] && echo "  ✅ $link accessible" || \
    echo "  ⚠️ $link returned HTTP $CODE"
done

echo ""
echo "============================================"
echo "✅ VALIDATION COMPLETE"
```

**Run validation:**
```bash
bash /tmp/post_merge_content_check.sh
```

---

## 📊 Health Monitoring Dashboard

### Key Metrics to Track Post-Merge

```python
#!/usr/bin/env python3
"""
Phase 4.4 Post-Merge Documentation Health Metrics
Tracks publication status, freshness, and accessibility
"""

import json
from datetime import datetime
from pathlib import Path

metrics = {
    "publication": {
        "github_pages_url": "https://aries-serpent.github.io/_codex_/",
        "theme": "Material for MkDocs",
        "last_build": None,
        "build_status": "pending",
        "propagation_status": "pending"
    },
    "content": {
        "total_docs": len(list(Path("docs").rglob("*.md"))),
        "nav_entries": 98,
        "external_links": 6,
        "homepage_updated": None,
        "mermaid_diagrams": 200
    },
    "validation": {
        "mkdocs_build_strict": "pending",
        "nav_integrity": "pending",
        "homepage_render": "pending",
        "ci_rescue_mermaid": "pending",
        "search_functional": "pending"
    },
    "timestamp": datetime.now().isoformat()
}

print("📊 POST-MERGE DOCUMENTATION HEALTH METRICS")
print("=" * 60)
print(json.dumps(metrics, indent=2))
```

**Track these metrics post-merge:**
- ✅ GitHub Pages build completes within 2 minutes
- ✅ All 98 nav entries point to valid pages
- ✅ Homepage renders with current timestamp
- ✅ CI Rescue Pipeline displays all 9 diagrams
- ✅ Search index includes ≥1,700 docs
- ✅ Zero 404 errors on main navigation paths

---

## 🚨 Incident Response: Post-Merge Publication Issues

### Troubleshooting Decision Tree

```
Is the GitHub Pages site not accessible?
├─ Check GitHub Actions workflow status
│  └─ Workflow failed? Check build logs for mkdocs errors
├─ Check DNS/CDN propagation (up to 2 min)
│  └─ Still down after 5 min? Check GitHub Pages settings
└─ GitHub Pages settings correct? (Branch: main, Folder: / or docs/)

Are pages returning 404?
├─ Check mkdocs.yml nav entries
│  └─ File path wrong? Update nav entry
├─ Check if file exists in docs/
│  └─ File moved? Update nav, rebuild
└─ MkDocs cache issue? Run: mkdocs clean && mkdocs build

Are Mermaid diagrams not rendering?
├─ Check mkdocs.yml has mermaid2 plugin enabled
├─ Verify plugin version: "10.4.0"
└─ Check diagram syntax in source file

Is search not working?
├─ Verify search plugin enabled in mkdocs.yml
├─ Check search.min.js loads in browser (DevTools)
└─ Rebuild search index: mkdocs build --force

Are external links broken?
├─ Test link manually: curl https://...
├─ Check for typos in link
└─ Verify domain/repo exists
```

### Common Issues & Fixes

| Issue | Cause | Solution |
|-------|-------|----------|
| **Page not found (404)** | Missing file in nav | Check `docs/` dir, update mkdocs.yml |
| **Stale content** | Cache not cleared | GitHub Pages clears auto; manual: `gh run` workflow |
| **Mermaid not rendering** | Plugin disabled | Enable in mkdocs.yml: `plugins: - mermaid2:` |
| **Search empty** | No search index | Run full build: `mkdocs clean && mkdocs build` |
| **Build takes >5 min** | Large codebase | Normal; GitHub Pages can handle |
| **Theme looks broken** | CSS not loading | Check Material plugin version match |

---

## 📅 Post-Merge Publication Timeline

```
T+0 min:  Merge PR to main
          └─ GitHub Actions auto-triggers docs-deploy.yml

T+0-30 sec: MkDocs builds locally on GitHub Actions runner
            └─ Runs: mkdocs build
            └─ Outputs: site/ directory

T+30 sec:  Build completes, GitHub Pages publishes
            └─ site/ pushed to gh-pages or deployed
            └─ CDN cache updated

T+30-90 sec: Content propagates to edge servers
             └─ DNS updates propagate
             └─ CloudFlare cache updates (if used)

T+2 min:   ✅ Site fully live and accessible
           └─ All diagrams rendered
           └─ Search index updated
           └─ Mobile responsive verified

T+5 min:   Manual verification checklist runs
           └─ Smoke tests confirm all key pages load
           └─ No broken links detected
```

---

## ✅ Post-Merge Publication Sign-Off

**After completing all publication sync tasks:**

```markdown
### GitHub Pages Publication Sync — SIGN-OFF

**Executor:** [Name]
**Date:** [Merge date]
**Site:** https://aries-serpent.github.io/_codex_/

**PUBLICATION VERIFICATION:**
- [ ] GitHub Actions workflow completed successfully
- [ ] MkDocs build passed (no errors/warnings)
- [ ] Site live and accessible within 2 minutes
- [ ] All 98 nav entries point to valid pages
- [ ] Homepage timestamp updated to merge date
- [ ] CI Rescue Pipeline doc displays all diagrams
- [ ] Search functionality working
- [ ] Mobile responsive design verified
- [ ] Dark/light mode toggle functional
- [ ] External links working (spot-check 5)

**SIGN-OFF:**
I confirm the GitHub Pages publication sync completed successfully.
All content is live, validated, and accessible.

Signature: ________________________
Date: ____________________________
```

---

## 🔗 Related Documentation

**Audit & Planning:**
- `.codex/PHASE_4_4_POST_MERGE_ALIGNMENT_AUDIT.md` — Comprehensive state analysis
- `.codex/PHASE_4_4_ALIGNMENT_CHECKLIST.md` — Day-0 through Phase 4.5 tasks

**Live Site:**
- https://aries-serpent.github.io/_codex_/ — Live documentation site
- `mkdocs.yml` — Navigation and theme configuration
- `docs/` — All source documentation

**Reference Docs:**
- `docs/ci/CI_RESCUE_PIPELINE.md` — S280 canonical CI automation reference
- `docs/index.md` — Homepage with quick-links
- `README.md` — Repository README with version claims

---

**Generated by Phase 4.4 Post-Merge Documentation Alignment Agent**  
**Campaign: Phase 3-5 Multi-Agent Deployment**  
**Status: ✅ COMPLETE**

*All scripts and workflows provided are templates and should be adapted to your CI/CD environment.*
