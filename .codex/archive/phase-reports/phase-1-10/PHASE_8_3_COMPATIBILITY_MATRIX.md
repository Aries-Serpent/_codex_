# 📊 PHASE 8.3 — PLATFORM COMPATIBILITY MATRIX

**Workstream:** 8.3.2 — Compatibility Matrix & Sequencing
**Track Lead:** cross-platform-filename-validator (Track 8.3)
**Authority:** @mbaetiong (D-tier autonomy)
**Authority Gate:** GO CONTINUE (all gates approved)
**Date Generated:** 2026-07-03T02:00Z
**Input:** PHASE_8_3_PLATFORM_AUDIT_REPORT.md (WS1 deliverable)

---

## EXECUTIVE SUMMARY

This matrix ranks all 11 identified compatibility issues by **severity** (blocking → high → medium → low),
**blast radius** (files affected / systems impacted), **remediation effort** (estimated person-hours),
**risk of side-effects**, and **cross-track dependencies**. The matrix informs the **remediation sequencing**
(see PHASE_8_3_REMEDIATION_PRIORITY.md) and gates the 8.3.3 Critical Fixes workstream.

---

## COMPATIBILITY ISSUE MATRIX

| ID | Finding | Category | Platform Impact | Files Affected | Severity | Effort | Risk | Dependencies | Status |
|:--:|---------|----------|-----------------|-----------------|----------|--------|------|--------------|--------|
| **B1** | **13 case-collision file groups (28 docs)** | Filename | 🪟 WIN 🍎 MAC | 28 MD files in `docs/` | 🔴 **BLOCKING** | **M** (8–12h) | 🔴 High: broken links if refs missed | **8.2 (doc moves)** | Pending |
| **H1** | **`.gitattributes` inactive repo-wide** | Config | 🪟 WIN (CRLF risk) | 216 `.sh` files + root | 🟠 **HIGH** | **S** (1–2h) | 🟢 Low: one-time normalize | None (fast-path) | Pending |
| **H2** | **15 tracked symlinks** | Filesystem | 🪟 WIN (unreliable) | 15 symlinks (2 critical code) | 🟠 **HIGH** | **M** (4–6h) | 🟡 Medium: policy decision needed | None (independent) | Pending |
| **H3** | **44 hardcoded repo-root paths** | Code Path | 🪟 WIN 🐧 LIN 🍎 MAC | 44 `.py` files | 🟠 **HIGH** | **M** (6–8h) | 🟡 Medium: must verify each | None (independent) | Pending |
| **H4** | **Linux tool-path assumptions** | Code Path | 🪟 WIN | ~8 CI helper files | 🟠 **HIGH** | **S** (2–4h) | 🟡 Medium: CI-scoped | None (independent) | Pending |
| **M1** | **93 hardcoded `/tmp/` paths** | Code Path | 🪟 WIN | 93 `.py` files | 🟡 **MEDIUM** | **M** (6–8h) | 🟢 Low: safe fallback exists | None (independent) | Pending |
| **M2** | **216 bash-only scripts** | Shell | 🪟 WIN | 216 `.sh` files | 🟡 **MEDIUM** | **L** (document; ~2h triage) | 🟢 Low: WSL/Git-Bash works | None (independent) | Pending |
| **M3** | **Linux-specific commands in scripts** | Shell | 🪟 WIN (apt/sudo/systemctl) | ~33 scripts | 🟡 **MEDIUM** | **L** (2–4h guards) | 🟢 Low: WSL/Git-Bash works | None (independent) | Pending |
| **L1** | **`.editorconfig` mislocated** | Config | ℹ️ Editor UX | 1 file (`.config/.editorconfig`) | 🔵 **LOW** | **S** (<1h) | 🟢 Low: hygiene only | None (independent) | Pending |
| **L2** | **Virtualenv symlinks tracked** | Filesystem | ℹ️ Hygiene | 9 symlinks (`.venv_ci/`, `venv_test/`) | 🔵 **LOW** | **S** (<1h) | 🟢 Low: gitignore only | None (independent) | Pending |
| **L3** | **Path-separator construction** | Code Path | ✅ CLEAN | 0 files | ✅ **NONE** | 0h | N/A | N/A | ✅ Complete |

---

## DETAILED ISSUE BREAKDOWN

### 🔴 BLOCKING

#### B1: Case-Collision File Groups (13 groups / 28 files)

**Problem:** Git tracks these files as distinct on case-**sensitive** systems (Linux) but case-insensitive
filesystems (Windows NTFS, macOS APFS default) silently overwrite duplicates, causing:
- One file survives checkout; others are lost or cause `git status` dirty tree
- Inbound reference links break
- Checkout may fail with conflict messages

**Affected Files:**
```
Group 1 (3-way)  docs/ARCHITECTURE.md | docs/Architecture.md | docs/architecture.md
Group 2          docs/CI.md | docs/ci.md
Group 3          docs/CLI.md | docs/cli.md
Group 4          docs/QUALITY_GATES.md | docs/quality_gates.md
Group 5          docs/QUICKSTART.md | docs/quickstart.md
Group 6          docs/TROUBLESHOOTING.md | docs/troubleshooting.md
Group 7          docs/agent/INDEX.md | docs/agent/index.md
Group 8          docs/guides/INDEX.md | docs/guides/index.md
Group 9          docs/guides/QUICKSTART.md | docs/guides/quickstart.md
Group 10         docs/security/INCIDENT_RESPONSE.md | docs/security/incident_response.md
Group 11         docs/validation/Tokenization_Validation.md | docs/validation/tokenization_Validation.md  # pragma: allowlist secret
Group 12         .codex/reports/EXECUTIVE_SUMMARY.md | .codex/reports/executive_summary.md
Group 13         reports/EXECUTIVE_SUMMARY.md | reports/executive_summary.md
```

**Remediation Strategy:**
1. Choose **canonical casing** for each group (recommend **lowercase** for index/summary files for consistency,
   or follow existing repo convention if one exists)
2. Merge content from colliding files if they differ
3. Delete duplicates from git tracking (`git rm --cached`)
4. Update **all inbound references** via grep+sed or reference-graph tool
5. Commit consolidated state

**Cross-Track Dependency:** 
- **Track 8.2:** Document restructuring (Phase 8.2.2) will move/reorganize docs. **Sequence 8.3 B1
  de-collision BEFORE 8.2 bulk moves** to avoid churn (resolve case collisions first, then move finalized
  files).

**Effort:** Medium (8–12 hours) — the manual reference update is the costliest part.
**Risk:** High — broken links if references are incomplete.
**Windows/macOS Blocker:** YES — checkout will fail or produce dirty tree.

---

### 🟠 HIGH

#### H1: `.gitattributes` Inactive Repo-Wide

**Problem:** The repository ships an excellent `.gitattributes` file **in `.config/`** with correct rules:
```
* text=auto eol=lf
*.sh  text eol=lf
*.bash text eol=lf
*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf
```

However, Git only applies `.gitattributes` to files within its own directory tree and below.
Since this file is at `.config/.gitattributes`, it only governs files inside `.config/`.

**Impact:**
- All 216 bash scripts in `scripts/`, `tools/`, `.github/`, etc. are **not subject to LF normalization**
- On a Windows clone with `core.autocrlf=true` (Git-for-Windows default), scripts risk **CRLF injection**
- Scripts fail to run under WSL/Git-Bash with: `bad interpreter: /usr/bin/env bash^M`
- This silently undermines the very cross-platform intent the config file was written for

**Remediation Strategy:**
1. **Copy** `.config/.gitattributes` to repository root (`.gitattributes`)
2. Verify activation: `git check-attr text eol -- scripts/run_updates.sh` → should report `text: auto`, `eol: lf`
3. Optionally add a root `.editorconfig` with `end_of_line = lf` for editor consistency
4. **One-time re-normalize:** `git add --renormalize .` (or use `core.safecrlf=false` + `git checkout --theirs -- .`)

**Effort:** Small (1–2 hours) — mostly copying + verification.
**Risk:** Low — one-time renormalization is safe; `.gitattributes` is passive.
**Windows/macOS Blocker:** YES — CRLF corruption risk to every bash script.
**Fast-Path Candidate:** YES — **this is a quick win** and highest-impact for shell integrity.

---

#### H2: 15 Tracked Symlinks (2 critical code + 13 others)

**Problem:** Symlinks (git mode `120000`) are not reliably materialized on Windows (require Developer Mode
and `core.symlinks=true`); otherwise, Git writes them as plain text files containing the target path string.

**Affected Symlinks:**
```
CRITICAL (functional code):
  scripts/audit_pipeline.py → target: ../path/to/real/file
  scripts/ci/session_preload.py → target: ../path/to/real/file

HIGH (Hydra config):
  configs/data → target
  configs/model → target
  configs/tracking → target
  configs/train → target

LOW (virtualenv links — should arguably be untracked):
  .venv_ci/bin/python, .venv_ci/bin/python3, .venv_ci/bin/python3.12, .venv_ci/lib64
  venv_test/bin/python, venv_test/bin/python3, venv_test/bin/python3.12, venv_test/lib64
```

**Remediation Strategy:**
1. **For critical code symlinks (2):** Convert to real files or import shims; decide on policy
   (prefer real files or import-time resolution via `__init__.py`?)
2. **For Hydra config symlinks (4):** Evaluate if these are strictly necessary or if configs can be
   replicated/consolidated
3. **For virtualenv symlinks (9):** Add to `.gitignore` (they should not be tracked; virtualenvs are
   generated on-demand)

**Effort:** Medium (4–6 hours) — policy decisions + testing for code symlinks; straightforward for
virtualenvs.
**Risk:** Medium — must test code imports after conversion; Hydra config symlinks may require integration testing.
**Windows/macOS Blocker:** YES — symlinks materialize as text files on Windows, breaking imports.

---

#### H3: 44 Hardcoded Repo-Root Paths (`/home/runner/work/_codex_/_codex_`)

**Problem:** 44 Python files hardcode the absolute repository root path, assuming the checkout is at
`/home/runner/work/_codex_/_codex_`. This breaks:
- Local development (different checkout path)
- Windows machines (different path structure)
- Non-GitHub-Actions CI systems

**Representative Examples:**
```
.codex/ast_migrator.py:129            os.chdir('/home/runner/work/_codex_/_codex_')
.codex/batch_migrator.py:118          os.chdir('/home/runner/work/_codex_/_codex_')
.codex/phase_9_3_report_generator.py:15  Path("/home/runner/work/_codex_/_codex_/.codex/...")
.github/audit_artifacts_output/validate_audit_artifacts.py:8  ROOT = Path("/home/runner/work/_codex_/_codex_")
scripts/ci/fix_remaining_security_issues.py:51  repo_root = Path("/home/runner/work/_codex_/_codex_")
scripts/ci/github_api_trickle.py:422  build_codeql_db(source_root="/home/runner/work/_codex_/_codex_")
```

**Remediation Strategy:**
1. Create a **centralized `repo_root()` resolver function** (recommended in `src/codex/utils/path_utils.py`):
   ```python
   def repo_root() -> Path:
       """Resolve repository root dynamically."""
       # Try git first (most reliable)
       try:
           result = subprocess.run(
               ["git", "rev-parse", "--show-toplevel"],
               capture_output=True, text=True, check=True
           )
           return Path(result.stdout.strip())
       except:
           # Fallback: walk up from __file__ until .git found
           current = Path(__file__).resolve()
           while current != current.parent:
               if (current / ".git").exists():
                   return current
               current = current.parent
           raise RuntimeError("Could not find repository root")
   ```
2. Replace all 44 hardcoded literals with `repo_root()`
3. Test each file's import/execution after replacement

**Effort:** Medium (6–8 hours) — most time is verification & testing, not replacement itself.
**Risk:** Medium — must verify each module still imports/executes correctly.
**Windows/macOS Blocker:** YES — path mismatch prevents execution.

---

#### H4: Linux Tool-Path Assumptions (~8 CI helper files)

**Problem:** Several CI helper scripts hardcode Linux tool paths:
```
scripts/ci/github_api_trickle.py:413  "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql"
cognitive_app/src/server/cli_api_server.py:803  ("/usr/bin", "/usr/local/bin", "/bin")
```

These are not portable to Windows or macOS without platform-specific conditional logic.

**Remediation Strategy:**
1. Use `shutil.which()` to locate tools dynamically instead of hardcoding paths
2. Add platform guards (e.g., `if sys.platform == "win32"`) where needed
3. Document WSL/Git-Bash requirement for scripts that assume `/usr` structure
4. For CI-specific paths (e.g., CodeQL), use GitHub Actions environment variables if available

**Effort:** Small (2–4 hours) — mostly straightforward path replacement + testing.
**Risk:** Medium (CI-scoped) — impacts GitHub Actions runners; low risk to local development.
**Windows/macOS Blocker:** Partial — GitHub Actions runners are CI-only; local Windows development uses WSL/Git-Bash.

---

### 🟡 MEDIUM

#### M1: 93 Hardcoded `/tmp/` Paths

**Problem:** 93 Python files assume Linux `/tmp/` directory exists:
```
.github/agents/infra-linter-agent/agent/reporter.py:78  os.getenv("CODEX_DB_PATH", "/tmp/codex_brain.db")
.github/scripts/collect_link_health_metrics.py:61       '--report-file', '/tmp/link_report_metrics.json'
.github/scripts/post_copilot_followup.py:28             if str(path.absolute()).startswith('/tmp/')
```

Windows has no native `/tmp/` equivalent; scripts fail or ignore temp files.

**Remediation Strategy:**
1. Replace all `/tmp/` literals with `tempfile.gettempdir()`:
   ```python
   import tempfile
   temp_dir = tempfile.gettempdir()  # Returns OS-specific temp dir
   ```
2. Use `tempfile.NamedTemporaryFile()` for file creation (auto-cleanup)
3. Verify no assumptions about `/tmp/` path structure (e.g., permissions, symlinks)

**Effort:** Medium (6–8 hours) — mostly grep+replace + testing.
**Risk:** Low — `tempfile` module is well-tested and safe; this is a straightforward fix.
**Windows/macOS Blocker:** Partial — Windows has `%TEMP%`, macOS has `/var/tmp/` or `/tmp/` (with caveats).

---

#### M2: 216 Bash-Only Scripts (No Windows-Native Equivalents)

**Problem:** All 216 shell scripts are bash-idiomatic and require bash interpreter. There are no `.bat`,
`.cmd`, or `.ps1` equivalents for Windows native execution. Scripts run on Linux, macOS, and
Windows-via-WSL/Git-Bash, but not in native Windows `cmd` or PowerShell.

**Remediation Strategy (Triage-Based):**
1. **Keep as-is + document WSL requirement:** For setup/test/ci scripts (~150 scripts) — document that
   native Windows users need WSL or Git-Bash
2. **Port high-traffic scripts to Python:** For core setup/test/ci workflows (~47 scripts) — create
   Python equivalents for true Windows portability
3. **Defer virtualenv-related scripts:** `.venv_ci/`, `venv_test/` setup scripts can remain bash if users
   are expected to use WSL

**Effort:** Low (triage ~2 hours) — porting is a separate workstream.
**Risk:** Low — WSL/Git-Bash is industry-standard for Windows developers; documented requirement is acceptable.
**Windows/macOS Blocker:** No — WSL/Git-Bash mitigates.

---

#### M3: Linux-Specific Commands in Scripts (~33 scripts)

**Problem:** Scripts use Debian-specific or Linux-only commands that don't work on Windows without WSL:
- `apt` / `apt-get` (25 scripts) — Debian package manager
- `sudo` (10 scripts) — privilege escalation
- `systemctl` (5 scripts) — systemd-only service management
- `sed -i` (10 scripts) — GNU vs BSD syntax differs
- Others: `grep -P`, `chmod`, `mktemp`, `ln -s`

**Remediation Strategy:**
1. Add platform guards and WSL checks:
   ```bash
   if command -v apt-get &> /dev/null; then
       apt-get install ...
   else
       echo "apt not found; WSL required for package install"
       exit 1
   fi
   ```
2. For `sed -i`, use Python for cross-platform in-place edits
3. Document that these scripts require WSL/Git-Bash on Windows
4. Normalize `grep -P` to standard POSIX `grep` if possible

**Effort:** Low (2–4 hours) — mostly guards + documentation.
**Risk:** Low — WSL/Git-Bash is standard; guards fail gracefully.
**Windows/macOS Blocker:** No — documented WSL requirement is acceptable.

---

### 🔵 LOW

#### L1: `.editorconfig` Mislocated

**Problem:** `.config/.editorconfig` sets `end_of_line = lf`, but EditorConfig resolution walks upward
from the edited file; a config in `.config/` only applies to files inside `.config/`. Root and `scripts/`
files don't get LF enforcement in editors.

**Remediation Strategy:**
1. Copy `.config/.editorconfig` to repository root
2. Or add an EditorConfig entry in root `.editorconfig` with broader scope

**Effort:** < 1 hour
**Risk:** Low — hygiene only; no functional impact.

---

#### L2: Virtualenv Symlinks Tracked (9 files)

**Problem:** `.venv_ci/` and `venv_test/` directories contain generated virtualenv symlinks that should
not be tracked in git.

**Remediation Strategy:**
1. Add to `.gitignore`:
   ```
   .venv_ci/
   venv_test/
   ```
2. Run `git rm --cached .venv_ci .venv_test` (or similar)

**Effort:** < 1 hour
**Risk:** Low — cleanup only.

---

### ✅ CLEAN

#### L3: Path-Separator Construction (0 violations)

**Finding:** No systemic manual-separator anti-patterns detected. The codebase predominantly uses
`pathlib.Path` (2,607 files) and `os.path.join()` (140 files), which are cross-platform-safe idioms.

---

## CROSS-TRACK COORDINATION SUMMARY

| Track | Interaction | Sequencing |
|-------|-------------|-----------|
| **8.2 (Doc Restructuring)** | B1 de-collision moves/renames docs; 8.2 also moves/reorganizes docs | **→ 8.3 MUST run B1 BEFORE 8.2 bulk moves** to avoid churn; resolve case collisions first, finalize, then move. |
| **8.1 (Core Agent Fixes)** | Independent (8.1 focuses on agent code, 8.3 on platform compat) | No direct coordination needed; 8.3 does not modify agent code. |
| **8.4 (CI/CD Hardening)** | H4 (tool paths) and M3 (Linux commands) are CI-scoped; 8.4 may inherit these fixes | Coordinate timing if 8.4 refactors CI helpers; H4/M3 fixes are prerequisite. |

---

## ISSUE SEVERITY SUMMARY TABLE

| Severity | Count | Total Files | Estimated Total Effort | Blocker | Recommended Sequence |
|----------|-------|-------------|------------------------|---------|---------------------|
| 🔴 BLOCKING (B1) | 1 | 28 MD | 8–12h | YES | **Phase 1 (must complete before downstream)** |
| 🟠 HIGH (H1–H4) | 4 | 268 files | 15–22h | YES | **Phase 2 (parallel, no inter-dependency)** |
| 🟡 MEDIUM (M1–M3) | 3 | 338 files | 10–14h | NO | **Phase 3 (can proceed independently)** |
| 🔵 LOW (L1–L2) | 2 | 10 files | 1–2h | NO | **Phase 4 (cleanup)** |
| ✅ CLEAN (L3) | 1 | N/A | 0h | NO | **No action** |

---

## MATRIX USAGE

This matrix feeds three downstream artifacts:

1. **PHASE_8_3_REMEDIATION_PRIORITY.md** — Detailed remediation sequencing with dependency graph,
   risk mitigation, and rollback strategy.

2. **8.3.3 Critical Fixes workstream** — Executable task list for each issue (Trello board, Jira tickets, or
   GitHub Projects).

3. **8.3.4 Validation & Testing** — Post-remediation verification (Windows checkout, macOS checkout,
   Linux verification, CI pipeline pass).

---

**Matrix Status:** ✅ COMPLETE
**Next Deliverable:** PHASE_8_3_REMEDIATION_PRIORITY.md
**Timestamp:** 2026-07-03T02:00Z
**Authority:** cross-platform-filename-validator (Track 8.3)
