# Contributing

Thank you for improving `codex-universal`.

## Getting Started

This project accepts documentation updates and `.codex` artefacts. Before submitting a pull request, run the standard checks:

```bash
pre-commit run --all-files
mypy .
pytest
```

### Pre-commit quickstart

We use **pre-commit** for fast linting/formatting locally and in CI.

1) Install git hooks and prewarm environments (much faster on first commit):

```bash
pre-commit install --install-hooks
```

2) Run all configured hooks:

```bash
pre-commit run --all-files
```

3) Heavy scanners are configured as **manual-stage** hooks. Run them explicitly when needed or in CI:

```bash
pre-commit run --hook-stage manual --all-files
```

These commands are also available via Make targets:

```bash
make hooks-prewarm
make hooks-manual
```

## Workflow consolidation

`codex_workflow.py` at the repository root is the canonical workflow script. Run
it via `python -m codex_workflow`.

If additional `codex_workflow*.py` files appear elsewhere in the repository,
use `python tools/workflow_merge.py` to merge logic into the authoritative
module and update imports.

If the secret scan (detect-secrets) fails due to a false positive (and no actual secret is present), update the baseline by running:

``` text
$ detect-secrets scan --baseline .secrets.baseline
```
Secret scanning runs as part of ``pre-commit``. To scan specific files prior to
committing, run:

``` text
pre-commit run detect-secrets --files <files>
```
To verify third-party dependency licenses, run:

``` text
python scripts/check_licenses.py
```
Only MIT, Apache-2.0, BSD, and ISC licenses are currently allowed. The script
exits with a non-zero status if disallowed licenses are detected.

## Manual Validation

When changes affect the snapshot database or related tooling, perform manual validation. Follow the [Manual Verification Template](documentation/manual_verification_template.md) and record the steps you completed (A1–A4, B1–B2, or C1) in your pull request description or issue.

## Experiment Documentation

- Record every significant training or evaluation effort under the `experiments/` directory using the template in [docs/experiments.md](docs/experiments.md) before requesting review.
- Capture reproducibility details: run IDs, seeds, CLI/config snapshots, dataset versions, manifests/checksums, and validation notes, plus links to logged artefacts (for example `params.ndjson`, `metrics.ndjson`, dashboards).
- Cross-link experiment notes from related PRs or issues and from the notes back to relevant artefacts so reviewers can trace conclusions to evidence and follow-up actions.

## Scope

See [docs/guides/AGENTS.md](docs/guides/AGENTS.md) for full guidelines.

## Extending Codex ML components

Codex ML exposes registries for tokenizers, models, metrics, data loaders and
trainers via :mod:`codex_ml.registry`.  When contributing a new component or
documenting a third-party plugin:

- Register the implementation using the appropriate ``register_*`` helper so it
  is available to in-process callers.
- If the component ships in an external package, declare an entry point in the
  relevant ``codex_ml.*`` group (for example ``codex_ml.metrics``) and ensure the
  callable returns the fully configured object.
- Add automated coverage that exercises registration and error handling.  See
  ``tests/test_registry.py`` for examples that verify collisions and load
  failures.
- Provide user-facing documentation under ``docs/modules/plugins.md`` describing
  configuration options and any additional dependencies.

## Local quality gates (no GitHub Actions)

- First run may be slow while `pre-commit` installs hook environments; use `--verbose` and `pre-commit clean` if needed.
- Tests with coverage: `pytest --cov=src/codex_ml --cov-fail-under=3.5 --cov-report=term`.
- **Do not** enable any GitHub Actions. All checks run locally.

### Coverage requirements

- Minimum coverage gate: **3.5%** (enforced via `config/pytest.ini`, `config/Makefile`, `noxfile.py`, and `.github/workflows/` pipelines).
- Local commands respecting the gate:
  - `pytest --cov=src/codex_ml --cov-fail-under=3.5`
  - `make -C config test`
  - `nox -s tests`
- Update README badges and contributor docs when the gate changes.

## Optional Dependencies

Core functionality works without optional extras. Install the packages below to enable advanced integrations:

| Package | Purpose | Install | Required For |
|---------|---------|---------|--------------|
| `hydra-core` | Configuration management | `pip install hydra-core` | Config schemas, multi-run experiments |
| `mlflow` | Experiment tracking | `pip install mlflow` | MLflow logging, model registry |
| `wandb` | Experiment tracking | `pip install wandb` | Weights & Biases integration |
| `tensorboard` | Visualization | `pip install tensorboard` | TensorBoard logging |
| `cyclonedx-bom` | SBOM generation | `pip install cyclonedx-bom` | `make -C config sbom` / CI SBOM workflow |

Install every optional dependency with:

```bash
pip install -r requirements-dev.txt
```

Offline/minimal environments can skip these extras. When optional features are invoked without the dependency installed, the CLI raises a descriptive `ImportError` including the `pip install …` command.

### Testing without optional dependencies

```bash
pip uninstall hydra-core mlflow wandb tensorboard -y
python -c "import codex_ml; print('✓ Core imports work without extras')"
pip install -r requirements-dev.txt
```

## Software Bill of Materials (SBOM)

We generate a [CycloneDX](https://cyclonedx.org/) Software Bill of Materials to track dependencies and supply-chain metadata.

### Generate locally

```bash
pip install -r requirements-dev.txt
make -C config sbom
# Output: dist/sbom.json
```

### Continuous integration

The `Generate SBOM` workflow runs on pushes to `main`/`develop`, pull requests targeting `main`, and release publications. It produces:

- `dist/sbom.json` uploaded as a build artifact (retained for 90 days).
- A release asset (`sbom.json`) attached to published releases.

### Working with the SBOM

```bash
# Count dependencies
jq '.components | length' dist/sbom.json

# Inspect a specific package
jq '.components[] | select(.name == "pytest")' dist/sbom.json
```

Use the SBOM to perform license audits, vulnerability scans, and downstream reporting.

## Error capture → commit comment (optional)

Errors are appended to `Codex_Questions.md` with the header:

``` text
Question for ChatGPT @codex {{TIMESTAMP}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```
`tools/install_codex_hooks.py` installs a `prepare-commit-msg` hook that appends trailers
(`Codex-Questions-Count`, `Codex-Report-Path`) using `git interpret-trailers`.

Optionally post the consolidated `codex_commit_comment.txt` as a commit comment:

```bash
export GH_PAT=***  # or GITHUB_TOKEN
export CODEX_POST_COMMIT_COMMENT=1
python tools/codex_run_tasks.py
# or via GH CLI:
tools/post_commit_comment.sh
```
