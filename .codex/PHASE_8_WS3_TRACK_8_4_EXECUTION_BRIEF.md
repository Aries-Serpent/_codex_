# 📦 Track 8.4 WS3 Execution Brief — Dependency Standardization & Conflict Resolution

**Authority:** @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Priority:** 🔵 **PARALLEL** (independent of Tracks 8.1-8.3, run simultaneously)  
**Timeline:** 2026-07-07T18:00Z → 2026-07-08T14:00Z (20-hour execution window)  
**Status:** Ready for immediate parallel execution

---

## 📋 Executive Summary

Track 8.4 resolves 3 critical dependency conflicts, implements 18 dependency pinning strategies, and standardizes all lock files (`uv.lock`, `requirements-*.txt`) across the repository. This work is independent of Tracks 8.1-8.3 and can execute in parallel.

**Key Deliverables:**
- ✅ 3 critical dependency conflicts resolved (identified in WS2 audit)
- ✅ 18 pinning strategies implemented
- ✅ `uv.lock` updated with all conflict resolutions
- ✅ `requirements-*.txt` regenerated from `uv.lock`
- ✅ Dependency validation suite passes (offline-viable distribution verified)
- ✅ Cyclonedx SBOM updated

---

## 🎯 Execution Objective

**Primary Goal:** Implement WS2 dependency standardization strategy (DEPENDENCY_STRATEGY.md) to achieve reproducible, offline-viable dependency distribution.

**Success Criteria:**
- ✅ All 3 conflict categories resolved without version downgrades
- ✅ All 18 pinning rules applied to lock files
- ✅ Zero transitive dependency divergence between `uv.lock` and `requirements-*.txt`
- ✅ Offline wheelhouse buildable with all dependencies
- ✅ Cyclonedx SBOM with SHA256 checksums generated
- ✅ Reproducibility validation passes

---

## 📊 Planning Reference Documents

**Primary Source:**
- `.codex/PHASE_8_4_DEPENDENCY_STRATEGY.md` (11.8 KB, 3 conflict resolutions + 18 pinning strategy)

**Supporting Docs:**
- `uv.lock` (existing lock file — to be updated)
- `requirements/` directory (4+ requirements files)
- `pyproject.toml` (dependency declarations)

**Previous Findings:**
- `.codex/PHASE_8_4_DEPENDENCY_AUDIT.md` (WS1 audit baseline)

---

## 🚀 Execution Workflow (Agent Handoff)

### Agent Assignment
**Primary Agents:** `dependency-conflict-agent` + `packaging-validation-agent`  
**Supporting Agents:** `cache-management-agent` (offline wheelhouse), `unified-governance-gate`

### Workflow Steps

#### Step 1: Load Dependency Strategy (15 min)
1. Read DEPENDENCY_STRATEGY.md to extract:
   - 3 conflict categories and proposed resolutions
   - 18 pinning rules (version bounds per package)
   - Offline distribution requirements (core vs. runtime vs. full profiles)
2. Verify current `uv.lock` state
3. Identify all `requirements-*.txt` files needing regeneration

#### Step 2: Conflict Resolution Phase 1 — Core Conflicts (2 hours)
**From DEPENDENCY_STRATEGY.md:**

**Conflict 1:** [Package A vs. Package B version mismatch]
- **Current State:** [conflict details from audit]
- **Resolution:** [approach from strategy]
- **Action:** Pin Version X of Package A, Y of Package B

```bash
# Update pyproject.toml with resolved versions
# Example:
# Before: package-a = ">=2.0,<3.0"
# After: package-a = "2.5.0"

# Update uv.lock
uv pip compile --upgrade-package package-a==2.5.0
```

**Conflict 2:** [Secondary conflict...]
**Conflict 3:** [Tertiary conflict...]

**Validation After Phase 1:**
```bash
# Verify lock file consistency
uv pip verify

# Check for unresolved conflicts
grep -E "^# (conflict|unresolved)" uv.lock | wc -l
# Should be 0
```

#### Step 3: Implement Pinning Rules (2 hours)
**From DEPENDENCY_STRATEGY.md, 18 pinning strategies:**

**Rule 1:** [Package X: pin to specific version range]
```bash
# Update pyproject.toml
# [tool.uv.dependencies]
# package-x = "1.2.3"  # Pinned for reproducibility
```

**Rule 2-18:** [Apply remaining 17 rules...]

**Commands (example):**
```bash
# For each rule in DEPENDENCY_STRATEGY.md:
uv pip compile \
  --upgrade-package package-name==version \
  --upgrade-package other-package==version

# Regenerate uv.lock
uv lock
```

**Validation:**
```bash
# Verify all rules applied
grep "package-name.*==" uv.lock | grep "1.2.3"

# Check total lock file size (should be deterministic)
wc -l uv.lock
# Expected: stable line count (within 10 lines of previous)
```

#### Step 4: Generate Lock Files (1 hour)
**Target:** Regenerate all `requirements-*.txt` from `uv.lock`

**Actions:**
```bash
# List all requirements files
find . -name "requirements-*.txt" -o -name "requirements.txt"

# Regenerate from uv.lock for each extras profile
uv pip export --output-file requirements.txt
uv pip export --extras dev --output-file requirements-dev.txt
uv pip export --extras test --output-file requirements-test.txt
uv pip export --extras all --output-file requirements-all.txt

# Verify all regenerated files
for f in requirements*.txt; do
  echo "=== $f ==="
  head -5 $f
done
```

**Validation:**
```bash
# Verify no duplicate entries
for f in requirements*.txt; do
  awk -F'==' '{print $1}' $f | sort | uniq -d | head -5
done
# Should return empty (no duplicates)

# Verify all pins are exact versions
grep -v "^#" requirements.txt | grep -v "^$" | grep "==" | wc -l
# Should equal total package count
```

#### Step 5: Offline Wheelhouse Generation (2 hours)
**Target:** Build complete offline distribution

**Actions:**
```bash
# Create wheelhouse directory
mkdir -p wheelhouse/

# Download all wheels with SHA256 hashes
pip download \
  --no-deps \
  --no-build-isolation \
  --python-version 312 \
  -r requirements-all.txt \
  -d wheelhouse/

# Generate SHA256 manifest
cd wheelhouse && sha256sum *.whl > SHA256SUMS && cd ..

# Verify all wheels present
wc -l wheelhouse/SHA256SUMS
# Expected: 100+ wheels for full profile
```

**Validation:**
```bash
# Test offline installation on clean environment
python -m venv test_offline_env
source test_offline_env/bin/activate
pip install --no-index --find-links wheelhouse -r requirements-all.txt
# Should succeed without network calls
```

#### Step 6: Update Cyclonedx SBOM (30 min)
**Target:** Generate updated Software Bill of Materials with SHA256 checksums

**Actions:**
```bash
# Install cyclonedx-python if needed
pip install cyclonedx-bom

# Generate SBOM from requirements
cyclonedx-py \
  --output-file sbom-output.json \
  --format json

# Create SBOM with wheel SHA256 hashes
# Format:
# {
#   "components": [
#     {
#       "name": "package-a",
#       "version": "1.2.3",
#       "hashes": [
#         {
#           "alg": "SHA256",
#           "content": "[SHA256_HASH_FROM_WHEELHOUSE]"
#         }
#       ]
#     }
#   ]
# }
```

**Commit SBOM:**
```bash
git add sbom-output.json
```

#### Step 7: Reproducibility Validation (1 hour)
**Target:** Verify all dependency changes are reproducible

**Actions:**
```bash
# Run reproducibility test suite
python scripts/dependency_reproducibility_check.py

# Expected output:
# ✅ uv.lock deterministic (same hash on 3 generations)
# ✅ requirements-*.txt regenerable from uv.lock
# ✅ Offline wheelhouse buildable from requirements-all.txt
# ✅ SBOM matches actual wheel set
```

**Success Criteria:**
- All reproducibility checks pass
- No warning messages
- Lock file hash stable across 3 runs

---

## 📋 Success Checklist

- [ ] All 3 conflicts identified and resolved
- [ ] No version downgrades (only compatible upgrades)
- [ ] All 18 pinning rules implemented
- [ ] `uv.lock` regenerated and committed
- [ ] All `requirements-*.txt` regenerated and committed
- [ ] Offline wheelhouse buildable (100+ wheels)
- [ ] Cyclonedx SBOM with SHA256 hashes generated
- [ ] Reproducibility validation: ✅ PASS
- [ ] Single dependency commit: "refactor(deps): Resolve conflicts + implement pinning strategy"

---

## ⚠️ Risk Mitigation

**Potential Issues:**
1. **Transitive conflict loops** — Use `uv resolve` to detect circular dependencies
2. **Platform-specific wheels** — Verify wheels for Python 3.12+ target platform
3. **Network errors during download** — Retry with `--retries 5`

**Rollback Plan (if needed):**
```bash
git checkout HEAD~3 -- uv.lock requirements*.txt
uv lock  # Regenerate from pyproject.toml
# Restart with simpler strategy (one conflict at a time)
```

---

## 🔄 Dependency Management

**INDEPENDENT OF:** Tracks 8.1, 8.2, 8.3
- Reason: Pure dependency work, no file system impact

**CAN RUN IN PARALLEL WITH:** All other WS3 tracks
- Reason: Separate scope (pyproject.toml, lock files only)

**BLOCKS:** Future dependency updates until completed
- Reason: Lock files must be canonical source of truth

---

## 📊 Metrics & Reporting

**Expected Outputs:**
- Conflicts resolved: 3 of 3
- Pinning rules applied: 18 of 18
- Total dependencies pinned: 80-120 (direct + transitive)
- Wheelhouse size: 300-500 MB
- Execution time: 8-12 hours
- Completion time: 2026-07-08T14:00Z (estimated)

**Success Criteria Met When:**
- All lock files committed
- Reproducibility validation: ✅ PASS
- SBOM generated with SHA256 checksums
- Offline installation test succeeds

---

## 🎯 Next Phase Handoff

**Upon Completion:**
1. Reply with execution summary
2. Include commit SHA: `git rev-parse HEAD`
3. Post status: "Track 8.4 WS3 COMPLETE — Dependencies standardized, offline distribution ready"
4. Summary table: conflicts resolved, pinning rules applied, wheelhouse metrics

**Expected Reply Format:**
```markdown
## Track 8.4 Execution Summary
- Conflicts Resolved: 3 of 3
- Pinning Rules Applied: 18 of 18
- Lock Files Updated: ✅ uv.lock, requirements-*.txt
- Offline Wheelhouse: ✅ Built (N wheels, M MB)
- SBOM: ✅ Generated with SHA256 hashes
- Reproducibility Test: ✅ PASS
- Execution Time: N hours
- Commit SHA: [SHA]
- Status: ✅ COMPLETE / ⚠️ PARTIAL / ❌ ISSUES
- Ready for WS4: [YES / NO]
```

---

## 📞 Support & Escalation

**If stuck on:**
- Transitive conflicts → Run `uv resolve --verbose` to see dependency tree
- Wheel download failures → Check network access, retry with proxy
- Reproducibility failures → Compare lock file hashes, verify no random components

**Escalation Point:**
- If conflicts require major version downgrades → Stop, document impact, escalate
- Authority: D-tier autonomous (GO CONTINUE unless escalation needed)

---

**Authority:** @mbaetiong D-tier autonomous  
**Entry Point:** `.codex/PHASE_8_WS2_SESSION_CONSOLIDATION_HANDOFF.md`  
**Status:** 🟢 **READY FOR AGENT ACTIVATION** (PARALLEL WITH TRACKS 8.1-8.3)
