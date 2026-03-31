# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Fixed (S254 — PR #3831 — 2026-03-31)
- **fix(mlflow):** `maybe_mlflow()` generator refactored — `mlflow.start_run()` moved before `yield` to prevent `RuntimeError: generator didn't stop after throw()` (gemini HIGH alert). `return` after `yield _NoOpLogger()` ensures correct generator termination.
- **fix(perf):** Performance threshold `dict_lookup_10000` raised 30K→45K; latency assert tightened 60ms→40ms (gemini MEDIUM suggestions — better regression detection vs. CI reliability balance).
- **feat(pr-template):** `🔄 Auto-Post @copilot review After Agent Session` checkbox added to all 6 PR body template locations (both static templates + 4 workflow-generated bodies).
- **feat(brain):** `cognitive-brain-manager.md` v4.4→v4.5 — S254 status, gemini review thread resolution patterns.


- **fix(ci):** `tests/config/conftest.py` — added explicit `sys.path.insert(0, src/)` guard
  (with directory-depth comment) to fix `ModuleNotFoundError: No module named 'config.openai_client'`
  in the Resilient Validation Suite. Root cause: pytest-split workers resolve `tests/config/` ahead
  of the root `conftest.py` path injection. Verified: 24/24 `test_openai_client.py` tests pass.
- **feat(brain):** `.github/agents/cognitive-brain-manager.md` v4.3→v4.4 — Sprint 13 status table,
  iterative self-review loop Mermaid architecture diagram, AfterMath patterns
  (RP-NEW-001/002/003), Phase 3+4 next-phase plan, PDA Loop front-matter enabled.
- **feat(agent):** `.github/agents/post-merge-doc-alignment-agent.md` v1.0→v1.1 — PDA Loop
  integration, `self_healing` config block (enabled, max 3 iterations), `iteration_history`
  tracking S244/S251/S252/S253 runs, `cognitive_integration_level: 3`.
- **fix(docs):** `docs/index.md` "Last Updated" refreshed to 2026-03-31.
- **health(sweep):** Issue #3829 nightly health sweep S200 completed — ruff check ✅ 0 violations;
  CodeQL on main ✅ success (3 consecutive); last 5 CI runs on main: success/skipped ✅;
  cognitive brain metadata updated; accountability report updated.

### Fixed (auto-update — PR #3831)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #3831 (SHA `06038612`) at 2026-03-31T07:15Z [auto-generated]



- **CI Rescue Pipeline** (`docs/ci/CI_RESCUE_PIPELINE.md`): New canonical reference documenting
  the end-to-end lifecycle from workflow failure to Copilot fix session. Includes 9 Mermaid
  diagrams (flowchart, sequence, state machine, timeline, dependency graph, anti-pattern maps)
  and a component responsibility matrix. Golden-path example from PR #3818 comment #4158728043.
- **CI/CD Index updated** (`docs/ci/INDEX.md`): CI Rescue Pipeline added as the top entry under
  a new "🚨 CI Rescue Pipeline (Golden Path)" section.
- **Homepage quick-links updated** (`docs/index.md`): "🚨 CI Rescue & Health" section added with
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
  - `self-healing-feedback-loop.yml`: Upgraded `actions/upload-artifact@v3` → `@v4` (4 occurrences)
  - `optimized-ci.yml`: Added missing `pytest-split` dependency for test sharding
  - `audit-improvement-pipeline.yml`: Added filename sanitization for NTFS compatibility, removed invalid CLI args
  - `detect-duplicates.yml`: Added PR context guards for `workflow_dispatch` manual runs
  - `pre-release-deployment.yml`: Upgraded `actions/upload-artifact@v3` → `@v4` (6 occurrences)
  - `workflow-validator.yml`: Fixed duplicate PR comment issue (now updates existing comments)
  - `decode-validate-artifact.yml`: Upgraded `actions/checkout@v3` → `@v4`

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
- **CI/CD Success Rate**: 14% → 100% (pending GitHub Pages manual config - now complete)
- **Build Success Rate**: 0% (12/12 failures) → 100%

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
- **Operational templates (v1.0.0):** Introduced Python File Relocation, CLI Hardening, and Intent Validation templates under `docs/templates/` with a navigation index.
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
