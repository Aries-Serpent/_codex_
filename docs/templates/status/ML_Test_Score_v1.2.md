# Guide: ML Test Score Framework (v1.2)
> Generated: 2024-11-02 15:08:30 UTC | Author: mbaetiong  
🧠 Roles: [Primary: ML Test Architect], [Secondary: QA Reviewer] ⚡ Energy: 5

Purpose
- Operationalize the "ml_test_score" section in the v1.2 status schema with concrete definitions, targets, and evidence paths.

Categories and Targets
| Category | Sub-Area | Definition | Target (v1) | Evidence Examples |
|---|---|---|---|---|
| Data Tests | feature_expectations | Column presence, types, ranges | >= 5 checks | tests/data/test_schema.py |
| Data Tests | schema_validation | Configs and run outputs validate against schemas | 100% PASS | tools/schema_validate.py runs |
| Data Tests | distribution_checks | Train/val drift, outliers | At least 1 drift check | tests/data/test_drift.py |
| Model Tests | unit_tests | Layer init, forward pass, shapes | Critical paths covered | tests/model/test_forward.py |
| Model Tests | integration_tests | End-to-end mini-train over toy data | 1 happy-path test | tests/integration/test_training_loop.py |
| Model Tests | invariance_tests | Invariance to permutations/augmentations | 1 invariance | tests/model/test_invariance.py |
| Infra Tests | reproducibility | Seeds, RNG in checkpoints, deterministic flags | PASS or WARN | tests/repro/test_determinism.py |
| Infra Tests | training_pipeline | CLI/entrypoints wired, configs validate | 1 minimal run | tests/integration/test_cli_train.py |
| Infra Tests | serving_pipeline | Inference CLI/REST sample | 1 minimal run | tests/integration/test_cli_infer.py |
| Monitoring | model_staleness | Alerts for aged runs | Boolean | MLflow/metadata snapshot |
| Monitoring | dependency_changes | Track deps drift | Boolean | requirements lock audit |
| Monitoring | data_invariants | Min/max checks over incoming data | Boolean | tests/data/test_invariants.py |

Scoring Suggestions
- Start with boolean coverage (present/absent) and count of checks per sub-area.
- Upgrade to a 0–3 ordinal score per sub-area in later iterations.

Status Report Mapping
- Populate counts/booleans into "ml_test_score" object.
- Link tests in snapshot.findings evidence where gaps are discovered.

Next Steps
- Add minimal placeholder tests where gaps exist; mark as xfail if not yet wired.
