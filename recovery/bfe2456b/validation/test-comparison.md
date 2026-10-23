# Test outcome comparison

## Latest continuation: 2026-10-23 (detached execution)

**Not ready. Neither full run is established complete.** New evidence is under
`full/resume-20261023/`. Its `checkpoint-summary.json` and
`checkpoint-background-manifest.json` describe the frozen publication checkpoint;
later local background progress is not silently represented as published evidence.
The earlier sections below remain historical.

| Section | Frozen continuation checkpoint |
|---|---|
| Regression | Reproduces: base pytest exit 0, snapshot exit 1. Source/test zero-round contract mismatch introduced by `053409ad`; no fix commit in this task. |
| Base full run | **Incomplete.** Cumulative observed 3,125 IDs: 3,016 passed, 52 failed, 0 errored, 57 skipped, 0 xfailed, 0 identified xpassed. This continuation has 40 completed test shards, six empty shards, and one absent union target; 758 originally incomplete targets remain pending/running, plus 64 prior-complete targets queued for revalidation. |
| Snapshot full run | **Incomplete.** Cumulative observed 3,160 IDs: 3,095 passed, eight failed, 0 errored, 57 skipped, 0 xfailed, 0 identified xpassed. This continuation has 41 completed test shards and six empty shards; 758 originally incomplete targets remain pending/running, plus 64 prior-complete targets queued for revalidation. |
| Outcome comparison | 3,015 paired passes, one regression, 44 improvements, seven pre-existing fail/error observations, 57 skipped/xfailed observations, one base-only and 36 snapshot-only observations. “Only” means observed on one side, not proven addition/deletion. |
| Recursion modules | 25 completed isolated commands without recurrence (19 passing, six failing for other reasons); three unresolved timeouts; zero demonstrated `src/` circular-import or test-level re-import causes. |
| Coverage | **UNKNOWN on both sides.** No partial percentage or readiness assertion. |
| Workflow check | Empty diff; no workflow edits, approvals, retries, or PR. |
| Push result | Final published SHA/result is recorded in the session response. Only frozen evidence and base startup restoration may be published. |
| Blocked items | Full runs and coverage still pending in detached execution, three diagnostic timeouts, unresolved test-contract mismatch, previously missing 295 historical identities. |

The checkpoint names **every pending/running leaf and its last available line**
in `checkpoint-summary.json`, along with the exact UTC checkpoint timestamp.
It separates the 758 originally incomplete targets from 64 optional revalidation
targets, so cached results are neither dropped nor incorrectly counted twice.
At this checkpoint each side has 821 queued new-attempt leaves and one running
leaf; this includes the 64 revalidation targets. An unstarted shard has no log
line, recorded as null rather than fabricated output. The per-side exact PID,
exit and coverage artifact mappings are in the frozen background manifest.

### Regression diagnosis

The exact test is
`tests/agents/test_edge_cases_phase9_4.py::TestBlueRedTeamSimulatorEdgeCases::test_run_simulation_zero_rounds_raises`.
A fresh standalone pytest command passes on base (exit 0) and fails on snapshot
(exit 1, `DID NOT RAISE any of (IndexError, Exception)`).
The first differing implementation frame is base
`src/agents/quantum_game_theory.py:1327`: an empty `round_results[-1]` raises
`IndexError`. Snapshot lines 1355–1356 instead return final payoffs of `0.0`.
The introducing snapshot commit is
`053409ad98ff3dc40243d1e132a1139e83ffaef7`.

This is a **source/test semantic mismatch, not an environment-only failure**:
the snapshot docstring explicitly specifies zero payoffs for zero rounds,
and `test_quantum_game_core_flows.py` also expects graceful zero-round returns.
The unchanged edge-case test still asserts the incidental old exception.
No source or test was changed, and there is **no fix commit in this task**.
Maintainers must reconcile that expectation with the documented contract in a
separately authorized patch. Exact commands, pytest output, a direct-call
traceback exposing the exception caught on base, and the source diff are in
`regression-diagnosis.json`, `regression-first-frame.json`,
`regression-source-diff.txt`, and per-side `regression-alone.log`.

### All 28 recursion modules rechecked individually

`recursion-classification.json` accounts for every module, its fresh first
40 log lines, exit/status, last line, and historical repeated frames:

- **25 environment-specific/import-order-dependent observations:** completed
  isolated commands do not reproduce recursion; 19 commands pass and six fail
  for other reasons. These are not 25 passing modules or proven permanent fixes.
- **Three unresolved timeouts:** `tests/cli/test_cli_rag_comprehensive.py`,
  `tests/codex_ml/test_rag_comprehensive.py`, and
  `tests/docs_agent/test_integration.py`. Each exceeded 90 seconds plus eight
  seconds of interrupt grace and exited -9; absence of recursion before timeout
  is not a cause classification.
- **Zero demonstrated circular imports within `src/`; zero demonstrated
  test-level re-import causes.** Unsupported classifications are not invented.

All 28 historical traces alternate publication-checkout and detached-worktree
`transformers` shims. A discovery-only `PathFinder` probe confirms that a shim
excluding only its own root can select the other checkout's shim; removing the
other checkout selects the actual installed package. This supports the observed
environment/import-order condition. It does not make incidental lazy `pathlib`
cache misses a root cause. Historical and fresh evidence are explicitly separate
in `recursion-historical-frames.json` and `shim-pathfinder-probe.json`.
No recursion-limit changes, deselections, added skips, xfails, or source fixes
were applied.

### Resumption and coverage

The old **804 NOT_RUN entries are shard selectors, not individual tests**.
The exact original 805 incomplete targets per side, including the one timeout,
are listed with last output lines in `remaining-at-start.json`.
The previously unfinished
`tests/agents/test_phase2_deep_coverage_batch14_exception_handling.py`
now completes with exit 0 on **both sides**.

The pinned trees remain base `71613ee000808ab758cc2f8ddb07a05c5101f731`
and snapshot `70798e17f0bb4463413684eddddd62358faa89d6`. Separate non-editable
environments were recreated with all 243 prior distribution versions matched;
both `pip check` commands exit 0. Subprocess `PATH` now explicitly starts with
the appropriate environment. Because the prior run did not record its
subprocess PATH, prior completed leaves are preserved and also scheduled for
revalidation after the previously incomplete targets, rather than assumed
equivalent for a final coverage claim.

The detached runner has two pytest workers overall, a 12-hour safety bound,
90 seconds per directory and 120 seconds per file, plus eight seconds of
interrupt grace. Directory timeouts/collection errors cause identical file
splits on both sides, with parent outcomes excluded. Every attempt has an
exact command, log, JUnit, PID/start-tick identity, and exit file. Tests run under
separate coverage data prefixes from the start; no coverage-free execution is
silently used to complete the coverage gate. Existing completed artifacts are
not overwritten. Supplemental diagnostic commands are not merged into suite totals.

**Coverage remains unknown while any valid leaf is pending, running, timed out,
or fails collection/execution.** A separately detached watcher combines only
explicit completed leaf coverage files after a side genuinely finishes, and
runs `coverage report --fail-under=80`. No percentage is estimated at this
checkpoint. The effective existing `.coveragerc` omissions remain disclosed.
The report is configured-source coverage, not proof that excluded files were traced.

The background tools are detached and survive the tool-session shutdown, but
they cannot guarantee survival of host reclamation. PIDs are host-local and
must be verified against process start ticks, not reused blindly. At publication,
only immutable completed artifacts and a frozen manifest are staged; live
manifests/logs remain local until a later secret-scanned checkpoint. Resume/poll
using the runtime paths recorded in the checkpoint; if the host is replaced,
recreate the pinned environments and use the published evidence instead of
assuming that the processes or `/tmp` paths still exist.

Publication remains restricted to validation evidence and the startup packet
restored to base, on `copilot/recover-unpushed-session-commits-again`, with no PR.
The workflow diff must remain empty. CI `action_required` runs were inspected
read-only; none were approved or retried.

## Pinned resumable comparison: 2026-10-23

The new execution evidence is under `full/`. Earlier observations below remain
historical; they are not substituted for execution at the requested pinned
snapshot. Neither a missing outcome nor a collection error establishes a pass.

- Base: `71613ee000808ab758cc2f8ddb07a05c5101f731`.
- Snapshot: `70798e17f0bb4463413684eddddd62358faa89d6`.
- Publication branch: `copilot/recover-unpushed-session-commits-again`; no PR.
- Remote publication HEAD at task start was `722c1352db5ee7a217d4cea246d43a7e93a26ca5`,
  not the pinned snapshot. Tests still target the requested snapshot.
- Requested old-to-new comparison: `955cd9974eac713333331482928d9b7d04fe5cf1`
  to `70798e17f0bb4463413684eddddd62358faa89d6`.
- Commits: `dae88aea`, `91759b88`, `f507214f`, `d368aaba`, `70798e17`.
- Changed paths: **164** (two `.codex` files and 162 validation files).
  **Zero `src/` or `tests/` changes**; zero workflow changes.
  Exact commit subjects, SHAs, and every path are in `full/head-change.json`.
- Initial worktree modification: startup-packet timestamp only. It is restored
  to the base version for publication; existing evidence is preserved.

Shard evidence must include root-level test files as well as immediate
directories. A timed-out directory is split by file on both sides, with its
parent outcomes excluded from leaf aggregation. Empty shards (pytest exit 5) are
not passes. Collection-error shards and unexecuted selectors remain incomplete.
Repository-defined optional-dependency exclusions are not added or changed.

Fresh environments use independent, non-editable installations from their
respective detached worktrees, outside the publication checkout. Both contain
243 distributions with identical versions, and both `pip check` commands exit
0. This is not the old shared 292-line environment. First installation attempts
hit a 300-second limit during unpacking; one cached retry per side exits 0.
`full/environment-comparison.json`, per-side import provenance, freezes, install
logs, and `full/pinned-run-manifest.json` record the actual new executions.

The authoritative new run manifest is `full/pinned-run-manifest.json`.
`full/delegated-setup-attempt.json` describes a cancelled preliminary setup
with no test execution; its temporary runtime directories were removed.
No copied source trees or virtual environments are published.

`coverage debug config` selects each tree's existing `.coveragerc`, including
`source = src`, its omissions, and `parallel = True`. Actual shard data files
therefore carry additional process suffixes; these are preserved and mapped
back to selectors. Superseded or unfinished shard data must be excluded from
any later complete-run combination.

Coverage is **unknown** for any incomplete side. The repository's configured
34% threshold does not replace the requested 80% acceptance threshold. Partial
coverage files are checkpoint evidence, never an estimated full-suite result.
Only a complete side may run `coverage combine` followed by
`coverage report --fail-under=80`; exact executed commands belong in its manifest.

### Report for the new pinned execution

**INCOMPLETE: no readiness claim.** The execution window was 900 seconds, with
45 seconds per shard and five seconds of interrupt grace. `tests/agents`
exceeded its directory limit and was split into the same 109 file selectors
on both sides. Its parent XML is excluded from totals. The complete paired
plan has 870 selectors per side, of which 869 are aggregate leaves.

| Section | New pinned execution evidence |
|---|---|
| Head change | Five commits and 164 paths; exact subjects/paths in `full/head-change.json`; no `src/`, `tests/`, or workflow changes in the requested head interval. |
| Base full run | **Not complete. Observed only:** 1,818 named IDs: 1,746 passed, 42 failed, 0 errored, 30 skipped, 0 xfailed, 0 identified xpassed. 61 completed leaf shards, two empty leaves, one absent union selector, one unfinished leaf, 804 NOT_RUN leaves. |
| Snapshot full run | **Not complete. Observed only:** 1,826 named IDs: 1,795 passed, one failed, 0 errored, 30 skipped, 0 xfailed, 0 identified xpassed. 62 completed leaf shards, two empty leaves, one unfinished leaf, 804 NOT_RUN leaves. |
| Outcome classification | 1,745 pass→pass; **one regression; 42 improvements**; zero observed pre-existing failures; 30 skipped/xfailed on either side; zero observed only on base; eight observed only on snapshot. Every observed ID and its XML provenance is in `full/outcome-table.csv`; exact regression/improvement ID lists are in `full/outcome-summary.json`. These are not complete-suite counts or inferred deletions. |
| Base collection errors | Of the **195 historical base `RecursionError` modules**, fresh pinned snapshot evidence shows **164 collecting, 28 still reporting `RecursionError`, zero proven deletions/moves, and three module skips**. The three skips cannot honestly be forced into the requested collect/delete/error categories. Per-module evidence: `full/base-195-fresh-classification.json`. |
| Historical IDs | Eleven supplied historical names remain identifiable; **295 identities remain unavailable**, each explicitly documented as an unknown placeholder in `historical-ids.md`, never fabricated as an actual test ID. |
| Coverage | **Base UNKNOWN; snapshot UNKNOWN at 80%.** Neither side completed; no combine/report command was executed and no partial percentage is reported. Actual data-file hashes and deferred exact commands are in `full/pinned-run-manifest.json` and `full/coverage-status.json`. |
| Workflow check | The requested `git diff --name-only origin/0D_base_ HEAD -- .github/workflows/` has empty output. All four held-back files remain at base. |
| Push result | Publication is restricted to `copilot/recover-unpushed-session-commits-again`; final pushed SHA/result is reported in the session response. No PR is opened. |
| Blocked items | Full runs, complete per-ID classification, 80% coverage verification, 295 historical identities, three skipped baseline-error modules, one observed regression, fresh collection errors, and the unavailable automated review wrapper remain unresolved. |

The remaining 804 leaves on each side comprise **216 directory selectors,
541 root test files, and 47 split files**. The same unfinished leaf on each
side is
`tests/agents/test_phase2_deep_coverage_batch14_exception_handling.py`.
The union selector `tests/agents/test_memory_connection_lifetime.py` does not
exist in the base Git tree: its original pytest exit 4 is preserved, with an
explicit absence proof, rather than counted as a base test error or pass.
The eight snapshot-only observed IDs are from this file.

Observed regression (actual JUnit `classname::name` identity):

- `tests.agents.test_edge_cases_phase9_4.TestBlueRedTeamSimulatorEdgeCases::test_run_simulation_zero_rounds_raises`
  — snapshot assertion: `DID NOT RAISE any of (IndexError, Exception)`.

The **42 improvement identities** are listed individually in
`full/outcome-summary.json` under `improvements` and in CSV rows classified
`improvement`; no classification is inferred from a missing outcome.
The 1,826-row CSV excludes superseded parent XML and anonymous cases.
Nonstrict XPASS identification uses the added `-rX` terminal output; no observed
passing record has unresolved XPASS status. Missing execution outcomes still
remain unknown, including any unexecuted XPASS tests.

### Fresh collection diagnostics are also incomplete

After shard execution, each isolated environment additionally ran:
`python -m pytest tests/ --collect-only -q -v -rs -p no:cacheprovider`.
Each had a 180-second limit and five-second interrupt grace. These commands
execute **no test bodies** and contribute nothing to the outcome CSV or coverage.

- Base: **11,114 printed node IDs, 70 observed `RecursionError` headers**;
  interrupted, process exit 2, 184.18 seconds including shutdown.
- Snapshot: **43,501 printed node IDs, 31 observed `RecursionError` headers**;
  interrupted, process exit -9 after interrupt grace, 185.09 seconds.

These are partial observations, **not completed collection totals**. In
particular, the historical 44,053/zero-error snapshot collection must not be
reused as proof that the fresh isolated environment collects cleanly.
Metadata, node IDs, error header/exception line references, and skip reasons
are preserved in `full/fresh-collection-observations.json` and per-side logs.
Of the 195 historical baseline-error modules, the three explicit fresh skips
are `tests/codex_ml/test_cli_train_config_bridge.py` (mlflow absent),
`tests/config/test_override_propagation.py` (Hydra override-file path unavailable),
and `tests/data/test_dataset_loaders_extended.py` (h5py absent).

Maintainer continuation: use the pinned revisions, per-side freezes and exact
manifest commands; resume the 804 NOT_RUN leaves and unfinished leaf on each
side without reusing older partial evidence as completion. Existing completed
leaves are reusable only with matching source/environment/configuration.
Investigate the observed regression and recursion errors separately before any
readiness decision. Recover the original historical identity artifact to resolve
the 295 missing identities. Only after all valid leaf bodies complete may the
recorded side-specific combine/report commands establish the 80% gate.

The historical 295 missing identities are documented in `historical-ids.md`;
placeholder rows are explicitly not test IDs and cannot establish improvements.

The required automated validation wrapper was attempted during this execution
but failed before review with:
`GitError: timeout git error: Command killed by signal SIGPIPE: git -c core.quotePath=false diff --no-renames --irreversible-delete -U0 71613ee000808ab758cc2f8ddb07a05c5101f731`.
This is not a successful review or CodeQL result.

A separate scoped read-only evidence review found **no significant issues**.
CSV identity/class totals, 295 placeholder rows, 195 module records, paired
selector symmetry, coverage-file uniqueness/hashes, base startup restoration,
and the empty workflow diff were checked successfully. Both worktrees began
clean and ended without tracked-file changes; no copied runtime is published.
An initial placeholder-count assertion used the wrong row pattern; the
corrected format-specific check passed without changing any evidence rows.

The mandatory secret-scanning tool passed on explicitly listed reports and
major raw logs. The existing local `detect_secrets scan --no-verify --all-files`
also scanned the complete evidence tree: **157 candidates**, all reviewed as
155 Git/evidence hashes or known artifact/source paths and two synthetic
test-assertion strings; **zero unresolved secrets**. See
`full/secret-scan-summary.json`. No credential verification network call was used.

`git diff --cached --check` exits **2** on 477 whitespace diagnostics in
preserved raw `.log` and `.xml` tracebacks. These outputs are kept verbatim,
not silently edited. The same check excluding raw log/XML/CSV files exits
**0**; there are no metadata/documentation whitespace findings.

### Earlier execution evidence (not a completed pinned comparison)

## Result: INCOMPLETE; acceptance gates not established

The complete-suite regression count is **unknown**, not zero. The base full run
timed out before producing JUnit; the available snapshot full-run XML is partial.
The user-required **80% coverage gate is NOT VERIFIED**. No complete full-run
coverage total is available. Individual shard coverage is not a suite total and
must not be added or treated as satisfying the gate.

## Environment and provenance

- Interpreter for this worker's runs:
  `/home/runner/work/_codex_/_codex_/.venv_ci/bin/python`.
- Python: `3.12.10 (main, Apr 8 2025, 22:38:13) [GCC 13.3.0]`.
- Dependency installation sentinel reported exit **0** before base collection.
- Base: `71613ee000808ab758cc2f8ddb07a05c5101f731`.
- Snapshot collection: `f507214f5d560762384eda29166d97b420d95948`, with
  concurrent dirty runtime artifacts recorded in `snapshot-collection-metadata.json`.
- Actual base-run worktree:
  `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/base-worktree`, detached at
  the recorded base commit and removed after evidence was copied. The parent's
  separately prepared `/tmp/bfe2456b-outcome-base` worktree was preserved.
- The same installed interpreter was used, without reinstalling between sides.
  Pytest's configured `pythonpath = src agents/codex_client` selects the local
  checkout's source. Editable distributions still reference the main checkout;
  complete package/environment isolation is **not** claimed.
- Exact per-run freezes and interpreter records are under `logs/`:
  `base-{collection,full}-pip-freeze.txt`, `base-shards-pip-freeze.txt`,
  `snapshot-{collection,full}-pip-freeze.txt`, and corresponding `*-python.txt`.
  All contain 292 freeze lines. Base collection differs only in six editable
  VCS revision references (`91759b88` versus `f507214f`), reflecting a concurrent
  main-checkout commit. Base full, base shards, snapshot collection and the
  pre-existing snapshot full freeze match byte-for-byte.
- Dependency consistency is **not clean** despite installation exit 0:
  the parent's `pip check` exited **1**; `logs/pip-check.log` records seven unsatisfied requirements involving
  OpenTelemetry instrumentation/exporters and existing Semgrep. Installed
  `opentelemetry-api`/`sdk` 1.45.1 conflict with Semgrep's `~=1.37.0`
  requirements; semantic conventions 0.66b1 conflict with instrumentation's
  required 0.58b0. Both sides share this environment; installation success is
  not evidence of a conflict-free dependency set. The coordinating session
  owns any separately authorized dependency reconciliation.
- A later handoff described publication HEAD `dae88aea`; the actual checkout
  rechecked by this worker was still `f507214f5d560762384eda29166d97b420d95948`,
  matching its snapshot run metadata. These results are **not** asserted to
  validate `dae88aea` or stale context revision `955cd997`.
- `.codex/agent_environment_config.yaml` has an existing net delta from base
  (three additions, six deletions). It was preserved, not edited by this worker;
  no whole-checkout source-identity claim is made. The handoff also reports the
  startup timestamp was restored to base; this worker did not alter it.

## Exact requested commands and observed results

Commands below use the interpreter above as `python`. Raw output is in `logs/`.

| Side | Command | Result |
|---|---|---|
| Base | `python -m pytest tests/ --collect-only -q` | exit **2**, **426.216 s**, **195 collection errors**, **41,560** collected items |
| Base | `python -m pytest tests/ --cov=src --junitxml=recovery/bfe2456b/validation/junit-base.xml -q` | **600 s timeout**, exit **124**, no full-run XML emitted; empty buffered log |
| Snapshot | `python -m pytest tests/ --collect-only -q` | exit **0**, **40.628 s**, **44,053** collected items, no collection errors |
| Snapshot | `python -m pytest tests/ --cov=src --junitxml=recovery/bfe2456b/validation/junit-snapshot.xml -q` | existing main-session evidence: interrupted with SIGINT at **572 s** to preserve XML before the 600 s bound, exit **2** |

The parent executed the snapshot full run in the same installed environment;
this worker executed snapshot collection and supplementary shards. The recursion
agent reports readiness was repeatedly sent
directly since 22:44 UTC; those confirmations are project evidence, regardless
of when this worker processed queued messages. No source/test edit was pending.
The snapshot invocation and interruption attribution above derive from
the existing log, XML, freeze and `snapshot-full-interruption.txt`, not an invented
second invocation. Collection errors were never treated as passes; the full
base command was attempted despite its collection failures.

## Bounded split fallback

After the base full-run timeout, a maximum of **two workers** ran standard pytest
selectors, each with `--cov=src --junitxml=... -q` and a **45 s** outer timeout.
The directory/root-file inventory contained **219** immediate test directories
and **535** root test files in base, not the anticipated 221 directories.
The first budget was 300 s (actual 300.054 s); an additional matched-root-file
budget was 180 s (actual 166.543 s). No tests were deselected, newly skipped or
xfail-marked; recursion limits and source were unchanged by this worker.

Of **754** selectors: **12 COMPLETED**, **11 TIMEOUT**, **731 NOT RUN**.
Exit 5 (`tests/assets`, no tests collected) is not counted as a passing test.
`base-shard-manifest.json` records every selector, its exact command, status,
duration and available XML. Eight extra root selectors were chosen explicitly
from modules with existing snapshot outcomes to obtain comparable identities;
this is partial evidence, not an unbiased complete-suite sample.

After the initial handoff, this worker processed `REC_FIX_READY` from recursion-diagnosis:
no source/test edit was justified. This worker then ran the snapshot split
fallback with **two workers**, **45 s** per selector and a **300 s** total budget
(actual 300.051 s). The snapshot inventory contains **219** directories and
**540** root test files: **9 COMPLETED**, **7 TIMEOUT**, **743 NOT RUN**.
The eight matched root files were prioritized, followed by directory selectors.
`snapshot-shard-manifest.json` records every selector, command and status;
`logs/snapshot-shards-{pip-freeze,python}.txt` records its environment.
Remaining selectors on both sides are required for broader comparison.
Concurrent shard coverage databases are not used as aggregate coverage evidence.

The recursion-diagnosis agent's final restored-dependency handoff supersedes its
earlier helper-module dependency blocker: the three isolated modules passed
unchanged (**74**, **5**, **25** tests), and their combined run passed **104**
tests under a 180 s bound. It reports real Torch 2.14.1+cu130 and Transformers
5.20.2 from the virtual environment, no reproduced `RecursionError`, and no
justified source/test edits. This is separately attributed focused-test evidence,
not additional complete-suite outcomes or a replacement for either full run.
See `recursion-diagnosis.md` and `*-dependencies-restored.log/.exit` evidence.

## Observed outcomes, not complete-suite totals

Identity comparison uses exact JUnit `classname::name` strings. It does not
fabricate pytest node IDs from class names.

| Evidence | Passed | Failed | Error | Ordinary skipped | Xfail | Reported testcase elements |
|---|---:|---:|---:|---:|---:|---:|
| Base supplementary shard XML | 325 | 10 | 4 | 0 | 0 | 339 |
| Snapshot interrupted full XML, named records only | 5,055 | 157 | 22 | 256 | 49 | 5,539 |

The XML contains **5,540 raw testcase elements**, including one anonymous
`<testcase time="0.002" />` with no name or class. That record is **not a pass**
and is excluded from identity/outcome comparisons. The remaining **5,539 named
records** agree with the suite header's `tests=5539`; there are **zero duplicate
named `(classname, name)` keys**. Raw XML is unchanged. No full-run `.coverage`
data survived in the main checkout according to the parent; later shard data
does not establish complete-suite coverage.

Only **19 identities** are reported on both sides:

- **17 pass → pass**.
- **0 observed regressions** (base pass → snapshot fail/error), **within these 19 only**.
- **0 observed improvements** (base fail/error → snapshot pass), within these 19.
- **2 pre-existing fail → fail**:
  - `tests.test_config_validation::test_training_validation_errors_include_path`
  - `tests.test_continuous_learning::test_model_comparison_and_rollback`
- **0 observed skip/xfail changes** among common identities.
- **320** base-reported identities are **not reported in snapshot**.
- **5,520** snapshot-reported identities are **not reported in base**.
- Non-strict **XPASS count is unknown**: quiet interrupted output and JUnit do
  not reliably distinguish these from passing tests. No explicit XPASS evidence
  was found; that is not proof of zero.

Missing outcomes are not passes, regressions, improvements, removed tests or
waived failures. `outcome-comparison.json` lists the actual reported identities
and all comparison sets.
Existing Torch/Pydantic-dependent collection exclusions in `tests/conftest.py`
can prevent tests from entering collection at all; such omissions are not
necessarily explicit JUnit skips. See `collection-diff.md`. No exclusion policy
was added or modified by this worker.

### Readiness-gated paired shard comparison

The later snapshot shard XML is kept separate from the interrupted full-run
XML; differing execution contexts are not silently merged. Snapshot shards
report **64 passed**, **2 failed**, **0 errors**, **0 skipped/xfail**, totaling
**66 testcase elements** in nine XML files.

Compared with base shards, **65 identities** are common: **63 pass → pass** and
the same **2 fail → fail** identities listed above. Within these 65 there are
**0 observed regressions**, **0 improvements** and **0 skip changes**.
**274** base-shard identities are not reported by snapshot shards; **1**
snapshot-shard identity is not reported by base shards. Complete-suite
regressions and XPASS remain unknown. Exact sets and separate source XML paths
are under `paired_shards` in `outcome-comparison.json`.

## Historical 306 errors and remaining work

No complete historical 306-ID artifact was available under the repository to this
worker. A subsequent
parent-transcript handoff supplies **11 historical error → skip identifiers and
reasons**; the other **295 identities/dispositions remain UNKNOWN**. The present
195 base collection errors are a separate observation.
`collection-diff.md` documents the current collection change without inventing
historical IDs.
The supplied 11 are old-environment transcript evidence, **not current-run
classifications**, and no historical improvements are proven. Their exact
supplied names/reasons appear in `collection-diff.md` and
`outcome-comparison.json`. The explorer confirmed no complete historical list
was found; do not infer the remaining 295 identities.
The historical report of 432 pytest errors is not an old mypy exit-code result
and is not used as a per-ID outcome baseline here.

Owner/next step: the coordinating session should integrate historical evidence
and authorize/execute remaining bounded selectors
as appropriate. Preserve the existing snapshot failure/error evidence; do not
declare green tests, zero full-suite regressions or 80% coverage from this run.

Artifact validation: six generated JSON documents, 13 base shard XML files,
nine snapshot shard XML files and the existing full snapshot XML parsed
successfully; scoped `git diff --check` passed.
The parallel review service failed while computing its git diff
(`GitError: timeout git error`, SIGPIPE); no successful service review is claimed.
The parent separately attempted parallel validation: its Code Review backend
was unavailable (`capi-prod-claude-sonnet-4.6` model not found), despite wrapper
success. Therefore **no clean Code Review result exists**. The parent's CodeQL
check was skipped as documentation/timestamp-trivial, not executed successfully.
The parent reports its secret scan of the initial diagnostics logs passed;
that scan is not claimed to cover every subsequently generated artifact.
