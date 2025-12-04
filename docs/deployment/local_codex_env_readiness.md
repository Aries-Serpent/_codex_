# Local Codex Env Readiness Guide

This document describes how to use the **Codex Env** tooling to prepare and
exercise a local `_codex_` environment.

It builds on the following components:

- Unified CLI: `python -m codex_ml.cli.codex_env`
- Task sequence: `codex_task_sequence.yaml`
- ML Test Score runner: `tools/codex_mltest_runner.py`
- Reproducibility tools: `tools/codex_env_snapshot.py`, `tools/codex_reproducibility_bundle.py`
- Security & safety tools: `tools/codex_dependency_audit.py`, `tools/codex_secret_scan_stub.py`
- Minimal train/eval CLIs: `python -m codex_ml.cli.train_minimal`, `python -m codex_ml.cli.eval_minimal`

## 1. Quickstart: Codex Env CLI

```bash
python -m codex_ml.cli.codex_env health
python -m codex_ml.cli.codex_env task-sequence
python -m codex_ml.cli.codex_env mltests -c infrastructure
python -m codex_ml.cli.codex_env bundle
```

Wrapper equivalent (after `chmod +x run_codex_env.sh`):

```bash
./run_codex_env.sh health
./run_codex_env.sh task-sequence
./run_codex_env.sh mltests -c infrastructure
./run_codex_env.sh bundle
```

## 2. Local Docker Env (Optional)

Build and run:

```bash
docker build -f Dockerfile.local-codex-env -t codex-local-env .
docker run --rm -it -v "$(pwd)":/workspace -w /workspace codex-local-env /bin/bash
```

Inside the container you can run `pytest tests -q` or `python -m codex_ml.cli.codex_env health`.

## 3. Integration with Existing Checklists

- Reproducibility: `docs/reproducibility/reproducibility_checklist.md`
- Security & Safety Baseline: `docs/security/codex_security_safety_baseline.md`
- ML Test Score Mapping: `docs/tests/ml_test_score_mapping.md`

## 4. Minimal Train/Eval in the Codex Env

```bash
python -m codex_ml.cli.train_minimal --config conf/minimal_train.yaml --seed 123 --runs-dir runs
python -m codex_ml.cli.eval_minimal --config conf/minimal_eval.yaml --seed 123 --runs-dir runs --checkpoint runs/train
```

Run directories and manifests are created under `runs/train/...` and `runs/eval/...` and are indexed by `tools/codex_experiment_index.py`.
