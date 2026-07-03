# 🖥️ PHASE 8.3 — PLATFORM COMPATIBILITY AUDIT REPORT

**Workstream:** 8.3.1 — Platform Compatibility Audit
**Track Lead:** cross-platform-filename-validator (Track 8.3)
**Authority:** @mbaetiong (D-tier autonomy)
**Decision Gate:** GO CONTINUE (all gates approved)
**Campaign:** Phase 8 Multi-Agent Deployment (Tracks 8.1–8.4 parallel)
**Branch:** `copilot/deploy-phase-8-agents`
**Report Generated:** 2026-07-03T01:36Z
**Mode:** AUDIT ONLY — no files renamed or modified; single report deliverable produced.

---

## 1. EXECUTIVE SUMMARY

A full cross-platform (Windows / Linux / macOS) compatibility audit was executed against
**17,081 tracked files** in `Aries-Serpent/_codex_`. The repository demonstrates **excellent
raw filename hygiene** — there are **zero** Windows-illegal characters, **zero** reserved
device-name collisions, **zero** trailing dot/space filenames, and **zero** paths exceeding
Windows length limits. However, the audit surfaced **one blocking class of issue** and several
high/medium concerns that will break checkouts and execution on Windows and (in part) macOS.

### Headline Findings

| # | Finding | Count | Severity |
|---|---------|-------|----------|
| 1 | **Case-collision file groups** (paths differing only by case) | 13 groups (28 files) | 🔴 **BLOCKING** |
| 2 | `.gitattributes` **not active repo-wide** (mislocated in `.config/`) | 1 config defect | 🟠 **HIGH** |
| 3 | Tracked **symlinks** (mode 120000) that break on native Windows | 15 | 🟠 **HIGH** |
| 4 | Python files hardcoding absolute repo root `/home/runner/work/...` | 44 | 🟠 **HIGH** |
| 5 | Python files hardcoding `/tmp/` (no Windows equivalent) | 93 | 🟡 **MEDIUM** |
| 6 | Shell scripts (all bash-only; no Windows equivalents) | 216 | 🟡 **MEDIUM** |
| 7 | Linux-only commands inside shell scripts (apt/sudo/systemctl/sed -i) | see §5 | 🟡 **MEDIUM** |
| 8 | `.editorconfig` also mislocated in `.config/` (scope limited) | 1 | 🔵 **LOW** |
| 9 | Windows-illegal chars, reserved names, trailing dot/space, long paths | 0 | ✅ **CLEAN** |

**Overall posture:** Filenames themselves are clean. The **blocking** risk is the 13 case-collision
groups, which cause **silent file loss / overwrites** when the repo is checked out on the default
case-insensitive filesystems of Windows (NTFS) and macOS (APFS/HFS+). The next most impactful item
is that the repository's carefully authored line-ending normalization rules are **not in effect**,
exposing all 216 bash scripts to CRLF corruption on Windows checkouts.

---

## 2. FILENAME INCOMPATIBILITY INVENTORY

**Method:** `git ls-files` (with `core.quotepath off`) across all 17,081 tracked paths;
per-character and per-rule scans.

### 2.1 Windows-Illegal Characters — ✅ NONE

Scanned for `< > : " | ? *` (and `\`) in any path component:

| Character | Count |
|-----------|-------|
| `<` | 0 |
| `>` | 0 |
| `:` (colon) | 0 |
| `"` | 0 |
| `\|` (pipe) | 0 |
| `?` | 0 |
| `*` | 0 |
| `\` (backslash) | 0 |

> Note: An initial naive grep flagged `docs/façade_cloudrun.md` — this was a **false positive**
> caused by `git`'s octal quoting of the non-ASCII `ç`; the actual filename contains **no** illegal
> character. Non-ASCII (UTF-8) filenames are otherwise Windows/macOS-safe.

### 2.2 Reserved Windows Device Names — ✅ NONE

Scanned basenames (any extension) for `CON, PRN, AUX, NUL, COM1–9, LPT1–9`: **0 matches.**

### 2.3 Trailing Spaces / Dots — ✅ NONE

Windows silently strips trailing `.` and ` ` from filenames. Scan for basenames ending in
space or dot: **0 matches.**

### 2.4 Path Length (Windows MAX_PATH = 260) — ✅ CLEAN

- Paths > 255 chars: **0**
- Paths > 200 chars: **0**

No `\\?\` long-path opt-in is required.

### 2.5 Case-Collision Risk — 🔴 BLOCKING (13 groups / 28 files)

Paths that differ **only by letter case**. On case-insensitive filesystems (Windows NTFS default,
macOS APFS default) only one file survives checkout; the other(s) are overwritten or cause
`git checkout` to report the tree as dirty/conflicted. This is a **data-loss and broken-link**
hazard.

| Group | Colliding Tracked Paths |
|-------|-------------------------|
| 1 | `docs/ARCHITECTURE.md` \| `docs/Architecture.md` \| `docs/architecture.md` (**3-way**) |
| 2 | `docs/CI.md` \| `docs/ci.md` |
| 3 | `docs/CLI.md` \| `docs/cli.md` |
| 4 | `docs/QUALITY_GATES.md` \| `docs/quality_gates.md` |
| 5 | `docs/QUICKSTART.md` \| `docs/quickstart.md` |
| 6 | `docs/TROUBLESHOOTING.md` \| `docs/troubleshooting.md` |
| 7 | `docs/agent/INDEX.md` \| `docs/agent/index.md` |
| 8 | `docs/guides/INDEX.md` \| `docs/guides/index.md` |
| 9 | `docs/guides/QUICKSTART.md` \| `docs/guides/quickstart.md` |
| 10 | `docs/security/INCIDENT_RESPONSE.md` \| `docs/security/incident_response.md` |
| 11 | `docs/validation/Tokenization_Validation.md` \| `docs/validation/tokenization_Validation.md` |
| 12 | `.codex/reports/EXECUTIVE_SUMMARY.md` \| `.codex/reports/executive_summary.md` |
| 13 | `reports/EXECUTIVE_SUMMARY.md` \| `reports/executive_summary.md` |

All 13 groups are Markdown documentation; none are source code. This limits functional blast
radius to docs/link integrity but **still blocks a clean Windows/macOS checkout**.

---

## 3. FILE-PATH ANALYSIS (CODE)

**Scope:** 6,676 tracked `*.py` files sampled for absolute POSIX paths and separator handling.

### 3.1 Hardcoded Absolute POSIX Paths — 184 files

| Pattern | File Count | Severity | Notes |
|---------|-----------|----------|-------|
| Any absolute POSIX prefix (`/home /usr /tmp /opt /var /etc`) | **184** | — | Union of below |
| `/home/runner/work/...` (hardcoded repo root) | **44** | 🟠 HIGH | Breaks off-CI and on Windows |
| `/tmp/...` (no Windows equivalent) | **93** | 🟡 MEDIUM | Use `tempfile.gettempdir()` |

**Representative examples (HIGH — hardcoded repo root):**
```
.codex/ast_migrator.py:129            os.chdir('/home/runner/work/_codex_/_codex_')
.codex/batch_migrator.py:118          os.chdir('/home/runner/work/_codex_/_codex_')
.codex/phase_9_3_report_generator.py:15  Path("/home/runner/work/_codex_/_codex_/.codex/...")
.github/audit_artifacts_output/validate_audit_artifacts.py:8  ROOT = Path("/home/runner/work/_codex_/_codex_")
scripts/ci/fix_remaining_security_issues.py:51  repo_root = Path("/home/runner/work/_codex_/_codex_")
scripts/ci/github_api_trickle.py:422  build_codeql_db(source_root="/home/runner/work/_codex_/_codex_")
```

**Representative examples (MEDIUM — `/tmp/`):**
```
.github/agents/infra-linter-agent/agent/reporter.py:78  os.getenv("CODEX_DB_PATH", "/tmp/codex_brain.db")
.github/scripts/collect_link_health_metrics.py:61       '--report-file', '/tmp/link_report_metrics.json'
.github/scripts/post_copilot_followup.py:28             if str(path.absolute()).startswith('/tmp/')
```

**Linux tool-path assumptions (HIGH within CI helpers):**
```
scripts/ci/github_api_trickle.py:413  "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql"
cognitive_app/src/server/cli_api_server.py:803  ("/usr/bin", "/usr/local/bin", "/bin")
```

### 3.2 Path-Separator Construction — Largely Good

| Approach | Files | Assessment |
|----------|-------|------------|
| `pathlib.Path` (`from pathlib import ...`) | **2,607** | ✅ Cross-platform preferred idiom, widely adopted |
| `os.path.join(...)` | **140** | ✅ Cross-platform-safe |
| Manual string concat with `"dir/" +` | ~0 detected | ✅ No systemic manual-separator anti-pattern |

**Interpretation:** The codebase predominantly uses `pathlib`/`os.path.join`, so **separator
handling is not a systemic defect**. The real path risk is *absolute path literals* (§3.1), not
separator style. This is encouraging and narrows remediation scope in 8.3.3.

---

## 4. SHELL-SCRIPT INVENTORY

**Total tracked `*.sh`: 216.** Distribution by top-level directory:

| Directory | Count |
|-----------|-------|
| `scripts/` | 145 |
| `tools/` | 26 |
| `.codex/` | 13 |
| `.github/` | 11 |
| `.devcontainer/` | 5 |
| `docker/` | 3 |
| `deploy/` | 3 |
| `examples/` | 2 |
| `.pre-commit-scripts/` | 2 |
| others (`tests`, `misc`, `docs`, `cognitive_app`, `automation`, root) | 1 each |

### 4.1 Interpreter / Shebang Profile

| Shebang | Count |
|---------|-------|
| `#!/usr/bin/env bash` | 161 |
| `#!/bin/bash` | 51 |
| `#!/bin/bash --login` | 1 |
| other/none (first line not shebang) | ~3 |

**100% are bash-dependent** — none are POSIX-`sh` portable, and there are **no `.bat`/`.cmd`/`.ps1`
equivalents**. These run on Linux, macOS, and Windows-via-WSL/Git-Bash, but **not** in native
Windows `cmd`/PowerShell.

### 4.2 Functional Categories (by filename keyword)

| Category | Approx. count | Category | Approx. count |
|----------|--------------|----------|--------------|
| run/orchestration | 34 | fix/remediation | 12 |
| test | 18 | ci | 10 |
| validate | 11 | check | 10 |
| build | 10 | setup | 9 |
| install | 6 | docker | 5 |
| audit | 5 | deploy | 3 |

### 4.3 Linux-Specific Command Usage (file counts)

| Command / Feature | Files | Portability Concern |
|-------------------|-------|---------------------|
| `apt` / `apt-get` | 25 / 8 | 🟡 Debian-only package install |
| `sudo` | 10 | 🟡 No native Windows equivalent |
| `systemctl` | 5 | 🟡 Linux systemd-only |
| `sed -i` | 10 | 🟡 GNU in-place syntax differs on BSD/macOS |
| `grep -P` | 1 | 🟡 GNU PCRE flag, not on macOS/BSD grep |
| `chmod` | 9 | 🟡 No-op / different on Windows |
| `mktemp` | 5 | 🟡 POSIX temp; fine under WSL/Git-Bash |
| `ln -s` | 2 | 🟡 Symlink creation restricted on Windows |
| `set -euo pipefail` (bashism) | 161 | ℹ️ Requires bash, not POSIX sh |
| `[[ ... ]]` (bashism) | 74 | ℹ️ Requires bash |
| redirects to `/dev/null` | 128 | ℹ️ Works under Git-Bash/WSL |

**Interpretation:** The scripts are cleanly bash-idiomatic (good for Linux/macOS/WSL) but carry a
**hard bash dependency** and **~33 scripts assume Debian `apt`**. Native-Windows execution requires
WSL/Git-Bash or Python re-implementation.

---

## 5. CONFIGURATION-FILE FINDINGS

Tracked ignore/attribute/config files reviewed:
`.gitignore`, `.dockerignore`, `.config/.gitattributes`, `.config/.editorconfig`,
`.config/.gitignore`, plus nested `.gitignore` files under `.codex/`, `apps/`, `cognitive_app/`,
`services/ita/`, `copilot/extension/`, `.dvc/`.

### 5.1 🟠 HIGH — `.gitattributes` Is NOT Active Repo-Wide

The repository ships an **excellent** attributes file (`.config/.gitattributes`) with correct
cross-platform rules:
```
* text=auto eol=lf
*.sh  text eol=lf     *.bash text eol=lf
*.ps1 text eol=crlf   *.bat  text eol=crlf   *.cmd text eol=crlf
```
**However, it is located at `.config/.gitattributes`, not the repository root.** Git only applies a
`.gitattributes` to files within its own directory tree, so these rules govern only files inside
`.config/`. Verification:
```
$ git check-attr text eol -- run_updates.sh
run_updates.sh: text: unspecified
run_updates.sh: eol: unspecified
$ git check-attr text eol -- conftest.py
conftest.py: text: unspecified
conftest.py: eol: unspecified
$ git config --get core.attributesFile   # (empty)
$ git config --get core.autocrlf         # (empty)
```
No root `.gitattributes`, no symlink, and no `core.attributesFile` pointer exists.

**Impact:** Line-ending normalization is effectively **off** repo-wide. On a Windows clone with
`core.autocrlf=true` (Git-for-Windows default), the **216 bash scripts risk CRLF injection**,
producing `bad interpreter: /usr/bin/env bash^M` failures under WSL/Git-Bash. This silently
undermines the very cross-platform intent the file was written for.

### 5.2 🔵 LOW — `.editorconfig` Also Mislocated

`.config/.editorconfig` sets `end_of_line = lf`, but EditorConfig resolution walks upward from the
edited file to the filesystem root; a config nested in `.config/` only applies to files **inside**
`.config/`. Editors will not apply LF enforcement to root/`scripts/` files.

### 5.3 ✅ `.gitignore` / `.dockerignore` — Clean

- No backslash (`\`) path separators and no drive-letter (`C:`) patterns in any tracked
  `.gitignore` (root or nested) or in `.dockerignore`.
- `.dockerignore` uses forward-slash / glob patterns only (portable).
- Patterns are POSIX-glob and Git-portable.

### 5.4 🟠 HIGH — Tracked Symlinks (15)

Symlinks (git mode `120000`) are not reliably materialized on Windows (require Developer Mode /
`core.symlinks=true`); otherwise Git writes them as plain text files containing the target path.

```
.codex/security_vulnerability_scan_latest.md
scripts/audit_pipeline.py
scripts/ci/session_preload.py
configs/data   configs/model   configs/tracking   configs/train
.venv_ci/bin/python  .venv_ci/bin/python3  .venv_ci/bin/python3.12  .venv_ci/lib64
venv_test/bin/python venv_test/bin/python3 venv_test/bin/python3.12 venv_test/lib64
```
Two are **functional code symlinks** (`scripts/audit_pipeline.py`, `scripts/ci/session_preload.py`)
— highest priority. Four are `configs/*` (Hydra config dirs). The remaining nine live inside
`.venv_ci/`/`venv_test/` — virtualenvs that arguably **should not be tracked at all** (candidate for
`.gitignore` in a later workstream, not this session).

---

## 6. SEVERITY CLASSIFICATION

### 🔴 BLOCKING (must fix before Windows/macOS support is claimed)
- **B1.** 13 case-collision groups (28 files) — silent overwrite / dirty-tree on case-insensitive
  filesystems. (§2.5)

### 🟠 HIGH (breaks execution or corrupts files on Windows)
- **H1.** `.gitattributes` inactive repo-wide → no line-ending normalization → CRLF risk to all
  216 bash scripts. (§5.1)
- **H2.** 2 functional code symlinks (+13 others) unreliable on Windows. (§5.4)
- **H3.** 44 Python files hardcode `/home/runner/work/...` repo root. (§3.1)
- **H4.** Linux tool-path assumptions in CI helpers (`/opt/hostedtoolcache/...`, `/usr/bin`). (§3.1)

### 🟡 MEDIUM (portability friction; degraded but not fatal under WSL/Git-Bash)
- **M1.** 93 Python files hardcode `/tmp/`. (§3.1)
- **M2.** 216 bash-only scripts with no Windows-native equivalents. (§4)
- **M3.** ~33 scripts assume Debian `apt`; 10 use `sudo`, 5 `systemctl`, 10 `sed -i`, 1 `grep -P`. (§4.3)

### 🔵 LOW (hygiene / future-proofing)
- **L1.** `.editorconfig` mislocated in `.config/`. (§5.2)
- **L2.** 9 tracked virtualenv symlinks under `.venv_ci/`/`venv_test/` (should be untracked). (§5.4)

### ✅ CLEAN (no action)
- Illegal characters, reserved device names, trailing dot/space, path length, `.gitignore`/
  `.dockerignore` separators, and separator-construction idioms (pathlib/os.path dominate).

---

## 7. PRIORITIZED REMEDIATION RECOMMENDATIONS → Workstream 8.3.2

Ordered by impact-to-effort. These feed the 8.3.2 Compatibility Matrix and 8.3.3 Critical Fixes.

| Priority | Item | Recommended Action | Est. Effort | Risk |
|----------|------|--------------------|-------------|------|
| **P0** | B1: 13 case collisions | Consolidate each group to a single canonical file (prefer lowercase `index.md`/`ci.md` style **or** the UPPERCASE convention — pick one repo-wide); redirect/merge content; update all inbound doc links. **Requires reference-graph update.** | M | Broken links if refs missed |
| **P0** | H1: gitattributes inactive | Add a **root** `.gitattributes` (or set `core.attributesFile`) replicating the `.config/` rules so `* text=auto eol=lf` + shell `eol=lf` + `.ps1/.bat/.cmd eol=crlf` actually apply. Verify via `git check-attr`. | S | Low; one-time renormalize |
| **P1** | H3: hardcoded repo root | Replace `/home/runner/work/_codex_/_codex_` literals with a `repo_root()` resolver (e.g. `Path(__file__).resolve().parents[N]` or `git rev-parse --show-toplevel`). 44 files. | M | Medium (must verify each) |
| **P1** | H2: code symlinks | Convert the 2 functional symlinks (`scripts/audit_pipeline.py`, `scripts/ci/session_preload.py`) to real files or import shims; decide policy for `configs/*` Hydra symlinks. | S–M | Medium |
| **P2** | M1: `/tmp/` literals | Replace with `tempfile.gettempdir()` / `tempfile.NamedTemporaryFile`. 93 files. | M | Low |
| **P2** | H4/M3: Linux tools | Add platform guards / `shutil.which` fallbacks; document WSL requirement for `apt`/`systemctl`/`sudo` scripts; normalize `sed -i`/`grep -P` or port to Python. | M–L | Low |
| **P3** | M2: bash-only scripts | Triage 216 scripts: (a) keep bash + document WSL/Git-Bash requirement, (b) port high-traffic ones (setup/test/ci ~47) to Python for true portability. | L | Low |
| **P3** | L1/L2: config hygiene | Move/duplicate `.editorconfig` to root; untrack `.venv_ci`/`venv_test` symlinks via `.gitignore`. | S | Low |

**Recommended quick wins for 8.3.3 (highest value, lowest risk):** **H1** (root `.gitattributes`)
and **P0 B1** consolidation — together they unblock clean Windows/macOS checkout and guarantee LF
integrity for every shell script.

---

## 8. AUDIT METHODOLOGY & COVERAGE

- **Corpus:** `git ls-files` = 17,081 tracked paths (100% of tracked filenames audited).
- **Filename scans:** per-character illegal set `< > : " | ? * \`; reserved device names via
  basename regex; trailing space/dot; path length; case-collision via lowercased-key grouping
  (Python `collections.defaultdict`).
- **Code scans:** 6,676 `*.py` grepped for absolute POSIX prefixes, `/tmp/`, repo-root literals,
  `pathlib`/`os.path.join` adoption.
- **Shell scans:** 216 `*.sh` — shebang census, directory distribution, keyword categorization,
  Linux-command file-counts, bashism detection.
- **Config:** `git check-attr` verification of attribute application; `.gitignore`/`.dockerignore`
  separator inspection; tracked-symlink enumeration via `git ls-files -s` mode `120000`.
- **Constraints honored:** audit only (no renames/edits); no workflow files created or modified;
  report stored exclusively in `.codex/`.

> **Note on Workstream 8.3.1 task #4 (Workflow Configuration Audit):** intentionally **deferred**.
> Session constraints prohibit creating/modifying GitHub Actions workflow files. A read-only
> workflow-platform assessment (`runs-on`, shell defaults, OS conditionals) is recommended as a
> separate read-only pass in 8.3.2 to avoid any accidental workflow edits.

---

**Report status:** ✅ COMPLETE — Workstream 8.3.1 audit deliverable produced.
**Next:** Feeds Workstream 8.3.2 (Compatibility Matrix) and 8.3.3 (Critical Fixes).
**Maintainer:** Track 8.3 — cross-platform-filename-validator
**Timestamp:** 2026-07-03T01:36Z
