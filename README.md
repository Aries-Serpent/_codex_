# codex-universal

`codex-universal` is a reference implementation of the base Docker image available in OpenAI Codex.

This repository is intended to help developers customize environments in Codex by providing a similar image that can be pulled and run locally. This is not an identical environment but should help for debugging and development.

* [Quickstart: tokenizer → training → evaluation](docs/quickstart.md)
* [Architecture overview diagram](docs/diagrams/architecture.svg)
* [Registry & plugin guide](docs/dev/plugins.md)

> **Policy:** No GitHub-hosted Actions. Run `make codex-gates` locally or on a self-hosted runner (ephemeral runners recommended).

For more details on environment setup, see OpenAI Codex.

For environment variables, logging roles, testing expectations, and tool usage, see [docs/guides/AGENTS.md](docs/guides/AGENTS.md).

### Quick setup for tools & tests

```bash
# Base dev tools
pip install -U pre-commit nox pytest

# Optional (enables coverage)
pip install -U pytest-cov

# Optional ML deps (CPU-only wheels shown; pick the right index for your platform)
pip install -U torch transformers datasets  \
  --index-url https://download.pytorch.org/whl/cpu

# Optional logging/telemetry
pip install -U mlflow prometheus-client click

# Run the basics
pre-commit run --all-files          # if pre-commit is installed
nox -s tests                        # or: pytest -m "not slow"
```

| Symptom                                     | Fix                                                                        |
| ------------------------------------------- | -------------------------------------------------------------------------- |
| `command not found: pre-commit`             | `pip install pre-commit`                                                   |
| `command not found: nox`                    | `pip install nox`                                                          |
| `pytest: unrecognized arguments: --cov=...` | `pip install pytest-cov` **or** run `pytest` without `--cov`               |
| `ModuleNotFoundError: torch`                | `pip install torch [right wheel index]` or rely on `importorskip` in tests |

## Local CI (no GitHub-hosted Actions)

Run the gates locally or on a self-hosted runner.

```bash
# Standard path (coverage gate enforced at 70%)
nox -s tests
```

# Fast paths vs isolation
We support fast developer loops while keeping a hermetic fallback:

**Fast paths**
- `nox -r` — reuse venvs between runs (no reinstall). :contentReference[oaicite:7]{index=7}
- `nox --no-venv` — run sessions in the current interpreter (no venv creation). Great for quick checks. :contentReference[oaicite:8]{index=8}
- `uv` inside sessions — ultra-fast installs (`uv pip install ...`). If `uv` isn’t found, we fall back to `pip`. :contentReference[oaicite:9]{index=9}

**Hermetic fallback**
- Build an offline **wheelhouse** once, then install from it with `--no-index --find-links`. See `tools/make_wheelhouse.sh` and `tools/bootstrap_wheelhouse.sh`. :contentReference[oaicite:10]{index=10}

**Trade-offs**
- Fastest: `nox --no-venv` + `uv` (uses your current env; not isolated). :contentReference[oaicite:11]{index=11}
- Balanced: `nox -r` (reused venvs, isolated enough, still quick). :contentReference[oaicite:12]{index=12}
- Most isolated/offline: install from wheelhouse (`pip install --no-index --find-links`), consistent and network-independent. :contentReference[oaicite:13]{index=13}

> Note: We intentionally keep **coverage fail-under at 70%** until we confirm 80%+ is consistently attainable.

### Deterministic installs preference order (Codex policy)

1. **Project lock (`uv.lock`) present**
   Use: `uv sync --frozen`
   - Requires: `pyproject.toml` + committed `uv.lock`
   - Guarantees: exact, reproducible environments without updating the lock.

2. **Requirements lock/pins present**
   Use: `uv pip sync requirements*.txt` (idempotent)
   - For repos without `pyproject.toml`, prefer compiled requirement files (e.g., `requirements.txt`, `requirements.lock`).

3. **Ad-hoc**
   Use: `pip install -r ...` (or `uv pip install -r ...`) with `PIP_CACHE_DIR` and, when offline, `--no-index --find-links ./wheelhouse`.

**Regenerating locks (standardized)**
Use `tools/uv_lock_refresh.sh`:
```bash
# Project mode (pyproject.toml present): refresh uv.lock
tools/uv_lock_refresh.sh

# Requirements mode (no pyproject.toml): compile pins
tools/uv_lock_refresh.sh -i requirements.in -o requirements.txt
```

> Codex rule of thumb: prefer `uv sync --frozen` if `uv.lock` exists; otherwise, prefer `uv pip sync <lockfile>`; otherwise, install with cache/wheelhouse.

For a high-level overview of Codex's training stages, symbolic objective, and data flow, see [documentation/codex_symbolic_training_summary.md](documentation/codex_symbolic_training_summary.md).

For guidance on offline experiment tracking with TensorBoard, Weights & Biases, and MLflow, see [docs/ops/experiment_tracking.md](docs/ops/experiment_tracking.md).

## Installation

Create and activate a virtual environment, then install this repository and verify the core modules:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .

python -c "import codex; import codex.logging"
```

This project requires `transformers>=4.3.3` for HuggingFace Trainer support;
later versions such as `4.38` or `4.55` are also compatible.

After installation, the main CLI can be invoked as:

```bash
codex-ml-cli --help
```

### Training CLI

- Default functional training config lives at `configs/training/base.yaml` with reproducible hyper-parameters.
- Run `codex train --config configs/training/base.yaml --resume` to launch the functional trainer and automatically resume from the latest checkpoint.
- Override the training seed with `--seed <value>`; overrides are applied before dispatching to the trainer.

### Maintenance tasks

Utility tasks are exposed via `python -m codex.cli`:

```bash
python -m codex.cli tasks            # list allowed tasks
python -m codex.cli run ingest       # ingest example data
python -m codex.cli run ci           # run nox -s tests
```

## Quick Start

**Notebook (CPU, offline)**

```bash
python scripts/make_quickstart_notebook.py
jupyter notebook notebooks/quick_start.ipynb
```

**Headless (CLI only)**

```bash
python -m training.engine_hf_trainer --max-steps 20 --tensorboard true
tensorboard --logdir runs/tb
```

### Train and evaluate

Run the demo training loop:


- New training CLI: `python -m codex_ml.cli.codex_cli train --config configs/training/base.yaml --resume`

```bash
python -m codex_ml.cli.codex_cli train --config configs/training/base.yaml
```

Enable MLflow logging and telemetry:

```bash
python -m codex_ml.cli.codex_cli train --config configs/training/base.yaml \
  --mlflow.enable --mlflow.uri file:./mlruns --mlflow.experiment codex \
  --telemetry.enable --telemetry.port 8001
```

Metrics are exposed at `http://localhost:8001/metrics` when telemetry is enabled.

Evaluate datasets with registered metrics:

```bash
python -m codex_ml.cli evaluate --datasets toy --metrics accuracy
```

### Dataset registry

Datasets can be retrieved via a simple registry:

```python
from codex_ml.data.registry import get_dataset

texts = get_dataset("lines", path="data/sample.txt")
```

If the `datasets` library is available, HuggingFace datasets can be streamed:

```python
from codex_ml.data import hf_datasets  # registers the loader
stream = get_dataset("hf", name="wikitext", split="train", fallback_path="data/sample.txt")
```

## Architecture Overview

See [docs/architecture.md](docs/architecture.md) for a high-level module and data-flow diagram.

## Examples

- Train with HF Trainer on a tiny corpus

  ```bash
  python -m training.engine_hf_trainer --max-steps 20 --tensorboard true
  ```
  Default hyperparameters reside in `configs/config.yaml` and are used when available.

- Evaluate a checkpoint with the evaluation runner

  ```bash
  python -m codex_ml.eval.eval_runner run --datasets toy_copy_task --metrics ppl --output-dir runs/eval --max-samples 1
  ```

- Train a tokenizer offline

  ```bash
  python -m codex_ml.tokenization.train_tokenizer --input-file corpus.txt --output-dir runs/tokenizer --vocab-size 8000
  ```

- View TensorBoard logs

  ```bash
  tensorboard --logdir runs/tb
  ```

## Evaluation & Metrics

`codex_ml.eval.eval_runner` offers a tiny evaluation loop and a registry of
deterministic metrics.  It can consume built-in toy datasets or custom
NDJSON files and emits both NDJSON and CSV summaries.

```bash
python -m codex_ml.eval.eval_runner run --datasets toy_copy_task --metrics exact_match
```

Metrics are written under `runs/eval/` by default (`metrics.ndjson` and
`metrics.csv`).

### Tokenization

We use HF fast tokenizers with explicit `padding`/`truncation`/`max_length` to ensure batchable tensors.
Example:

```python
from interfaces.tokenizer import HFTokenizer
tk = HFTokenizer("distilbert-base-uncased", padding="max_length", truncation=True, max_length=128)
batch = tk.encode(["hello", "world"])
```

Lower-level utilities like `HFTokenizerAdapter` also expose `pad_to_max` and
`max_length` parameters for deterministic sequence lengths in downstream tools.

A lightweight `SentencePieceAdapter` is available for custom vocabularies and
supports explicit padding and truncation controls similar to Hugging Face
tokenizers.

## Fallback Modes & Feature Flags

The analysis utilities provide tiered parsing with safe fallbacks and optional features:

- Tiered parsing: [`parsers.py`](src/codex_ml/analysis/parsers.py)
- Metrics helpers: [`metrics.py`](src/codex_ml/analysis/metrics.py)
- Optional external search via `--external-search` (disabled by default).

## Continuous Integration

Run `make codex-gates` to execute pre-commit and tests locally or on a self-hosted runner. No GitHub-hosted minutes and no workflow YAML required.

If you prefer to call the tools directly:

```bash
pre-commit run --all-files
pytest -q
```

Optional MLflow tracking:

```bash
export MLFLOW_TRACKING_URI="$PWD/mlruns"
```

GitHub Actions workflows exist under `.github/workflows/` but remain disabled; all CI runs should be executed locally or on self-hosted runners.

## Quality Gates (local/Codex only)

- Run all local gates: `export CODEX_ENV=1 && bash tools/run_quality_gates.sh`
- Security sweep: `make sec-scan`
- Deterministic locks: `make lock-refresh` (uses Astral **uv**)

To skip formatting hooks (Black/Ruff-format) during gates:
`SKIP_FORMAT=1 CODEX_ENV=1 bash tools/run_quality_gates.sh`

> Note: no GitHub Actions are enabled by this project policy; all checks run locally or on the Codex self-hosted runner.

## Makefile

Common tasks are provided via a simple `Makefile`:

```bash
make format  # pre-commit run --all-files
make lint    # ruff src tests
make test    # nox -s tests
make build   # python -m build
make type    # mypy src
```

## Testing

### Quick checks

- Run pre-commit on config changes:

  ```bash
  pre-commit run --files .pre-commit-config.yaml
  ```

- Run pytest with coverage:

  ```bash
  nox -s ci_local
  ```

> **Note:** Automated GitHub Actions remain disabled by default; `codex-self-manage` runs only when manually triggered or when a pull request carries the `codex-ci` label.

## Security Scanning

This project uses **Bandit** for static security analysis and **detect-secrets** for secret scanning.

- **Bandit**: runs automatically via pre-commit to catch common security issues in code.
- **Detect-Secrets**: uses a baseline file (`.secrets.baseline`) to track allowed secret patterns. If you add or modify credentials or keys in the code, update the baseline by running:

```
detect-secrets scan > .secrets.baseline
```

Ensure no real secrets are committed; the baseline helps filter out false positives.

### Semgrep Security Rules

Run Semgrep locally to catch insecure patterns:

```bash
semgrep --config semgrep_rules/ --error
```

### SBOM and Dependency Pins

Generate a CycloneDX SBOM and verify pinned dependencies:

```bash
make sbom
python tools/verify_pins.py
```

### Offline Tracking (local-only)

```bash
# W&B offline
export WANDB_MODE=offline
```

```python
from src.utils.trackers import init_wandb_offline, init_mlflow_local
init_wandb_offline("codex")
init_mlflow_local()
```

## Logging Locations

- SQLite DB: `.codex/session_logs.db`
- NDJSON sessions: `.codex/sessions/<SESSION_ID>.ndjson`

See [documentation/session_log_rotation.md](documentation/session_log_rotation.md) for rotation and archival guidelines.

## Usage

The Docker image is available at:

```
docker pull ghcr.io/openai/codex-universal:latest
```

The below script shows how can you approximate the `setup` environment in Codex:

```sh
# See below for environment variable options.
# This script mounts the current directory similar to how it would get cloned in.
docker run --rm -it \
    -e CODEX_ENV_PYTHON_VERSION=3.12 \
    -e CODEX_ENV_NODE_VERSION=20 \
    -e CODEX_ENV_RUST_VERSION=1.87.0 \
    -e CODEX_ENV_GO_VERSION=1.23.8 \
    -e CODEX_ENV_SWIFT_VERSION=6.1 \
    -v $(pwd):/workspace/$(basename $(pwd)) -w /workspace/$(basename $(pwd)) \
    ghcr.io/openai/codex-universal:latest
```

`codex-universal` includes setup scripts that look for `CODEX_ENV_*` environment variables and configures the language version accordingly.

### Configuring language runtimes

The following environment variables can be set to configure runtime installation. Note that a limited subset of versions are supported (indicated in the table below):

| Environment variable       | Description                | Supported versions                               | Additional packages                                                  |
| -------------------------- | -------------------------- | ------------------------------------------------ | -------------------------------------------------------------------- |
| `CODEX_ENV_PYTHON_VERSION` | Python version to install  | `3.10`, `3.11.12`, `3.12`, `3.13`                | `pyenv`, `poetry`, `uv`, `ruff`, `black`, `mypy`, `pyright`, `isort` |
| `CODEX_ENV_NODE_VERSION`   | Node.js version to install | `18`, `20`, `22`                                 | `corepack`, `yarn`, `pnpm`, `npm`                                    |
| `CODEX_ENV_RUST_VERSION`   | Rust version to install    | `1.83.0`, `1.84.1`, `1.85.1`, `1.86.0`, `1.87.0` |                                                                      |
| `CODEX_ENV_GO_VERSION`     | Go version to install      | `1.22.12`, `1.23.8`, `1.24.3`                    |                                                                      |
| `CODEX_ENV_SWIFT_VERSION`  | Swift version to install   | `5.10`, `6.1`                                    |                                                                      |

### Custom user setup

If a shell script exists at `.codex/user_setup.sh`, it runs once after the environment is initialized. Override the location with `CODEX_USER_SETUP_PATH`. The sentinel `.codex/.user_setup.done` prevents reruns unless `CODEX_USER_SETUP_FORCE=1` is set. Output is written to `.codex/setup_logs/<timestamp>.log`.

| Environment variable     | Description                                                        |
| ------------------------ | ------------------------------------------------------------------ |
| `CODEX_USER_SETUP_PATH`  | Path to the user setup script. Defaults to `.codex/user_setup.sh`. |
| `CODEX_USER_SETUP_FORCE` | Run the user setup even if `.codex/.user_setup.done` exists.       |

## Deployment

Build a reproducible wheel and run a minimal smoke test entirely offline:

```bash
bash scripts/build_wheel.sh --local
bash scripts/smoke_after_build.sh
```

Generate text from a checkpoint on the command line:

```bash
codex-infer --checkpoint sshleifer/tiny-gpt2 --prompt "hello codex"
```

`codex-infer` writes results under `./artifacts/infer/` alongside a JSON manifest.

### Docker Compose

Spin up a containerised CPU inference service with volume mounts for data and artifacts:

```bash
docker compose up codex-cpu
```

To enable GPU inference, uncomment the `codex-gpu` service in `docker-compose.yml` and ensure
`nvidia-smi` works on the host.

The compose file expects an `.env` with:

```
MODEL_NAME=sshleifer/tiny-gpt2
TOKENIZER_NAME=sshleifer/tiny-gpt2
MAX_NEW_TOKENS=20
```

Volumes map `./data` to `/data` and `./artifacts` to `/artifacts` inside the container.

## Training & Monitoring

The repository includes lightweight helpers for experimenting with training loops.

- `functional_training.py` writes per-epoch metrics to `metrics.json` and, when
  invoked with `--tensorboard`, logs scalars under `CHECKPOINT_DIR/runs/` for
  visualization with TensorBoard.
- `deploy/deploy_codex_pipeline.py` accepts `--enable-wandb` and MLflow flags
  (`--mlflow-enable`, `--mlflow-tracking-uri`, `--mlflow-experiment`) to log
  parameters, metrics, and artifacts.
- The HuggingFace Trainer wrapper supports validation data and respects
  `evaluation_strategy="epoch"` when provided via `--trainer-config`.
  Early stopping and named learning-rate schedulers can be enabled via
  `build_trainer` parameters (e.g. `scheduler_name="cosine"`,
  `early_stop_patience=2`).

### GPU deployment

`docker-compose.yml` declares optional NVIDIA GPU reservations, and
`scripts/deploy/run.sh` automatically adds `--gpus all` when `nvidia-smi` is
available on the host.

## What's included

In addition to the packages specified in the table above, the following packages are also installed:

- `ruby`: 3.2.3
- `bun`: 1.2.10
- `java`: 21
- `bazelisk` / `bazel`

See [Dockerfile](Dockerfile) for the full details of installed packages.

## Development

Set up the git hooks before committing:

```bash
pip install pre-commit
pre-commit install
```

Pull requests are validated with `pre-commit run --all-files`; submissions failing these
hooks will be rejected. Before committing, run `pre-commit run --all-files` locally to
catch formatting or lint issues early.

### Maintenance workflow

Run a sequence of maintenance utilities and tests:

```bash
python tools/codex_maintenance.py
```

The script executes `codex_repo_scout`, `codex_precommit_bootstrap`, `codex_logging_workflow`, `codex_session_logging_workflow`, and `pytest`, then prints a summary of each step's success or failure.

### Sample DB initialization

Create or reset a minimal `session_events` table in the local development database and seed example rows:

```bash
python scripts/init_sample_db.py --reset --seed
# or specify a custom path:
python scripts/init_sample_db.py --db-path ./.codex/session_logs.db --reset --seed
```

By default, the script uses `./.codex/session_logs.db` to align with existing logging in this repository.

## Session Logging (SQLite)

This repository provides a CLI viewer for session-scoped logs stored in SQLite.

### Usage

```bash
python -m codex.logging.viewer --session-id <ID> [--db path/to.db] [--format json|text] \
  [--level INFO --contains token --since 2025-01-01 --until 2025-12-31] [--limit 200] [--table logs]
```

- **--session-id** (required): Which session to view.
- **--db**: Path to the SQLite DB. If omitted, common names like `data/logs.sqlite` or `logs.db` are autodetected.
- **--format**: Output `json` or `text` (default).
- **--level**: Filter by level (repeatable), e.g., `--level INFO --level ERROR`.
- **--contains**: Case-insensitive substring match over the message.
- **--since / --until**: ISO timestamps or dates. Results are chronological.
- **--limit**: Cap the number of returned rows.
- **--table**: Explicit table name. If omitted, the CLI infers a suitable table/columns. Table names must match `[A-Za-z0-9_]+`.

> **Note:** Inference expects columns like `session_id`, `ts`/`timestamp`, and `message`. If levels are present, common names (`level`, `severity`) are detected.

#### SQLite Connection Pooling

Set `CODEX_SQLITE_POOL=1` to prefer a pooled/shared SQLite connection in CLI tools
(e.g., viewer/query/export). This reduces connection churn and can improve throughput
on repeated commands. Default is non-pooled behavior.

Examples:
export CODEX_SQLITE_POOL=1
python -m codex.logging.viewer --session-id S123 --format text
python -m codex.logging.export S123 --format json

# Registering a toy tokenizer
```python
from codex_ml.plugins import tokenizers
from codex_ml.interfaces.tokenizer import TokenizerAdapter, get_tokenizer

@tokenizers.register("toy")
class ToyTokenizer(TokenizerAdapter):
    __codex_ext_api__ = "v1"

    def encode(self, text: str, *, add_special_tokens: bool = True):
        return [1]

    def decode(self, ids, *, skip_special_tokens: bool = True):
        return "toy"

    @property
    def vocab_size(self) -> int:
        return 0

tk = get_tokenizer("toy")
```

## Logging: Querying transcripts

This repository includes a CLI to query a SQLite database and render chat transcripts, auto-detecting tables and columns.

### Installation / Invocation

```bash
python -m codex.logging.query_logs --help
# Specify DB path explicitly or via env:
#   export CODEX_DB_PATH=.codex/session_logs.db
#   python -m codex.logging.query_logs --session-id S123 --role user --after 2025-01-01 --format json
```

### Filters

- `--session-id`: exact match on session identifier
- `--role`: one of your stored roles (e.g., `user`, `assistant`, `system`, `tool`)
- `--after`, `--before`: ISO-8601 or `YYYY-MM-DD` boundaries
- `--format {text,json}`: choose plain text or JSON (default `text`)
- `--limit/--offset`, `--order {asc,desc}`

> The tool auto-adapts to schemas (e.g., it tolerates `created_at` vs `timestamp`, `content` vs `message`, etc.). If the table or required columns are missing, it will explain what’s expected.

## Logging: Exporting session events

Dump all events for a session as JSON or plain text.

```bash
python -m codex.logging.export SESSION_ID --format json
# plain text
python -m codex.logging.export SESSION_ID --format text
# specify a custom database
python -m codex.logging.export SESSION_ID --db /path/to/db.sqlite
```

The tool reads from `src.codex.logging.config.DEFAULT_LOG_DB` (defaults to
`.codex/session_logs.db`). Override with the
`CODEX_LOG_DB_PATH` environment variable.

## Session Logging (Opt-in)

This repository includes an optional session logging module generated by the workflow.

**Usage (example):**

```python
from src.codex.logging.session_logger import log_event, get_session_id

session_id = get_session_id()

def handle_user_message(prompt: str) -> str:
    log_event(session_id, "user", prompt)
    reply = generate_reply(prompt)  # your existing logic
    log_event(session_id, "assistant", reply)
    return reply
```

**Storage:** SQLite at `src.codex.logging.config.DEFAULT_LOG_DB`.
**Note:** This change is additive and does not activate any GitHub Actions.

## Session Hooks (NDJSON)

Lightweight helpers capture shell and Python entry sessions as NDJSON lines:

- `scripts/session_hooks.sh` – shell functions `codex_session_start` / `codex_session_end`
  backed by Python logging. Each Python invocation is checked and failures are
  reported to `stderr`.
- `scripts/session_logging.sh` – backwards-compatible wrapper sourcing
  `session_hooks.sh`.
- `src/codex/logging/session_hooks.py` – Python context manager emitting start/end events

Logs are written under `.codex/sessions/<SESSION_ID>.ndjson` and exercised via `tests/test_session_hooks.py`.

<!-- CODEX:LOGGING:START -->

## End-to-End Logging

This repository supports a simple, environment-driven logging flow suitable for scripting and CLI tasks. See [documentation/end_to_end_logging.md](documentation/end_to_end_logging.md) for a detailed walkthrough.

### Environment Variables

- `CODEX_SESSION_ID` — A unique ID (GUID/UUID) that ties **start**, **message**, and **end** events together across commands.
- `CODEX_LOG_DB_PATH` — Filesystem path to a SQLite database (or NDJSON file) used by tools to persist log events.

#### Set in Bash/Zsh

```bash
export CODEX_SESSION_ID="$(uuidgen || python -c 'import uuid;print(uuid.uuid4())')"
export CODEX_LOG_DB_PATH="${PWD}/.codex/session_logs.db"
```

#### Set in PowerShell

```powershell
$env:CODEX_SESSION_ID = [guid]::NewGuid().ToString()
$env:CODEX_LOG_DB_PATH = (Join-Path (Get-Location) ".codex/session_logs.db")
```

> **Note:** Keep logs within the repo (e.g., `./.codex/`) for portability and review.

### Quick Start (Python)

```python
import os, sqlite3, time, pathlib

db = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))
db.parent.mkdir(parents=True, exist_ok=True)
sid = os.getenv("CODEX_SESSION_ID", "dev-session")

con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS logs(ts REAL, session TEXT, kind TEXT, message TEXT)")
now = time.time()
cur.executemany("INSERT INTO logs(ts, session, kind, message) VALUES(?,?,?,?)", [
    (now, sid, "start", "session begin"),
    (now+0.1, sid, "message", "hello world"),
    (now+0.2, sid, "end", "session end"),
])
con.commit(); con.close()
print(f"Wrote 3 log rows to {db}")
```

### Log Viewer CLI

Use `codex.logging.query_logs` to inspect stored events:

```bash
python -m codex.logging.query_logs --db "$CODEX_LOG_DB_PATH" --session-id "$CODEX_SESSION_ID" --tail 20
```

<!-- CODEX:LOGGING:END -->

## Session Logging (Context Manager)

You can log session lifecycle and chat events via a small context manager:

```python
from src.codex.logging.session_logger import SessionLogger

with SessionLogger(session_id="demo") as sl:
    sl.log("user", "hi")
    sl.log("assistant", "hello")
```

This writes to `src.codex.logging.config.DEFAULT_LOG_DB` by default; override with
`CODEX_LOG_DB_PATH`.

## Session Query (Experimental)

Query session events from the local SQLite database.

```bash
# by session id (ascending by default)
python -m src.codex.logging.session_query --session-id 12345 --db .codex/session_logs.db

# last N events (most recent first)
python -m src.codex.logging.session_query --last 50 --db .codex/session_logs.db

# descending order for session view (optional)
python -m src.codex.logging.session_query --session-id 12345 --db .codex/session_logs.db --desc
```

The tool auto-detects timestamp, session, role, and message columns and will look for
both `.db` and `.sqlite` variants of the database path. Override the path via `--db` or
`CODEX_DB_PATH`.

## Pre-commit (Ruff + Black)

This repository uses pre-commit to run code-quality hooks locally.

**Install once**

```bash
pipx install pre-commit || pip install --user pre-commit
pre-commit install
pre-commit autoupdate
```

**Run on all files**

```bash
pre-commit run --all-files
```

**Run on specific files**

```bash
pre-commit run --files path/to/file1.py path/to/file2.py
```

**Optional — run Black manually (kept as manual stage)**

```bash
pre-commit run --hook-stage manual black --all-files
```

## Timestamp Parsing

This project supports ISO-8601 timestamps including `Z` (UTC), explicit offsets (e.g., `+05:30`), and naive timestamps (no timezone). See `parse_when` and the regression tests in `tests/test_parse_when.py`.

## Optional SQLite Connection Pool (Per-Session)

Set `CODEX_SQLITE_POOL=1` to enable an import-time monkey patch that reuses
a single SQLite connection per `(database, pid, tid, CODEX_SESSION_ID)`.
Optionally set `CODEX_SESSION_ID` to group work by a logical session.
No code changes are required beyond importing `sqlite3` normally.

- Disable: `CODEX_SQLITE_POOL=0` (default)
- DB path for adapters: `CODEX_SQLITE_DB` (defaults to `codex_data.sqlite3`)
- Connections are cached **per thread** and are not safe to share between
  threads or processes. Each thread gets its own connection, and highly
  concurrent or long-running applications should consider a more robust
  database.
- Calling `close()` on a pooled connection leaves it in a closed state within
  the pool. Avoid context managers like `with sqlite3.connect(...)` when pooling
  is enabled.

## Immutable SQLite snapshots

The script `tools/build_sqlite_snapshot.py` creates a small snapshot database under `.artifacts/snippets.db`. Open the snapshot in read-only mode using SQLite's immutable flag:

```python
import sqlite3
con = sqlite3.connect('file:snippets.db?immutable=1', uri=True)
```

This prevents SQLite from creating journal files or writing to the database file.

> **Safety note:** Avoid using live SQLite databases on network shares. SQLite's
> locking model does not work reliably over network filesystems and can result in
> database corruption. Keep working copies on local disks or use read-only
> snapshots.

View the snapshot in your browser with Datasette Lite.

## Ingestion

`ingestion.ingest` and its `Ingestor.ingest` shim now accept an optional
`encoding: str = "utf-8"` parameter. Setting `encoding="auto"` enables
best-effort autodetection; otherwise, specify an explicit codec.

## Codex Logs

- `.codex/change_log.md`: human-readable changes
- `.codex/errors.ndjson`: NDJSON (one JSON object per line)
- `.codex/results.md`: summaries/results

## codex_workflow entry point

Run the consolidated workflow with:

```bash
python -m codex_workflow
```

`codex_workflow.py` at the repository root serves as the authoritative module.
Legacy copies under `tools/` or other directories have been removed. If new
variants appear, execute `python tools/workflow_merge.py` to migrate or delete
them.

## Ruff Usage

- Lint: `ruff .`
- Auto-fix target: `ruff --fix codex_workflow.py`
- Converge until clean: re-run `ruff` until exit code 0

> **DO NOT ACTIVATE ANY GitHub Actions files. ALL GitHub Action.**

## Hydra Configuration & CLI

This project uses Hydra for configuration.  The root configuration lives at
`configs/config.yaml` and composes several groups (`model`, `data`, `tokenizer`,
`logging`, `training`, `tracking`).  Each group has a `base.yaml` defining
defaults that can be overridden on the command line.

### Run (dry)

```bash
python -m codex_ml.cli.main +dry_run=true
```

### Override examples

```bash
python -m codex_ml.cli.main train.epochs=2 tokenizer.name=gpt2 +dry_run=true

# Use Hugging Face Trainer via CLI
python -m codex.cli train --engine hf
```

Effective composed config is saved to `.codex/hydra_last/config.yaml`.

### Multi-GPU Training

`training/engine_hf_trainer.py` initialises `torch.distributed` when multiple CUDA
devices are available. Ensure that the appropriate NVIDIA drivers and the NCCL
backend are installed. Distributed support can be disabled by invoking
`run_hf_trainer(..., distributed=False)`.

### Resuming & LoRA

`run_hf_trainer` accepts `resume_from="/path/to/checkpoint"` to continue
training from a saved checkpoint. When the `peft` package is installed, LoRA
adapters are applied via `apply_lora` with the requested precision and device
placement.

<!-- BEGIN: CODEX_README_UPDATE -->

Local-only validations & explicit flags for monitoring/tracking.
**Do not** enable remote CI triggers; run Codex scripts directly.

<!-- BEGIN: CODEX_SMOKE_README -->

## Smoke Tests & Offline Logging

This repository includes CPU-friendly smoke tests for HF Trainer and end-to-end logging flags. All logging integrations are offline-safe for local validation.

## Offline CI & Local Parity

This repository enforces **offline-only** validation in the Codex environment.

- No remote CI/CD or network I/O during tests.
- GitHub Actions are **manual-only** and must not run automatically.
- Use `scripts/codex_local_gates.sh` for local gates (lint, tests, coverage).

## Quickstart

```bash
pip install -e .[dev]
pre-commit install
detect-secrets scan > .secrets.baseline && detect-secrets audit .secrets.baseline
nox -s lint tests
codex-train
# enable local MLflow
export MLFLOW_TRACKING_URI="file:./mlruns"
```

## Data Handling

Utilities in `codex_ml.data_utils` help manage large text corpora deterministically and redact basic PII/secret patterns before splitting.

```python
from codex_ml.data_utils import split_dataset, stream_texts

train, val = split_dataset(lines, seed=42, cache_path="split.json")
for chunk in stream_texts("corpus.txt", chunk_size=1024):
    ...
```

## Tokenizer workflow

Train and inspect tokenizers deterministically with the provided utilities.

```bash
python -m tokenization.train_tokenizer corpus_glob="data/*.txt" out_dir=artifacts/tokenizers name=demo
codex-tokenizer inspect artifacts/tokenizers/demo
codex-tokenizer export artifacts/tokenizers/demo exported_tok
```

Use `HFTokenizer` to load the exported artifacts:

```python
from codex_ml.interfaces.tokenizer import HFTokenizer
tk = HFTokenizer(name_or_path=None, artifacts_dir="exported_tok")
ids = tk.encode("hello world")
```

⚠️ Changing seeds or normalization rules alters the vocabulary and encoded ids.

## Single-Job (Ephemeral) Self-Hosted Runners

See `docs/ephemeral-runners.md` for the toolkit, label policy, pre-flight, and CLI.
Tools operate externally and do not modify GitHub Actions workflows.

## Testing & Coverage (Local-Only)

Run the test suite with coverage locally:

```
pytest -q --cov=src/codex_ml --cov-report=term-missing:skip-covered --cov-report=xml
```

Optional components:

- Install `sentencepiece` for tokenization features: `pip install sentencepiece`.
- The `train_loop` writes metrics under `artifacts/metrics`.
- MLflow utilities are offline by default; set `MLFLOW_TRACKING_URI` to enable tracking.

No GitHub Actions are enabled; all checks execute in this local environment.

### Decoder-Only Minimal Model

The `codex_ml.models.decoder_only` module provides a tiny GPT-style network
implemented purely in PyTorch.  It supports rotary embeddings, causal
attention, optional LoRA adapters and a small generation helper.  Models can
also be discovered via `codex_ml.models.registry.get_model`; the MiniLM config
is registered as `"minilm"`.  The model is intended for tests and local smoke
experiments rather than production use.

Example smoke test:

```bash
codex-generate --prompt "hello" --max-new-tokens 5
```

This prints a short string using randomly initialised weights.  The CLI is only
meant for local experimentation.

## New Features

- **Telemetry:** Prometheus metrics via `codex_ml.telemetry` and a metrics server.
- **Multilingual:** mBERT tokenisation and dataset language filtering.
- **Privacy:** Optional differential privacy training through Opacus.
- **Connectors:** Async connector interface with a local filesystem implementation.
- **CLI:** New Click-based commands under `codex_ml.cli.codex_cli`.
