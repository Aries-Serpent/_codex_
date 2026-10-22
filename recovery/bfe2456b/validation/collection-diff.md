# Collection comparison

Both requested commands were executed with the same installed Python 3.12.10
interpreter: `python -m pytest tests/ --collect-only -q`.

| Observation | Base `71613ee0` | Snapshot `f507214f` |
|---|---:|---:|
| Exit code | **2** | **0** |
| Wall time | 426.216 s | 40.628 s |
| Collected item count from module-count output | 41,560 | 44,053 |
| Modules reporting collected items | 2,579 | 2,791 |
| Collection error summaries | **195** | **0** |

Base errors include widespread `RecursionError` failures. The full base command
was still attempted and timed out; collection failure was not treated as a pass.
The snapshot has **2,493 more collected items**, but these are not necessarily
new tests: modules blocked by baseline collection failures can now contribute.

## Module-level diff

- **212** modules report items only in snapshot.
- **0** modules report items only in base.
- **26** shared modules have changed reported item counts.
- Full exact paths, counts and current collection error summary strings are in
  `collection-comparison.json`.

The exact commands combine requested `-q` with configured quiet options and
therefore emit **module item counts**, not individual node IDs. Base individual
IDs are **unknown**; this report cannot claim an exact added/removed-ID diff.
The existing main-session supplemental `logs/snapshot-nodeids-collection.log`
contains **44,053 actual snapshot node IDs**, preserved in
`collection-comparison.json`. There is no fabricated base-ID reconstruction.

## Historical comparison limit

The complete historical **306 error IDs** were not available in a repository
artifact to this worker. A later parent-transcript handoff supplies 11 names
and historical error → skip reasons below; the other **295 identities and
dispositions remain UNKNOWN**. Aggregate current counts do not establish which
historical errors resolved. The current base's 195 errors must not be mislabeled
as the historical 306.

Subsequent explorer handoff confirms neither historical comparison artifact nor
the 306-ID list was found. A complete per-ID historical comparison remains
unverifiable. The separately reported historical **432 pytest errors**
must not be inferred from, or conflated with, an old mypy exit code 2.

### Parent-transcript historical subset: 11 error → skip entries

These names/reasons are preserved exactly as supplied by the parent transcript;
they are **old-environment observations**, not verified current collection or
current test outcomes. The supplied names are not reconstructed pytest node IDs.

| Supplied historical identifier | Historical skip reason |
|---|---|
| `tests.codex_ml.test_cli_train_config_bridge` | mlflow absent |
| `tests.config.test_override_propagation` | Hydra `--override-file` path unavailable with Typer |
| `tests.monitoring.test_logging_bootstrap_real` | mlflow |
| `tests.peft.test_peft_smoke` | PEFT registry unavailable |
| `tests.phase_5_coverage_cli.utils_modules.test_seed_manager` | module not importable |
| `tests.space_traversal.test_peft_comprehensive.test_run_functional_training_resume` | numpy |
| `tests.test_checkpoint_restore_rng_torch` | numpy |
| `tests.test_checkpoint_roundtrip` | numpy |
| `tests.test_monitoring_cli` | mlflow |
| `tests.test_peft_adapter` | torch stub |
| `tests.test_peft_integration` | peft absent |

The other **295** historical IDs were not reported by the old snapshot and no
complete list persisted. They are not passes or proven fixes.
**No historical improvements are proven** by this partial transcript evidence.

## Existing dependency-based collection exclusions

`tests/conftest.py` already contains Torch/Pydantic-dependent `collect_ignore`,
`collect_ignore_glob`, `pytest_ignore_collect` and skip behavior. This worker
did not add or alter those rules. Exit-zero collection and its reported count
cover only tests admitted by the existing environment-dependent policy.
Excluded/not-reported tests are **not passes** and are not necessarily represented
as skipped testcase elements in JUnit. Full repository test availability cannot
be inferred from the collected-item total alone.

## Provenance and limitations

Raw logs: `logs/base-collection.log` and `logs/snapshot-collection.log`; exact
freezes and Python records accompany each. Detailed invocation metadata is in
`base-run-metadata.json` and `snapshot-collection-metadata.json`.
Base ran in an equivalent detached project-local worktree because temporary
directory writes were prohibited. Snapshot collection ran in the assigned main
checkout; concurrent main commits/dirty runtime artifacts are recorded in its
metadata. See `test-comparison.md` for incomplete full-suite and coverage gates.
