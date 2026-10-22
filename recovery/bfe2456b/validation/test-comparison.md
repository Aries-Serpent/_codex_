# Test outcome comparison

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
