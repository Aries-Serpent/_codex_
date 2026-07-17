# Local Deployment & Development Guide

**Version**: 1.0.0 | **Last Updated**: 2026-07-13 | **Status**: Production-Ready

## Overview

This guide provides comprehensive instructions for deploying and testing the Codex documentation site locally. The site is built with MkDocs Material theme and deployed to GitHub Pages at [https://aries-serpent.github.io/_codex_/](https://aries-serpent.github.io/_codex_/).

## Quick Start — Local Development Server

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install MkDocs and dependencies
pip install mkdocs-material mkdocs-mermaid2-plugin mkdocs-git-revision-date-localized-plugin
```

### Start Local Server

```bash
# Navigate to repository root
cd /home/runner/work/_codex_/_codex_

# Start development server
mkdocs serve

# Output:
# INFO - Building documentation...
# INFO - Listening on http://127.0.0.1:8000
```

### Access Documentation

Open your browser and navigate to: **http://127.0.0.1:8000**

The development server automatically:
- Watches for file changes
- Rebuilds documentation on save
- Hot-reloads browser (requires F5 refresh)

## Local Build & Static Site Generation

### Generate Static Files

```bash
# Build complete static site
mkdocs build --verbose

# Output directory:
# site/ # Generated static files
# index.html # Homepage
# assets/ # CSS, JS, images
# search/ # Search index
# [page_name]/index.html # All documentation pages
```

### Verify Build Output

```bash
# Check site directory
ls -la site/

# Verify index page
cat site/index.html | head -20

# Count total pages
find site -name "index.html" | wc -l
```

## Configuration Reference

### Site URL Configuration

**File**: `mkdocs.yml` (line 158)

```yaml
site_url: https://aries-serpent.github.io/_codex_/
```

**Local Override** (optional, for testing):

```bash
# Temporarily change site_url for local testing
mkdocs serve --config-file mkdocs.local.yml
```

### Theme Configuration

**Theme**: Material for MkDocs (Premium feature set)

**Key Settings**:

| Setting | Value | Purpose |
|---------|-------|---------|
| `theme.name` | `material` | MkDocs Material theme |
| `theme.language` | `en` | English documentation |
| `theme.features` | 12 features | Navigation, search, code copy |
| `dev_addr` | `127.0.0.1:8000` | Local development address |

### Plugins

| Plugin | Version | Purpose |
|--------|---------|---------|
| `material/search` | Built-in | Full-text search index |
| `mermaid2` | 10.4.0 | Mermaid diagram rendering |

### Markdown Extensions

- **admonition** — Note/warning/info boxes
- **tables** — Markdown table support
- **toc** — Table of contents generation
- **pymdownx.highlight** — Syntax highlighting
- **pymdownx.superfences** — Code block extensions
- **pymdownx.tabbed** — Tabbed content
- **pymdownx.tasklist** — Task lists
- **attr_list** — Element attributes
- **md_in_html** — Markdown in HTML

## Deployment Modes

### Mode 1: Local Development (127.0.0.1:8000)

**Purpose**: Real-time development and testing

**When to use**:
- Making documentation updates
- Testing new features
- Reviewing changes before commit
- Validating Mermaid diagrams

**Command**:
```bash
mkdocs serve --dev-addr 127.0.0.1:8000
```

**Browser**: `http://127.0.0.1:8000`

### Mode 2: GitHub Pages (Production)

**Purpose**: Live public documentation site

**When triggered**:
- Push to `main` branch with changes to `docs/**` or `mkdocs.yml`
- Manual workflow dispatch (GitHub Actions)
- Scheduled builds (daily validation)

**Workflow**: `.github/workflows/pages-mkdocs.yml`

**Site URL**: `https://aries-serpent.github.io/_codex_/`

**Build steps**:
1. Install MkDocs dependencies
2. Generate API documentation
3. Build MkDocs site
4. Build cognitive_app dashboard
5. Upload artifact
6. Deploy to GitHub Pages
7. Verify health check

### Mode 3: Docker Deployment (Optional)

For containerized deployments, create a Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install mkdocs-material mkdocs-mermaid2-plugin mkdocs-git-revision-date-localized-plugin

# Copy documentation
COPY docs ./docs
COPY mkdocs.yml .

# Build site
RUN mkdocs build

# Serve with nginx
FROM nginx:alpine
COPY --from=builder /app/site /usr/share/nginx/html
EXPOSE 80
```

## Deployment Scripts

### 1. `deploy/deploy.sh`

**Purpose**: Kubernetes-based production deployment

**Capabilities**:
- Prerequisites validation (kubectl, helm, docker)
- Image security scanning (Trivy)
- Manifest application
- Health checks
- Automatic rollback on failure
- Smoke tests

**Usage**:
```bash
bash deploy/deploy.sh \
 --namespace codex-ml \
 --image-tag v1.2.3 \
 --environment production
```

### 2. `deploy/setup_universal.sh`

**Purpose**: Multi-language runtime configuration

**Manages**:
- Python (pyenv)
- Node.js (nvm)
- Rust (rustup)
- Go (golang)
- Swift (swiftly)

**Usage**:
```bash
source deploy/setup_universal.sh
```

### 3. `deploy/interactive_entrypoint.sh`

**Purpose**: Interactive setup wizard for deployment

**Features**:
- Interactive prompts for configuration
- Validation of prerequisites
- Environment setup
- Bootstrap operations

### 4. `deploy/deploy_codex_pipeline.py`

**Purpose**: Programmatic deployment automation

**Supports**:
- Multiple deployment strategies
- Configuration management
- Pre/post-deployment hooks
- Logging and monitoring

## Verification Checklist

### Pre-Deployment Verification

- [ ] Python 3.12+ installed: `python --version`
- [ ] MkDocs installed: `mkdocs --version`
- [ ] Repository cloned: `git status`
- [ ] All docs files present: `find docs -name "*.md" | wc -l`
- [ ] mkdocs.yml valid: `python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"`

### Local Build Verification

- [ ] Build completes without errors: `mkdocs build --verbose 2>&1 | grep -i error`
- [ ] No broken references: Check build output for warnings
- [ ] Static files generated: `test -d site && echo " site/ directory exists"`
- [ ] Index page valid: `test -f site/index.html && echo " Homepage generated"`

### Development Server Verification

- [ ] Server starts: `mkdocs serve` runs without errors
- [ ] Accessible at 127.0.0.1:8000: Browser responds with HTTP 200
- [ ] Hot reload works: Edit a .md file, save, check browser refresh
- [ ] Navigation renders: All nav items accessible and clickable
- [ ] Search functional: Search index builds and searches work

### GitHub Pages Verification

- [ ] Workflow triggers: Push to `main` triggers `pages-mkdocs.yml`
- [ ] Build succeeds: GitHub Actions build completes
- [ ] Deployment succeeds: Pages deployment completes
- [ ] Site accessible: https://aries-serpent.github.io/_codex_/ returns HTTP 200
- [ ] Content updated: New changes visible on live site within 2 minutes

## Configuration Files

### mkdocs.yml Structure

```yaml
site_name: Codex Docs v0.2.1
site_url: https://aries-serpent.github.io/_codex_/
repo_name: Aries-Serpent/_codex_
repo_url: https://github.com/Aries-Serpent/_codex_

docs_dir: docs/
site_dir: site/

theme:
 name: material
 language: en
 features: [12 features for navigation & search]

plugins:
 - material/search
 - mermaid2:
 version: "10.4.0"

nav:
 - Home: index.md
 - [40+ documentation sections with 100+ total nav entries]

markdown_extensions:
 - [11 markdown extensions for enhanced formatting]

validation:
 links:
 absolute_links: ignore
 anchors: ignore
 nav:
 omitted_files: ignore
```

### Navigation Coverage

**Total Navigation Entries**: 100+

**Main Sections**:
1. Home & Dashboard (2)
2. Cognitive App (1)
3. Evolution Center (7)
4. Guides (9)
5. Token Management (8)
6. Architecture (3)
7. Training (2)
8. Deployment (2)
9. Logging & Troubleshooting (5)
10. Reference (9)
11. Agents (1)
12. Accountability (3)
13. Phase 9 Execution (4)
14. CI/CD Workflows (5)
15. Reporting (2)
16. CI Rescue & Health (5)
17. Safety (1)
18. Database Options (3)
19. Templates (12)
20. Examples (1)
21. Ops (5)
22. Tutorials (2)
23. Legacy Catalog (3)

### GitHub Pages Workflow Structure

**File**: `.github/workflows/pages-mkdocs.yml`

**Key Jobs**:

1. **Build Job**
 - Checkout repository (fetch-depth: 0)
 - Setup Python 3.12 with caching
 - Install dependencies
 - Generate API documentation
 - Validate documentation links
 - Build MkDocs site (verbose)
 - Build cognitive_app dashboard
 - Upload artifact

2. **Deploy Job**
 - Wait for previous deployments
 - Deploy to GitHub Pages
 - Verify deployed site health
 - Post summary

**Concurrency**: `${{ github.workflow }}-${{ github.head_ref || github.ref }}`

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'mkdocs'`

**Solution**:
```bash
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
```

### Issue: `Port 8000 already in use`

**Solution**:
```bash
# Use different port
mkdocs serve --dev-addr 127.0.0.1:8001

# Or find and kill process
lsof -ti:8000 | xargs kill -9
```

### Issue: Mermaid diagrams not rendering

**Solution**:
```bash
# Verify plugin installed
pip show mkdocs-mermaid2-plugin

# Verify in mkdocs.yml:
# plugins:
# - mermaid2:
# version: "10.4.0"

# Rebuild
mkdocs build --clean
```

### Issue: Changes not visible after save

**Solution**:
```bash
# Restart development server
# Press Ctrl+C to stop
# Run: mkdocs serve

# If still not working, clear cache:
rm -rf site/ .mkdocs/
mkdocs serve
```

### Issue: GitHub Pages shows 404 error

**Solution**:
1. Verify site built successfully (check workflow logs)
2. Verify site_url is correct: `https://aries-serpent.github.io/_codex_/`
3. Check GitHub Pages settings in repository
4. Verify branch is `gh-pages` (auto-deployed)
5. Wait 2-3 minutes for CDN propagation

## Performance Optimization

### Build Performance

```bash
# Use --dirty to only rebuild changed pages
mkdocs serve --dirty

# Profile build time
time mkdocs build --verbose

# Expected build time: ~30-60 seconds for full site
```

### Search Index Optimization

- Indexed automatically during build
- Full-text search on all pages
- Minimal performance impact
- Stored in `site/search/search_index.json`

## Security Considerations

### Site URL Configuration

Always use the canonical HTTPS URL:
```yaml
site_url: https://aries-serpent.github.io/_codex_/
```

This ensures:
- Correct canonical links
- Proper social media sharing
- SEO optimization
- Cross-origin requests work correctly

### Repository Access

The workflow uses:
- `secrets.GITHUB_TOKEN` — Default GitHub Actions token
- `secrets.CODEX_MASTER_KEY` — Optional custom key
- `secrets.CODEX_BACKUP_KEY` — Optional fallback key

All sensitive operations are audited and encrypted.

## Related Documentation

- **Deployment Guide**: `docs/deployment/DEPLOYMENT_GUIDE.md`
- **CI/CD Configuration**: `.github/workflows/pages-mkdocs.yml`
- **GitHub Pages Status**: `docs/status/GITHUB_PAGES_STATUS.md`
- **Agent Documentation**: `docs/agents/POST_MERGE_ALIGNMENT_PROMPT.md`

## Support & Contact

For questions or issues:

1. **Check troubleshooting** section above
2. **Review GitHub workflow logs**: Actions pages-mkdocs
3. **Inspect build output**: `mkdocs build --verbose 2>&1 | tee build.log`
4. **Create GitHub Issue**: Report bugs with logs attached

---

**Last Verified**: 2026-07-13 | **Next Review**: 2026-08-13 | **Status**: Operational
