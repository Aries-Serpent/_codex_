# Deployment Verification Checklist

**Purpose**: Ensure all deployment components are properly configured and operational

**Usage**: Run through this checklist after any deployment or configuration changes

---

## 1. MkDocs Configuration Verification

### 1.1 Site Configuration
- [ ] **site_url correct**: `https://aries-serpent.github.io/_codex_/`
  ```bash
  grep "site_url:" mkdocs.yml
  ```
- [ ] **site_name defined**: `Codex Docs v0.2.1`
  ```bash
  grep "site_name:" mkdocs.yml
  ```
- [ ] **repo_url correct**: `https://github.com/Aries-Serpent/_codex_`
  ```bash
  grep "repo_url:" mkdocs.yml
  ```
- [ ] **docs_dir exists**: `docs/`
  ```bash
  test -d docs && echo "✅ docs/ exists"
  ```

### 1.2 Theme Configuration
- [ ] **Theme set to Material**: `material`
  ```bash
  grep "name: material" mkdocs.yml
  ```
- [ ] **12 navigation features enabled**
  ```bash
  grep -A 12 "features:" mkdocs.yml | wc -l
  ```
- [ ] **Logo configured**: `material/book-open-page-variant`
  ```bash
  grep "logo:" mkdocs.yml
  ```

### 1.3 Plugin Configuration
- [ ] **Material Search plugin enabled**
  ```bash
  grep "material/search" mkdocs.yml
  ```
- [ ] **Mermaid2 plugin enabled**: Version 10.4.0
  ```bash
  grep -A 1 "mermaid2:" mkdocs.yml
  ```
- [ ] **No plugin errors on build**
  ```bash
  mkdocs build 2>&1 | grep -i "plugin" | grep -i error || echo "✅ No plugin errors"
  ```

### 1.4 Markdown Extensions
- [ ] **admonition** (notes/warnings): Enabled ✓
- [ ] **tables** (markdown tables): Enabled ✓
- [ ] **toc** (auto table of contents): Enabled ✓
- [ ] **pymdownx.highlight** (syntax highlighting): Enabled ✓
- [ ] **pymdownx.superfences** (code blocks): Enabled ✓
- [ ] **pymdownx.tabbed** (tabbed content): Enabled ✓
- [ ] **attr_list** (element attributes): Enabled ✓

**Verify all enabled**:
```bash
grep -E "admonition|tables|toc|pymdownx" mkdocs.yml | wc -l
# Should output: 11+
```

---

## 2. Documentation Files Verification

### 2.1 Documentation Structure
- [ ] **Total docs files**: ~1947 markdown files
  ```bash
  find docs -name "*.md" | wc -l
  ```
- [ ] **No broken reference in docs**
  ```bash
  find docs -name "*.md" -exec grep -l "\\[.*\\]" {} \; | wc -l
  # Count files with links
  ```
- [ ] **docs/ directory not empty**: Multiple subdirectories present
  ```bash
  ls -d docs/*/ | wc -l
  ```

### 2.2 Navigation Configuration
- [ ] **Navigation entries count**: 100+ entries
  ```bash
  python3 -c "import yaml; nav = yaml.safe_load(open('mkdocs.yml'))['nav']; print(len([i for i in nav]))"
  ```
- [ ] **Home page exists**: `docs/index.md`
  ```bash
  test -f docs/index.md && echo "✅ Homepage exists"
  ```
- [ ] **README exists**: `docs/README_ROOT.md`
  ```bash
  test -f docs/README_ROOT.md && echo "✅ README exists"
  ```

### 2.3 Required Documentation Pages
- [ ] **Getting Started**: `docs/getting-started.md` exists
- [ ] **Deployment Guide**: `docs/deployment/DEPLOYMENT_GUIDE.md` exists
- [ ] **Local Deployment**: `docs/deployment/LOCAL_DEPLOYMENT_GUIDE.md` exists ✅ NEW
- [ ] **Architecture**: `docs/architecture.md` or `docs/architecture/` exists
- [ ] **Changelog**: `docs/CHANGELOG.md` exists

**Verify**:
```bash
test -f docs/deployment/LOCAL_DEPLOYMENT_GUIDE.md && echo "✅ New guide created"
```

### 2.4 Excluded Files Check
- [ ] **Template files excluded**: files in `docs/templates/` are excluded by design
- [ ] **Exclusion configured correctly**: `exclude_docs` in mkdocs.yml
  ```bash
  grep -A 2 "exclude_docs:" mkdocs.yml
  ```
- [ ] **Expected exclusions**: README.md, _config.yml, _layouts/

---

## 3. Local Deployment Verification

### 3.1 Environment Setup
- [ ] **Python 3.12+ installed**: `python --version`
  ```bash
  python --version | grep -E "3\.(12|13|14)"
  ```
- [ ] **MkDocs installed**: `mkdocs --version`
  ```bash
  mkdocs --version
  ```
- [ ] **MkDocs Material installed**: Visible in `pip list`
  ```bash
  pip list | grep mkdocs
  ```
- [ ] **Mermaid2 plugin installed**
  ```bash
  pip show mkdocs-mermaid2-plugin | grep "Version"
  ```

### 3.2 Local Build Test
- [ ] **Build completes without errors**
  ```bash
  mkdocs build 2>&1 | grep -i "✅"
  ```
- [ ] **site/ directory created**: Output files generated
  ```bash
  test -d site && echo "✅ site/ directory created"
  ```
- [ ] **index.html generated**: Homepage present
  ```bash
  test -f site/index.html && echo "✅ Homepage generated"
  ```
- [ ] **Search index created**: Full-text search data
  ```bash
  test -f site/search/search_index.json && echo "✅ Search index created"
  ```
- [ ] **No broken links in output**: Validate references
  ```bash
  find site -name "*.html" | wc -l
  # Should match number of docs
  ```

### 3.3 Development Server Test
- [ ] **Server starts successfully**
  ```bash
  timeout 5 mkdocs serve 2>&1 | grep -E "127.0.0.1:8000"
  ```
- [ ] **Accessible at 127.0.0.1:8000**: HTTP 200 response
  ```bash
  curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000
  # Expected: 200
  ```
- [ ] **Hot reload functional**: Changes reflected without restart
  - Edit a .md file
  - Save changes
  - Browser refresh shows new content

### 3.4 Content Rendering
- [ ] **Markdown renders correctly**: No syntax errors
- [ ] **Mermaid diagrams render**: SVG diagrams visible
- [ ] **Code blocks highlighted**: Syntax coloring applied
- [ ] **Tables formatted correctly**: Border and alignment
- [ ] **Navigation renders**: All sidebar items visible and clickable

---

## 4. GitHub Pages Workflow Verification

### 4.1 Workflow Configuration
- [ ] **Workflow file exists**: `.github/workflows/pages-mkdocs.yml`
  ```bash
  test -f .github/workflows/pages-mkdocs.yml && echo "✅ Workflow exists"
  ```
- [ ] **Trigger on push to main with doc changes**
  ```bash
  grep -A 3 "push:" .github/workflows/pages-mkdocs.yml
  ```
- [ ] **Trigger on manual dispatch**
  ```bash
  grep "workflow_dispatch:" .github/workflows/pages-mkdocs.yml
  ```
- [ ] **Concurrency configured**: Prevent simultaneous deployments
  ```bash
  grep -A 2 "concurrency:" .github/workflows/pages-mkdocs.yml
  ```

### 4.2 Workflow Jobs
- [ ] **Build job configured**: Ubuntu latest runner, timeout 60m
  ```bash
  grep -A 3 "build:" .github/workflows/pages-mkdocs.yml
  ```
- [ ] **Deploy job configured**: Wait for build completion
  ```bash
  grep -A 3 "deploy:" .github/workflows/pages-mkdocs.yml
  ```
- [ ] **Health check step included**: Verify deployed site
  ```bash
  grep "health_check" .github/workflows/pages-mkdocs.yml
  ```

### 4.3 Build Steps
- [ ] **Python 3.12 setup**: Correct version specified
- [ ] **Dependencies installed**: mkdocs-material, plugins
- [ ] **API docs generated**: Auto-generation step
- [ ] **MkDocs build step**: Verbose mode enabled
- [ ] **Artifact upload**: Ready for deployment
- [ ] **Cache enabled**: For faster builds
  - MkDocs plugins cache
  - Built site cache

### 4.4 Deployment Steps
- [ ] **GitHub Pages deployment**: Using `deploy-pages@v5`
- [ ] **Health check implemented**: 200ms polling, 60s timeout
- [ ] **Step summary posted**: To GitHub Actions summary
- [ ] **Permissions correct**: pages:write, id-token:write

---

## 5. Deployment Scripts Verification

### 5.1 Kubernetes Deployment (deploy/deploy.sh)
- [ ] **File exists and is executable**
  ```bash
  test -x deploy/deploy.sh && echo "✅ deploy.sh is executable"
  ```
- [ ] **Syntax valid**: No shell errors
  ```bash
  bash -n deploy/deploy.sh && echo "✅ Syntax valid"
  ```
- [ ] **Documentation present**: Comments and help text
  ```bash
  grep -c "^#" deploy/deploy.sh
  # Should be >50 lines of documentation
  ```
- [ ] **Key functions present**:
  - [ ] `check_prerequisites()`
  - [ ] `validate_image()`
  - [ ] `apply_manifests()`
  - [ ] `wait_for_deployment()`
  - [ ] `health_check()`
  - [ ] `rollback_deployment()`
  - [ ] `smoke_tests()`

### 5.2 Universal Setup (deploy/setup_universal.sh)
- [ ] **File exists**: `deploy/setup_universal.sh`
- [ ] **Configures Python**: Via pyenv
- [ ] **Configures Node.js**: Via nvm
- [ ] **Configures Rust**: Via rustup
- [ ] **Configures Go**: Via golang
- [ ] **Configures Swift**: Via swiftly (optional)

### 5.3 Interactive Entrypoint (deploy/interactive_entrypoint.sh)
- [ ] **File exists**: `deploy/interactive_entrypoint.sh`
- [ ] **Provides interactive setup**: Prompts for configuration
- [ ] **Sets environment variables**: For local development

### 5.4 Python Pipeline (deploy/deploy_codex_pipeline.py)
- [ ] **File exists**: `deploy/deploy_codex_pipeline.py`
- [ ] **No syntax errors**
  ```bash
  python3 -m py_compile deploy/deploy_codex_pipeline.py
  ```
- [ ] **Documented**: Includes docstrings and comments

---

## 6. Site Navigation Coverage Verification

### 6.1 Main Navigation Sections
- [ ] **Home**: index.md ✓
- [ ] **Status Dashboard**: status/GITHUB_PAGES_STATUS.md ✓
- [ ] **Cognitive App**: cognitive_app.md ✓
- [ ] **Evolution Center**: 7 sub-pages ✓
- [ ] **README**: README_ROOT.md ✓
- [ ] **Getting Started**: getting-started.md ✓
- [ ] **API Reference**: api/index.md ✓
- [ ] **Guides**: 9 sub-pages ✓
- [ ] **Token Management**: 8 sub-pages ✓
- [ ] **Architecture**: 3 sub-pages ✓
- [ ] **Training**: 2 sub-pages ✓
- [ ] **Deployment**: 2 sub-pages ✓ (now includes Local Deployment Guide)
- [ ] **Logging & Troubleshooting**: 5 sub-pages ✓
- [ ] **Plugins**: 1 sub-page ✓
- [ ] **Reference**: 9 sub-pages ✓
- [ ] **Agent Prompts**: 1 sub-page ✓
- [ ] **Accountability**: 3 sub-pages ✓
- [ ] **Phase 9 Execution**: 4 sub-pages ✓
- [ ] **CI/CD Workflows**: 5 external links ✓
- [ ] **Reporting**: 2 sub-pages ✓
- [ ] **CI Rescue & Health**: 5 sub-pages ✓
- [ ] **Safety**: 1 sub-page ✓
- [ ] **Database Options**: 3 sub-pages ✓
- [ ] **Templates**: 12 sub-pages ✓
- [ ] **Examples**: 1 sub-page ✓
- [ ] **Ops**: 5 sub-pages ✓
- [ ] **Tutorials**: 2 sub-pages ✓
- [ ] **Legacy Catalog**: 3 sub-pages ✓

**Verify count**:
```bash
python3 << 'EOF'
import yaml
with open('mkdocs.yml', 'r') as f:
    config = yaml.safe_load(f)
nav = config.get('nav', [])
print(f"✅ Navigation entries: {len(nav)} main sections")
EOF
```

---

## 7. Pre-Production Validation

### 7.1 Build Quality
- [ ] **No build warnings**: `mkdocs build 2>&1 | grep -i warning` (should be empty)
- [ ] **No broken links**: All internal links valid
- [ ] **All referenced files exist**: No 404s in nav
- [ ] **Search index valid**: Can be parsed and searched
- [ ] **Mermaid diagrams valid**: All render without errors

### 7.2 Performance
- [ ] **Build time < 90 seconds**: `time mkdocs build`
- [ ] **Static files optimized**: Images compressed, CSS minified
- [ ] **Search index size reasonable**: < 10MB

### 7.3 Accessibility
- [ ] **HTML valid**: No critical errors
- [ ] **Semantic markup used**: Proper heading hierarchy
- [ ] **Color contrast sufficient**: WCAG AA standard
- [ ] **Links descriptive**: Not "click here"
- [ ] **Images have alt text**: Accessibility support

---

## 8. Post-Deployment Validation

### 8.1 GitHub Pages Live Site
- [ ] **Site accessible**: https://aries-serpent.github.io/_codex_/ returns 200
- [ ] **Homepage renders**: Content visible and styled
- [ ] **Navigation works**: All menu items clickable
- [ ] **Search functional**: Can search and get results
- [ ] **Mermaid diagrams render**: SVG diagrams visible on live site
- [ ] **Code blocks styled**: Syntax highlighting visible
- [ ] **Tables formatted**: Borders and alignment correct
- [ ] **Dark mode works**: Theme toggle functional
- [ ] **Mobile responsive**: Site works on mobile browsers
- [ ] **Performance good**: Page loads in <3 seconds

### 8.2 Deployment Monitoring
- [ ] **No 404 errors**: Workflow health check passed
- [ ] **CDN propagation complete**: <2 minute deploy-to-live time
- [ ] **Search index updated**: Latest pages appear in search
- [ ] **Previous version accessible**: Browser back button works
- [ ] **All new pages linked**: No orphaned pages

### 8.3 Analytics
- [ ] **Page views tracked**: Google Analytics or custom tracking
- [ ] **Search queries logged**: User behavior data collected
- [ ] **Performance metrics collected**: Page speed data available
- [ ] **Error rates monitored**: Any console errors detected

---

## 9. Troubleshooting Checklist

If any check fails, use this troubleshooting guide:

### Issue: MkDocs build fails
- [ ] Clear cache: `rm -rf site/ .mkdocs/`
- [ ] Reinstall: `pip install --upgrade mkdocs-material`
- [ ] Check syntax: `python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"`
- [ ] Run with verbose: `mkdocs build --verbose 2>&1 | tail -20`

### Issue: Site not updating on GitHub Pages
- [ ] Check workflow logs: Actions → pages-mkdocs → Latest run
- [ ] Verify trigger: Push to `main` with `docs/**` changes
- [ ] Wait 2-3 minutes: CDN propagation delay
- [ ] Hard refresh browser: Ctrl+Shift+R
- [ ] Check branch: Verify `gh-pages` branch exists

### Issue: Local server doesn't start
- [ ] Verify port available: `lsof -i :8000`
- [ ] Kill existing process: `kill -9 <PID>`
- [ ] Try different port: `mkdocs serve --dev-addr 127.0.0.1:8001`
- [ ] Check Python version: Must be 3.12+

### Issue: Mermaid diagrams not rendering
- [ ] Check plugin installed: `pip show mkdocs-mermaid2-plugin`
- [ ] Verify mkdocs.yml has plugin: Search for `mermaid2:`
- [ ] Check diagram syntax: Valid Mermaid syntax required
- [ ] Rebuild: `mkdocs build --clean`

---

## Approval & Sign-Off

**Checklist Authority**: @mbaetiong (D-tier autonomous)

**When to run**: 
- After configuration changes
- Before pushing to main
- After merging promotion branches
- During monthly maintenance

**Expected Duration**: 10-15 minutes

**Last Completed**: [Date to be updated after execution]

**Status**: ✅ **PASS** / ❌ **FAIL** / ⏸️ **BLOCKED**

---

**Document Version**: 1.0.0 | **Last Updated**: 2026-07-13 | **Next Review**: 2026-08-13
