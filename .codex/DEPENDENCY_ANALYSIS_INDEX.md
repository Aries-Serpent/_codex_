# PHASE 4 CUSTOM IMAGES — COMPREHENSIVE DEPENDENCY ANALYSIS INDEX

**Date:** 2026-07-18  
**Scope:** Complete dependency inventory of all 219 active workflows in `.github/workflows/`  
**Authority:** D-tier autonomous (@mbaetiong)  

---

## 📊 DELIVERABLES SUMMARY

### 1. **Complete Dependency Inventory**
**File:** `PHASE4_DEPENDENCY_INVENTORY.csv`  
- **Format:** CSV with columns: workflow, category, dependency, version, count
- **Size:** 2,312 rows (including header)
- **Coverage:** 219 workflows scanned
- **Content:** Every dependency extracted from every workflow file

**Categories:**
- **Actions:** 1,196 records (GitHub Actions tools)
- **Languages:** 432 records (Python, Node, Go, Rust, Java, .NET versions)
- **Tools:** 352 records (System utilities)
- **Pip:** 326 records (Python packages)
- **Npm:** 5 records (Node packages)
- **Apt:** 1 record (System packages)

### 2. **Dependency Analysis Report**
**File:** `PHASE4_DEPENDENCY_ANALYSIS.md`  
- **Content:** 8.4 KB, 252 sections
- **Highlights:**
  - Language version ranges (Python 3.10→3.13, Node 18→22, Go 1.20→1.23, Rust stable)
  - Top 20 GitHub Actions (with usage percentages)
  - System tools breakdown (git, curl, make, gcc, etc.)
  - Top 30 Pip packages (with workflow percentages)
  - Version pinning recommendations
  - Tools compatibility matrix
  - Implementation checklist for Phase 4

### 3. **Tools Compatibility Matrix**
**File:** `PHASE4_TOOLS_COMPATIBILITY_MATRIX.md`  
- **Content:** Exact versions for all languages and tools
- **Sections:**
  - Language runtime versions (min/max/recommended)
  - GitHub Actions tools (Top 20 with pinning guidance)
  - System tools (critical tools with version requirements)
  - Pre-install pip packages (high-priority for base image)

### 4. **Version Pinning Strategy**
**File:** `PHASE4_VERSION_PINNING.md`  
- **Content:** Exact Dockerfile directives for each language
- **Includes:**
  - Python 3.12 installation instructions
  - Node.js 22.x setup (via NodeSource)
  - Go 1.23 binary installation
  - Rust stable via rustup
  - System packages (build-essential, curl, git, jq, etc.)
  - Pre-install pip packages
  - Build optimization tips
  - Version override strategy for actions

### 5. **High-Priority Dependency List**
**File:** `PHASE4_HIGH_PRIORITY_DEPENDENCIES.md`  
- **Content:** Curated list of must-have dependencies
- **Sections:**
  - MUST-HAVE languages & runtimes
  - MUST-HAVE system tools
  - SHOULD-HAVE pip packages (>15% workflow usage)
  - Optional but common tools

### 6. **JSON Summary**
**File:** `PHASE4_DEPENDENCY_SUMMARY.json`  
- **Format:** Machine-readable JSON
- **Content:**
  - Aggregated statistics
  - Language version ranges
  - Top actions and tools
  - Critical tools list with percentages

---

## 🔍 KEY FINDINGS

### Language Versions (Detected)

| Language | Min | Max | Recommended |
|---|---|---|---|
| **Python** | 3.10 | 3.13 | 3.12 (LTS) |
| **Node** | 18 | 22 | 22 (LTS) |
| **Go** | 1.20 | 1.23 | 1.22+ |
| **Rust** | 1.70 | stable | stable |

### Critical System Tools (>50% of workflows)

| Tool | Workflows | Percentage | Priority |
|---|---|---|---|
| bash | 219 | 100% | CRITICAL |
| python | 211 | 96.3% | CRITICAL |
| git | 203 | 92.7% | CRITICAL |
| docker | 179 | 81.7% | HIGH |
| make | 176 | 80.4% | HIGH |
| grep | 148 | 67.6% | HIGH |
| curl | 137 | 62.6% | MEDIUM |
| jq | 127 | 58.0% | MEDIUM |

### Top GitHub Actions (Most Used)

1. `actions/checkout` - Standard repo checkout
2. `actions/setup-python` - Python runtime
3. `actions/setup-node` - Node.js runtime
4. `actions/setup-go` - Go runtime
5. `actions/setup-rust` - Rust runtime
6. `actions/upload-artifact` - Artifact management
7. `actions/download-artifact` - Artifact retrieval
8. `github/codeql-action` - Security scanning
9. `codecov/codecov-action` - Coverage reporting
10. `super-linter/super-linter` - Code linting

### Top Pip Packages (Most Used)

1. `setuptools` (20+ workflows)
2. `wheel` (20+ workflows)
3. `requests` (15+ workflows)
4. `pytest` (15+ workflows)
5. `pyyaml` (12+ workflows)
6. `pytest-cov` (10+ workflows)
7. `black` (8+ workflows)
8. `ruff` (8+ workflows)

---

## 📋 IMPLEMENTATION CHECKLIST FOR PHASE 4

### Phase 4A: Dockerfile Creation
- [ ] Select base image (ubuntu:24.04 or debian:bookworm-slim)
- [ ] Install system dependencies (gcc, make, git, curl, jq, etc.)
- [ ] Install Python 3.12 with pip, venv
- [ ] Install Node.js 22.x via NodeSource
- [ ] Install Go 1.23 binary
- [ ] Install Rust via rustup (stable)
- [ ] Pre-warm pip cache with top 30 packages
- [ ] Configure PATH and environment variables

### Phase 4B: Image Building & Testing
- [ ] Build custom image locally
- [ ] Test image with 20+ representative workflows
- [ ] Benchmark: startup time vs. ubuntu-latest
- [ ] Verify all language runtimes work
- [ ] Verify all system tools available
- [ ] Test pip packages pre-installed correctly

### Phase 4C: Registry & Deployment
- [ ] Push image to GHCR (ghcr.io/aries-serpent/...)
- [ ] Tag image with semantic version (e.g., v1.0.0)
- [ ] Document image location and usage
- [ ] Update workflow runner references
- [ ] Monitor for regression in affected workflows

### Phase 4D: Documentation
- [ ] Document version strategy
- [ ] Document how to override versions with actions/setup-*
- [ ] Document breaking changes (if any)
- [ ] Create migration guide for dependent workflows

---

## 📊 DEPENDENCY DISTRIBUTION

### By Category
```
actions    1,196  (52%)
tools        352  (15%)
language     432  (19%)
pip          326  (14%)
npm            5  (0.2%)
apt            1  (0.0%)
```

### Coverage
- **Unique GitHub Actions:** 50+
- **Unique System Tools:** 20+
- **Unique Pip Packages:** 100+
- **Unique Npm Packages:** 5
- **Unique Apt Packages:** 1

---

## 🎯 PHASE 4 STRATEGY

### Version Selection Criteria
1. **LTS Preference:** Always choose LTS versions when available
2. **Latest Minor:** If no LTS, use latest minor version
3. **Compatibility:** Select versions compatible with 90%+ of workflows
4. **Security:** Ensure latest security patches

### Base Image Philosophy
- **Pre-install common tools** → Faster cold starts
- **Allow action overrides** → Maximum flexibility
- **Optimize layer caching** → Efficient builds
- **Minimize size** → Faster image pulls

### Performance Goals
- **Startup time:** <30 seconds (vs. ubuntu-latest ~60s)
- **Build time:** 15% faster than baseline
- **Disk footprint:** ~8-12 GB (ubuntu-latest base ~5GB)
- **Cache efficiency:** >80% hit rate for pip packages

---

## 🔄 WORKFLOW COMPATIBILITY

### Guaranteed Compatible (with actions override)
- Workflows using `actions/setup-python` → Can request any Python version
- Workflows using `actions/setup-node` → Can request any Node version
- Workflows using `actions/setup-go` → Can request any Go version
- Workflows using `actions/setup-rust` → Can request any Rust version

### Fallback Strategy
If a workflow requires a version not pre-installed in base image:
1. GitHub Actions setup-* automatically downloads and installs
2. No fallback needed—full version flexibility preserved
3. Performance penalty: +5-10 seconds for download/install

---

## 📁 FILE REFERENCE

| File | Purpose | Size |
|---|---|---|
| `PHASE4_DEPENDENCY_INVENTORY.csv` | Complete dependency list | 124 KB |
| `PHASE4_DEPENDENCY_ANALYSIS.md` | Analysis report | 8.4 KB |
| `PHASE4_TOOLS_COMPATIBILITY_MATRIX.md` | Tools versions | 2.8 KB |
| `PHASE4_VERSION_PINNING.md` | Dockerfile directives | 2.5 KB |
| `PHASE4_HIGH_PRIORITY_DEPENDENCIES.md` | Must-have list | 599 B |
| `PHASE4_DEPENDENCY_SUMMARY.json` | JSON summary | 2.0 KB |

---

## 🚀 NEXT STEPS

1. **Review** this index and all supporting documents
2. **Create Dockerfile** using Version Pinning guidance
3. **Build locally** and test against sample workflows
4. **Push to registry** (GHCR or DockerHub)
5. **Update runner configuration** to use new image
6. **Monitor workflows** for improvement in startup time
7. **Iterate** based on real-world performance data

---

## 📞 CONTACTS & REFERENCES

- **Analysis Date:** 2026-07-18
- **Workflows Scanned:** 219
- **Authority:** D-tier autonomous
- **Repository:** Aries-Serpent/_codex_
- **Related Issues:** Phase 4 Custom Images Implementation

---

*End of Dependency Analysis Index*
