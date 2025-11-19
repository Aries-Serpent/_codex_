# Changelog

All notable changes to this project will be documented in this file.

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
