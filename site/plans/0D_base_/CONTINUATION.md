# PR #5773 — staging continuation

Snapshot: 2026-11-11 UTC. Refresh all hosted state before acting.

## Status and scope

The dependency consolidation and all five requested review fixes are implemented.
All five review threads are now marked resolved, with individual replies citing
`f983ac60bc856506971cf68e007c062851e31ee2`.
This is not a declaration of full security clearance or green required checks.

At inspection, PR #5773 was **open, unmerged, non-draft**, with
`mergeable_state: unstable`. Its head was
`aafbc726c14c7ca0fac51fdf25a5fee77a8ef53c`; its target `0D_base_` was
`fec362069b774564e97afc792b279bbd7c9dc18f`. A synthetic PR merge is not proof of
actual staging inclusion. This handoff is an additional documentation-only commit.
The user intends to merge; this session did not execute a merge.

Repository: `/home/runner/work/_codex_/_codex_`.
Read current instructions and preserve dirty work before editing.

## Implemented and previously validated

- Scoped dependency/action deltas from #5769–#5772 were consolidated, with
  extension real-HTTP tests, Rust/Python gzip boundary tests and frontend
  affected-feature regressions. Recheck source-head consumption if sources move.
- Dedicated lazy-init configuration isolates ten synthetic loopback variants;
  default discovery excludes that suite, exposed via `npm run test:e2e:lazy`.
- External HTTP(S) `BASE_URL` targets no longer launch a local fixture; credential
  URLs and non-HTTP schemes are rejected. The documented external HAR command
  collected 30 cases using `--list`; no external capture was executed.
- Lazy server paths use `resolve(import.meta.dirname, '..')`; the HAR spec also
  uses the ESM directory property.
- Frontend Node engines and npm-generated root lock metadata match jsdom 31:
  `^22.22.2 || ^24.15.0 || >=26.0.0`. Requested upgrades remain; the review fix
  changed no dependency versions or checksums.
- Review-fix validation: clean npm install, 204 unit tests, seven default Chromium
  feature cases, one real Chromium lazy case in a checkout path containing
  spaces, scoped lint, engine-boundary checks and secret scanning passed.
  Seven configuration regressions passed on Node 22.23.4 and 24.22.1.
  All task-owned fixture ports closed.
- Earlier browser matrices: lazy-init 87/87 and affected features 21/21 for each
  of development, production and GitHub Actions base-path production across
  Chromium/Firefox/WebKit. These are historical results, not fresh runs here.
- Historical CDX 373, fresh-wheel FFI 19, extension HTTP three and Rust gates
  must not be presented as freshly executed on a later or merged tree.
- Today's PDA/accountability entries exist. Detailed historical evidence:
  `/home/runner/work/_codex_/_codex_/docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
  and `/home/runner/work/_codex_/_codex_/.codex/aftermath/pda_iterations.jsonl`.
  Their old hosted-review/security dispositions require the updates below.
- Explicit compiler validation still reports 62 pre-existing diagnostics; build
  uses `--noCheck` and is not a compiler gate. Previous full lint baseline was
  44 errors/65 warnings. Neither backlog was fixed by this PR.

## Checkpoints for the next session

### 1. Confirm real staging inclusion and review the final delta

Owner: PR/staging maintainer.

- Refresh PR #5773 and `0D_base_`; record actual merge SHA and parents if merged.
  Verify intended files/dependency targets, not merely PR closure or scorecards.
- Compare `f983ac60` to the actual merged candidate. At this snapshot its only
  committed successor delta was a startup-packet timestamp. That means the
  timestamp-only churn restored by the review fix was subsequently reintroduced.
  Inspect whether it remains in the final tree and restore the appropriate
  tracked baseline only within authorized scope, without discarding dirty work.
- The local startup packet was already dirty before this handoff. It was excluded
  from publication and must remain visible and byte-for-byte preserved.
- No source PR mutation, workflow dispatch/approval, deployment or merge is
  authorized by this document. Honor real protections and requested operations.

### 2. Finish hosted security artifact disposition

Owner: security/CI maintainers.

New evidence supersedes the earlier "Python still running" handoff:
[Enterprise Compliance & CodeQL run 42955914698](https://github.com/Aries-Serpent/_codex_/actions/runs/42955914698),
attempt 2, reports **success**, with completed Python and JavaScript analysis,
bound by API metadata to head `aafbc726`. Both SARIF/source artifacts exist:

| Artifact | ID | Archive SHA-256 |
| --- | --- | --- |
| Python SARIF | 13827513062 | d9cd27300fdfd8b889a1d50b5edfac1de109ad1a8bc7562ab95bd7bfb520d8a5 |
| Python source | 13827418474 | b4c8ecd7fb57282510d3f1f542e7df09871ab06b46c46c35ab119ccee5197c39 |
| JavaScript SARIF | 13826663822 | 2a1796f4903d7084e7170ca7d0fbbe303b6e3a8e9c986e133e9741e6995a1310 |
| JavaScript source | 13827670386 | f714636f2acebcc330723c066b5ec282eaa664e616e583d616cf17d53349c06f |

These new artifacts were listed, **not downloaded or triaged in this session**.
Download through authenticated tooling; verify archive hashes, source checkout,
PR head/base, run attempt, SARIF invocation diagnostics, findings and coverage.
The synthetic merge reported for this candidate is
`5e3fd6b85e7eca154f3cf13d2421d7f8d90fe007`; establish tree equivalence rather
than assuming standalone exact-head coverage.

Check incremental/diff-informed scope and exclusions: the inspected CodeQL
configuration omits `copilot/extension`. Job success and informational
Bandit/Semgrep jobs do not establish zero findings or all-component clearance.
Security Scanning Suite run `42955914821`, attempt 2, reports success too;
inspect actual jobs/owning-root coverage before relying on it. Earlier JS
dependency audit ran at repository root and did not clear the frontend advisory.
Do not repeat the timed-out local CodeQL operation or portray its oversized
Python database skip as clearance. Use the already-produced hosted artifacts.

### 3. Dispose remaining hosted failures without bypassing controls

Owner: repository/CI maintainers.

- Validation Pipeline `42956274412`, attempt 2: success at `aafbc726`.
- Agent Token Delegation `42956274434`, attempt 2: failure. Authenticated logs
  for job `130312493940` show empty `OWNER_APPROVAL_PROTECTED` and exit 1 at
  `test "$OWNER_APPROVAL_PROTECTED" = "true"`. Only a genuine protected approval
  or maintainer decision can address that gate; do not weaken it.
- Data Quality `42955914843`, attempt 2: `startup_failure`. Establish the startup
  diagnostic and whether jobs were created; do not count it as passing tests.
- Strict gate run `42955914540` succeeded, while later run `42956569401` remains
  `action_required`. Report these separately; refresh required-check disposition.
- Refresh review approvals for the actual final SHA. Resolved threads, an older
  approval, local scorecards and synthetic merge commits are not blanket consent.

### 4. Keep dependency and quality findings explicit

Owner: frontend dependency/API-client maintainers.

Zod 4.4.3 remains affected by GHSA-mrhx-c7xc-m3w5 (`<4.6.6`). Prior frontend
audit reported one high and ten moderate findings; extension had four moderate.
Specific constrained-collection exploitation and attacker control of configured
API responses were not established. Client arrays lack collection-size
constraints; `response.json()` precedes schema validation without byte limits.
The upstream fix checks existing collection limits earlier; upgrading alone
does not impose application response bounds.

Request a separately authorized compatibility-tested upgrade assessment to
4.6.6 or later, API ownership/reachability review and appropriate pre-parse/
collection limits. Do not blanket-audit-fix dependencies or describe fallback
handling as an allocation guard. Triage findings without claiming exploitability
solely from advisory metadata.

Keep the 62 compiler diagnostics and lint baseline separately scoped. Revalidate
only affected gates when code changes or staging integration invalidates evidence.
Any required CDX rerun must use the actual authenticated adapter and inspect
executed/skip counts; catalog validation is read-only absent CDX source edits.

## Copyable resumption prompt

```text
Resume PR #5773/staging follow-up using
/home/runner/work/_codex_/_codex_/site/plans/0D_base_/CONTINUATION.md.
Refresh PR/head/base/merge state and preserve dirty work. All five review
threads are resolved in f983ac60; implementation is complete, not all assurance.
First verify actual 0D_base_ inclusion and inspect successor timestamp churn.
Then triage existing hosted run 42955914698 attempt-2 Python/JS SARIF and
source artifacts, binding hashes, checkout, scope and findings to the candidate.
Do not repeat timed-out local CodeQL. Disposition token protected-approval
failure, Data Quality startup failure and action-required checks with owners.
Keep Zod advisory and compiler/lint backlog open pending scoped decisions.
Do not dispatch/approve workflows, weaken scanners, mutate source PRs, deploy
or merge without explicit operation authorization. Use bounded checkpoints;
publish authorized scoped changes and provide another precise continuation.
```

## SARIF triage and extension coverage checkpoint — 2026-11-12

### Exact-staging SARIF: blocked before triage

The active local checkout is branch `0D_base_` at
`8746dfaa29126f6f65d939d419d2834af737d755`; the locally cached
`origin/0D_base_` ref has the same value. The workspace was clean before this
checkpoint. The cached ref was not refreshed from GitHub, so this does not
establish the current remote staging tip or PR #5773 merge state.

The candidate evidence remains Enterprise Compliance & CodeQL run
`42955914698`, attempt 2, recorded above against PR head `aafbc726`. Its four
listed Python/JavaScript SARIF and source artifacts have not been retrieved or
verified here. The terminal has no `gh` executable and the available GitHub
interfaces did not expose Actions artifact download. A read-only PR #5773
status query returned no status-check records; an empty result is not a pass or
proof that the run/artifacts are current.

The workspace also contains
`.codex/reports/security/codeql-sarif/javascript/javascript.sarif`. Its
structured metadata reports SARIF 2.1.0, CodeQL 2.26.0, JavaScript only, and
37 results. No run/SHA binding to `42955914698` or current staging was
established. It is not the stated 35-result set and is not accepted as a
substitute. No finding rows or dispositions are asserted in this checkpoint.

**Next action:** obtain the existing four artifacts through an authorized
read-only artifact interface, or have an authorized maintainer place them in
approved private storage. Verify archive and extracted-file hashes, run and
attempt, checkout SHA, SARIF invocation metadata, and exact tree equivalence to
the refreshed `0D_base_` tip. Then reconcile the claimed 35 results before
triaging. If any binding fails or the count differs, record the discrepancy and
keep triage blocked; do not filter, infer, or silently reuse PR-head results.
Keep raw SARIF and source data in approved private storage. Because a separate
`SARIF_TRIAGE.md` would currently be ignored by `.gitignore`, maintain the
initial inventory/disposition record in this tracked continuation unless a
separate, reviewed tracking-path decision is made.

### `copilot/extension` CodeQL coverage: authorization pending, not changed

The active `.github/codeql/codeql-config.yml` paths do not include the
repository-root `copilot/extension/`. The active
`.github/workflows/codeql-ga-gate.yml` analyzes JavaScript through this shared
configuration. Therefore the recorded CodeQL success does not by itself prove
that the extension source or tests were extracted and analyzed.

**Next action / owner:** obtain a separately authorized coverage decision from
the Security/CI maintainer: either add `copilot/extension/` to the shared CodeQL paths, with
review of the impact on every consumer, or approve a separate least-privilege
analysis lane if shared scope is unsuitable. No configuration/workflow change,
workflow dispatch, permission change, alert dismissal, publication, or merge
was made. Once authorized and reviewed, validate that the completed analysis
for the exact staging SHA includes the extension source and tests; existing
unit tests or config inspection alone do not prove CodeQL coverage.

### Current limits

- No exact-staging SARIF was downloaded, no 35-result count was verified, and
  no finding was individually triaged or dispositioned.
- No current remote branch/merge state or completed staging check result was
  established by this local checkpoint.
- Extension CodeQL coverage remains unverified pending owner decision,
  reviewed implementation, and exact-SHA completed analysis.

## PR #5773 and hosted-evidence refresh — 2026-11-12

This refresh supersedes the earlier checkpoint's statements that merge state
and remote staging state were not refreshed. The pre-existing local changes to
this continuation are preserved; this section is appended rather than
replacing that work.

### Actual merge and successor timestamp

The refreshed GitHub API reports PR #5773 closed and merged at
`2026-11-11T04:34:37Z` as `0d185fa855a8a0ac6cd99ca5653892dab9bbaf9b` into
`0D_base_` at `fec362069b774564e97afc792b279bbd7c9dc18f`. The current remote
`0D_base_` tip is `8746dfaa29126f6f65d939d419d2834af737d755`, whose parent is
the merge commit; ancestry was verified. `main` remains
`25ab8b63afc8fddcc93dbbfb123e0d708c777e0e`. The current PR source head is
`9cea274a43bb0cbb457fbb1d5ab089b0a570f25a`; its tree matches the merged tree
`759654a453dfefefc6a204545c086a08debba9e6`.

The CodeQL run head `aafbc726c14c7ca0fac51fdf25a5fee77a8ef53c` has tree
`e749b94c`; comparing it with the merged tree shows only:

- modified `.codex/session_startup_packet.json`;
- added `site/plans/0D_base_/CONTINUATION.md`.

No path in the configured CodeQL paths changed in that comparison, but this is
not exact tree equivalence and does not replace source-artifact or SARIF
binding.

The merged commit's packet timestamp is `2026-11-11T04:25:05Z`; its sole
successor changes only that field to `2026-11-11T04:41:25Z`. The earlier
`f983ac60` packet value was `2026-11-10T05:13:16Z`, and the CodeQL run-head
value was `2026-11-11T03:44:16Z`. No timestamp restoration was made. Keep
this churn visible; do not restore or regenerate the packet absent separately
authorized scope.

### Existing CodeQL artifacts: metadata available, triage still blocked

Run `42955914698`, attempt 2, completed successfully against head `aafbc726`.
GitHub lists the following four unexpired artifacts, expiring
`2027-01-10T03:59:57Z`:

| Artifact | ID | Listed size | API-listed archive SHA-256 |
| --- | ---: | ---: | --- |
| Python SARIF (`codeql-results-python`) | 13827513062 | 474808 bytes | `d9cd27300fdfd8b889a1d50b5edfac1de109ad1a8bc7562ab95bd7bfb520d8a5` |
| Python source (`codeql-source-python`) | 13827418474 | 389 bytes | `b4c8ecd7fb57282510d3f1f542e7df09871ab06b46c46c35ab119ccee5197c39` |
| JavaScript SARIF (`codeql-results-javascript`) | 13826663822 | 152012 bytes | `2a1796f4903d7084e7170ca7d0fbbe303b6e3a8e9c986e133e9741e6995a1310` |
| JavaScript source (`codeql-source-javascript`) | 13827670386 | 389 bytes | `f714636f2acebcc330723c066b5ec282eaa664e616e583d616cf17d53349c06f` |

These are API metadata digests only; the archive bytes and contents have not
been verified. Download attempts using `GITHUB_TOKEN` returned HTTP 401 for
the four artifacts. A bounded retry for the Python SARIF with
`CODEX_MASTER_KEY` and `CODEX_BACKUP_KEY` also returned HTTP 401. The GitHub
Actions MCP list/download calls failed before retrieval with a missing
`Mcp-Param-owner` header. No archive was obtained. Do not report a SARIF result
count, zero findings, a clean scan, or finding dispositions.

The shared CodeQL configuration still excludes `copilot/extension/`. Security
and CI maintainers must decide whether to extend the shared scope or provide a
separate reviewed analysis lane. No configuration change or local CodeQL rerun
was made.

### Hosted failures, checks, and owners

- Agent Token Delegation run `42956274434`, attempt 2, failed on the PR head;
  merge-commit run `42960150163`, attempt 1, also failed at
  `Verify protected owner approval`. The first run's log identified an empty
  `OWNER_APPROVAL_PROTECTED`. **Owner:** repository/security maintainer
  responsible for the genuine protected-approval configuration. Preserve the
  gate; no approval or dispatch was performed.
- Data Quality run `42955914843`, attempt 2, is `startup_failure` with zero
  jobs. **Owner:** Actions/CI workflow and runner-infrastructure maintainers
  to diagnose startup; it is not a test pass or source-level test result.
- Strict No-Deferral run `42955914540`, attempt 2, succeeded. The later
  `42956569401` run is now reported by the API as completed `failure`, attempt
  1, with zero jobs, not `action_required`. **Owner:** CI/security gate owner
  to reconcile the earlier action-required description and determine whether
  a valid rerun is needed. No rerun or approval was initiated.
- No check run with `action_required` conclusion was found on the analyzed
  head, merge commit, or current staging tip. The pull-request status tool
  returned an empty check list. The legacy combined status is `pending` with
  zero legacy status entries, despite nine successful check runs on current
  staging. The merged commit has 117 check runs across two pages: 55 success,
  42 skipped, one neutral, and two failures. This does not establish that all
  branch-protection-required checks are satisfied. **Owner:** repository/CI
  maintainer to reconcile required-check configuration and status.
- The merged-commit ML Components Test Suite run `42960150291` failed in
  `test-ml-components (ubuntu-latest, 3.12, integration)`, at step
  `Run integration tests`; its other reported matrix jobs succeeded.
  **Owner:** ML Components test and CI maintainers to inspect the failed job
  log and classify the failure. No failure cause is inferred here.

Current staging tip `8746dfaa` has nine successful check runs and is a direct
child of the merged commit, but that limited result does not clear the failed
merge-commit checks or the pending/empty combined status. Obtain the actual
required-check and owner dispositions before representing the candidate as
fully assured.

### Remaining scope and next authorized decisions

Keep the Zod GHSA-mrhx-c7xc-m3w5 advisory, 62 compiler diagnostics, and
previous lint backlog open pending scoped owner decisions and their own
validation. No source changes, workflow dispatch/approval, PR mutation, push,
deployment, or merge occurred in this refresh. Documentation validation was
limited to `git diff --check`; tests were not run.

For the next session:

```text
Resume PR #5773 follow-up from
/workspaces/_codex_/site/plans/0D_base_/CONTINUATION.md. Preserve the existing
dirty continuation work and do not restore the startup-packet timestamp
without separate authorization. PR #5773 is merged as 0d185fa; current
0D_base_ is 8746dfaa, its direct child. Obtain the four existing artifacts
from run 42955914698 attempt 2 through authorized private storage; verify
archive hashes, source checkout metadata, invocation/SHA binding, result
counts, and individual SARIF findings before triage. Do not rerun local
CodeQL. Ask Security/CI to decide extension CodeQL scope; ask CI owners to
resolve the protected-approval failure, zero-job Data Quality startup failure,
the zero-job 42956569401 classification, and required-check status. Have the
ML Components/CI owner inspect 42960150291's integration-test failure. Keep
Zod and compiler/lint findings open pending scoped decisions. Do not dispatch
or approve workflows, change scanners, mutate source PRs, push, deploy, or
merge without explicit operation authorization.
```

## PR #5766 merge-readiness checkpoint — 2026-11-12

@mbaetiong authorized maintainer action to bring PR #5766 (`0D_base_` →
`main`) to a mergeable state. At this checkpoint the PR was open with head
`8746dfaa`, base `main` `25ab8b63`, `mergeable=true` and
`mergeable_state=unstable`. Neither `main`'s classic protection nor ruleset
11369401 configures required status checks. The ruleset requires Copilot code
review; failing optional checks report `unstable` but do not block the merge.

The head's 18 pull-request runs were held at `action_required` because
`copilot-swe-agent` authored the commit. The session's Codespaces token got
HTTP 403 on run approval because it lacks `actions:write`. @mbaetiong then
approved them, producing attempt 2. The scheduled auto-approve sweep had found
the same runs but failed all 18 approvals: the GitHub App private-key secret is
not a PEM key (`Invalid keyData`), and the fallback PATs are rejected.
**Owner:** repository admin, to replace the App key and rotate the fallback
tokens.

### Dispositions

- **Data Quality `startup_failure` (fixed in this sub-PR):**
  `data-quality-suite.yml` calls `cost-gate.yml` without job permissions. The
  caller's workflow grant is `contents: read, pull-requests: write`, while
  `cost-gate.yml`'s `rescue-comment` job requests `issues: write`. GitHub
  rejected the run at startup with zero jobs. The workflow file is identical on
  `main`, so this is pre-existing.
  - The caller now grants exactly what the reusable workflow requests, the same
    grant already used by the working `rust_swarm_ci.yml` caller.
  - The manually disabled `docker-build-push.yml` had the same latent defect
    and gets the same grant.
  - A regression test checks every `cost-gate.yml` caller.
  - Nothing in `cost-gate.yml` was weakened.
- **Agent Token Delegation (owner settings action):** attempt 2 failed only at
  `Verify protected owner approval`. The `owner-approval` environment exists
  without protection rules, and this token cannot read secrets. The fail-closed
  gate is intentionally unchanged.
  **Owner:** repository admin. Configure the required independent reviewers
  and the `OWNER_APPROVAL_PROTECTED` secret as described in
  `MAINTAINER_PROVIDER_EXECUTION_GUIDE.md`.
- **ML Components integration job (pre-existing):** the merge-commit run
  `42960150291` and daily `main` schedule runs share the same failure baseline.
  The intermittent `tests/integration/test_gap23_boundaries.py` failures
  (`No module named 'monitoring.dashboard_api'`) also occur on main-based
  Dependabot runs `43001109241` and `42593310266`. This is not a PR #5766
  regression.
  **Owner:** ML Components/CI maintainers, to isolate the order-dependent
  `monitoring` import pollution.
- **Scorecard `auto_fix` dimension (open backlog):**
  `auto_fix_common_issues.py --check-only` reports repository-wide existing
  findings: patterns 6, 7, 19, 34 and 36, including 4,587 assertion-message
  candidates. These were not mass-edited in this scoped change. The check also
  rewrites `.codex/fragile_tests.json`; revert that side effect before
  committing.
- The SARIF artifact binding, `copilot/extension` CodeQL scope, Zod advisory
  and compiler/lint backlog items above remain open and unchanged.

### Validation (local)

- `pytest tests/capabilities/ci_test/test_cost_gate_integration.py
  tests/ci/test_owner_approval_guard.py tests/unit/test_check_workflow_yaml.py
  tests/ci/test_workflow_validation.py`: 69 passed.
- The new caller test failed against the unfixed `data-quality-suite.yml`.
- `actionlint` 1.7.12 passed on both changed workflows.
- The workflow compliance matrix is identical with and without the change.
- Hosted results for the published fix must be read from its own runs; local
  results are not hosted CI.

```text
Resume PR #5766 merge readiness from
/workspaces/_codex_/site/plans/0D_base_/CONTINUATION.md. Confirm the
copilot/session-pr5766-merge-readiness sub-PR is merged into 0D_base_ and that
Data Quality on the new PR #5766 head starts jobs. Then classify any failures
against main baselines. Do not weaken OWNER_APPROVAL_PROTECTED or cost-gate
controls. Ask the repository admin to configure owner-approval reviewers and
its secret, and to repair the auto-approve App key and PATs. Keep the SARIF,
extension-scope, Zod and compiler/lint items open pending scoped decisions.
Re-check mergeable/mergeable_state and the required Copilot review before
reporting PR #5766 as ready.
```

## PR #5766 assurance repair — 2026-11-12

**NOT READY:** `mergeable=true` does not clear the remaining assurance gates.
PR #5766 is open at head `285a0090f1d7ced742528410b4fde2690d13dc38`,
base `25ab8b63afc8fddcc93dbbfb123e0d708c777e0e`, with
`mergeable_state=unstable`. All four review threads are resolved. Data Quality
run `43149315400`, attempt 1, succeeded on this exact head; the startup failure
is fixed. Agent Token Delegation `43149315443` and ML Components
`43149315492` still fail. Baseline parity alone is not owner acceptance.

### Original artifact recovery and binding

All four archives listed earlier were downloaded to restricted local session
storage and verified against the API digests in that table. The authenticated
API redirect and signed storage download were separate requests; no GitHub
credential was forwarded to the storage host. Raw SARIF stays outside Git.

| Extracted member | SHA-256 |
| --- | --- |
| Python `python.sarif` | `a76317d5017d31c5c01a0c2cfbd0a8a0ef04184251b548afb76be103a1358247` |
| JavaScript `javascript.sarif` | `54e45be60cc1296e69a9175c449b65d50d92e64f30fefa2ede4ff0b345a92a75` |
| Both `scan-source.json` members | `a247a3ed31fc7d10e9f9718c48aeff255d33064338ba64733523ea43c5950f05` |

Both source records identify run `42955914698`, attempt `2`, PR #5773,
`refs/pull/5773/merge`, and checkout/event SHA
`5e3fd6b85e7eca154f3cf13d2421d7f8d90fe007`. Its parents are `fec36206`
and `aafbc726`; Git verifies tree
`e749b94c89971ffefaeb4a4c6b24bc158a37cfcf`, identical to that old PR head.
Artifact metadata binds all four to that run/head. JavaScript uploads at
04:01:22–23Z fall within job `130312198375` (04:00:00–04:01:27Z); Python
uploads at 04:11:33–34Z fall within job `130312198331`
(04:00:00–04:11:39Z), all on 2026-11-11.

SARIF reports CodeQL **2.27.4**, successful invocations, language-specific
automation IDs, and no error-level extraction notifications. It does not
contain `versionControlProvenance`; checkout binding relies on the verified
co-retained source records and run/job/artifact metadata, not an invented
embedded SHA.

Current candidate tree `3867a0fcc36d47bf1daf9e4855b94d8cb896e86b` differs
in nine paths: the startup packet, Data Quality/Docker workflows,
`.secrets.baseline`, `CHANGELOG.md`, `CODEX_MANIFEST.json`, accountability,
this continuation and `tests/ci/test_workflow_validation.py`. Thus old
artifacts are not exact-candidate evidence. No timestamp restoration or local
CodeQL rerun was performed.

### Result-count discrepancy and bounded review

The actual complete arrays contain **2,794 Python results and zero JavaScript
results**, not 35. Six Python results carry the `security` tag (all rule
security-severity 7.8); the remaining 2,788 are quality/reliability findings
and are not individually accepted or dismissed. The unrelated local
37-result JavaScript file is not a substitute. **Owner: Security/CI**, to
identify the source of the 35-result claim and accept a candidate-bound triage.

The following are provisional technical classifications of the six actual
security-tagged results, not alert dismissals or independent risk acceptance.
Their files are unchanged between the analyzed checkout and `285a0090`.

| Rule / location | Reviewed context and proposed disposition |
| --- | --- |
| `py/incomplete-url-substring-sanitization`, `scripts/validate_and_fix_links.py:150` | Classifies schemeless GitHub links for an offline documentation checker; all HTTP(S) URLs are already accepted. No network request, authorization or hostname trust decision occurs here. Proposed non-security result; Security owner to confirm. |
| Same rule, `tests/test_link_validation.py:352` | Assertion on a fixed malformed-link fixture, not untrusted endpoint authorization. Proposed test-only result; Security/test owner to confirm. |
| Same rule, `tests/github/test_package_registry.py:171` | Assertion on literal `https://ghcr.io`; no dynamic URL or network call. Proposed test-only result; Security/test owner to confirm. |
| `py/overly-permissive-file`, `tests/test_monkeypatch_log_adapters.py:452` | Makes a synthetic database read-only inside a `TemporaryDirectory` for a permission-error test. No production data; parent directory restricts access. Proposed test-only result; Security/test owner to confirm. |
| Same rule and file, line 464 | Restores synthetic database permissions inside that private directory before cleanup. Proposed test-only result; Security/test owner to confirm. |
| Same rule, `tests/test_phase12_tier2_lane4_edge_cases.py:491` | Restores an empty temporary fixture before immediate deletion. Proposed test-only result; Security/test owner to confirm. |

### Extension coverage and authentic approval

The prepared shared-config change adds only `copilot/extension/`. Enterprise
Compliance, the GA gate and the manual/reusable security-suite CodeQL lane
consume it. Queries, exclusions and permissions are unchanged. Both original
SARIFs have **zero extension artifacts/extraction diagnostics**. New hosted
JavaScript extraction must include `server/index.js`, `test/server.test.js`
and `eslint.config.js`; configuration or unit tests alone cannot close this.

Exact-head token job `130955570479` fails because
`OWNER_APPROVAL_PROTECTED` is empty. The live environment has no protection
rules, permits admin bypass, and has no pending deployment approval.
Environment-secret public-key access and workflow-permission access return
HTTP 403. **Owner: repository/security administrator**, to configure genuine
independent reviewers and the protected secret using an authorized account.
The workflow guard remains unchanged. Broad task authorization cannot supply
missing API scopes or manufacture independent approval.
Fresh bounded attempts through both already-known fallback token routes
returned HTTP 401; no usable administrative alternative was established.

Local validation passed 43 focused enterprise/CodeQL/approval tests (zero
skips after supplying Node); two existing pytest configuration warnings remain.
actionlint passed on all three consumers; scoped secret scanning returned
zero findings; `git diff --check` passed. Installed official checksum-verified
GitHub and musl Copilot CLIs in user scope. System Node installation was denied;
signed Alpine packages were instead extracted into user scope without system
install scripts. Native runtime diagnostics work; native Actions MCP still
fails with the owner-header mismatch, so verified REST/`gh` is used.

The CI Testing Agent is repairing the separate ML integration lane. Keep
the Zod advisory, compiler/lint backlog, 2,788 unreviewed quality results and
authentic owner decisions open. Do not promote #5766 until its exact head has
completed required analysis/checks and actual owner dispositions.

### Published coverage proof and gate parser correction

Draft repair PR **#5776** targets `0D_base_`. Signed commit
`809d2824d8c697a9417c45a41b3c005956094d19` is verified by GitHub. Its
automation successor `0f6e088df0c28ae3333d993b168bcf08e93b010c` changes only
`.secrets.baseline` and `CODEX_MANIFEST.json`; it was fast-forwarded locally
without discarding the CI Testing Agent's unstaged ML changes.

Hosted JavaScript job `130966429104` in run `43153020206`, attempt 1,
**completed successfully**. Both artifacts were downloaded and hash-verified:

| Artifact/member | SHA-256 |
| --- | --- |
| Results archive `13914304326` | `1213687123d7efc699752b6fb97122b71858d21dc706a50e33b779b8bd001166` |
| Extracted `javascript.sarif` | `500461f7e899869321931ef45bf1730a4425f53cf156123145b54a25ac8b8dc7` |
| Python results archive `13914952037` | `1fd8cad27d4bd1f82db3b04125ad7f40b55ecda209a9b3654c8b36bf2c8c207d` |
| Extracted `python.sarif` | `ce54bfac28139eb3a69e49620c2fc7b220af956c96af9325ec4c106930d505aa` |
| Source archives `13914886232` (JS), `13914748212` (Python) | `0ef4cc6f34629c77c87fe048b979fb4a2508b4953f6f7fef3df2863c2150921c` |
| Both extracted `scan-source.json` members | `e0ca77d515c217e34b77b1bb72042bc918d21b8af4c039a1f019dcdc243a14dc` |

The Python job `130966429434` subsequently completed successfully at
04:19:22Z and the full run completed successfully at 04:19:47Z.
Its verified SARIF again contains 2,794 results: the same six security-tagged
locations listed above and 2,788 quality/reliability results. Successful
analysis is not a zero-finding result or acceptance of that inventory.

The source record identifies PR #5776 head `809d2824`, base `285a0090`,
and synthetic checkout `15667f6c1e1a705d6d49258ffadb5032e48db4e7`.
Git confirms both head and synthetic checkout have tree
`dba669d532de8c6b36fbed2bd2960ecf091b1470`. Successfully-extracted-file
diagnostics include all three expected files:
`copilot/extension/server/index.js`, `copilot/extension/test/server.test.js`,
and `copilot/extension/eslint.config.js`. This SARIF contains **zero results**.
Coverage is now demonstrated for that revision; do not silently transfer the
claim to a later head or to unmerged promotion #5766.

Actual-artifact replay also found a **silent GA gate counting defect**.
All original 2,794 Python results omit `result.level`; their descriptor
`defaultConfiguration.level` carries the severity. The old parser ignored
those defaults and returned `critical=0 high=0 medium=0`.
The repair resolves driver and extension descriptors, respects explicit
result levels, defaults to warning as specified by SARIF, and fails on invalid
indexed references. Replaying the same artifact now returns
`critical=644 high=358 medium=1792` under the **existing** policy buckets.
Those buckets include quality/reliability findings and must not be described
as CVSS vulnerability counts. Queries, filters and thresholds are unchanged.
**Owner: Security/CI**, to review the exposed backlog and approve any separate
policy decision; do not suppress findings to recover a green badge.

The focused enterprise/GA/approval command now passes **45 tests**, including
two parser regressions. Actual-artifact before/after replay verifies both count
triples. Changed-test Black/Ruff/isort/mypy and all-consumer actionlint pass.
From `copilot/extension`, `npm test` passes all three real-server tests and
`npm run lint` passes. An earlier root-directory npm command was a no-op and
is not counted as extension validation. The relocated user-local Node runtime
now supports real child processes and ICU data without system installation.

### ML integration repair published to PR #5776

ML integration fixes (pandas `<3.1` bound for Evidently 0.7, fail-closed drift
parsing, OmegaConf mapping validation, multi-field perf logs, API-doc root,
inactive-tenant revocation) and the GA SARIF level parser fix are committed on
`copilot/session-pr5766-assurance-repair`. Locally, two tests fail identically
on unmodified HEAD due to the repository `torch/` stub; hosted
`test-ml-components (ubuntu-latest, 3.12, integration)` only runs for PRs
targeting `main`, so it must be confirmed on #5766 after #5776 reaches
`0D_base_`. #5766 remains NOT READY pending that run, Security/CI acceptance
of the 2,794-result SARIF inventory, and genuine protected owner approval.

### #5776 integrated; `[skip ci]` suppression of #5766 checks

PR #5776 was squash-merged into `0D_base_` as `a801ed41` at
`2026-11-12T05:05:00Z`. The default squash body listed the bot commit
`chore(manifest): auto-refresh CODEX_MANIFEST.json [skip ci]`, so GitHub
created no `push` or `pull_request` workflow runs for #5766's new head; only
dynamic Copilot/CodeQL runs appeared. An absent run is not a pass. This
follow-up is merged with an explicit commit message free of skip directives so
the PR-to-`main` lanes (ML integration, GA CodeQL gate, RAG) execute on the
real head. **Convention:** when squash-merging staging sub-PRs, always supply
an explicit commit body; never inherit bot `[skip ci]` lines.

Pre-merge hosted results on `1a591054`: Enterprise Compliance & CodeQL
`43156022460` success; WEC, Status, Deferral and Strict No-Deferral gates
success; Agent Token Delegation failed at the protected-approval step
(repository admin owner). RAG Module Tests `43156015673` ended with a hosted
runner shutdown signal (exit 143), matching pre-existing run `41394751224`,
after reporting failures in unchanged `tests/rag/` files. **Owner:** RAG/CI
maintainers to diagnose runner resource exhaustion and the RAG test failures;
no rerun or scope change was made here.

Expected on #5766 once checks run: the GA gate now sees the true backlog
(644 critical / 358 high / 1,792 medium from the original artifact replay) and
should fail under its `high` threshold. That is a correct, previously masked
signal, not a regression to suppress; Security/CI owners must remediate or
formally disposition it before #5766 can be represented as ready.

### Hosted results on #5766 head `46699c4a`; dashboard import fix

PR-to-`main` lanes fired on `46699c4a` after the clean #5777 merge:

- Success: Enterprise Compliance & CodeQL `43162728218`, Data Quality &
  Determinism `43162728308` (startup fix confirmed), Audit & QA
  `43162728075`, Code Quality & Coverage `43162728099`, Semgrep, Security
  Scanning, Validation Pipeline, Rust-Python Hybrid, WEC, Status, Template
  Lint, Deferral and Strict No-Deferral gates.
- ML Components `43162728212`: every matrix lane passed except
  `integration` (5 failed, 537 passed, 22 skipped). All five failures were
  `tests/integration/test_gap23_boundaries.py` API tests raising
  `No module named 'monitoring.dashboard_api'`; two other tests in that
  file passed in the same run, confirming the order-dependent resolution
  noted earlier. The previously repaired pandas/Evidently/OmegaConf/perf/
  doc/tenant failures did not recur.
- Art_CodeQL GA Security Gate `43162728254`: failed as expected with
  641 critical / 358 high / 1,791 medium under threshold `high`. This is
  the correct, previously masked signal. **Owner:** Security/CI maintainers
  to remediate or formally disposition the backlog; not suppressed here.
- RAG Module Tests `43162728399`: runner shutdown signal (exit 143) after
  test failures, matching earlier runs. **Owner:** RAG/CI maintainers.
- Agent Token Delegation `43162728260`: failed at protected owner approval.
  **Owner:** repository admin; the gate is unchanged.

**Fix (direct execution):** `tests/conftest.py` deliberately places `src/`
before the repository root, so `monitoring` resolves to `src/monitoring`
(which has no `dashboard_api`) unless an earlier test cached the root
package. The integration test now loads the repository-root
`monitoring/dashboard_api.py` by explicit path under a private module name,
without changing `sys.path` order or either package. Locally the five tests
failed in isolation before the change and all 19 tests in the file pass
after it; the full local integration lane shows no `gap23` failure (the
remaining local failures are the known root `torch/` stub shadowing and a
missing local `msgpack`, all passing in hosted CI). Hosted ML integration on
the next #5766 head remains the authority.

#5766 remains NOT READY: GA gate backlog disposition, RAG runner/test
failures and genuine protected owner approval are open owner items, and the
Zod advisory and compiler/lint backlog stay open.
