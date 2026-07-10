# Lane 2 Brief: Offline Bootstrap & Dependency Supply

**Lane 2 Owner:** `packaging-validation-agent` (dependencies), `documentation-quality-agent` (bootstrap guide)  
**Duration:** Days 3-9 (Phase 1) + Days 10-16 (Phase 2)  
**Authority:** @mbaetiong D-tier approved  
**Phase 0 Decision Leverage:** Strategic Decision #3 (Lockfile-based offline strategy)

---

## 🎯 Lane 2 Objective

Enable reproducible, offline-first installation by delivering a hash-locked dependency manifest and air-gap bootstrap workflow for all 3 package profiles.

---

## 📋 Deliverables

### Phase 1 (Days 3-9)

1. **lockfile.lock**
   - Format: pip-tools compatible (compatible with `pip install -r lockfile.lock`)
   - Contents: All transitive dependencies (1,200+ packages for full profile)
   - Includes: Package name, version, SHA256 hash, URL
   - Coverage: All 3 profiles (core, runtime, full) in single lockfile
   - Format example:
     ```
     omegaconf==2.3.11 \
         --hash=sha256:abc123def456... \
         --hash=sha256:ghi789jkl012...
     pydantic==2.4.0 \
         --hash=sha256:mno345pqr678...
     # ... 1,200+ more entries
     ```

2. **OFFLINE_BOOTSTRAP.sh** (Draft)
   - Bash script for air-gap installation workflow
   - Steps:
     1. Download all wheels to `./wheelhouse/` (from mirror or archive)
     2. Verify SHA256 hashes match lockfile
     3. Install from wheelhouse only (no network)
   - Usage: `bash OFFLINE_BOOTSTRAP.sh [core|runtime|full]`
   - Platform support: Linux/macOS (Windows: batch variant)

3. **Dependency Audit Report**
   - Identify external registries (PyPI is default, others?)
   - List any network-dependent packages (at import time)
   - Categorize by offline viability: safe, problematic, requires pre-download
   - Output: CSV with package name, registry, safety assessment

### Phase 2 (Days 10-16)

4. **Air-Gap Installation Validation**
   - Test on 3 platforms: Ubuntu 22.04, macOS 12+, Windows 10+
   - Procedure:
     1. Download wheels to wheelhouse (simulated offline)
     2. Run OFFLINE_BOOTSTRAP.sh in isolated network
     3. Verify install succeeds without internet
     4. Test all entrypoints work
   - Output: Validation report per platform

5. **OFFLINE_BOOTSTRAP.sh (Final)**
   - Refined based on Phase 2 testing
   - Error handling: clear messages for network issues
   - Compatibility: Works on all 3 platforms
   - Documentation: Usage guide, troubleshooting

---

## 🚀 Execution Roadmap

### Days 3-4: Dependency Analysis

**Task 2.1: Generate Initial Lockfile**
- Use pip-tools or poetry to lock dependencies
- Include all transitive deps for "full" profile
- Command example: `pip-compile pyproject.toml --all-extras --resolver=backtracking`
- Output: lockfile.lock (draft, ~2,000-3,000 lines)

**Task 2.2: Hash Verification**
- Ensure all packages have SHA256 hashes
- Validate hashes against PyPI
- Identify any unhashable packages (pip requires them)
- Output: Hash verification report

**Task 2.3: Dependency Audit**
- Scan lockfile for network-dependent packages
- Check for import-time network calls (e.g., certifi CA updates)
- Identify pre-download requirements (PyTorch weights, models)
- Output: Audit report, categorized by safety

### Days 5-6: Bootstrap Script Development

**Task 2.4: Wheelhouse Architecture**
- Design wheelhouse directory structure:
  ```
  wheelhouse/
  ├── core/          # core profile wheels
  ├── runtime/       # runtime profile wheels
  ├── full/          # all wheels for full profile
  └── hashes.txt     # SHA256 manifest
  ```
- Determine download mechanism: mirror, artifact download, archive extract
- Output: Wheelhouse design document

**Task 2.5: OFFLINE_BOOTSTRAP.sh Development**
- Script template:
  ```bash
  #!/bin/bash
  set -e
  
  PROFILE=${1:-core}
  WHEELHOUSE="${WHEELHOUSE:-./wheelhouse}"
  
  # Validate profile
  if [[ ! "$PROFILE" =~ ^(core|runtime|full)$ ]]; then
    echo "Usage: $0 [core|runtime|full]"
    exit 1
  fi
  
  # Verify hashes
  cd "$WHEELHOUSE"
  sha256sum -c hashes.txt || {
    echo "ERROR: Hash verification failed. Wheels may be corrupted."
    exit 1
  }
  
  # Install from wheelhouse
  pip install --no-index --find-links . -r "$PROFILE.lock"
  
  echo "✅ Installation complete. Run: codex --version"
  ```
- Support profiles: core, runtime, full
- Platform support: Linux/macOS (Windows: batch file variant)

### Days 7-8: Testing & Refinement

**Task 2.6: Lockfile Rebuild Test**
- Goal: Verify deterministic reproduction
- Steps:
  1. Delete current venv
  2. Create fresh venv
  3. Install from lockfile: `pip install -r lockfile.lock`
  4. Generate new lockfile: `pip-compile ... > lockfile.new`
  5. Diff: `diff lockfile.lock lockfile.new` (should be identical or only order changes)
- Output: Determinism validation report

**Task 2.7: Bootstrap Script Testing**
- Create offline simulation environment
- Download wheels to wheelhouse/
- Run OFFLINE_BOOTSTRAP.sh with no internet
- Verify installation succeeds
- Test entrypoints: `codex --version`
- Output: Bootstrap script validation report

### Days 9+: Documentation Handoff (to Lane 5)

**Task 2.8: Bootstrap Guide (for Lane 5)**
- Write user-facing guide: `OFFLINE_.codex/archive/misc/INSTALL.md`
- Include:
  - Prerequisites (Python 3.12, pip, bash/batch)
  - Download procedure (where to get wheels)
  - Hash verification (how to verify integrity)
  - Step-by-step installation
  - Troubleshooting (common errors)
- Output: Draft guide, ready for Lane 5 to integrate into full docs

---

## 🔗 Cross-Lane Dependencies

### Lane 2 ← Lane 1 (Dependencies ← Packaging)

**Dependency:** Lane 1 finalizes dependencies by Day 7
- Lane 1 pyproject.toml determines which packages to lock
- Lane 2 generates lockfile from Lane 1 dependencies
- **Sync Point:** By Day 7, Lane 1 confirms final optional-dependencies groups

### Lane 2 → Lane 3 (Dependencies → Cognitive Runtime)

**Dependency:** Lane 3 cognitive extraction avoids import-time network calls
- Lane 2 audit identifies any network-dependent patterns in cognitive modules
- Lane 3 refactors to make cognitive engine import-safe
- **Sync Point:** Day 5, share dependency audit with Lane 3

### Lane 2 → Lane 4 (Dependencies → Network Policy)

**Dependency:** Lane 4 policy includes any approved external registries
- Lane 2 identifies if non-PyPI registries are needed
- Lane 4 adds to allowlist if required
- **Sync Point:** Day 6, confirm no external registries in core/runtime profiles

### Lane 2 → Lane 6 (Dependencies → Validation)

**Dependency:** Lane 6 air-gap validation uses Lane 2 lockfile + bootstrap script
- Lane 2 delivers final lockfile by Phase 2 Day 14
- Lane 6 validates offline install using lockfile in Phase 4
- **Sync Point:** Lane 6 has lockfile + bootstrap script by Phase 2 Day 16

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| Lockfile generated & hashed | All 1,200+ deps locked with SHA256 | packaging-validation-agent |
| Deterministic rebuild | Rebuild = identical lockfile (order-independent) | packaging-validation-agent |
| Bootstrap script works | OFFLINE_BOOTSTRAP.sh succeeds without internet | packaging-validation-agent |
| No import-time network calls | Audit confirms cognitive modules are import-safe | packaging-validation-agent |
| Air-gap validation passed | Install from wheelhouse succeeds on 3 platforms | packaging-validation-agent |
| Phase 1 gate (Day 9) | Lockfile draft + bootstrap tested | orchestrator-agent |
| Phase 2 gate (Day 16) | Air-gap validation complete, final bootstrap | orchestrator-agent |

---

## 📌 Key Decisions from Phase 0

**Strategic Decision #3: Lockfile-based offline strategy**
- ✅ APPROVED in .codex/archive/misc/INTELLIGENCE_CAMPAIGN_BASELINE.md
- Mechanism: pip-tools compatible lockfile with SHA256 hashes
- Offline bootstrap: Wheelhouse + verification script
- Validation: Air-gap install on representative platforms

---

## 🛠️ Tools & Commands

```bash
# Generate lockfile
pip install pip-tools
pip-compile pyproject.toml --all-extras --resolver=backtracking -o lockfile.lock

# Verify hashes
sha256sum -c hashes.txt

# Install from lockfile
pip install -r lockfile.lock

# Test offline install
pip install --no-index --find-links ./wheelhouse -r lockfile.lock

# Simulate air-gap (block network)
sudo iptables -A OUTPUT -d 0.0.0.0/0 -j DROP  # Linux (undo: -D instead of -A)
```

---

## 📞 Escalation

**Dependency Conflicts?** Report to orchestrator-agent with:
- Conflicting packages (e.g., `package-a==1.0` conflicts with `package-b>=2.0`)
- Proposed resolution (upgrade, downgrade, or exclude)
- Impact assessment (does it block core, runtime, or full profile only?)

**Example:**
> Conflict: transformers==5.12.1 requires torch>=2.6, but torch latest is 2.8. Resolution: Pin torch to compatible version range. Impact: Affects runtime + full profiles only, core profile unaffected.

