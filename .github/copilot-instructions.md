# Copilot repository instructions

## Current execution contract

Read the relevant provisions of
[AI Codebase Agency Policy](../.codex/CODEBASE_AGENCY_POLICY.md) and applicable
directory/path instructions before editing. This is repository guidance, not
an override of the user's task or a grant of GitHub access.

- Respect explicit read-only/user boundaries and preserve all existing dirty
  work. Do not reset, stash, rebase or discard it as a startup ritual.
- Direct scoped inspection, editing and validation are permitted. Delegate
  only when useful, authorized, and supported by actual tools. No compulsory
  first-response agents, lane count, or agent-binding format applies.
- Use supplied/relevant memories when available. Do not claim exhaustive
  retrieval or simulate loading through a storage tool. Cached flags and
  repository snapshots are not current credential or hosted-runtime proof.
- Resolve relevant issues and disclose other findings with evidence,
  mitigation/owner and next steps. Scope explanations and documented handoffs
  are legitimate; they do not waive actual security or review controls.
- Use risk-based review and bounded retries. There is no minimum five passes,
  attempts or commits, nor a requirement to keep working after the objective
  is already verified.

## Preparation versus GitHub operations

Authorized local code and workflow preparation is allowed without an existing
PR. Workflow patches require relevant YAML/actionlint, secret and permission
checks and applicable review before publishing or executing them. Setup-workflow
changes still require explicit human authorization for that task.

Do not activate/create workflows, dispatch runs, mutate PRs, approve, push,
change settings, merge or deploy without authorization for that operation.
Preserve actual credential scopes, branch/ruleset protections, CODEOWNERS where
enforced, required reviews/checks, environments and genuine execution approvals.
A policy file, auth flag, WEC checkbox or session TTL cannot grant those rights.

Agent profiles may be read for selection and understanding. Their tool filters
and model settings may be deliberate; do not widen them indiscriminately.
The registry, profile candidates and archived sources are not evidence of
hosted activation or selection.

## Project and quality conventions

- Packaging: `pyproject.toml`; Python tasks include `src/codex/cli.py`.
- Configuration is primarily in `configs/` and `conf/`.
- Format/lint changed Python with the configured Black/Ruff/isort rules and
  run relevant mypy checks. Use the project's supported dependency environment.
- Compile changed Python, run focused tests, inspect the diff and run
  `git diff --check`. Run broader pre-commit/nox checks when appropriate,
  reporting actual results and environmental limits.
- Never commit secrets/PII or log plaintext credentials. Use explicit
  least-privilege permissions and safe input handling.
- Prefer timezone-aware UTC timestamps and correct dependency/mock namespaces.
- Preserve compatibility and update documentation/tests relevant to the patch.

Use the actual available tool schema rather than prescribing historical
`task(mode="background")`, `parallel_validation`, or `codeql_checker` APIs.
If a needed tool/service is unavailable, identify the limitation and use a
relevant authorized alternative; do not invent a successful check.

## PR work, CI and handoff

For PR tasks, read relevant current feedback and CI using available authorized
tools. Distinguish local tests from live CI and running checks from completed
ones. Do not claim green CI, mergeability or deployment from stale/local data.
For local/no-PR work, PR review and public comments are not prerequisites.

When authorized to update a PR body, preserve applicable maintainer WEC
selections. The existing wrapup helper can validate PR-specific bookkeeping;
it must record actual agents or an honest direct-execution declaration, not
invent registered agents. Do not call PR-mutating helper modes for a read-only
or no-PR task.

Report the changed files, exact validation results, open findings and limits.
Handoff may be in the response or requested session artifact. No public
`@copilot` continuation ping, repository follow-up/status file or memory write
is universally required. The legacy wording scanner is advisory, while real
security owner/reason and execution gates remain intact.

## Local environment references

`CODEX_SESSION_ID`, `CODEX_SESSION_LOG_DIR`, `CODEX_LOG_DB_PATH`/`CODEX_DB_PATH`
and `CODEX_SQLITE_POOL` configure local session/logging consumers when present.
Language-version/runtime variables configure only documented consumers; no
declaration here pins or grants control of the hosted Copilot service.

For API work, consult the relevant current API/tool reference, verify
operation-specific access, protect credentials and report denied sources.
Historical token names or cached booleans are not proof of scope.

## Offline CDX skills discovery

The startup packet `.codex/session_startup_packet.json` includes a structured
`skills_registry`, `cdx_module_index` (exact source lines, CLI and test entrypoints),
and `cdx_common_preflight`. `scripts/ci/cdx_context.py` builds these from explicit
local source/test paths without network discovery or browsing agent directories.
`python -m scripts.ci.startup_health --refresh-context` updates only catalog fields;
`--validate` rejects omitted or stale mappings. Normal packet generation also
persists the catalog. Validation allows unrelated non-CDX skills/candidates and
context refresh preserves them. Context discovery is not scanner execution or
authorization.
`python -m scripts.archive.cdx_preflight --preflight-summary --json` provides
the shared read-only context alias. The module index also maps common's public
validation/verification/blob-inspection wrappers and `assess_acquired_batch`.
The candidate ID `cdx-archive-lifecycle` appears in skills as `staged_candidate`.
Each module's `cli_contract` records actual parser subcommands/options.
Query supports `info/list/read/search/symbols/callgraph/context`; rehydrate requires
`verify`, `extract`, or `compare` (for example `codex_rehydrate extract ARCHIVE DESTINATION`).
`pack_directory` is absent: use `pack_archive`; canonical scanner API
`run_secret_scanners` also exports the compatibility alias `run_secret_scanner`.
The common-preflight function map includes text inspection,
Merkle computation, canonical findings, external-path validation and lifecycle
entrypoints with exact source locations.
Preflight `--gitleaks-adapter EXECUTABLE --assess-acquired-batch` independently
assesses at most 32 validated acquisition findings in namespace
`acquired_full_file_adapter_not_stock`; `--assess-first-batch` is stock-only.
Acquired assessment checkpoints are one-based; discovery indices are zero-based.
Neither assessment transfers stock fragment provenance or grants clearance.

| Module | Key callable(s) | CLI / tests |
| --- | --- | --- |
| `scripts.archive.cdx_common` | `run_cdx_common_preflight`, `run_secret_scanners` | `python -m scripts.archive.cdx_common --preflight-context --json`; `tests/archive/test_cdx_context.py`, `test_cdx_sqlite_archive.py` |
| `scripts.archive.cdx_preflight` | `run_preflight`, `load_preflight`, `assess_batch` | `python -m scripts.archive.cdx_preflight --help`; `tests/archive/test_cdx_preflight.py` |
| `scripts.archive.cdx_review` | `build_queue`, `schedule_batch`, `write_checkpoint` | `python -m scripts.archive.cdx_review --help`; `tests/archive/test_cdx_review.py` |
| `scripts.archive.cdx_adapter` | `run_adapter`, `load_adapter`, `acquired_span`, `list_batches` | `python -m scripts.archive.cdx_adapter --list-batches --source SOURCE --private-directory PRIVATE --gitleaks-adapter EXECUTABLE`; `tests/archive/test_cdx_adapter.py` |
| `scripts.archive.codex_packer` | `pack_archive` | `python -m scripts.archive.codex_packer --help`; `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts.archive.codex_query` | `CodexArchiveQuery`, `build_llm_context` (method) | `python -m scripts.archive.codex_query --help`; `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts.archive.codex_rehydrate` | `verify_archive`, `rehydrate_archive`, `compare_trees` | `python -m scripts.archive.codex_rehydrate --help`; `tests/archive/test_cdx_sqlite_archive.py` |
| `scripts/archive/gitleaks_adapter/main.go` | `provenance`, `scan`, `localize` | `EXECUTABLE identity` / private request on stdin; `cd scripts/archive/gitleaks_adapter && GOPROXY=off GOSUMDB=off go test ./...` |

`.github/agents-holding/cdx-archive-lifecycle.agent.md` is a discoverable staged
candidate only. Its listing does not establish hosted activation, selection,
credentials, reviewer authority, or permission to pack or publish.
