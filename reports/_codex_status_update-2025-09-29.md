# _codex_: Status Update (2025-09-29) — Branch: main @ 142662e1dd0bcce7a16d34d0bfeaee5a467a3025

## Audit Scope & Provenance
- Repository: Aries-Serpent/_codex_
- Default branch: main
- Selected branch: main
- S1: 142662e1dd0bcce7a16d34d0bfeaee5a467a3025
- Parents: 7533a009b187b8ca4e8dcc1417bfe3c868e31a86, c5032f742800b934f6c4d30a2a44bfb7d873ed27
- Generated at: 2025-09-30T02:08:53.9418074Z

## Repo Map
# Repo Map

Top-level directories and file counts:
- tests: 444 files
- src: 223 files
- .codex: 171 files
- tools: 129 files
- docs: 119 files
- scripts: 53 files
- temp: 43 files
- configs: 37 files
- artifacts: 34 files
- patches: 20 files
- services: 20 files
- examples: 19 files
- documentation: 16 files
- .github: 15 files
- reports: 13 files
- codex_digest: 12 files
- semgrep_rules: 8 files
- agents: 8 files
- analysis: 8 files
- training: 8 files
- copilot: 6 files
- codex_utils: 5 files
- codex_ml: 5 files
- archive: 5 files
- _codex: 4 files
- data: 4 files
- LICENSES: 3 files
- conf: 3 files
- deploy: 3 files
- mcp: 2 files
- notebooks: 2 files
- hydra: 2 files
- interfaces: 2 files
- schemas: 2 files
- codex_addons: 2 files
- _codex_status_update-0C_base_-2025-09-27.md: 1 files
- _codex_codex-ready-sequence-and-patches-2025-09-27.md: 1 files
- torch: 1 files
- tokenization: 1 files
- requirements: 1 files
- .bandit.yml: 1 files
- yaml: 1 files
- typer: 1 files
- ops: 1 files
- logs: 1 files
- experiments: 1 files
- db: 1 files
- omegaconf: 1 files
- nox_sessions: 1 files
- monitoring: 1 files
- codex.mk: 1 files
- codex_ast_upgrade.py: 1 files
- codex_patch_runner.py: 1 files
- CHANGELOG_CODEX.md: 1 files
- CHANGELOG_SESSION_LOGGING.md: 1 files
- CODEBASE_AUDIT_2025-08-26_203612.md: 1 files
- codex_setup.py: 1 files
- codex_task_sequence.py: 1 files
- codex_update_runner.py: 1 files
- Codex_Questions.md: 1 files
- codex_ready_task_sequence.yaml: 1 files
- codex_script.py: 1 files
- .gitattributes: 1 files
- .gitignore: 1 files
- .pre-commit-config.yaml: 1 files
- .coveragerc: 1 files
- .dockerignore: 1 files
- .env.example: 1 files
- AUDIT_PROMPT.md: 1 files
- bandit.yaml: 1 files
- CHANGELOG.md: 1 files
- .pre-commit-hybrid.yaml: 1 files
- .pre-commit-ruff.yaml: 1 files
- .secrets.baseline: 1 files
- codex_workflow.py: 1 files
- pytest.ini: 1 files
- README.md: 1 files
- requirements-dev.txt: 1 files
- noxfile.py: 1 files
- OPEN_QUESTIONS.md: 1 files
- pyproject.toml: 1 files
- sitecustomize.py: 1 files
- tox.ini: 1 files
- uv.lock: 1 files
- requirements.lock: 1 files
- requirements.txt: 1 files
- setup_universal.sh: 1 files
- DEFERRED.md: 1 files
- docker-compose.yml: 1 files
- Dockerfile: 1 files
- compare_report.json: 1 files
- conftest.py: 1 files
- CONTRIBUTING.md: 1 files
- LFS_POLICY.md: 1 files
- Makefile: 1 files
- mkdocs.yml: 1 files
- Dockerfile.gpu: 1 files
- entrypoint.sh: 1 files
- ERROR_LOG.md: 1 files

- Found: README.md
- Found: pyproject.toml
- Found: tox.ini
- Found: noxfile.py
- Found: requirements.txt
- Found: uv.lock

Key packages:
- codex_ml/
- codex_utils/
- training/
- tools/
- agents/
- scripts/


## Structural Metrics
- Docstring coverage (modules/classes/functions): 39.78 / 30.43 / 21.34 %
- LoC by top-level directory:
- Import cycles detected: 2

## Capability Audit Table\n\n| Capability | Status | Existing artefacts | Gaps | Risks | Minimal patch plan | Rollback plan |\n| --- | --- | --- | --- | --- | --- | --- |\n| Tokenization (SentencePiece/HF) | Implemented | tools/make_spm_fixture.py; tools/gen_tiny_spm.py; src/codex_ml/tokenization/*; configs/train_tokenizer.yaml; docs/validation/tokenization_Validation.md; tests/test_api_infer_tokenizer.py | - Expand round-trip tests (pad/truncation/offsets)\n- Ensure tiny local SP model fixtures used everywhere | - Inconsistent padding/truncation causing shape errors\n- Hidden network deps for tokenizer downloads | - Add deterministic round-trip tests using local fixtures\n- Guard against remote downloads; enforce offline paths | - Revert tests and guards; keep original tokenizer flow |\n| ChatGPT Codex Modeling (init/dtype/device/PEFT) | Partially Implemented | training/engine_hf_trainer.py; training/functional_training.py; src/codex_ml/models/*; codex_ml/models/utils/peft.py; conf/config.yaml | - Explicit dtype/device tests\n- Optional LoRA/PEFT load path behind flag | - Misplaced dtype casts; OOM on device misplacement | - Add init smoke tests (cpu/bf16 fallback)\n- Add PEFT loader flag default-off | - Remove tests and feature flag; restore defaults |\n| Training Engine | Implemented | training/*.py; src/codex_ml/train_loop.py; conf/trainer/base.yaml; tests/test_cli_train_* | - Tiny overfit deterministic test | - Non-deterministic regressions | - Add tiny-overfit single-batch test with fixed seed | - Drop test if regressions occur |\n| Config Management (Hydra) | Implemented | conf/config.yaml; conf/trainer/base.yaml; src/codex_ml/cli/main.py; configs/* | - Document defaults list structure and overrides | - Misconfig leading to silent defaults | - Add README snippet + example conf override | - Revert docs snippet |\n| Evaluation & Metrics | Partially Implemented | src/codex_ml/metrics/*; tools/metrics/*; data/offline/*.json | - NDJSON/CSV logging examples/tests\n- Validation loop examples | - Metrics drift; missing step indices in logs | - Add logging helpers usage and step-aware metric tests | - Remove helper usage/tests |\n| Logging & Monitoring (MLflow offline, psutil) | Implemented | codex_utils/mlflow_offline.py; src/codex_ml/tracking/mlflow_utils.py; tools/monitoring_integrate.py | - Ensure default tracking URI local under artifacts | - Accidental remote tracking | - Default MLflow URI to file:./artifacts/mlruns (done) | - Revert default URI in mlflow_utils.py |\n| Checkpointing & Resume | Implemented | codex_ml/utils/checkpointing.py; training/checkpoint_manager.py; tests/test_checkpoint_* | - Verify RNG restore in resume path on Windows/Linux | - Partial restores yield silent divergence | - Add resume-with-RNG test using codex_utils/repro | - Remove test if unstable |\n| Data Handling (splits/cache) | Implemented | training/datasets.py; training/data_utils.py; training/streaming.py; src/codex_ml/data/loaders.py | - Windows guard for POSIX-only safety sandbox import | - Import errors on Windows block tests | - Make sandbox optional at import in loaders | - Revert import guard |\n| Security & Safety | Implemented | semgrep_rules/*; bandit.yaml; tools/scan_secrets.py; tools/pip_audit_wrapper.py | - Safety scan alternative (offline SBOM) | - Safety CLI requires login; gaps in visibility | - Generate CycloneDX SBOM + local scan (deferred) | - Keep current pipeline |\n| Internal CI/Test (local gates) | Partially Implemented | tox.ini; pytest.ini; tests/*; tools/run_quality_gates.sh | - nox sessions for lint/type/tests/coverage/package | - Inconsistent local runs across machines | - Add noxfile.py sessions (local only) | - Remove noxfile.py if undesired |\n| Deployment (packaging/Docker) | Partially Implemented | agents/codex_client/pyproject.toml; entrypoint.sh; Dockerfile | - Package src/codex_ml; CLI entry points inventory | - Drift between repo run vs. packaged run | - Add pyproject for codex_ml (deferred) | - No change |\n| Documentation & Examples | Implemented | docs/**; documentation/**; scripts/make_quickstart_notebook.py | - Improve docstring coverage | - API usage unclear for new users | - Add pydocstyle gate via nox (deferred) | - No change |\n| Experiment Tracking (MLflow file:) | Implemented | codex_utils/mlflow_offline.py; src/codex_ml/tracking/mlflow_utils.py | - Seed snapshot always written; optional mlflow log | - Missing run reproducibility breadcrumbs | - Ensure seeds.json written and optionally logged | - Revert if not desired |\n| Extensibility (registries/plugins) | Implemented | docs/modeling/registry.md; src/codex_ml/plugins/*; src/codex_ml/registry/* | - Cycle checks in import graph CI (local) | - Plugin cycles cause import-time errors | - Add simple cycle check script to gates | - Remove gate if noisy |\n\n## High-Signal Findings
- Strong offline posture: MLflow utilities default to file-backed stores; multiple offline validation docs.
- Hydra-based configuration present with defaults list; supports overrides.
- Rich checkpointing utilities with extensive test coverage (Windows POSIX caveat).
- Import graph cycles minimal; modular boundaries across codex_ml/codex_utils/training hold.
- Docstring coverage is modest; opportunity to improve public API docs.
- Security scaffolding exists (Bandit, semgrep rules, secret scanning), but Safety scan requires credentials.
- Guardrail scan: No workflow files found. 
- Coverage artifacts produced from a minimal subset; global fail-under triggers in this environment.
- Windows-specific incompatibility: POSIX-only "resource" module in sandbox; full test suite cannot run on Windows.

## Atomic Diffs (applied)
1) Default MLflow URI -> file:./artifacts/mlruns
   - Why: keep runs local under artifacts; aligns with audit outputs.
   - Risk: location change vs. prior defaults; mitigated by env CODEX_MLFLOW_URI override.
   - Rollback: revert change in src/codex_ml/tracking/mlflow_utils.py:MLFLOW_DEFAULT_URI
   - Tests: manual validation via env capture; no behavior change when CODEX_MLFLOW_URI set.
2) Determinism hook: torch.use_deterministic_algorithms(True)
   - Why: stronger determinism per PyTorch docs; falls back to CuDNN knobs if unavailable.
   - Risk: performance/regression on unsupported ops; opt-in via deterministic flag.
   - Rollback: revert codex_utils/repro.py changes in set_seed().

## Local Tests & Gates
- Command: pytest agents/codex_client/tests/test_config.py (subset)
- Coverage: pytest --cov with HTML/XML written to artifacts/coverage/
```
pytest : C:\Users\110438\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-pac
kages\Python311\site-packages\pytest_asyncio\plugin.py:208: PytestDeprecationWarning: The configuration option 
"asyncio_default_fixture_loop_scope" is unset.
At line:1 char:153
+ ... .coverage'; pytest -q agents/codex_client/tests/test_config.py --cov= ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (C:\Users\110438...cope" is unset.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of 
pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop 
scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", 
"class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
C:\Users\110438\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Pyt
hon311\site-packages\coverage\report_core.py:110: CoverageWarning: Couldn't parse Python file 
'E:\_codex_\tools\codex_ingestion_workflow.py' (couldnt-parse)
  coverage._warn(msg, slug="couldnt-parse")
C:\Users\110438\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Pyt
hon311\site-packages\coverage\report_core.py:110: CoverageWarning: Couldn't parse Python file 
'E:\_codex_\tools\codex_seq_runner.py' (couldnt-parse)
  coverage._warn(msg, slug="couldnt-parse")
C:\Users\110438\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Pyt
hon311\site-packages\coverage\report_core.py:110: CoverageWarning: Couldn't parse Python file 
'E:\_codex_\tools\codex_sqlite_align.py' (couldnt-parse)
  coverage._warn(msg, slug="couldnt-parse")
..
ERROR: Coverage failure: total of 0.32 is less than fail-under=80.00
                                                                         [100%]
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.11.9-final-0 _______________

Name                                                 Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------------------------------
agents\codex_client\codex_client\bridge.py              55     29      4      0 44.07%   27-28, 32, 44-49, 58-60, 71-75, 84-86, 106-117, 120, 123, 126
analysis\audit_pipeline.py                              64     64     18      0  0.00%   2-96
analysis\intuitive_aptitude.py                         413    413    184      0  0.00%   10-719
analysis\metrics.py                                     10     10      2      0  0.00%   1-16
analysis\parsers.py                                      8      8      2      0  0.00%   1-17
analysis\providers.py                                    9      9      4      0  0.00%   1-11
analysis\registry.py                                    14     14      2      0  0.00%   1-18
analysis\tests_docs_links_audit.py                     165    165     66      0  0.00%   20-290
codex_ast_upgrade.py                                   205    205     58      0  0.00%   25-1486
codex_digest\cli.py                                     26     26      4      0  0.00%   1-40
codex_digest\error_capture.py                           30     30      0      0  0.00%   1-54
codex_digest\mapper.py                                  25     25     12      0  0.00%   1-58
codex_digest\pipeline.py                                45     45     10      0  0.00%   1-72
codex_digest\semparser.py                               33     33      6      0  0.00%   1-50
codex_digest\tokenizer.py                               55     55     20      0  0.00%   1-74
codex_digest\utils.py                                   14     14      2      0  0.00%   1-22
codex_digest\workflow.py                                23     23      4      0  0.00%   1-38
codex_patch_runner.py                                  169    169     64      0  0.00%   3-261
codex_script.py                                        198    198     30      0  0.00%   18-753
codex_setup.py                                         172    172     38      0  0.00%   20-339
codex_task_sequence.py                                 326    326     86      0  0.00%   9-717
codex_update_runner.py                                 197    197     56      0  0.00%   4-500
codex_utils\logging_setup.py                            75     75     12      0  0.00%   3-129
codex_utils\mlflow_offline.py                           36     36     10      0  0.00%   3-92
codex_utils\ndjson.py                                   33     33      6      0  0.00%   3-47
codex_utils\repro.py                                   103    103     22      0  0.00%   3-146
codex_workflow.py                                      292    292     82      0  0.00%   13-555
configs\base_config.py                                   5      5      0      0  0.00%   3-22
conftest.py                                             26     12     10      4 50.00%   9->22, 13, 17->22, 20, 26-31, 37-46
examples\chat_finetune.py                               14     14      2      0  0.00%   3-41
examples\evaluate_toy.py                                10     10      2      0  0.00%   3-22
examples\mlflow_offline.py                              36     36     14      0  0.00%   20-69
examples\tokenize.py                                    13     13      2      0  0.00%   3-21
examples\train_toy.py                                   12     12      2      0  0.00%   3-32
hydra\errors.py                                          9      9      0      0  0.00%   3-24
interfaces\tokenizer.py                                  2      2      0      0  0.00%   9-11
noxfile.py                                             489    489    150      0  0.00%   2-887
scripts\apply_session_logging_workflow.py              144    144     32      0  0.00%   10-550
scripts\benchmark_logging.py                            62     62     14      0  0.00%   1-91
scripts\check_licenses.py                               26     26      4      0  0.00%   3-41
scripts\cli\viewer.py                                   15     15      0      0  0.00%   2-24
scripts\codex_end_to_end.py                             25     25      4      0  0.00%   9-56
scripts\codex_orchestrate.py                            96     96     32      0  0.00%   17-188
scripts\codex_ready_task_runner.py                     168    168     40      0  0.00%   3-375
scripts\deep_research_task_process.py                  433    433    166      0  0.00%   66-1187
scripts\export_env.py                                   28     28      2      0  0.00%   4-64
scripts\export_env_info.py                              14     14      0      0  0.00%   3-22
scripts\fix_markdown_fences.py                          37     37     14      0  0.00%   2-53
scripts\fix_md_fences.py                                60     60     26      0  0.00%   12-86
scripts\init_sample_db.py                               45     45      8      0  0.00%   9-109
scripts\make_quickstart_notebook.py                     21     21      2      0  0.00%   1-147
scripts\run_codex_tasks.py                              74     74     20      0  0.00%   21-132
scripts\run_sweep.py                                    69     69     22      0  0.00%   9-95
scripts\sbom_cyclonedx.py                               17     17      4      0  0.00%   1-24
scripts\torch_policy_check.py                           47     47      8      0  0.00%   10-85
sitecustomize.py                                        16     16      6      0  0.00%   5-24
src\codex\_version.py                                    2      2      0      0  0.00%   3-8
src\codex\chat.py                                       37     37      2      0  0.00%   17-87
src\codex\cli.py                                       276    276     56      0  0.00%   3-606
src\codex\logging\config.py                              2      2      0      0  0.00%   11-14
src\codex\logging\conversation_logger.py                51     51      8      0  0.00%   8-91
src\codex\logging\db_utils.py                           91     91     30      0  0.00%   12-161
src\codex\logging\export.py                             71     71     22      0  0.00%   22-125
src\codex\logging\fetch_messages.py                     63     63     10      0  0.00%   8-138
src\codex\logging\import_ndjson.py                     107    107     26      0  0.00%   29-271
src\codex\logging\query_logs.py                        158    158     62      0  0.00%   29-257
src\codex\logging\session_hooks.py                      97     97     16      0  0.00%   22-208
src\codex\logging\session_logger.py                    214    214     44      0  0.00%   20-430
src\codex\logging\session_query.py                     115    115     42      0  0.00%   24-204
src\codex\logging\viewer.py                            145    145     54      0  0.00%   26-260
src\codex\search\providers.py                           61     61     14      0  0.00%   10-118
src\codex\training.py                                  499    499    148      0  0.00%   7-1096
src\codex\utils\subprocess.py                            6      6      0      0  0.00%   3-23
src\codex_ml\analysis\extractors.py                     45     45      6      0  0.00%   2-128
src\codex_ml\analysis\metrics.py                         9      9      0      0  0.00%   2-16
src\codex_ml\analysis\parsers.py                        30     30      4      0  0.00%   3-50
src\codex_ml\analysis\providers.py                     196    196     76      0  0.00%   2-288
src\codex_ml\analysis\registry.py                       14     14      0      0  0.00%   2-35
src\codex_ml\callbacks.py                               41     41     12      0  0.00%   25-103
src\codex_ml\cli\__main__.py                             1      1      0      0  0.00%   1
src\codex_ml\cli\audit_pipeline.py                      99     99     44      0  0.00%   2-203
src\codex_ml\cli\codex_cli.py                          153    153     24      0  0.00%   1-333
src\codex_ml\cli\config.py                              61     61      6      0  0.00%   3-106
src\codex_ml\cli\evaluate.py                            98     98     42      0  0.00%   3-192
src\codex_ml\cli\generate.py                            60     60      6      0  0.00%   3-111
src\codex_ml\cli\hydra_main.py                          17     17      8      0  0.00%   3-38
src\codex_ml\cli\infer.py                               57     57      4      0  0.00%   3-107
src\codex_ml\cli\list_plugins.py                        19     19      8      0  0.00%   3-32
src\codex_ml\cli\main.py                                66     66     24      0  0.00%   9-181
src\codex_ml\cli\plugins_cli.py                         53     53     12      0  0.00%   3-123
src\codex_ml\cli\train.py                               94     94     28      0  0.00%   3-128
src\codex_ml\cli\validate.py                            79     79     26      0  0.00%   1-145
src\codex_ml\config.py                                 263    263     94      0  0.00%   3-451
src\codex_ml\config_schema.py                           55     55      8      0  0.00%   6-118
src\codex_ml\data\cache.py                              37     37     10      0  0.00%   3-55
src\codex_ml\data\checksums.py                          26     26      6      0  0.00%   1-55
src\codex_ml\data\cli.py                                24     24      2      0  0.00%   4-43
src\codex_ml\data\hf_datasets.py                        27     27     10      0  0.00%   3-54
src\codex_ml\data\integrity.py                          14     14      2      0  0.00%   3-34
src\codex_ml\data\jsonl_loader.py                       44     44     20      0  0.00%   3-72
src\codex_ml\data\jsonl_stream.py                       23     23     10      0  0.00%   3-49
src\codex_ml\data\loader.py                            275    275    112      0  0.00%   3-533
src\codex_ml\data\loaders.py                           277    277    134      0  0.00%   14-520
src\codex_ml\data\registry.py                          173    173     60      0  0.00%   3-365
src\codex_ml\data\sharding.py                            7      7      0      0  0.00%   2-10
src\codex_ml\data\split.py                              80     80     22      0  0.00%   9-217
src\codex_ml\data\split_utils.py                        71     71     22      0  0.00%   3-122
src\codex_ml\data\splits.py                              6      6      0      0  0.00%   3-32
src\codex_ml\data_utils.py                              54     54     16      0  0.00%   9-142
src\codex_ml\eval\datasets.py                           81     81     46      0  0.00%   3-201
src\codex_ml\eval\eval_runner.py                        51     51     14      0  0.00%   3-108
src\codex_ml\eval\evaluator.py                          38     38      6      0  0.00%   1-61
src\codex_ml\eval\metrics.py                           197    197     80      0  0.00%   3-303
src\codex_ml\eval\run_eval.py                           60     60     22      0  0.00%   1-80
src\codex_ml\eval\runner.py                            189    189     98      0  0.00%   3-312
src\codex_ml\hf_loader.py                              116    116     46      0  0.00%   1-260
src\codex_ml\interfaces\registry.py                     67     67     20      0  0.00%   7-140
src\codex_ml\interfaces\reward_model.py                 83     83     36      0  0.00%   4-176
src\codex_ml\interfaces\rl.py                           97     97     34      0  0.00%   4-148
src\codex_ml\interfaces\tokenizer.py                   228    228     64      0  0.00%   17-532
src\codex_ml\logging\file_logger.py                     65     65     26      0  0.00%   3-86
src\codex_ml\logging\ndjson_logger.py                   55     55      6      0  0.00%   3-91
src\codex_ml\logging\run_logger.py                      77     77     30      0  0.00%   3-151
src\codex_ml\metrics\curves.py                          17     17      4      0  0.00%   2-24
src\codex_ml\metrics\evaluator.py                       40     40     12      0  0.00%   3-63
src\codex_ml\metrics\registry.py                       178    178     58      0  0.00%   12-367
src\codex_ml\metrics\text.py                            14     14      2      0  0.00%   1-30
src\codex_ml\modeling\codex_model_loader.py             81     81     24      0  0.00%   1-164
src\codex_ml\models\activations.py                      30     30      2      0  0.00%   2-46
src\codex_ml\models\decoder_only.py                    154    154     18      0  0.00%   3-237
src\codex_ml\models\generate.py                         39     39     14      0  0.00%   3-63
src\codex_ml\models\loader_registry.py                  25     25      2      0  0.00%   3-57
src\codex_ml\models\minilm.py                           69     69      4      0  0.00%   1-94
src\codex_ml\models\offline_tiny.py                     35     35      8      0  0.00%   3-53
src\codex_ml\models\registry.py                        132    132     56      0  0.00%   3-245
src\codex_ml\models\utils\peft.py                       13     13      2      0  0.00%   3-51
src\codex_ml\monitoring\async_writer.py                 74     74      8      0  0.00%   1-131
src\codex_ml\monitoring\cli.py                          40     40      4      0  0.00%   1-93
src\codex_ml\monitoring\codex_logging.py               362    362    130      0  0.00%   3-793
src\codex_ml\monitoring\microhelpers.py                 76     76     14      0  0.00%   4-133
src\codex_ml\monitoring\mlflow_utils.py                 23     23      6      0  0.00%   8-72
src\codex_ml\monitoring\prometheus.py                   53     53      2      0  0.00%   2-110
src\codex_ml\monitoring\schema.py                       28     28      6      0  0.00%   1-51
src\codex_ml\monitoring\system_metrics.py              347    347    124      0  0.00%   3-778
src\codex_ml\monitoring\tb_writer.py                    22     22      6      0  0.00%   1-44
src\codex_ml\monitoring\tracking.py                     48     48     22      0  0.00%   3-73
src\codex_ml\peft\peft_adapter.py                       27     27      8      0  0.00%   26-136
src\codex_ml\perf\bench.py                             105    105     32      0  0.00%   2-157
src\codex_ml\pipeline.py                               365    365    140      0  0.00%   10-703
src\codex_ml\plugins\loader.py                          66     66     16      0  0.00%   3-116
src\codex_ml\plugins\registries.py                     361    361    124      0  0.00%   3-765
src\codex_ml\plugins\registry.py                        64     64     12      0  0.00%   12-157
src\codex_ml\registry.py                                 9      9      0      0  0.00%   1-15
src\codex_ml\registry\base.py                           85     85     22      0  0.00%   18-218
src\codex_ml\registry\data_loaders.py                    6      6      0      0  0.00%   3-10
src\codex_ml\registry\metrics.py                         3      3      0      0  0.00%   3-12
src\codex_ml\registry\models.py                          3      3      0      0  0.00%   3-12
src\codex_ml\registry\token_cache.py                    31     31      8      0  0.00%   3-56
src\codex_ml\registry\tokenizers.py                    179    179     74      0  0.00%   3-323
src\codex_ml\registry\trainers.py                       27     27      6      0  0.00%   3-45
src\codex_ml\reward_models\rlhf.py                     138    138     48      0  0.00%   11-258
src\codex_ml\reward_models\simple.py                    11     11      0      0  0.00%   1-39
src\codex_ml\rl\scripted_agent.py                       45     45      8      0  0.00%   3-64
src\codex_ml\rl\simple_agent.py                         15     15      0      0  0.00%   3-28
src\codex_ml\safety\filters.py                         557    557    246      0  0.00%   25-1013
src\codex_ml\safety\risk_score.py                       29     29      8      0  0.00%   9-61
src\codex_ml\safety\sandbox.py                          50     50      8      0  0.00%   2-96
src\codex_ml\safety\sanitizers.py                       64     64     14      0  0.00%   1-118
src\codex_ml\symbolic_pipeline.py                      252    252     86      0  0.00%   24-520
src\codex_ml\telemetry\metrics.py                       21     21      0      0  0.00%   1-33
src\codex_ml\telemetry\server.py                        14     14      2      0  0.00%   1-29
src\codex_ml\tokenization\adapter.py                   271    271    110      0  0.00%   3-456
src\codex_ml\tokenization\cli.py                        66     66     10      0  0.00%   1-111
src\codex_ml\tokenization\hf_tokenizer.py               56     56     10      0  0.00%   3-151
src\codex_ml\tokenization\offline_vocab.py              34     34      6      0  0.00%   3-51
src\codex_ml\tokenization\pipeline.py                  126    126     46      0  0.00%   3-218
src\codex_ml\tokenization\sentencepiece_adapter.py     154    154     72      0  0.00%   14-251
src\codex_ml\tokenization\sp_trainer.py                 74     74     22      0  0.00%   10-179
src\codex_ml\tokenization\train_tokenizer.py            11     11      0      0  0.00%   12-47
src\codex_ml\tracking\cli.py                            10     10      0      0  0.00%   2-30
src\codex_ml\tracking\git_tag.py                        19     19      4      0  0.00%   9-34
src\codex_ml\tracking\init_experiment.py               186    186     64      0  0.00%   1-345
src\codex_ml\tracking\mlflow_guard.py                   28     28      8      0  0.00%   3-54
src\codex_ml\tracking\mlflow_utils.py                  113    113     42      0  0.00%   22-327
src\codex_ml\tracking\writers.py                       141    141     44      0  0.00%   1-236
src\codex_ml\train_loop.py                             583    583    202      0  0.00%   18-1002
src\codex_ml\training.py                                41     41     12      0  0.00%   3-71
src\codex_ml\training\callbacks.py                      21     21      6      0  0.00%   13-42
src\codex_ml\training\dataloader_utils.py               10     10      2      0  0.00%   3-39
src\codex_ml\training\eval.py                           53     53     22      0  0.00%   3-91
src\codex_ml\training\functional_training.py           265    265     72      0  0.00%   15-435
src\codex_ml\utils\artifacts.py                         32     32      2      0  0.00%   6-60
src\codex_ml\utils\checkpoint.py                       317    317    134      0  0.00%   3-502
src\codex_ml\utils\checkpoint_event.py                  37     37      8      0  0.00%   1-65
src\codex_ml\utils\checkpointing.py                    455    455    194      0  0.31%   13-920
src\codex_ml\utils\checksum.py                          14     14      2      0  0.00%   9-37
src\codex_ml\utils\checksums.py                         14     14      4      0  0.00%   2-20
src\codex_ml\utils\config_loader.py                    163    163     74      0  0.00%   1-320
src\codex_ml\utils\determinism.py                       61     61     14      0  0.00%   17-130
src\codex_ml\utils\env.py                               24     24      4      0  0.00%   1-45
src\codex_ml\utils\error_log.py                         33     33      4      0  0.00%   1-53
src\codex_ml\utils\experiment_tracking_mlflow.py        55     55     12      0  0.00%   3-155
src\codex_ml\utils\hf_pinning.py                        56     56     26      0  0.00%   3-96
src\codex_ml\utils\hf_revision.py                       11     11      2      0  0.00%   1-23
src\codex_ml\utils\jsonl.py                             10     10      0      0  0.00%   1-15
src\codex_ml\utils\logging_mlflow.py                    23     23      6      0  0.00%   3-67
src\codex_ml\utils\logging_wandb.py                     13     13      0      0  0.00%   1-34
src\codex_ml\utils\modeling.py                          47     47     16      0  0.00%   1-109
src\codex_ml\utils\optional.py                           9      9      0      0  0.00%   1-19
src\codex_ml\utils\provenance.py                        90     90     24      0  0.00%   3-187
src\codex_ml\utils\repro.py                             28     28      6      0  0.00%   3-65
src\codex_ml\utils\retention.py                         85     85     46      0  0.00%   27-179
src\codex_ml\utils\seed.py                              10     10      0      0  0.00%   3-25
src\codex_ml\utils\seeding.py                           43     43     10      0  0.00%   3-111
src\codex_ml\utils\subproc.py                           68     68     30      0  0.00%   3-114
src\codex_ml\utils\torch_checks.py                      54     54     16      0  0.00%   10-125
src\codex_ml\utils\train_helpers.py                     42     42      8      0  0.00%   3-108
src\codex_ml\utils\yaml_support.py                      21     21      2      0  0.00%   1-65
src\ingestion\csv_ingestor.py                           12     12      2      0  0.00%   1-28
src\ingestion\encoding_detect.py                        71     71     22      0  0.00%   17-154
src\ingestion\file_ingestor.py                           9      9      2      0  0.00%   1-23
src\ingestion\io_text.py                                81     81     20      0  0.00%   12-156
src\ingestion\json_ingestor.py                          11     11      2      0  0.00%   1-25
src\ingestion\utils.py                                 170    170     34      0  0.00%   23-351
src\logging_config.py                                   11     11      2      0  0.00%   1-18
src\tokenization\cli.py                                 62     62     20      0  0.00%   1-171
src\tokenization\sentencepiece_adapter.py               26     26     12      0  0.00%   1-55
src\tokenization\train_tokenizer.py                    145    145     38      0  0.00%   1-251
src\utils\checkpointing.py                             100    100     40      0  0.00%   22-236
src\utils\trackers.py                                   20     20      4      0  0.00%   1-29
src\utils\training_callbacks.py                         24     24      6      0  0.00%   6-39
tools\allowlist_args.py                                 11     11      4      0  0.00%   2-17
tools\answer_codex_questions.py                         28     28     14      0  0.00%   2-31
tools\apply_ci_precommit.py                            121    121     32      0  0.00%   19-336
tools\apply_container_api.py                            96     96     20      0  0.00%   24-445
tools\apply_data_loaders.py                             76     76     16      0  0.00%   4-130
tools\apply_docs.py                                    131    131     32      0  0.00%   20-427
tools\apply_hydra_scaffold.py                           87     87     24      0  0.00%   15-274
tools\apply_interfaces.py                              108    108     28      0  0.00%   22-483
tools\apply_ml_metrics.py                              105    105     24      0  0.00%   20-449
tools\apply_mlflow_tracking.py                         102    102     16      0  0.00%   20-367
tools\apply_patch_safely.py                            103    103     18      0  0.00%   2-159
tools\apply_pyproject_packaging.py                     178    178     56      0  0.00%   14-362
tools\apply_safety.py                                   63     63     10      0  0.00%   6-95
tools\apply_stack_polish.py                            182    182     26      0  0.00%   7-711
tools\audit_builder.py                                  60     60     16      0  0.00%   11-131
tools\audit_runner.py                                   33     33      8      0  0.00%   6-53
tools\auto_analyze_errors.py                            61     61     24      0  0.00%   10-122
tools\build_sqlite_snapshot.py                          20     20      4      0  0.00%   1-39
tools\bundle_run.py                                     28     28      2      0  0.00%   2-52
tools\catalog_db.py                                     55     55      6      0  0.00%   3-167
tools\ci_guard.py                                       12     12      4      0  0.00%   2-16
tools\codex_agents_workflow.py                         131    131     36      0  0.00%   10-352
tools\codex_apply_modeling_monitoring_api.py           117    117     22      0  0.00%   16-656
tools\codex_cli.py                                      85     85     24      0  0.00%   2-162
tools\codex_coverage_booster.py                        138    138     32      0  0.00%   17-456
tools\codex_db.py                                       28     28      8      0  0.00%   7-73
tools\codex_exec.py                                     80     80     20      0  0.00%   6-125
tools\codex_execute_audit.py                           159    159     32      0  0.00%   2-336
tools\codex_import_normalizer.py                       194    194     58      0  0.00%   15-378
tools\codex_ingest_md.py                                73     73     22      0  0.00%   7-111
tools\codex_logging_workflow.py                        205    205     52      0  0.00%   16-510
tools\codex_maintenance.py                              35     35     10      0  0.00%   13-90
tools\codex_make_smoke_tests.py                        104    104     26      0  0.00%   8-282
tools\codex_patch_exec.py                              147    147     40      0  0.00%   8-274
tools\codex_patch_session_logging.py                   174    174     62      0  0.00%   16-345
tools\codex_precommit_bootstrap.py                     171    171     50      0  0.00%   22-429
tools\codex_run.py                                     104    104     28      0  0.00%   4-128
tools\codex_run_tasks.py                               126    126     24      0  0.00%   20-457
tools\codex_safety\openai_wrapper.py                    60     60     14      0  0.00%   3-98
tools\codex_session_logging_workflow.py                127    127     34      0  0.00%   6-424
tools\codex_src_consolidation.py                       230    230     80      0  0.00%   7-469
tools\codex_supplied_task_runner.py                    159    159     52      0  0.00%   12-390
tools\codex_task_runner.py                             211    211     56      0  0.00%   14-413
tools\codex_workflow.py                                 60     60     14      0  0.00%   10-112
tools\codex_workflow_executor.py                        93     93     16      0  0.00%   3-156
tools\codex_workflow_session_query.py                   18     18      4      0  0.00%   8-49
tools\compact_ledger_to_parquet.py                      33     33      6      0  0.00%   3-46
tools\disable_remote_ci.py                             113    113     32      0  0.00%   11-171
tools\export_to_parquet.py                              55     55     10      0  0.00%   1-92
tools\file_integrity_audit.py                           88     88     30      0  0.00%   4-149
tools\fix_code_fences.py                                70     70     34      0  0.00%   4-89
tools\gen_tiny_spm.py                                   25     25      4      0  0.00%   4-52
tools\git_patch_parser_complete.py                     479    479    220      0  0.00%   20-809
tools\install_codex_hooks.py                            34     34      2      0  0.00%   2-100
tools\label_policy_lint.py                              57     57     26      0  0.00%   10-84
tools\ledger.py                                         67     67     16      0  0.00%   5-114
tools\lint_policy_probe.py                              26     26      8      0  0.00%   4-39
tools\make_spm_fixture.py                               22     22      2      0  0.00%   7-59
tools\mkdocs_repair.py                                  42     42     24      0  0.00%   2-53
tools\monitoring_integrate.py                          270    270     66      0  0.00%   15-493
tools\offline_repo_auditor.py                          229    229     80      0  0.00%   18-470
tools\package_functional_training.py                    30     30     14      0  0.00%   3-42
tools\pip_audit_prewarm.py                              12     12      2      0  0.00%   4-33
tools\pip_audit_wrapper.py                              40     40     12      0  0.00%   8-82
tools\precommit_block_large.py                          18     18     12      0  0.00%   7-31
tools\preflight_minimal_labels.py                       94     94     28      0  0.00%   4-135
tools\purge_session_logs.py                             50     50     18      0  0.00%   2-101
tools\pytest_repair.py                                  32     32     12      0  0.00%   2-42
tools\revert_or_restore.py                              61     61     24      0  0.00%   21-113
tools\run_codex_improvements.py                         37     37      8      0  0.00%   4-59
tools\run_precommit.py                                  33     33      8      0  0.00%   6-52
tools\run_supplied_task.py                             172    172     54      0  0.00%   18-415
tools\run_tests.py                                      37     37      6      0  0.00%   5-70
tools\runner_doctor.py                                  61     61     26      0  0.00%   8-112
tools\scan_config_references.py                         27     27     16      0  0.00%   3-39
tools\scan_secrets.py                                   50     50     22      0  0.00%   12-84
tools\select_precommit.py                               23     23      6      0  0.00%   4-34
tools\shebang_exec_guard.py                             41     41     18      0  0.00%   2-57
tools\test_auto_analyze_errors.py                       28     28      2      0  0.00%   1-72
tools\unify_logging_canonical.py                       186    186     54      0  0.00%   5-353
tools\update_docs_nav_and_links.py                      48     48     28      0  0.00%   3-73
tools\validate.py                                      178    178     54      0  0.00%   13-279
tools\validate_fences.py                               105    105     46      0  0.00%   24-214
tools\verify_data_paths.py                              22     22      2      0  0.00%   8-36
tools\verify_pins.py                                    18     18      4      0  0.00%   1-28
tools\workflow_merge.py                                192    192     48      0  0.00%   10-381
tools\worm_ship.py                                      22     22      8      0  0.00%   5-34
training\cache.py                                       50     50      8      0  0.00%   1-67
training\checkpoint_manager.py                         121    121     32      0  0.00%   1-180
training\data_utils.py                                 131    131     38      0  0.00%   1-331
training\datasets.py                                    41     41     12      0  0.00%   1-85
training\engine_hf_trainer.py                          441    441    162      0  0.00%   25-1107
training\functional_training.py                        412    412    158      0  0.00%   1-712
training\streaming.py                                   19     19     10      0  0.00%   1-38
------------------------------------------------------------------------------------------------
TOTAL                                                29304  29192   9018      4  0.32%

4 files skipped due to complete coverage.
Coverage HTML written to dir artifacts/coverage
Coverage XML written to file artifacts/coverage/coverage.xml
FAIL Required test coverage of 80.0% not reached. Total coverage: 0.32%

```

## Reproducibility Checklist
- Seeds: random, numpy, torch via codex_utils/repro.set_seed()
- Determinism: torch.use_deterministic_algorithms(True) with fallbacks (see PyTorch docs).
- Environment capture: artifacts/env/{python.txt, pip-freeze.txt, os.txt, hw.txt}
- Code versioning: provenance.json includes S1 and parents; git HEAD pinned during audit.
- MLflow: file backend only by default (file:./artifacts/mlruns).

## Deferred Items
- Full test suite on POSIX environment to exercise sandbox paths.
- Safety vulnerability scan using an authenticated CLI session or SBOM-based scanner.

## Error Capture (selected)
- See .codex/status/errors.ndjson for structured records.

## References
- GitHub REST – Events API: https://docs.github.com/en/rest/activity/events
- GitHub REST – Branches & Refs: https://docs.github.com/en/rest/branches/branches
- GitHub REST – Contents/Git Trees: https://docs.github.com/en/rest/git/trees#get-a-tree
- Hydra Defaults List: https://hydra.cc/docs/advanced/defaults_list/
- PyTorch Determinism: https://pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html
- MLflow Tracking URIs: https://mlflow.org/docs/latest/tracking.html
- SentencePiece: https://github.com/google/sentencepiece
- psutil: https://psutil.readthedocs.io/
- nox: https://nox.thea.codes/
- pytest-cov: https://pytest-cov.readthedocs.io/
- pydocstyle: http://www.pydocstyle.org/
- detect-secrets: https://github.com/Yelp/detect-secrets
- Bandit: https://bandit.readthedocs.io/
- Safety: https://docs.pyup.io/docs/safety/

