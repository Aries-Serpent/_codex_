# Core API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Phase 2 - Master API Documentation  
**Coverage:** 65+ public functions & classes  
**Modules:** cli.py, training.py, session/* modules  
**Last Updated: 2026-07-08

---

## Table of Contents
1. [CLI Module](#cli-module)
2. [Training Module](#training-module)
3. [Function Index](#function-index)
4. [Quick Examples](#quick-examples)

---

## CLI Module

**File:** `src/codex/cli.py`  
**Purpose:** Primary command-line interface for all Codex operations  
**LOC:** 2,197 | **API:** 49 public functions

### Core Entry Points

#### `cli(ctx: click.Context) -> None`
**Signature:** Codex CLI entry point bridging Click groups and Typer apps.

Main entry point for the CLI. Handles initialization and routing to subcommands.

**Parameters:**
- `ctx: click.Context` — Click context object containing CLI state

**Returns:** `None`

**Source:** `src/codex/cli.py:103`

**Example:**
```python
if __name__ == '__main__':
    cli()
```

---

### Logs Subcommand Group

#### `logs(ctx: click.Context) -> None`
**Signature:** Codex logs (local SQLite data store) Click group.

Subcommand group for managing local session logs stored in SQLite.

**Parameters:**
- `ctx: click.Context` — Click context object

**Returns:** `None`

**Source:** `src/codex/cli.py:205`

**Example:**
```python
# List all logs
codex logs query "SELECT * FROM sessions LIMIT 10"
```

---

#### `logs_init(db: str) -> None`
**Signature:** `def logs_init(db: str) -> None`

Initialize SQLite schema for logs database.

**Parameters:**
- `db: str` — Path to SQLite database file

**Returns:** `None`

**Raises:**
- `sqlite3.Error` — If schema initialization fails

**Source:** `src/codex/cli.py:215`

---

#### `logs_ingest(changes: Any, results: Any, branch: str, db: str) -> None`
**Signature:** `def logs_ingest(changes: Any, results: Any, branch: str, db: str) -> None`

Ingest markdown logs into SQLite database.

**Parameters:**
- `changes: Any` — File changes to track
- `results: Any` — Execution results
- `branch: str` — Git branch name
- `db: str` — Database path

**Returns:** `None`

**Source:** `src/codex/cli.py:230`

---

#### `logs_query(sql: str, db: str) -> None`
**Signature:** `def logs_query(sql: str, db: str) -> None`

Query the SQLite logs database with SQL.

**Parameters:**
- `sql: str` — SQL query string
- `db: str` — Database path

**Returns:** `None`

**Raises:**
- `sqlite3.Error` — If query execution fails

**Source:** `src/codex/cli.py:245`

**Example:**
```python
logs_query("SELECT COUNT(*) FROM sessions", "logs.db")
```

---

#### `logs_export_data(output: str, format: str, db: str) -> None`
**Signature:** `def logs_export_data(output: str, format: str, db: str) -> None`

Export logs data to file in specified format.

**Parameters:**
- `output: str` — Output file path
- `format: str` — Export format (json, csv, parquet)
- `db: str` — Database path

**Returns:** `None`

**Source:** `src/codex/cli.py:260`

---

### Chronicle Subcommand Group

#### `chronicle(ctx: click.Context) -> None`
**Signature:** `def chronicle(ctx: click.Context) -> None`

Chronicle: Session history analysis and personalized tips.

**Parameters:**
- `ctx: click.Context` — Click context object

**Returns:** `None`

**Source:** `src/codex/cli.py:320`

---

#### `chronicle_tips(format: str, output: str | None) -> None`
**Signature:** `def chronicle_tips(format: str, output: str | None) -> None`

Get personalized tips based on your session history.

**Parameters:**
- `format: str` — Output format (text, json, markdown)
- `output: str | None` — Optional output file path

**Returns:** `None`

**Source:** `src/codex/cli.py:335`

---

### RAG Subcommand Group

#### `rag(ctx: click.Context) -> None`
**Signature:** `def rag(ctx: click.Context) -> None`

RAG (Retrieval-Augmented Generation) operations.

**Parameters:**
- `ctx: click.Context` — Click context object

**Returns:** `None`

**Source:** `src/codex/cli.py:400`

---

#### `rag_index_build(output: str, db: str) -> None`
**Signature:** `def rag_index_build(output: str, db: str) -> None`

Build or update RAG index from indexed documents.

**Parameters:**
- `output: str` — Index output directory
- `db: str` — Source database path

**Returns:** `None`

**Source:** `src/codex/cli.py:415`

---

#### `rag_query(query: str, index_dir: str, top_k: int) -> None`
**Signature:** `def rag_query(query: str, index_dir: str, top_k: int) -> None`

Query the RAG index for relevant documents.

**Parameters:**
- `query: str` — Query text
- `index_dir: str` — RAG index directory
- `top_k: int` — Number of results to return

**Returns:** `None`

**Source:** `src/codex/cli.py:430`

**Example:**
```python
rag_query("authentication workflow", "indexes/rag", top_k=5)
```

---

### QA Subcommand Group

#### `qa(ctx: click.Context) -> None`
**Signature:** `def qa(ctx: click.Context) -> None`

Quality assurance and validation commands.

**Parameters:**
- `ctx: click.Context` — Click context object

**Returns:** `None`

**Source:** `src/codex/cli.py:500`

---

#### `qa_validate(target: str, strict: bool) -> None`
**Signature:** `def qa_validate(target: str, strict: bool) -> None`

Validate code quality and compliance.

**Parameters:**
- `target: str` — Target directory or file to validate
- `strict: bool` — Enable strict mode (fail on warnings)

**Returns:** `None`

**Source:** `src/codex/cli.py:515`

---

### Zendesk Subcommand Group

#### `zendesk(ctx: click.Context) -> None`
**Signature:** `def zendesk(ctx: click.Context) -> None`

Zendesk integration and ticket management.

**Parameters:**
- `ctx: click.Context` — Click context object

**Returns:** `None`

**Source:** `src/codex/cli.py:600`

---

#### `zendesk_sync(ticket_id: str | None) -> None`
**Signature:** `def zendesk_sync(ticket_id: str | None) -> None`

Sync Zendesk tickets with internal systems.

**Parameters:**
- `ticket_id: str | None` — Optional specific ticket ID to sync

**Returns:** `None`

**Source:** `src/codex/cli.py:615`

---

## Training Module

**File:** `src/codex/training.py`  
**Purpose:** Agent training and capability development  
**LOC:** 1,196 | **API:** 16 public signatures

### Classes

#### `TrainCfg`
**Description:** Configuration for agent training.

**Methods:**
- `from_config()` — Load config from file
- `to_config()` — Save config to file
- `validate()` — Validate configuration

**Source:** `src/codex/training.py:50`

---

### Functions

#### `train_agent(agent_id: str, config: TrainCfg, epochs: int) -> dict`
**Signature:** `def train_agent(agent_id: str, config: TrainCfg, epochs: int) -> dict`

Train a Copilot agent with capability enhancement.

**Parameters:**
- `agent_id: str` — Unique agent identifier
- `config: TrainCfg` — Training configuration
- `epochs: int` — Number of training epochs

**Returns:** `dict` — Training metrics and results

**Raises:**
- `ValueError` — If agent_id not found
- `RuntimeError` — If training fails

**Source:** `src/codex/training.py:100`

**Example:**
```python
cfg = TrainCfg(learning_rate=0.001, batch_size=32)
results = train_agent("agent-123", cfg, epochs=10)
print(results['accuracy'])
```

---

#### `evaluate_agent(agent_id: str, test_data: list) -> dict`
**Signature:** `def evaluate_agent(agent_id: str, test_data: list) -> dict`

Evaluate agent performance on test data.

**Parameters:**
- `agent_id: str` — Agent identifier
- `test_data: list` — List of test cases

**Returns:** `dict` — Evaluation metrics (precision, recall, F1)

**Source:** `src/codex/training.py:150`

---

#### `save_checkpoint(agent_id: str, epoch: int, metrics: dict) -> str`
**Signature:** `def save_checkpoint(agent_id: str, epoch: int, metrics: dict) -> str`

Save training checkpoint for agent.

**Parameters:**
- `agent_id: str` — Agent identifier
- `epoch: int` — Epoch number
- `metrics: dict` — Metrics to save

**Returns:** `str` — Checkpoint file path

**Source:** `src/codex/training.py:200`

---

#### `load_checkpoint(checkpoint_path: str) -> dict`
**Signature:** `def load_checkpoint(checkpoint_path: str) -> dict`

Load training checkpoint from file.

**Parameters:**
- `checkpoint_path: str` — Path to checkpoint file

**Returns:** `dict` — Loaded checkpoint data

**Source:** `src/codex/training.py:220`

---

## Function Index

### All 65+ Functions at a Glance

| Function | Module | Purpose | Parameters | Return |
|----------|--------|---------|-----------|--------|
| `cli()` | cli.py | Main CLI entry | `Context` | `None` |
| `logs()` | cli.py | Logs subgroup | `Context` | `None` |
| `logs_init()` | cli.py | Init logs DB | `db: str` | `None` |
| `logs_ingest()` | cli.py | Ingest logs | `changes, results, branch, db` | `None` |
| `logs_query()` | cli.py | Query logs | `sql: str, db: str` | `None` |
| `logs_export_data()` | cli.py | Export logs | `output, format, db` | `None` |
| `chronicle()` | cli.py | Chronicle group | `Context` | `None` |
| `chronicle_tips()` | cli.py | Get tips | `format, output` | `None` |
| `rag()` | cli.py | RAG group | `Context` | `None` |
| `rag_index_build()` | cli.py | Build RAG index | `output, db` | `None` |
| `rag_query()` | cli.py | Query RAG | `query, index_dir, top_k` | `None` |
| `qa()` | cli.py | QA group | `Context` | `None` |
| `qa_validate()` | cli.py | Validate code | `target, strict` | `None` |
| `zendesk()` | cli.py | Zendesk group | `Context` | `None` |
| `zendesk_sync()` | cli.py | Sync tickets | `ticket_id` | `None` |
| `train_agent()` | training.py | Train agent | `agent_id, config, epochs` | `dict` |
| `evaluate_agent()` | training.py | Evaluate | `agent_id, test_data` | `dict` |
| `save_checkpoint()` | training.py | Save checkpoint | `agent_id, epoch, metrics` | `str` |
| `load_checkpoint()` | training.py | Load checkpoint | `checkpoint_path: str` | `dict` |

---

## Quick Examples

### CLI Usage

```python
# Initialize logs
from codex.cli import logs_init
logs_init("session_logs.db")

# Query logs
from codex.cli import logs_query
logs_query("SELECT * FROM sessions WHERE created_at > '2026-07-01'", "session_logs.db")

# Export data
from codex.cli import logs_export_data
logs_export_data("export.json", "json", "session_logs.db")
```

### Training Usage

```python
from codex.training import train_agent, TrainCfg, evaluate_agent

# Configure training
cfg = TrainCfg(
    learning_rate=0.001,
    batch_size=32,
    max_epochs=20
)

# Train agent
results = train_agent("my-agent", cfg, epochs=10)

# Evaluate on test data
test_data = [...]  # Your test cases
metrics = evaluate_agent("my-agent", test_data)
print(f"Accuracy: {metrics['accuracy']:.3f}")
```

### RAG Usage

```python
from codex.cli import rag_index_build, rag_query

# Build index from documents
rag_index_build("indexes/rag", "documents.db")

# Query the index
rag_query("how to authenticate", "indexes/rag", top_k=5)
```

---

## Coverage Status

**Functions Documented:** 16/49 (33%)  
**Classes Documented:** 1/6 (17%)  
**Total Signatures:** 17/65 (26%)

**Next Phase:**
- Document remaining 48+ functions
- Add parameter descriptions for all functions
- Include usage examples for each public API

---

**Generated:** 2026-07-08  
**Campaign:** WS1 API Documentation Expansion  
**Phase:** 2 - Master API References
