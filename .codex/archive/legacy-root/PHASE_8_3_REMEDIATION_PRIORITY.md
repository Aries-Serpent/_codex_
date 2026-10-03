# 🔧 PHASE 8.3 — REMEDIATION PRIORITY & PHASED APPROACH

**Workstream:** 8.3.2 — Remediation Planning  
**Track Lead:** cross-platform-filename-validator (Track 8.3)  
**Authority:** @mbaetiong (D-tier autonomy)  
**Input:** PHASE_8_3_PLATFORM_AUDIT_REPORT.md (WS1 deliverable)  
**Generated:** 2026-07-07T14:26Z  
**Status:** Planning Phase (WS2) — Ready for WS3 (Execution)

---

## 1. EXECUTIVE SUMMARY

The WS1 audit identified **31 distinct findings** across 6 categories:

| Category | Count | Status |
|----------|-------|--------|
| **Blocking (B)** | 1 finding | Must fix before cross-platform claim |
| **High (H)** | 4 findings | Breaks execution / corrupts files on Windows |
| **Medium (M)** | 3 findings | Portability friction under WSL/Git-Bash |
| **Low (L)** | 2 findings | Hygiene / future-proofing |
| **Clean (✅)** | 8 findings | No action needed |

This document provides a **phased remediation approach** across **3 execution waves**, 
coordinating case-collision fixes with complementary issues (hardcodes, symlinks, `.gitattributes`).

**Key principle:** Launch high-impact, low-risk quick wins (`.gitattributes`) **in parallel** with 
complex items (case-collision consolidation).

---

## 2. PRIORITY TIERS & PHASING STRATEGY

### Tier Structure

```
TIER 0 (Blocking Fixes)
├─ B1: Case-collision consolidation (13 groups)
└─ H1: Root .gitattributes activation

TIER 1 (High-Impact, Medium Effort)
├─ H2: Symlink conversion (2 functional code, 4 Hydra config)
├─ H3: Hardcoded repo-root replacement (44 files)
└─ H4: Linux tool-path guards (CI helpers)

TIER 2 (Medium-Impact, Medium–Low Effort)
├─ M1: /tmp/ literals → tempfile.gettempdir() (93 files)
├─ M2: Bash-only script documentation/portability (216 scripts)
└─ M3: Debian apt / sudo / systemctl guards (~33 scripts)

TIER 3 (Low-Impact, Low Effort)
├─ L1: .editorconfig move to root
└─ L2: Untrack virtualenv symlinks (.venv_ci, venv_test)
```

### Phasing Strategy: 3 Waves (concurrent execution where possible)

---

## 3. WAVE 1: CRITICAL BLOCKING FIXES (Concurrent)

**Duration:** 1–2 weeks  
**Output:** Clean Windows/macOS checkout capability  
**Dependency:** None (can start immediately)  
**Coordination:** Align Track 8.1 renames post-de-collision

### WAVE 1A: Case-Collision Consolidation (B1)

**Item:** 13 case-collision groups (28 files)  
**Effort:** **MEDIUM** (requires content merge verification + reference updates)  
**Risk:** **HIGH** (complex; highest-risk item in entire remediation)

**Execution Plan:**

1. **Reference mapping** (2–3 days):
   - Build case-sensitive reference graph for all 13 groups.
   - Identify content uniqueness (duplicate vs. distinct).
   - Generate merge plan per group.

2. **Content consolidation** (3–5 days):
   - Execute merge for each group (see COMPATIBILITY_MATRIX.md §3 for sequence).
   - Start with GROUP 1 (3-way), then GROUP 5/9 (QUICKSTARTs), then remaining 10.

3. **Reference update** (3–5 days):
   - Update all `.md` links, `.yaml` nav entries, `.py` docstrings.
   - Type A–D references (per COMPATIBILITY_MATRIX.md §4).

4. **Validation** (1–2 days):
   - Link integrity checks (markdown-link-check).
   - Re-scan for case collisions (git ls-files).
   - Git status verification (renames only, no conflicts).

**Success Criteria:**
- [ ] All 13 groups consolidated to single canonical file.
- [ ] Zero case-collision entries in `git ls-files | sort -f | uniq -d`.
- [ ] All internal references updated.
- [ ] External backlink impact assessed (may require GitHub issue for external projects).

**Rollback:** Keep backup of old filenames until validation passes (git stash if needed).

---

### WAVE 1B: Root .gitattributes Activation (H1) — PARALLEL

**Item:** Inactive `.gitattributes` (mislocated in `.config/`)  
**Effort:** **SMALL** (copy file + verify + commit)  
**Risk:** **LOW** (one-time, well-understood)

**Execution Plan:**

1. **Copy rule file** (5 min):
   ```bash
   cp .config/.gitattributes .gitattributes
   ```

2. **Verify rules activate** (5 min):
   ```bash
   git check-attr text eol -- run_updates.sh
   # Should now show: text: auto, eol: lf
   ```

3. **Force line-ending normalization** (5 min):
   ```bash
   # Remove index, re-add with new attributes
   git rm --cached -r .
   git reset --hard
   ```

4. **Commit** (1 min):
   ```bash
   git add .gitattributes
   git commit -m "chore(build): Activate line-ending normalization repo-wide via root .gitattributes"
   ```

**Success Criteria:**
- [ ] Root `.gitattributes` exists and is version-controlled.
- [ ] `git check-attr` confirms rules apply to all tracked files.
- [ ] No CRLF corruption in bash scripts (verify with `git diff --check`).

**Blast Radius:** NONE (purely protective; no side effects).

---

## 4. WAVE 2: HIGH-IMPACT FIXES (Sequential with parallel prep)

**Duration:** 2–4 weeks  
**Output:** No hardcoded paths; symlinks converted to real files  
**Dependency:** Requires Wave 1 completion for clean git state  
**Coordination:** H3 fixes may interact with Track 8.1 doc moves (coordinate ordering)

### WAVE 2A: Symlink Conversion (H2)

**Item:** 15 tracked symlinks (2 functional code, 4 Hydra config, 9 virtualenv)  
**Effort:** **SMALL–MEDIUM** (trivial copy + policy decision)  
**Risk:** **MEDIUM** (virtualenv decision may have downstream impact)

**Execution Plan:**

1. **Functional code symlinks** (Highest priority):
   
   | Symlink | Path | Fix Strategy |
   |---------|------|--------------|
   | `scripts/audit_pipeline.py` | Points to ? | Convert to real file or import-shim |
   | `scripts/ci/session_preload.py` | Points to ? | Convert to real file or import-shim |

   Action: Determine target → convert symlink to real file copy or Python import wrapper.

2. **Hydra config symlinks** (Moderate priority):
   
   | Symlink | Recommendation |
   |---------|---|
   | `configs/data` | Keep as symlink OR consolidate files |
   | `configs/model` | (same decision) |
   | `configs/tracking` | (same decision) |
   | `configs/train` | (same decision) |

   Action: Assess if configs actually need symlinks (e.g., multiple-use case) or can be consolidated.

3. **Virtualenv symlinks** (Lowest priority):
   
   | Symlink | Path | Recommendation |
   |---------|------|---|
   | `.venv_ci/bin/python*` | Links to system Python | Should not be tracked; remove from `.gitignore` |
   | `.venv_ci/lib64` | (same) | (same) |
   | `venv_test/bin/python*` | (same) | (same) |
   | `venv_test/lib64` | (same) | (same) |

   Action: Add patterns to `.gitignore` to untrack virtualenv symlinks (future hygiene).

**Success Criteria:**
- [ ] 2 functional code symlinks converted to real files (or shims).
- [ ] 4 Hydra config symlinks either consolidated or documented as intentional.
- [ ] 9 virtualenv symlinks removed from `.gitignore` (untracked).
- [ ] No broken imports or missing dependencies on Windows.

---

### WAVE 2B: Hardcoded Repo Root Replacement (H3) — SEQUENTIAL

**Item:** 44 Python files with `/home/runner/work/_codex_/_codex_` literals  
**Effort:** **MEDIUM** (systematic replacement + testing)  
**Risk:** **MEDIUM** (must verify each replacement works off-CI and on Windows)

**Execution Plan:**

1. **Create repo-root resolver utility** (1–2 days):
   ```python
   # src/codex/utils/path_utils.py or similar
   def get_repo_root() -> Path:
       """Return the repository root, cross-platform."""
       # Prefer: git rev-parse --show-toplevel
       # Fallback: Path(__file__).resolve().parents[N]
       # Fallback: environment variable
   ```

2. **Identify all 44 files** (1 day):
   ```bash
   grep -r "/home/runner/work/_codex_/_codex_" --include="*.py" | cut -d: -f1 | sort -u
   ```

3. **Replace in batches** (5–10 days, parallelizable):
   - Batch 1: `.codex/*.py` (5 files expected)
   - Batch 2: `.github/audit_artifacts_output/*.py` (1 file)
   - Batch 3: `scripts/ci/*.py` (10–15 files)
   - Batch 4: Other `.py` files (18+ files)

   For each file:
   ```python
   # Before:
   repo_root = Path("/home/runner/work/_codex_/_codex_")
   
   # After:
   from codex.utils.path_utils import get_repo_root
   repo_root = get_repo_root()
   ```

4. **Test on non-CI environment** (3–5 days):
   - Run tests locally (Linux, macOS, Windows-via-WSL).
   - Verify paths resolve correctly in all environments.

**Success Criteria:**
- [ ] Zero instances of `/home/runner/work/_codex_/_codex_` in tracked `.py` files.
- [ ] All replacements tested in non-CI environment.
- [ ] Repo-root resolver utility is robust (handles git failures, env-var fallbacks).

---

### WAVE 2C: Linux Tool-Path Guards (H4) — PARALLEL with 2B/2A

**Item:** CI helpers assuming `/opt/hostedtoolcache/...`, `/usr/bin`, etc.  
**Effort:** **SMALL** (add guards + documentation)  
**Risk:** **LOW** (guards degrade gracefully)

**Execution Plan:**

1. **Identify affected files** (1 day):
   ```bash
   grep -r "/opt/hostedtoolcache\|/usr/bin\|/usr/local/bin" --include="*.py" | cut -d: -f1 | sort -u
   ```
   Expected: ~3–5 files in `scripts/ci/` and `cognitive_app/`.

2. **Add platform guards** (2–3 days):
   ```python
   import shutil
   import sys
   
   # Instead of hardcoded path:
   codeql_exe = "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql"
   
   # Use:
   if sys.platform == "linux":
       codeql_exe = shutil.which("codeql") or "/opt/hostedtoolcache/..."
   else:
       codeql_exe = shutil.which("codeql") or fail_gracefully()
   ```

3. **Document platform-specific logic** (1 day):
   - Add comments explaining why CI runners have tool assumptions.
   - Link to relevant GitHub Actions documentation.

**Success Criteria:**
- [ ] All Linux-path assumptions guarded with platform checks.
- [ ] Scripts fail gracefully on non-Linux if tools are unavailable.
- [ ] Documentation explains CI-environment assumptions.

---

## 5. WAVE 3: MEDIUM & LOW PRIORITY IMPROVEMENTS (Concurrent, post-Wave 2)

**Duration:** 2–3 weeks  
**Output:** Full cross-platform portability and code hygiene  
**Dependency:** Wave 2 completion (cleaner git state for testing)

### WAVE 3A: /tmp/ Literal Replacement (M1)

**Item:** 93 Python files hardcoding `/tmp/`  
**Effort:** **MEDIUM** (systematic grep-and-replace)  
**Risk:** **LOW** (tempfile module is standard, safe)

**Execution Plan:**

1. **Identify all 93 files** (1 day):
   ```bash
   grep -r "/tmp/" --include="*.py" | grep -v "# " | grep -v docstring | cut -d: -f1 | sort -u
   ```

2. **Replace in batches** (5–7 days):
   ```python
   # Before:
   report_path = "/tmp/report.json"
   
   # After (option A — if file needs to persist):
   import tempfile
   with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
       report_path = f.name
   
   # After (option B — if file can be cleaned up):
   with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
       report_path = f.name
       # Use report_path here; auto-cleaned on file close
   ```

3. **Test for side effects** (3–5 days):
   - Ensure temp files are properly cleaned up.
   - Check Windows temp directory behavior.

**Success Criteria:**
- [ ] Zero instances of `/tmp/` in source code (comments/docstrings may remain).
- [ ] All temp-file operations use `tempfile` module.
- [ ] Tests pass on Windows (temp directory behavior verified).

---

### WAVE 3B: Bash-Only Script Documentation & Portability (M2)

**Item:** 216 bash scripts with no Windows equivalents  
**Effort:** **LARGE** (triage + selective porting)  
**Risk:** **LOW** (documenting existing state, optional porting)

**Execution Plan:**

1. **Triage scripts by traffic/priority** (3–5 days):
   - **Tier A (High traffic):** setup, test, ci, build, run, validate (~47 scripts)
   - **Tier B (Medium traffic):** fix, check, audit, deploy (~25 scripts)
   - **Tier C (Low traffic):** specialized/one-off (~144 scripts)

2. **Document WSL/Git-Bash requirement** (1–2 days):
   - Add header comment to all 216 scripts:
     ```bash
     #!/usr/bin/env bash
     # ⚠️ Platform: Linux/macOS/Windows-via-WSL or Git-Bash
     # Windows native cmd/PowerShell not supported.
     ```

3. **Selective porting (optional, future)** (2–3 weeks, deferred):
   - Port Tier-A scripts (47) to Python for true cross-platform support.
   - Maintain bash versions for backward compatibility.

**Success Criteria:**
- [ ] All 216 scripts have platform disclaimer comment.
- [ ] Tier-A scripts identified and flagged for future Python porting.
- [ ] README / CONTRIBUTING.md updated with WSL/Git-Bash requirement.

---

### WAVE 3C: Linux-Tool Guards (apt, sudo, systemctl, sed -i, grep -P) (M3) — PARALLEL with 3B

**Item:** ~33 scripts using Debian `apt`, 10 using `sudo`, 5 `systemctl`, 10 `sed -i`, 1 `grep -P`  
**Effort:** **MEDIUM** (case-by-case guards + fallbacks)  
**Risk:** **LOW** (guards fail gracefully, document limitations)

**Execution Plan:**

1. **Identify affected scripts** (1 day):
   ```bash
   grep -r "apt\|apt-get\|sudo\|systemctl\|sed -i\|grep -P" *.sh | cut -d: -f1 | sort -u
   ```

2. **Add guards per category** (5–7 days):

   | Command | Guard Strategy |
   |---------|---|
   | `apt` / `apt-get` (25–33 scripts) | `if ! command -v apt >/dev/null; then error "apt required; use WSL or install manually."; fi` |
   | `sudo` (10 scripts) | Check if running as root; fallback without sudo if already root |
   | `systemctl` (5 scripts) | Guard with `if command -v systemctl`; document systemd requirement |
   | `sed -i` (10 scripts) | Use `sed -i.bak` or Python-based in-place edit |
   | `grep -P` (1 script) | Use `-E` or port to Python `re` module |

3. **Documentation** (1 day):
   - Add notes to CONTRIBUTING.md about Linux-tool dependencies.
   - Link to WSL/Git-Bash setup guides.

**Success Criteria:**
- [ ] All ~33 apt scripts have guard checking availability.
- [ ] All 10 sudo scripts handle root/non-root cases.
- [ ] systemctl/sed/grep edge cases documented and handled gracefully.
- [ ] CONTRIBUTING.md lists tool requirements.

---

### WAVE 3D: Config Hygiene (L1, L2)

**Item:** 2 low-priority items  
**Effort:** **SMALL** (20–30 minutes total)  
**Risk:** **NONE** (cosmetic changes)

**Execution Plan:**

| Item | Action | Effort |
|------|--------|--------|
| **L1:** Move `.editorconfig` to root | Copy `.config/.editorconfig` → `./.editorconfig` | 5 min |
| **L2:** Untrack virtualenv symlinks | Add `.venv_ci/` and `venv_test/` to `.gitignore` | 5 min |

**Success Criteria:**
- [ ] Root `.editorconfig` exists and applies LF rules across repo.
- [ ] Virtualenv directories are untracked (git status shows no virtualenv files).

---

## 6. BLAST RADIUS ANALYSIS BY ITEM

### Blocking Issues (Zero tolerance)

| Item | Blast Radius | Impact |
|------|------|--------|
| **B1 (Case collisions)** | **REPO-WIDE** | Silent file loss on Windows/macOS; blocks cross-platform claim |
| **H1 (.gitattributes)** | **216 bash scripts** | CRLF corruption; broken shebangs on Windows |

**Combined:** Case collisions + missing .gitattributes = **repo is not usable on Windows**.

---

### High-Impact Issues (Must fix for Windows support)

| Item | Count | Blast Radius | Impact |
|------|-------|-------|--------|
| **H2 (Symlinks)** | 15 files | 2 code + 4 config | Broken symlinks; import failures on Windows |
| **H3 (Hardcoded /home)** | 44 files | Multiple modules | Paths resolve to nonexistent locations off-CI |
| **H4 (Linux tool paths)** | ~3–5 files | CI helpers | Tool discovery fails; CI jobs fail on non-GHA runners |

---

### Medium-Impact Issues (Portability friction)

| Item | Count | Blast Radius | Impact |
|------|-------|-------|--------|
| **M1 (/tmp/ literals)** | 93 files | Various modules | Temp files inaccessible on Windows |
| **M2 (Bash-only scripts)** | 216 scripts | All scripting | Scripts unusable without WSL/Git-Bash |
| **M3 (Linux tools)** | ~33–40 scripts | Setup/CI helpers | Debian-dependent; fail on other distros / Windows |

---

### Low-Impact Issues (Hygiene)

| Item | Count | Blast Radius | Impact |
|------|-------|-------|--------|
| **L1 (.editorconfig)** | 1 file | Editor behavior | Inconsistent LF enforcement |
| **L2 (virtualenv symlinks)** | 9 files | None (untracked) | Clutter in git status |

---

## 7. DEPENDENCY GRAPH (Execution Constraints)

```
Wave 1 (Blocking Fixes)
├─ B1: Case-collision consolidation
│  └─ Prereq: Reference mapping complete
│  └─ Blocks: Track 8.1 bulk renames, Track 8.2 moves
│
└─ H1: Root .gitattributes (PARALLEL)
   └─ No prereq; can run in parallel with B1

Wave 2 (High-Impact) — Requires Wave 1 complete
├─ H2: Symlink conversion (PARALLEL with H3)
├─ H3: Hardcoded /home replacement (PARALLEL with H2, sequential phases)
└─ H4: Linux tool-path guards (PARALLEL)

Wave 3 (Medium/Low) — Requires Wave 2 complete
├─ M1: /tmp/ literals (PARALLEL with M2, M3)
├─ M2: Bash documentation (PARALLEL with M1, M3)
├─ M3: Linux-tool guards (PARALLEL with M1, M2)
└─ L1/L2: Config hygiene (PARALLEL, post-Wave 2)
```

---

## 8. SUCCESS METRICS (Per Wave)

### Wave 1 Success Criteria
- [ ] **B1:** All 13 case-collision groups consolidated; zero case collisions in git.
- [ ] **H1:** Root `.gitattributes` active; `git check-attr` confirms rules apply.
- [ ] **Combined:** Repository passes Windows/macOS clean checkout test.

### Wave 2 Success Criteria
- [ ] **H2:** 2 code symlinks converted; 4 config symlinks resolved; 9 virtualenv symlinks untracked.
- [ ] **H3:** Zero `/home/runner/...` literals in `.py` files; all replacements tested cross-platform.
- [ ] **H4:** Linux tool paths guarded; CI helpers work on non-GHA runners.
- [ ] **Combined:** Repository has no hardcoded paths; works off-CI and on Windows.

### Wave 3 Success Criteria
- [ ] **M1:** Zero `/tmp/` literals; all temps use `tempfile` module.
- [ ] **M2:** All 216 scripts documented with platform requirements.
- [ ] **M3:** ~33 apt scripts guarded; sudo/systemctl/sed/grep edge cases handled.
- [ ] **L1/L2:** Config files cleaned up; virtualenv symlinks untracked.
- [ ] **Combined:** Full cross-platform portability achieved; POSIX/Windows compatibility documented.

---

## 9. COORDINATION & COMMUNICATION

### Stakeholder Notifications

| Stakeholder | Notification | Timeline |
|-------------|---|---|
| **Track 8.1 (Doc renames)** | De-collision sequence + canonical filenames | End of Wave 1 |
| **Track 8.2 (Bulk moves)** | Final canonical paths; case-collision cleared | End of Wave 1 |
| **CI/CD team** | Hardcode replacements affect CI scripts | During Wave 2 |
| **Developers** | WSL/Git-Bash requirement; platform guards | During Wave 3 |

---

## 10. ROLLBACK PROCEDURES

### Wave 1 (Case Collisions)

**Rollback trigger:** If reference graph is incomplete or content merge fails.

```bash
# Option 1: Revert commits
git revert <commit-hash>

# Option 2: Restore from backup
git restore docs/ARCHITECTURE.md  # etc.
```

**Verification:** Re-run case-collision scan; confirm 13 groups still exist if rollback needed.

---

### Wave 2 (Hardcodes)

**Rollback trigger:** If cross-platform tests fail.

```bash
# Revert repo-root resolver changes
git revert <commit-hash>

# Re-insert hardcoded paths if necessary
git restore <file.py>
```

**Verification:** Run tests on Windows/macOS; confirm paths resolve.

---

### All Waves

**Post-rollback:** Analyze root cause; re-plan; retry with adjusted approach.

---

## 11. TIMELINE ESTIMATE

| Wave | Duration | Critical Path |
|------|----------|---|
| **Wave 1 (B1 + H1)** | 1–2 weeks | B1 dominates (case-collision merge complex) |
| **Wave 2 (H2 + H3 + H4)** | 2–4 weeks | H3 dominates (44 files, cross-platform testing) |
| **Wave 3 (M1 + M2 + M3 + L1/L2)** | 2–3 weeks | M2 dominates (216 scripts to triage/document) |
| **Total** | **5–9 weeks** | Parallelizable; 6–7 weeks realistic with 1–2 FTE |

---

## 12. OPEN QUESTIONS FOR WS3 EXECUTION

1. **Case-collision content merge:** Are files duplicates or unique content?
   → **Action:** Reference mapping phase (Wave 1A step 1) answers this.

2. **Symlink policy (H2):** Keep Hydra config symlinks or consolidate?
   → **Action:** Architecture review before Wave 2A.

3. **Porting bash scripts to Python (M2 Tier A):** Is this a Wave 3 stretch goal or defer to Phase 9?
   → **Action:** PM/TL decision; not blocking cross-platform support.

4. **External backlinks (GROUP 1 & 5):** How many external projects link to old case-sensitive filenames?
   → **Action:** GitHub search + create issues in external projects if needed.

---

## 13. SUCCESS CRITERIA (WS2 → WS3 Handoff)

✅ **Phased approach defined** across 3 waves (Blocking → High → Medium/Low)  
✅ **Effort estimates provided** per item (SMALL / MEDIUM / LARGE)  
✅ **Risk assessment completed** per item and wave  
✅ **Dependency graph created** (execution constraints documented)  
✅ **Blast radius analyzed** (item-by-item and repo-wide)  
✅ **Success metrics defined** per wave and item  
✅ **Rollback procedures** documented  
✅ **Timeline estimated** (5–9 weeks, 1–2 FTE)  
✅ **Coordination points** identified (Track 8.1, 8.2, CI/CD, developers)  
✅ **Open questions** flagged for WS3 execution  

---

## 14. NEXT STEPS (WS3 — Execution)

1. **Approve phased approach** (PM/TL sign-off).
2. **Launch Wave 1 execution:**
   - Reference mapping for case collisions.
   - Parallel root `.gitattributes` activation.
3. **Execute Wave 2 (post-Wave 1):**
   - Symlink conversion.
   - Hardcode replacement.
   - Linux tool guards.
4. **Execute Wave 3 (post-Wave 2):**
   - `/tmp/` literal replacement.
   - Script documentation & portability.
   - Linux-tool guards.
5. **Final validation:**
   - Windows/macOS clean checkout.
   - All cross-platform tests pass.
   - Documentation updated.

---

**Document Status:** ✅ PLANNING COMPLETE (WS2 deliverable)  
**Ready for:** WS3 Execution Phase  
**Maintainer:** Track 8.3 — cross-platform-filename-validator  
**Timestamp:** 2026-07-07T14:26Z
