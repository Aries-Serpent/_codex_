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
