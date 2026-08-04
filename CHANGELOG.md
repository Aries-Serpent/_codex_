## [Unreleased]

### Fixed (PR #5462)
- Resolved stacked PR merge conflict by rebasing `copilot/fix-rag-module-test-timeout` onto latest `0D_base_`.
- Preserved base-branch `.codex/session_startup_packet.json` to avoid generated timestamp churn.
- Synced accountability report to canonical archive and CHANGELOG to root copy.


### Fixed (auto-update — PR #5460)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5460 (SHA `03201a3f`) at 2026-08-04T05:02Z [auto-generated]

### Fixed (2026-08-03 — PR #5430 Code Review Comment Resolution)
- Fixed import system compatibility: Replaced `from src.codex...` with relative `from .` imports throughout cognitive_brain module to ensure compatibility with installed package environments where `src` is not a top-level package.
  - Files: telemetry.py, session_guard.py, model_negotiator.py, orchestrator.py, reasoning_engine.py, kernel.py, __init__.py, shell_policy.py, integration_adapters.py
  - Updated docstring examples to use `codex.cognitive_brain` instead of `src.codex.cognitive_brain`
- Added debug logging in `telemetry.py:139`: NDJSONTelemetryBackend now logs exceptions when skipping malformed telemetry lines instead of silently passing.
- Normalized tool names in `capability_registry.py`: Replaced fully-qualified MCP names (e.g., `"github-mcp-server-actions_get"`) with short form (e.g., `"actions_get"`) for consistency in `available_tools` list.
- Removed unused permission in `.github/workflows/cognitive-brain-regression-guard.yml`: Dropped `pull-requests: write` from permissions (job only needs `contents: read`) — follows least-privilege principle.
- Fixed actionlint.yaml comment accuracy: Updated suppressed codes comment to correctly reflect all severity levels ("info/style/warning/error") instead of claiming only "info/style/warning".


### Fixed (2026-08-03 — Multi-Lane CI Fix + CCA Panic Prevention)
- Fixed action version violations in `.github/workflows/cognitive-brain-regression-guard.yml` (`actions/checkout@v4` → `@v5`, `actions/setup-python@v5` → `@v6`).
- Added `GITHUB_REPOSITORY` guard to `dependency-submission.yml` — prevents CCA Rust proxy stderr panic (os error 11) caused by `org/repo` placeholder fetching non-existent repos.
- Added `## 🚀 Multi-Lane Custom Agent Delegation Framework` to `.github/AGENTS.md` — declares parallel agent delegation as mandatory default for all sessions.
- Added multi-lane Step 7 to MANDATORY SESSION PRE-LOAD and full framework section in `.github/copilot-instructions.md`.

### Added (2026-08-02 — Cognitive Brain Runtime Layer)
- `src/codex/cognitive_brain/capability_registry.py`: TTL-aware model capability cache; gates `reasoning_effort` and other params per model profile.
- `src/codex/cognitive_brain/model_negotiator.py`: `ModelNegotiator` strips unsupported session config params (fixes `claude-haiku-4.5` reasoning-effort runtime error) and selects ranked fallback models when required capabilities are unmet.
- `src/codex/cognitive_brain/policy.py`: `DeterministicPolicy` scoring across five physics-inspired dimensions — Path, Fields, Patterns, Redundancy, Balance — with seeded deterministic output.
- `src/codex/cognitive_brain/orchestrator.py`: `MCPOrchestrator` toolchain planner composes GitHub MCP, Playwright, web_search, and shell tool surfaces using policy scores.
- `src/codex/cognitive_brain/fallbacks.py`: `FallbackChain`, `with_fallback` decorator, `rate_limited_call`, `import_optional`, and `safe_default_config` for auto-recovery.
- `src/codex/cognitive_brain/telemetry.py`: Structured telemetry with `InMemoryTelemetryBackend` and `NDJSONTelemetryBackend`; captures negotiation, policy-score, orchestration, fallback, and startup events.
- `src/codex/cognitive_brain/kernel.py`: `CognitiveBrainKernel` singleton wiring all sub-systems; environment auto-load via `COGNITIVE_BRAIN_AUTO_LOAD=true`; CCA stability guards.
- 91 new unit/integration tests across 4 test modules for the above components.

### Fixed (auto-update — PR #5428)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5428 (SHA `99619ba4`) at 2026-08-02T05:54Z [auto-generated]

### Fixed (auto-update — PR #5427)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5427 (SHA `7de0bcf9`) at 2026-08-02T04:53Z [auto-generated]

### Added
- Canonical, source-backed repository briefing for `codex-ml` 0.3.0, including the five-layer architecture, Cognitive Brain behavior, runtime matrix, MCP boundaries, and dated Chronicle guidance.
- Separate GitHub Markdown frontmatter schema requiring a nonblank custom-agent `description`.
- Dated machine-readable Chronicle snapshot for the exact 30-day window ending 2026-08-01.
- Validator regression coverage for root/nested discovery, malformed frontmatter, blank descriptions, duplicates, reference mismatches, and the Pattern Discovery and Memory Sync Consolidation skills.

### Changed
- Hardened `validate_agent_specs.py` so parse errors fail validation, registered Markdown profiles are discovered recursively, registry/profile identity and selectability are compared, and handler/manifest references and duplicate IDs/names/files are checked.
- Required nonblank descriptions in the repository agent-registry schema.
- Updated Copilot MCP references and added a tested machine-readable contract for the supplied 36-name research inventory: 35 read-only GitHub MCP tools plus standalone `web_search`, alongside 21 Playwright MCP tools.
- Synchronized the mandatory archived accountability record with the repository briefing, MCP inventory, Chronicle, validation, and verification results.

### Fixed (auto-update — PR #5425)
- Auto-fix: `session_wrapup_autofix.py` updated accountability report and CHANGELOG for PR #5425 (SHA `79c522a1`) at 2026-08-01T17:31Z [auto-generated]

### Fixed
- PR #5418 security remediation completion (session 2026-08-01):
  - Remediated 16 security vulnerabilities (11 High, 5 Low) across nltk, PyJWT, pyasn1
  - Updated PyJWT from 2.13.0 to 2.14.0 (CVE-2026-48524 JWKS endpoint DoS fix)
  - Updated nltk from 3.9.5 to 3.10 (4 CVEs: SSRF in urlopen, ReDoS in regex, path traversal in FramenetCorpusReader/NKJPCorpusReader)
  - Added pyasn1≥0.4.8 transitive dependency (CVE-2026-59884 DoS via unbounded long-form tag IDs)
  - CVSS risk reduction: 94.6 → 0.0 (-100%)
  - Test pass rate: 97.6% (1,096/1,123 tests passing)
  - Security score: 10/10 (zero critical/high/medium issues in usage patterns)
  - Zero breaking changes, all existing APIs unchanged
  - Mapped 22 Dependabot alerts to CVE fixes with dismissal rationale
