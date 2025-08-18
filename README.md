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

This repository now supports **session event logging** via a lightweight SQLite module:

- **Modules:**
  - `src/codex/logging/session_logger.py` – low-level logger with `SessionLogger`
  - `src/codex/logging/conversation_logger.py` – convenience wrapper with
    `start_session`, `log_message`, and `end_session`
  - **DB (default):** `./codex_session_log.db` (override with `CODEX_LOG_DB_PATH`)
  - **Schema:**
    `session_events(session_id TEXT, timestamp TEXT, role TEXT, message TEXT, model TEXT, tokens INTEGER, PRIMARY KEY(session_id, timestamp))`

### Quick start

```bash
# Log start/end from shell (e.g., entrypoint)
python -m codex.logging.session_logger --event start --session-id "$CODEX_SESSION_ID"
python -m codex.logging.session_logger --event end   --session-id "$CODEX_SESSION_ID"

# Log messages
python -m codex.logging.session_logger --event message \
  --session-id "$CODEX_SESSION_ID" --role user --message "Hello"

# Programmatic usage
```python
from codex.logging.session_logger import SessionLogger

with SessionLogger("demo-session") as log:
    log.log_message("user", "Hello")
```
```

### Querying

```sql
-- Example: last 10 messages for a session
SELECT timestamp, role, message
FROM session_events
WHERE session_id = 'YOUR_SESSION_ID'
ORDER BY timestamp DESC
LIMIT 10;
```

### Notes

* Writes are serialized and safe for multi-threaded usage (SQLite WAL mode).
* To change the DB location, set `CODEX_LOG_DB_PATH=/path/to/db.sqlite`.
* **Do NOT activate any GitHub Actions files** as part of this change; keep CI disabled unless you explicitly enable it in repo settings.

## Logging: Querying transcripts

This repository includes a CLI to query a SQLite table named `session_events` and render chat transcripts.

### Installation / Invocation
```bash
python3 -m src.codex.logging.query_logs --help
# Specify DB path explicitly or via env:
#   export CODEX_DB_PATH=data/codex.db
#   python3 -m src.codex.logging.query_logs --session-id S123 --role user --after 2025-01-01 --format json
```

### Filters

* `--session-id`: exact match on session identifier
* `--role`: one of your stored roles (e.g., `user`, `assistant`, `system`, `tool`)
* `--after`, `--before`: ISO-8601 or `YYYY-MM-DD` boundaries
* `--format {text,json}`: choose plain text or JSON (default `text`)
* `--limit/--offset`, `--order {asc,desc}`

> The tool auto-adapts to columns in `session_events` (e.g., it tolerates `created_at` vs `timestamp`, `content` vs `message`, etc.). If the table or required columns are missing, it will explain what’s expected.
