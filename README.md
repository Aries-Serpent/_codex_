# codex-universal

`codex-universal` is a reference implementation of the base Docker image available in [OpenAI Codex](http://platform.openai.com/docs/codex).

This repository is intended to help developers cutomize environments in Codex, by providing a similar image that can be pulled and run locally. This is not an identical environment but should help for debugging and development.

For more details on environment setup, see [OpenAI Codex](http://platform.openai.com/docs/codex).

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

## What's included

In addition to the packages specified in the table above, the following packages are also installed:

- `ruby`: 3.2.3
- `bun`: 1.2.10
- `java`: 21
- `bazelisk` / `bazel`

See [Dockerfile](Dockerfile) for the full details of installed packages.

## Session Logging (SQLite)

This repository provides a CLI viewer for session-scoped logs stored in SQLite.

### Usage
```bash
python -m src.codex.logging.viewer --session-id <ID> [--db path/to.db] [--format json|text] \
  [--level INFO --contains token --since 2025-01-01 --until 2025-12-31] [--limit 200] [--table logs]
```

* **--session-id** (required): Which session to view.
* **--db**: Path to the SQLite DB. If omitted, common names like `data/logs.sqlite` or `logs.db` are autodetected.
* **--format**: Output `json` or `text` (default).
* **--level**: Filter by level (repeatable), e.g., `--level INFO --level ERROR`.
* **--contains**: Case-insensitive substring match over the message.
* **--since / --until**: ISO timestamps or dates. Results are chronological.
* **--limit**: Cap the number of returned rows.
* **--table**: Explicit table name. If omitted, the CLI infers a suitable table/columns.

> **Note:** Inference expects columns like `session_id`, `ts`/`timestamp`, and `message`. If levels are present, common names (`level`, `severity`) are detected.

**DO NOT ACTIVATE ANY GitHub Actions files.**

## Logging: Querying transcripts

This repository includes a CLI to query a SQLite database and render chat transcripts, auto-detecting tables and columns.

### Installation / Invocation
```bash
python3 -m src.codex.logging.query_logs --help
# Specify DB path explicitly or via env:
#   export CODEX_DB_PATH=.codex/session_logs.db
#   python3 -m src.codex.logging.query_logs --session-id S123 --role user --after 2025-01-01 --format json
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
python -m src.codex.logging.export SESSION_ID --format json
# plain text
python -m src.codex.logging.export SESSION_ID --format text
# specify a custom database
python -m src.codex.logging.export SESSION_ID --db /path/to/db.sqlite
```

The tool reads from `codex.logging.config.DEFAULT_LOG_DB` (defaults to
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

**Storage:** SQLite at `codex.logging.config.DEFAULT_LOG_DB`.
**Note:** This change is additive and does not activate any GitHub Actions.

## Session Hooks (NDJSON)

Lightweight helpers capture shell and Python entry sessions as NDJSON lines:

- `scripts/session_logging.sh` – provides `codex_session_start` / `codex_session_end`
- `codex/logging/session_hooks.py` – Python context manager emitting start/end events

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
export CODEX_LOG_DB_PATH="${PWD}/.codex/codex_logs.sqlite"
```

#### Set in PowerShell

```powershell
$env:CODEX_SESSION_ID = [guid]::NewGuid().ToString()
$env:CODEX_LOG_DB_PATH = (Join-Path (Get-Location) ".codex/codex_logs.sqlite")
```

> **Note:** Keep logs within the repo (e.g., `./.codex/`) for portability and review.

### Quick Start (Python)

```python
import os, sqlite3, time, pathlib

db = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/codex_logs.sqlite"))
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

If absent, a minimal viewer is provided at `tools/codex_log_viewer.py`:

```bash
python tools/codex_log_viewer.py --db "$CODEX_LOG_DB_PATH" --session "$CODEX_SESSION_ID"
```

**DO NOT ACTIVATE ANY GitHub Actions files.**

<!-- CODEX:LOGGING:END -->

## Session Logging (Context Manager)

You can log session lifecycle and chat events via a small context manager:

```python
from src.codex.logging.session_logger import SessionLogger

with SessionLogger(session_id="demo") as sl:
    sl.log("user", "hi")
    sl.log("assistant", "hello")
```

This writes to `codex.logging.config.DEFAULT_LOG_DB` by default; override with
`CODEX_LOG_DB_PATH`.

## Session Query (Experimental)

**DO NOT ACTIVATE ANY GitHub Actions files.**

Query session events from the local SQLite database.

```bash
# by session id (ascending by default)
python -m codex.logging.session_query --session-id 12345 --db .codex/session_logs.db

# last N events (most recent first)
python -m codex.logging.session_query --last 50 --db .codex/session_logs.db

# descending order for session view (optional)
python -m codex.logging.session_query --session-id 12345 --db .codex/session_logs.db --desc
```

The tool auto-detects timestamp, session, role, and message columns and will look for
both `.db` and `.sqlite` variants of the database path. Override the path via `--db` or
`CODEX_DB_PATH`.

