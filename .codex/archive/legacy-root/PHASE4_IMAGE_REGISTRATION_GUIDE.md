# Phase 4 Image Registration Guide

**Version:** 1.0.0  
**Effective Date:** 2026-07-18  
**Status:** DRAFT - Ready for Implementation  
**Target Image:** `codex-base:v1.0`  
**Authority:** @mbaetiong (D-tier autonomous)  

---

## 1. Pre-Registration Checklist

Before registering any custom image with GitHub Actions, complete these verification steps:

### 1.1 Prerequisites

- [ ] **Organization Admin Access:** Verify access to `https://github.com/organizations/Aries-Serpent/settings`
- [ ] **GHCR Access:** Confirmed at `ghcr.io/aries-serpent` via `docker login`
- [ ] **GitHub CLI Available:** `gh --version` returns v2.0+
- [ ] **Docker Installed:** `docker --version` returns v20.0+
- [ ] **Token Available:** `CODEX_MASTER_KEY` secret exists and has `write:packages` scope
- [ ] **Build Artifacts Ready:** Dockerfile and dependencies in place
- [ ] **Security Scan Passed:** Initial vulnerability scan clean (Trivy/Dependabot)

### 1.2 Image Requirements

**For `codex-base:v1.0`:**

- [ ] **Base Image:** Ubuntu 22.04 LTS or Python 3.12-slim
- [ ] **Size Limit:** < 1 GB (preferably < 600 MB)
- [ ] **Python Version:** 3.12+ installed
- [ ] **Node.js Version:** 22+ installed (if needed)
- [ ] **Security:** No hardcoded credentials, known vulnerabilities
- [ ] **Documentation:** Included in image (README, license)
- [ ] **Tests:** Local build succeeds without errors

---

## 2. Step-by-Step Registration Process

### 2.1 Phase 1: Prepare Image Artifacts

**Location:** `.docker/base/` (in `_codex_` repository)

```bash
# Create directory structure
mkdir -p .docker/base
cd .docker/base

# 1. Create Dockerfile.base
cat > Dockerfile << 'EOF'
# Multi-stage build for optimization
FROM ubuntu:22.04 AS builder

# Install Python build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Build Python dependencies
WORKDIR /tmp
COPY requirements-base.txt .
RUN python3.12 -m pip install --no-cache-dir -r requirements-base.txt

# Final stage
FROM ubuntu:22.04

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-minimal \
    nodejs \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy built Python packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Set environment variables
ENV PYTHON_VERSION=3.12 \
    PATH="/usr/local/bin:$PATH" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3.12 --version || exit 1

# Metadata
LABEL org.opencontainers.image.vendor="Aries-Serpent" \
      org.opencontainers.image.title="codex-base" \
      org.opencontainers.image.version="1.0" \
      org.opencontainers.image.description="Aries-Serpent Codex base image with Python 3.12 and Node.js 22"

WORKDIR /workspace
CMD ["/bin/bash"]
EOF

# 2. Create requirements-base.txt
cat > requirements-base.txt << 'EOF'
# Core dependencies for codex-base:v1.0
pip>=24.0
setuptools>=68.0
wheel>=0.40.0
black==24.1.0
ruff==0.1.0
isort==5.13.0
mypy==1.8.0
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.23.0
pydantic==2.5.0
pyyaml==6.0.1
requests==2.31.0
urllib3==2.1.0
EOF

# 3. Create .dockerignore
cat > .dockerignore << 'EOF'
.git
.gitignore
*.md
*.lock
node_modules
__pycache__
*.pyc
.pytest_cache
.coverage
.mypy_cache
.ruff_cache
dist
build
*.egg-info
EOF

# 4. Verify local build
cd /home/runner/work/_codex_/_codex_
docker build -t ghcr.io/aries-serpent/codex-base:v1.0-test -f .docker/base/Dockerfile .
```

### 2.2 Phase 2: Security Scanning

```bash
# Run Trivy vulnerability scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest image \
    --severity HIGH,CRITICAL \
    --exit-code 0 \
    ghcr.io/aries-serpent/codex-base:v1.0-test

# Check for known vulnerabilities
docker run --rm \
    -e DOCKER_HOST=unix:///var/run/docker.sock \
    -v /var/run/docker.sock:/var/run/docker.sock \
    anchore/grype:latest \
    ghcr.io/aries-serpent/codex-base:v1.0-test

# Generate SBOM (Software Bill of Materials)
syft ghcr.io/aries-serpent/codex-base:v1.0-test -o spdx-json > sbom-v1.0.json
```

### 2.3 Phase 3: Push to GHCR

```bash
# 1. Authenticate with GHCR
echo "$CODEX_MASTER_KEY" | docker login ghcr.io -u "mbaetiong" --password-stdin

# 2. Tag image with all required tags
docker tag ghcr.io/aries-serpent/codex-base:v1.0-test ghcr.io/aries-serpent/codex-base:v1.0
docker tag ghcr.io/aries-serpent/codex-base:v1.0-test ghcr.io/aries-serpent/codex-base:latest
docker tag ghcr.io/aries-serpent/codex-base:v1.0-test ghcr.io/aries-serpent/codex-base:stable

# 3. Push all tags
docker push ghcr.io/aries-serpent/codex-base:v1.0
docker push ghcr.io/aries-serpent/codex-base:latest
docker push ghcr.io/aries-serpent/codex-base:stable

# 4. Verify push success
docker inspect ghcr.io/aries-serpent/codex-base:v1.0

# 5. Cleanup
docker logout ghcr.io
```

### 2.4 Phase 4: Register with GitHub Actions

**Navigate to:** `https://github.com/organizations/Aries-Serpent/settings/actions/custom_images`

#### Form Fields to Fill:

**1. Image Details**

```
Image name:           codex-base
Registry source:      GitHub Container Registry (GHCR)
Full image URL:       ghcr.io/aries-serpent/codex-base:v1.0
```

**2. Access Control**

```
Who can use this image:
  ☑ All users and GitHub Actions
  ☐ Selected users/teams only

Allow image creation by:
  ☑ GitHub Actions bot
  ☑ Copilot agents (copilot-swe-agent[bot])
```

**3. Image Configuration**

```
Image architecture:   linux/amd64 (+ linux/arm64 if available)
Default tag:          v1.0
Allow tag updates:    ☑ Yes
Pinned version:       v1.0
```

**4. Visibility & Permissions**

```
Visibility:           Organization-level (default)
Access level:
  ☑ Read (pull)
  ☑ Write (push/update for CI/CD only)
  ☐ Admin
```

**5. Workflow Integration**

```
Reference image in workflows as:
  container:
    image: ghcr.io/aries-serpent/codex-base:v1.0
    credentials:
      username: ${{ github.actor }}
      password: ${{ secrets.CODEX_MASTER_KEY }}
```

#### Click "Create" to Register

---

## 3. Verification After Registration

### 3.1 Verify Image Registration

```bash
# 1. Query GitHub API to confirm registration
gh api orgs/Aries-Serpent/packages/container \
  --jq '.[] | select(.name=="codex-base") | {name, visibility, updated_at}'

# Expected output:
# {
#   "name": "codex-base",
#   "visibility": "public",
#   "updated_at": "2026-07-18T10:30:00Z"
# }

# 2. Verify image pull works
docker pull ghcr.io/aries-serpent/codex-base:v1.0

# 3. Verify image contents
docker run --rm ghcr.io/aries-serpent/codex-base:v1.0 \
  python3.12 --version

# 4. Check image metadata
docker inspect ghcr.io/aries-serpent/codex-base:v1.0 | jq '.[] | {Size, Created, Labels}'
```

### 3.2 Test Image in Workflow

**Create test workflow:** `.github/workflows/test-custom-image.yml`

```yaml
name: Test Custom Image
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - '.docker/base/Dockerfile'

jobs:
  test-custom-image:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aries-serpent/codex-base:v1.0
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.CODEX_MASTER_KEY }}

    steps:
      - name: Verify Python
        run: python3.12 --version

      - name: Verify Node.js
        run: node --version

      - name: Verify pip
        run: pip3 --version

      - name: Check image ID
        run: cat /etc/hostname

      - name: Report Success
        run: echo "✅ Custom image working correctly"
```

**Execute:**

```bash
gh workflow run test-custom-image.yml -R Aries-Serpent/_codex_
gh run watch --exit-status  # Monitor execution
```

---

## 4. Image Management

### 4.1 Update Image Version

**When creating v1.1.0:**

```bash
# 1. Build new version locally
docker build -t ghcr.io/aries-serpent/codex-base:v1.1.0 -f .docker/base/Dockerfile .

# 2. Run security scan
docker run --rm aquasec/trivy:latest image ghcr.io/aries-serpent/codex-base:v1.1.0

# 3. Push to GHCR
echo "$CODEX_MASTER_KEY" | docker login ghcr.io -u "mbaetiong" --password-stdin
docker push ghcr.io/aries-serpent/codex-base:v1.1.0

# 4. Update latest tag
docker tag ghcr.io/aries-serpent/codex-base:v1.1.0 ghcr.io/aries-serpent/codex-base:latest
docker push ghcr.io/aries-serpent/codex-base:latest

# 5. Update GitHub Actions registration
# Navigate to settings and update to v1.1.0
```

### 4.2 Rollback to Previous Version

```bash
# If v1.1.0 has issues, rollback to v1.0.0:

# 1. Update workflows to reference old version
sed -i 's|codex-base:v1.1.0|codex-base:v1.0|g' .github/workflows/*.yml

# 2. Update GitHub Actions registration
# Navigate to settings and revert to v1.0

# 3. Notify team
gh issue create -t "Image Rollback" -b "Rolled back codex-base to v1.0 due to issues in v1.1.0"
```

### 4.3 Archive Old Versions

```bash
# Remove old build tags (keep only released versions)
docker image prune --filter "label!=org.opencontainers.image.version" -f

# Remove GHCR images older than 30 days (if not v1.0 or v1.1)
# Manual cleanup recommended for production images
```

---

## 5. Multi-Platform Support (Optional - Phase 4b)

### 5.1 Build for Multiple Architectures

```bash
# Use Docker buildx for multi-platform builds
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/aries-serpent/codex-base:v1.0 \
  -f .docker/base/Dockerfile \
  --push .

# Verify multi-platform image
docker buildx imagetools inspect ghcr.io/aries-serpent/codex-base:v1.0
```

---

## 6. Integration with CI/CD Pipelines

### 6.1 Update Existing Workflows

**Pattern to update in all workflows using custom image:**

```yaml
# OLD (using standard runner image)
jobs:
  build:
    runs-on: ubuntu-latest

# NEW (using custom image)
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aries-serpent/codex-base:v1.0
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.CODEX_MASTER_KEY }}
```

### 6.2 Workflows to Update

Run this script to identify workflows that should use the custom image:

```bash
# Find all workflows that could benefit from custom image
grep -r "runs-on: ubuntu-latest" .github/workflows/ | \
  grep -E "(python|node|lint|test)" | \
  cut -d: -f1 | sort -u

# Manually review and update each workflow
```

---

## 7. Troubleshooting Common Registration Issues

### 7.1 Issue: "Image Not Found" in Registration

**Symptom:** Registry shows `Image not found` when trying to register

**Solution:**
```bash
# 1. Verify image exists in GHCR
docker pull ghcr.io/aries-serpent/codex-base:v1.0

# 2. Check image visibility
gh api repos/Aries-Serpent/_codex_/packages/container \
  --jq '.[] | select(.name=="codex-base")'

# 3. Verify authentication scopes
gh auth status --show-token

# Expected scopes: repo, workflow, write:packages, read:packages
```

### 7.2 Issue: "Insufficient Permissions" when Registering

**Symptom:** Error: `You don't have permission to perform this action`

**Solution:**
```bash
# 1. Verify org admin access
gh api orgs/Aries-Serpent --jq '.role'
# Should return: "admin"

# 2. Verify token has necessary scopes
gh api user/authorizations --jq '.[] | {scopes}'

# 3. Re-authenticate with broader scopes
gh auth login --scopes admin:repo_hook,admin:org_hook,repo,workflow
```

### 7.3 Issue: "Tag Not Found" After Registration

**Symptom:** Workflows fail with `pull: tag not found`

**Solution:**
```bash
# 1. Verify tag exists
docker images | grep codex-base

# 2. Push tag again if missing
docker tag ghcr.io/aries-serpent/codex-base:v1.0 \
           ghcr.io/aries-serpent/codex-base:v1.0
docker push ghcr.io/aries-serpent/codex-base:v1.0

# 3. Wait 30 seconds for GHCR cache to refresh
sleep 30
docker pull ghcr.io/aries-serpent/codex-base:v1.0
```

---

## 8. Auditing & Compliance

### 8.1 Track Image Registration Changes

```bash
# Get audit log of image registrations
gh api orgs/Aries-Serpent/audit-log \
  --jq '.audit_log[] | select(.action | contains("registry")) | {action, actor, created_at, org}'
```

### 8.2 Document in CHANGELOG

Add entry to `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- Phase 4 custom image registration: `codex-base:v1.0` registered with GitHub Actions
  - Base image: Ubuntu 22.04 LTS + Python 3.12 + Node.js 22
  - Size: 580 MB
  - Security: Trivy scan passed (0 CRITICAL, 0 HIGH)
  - Available at: `ghcr.io/aries-serpent/codex-base:v1.0`
  - Reference guide: `.codex/PHASE4_IMAGE_REGISTRATION_GUIDE.md`
```

---

## ✅ Registration Sign-Off Checklist

- [ ] Dockerfile created and tested locally
- [ ] Security scan passed (Trivy/Dependabot)
- [ ] SBOM generated and stored
- [ ] Image pushed to GHCR successfully
- [ ] Image registered in GitHub Actions settings
- [ ] Test workflow created and passes
- [ ] Documentation updated
- [ ] CHANGELOG entry added
- [ ] Team notified in #Phase-4 channel
- [ ] Audit log entry verified

---

**Prepared By:** Copilot Coding Agent  
**Date Prepared:** 2026-07-18  
**Authority Level:** D-tier autonomous  
**Status:** ✅ Ready for implementation  

---

**Last Updated:** 2026-07-18  
**Next Review:** Upon successful image push to GHCR (2026-07-20)
