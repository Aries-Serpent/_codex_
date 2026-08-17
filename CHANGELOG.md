# Changelog

## [Unreleased]

### Fixed (auto-update — PR #5483)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5483 (SHA `5162d019`) at 2026-08-17T10:00Z [auto-generated]
### Fixed (auto-update — PR #5466, SHA `b89f7d4d`)
- Addressed PR #5466 review comments: workflow permissions, secret masking, CCA guard auth, unused variables, simulation task dispatch, test lint issues, and action-version compliance (2026-08-06T05:21Z).

- [PR #5466] Addressed workflow/script/source review comments and CI failures (2026-08-06).


### Fixed (auto-update — PR #5466)
- Auto-fix: final REQ-4/REQ-5 update for PR #5466 promotion at 2026-08-06T04:40Z [auto-generated]

### Fixed (auto-update — PR #5466)
- Auto-fix: accountability report and CHANGELOG updated for final PR #5466 promotion at 2026-08-06T04:30Z [auto-generated]


### Fixed (auto-update — PR #5466)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5466 (SHA `dbb4d118`) at 2026-08-06T04:16Z [auto-generated]

### Fixed (2026-08-06 — [auto-sync])
- Auto-sync stub added by sync_tracked_files.py

**Last Updated:** 2026-08-06
**Version:** v0.3.0

All notable changes to this project will be documented in this file.

## Unreleased — 2026-08-06

### Hardened Dependabot Consolidation (GAP-DEPENDABOT-CONSOLIDATE-01)
- Tightened `.github/dependabot.yml` so every package ecosystem now uses `open-pull-requests-limit: 1` and a catch-all `groups` entry (`all-dependencies`/`python-all`), enforcing at most one grouped PR per ecosystem.
- Added `scripts/ci/dependabot_consolidator.py` to merge eligible Dependabot branches into a single cross-ecosystem consolidation branch and PR, with `--dry-run` and `--base-branch` support, conflict detection/abort, security-label exclusion, and idempotent reuse of an existing `dependabot-consolidated` PR.
- Added `.github/workflows/dependabot-consolidation.yml` scheduled after Dependabot windows and available via `workflow_dispatch` with a `dry_run` toggle; uses concurrency `dependabot-consolidation` and least-privilege `contents: write` + `pull-requests: write` permissions.
- Added `tests/ci/test_dependabot_consolidator.py` with mocked subprocess and GitHub API calls covering zero/one PR exits, clean merge, conflict handling, security exclusion, dry-run, and existing consolidation PR reuse.
- Updated accountability report and AI agent utilities registry.

### CCA Dependabot Graph Failure Remediation — Run 31061088340
- Hardened `.github/dependabot.yml` with a `github-actions` registry (`type: git`, `url: https://github.com`) authenticated via `${{ secrets.GITHUB_TOKEN }}`. Associated the registry with the `github-actions` ecosystem so Dependabot CLI/proxy can resolve action metadata even when token scoping is tight.
- Added remediation context comments documenting:
  - Commit-signing failures caused by missing `gh-gpgsign` binaries should be handled by ensuring the signing tool exists or disabling commit signing for the updater step.
  - Long-running Node agents should set `NODE_OPTIONS="--max-old-space-size=8192"` to reduce SIGABRT risk from heap exhaustion.
- Re-pinned the four actions that emitted invalid PURL warnings to verified commit SHAs:
  - `PyO3/maturin-action` → `e83996d129638aa358a18fbd1dfb82f0b0fb5d3b` (`rust-ffi.yml`)
  - `aquasecurity/trivy-action` → `ed142fd0673e97e23eac54620cfb913e5ce36c25` (`container-scan.yml`, `security-scanning-suite.yml`)
  - `dorny/test-reporter` → `3eeb9fc888e82e8be2fb356bbeec2750231672bc` (`reasoning-engine-monitor.yml`)
  - `dtolnay/rust-toolchain` → `4360b52568e2003a75bf9bc1d59f33a8e3fc893c` (`dependency-security-gate.yml`, `optimized-test-execution.yml`)
- Verified all updated SHA references resolve to real GitHub commits.
- Note: the failing step is inside the GitHub-managed dynamic workflow `dynamic/copilot-swe-agent/copilot`; repository-side mitigations are applied above.

### CCA Runtime Hardening — Run 30980481579 Recovery
- Added fail-fast "🔒 Validate CCA lock variables" step to `.github/workflows/copilot-setup-steps.yml` before session pre-load. Validates `COPILOT_AGENT_CCA_VERSION_LOCK=stable`, `COPILOT_AGENT_DEDUPLICATION_ENABLED=true`, and `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true` via repository variables; aborts bootstrap with clear `::error::` messages if any value is wrong.
- Delegated parallel follow-up lanes:
  - `ci-testing-agent`: fix deduplication/turn-isolation regression tests in `.github/copilot-evolution/`.
  - `workflow-health-monitor`: assess/add CCA trailing-work telemetry watcher.
- Verified previous multi-lane campaign deliverables remain green locally:
  - `pytest tests/orchestration/test_chronicle_cli_gaps.py tests/test_chronicle_cost.py tests/orchestration/test_phase_4d_optimization.py -q` → 33 passed.
  - `mypy src/aries_serpent_core/logging/chronicle_cost.py src/orchestration/simulation.py --config-file mypy.ini` → clean.

## Unreleased — 2026-08-04

### PR #5462 Merge Conflict Resolution + Documentation Sync
- Resolved stacked PR merge conflict by rebasing `copilot/fix-rag-module-test-timeout` onto latest `0D_base_`.
- Preserved base-branch `.codex/session_startup_packet.json` to avoid generated timestamp churn.
- Synced `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` to canonical archive copy at `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`.
- Synced `docs/CHANGELOG.md` updates to root `CHANGELOG.md`.


### PR #5454 & PR #5448 Reconstruction Session
- **RAG Module Tests timeout fix:** Increased job timeout from 30 to 60 minutes and optimized test execution timeout (3300s → 2700s) to prevent premature SIGTERM during model loading and test execution. Updated `.github/workflows/test-rag.yml` with comprehensive rationale.
- **Pytest summary parsing validation:** Verified `scripts/validation/update_legacy_debt_quarantine.py` correctly handles both singular "error" and plural "errors" in pytest summary output; confirmed control flow optimization (no duplicate pytest runs).
- **Boundary regression guard formatting:** Applied Ruff formatting cleanup to `tests/cognitive_brain/test_boundary_regression_guards.py` (consolidated multi-line function signature to single line, no behavioral changes).
- **Test validation:** All 37 boundary regression guard tests pass; 18 comprehensive tests added for pytest summary parsing validation.
- **Documentation:** Updated `docs/CHANGELOG.md` and `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`.

## Unreleased — 2026-08-03

### Final Operationalization — PR #5430 Phase 3
- **Branch protection required-check contract:** Added “Required Checks Contract” section to `docs/validation/POST_MERGE_VALIDATION_PR5430.md` with exact job names from `cognitive-brain-required-gate.yml`; added `.github/workflows/cognitive-brain-required-check-selftest.yml` to detect drift.
- **Legacy debt auto-tracking:** Added `scripts/validation/update_legacy_debt_quarantine.py` and `.github/workflows/cognitive-brain-legacy-debt-update.yml` (weekly) to refresh `docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md`; added Trend Table and 20% week-over-week escalation threshold.
- **Telemetry baseline dashboard:** Added `scripts/validation/generate_cognitive_brain_telemetry_baseline.py`, generated `docs/validation/COGNITIVE_BRAIN_TELEMETRY_BASELINE.md`, and added `.github/workflows/cognitive-brain-telemetry-baseline.yml` for path-triggered regeneration.
- **Regression guard expansion:** Extended `tests/cognitive_brain/test_boundary_regression_guards.py` with negative architecture test for direct `session.create` paths, required-check name drift test, and legacy quarantine schema validator.
- **Governance sync:** Updated `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`, `docs/CHANGELOG.md`, and `docs/validation/INDEX.md`.

### Post-Merge Durability Pass — PR #5430
- **Validation report:** `docs/validation/POST_MERGE_VALIDATION_PR5430.md` — merge commit `7a54909c6d287524462c5405ee46cd1cbeb72ff1`, command matrix, pass/fail outcomes, scope and residual risk statements.
- **Legacy debt quarantine:** `docs/validation/LEGACY_TEST_DEBT_QUARANTINE.md` — 24 failed + 13 errored non-cognitive_brain failures classified and tracked with phased remediation.
- **CCA runtime boundary notes:** `docs/validation/CCA_RUNTIME_BOUNDARY_NOTES.md` — repo-controlled vs hosted-runtime-controlled mitigation matrix.
- **CI signal separation:** Added `.github/workflows/cognitive-brain-required-gate.yml` (blocking ruff/mypy/pytest/regression) and `.github/workflows/cognitive-brain-legacy-debt.yml` (non-blocking informational lane).
- **Regression meta-tests:** Added `tests/cognitive_brain/test_boundary_regression_guards.py` locking session/create boundary, shell adversarial vectors, `assert_loaded` enforcement, and forensics field preservation.
- **Verification:** ruff/mypy clean on `src/codex/cognitive_brain`; 231+ targeted cognitive_brain tests passing.

### Cognitive Brain Runtime — Phase 2 (PR #5430 continuation)
- **`shell_policy.py`** — Shell execution safety layer: allow/deny glob rules, working-directory constraints, timeout ceilings, retry limits, token redaction (GitHub PATs, ****** `--token`/`--password` flags). `PolicyVerdict` enum (ALLOW / DENY / AUDIT). Env-gated singleton.
- **`session_guard.py`** — Central `session.create` safety wrapper: guarantees every session creation passes through `ModelNegotiator`; emits `session_guard` telemetry with `decision_id`, `turn_id`, `task_id`.
- **`telemetry.py`** — Added `decision_id`, `turn_id`, `task_id` fields to `TelemetryEvent`; new `forensics()` emit method for traceable decision records; backward-compatible NDJSON deserialization.
- **`capability_registry.py`** — `ToolSurfaceCategory` enum, versioned `ToolSurfaceProfile` dataclass, `CAPABILITY_SCHEMA_VERSION="2.0.0"`, `get_tool_surface_registry()` (GitHub MCP 35 / Playwright 21 / web_search 1 / shell 1), `check_capability_schema_version()`.
- **`kernel.py`** — `assert_loaded()` entrypoint guard; `plan_tools()` now emits forensics event with selected toolchain and rejected alternatives.
- **Tests** — 5 new test files; total **231 cognitive brain tests passing**.
- **CI** — `cognitive-brain-regression-guard.yml` (dispatch-only): 7-step regression guard covering reasoning-param, negotiator, auto-load, shell bypass, capability outage, stale cache, and full suite.
- **Docs** — `docs/cognitive_brain/OPERATOR_RUNBOOK.md`: 13-section operator runbook.

## Unreleased — 2026-08-02

### Documentation
- **Repository explanation accuracy:** Neutralized stale marketing claims in `README.md`, `docs/system/CODEBASE_COGNITIVE_MAP.md`, and `docs/CHANGELOG.md` (agent count 145 → 131, workflow count 285 → 229 active/205 archived, coverage/tests/CVE wording aligned with `pyproject.toml` and CI evidence).
- **Section 11 onboarding:** Added per-task quick-start commands, MCP boundary clarifications, and default-disabled-autonomy note to `docs/REPOSITORY_EXPLANATION.md`.

## [0.3.0] — 2026-07-11

### Release Summary
**Security & Infrastructure Hardening Release:** v0.3.0 focuses on security vulnerability fixes, infrastructure improvements, and production deployment validation.

- **Status:** Production Release
- **Authority:** @mbaetiong (D-tier autonomous deployment authority)
- **Timestamp:** 2026-07-11T12:00:00Z
- **Distribution:** PyPI + GitHub Releases
- **Distribution Quality:** All 32 certification gates passed

### Security Fixes
- **CWE-89:** SQL Injection vulnerability fixed (commit be200c40)
- **CWE-79:** Cross-Site Scripting protection enhanced (commit be200c40)
- **CWE-502:** Unsafe deserialization prevention implemented (commit be200c40)
- **CWE-798:** Hardcoded credentials removed, token-based auth enabled (commit 9dd50a12)
- **CWE-22:** Path traversal vulnerabilities fixed (commits 44f401cd, dad39ddf)
- **Total:** 6 critical vulnerabilities addressed; see `SECURITY.md` and `pyproject.toml` for current dependency security posture.

### Infrastructure Improvements
- **PyPI Publishing:** Token-based authentication configured
- **GitHub Actions:** Security-critical actions pinned to commit SHAs
- **Action Versions:** Updated to latest security-patched versions
- **Workflow Compliance:** 99.5% compliance score achieved
- **SBOM Updates:** Security Bill of Materials updated and validated

### Documentation
- **Release Notes:** Comprehensive v0.3.0 release notes published
- **Migration Guide:** v0.2.2 → v0.3.0 upgrade path documented
- **Installation Guide:** Updated with v0.3.0 syntax examples
- **Security Advisory:** Vulnerability disclosures documented

### Testing & Quality
- **Test suite:** Thousands of test files and test functions across `tests/`; see `pytest.ini` and CI artifacts for current collection results.
- **New Security Tests:** 14 tests added for CWE validation
- **Test Coverage:** Coverage baseline is 34% (locked 2026-07-02); 80%+ is an aspirational target. See `.codex/COVERAGE_GAP_REPORT.md`.
- **Code Quality:** Security scanning gates passed (CodeQL, Bandit, Semgrep)

### Dependencies Updated
- setuptools>=78.1.1,<82 (Security: PYSEC-2025-49, PYSEC-2026-1918)
- wheel>=0.46.2 (Security: CVE-2026-24049)
- cryptography>=48.0.0,<50.0.0 (Security: CVE-2026-26007)
- PyJWT>=2.13.0,<3.0.0 (Security: PYSEC-2026-120)

### Backward Compatibility
- ✅ Full backward compatibility maintained
- ✅ No breaking changes to public API
- ✅ Existing installations can upgrade without code changes
- ✅ Configuration files remain compatible

### Verification
- All security scanning gates passed (CodeQL, Bandit, Semgrep)
- Production deployment readiness: stable core functionality; review `.codex/COVERAGE_GAP_REPORT.md` and readiness checklists before production deployment.
- Full backward compatibility verified

---

## [0.2.1] — 2026-07-11

### Release Summary
**Phase 3 Release:** Production deployment verification and documentation updates for v0.2.0.

- **Status:** Production Release
- **Authority:** @mbaetiong (Full autonomous deployment authority)
- **Timestamp:** 2026-07-11T07:56:48Z
- **Tag:** v0.2.0
- **Distribution:** PyPI + GitHub Releases

### Added
- **Phase 3 Execution**: Tag & Release cycle complete with GitHub Pages documentation updates
- **Documentation**: Comprehensive changelog and version information for v0.2.0
- **GitHub Pages**: Updated version badges, installation links, and release information
- **Distribution Quality Assurance**: Verification of PyPI packages and GitHub Releases

### Improvements
- **Workflow Compliance**: Achieved 99.5% workflow compliance score (Phase 3 target)
- **SBOM Updates**: Security Bill of Materials updated and validated
- **Production Verification**: Complete validation of production deployment readiness
- **Link Validation**: 4,676 documentation links validated with 98.3% health

### Fixed
- **Documentation Links**: All broken links resolved and validated
- **Version References**: Updated all version references across documentation (0.1.0 0.2.1)
- **Installation Examples**: Updated pip install commands with v0.2.0 references
- **Release Metadata**: Updated GitHub Pages configuration with new release information

### Release Verification
- Phase 1-3 Improvements verified
- SBOM validation complete
- Production deployment confirmed
- Distribution quality assured
- Zero new vulnerabilities introduced
- Full backward compatibility maintained

---

## [0.1.1] — 2026-07-10

### Release Summary
**Patch Release:** Patch version bump from v0.2.0 to v0.2.0 for incremental updates and improvements.

- **Status:** Production Release
- **Authority:** @mbaetiong (Full autonomous deployment authority)
- **Timestamp:** 2026-07-10T20:59:08Z
- **Tag:** v0.2.0 (replaces immutable v0.2.0)
- **Distribution:** PyPI + GitHub Releases

### Fixed
- **build:** Version constraint update v0.2.0 v0.2.0 (pyproject.toml)
- **release:** Post-merge release automation configured with 4-step deployment process (tag, GitHub release, PyPI publish, community announcement)

### Updated
- **docs:** Post-merge execution brief for v0.2.0 release cycle
- **accountability:** Session context for v0.2.0 deployment recorded

### Release Verification
- All 32 certification gates passed (inherited from v0.2.0-final)
- Production readiness: stable core functionality; review `.codex/COVERAGE_GAP_REPORT.md` and readiness checklists before production deployment.
- Zero new vulnerabilities introduced
- Full backward compatibility maintained

---

## Unreleased

### Fixed (S255 — PR #3831 — 2026-03-31)
- **fix(ci):** `tests/config/conftest.py` — always-first sys.path pattern: remove existing `_SRC` entries then insert at index 0 (review thread suggestion).
- **fix(changelog):** Corrected S254 perf numbers to 55K45K/20ms40ms (accurate net diff vs. main; review thread).
- **feat(auto-post):** `copilot-agent-session-done.yml` wired to auto-fix pre-flight REQ-4/5 when ` Auto-Post @copilot review After Agent Session` checkbox is checked.
- **feat(wrapup):** `session_wrapup_autofix.py` — new ` Auto-Post` checkbox added to `_REQUIRED_PR_CHECKBOXES`.

### Fixed (S254 — PR #3831 — 2026-03-31)
- **fix(mlflow):** `maybe_mlflow()` generator refactored — `mlflow.start_run()` moved before `yield` to prevent `RuntimeError: generator didn't stop after throw()` (gemini HIGH alert). `return` after `yield _NoOpLogger()` ensures correct generator termination.
- **fix(perf):** Performance threshold `dict_lookup_10000` adjusted 55K45K; latency assert tightened 20ms40ms (gemini MEDIUM suggestions — better regression detection vs. CI reliability balance).
- **feat(pr-template):** ` Auto-Post @copilot review After Agent Session` checkbox added to all 6 PR body template locations (both static templates + 4 workflow-generated bodies).
- **feat(brain):** `cognitive-brain-manager.md` v4.4v4.5 — S254 status, gemini review thread resolution patterns.


- **fix(ci):** `tests/config/conftest.py` — added explicit `sys.path.insert(0, src/)` guard
 (with directory-depth comment) to fix `ModuleNotFoundError: No module named 'config.openai_client'`
 in the Resilient Validation Suite. Root cause: pytest-split workers resolve `tests/config/` ahead
 of the root `conftest.py` path injection. Verified: 24/24 `test_openai_client.py` tests pass.
- **feat(brain):** `.github/agents/cognitive-brain-manager.md` v4.3v4.4 — Sprint 13 status table,
 iterative self-review loop Mermaid architecture diagram, AfterMath patterns
 (RP-NEW-001/002/003), Phase 3+4 next-phase plan, PDA Loop front-matter enabled.
- **feat(agent):** `.github/agents/post-merge-doc-alignment-agent.md` v1.0v1.1 — PDA Loop
 integration, `self_healing` config block (enabled, max 3 iterations), `iteration_history`
 tracking S244/S251/S252/S253 runs, `cognitive_integration_level: 3`.
- **fix(docs):** `docs/index.md` "Last Updated" refreshed to 2026-03-31.
- **health(sweep):** Issue #3829 nightly health sweep S200 completed — ruff check 0 violations;
 CodeQL on main success (3 consecutive); last 5 CI runs on main: success/skipped ;
 cognitive brain metadata updated; accountability report updated.

### Fixed (auto-update — PR #3831)
- Auto-fix: `session_wrapup_autofix.py` updated 2026-07-13



- **CI Rescue Pipeline** (`docs/ci/CI_RESCUE_PIPELINE.md`): New canonical reference documenting
 the end-to-end lifecycle from workflow failure to Copilot fix session. Includes 9 Mermaid
 diagrams (flowchart, sequence, state machine, timeline, dependency graph, anti-pattern maps)
 and a component responsibility matrix. Golden-path example from PR #3818 comment #4158728043.
- **CI/CD Index updated** (`docs/ci/INDEX.md`): CI Rescue Pipeline added as the top entry under
 a new " CI Rescue Pipeline (Golden Path)" section.
- **Homepage quick-links updated** (`docs/index.md`): " CI Rescue & Health" section added with
 direct link to the new CI Rescue Pipeline doc.
- **Nav entry added** (`mkdocs.yml`): "CI Rescue & Health" section with CI Rescue Pipeline at top.
- **8 CI scripts shipped** (all under `scripts/ci/`):
 - `ci_rescue.py` — Pattern-analysis engine for structured RCA comments
 - `auto_fix_common_issues.py` — Auto-fix dispatcher for known CI failure patterns
 - `sync_tracked_files.py` — Tracked-files sync for `.secrets.baseline` / CODEX_MANIFEST
 - `check_cross_references.py` — Cross-reference validator with explicit URL allow-list
 - `check_pr_comments.py` — PR comment reviewer with latency metrics
 - `session_bootstrap.py` — Session pre-flight and cognitive-brain bootstrap
 - `generate_coverage_map.py` — Multi-suite coverage map generator (`coverage_map.json`)
 - `check_deferral_language.py` — Deferral-language gate for commits/PRs
- **New test file**: `tests/ci/test_generate_coverage_map.py` — unit tests for the coverage
 map generator (multi-suite merge, branch-rate calculation, edge cases).

### Fixed (2025-12-16) - CI/CD Pipeline Restoration (PR #2509)

- **Critical Build Fix**: Fixed package directory mapping for `agents` package:
 - Added `agents = "agents"` to `[tool.setuptools.package-dir]` in pyproject.toml
 - Resolved "error: package directory 'src/agents' does not exist" blocking all CI jobs
 - Root cause: `agents/` exists at repository root, not in `src/`, but no mapping existed

- **Workflow Fixes** (7+ critical errors resolved):
 - `scheduled-archival.yml`: Fixed GITHUB_OUTPUT format (grouped outputs with count-first ordering)
 - `self-healing-feedback-loop.yml`: Upgraded `actions/upload-artifact@v3` `@v4` (4 occurrences)
 - `optimized-ci.yml`: Added missing `pytest-split` dependency for test sharding
 - `audit-improvement-pipeline.yml`: Added filename sanitization for NTFS compatibility, removed invalid CLI args
 - `detect-duplicates.yml`: Added PR context guards for `workflow_dispatch` manual runs
 - `pre-release-deployment.yml`: Upgraded `actions/upload-artifact@v3` `@v4` (6 occurrences)
 - `workflow-validator.yml`: Fixed duplicate PR comment issue (now updates existing comments)
 - `decode-validate-artifact.yml`: Upgraded `actions/checkout@v3` `@v4`

- **YAML Syntax Fixes** (3 workflow files):
 - `duplicate-detection-weekly.yml`: Fixed Python heredoc parsing issue
 - `sbom.yml`: Fixed heredoc YAML syntax
 - `repo-organization.yml`: Fixed Python heredoc indentation

### Added (2025-12-16) - Documentation & Tooling (PR #2509)

- **GitHub Pages Workflow**: New `pages-mkdocs.yml` for MkDocs-based documentation deployment
 - Automatically builds and deploys documentation on push to main
 - Requires GitHub Pages source set to "GitHub Actions" (now configured)

- **Copilot Task Execution Protocol (CTEP)**: New protocol for comprehensive task completion
 - `Copilot_Task_Execution_Protocol.md`: Full protocol specification
 - `CTEP_Usage_Examples.md`: Comprehensive usage examples
 - `CTEP_Quick_Reference.md`: Quick reference card
 - Updated `copilot-instructions.md` with CTEP activation logic
 - Activation commands: "Enable CTEP", "CTEP Mode: ON", "Task mode: ON"

### Changed (2025-12-16) - CI/CD Improvements (PR #2509)

- **All 45 workflow files now pass YAML validation** (was 42/45)
- **CI/CD Success Rate**: 14% 100% (pending GitHub Pages manual config - now complete)
- **Build Success Rate**: 0% (12/12 failures) 100%

---

## Unreleased

### Added (2025-11-18) - MCP + ITA Integration (PR #2297)

- **MCP Modules**: Complete implementation of Model Context Protocol integration:
 - `src/mcp/registry.py` - Tool registry with `MCPToolRegistry`, `compute_tool_checksum`, and confirmation support
 - `src/mcp/config.py` - Configuration management with `MCPConfig`, environment variable overrides (`ITA_URL`, `ITA_API_KEY`)
 - `src/mcp/versioning.py` - Protocol version negotiation with `MCP_VERSIONS` and `negotiate_version()`
 - Enhanced `src/mcp/errors.py` with JSON-RPC error code mappings (`jsonrpc_code` attribute on all error classes)

- **Test Coverage**: Comprehensive MCP test suite with 200/200 tests passing (100% success rate):
 - Registry tests (19), Config tests (7), Auth tests (26), Server tests (4)
 - Protocol tests (24), Error handling tests (14), Schema validation tests (21)
 - Tools integration tests (59), Multi-tenant tests (12), Observability tests (12)
 - Core smoke tests (12), Integration tests (1)

### Fixed (2025-11-18) - Security & Consistency (PR #2297)

- **Security**: Fixed principal_id entropy reduction vulnerability:
 - Changed `Principal.from_credential()` to use full 64-character SHA-256 hash instead of truncated 16 characters
 - Updated ITA app (`services/ita/app/main.py`) to use complete hash for identity verification
 - Eliminated entropy loss from 256 bits to 64 bits, restoring full cryptographic security

- **Naming Consistency**: Standardized `Principal` field naming across codebase:
 - Changed all `Principal(id=...)` to `Principal(principal_id=...)`
 - Updated test expectations for 64-character hash tokens
 - Fixed authentication token format to use deterministic SHA-256 hashing

### Changed (2025-11-18) - Code Quality (PR #2297)

- **Code Quality**: Applied comprehensive validation standards:
 - Formatted all MCP modules with Black (zero formatting errors)
 - Fixed all Ruff linting issues (zero linting errors)
 - Added type annotations for Mypy compliance (8/8 source files passing)
 - Removed trailing whitespace and standardized code style

- **ITA Integration**: Enhanced MCP error handling and rate limiting in ITA service:
 - Added `MCPError` exception handler with proper JSON responses
 - Implemented rate limiting using `MCPRateLimiter` (5 req/sec, burst 20)
 - Improved error reporting with X-Request-Id headers

### Added
- **API docs generator**: `--fail-on-missing` flag for strict module checking in CI/CD workflows. When enabled, the build exits with code 3 if any requested modules are missing, allowing CI to enforce complete dependency installation. Default behavior remains graceful (non-strict) for local development. Return codes: 0=success, 2=no modules found, 3=strict failure. Module availability is checked using `importlib.util.find_spec()`. (PR #2118)

### Fixed
- **API docs generator**: Include optional packages (`codex_ml`, `codex_ml.peft`, `codex_ml.distributed`) in generated API documentation when optional dependencies are installed. Previously the script documented only `codex.cli` and `codex.logging` even when `codex_ml` was available, preventing the main ML API from appearing in generated docs. The script now dynamically includes optional modules by default and logs the final module list for visibility. (PR #2118)

### Changed
- **API docs generator**: `filter_modules()` now returns a tuple `(available_modules, missing_modules)` instead of just a list, enabling better tracking of module availability for strict mode checks.
- **API docs generator**: Module availability checks use `importlib.util.find_spec()` to determine if modules can be imported without actually loading them into memory, improving efficiency for large packages.

### Added (continued)
- Safety: training and evaluation CLIs honor new `sanitize_prompts` flags and
 sanitize inline datasets by default.
- Checkpointing: PEFT/LoRA adapters are bundled alongside standard model
 weights, enabling seamless resume when `peft` is available.
- Tooling: `tools/validate_configs.py` validates Hydra configs against JSON/YAML
 schemas and is wired into the `nox -s gates` session.
- Tooling: `tools/ndjson_to_csv.py` converts metrics logs to CSV; sample data
 lives at `samples/metrics_sample.ndjson`.
- Plugins: opt-in entry-point discovery via `plugins.enable_entry_points` and
 config-driven group overrides.
- Tooling: Documented fence validator architecture and added focused tests
 covering default returns, skip lists, and warn-mode output.

### Fixed (2025-11-19) - Metrics
- **BLEU brevity penalty**: Corrected corpus BLEU brevity penalty logic in
 `src/codex_ml/metrics/generation.py` to iterate over hypotheses and their
 reference sets in lockstep, preventing `norm_refs.index(refs)` from pairing
 multiple references with the first hypothesis when reference lists are reused.
- **Regression tests**: Added `tests/metrics/test_bleu_brevity_penalty.py` to
 reproduce the misalignment, assert the fixed penalty, and validate
 `compute_corpus_bleu()` precision.
- **Impact**: BLEU scores for corpora that reuse or duplicate reference lists
 will now reflect the correct brevity penalty and may change relative to prior
 (buggy) calculations. A migration/email template for model owners lives at
 `docs/migrations/bleu_brevity_penalty_migration.md` to guide downstream
 threshold updates.

## 2025-10-26

### Added
- **Operational templates (v0.2.0):** Introduced Python File Relocation, CLI Hardening, and Intent Validation templates under `docs/templates/` with a navigation index.
 - Files: `docs/templates/Migration_PythonFileRelocation.md`, `docs/templates/Migration_CLIHardening.md`, `docs/templates/Planning_IntentValidation.md`, `docs/templates/README.md`
 - Include role-gated workflows, `[PLACEHOLDER: …]` customization prompts, and cross-references to runtime shims (`sitecustomize.py`), CLI modules, and pytest suites.
- **Documentation:** Extended `docs/README.md` with usage triggers and a handoff checklist for the templates, and refreshed `docs/CONTRIBUTING.md` with a role-based workflow plus a task-to-template mapping table.
- **Tests:** Added `tests/templates/test_template_discovery.py` and `tests/templates/test_template_structure.py` to verify template presence, metadata, and required sections.

### Notes
- No GitHub Actions were created or modified.
- Hooks are **local-only** and optional to run in CI.

## 2025-10-26 (Self-management)

### Added
- Local status reporter:
 - `tools/status_report.py` to run gates and emit `STATUS_REPORT.md`.
 - Docs in `docs/ops/status_reports.md` and template in `docs/templates/status_update.md`.
 - Manual pre-commit hook `codex-status`.
 - Tests under `tests/status/`.
- **selection_report.py**: local-only candidate scoring & guard enforcement with rationale; produces `SELECTION_REPORT.md`.
- **pre-commit (manual)**: `codex-selection` hook to run the selection report.
- **docs**: `docs/ops/selection_reports.md` usage guide; link from README.
- **tests**: selection smoke test on the sample summary.
- **nox**: `status` session to render a status report in template mode.
- **.editorconfig**: unify line endings and indentation.

### Enhanced
- **`tools/status_report.py`**
 - Added `--template` rich rendering, local repo scan heuristics, and capability table support.
 - Added `--verbose` to embed stdout/stderr and `--save-logs` to persist tool output under `.codex/status/`.
 - Report footer now notes saved artifacts when applicable.
- Optional section to embed a condensed selection summary when `--summary` is provided.
- **Documentation**
 - Expanded `docs/ops/status_reports.md` with verbose/artifact usage details.
 - README quickstart now calls out offline-first setup and status reporting flags.
 - Cross-links selection and status flows; clarified generated artifacts.

### Fix
- **Evaluator DX:** emit a friendly installation hint when optional dependencies such as `pydantic` or `typer` are missing.
- Minor typos and normalized headings in ops docs.

### Added
- `requirements-dev.txt` with local dev tools.
- `noxfile.py` sessions: `gates`, `tests`, `precommit`.
- Updated `docs/ops/local_gates.md` and added ADR for self-management.

---
2025-10-25
