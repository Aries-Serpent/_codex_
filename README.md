# codex-universal

[![CI](https://github.com/openai/codex-universal/actions/workflows/ci.yml/badge.svg)](https://github.com/openai/codex-universal/actions/workflows/ci.yml)

`codex-universal` is a reference implementation of the base Docker image available in [OpenAI Codex](http://platform.openai.com/docs/codex).

This repository is intended to help developers cutomize environments in Codex, by providing a similar image that can be pulled and run locally. This is not an identical environment but should help for debugging and development.

For more details on environment setup, see [OpenAI Codex](http://platform.openai.com/docs/codex).

For environment variables, logging roles, testing expectations, and tool usage, see [AGENTS.md](AGENTS.md).

## Installation

Create and activate a virtual environment, then install this repository and verify the core modules:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .

python -c "import codex; import codex.logging"
```

## Continuous Integration (local parity)

Run locally before pushing:

```bash
pre-commit run --all-files
pytest -q
```

Alternatively, run `./ci_local.sh` to execute these checks along with a local build step.

These same commands run in CI; see the workflow definition in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) (read-only).

## Makefile

Common tasks are provided via a simple `Makefile`:

```bash
make format  # pre-commit run --all-files
make lint    # ruff src tests
make test    # pytest
make build   # python -m build
```

## Testing

### Quick checks
- Run pre-commit on config changes:

  ```bash
  pre-commit run --files .pre-commit-config.yaml
  ```

- Run pytest with coverage:

  ```bash
  scripts/run_coverage.sh
  ```

> **Note:** DO NOT ACTIVATE ANY GitHub Actions files. This repository intentionally avoids enabling `.github/workflows/*` in this workflow.

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

| Environment variable | Description |
| -------------------- | ----------- |
| `CODEX_USER_SETUP_PATH` | Path to the user setup script. Defaults to `.codex/user_setup.sh`. |
| `CODEX_USER_SETUP_FORCE` | Run the user setup even if `.codex/.user_setup.done` exists. |

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

* **--session-id** (required): Which session to view.
* **--db**: Path to the SQLite DB. If omitted, common names like `data/logs.sqlite` or `logs.db` are autodetected.
* **--format**: Output `json` or `text` (default).
* **--level**: Filter by level (repeatable), e.g., `--level INFO --level ERROR`.
* **--contains**: Case-insensitive substring match over the message.
* **--since / --until**: ISO timestamps or dates. Results are chronological.
* **--limit**: Cap the number of returned rows.
* **--table**: Explicit table name. If omitted, the CLI infers a suitable table/columns. Table names must match `[A-Za-z0-9_]+`.

> **Note:** Inference expects columns like `session_id`, `ts`/`timestamp`, and `message`. If levels are present, common names (`level`, `severity`) are detected.

#### SQLite Connection Pooling

Set `CODEX_SQLITE_POOL=1` to prefer a pooled/shared SQLite connection in CLI tools
(e.g., viewer/query/export). This reduces connection churn and can improve throughput
on repeated commands. Default is non-pooled behavior.

Examples:
  export CODEX_SQLITE_POOL=1
  python -m codex.logging.viewer --session-id S123 --format text
  python -m codex.logging.export  S123 --format json


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

* `--session-id`: exact match on session identifier
* `--role`: one of your stored roles (e.g., `user`, `assistant`, `system`, `tool`)
* `--after`, `--before`: ISO-8601 or `YYYY-MM-DD` boundaries
* `--format {text,json}`: choose plain text or JSON (default `text`)
* `--limit/--offset`, `--order {asc,desc}`

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
  backed by Python logging.  Each Python invocation is checked and failures are
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

This repository uses [pre-commit](https://pre-commit.com) to run code-quality hooks locally.

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
