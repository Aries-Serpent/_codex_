# Recursion diagnosis

## Scope and environment

- Assigned branch: `copilot/recover-unpushed-session-commits-again`.
- Inspected HEAD: `91759b88f02c9981d0cb91f7fc4d0c801072aef2`.
- Comparison base: `71613ee000808ab758cc2f8ddb07a05c5101f731`.
- Interpreter: `/home/runner/work/_codex_/_codex_/.venv_ci/bin/python`,
  Python 3.12.10; pytest 9.1.1.
- Repository and command working directory:
  `/home/runner/work/_codex_/_codex_`.
- Read `/home/runner/work/_codex_/_codex_/.github/instructions/python.instructions.md`
  and `/home/runner/work/_codex_/_codex_/.codex/CODEBASE_AGENCY_POLICY.md`.
- Dependency restoration was running concurrently in the parent session.
  Initial imports found no installed Torch, Transformers, Datasets or Accelerate
  distributions. Torch resolved to the repository stub, version `stub`, without
  `torch.long`; Transformers and Datasets had repository-local specs but their
  imports raised `ModuleNotFoundError`. Hydra 1.3.7 and OmegaConf 2.3.1 imported.
  See `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/interpreter-import-availability.log`.
- Raw output directory:
  `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs`.

## Exact isolated commands and initial results

Each command ran in a separate Python process with a 180-second bound.
The `.log` files are unmodified stdout/stderr; matching `.exit` files record
the shell exit status separately. No test command timed out.

| Command | Exit | Result | Raw log |
| --- | --- | --- | --- |
| `timeout 180s python -m pytest tests/test_phase7b_gap_fill_batch2.py -x -q` | 0 | 74 passed | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_phase7b_gap_fill_batch2.log` |
| `timeout 180s python -m pytest tests/codex_ml/test_training_helper_import_contracts.py -x -q` | 2 | Collection error: `AttributeError: module 'torch' has no attribute 'long'` | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts.log` |
| `timeout 180s python -m pytest tests/codex_ml/test_training_initialization_contracts.py -x -q` | 0 | 25 passed | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_initialization_contracts.log` |

### First 40 lines of each raw isolated log

All three logs contain fewer than 40 lines, so these are their complete outputs.

`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_phase7b_gap_fill_batch2.log`:

```text
........................................................................ [ 97%]
..                                                                       [100%]
```

`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts.log`:

```text

==================================== ERRORS ====================================
___ ERROR collecting tests/codex_ml/test_training_helper_import_contracts.py ___
tests/codex_ml/test_training_helper_import_contracts.py:17: in <module>
    ???
torch/__init__.py:254: in __getattr__
    raise AttributeError(f"module 'torch' has no attribute {name!r}")
E   AttributeError: module 'torch' has no attribute 'long'
------------------------------- Captured stderr --------------------------------
✓ Determinism bootstrap complete
=========================== short test summary info ============================
ERROR tests/codex_ml/test_training_helper_import_contracts.py - AttributeError: module 'torch' has no attribute 'long'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_initialization_contracts.log`:

```text
.........................                                                [100%]
```

## Observed dependency failure; historical recursion root cause unknown

**No `RecursionError` was reproduced in these isolated executions. There is no
repeated recursion frame to report.** The sole observed failure occurs while
evaluating the helper contract test's parametrization at module scope:

```text
/home/runner/work/_codex_/_codex_/tests/codex_ml/test_training_helper_import_contracts.py:17
  -> torch.long
  -> /home/runner/work/_codex_/_codex_/torch/__init__.py:247-254, __getattr__
  -> AttributeError
```

The repository stub implements `float32`, `float16`, and `bfloat16`, but not
`long` or `float64`
(`/home/runner/work/_codex_/_codex_/torch/__init__.py:223-225`). Its real-module delegation
cannot find an installed Torch distribution. A discoverable `torch` import
spec therefore does not establish availability of the real tensor backend.
This is an evidenced missing-dependency failure, not evidence of recursive
training imports.

Collection-order/global import poisoning from a larger test run remains
unproven. It would require the original failing command/order and traceback
to identify an actual repeated frame. No speculative production or test patch
was made; no skips, xfails or recursion-limit changes were introduced.

## Import-chain comparison with the requested base

Comparison used `git show 71613ee000808ab758cc2f8ddb07a05c5101f731:<path>`
and scoped `git diff` without checking out or modifying the base.

- The current batch-2 tests import `codex_ml.interfaces.peft_hooks`,
  `codex_ml.tracking.mlflow_guard`, and training `dp_config`/`rng_checkpoint`
  during collection. The base deferred imports into individual tests and
  referred to speculative APIs such as `MLflowGuard`; the current contracts
  therefore exercise the import chain earlier.
- Both training contract files are new relative to the base; `git show`
  reports that neither path exists in that commit.
- Importing `codex_ml.training.dp_config` first executes
  `codex_ml.training.__init__`, which attempts `legacy_api`, device strategy
  and unified training imports. Those training provider files, DP/RNG
  implementations, PEFT hooks and the Torch shim are unchanged from the base.
- `codex_ml.__init__` removed eager optional pipeline/metrics/symbolic imports;
  its `__getattr__` implementation is unchanged from the base.
  `codex_ml.utils.__init__` changed from eager provider imports to
  `import_module`-based lazy exports cached in `globals()`.
- `/home/runner/work/_codex_/_codex_/tests/conftest.py` adds `codex_ml` to `_CanonicalPackageFinder`, directing
  that root import to the source package; the finder was already present in
  the base. Other changes include cwd-fixture restoration and formatting.
- `_train_init_helpers.setup_dataset_and_loader` now imports the existing
  canonical `ToyDataset` and `_make_casting_collate` from
  `codex_ml.train_loop` instead of nonexistent training provider modules.
  This import is inside the helper function, not at helper module import.
  `train_loop` calls initialization helpers lazily inside `run_training`;
  this mutual dependency alone does not demonstrate an import recursion.
- `setup_optimizer_with_dp` imports `make_private_model` from the existing
  `codex_ml.training.dp_config` rather than `codex_ml.training.dp`.

The scoped source/conftest diff is retained in
`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/base-import-chain.diff`.

## Focused cross-module validation

```text
timeout 180s python -m pytest tests/test_phase7b_gap_fill_batch2.py tests/codex_ml/test_training_initialization_contracts.py -x -q
```

Exit 0: **99 passed**; output in
`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/combined-available-contracts.log`.
The available suites also pass together, including the initialization tests
that temporarily intercept `builtins.__import__` and restore it via monkeypatch.
This does not reproduce or rule out poisoning from other test modules.

The helper module was rechecked with the same isolated 180-second command while
the parent's dependency installation was still running. It again exited 2 with
the same `torch.long` collection error; raw output is in
`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts-recheck.log`. NumPy had become
available by this recheck, but real Torch had not. Searching the preserved
`.log` files found neither `RecursionError` nor `maximum recursion`.
`git diff --check` exited 0. No Python source changed, so Python compilation,
format/lint and mypy checks were not applicable to this documentation-only
diagnostic work.
Parallel validation was requested for this documentation/evidence scope.
The review backend was unavailable because its configured
`claude-sonnet-4.6` model was not in the service registry; the wrapper's success
label is not evidence of a completed review. CodeQL explicitly skipped this
documentation-only scope as trivial.

## Final rerun after dependency restoration

The parent reported successful installation of `.[test-core,runtime]`. Actual
fresh-process imports subsequently confirmed Torch `2.14.1+cu130` (with
`torch.long`), Transformers `5.20.2`, NumPy `2.5.4`, Tokenizers `0.23.3`,
Accelerate `1.15.0` and Datasets `5.1.0`, all from the same interpreter's
site-packages. See
`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/interpreter-import-availability-dependencies-restored.log`.

Each original isolated command was rerun unchanged with `timeout 180s`:

| Module | Exit | Final result | Raw log |
| --- | --- | --- | --- |
| `/home/runner/work/_codex_/_codex_/tests/test_phase7b_gap_fill_batch2.py` | 0 | 74 passed | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_phase7b_gap_fill_batch2-dependencies-restored.log` |
| `/home/runner/work/_codex_/_codex_/tests/codex_ml/test_training_helper_import_contracts.py` | 0 | 5 passed | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts-dependencies-restored.log` |
| `/home/runner/work/_codex_/_codex_/tests/codex_ml/test_training_initialization_contracts.py` | 0 | 25 passed | `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_initialization_contracts-dependencies-restored.log` |

First 40 lines (each log is shorter than 40 lines):

```text
# /home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_phase7b_gap_fill_batch2-dependencies-restored.log
........................................................................ [ 97%]
..                                                                       [100%]

# /home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts-dependencies-restored.log
.....                                                                    [100%]

# /home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_initialization_contracts-dependencies-restored.log
.........................                                                [100%]
```

All three modules also passed in a single process:

```text
timeout 180s python -m pytest tests/test_phase7b_gap_fill_batch2.py tests/codex_ml/test_training_helper_import_contracts.py tests/codex_ml/test_training_initialization_contracts.py -x -q
```

Exit 0: **104 passed**; raw output in
`/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/combined-dependencies-restored.log`.
No source/test fix is needed on this evidence, and the source state is final
for the parent's full snapshot collection. Dependency restoration resolved
the observed helper collection error without a code change. Recursion remains
unreproduced in both isolated and combined execution of the three modules;
this does not rule out larger-suite import poisoning.

At the parent's final request, all three original isolated commands were
repeated again after installation had completed. Results remained **74 passed**,
**5 passed**, and **25 passed**, respectively, each exit 0 within 180 seconds.
Final raw logs:

- `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_phase7b_gap_fill_batch2-final-isolated.log`
- `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_helper_import_contracts-final-isolated.log`
- `/home/runner/work/_codex_/_codex_/recovery/bfe2456b/validation/logs/test_training_initialization_contracts-final-isolated.log`

Matching absolute-path `.exit` files alongside these logs record each exit code.
`REC_FIX_READY` was sent to the outcome-comparison agent after these final runs.
The historical recursion root cause is **unknown**, not fixed.

## Changes and remaining acceptance boundary

No changes under `/home/runner/work/_codex_/_codex_/src` or
`/home/runner/work/_codex_/_codex_/tests` were justified. Only this requested diagnosis
and its raw validation evidence were created. No startup, workflow, environment
or dependency files were edited, and no commit/push was performed.

Tests emitted `/home/runner/work/_codex_/_codex_/artifacts/metrics.ndjson`,
`/home/runner/work/_codex_/_codex_/artifacts/telemetry.json`
and `/home/runner/work/_codex_/_codex_/artifacts/telemetry.ndjson`.
They were left in place rather than deleting
potentially shared outputs while the parent was working concurrently.
The parent's concurrent startup-packet modification and base-worktree directory
were not touched.

The initial missing-Torch blocker is resolved and all five real
tensor/optimizer helper tests now pass. The parent's reported OpenTelemetry
and Semgrep dependency conflicts were not changed by this subtask. Original
full-suite recursion remains unreproduced and must not be described as fixed.
