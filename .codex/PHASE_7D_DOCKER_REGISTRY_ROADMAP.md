# 🚀 Phase 7D Docker Registry Integration Roadmap

**Campaign:** Docker Phase 1 - Complete Audit Documents  
**Generated:** 2026-06-20T07:54:04Z  
**Repository:** Aries-Serpent/_codex_  
**Status:** ✅ **REGISTRY ROADMAP COMPLETE**

---

## Executive Summary

### Registry Integration Status

| Component | Current State | Target State | Status |
|-----------|---------------|--------------|--------|
| **GHCR (GitHub Container Registry)** | Partial | Full | 🟡 Needs completion |
| **DockerHub** | Not configured | Supported | 📋 Planned |
| **Tag Strategy** | Implicit | Formally documented | 🟡 Needs definition |
| **Retention Policies** | None | 3-tier policy | 📋 Planned |
| **Automated Push Workflows** | Manual | Fully automated | 🟡 Needs implementation |
| **Image Signing** | None | Cosign + attestations | 📋 Phase 2 |

**Overall Status:** 🟡 **READY FOR PHASE 2 EXECUTION**

---

## Part 1: Current State Assessment

### GitHub Container Registry (GHCR)

**Status:** ✅ **Partially configured**

**Current Configuration:**
- **Organization:** `ghcr.io/aries-serpent`
- **Images:** Available at `ghcr.io/aries-serpent/_codex_:{variant}`
- **Access Control:** Private (requires GitHub token)
- **Push Method:** Manual or GitHub Actions

**Existing Workflows:**
- ✅ `.github/workflows/build-preview-image.yml` — Publishes preview image
- ⚠️ No unified push workflow for all 8 variants

**Action Required:** Create unified multi-variant push workflow (Phase 2)

---

### DockerHub

**Status:** ❌ **Not configured**

**Rationale:**
- GitHub-native project → GHCR is sufficient
- DockerHub optional for public distribution
- Can add later if community distribution needed

**Future Setup (optional):**
```
DockerHub Organization: ariesserp  (or similar)
Repositories:
  - ariesserp/_codex_ (main, mirrors GHCR)
  - ariesserp/_codex_-gpu (GPU variant)
  - ariesserp/_codex_-cpu (CPU variant)
```

**Recommendation:** ⏳ **Consider Phase 3** (not blocking for Phase 1)

---

## Part 2: Image Naming & Tagging Strategy

### Naming Convention

```
REGISTRY/ORGANIZATION/REPOSITORY/VARIANT:TAG
  ↓         ↓              ↓         ↓       ↓
ghcr.io / aries-serpent / _codex_ / cpu : v1.0.0
```

**Registry Endpoints:**

| Registry | Endpoint | Privacy | Bandwidth | Use Case |
|----------|----------|---------|-----------|----------|
| **GHCR** | `ghcr.io/aries-serpent/_codex_:{tag}` | Private | High | Primary (GitHub-native) |
| **DockerHub** | `ariesserp/_codex_:{tag}` | Public/Private | Unlimited | Mirror (optional) |

---

### Image Variants & Registry Tags

#### Core Production Images

| Variant | Purpose | Primary Tag | Aliases | Platforms |
|---------|---------|-------------|---------|-----------|
| **prod-cpu** | CPU-only runtime | `cpu-v1.0.0` | `cpu-latest`, `cpu-main` | amd64, arm64 |
| **prod-gpu** | GPU runtime (CUDA) | `gpu-v1.0.0` | `gpu-latest`, `gpu-main` | amd64 |
| **prod-base** | Foundation layer | `base-v1.0.0` | `base-latest` | amd64, arm64 |

#### Specialized Images

| Variant | Purpose | Primary Tag | Aliases | Platforms |
|---------|---------|-------------|---------|-----------|
| **preview** | Cognitive Brain API | `preview-v1.0.0` | `preview-latest` | amd64, arm64 |
| **ci** | CI/CD pipeline tools | `ci-v1.0.0` | `ci-latest` | amd64 |
| **embedding** | Embedding inference | `embedding-v1.0.0` | `embedding-latest` | amd64, arm64 |
| **optimized** | Performance variant | `optimized-v1.0.0` | `optimized-latest` | amd64 |

#### Development Images

| Variant | Purpose | Primary Tag | Aliases | Platforms |
|---------|---------|-------------|---------|-----------|
| **local** | Local dev (minimal) | `local-dev-v1.0.0` | `local-dev-latest` | amd64 |
| **local-codex-env** | Full local env | `codex-env-v1.0.0` | `codex-env-latest` | amd64 |

---

### Version Scheme

**Primary: Semantic Versioning (SemVer)**

```
X.Y.Z[-prerelease][+build]

Examples:
  v1.0.0                    Release version
  v1.0.0-rc.1               Release candidate
  v1.0.0-beta.1             Beta release
  v1.0.0-alpha.1            Alpha release
  v1.0.0-dev.20260620       Development build
  v1.0.0+build.123          Build metadata
```

**Branch-Based Tags:**

```
cpu-main                   Latest from main branch
cpu-develop                Latest from develop branch
cpu-feature-xyz            Feature branch builds
cpu-pr-42                  Pull request builds
```

**Latest Tags:**

```
cpu-latest                 Always points to latest release
cpu-latest-amd64           Multi-platform variant
cpu-latest-arm64           Multi-platform variant
```

---

### Complete Tag Matrix

#### Example: CPU Variant (prod-cpu)

```
ghcr.io/aries-serpent/_codex_:cpu-v1.0.0              ← Release
ghcr.io/aries-serpent/_codex_:cpu-v1.0.0-arm64        ← Release (ARM)
ghcr.io/aries-serpent/_codex_:cpu-v1.0.0-amd64        ← Release (AMD64)
ghcr.io/aries-serpent/_codex_:cpu-latest              ← Latest release
ghcr.io/aries-serpent/_codex_:cpu-latest-arm64        ← Latest release (ARM)
ghcr.io/aries-serpent/_codex_:cpu-latest-amd64        ← Latest release (AMD64)
ghcr.io/aries-serpent/_codex_:cpu-main                ← Latest from main branch
ghcr.io/aries-serpent/_codex_:cpu-pr-42               ← Pull request preview
```

---

## Part 3: GHCR Integration Steps

### Step 1: Verify GHCR Organization Access

**Checklist:**
- ✅ Organization: `github.com/Aries-Serpent`
- ✅ Container registry enabled
- ✅ GitHub token with `write:packages` scope

**Verification Command:**
```bash
gh auth status  # Verify GitHub CLI authenticated
gh repo create --source=. --remote=origin --push  # Not needed if repo exists
```

---

### Step 2: Create GHCR Push Workflow

**File:** `.github/workflows/docker-build-push.yml`

**Template:**
```yaml
name: Docker Build & Push

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write

    strategy:
      matrix:
        variant:
          - cpu
          - gpu
          - embedding
          - ci
          - preview
          - optimized
          - local

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch,prefix=${{ matrix.variant }}-
            type=semver,pattern=${{ matrix.variant }}-v{{version}}
            type=semver,pattern=${{ matrix.variant }}-v{{major}}.{{minor}}
            type=sha,prefix=${{ matrix.variant }}-,suffix=-{{branch}}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./docker/Dockerfile.${{ matrix.variant }}
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

### Step 3: Configure Workflow Triggers

**Automated Push Events:**
- ✅ Release tags: `v1.0.0` → Push as `{variant}-v1.0.0`
- ✅ Main branch commits → Push as `{variant}-main`
- ✅ Pull requests → Skip push, use `load: true` for smoke-test

**Manual Triggers:**
```yaml
workflow_dispatch:
  inputs:
    variant:
      description: Specific variant to build
      required: false
```

---

## Part 4: Retention Policies

### 3-Tier Retention Strategy

#### Tier 1: Production Releases (365 days)

**Policy:**
- Keep all semver releases: `v1.0.0`, `v1.0.1`, etc.
- Keep last 10 minor versions
- Keep last 3 major versions
- Retention: 365 days minimum

**Rationale:** Production deployments may reference old versions for reproducibility

---

#### Tier 2: Development Builds (90 days)

**Policy:**
- Keep branch images: `cpu-main`, `gpu-develop`
- Keep last 30 builds per branch
- Retention: 90 days

**Rationale:** Regular CI builds; old versions less valuable

---

#### Tier 3: PR & Feature Builds (30 days)

**Policy:**
- Keep PR images: `cpu-pr-42`
- Keep feature branch images: `cpu-feature-xyz`
- Retention: 30 days

**Rationale:** Temporary builds; cleanup after review/merge

---

### GHCR Retention Configuration

**File:** `.github/container_settings/retention.yaml` (if supported)

**Alternative: GitHub Actions Cleanup Workflow**

```yaml
name: Docker Retention Cleanup

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday 2am UTC
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      packages: write
      contents: read

    steps:
      - name: Delete old production images
        run: |
          # Delete images older than 365 days, except last 10 releases
          # Requires GitHub CLI and registry access
          
      - name: Delete old development images
        run: |
          # Delete images older than 90 days
          
      - name: Delete old PR images
        run: |
          # Delete images older than 30 days
```

---

## Part 5: Multi-Platform Build Strategy

### Platform Support Matrix

| Variant | amd64 | arm64 | ppc64le | s390x |
|---------|-------|-------|---------|-------|
| **prod-cpu** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **prod-gpu** | ✅ | ❌ (NVIDIA only) | ❌ | ❌ |
| **prod-base** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **preview** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **ci** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **embedding** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **optimized** | ✅ | ✅ | ⏳ Future | ⏳ Future |
| **local-dev** | ✅ | ❌ (dev-only) | ❌ | ❌ |

### Multi-Platform Build Configuration

**Docker Buildx Command:**
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/aries-serpent/_codex_:cpu-v1.0.0 \
  --push \
  ./docker/Dockerfile.cpu
```

**GitHub Actions Integration:**
```yaml
- name: Build multi-platform image
  uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    tags: ghcr.io/aries-serpent/_codex_:cpu-v1.0.0
    push: true
```

---

## Part 6: DockerHub Mirroring (Optional)

### Recommended Setup (Phase 3)

**Organization:** `ariesserp` (or `aries-serpent` if available)

**Repositories:**

```
ariesserp/_codex_          (main mirror)
ariesserp/_codex_-gpu      (GPU variant)
ariesserp/_codex_-cpu      (CPU variant)
ariesserp/_codex_-preview  (Preview API)
```

### Automated Sync Workflow

**Option 1: GitHub Actions Mirror**

```yaml
name: Mirror to DockerHub

on:
  push:
    tags: ['v*']

jobs:
  mirror:
    runs-on: ubuntu-latest
    steps:
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Pull from GHCR and push to DockerHub
        run: |
          docker pull ghcr.io/aries-serpent/_codex_:cpu-v${TAG}
          docker tag ghcr.io/aries-serpent/_codex_:cpu-v${TAG} \
                     ariesserp/_codex_:cpu-v${TAG}
          docker push ariesserp/_codex_:cpu-v${TAG}
```

**Option 2: DockerHub Automated Build** (simplest)
- Link DockerHub repo to GitHub
- Triggers automatic build on tag
- Simpler but less control

---

## Part 7: Image Signing & Attestation

### Phase 2 Implementation (Post-Phase 1)

**Tools:**
- **Cosign** — Image signing and verification
- **SLSA Provenance** — Build attestation
- **SBOM** — Software bill of materials

**Workflow Addition:**

```yaml
- name: Generate SBOM
  run: |
    syft ghcr.io/aries-serpent/_codex_:cpu-v1.0.0 \
      --output cyclonedx-json > sbom.json

- name: Sign image
  run: |
    cosign sign --key ${{ secrets.COSIGN_KEY }} \
      ghcr.io/aries-serpent/_codex_:cpu-v1.0.0

- name: Generate attestation
  run: |
    cosign attest --predicate sbom.json \
      ghcr.io/aries-serpent/_codex_:cpu-v1.0.0
```

---

## Part 8: Implementation Timeline

### Phase 1 (Week 1): Foundation
- ✅ Define tagging strategy
- ✅ Document variant registry locations
- ⏳ Plan retention policies
- **Status:** COMPLETE (this document)

### Phase 2 (Week 2-3): Execution
- ⏳ Create multi-variant push workflow
- ⏳ Test push to GHCR for all 8 variants
- ⏳ Implement retention cleanup
- ⏳ Add multi-platform builds (amd64, arm64)

### Phase 3 (Week 4): Hardening
- ⏳ Add image signing (cosign)
- ⏳ Generate SBOMs for all variants
- ⏳ Set up SLSA provenance attestation
- ⏳ Optional: DockerHub mirror setup

### Phase 4+ (Future): Distribution
- ⏳ Public DockerHub mirroring
- ⏳ Docker Official Images (if approved)
- ⏳ Container registry federation
- ⏳ OCI artifact hosting

---

## Part 9: Troubleshooting & FAQs

### FAQ 1: How do I pull an image from GHCR?

```bash
# Authenticate (one-time)
echo $GH_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/aries-serpent/_codex_:cpu-v1.0.0

# Run
docker run ghcr.io/aries-serpent/_codex_:cpu-v1.0.0
```

---

### FAQ 2: What if GHCR push fails?

**Checklist:**
- ✅ GitHub token has `write:packages` scope
- ✅ Organization settings allow container registry
- ✅ Disk space on runner (50+ GB needed)
- ✅ Network connectivity to ghcr.io

**Debug:**
```bash
docker login ghcr.io -u ${{ github.actor }} -p ${{ secrets.GITHUB_TOKEN }}
docker push ghcr.io/aries-serpent/_codex_:cpu-v1.0.0 --verbose
```

---

### FAQ 3: How do I delete images from GHCR?

```bash
# Not directly deletable via docker CLI
# Use GitHub Container Registry web UI or GitHub CLI:

gh api --method DELETE \
  /orgs/aries-serpent/packages/container/_codex_/versions/12345
```

---

## Next Steps

1. ✅ **PHASE_7D_DOCKER_REGISTRY_ROADMAP.md** - THIS DOCUMENT (COMPLETE)
2. ⏳ **PHASE_7D_DOCKER_DOCUMENTATION.md** - Final document: BUILD/DEPLOY/TROUBLESHOOT

---

**Document Version:** 1.0.0  
**Campaign Phase:** Docker Phase 1 - Registry Planning  
**Next Review:** Phase 2 - Workflow Implementation
