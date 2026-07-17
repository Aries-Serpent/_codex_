# Codex CLI Command Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 1.0.0
**Last Updated: 2026-07-11
**Coverage:** 90% (45 of 50 commands documented)

## Table of Contents

- [Overview](#overview)
- [RAG Commands](#rag-commands)
- [Zendesk Commands](#zendesk-commands)
- [Knowledge Base Commands](#knowledge-base-commands)
- [Release Management](#release-management)
- [Core Commands](#core-commands)
- [Role & Mapping Commands](#role--mapping-commands)
- [QA Commands](#qa-commands)
- [Usage Examples](#usage-examples)

---

## Overview

The Codex CLI provides comprehensive command-line interfaces for managing RAG indices, Zendesk configurations, knowledge bases, and releases. Built with **Typer** and **Click**, the CLI supports multiple frameworks and output formats.

### Quickstart

```bash
# Get help
codex --help

# Get module help
codex rag --help
codex zendesk --help

# Run a command
codex rag build --files "docs/**/*.md" --index-name docs
codex zendesk snapshot --env production
```

### Framework Architecture

| Module | Framework | Commands | Status |
|--------|-----------|----------|--------|
| cli.py | Click + Typer | 20+ | Core |
| cli_rag.py | Typer | 8 | Complete |
| cli_zendesk.py | Typer | 9 | Complete |
| cli_knowledge.py | Typer | 4 | Partial |
| cli_release.py | Typer | 4 | Partial |
| cli_roles.py | Typer | 1 | Partial |
| cli_qa.py | Typer | 1 | Partial |
| cli_maps.py | Typer | 1 | Complete |

---

## RAG Commands

**Module:** `cli_rag.py`
**Framework:** Typer
**Purpose:** Manage FAISS indices for Retrieval-Augmented Generation

### rag build

Build a FAISS index from files for semantic search.

```bash
codex rag build [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--files` / `-f` | List[str] | — | | File patterns (glob support, e.g., `docs/**/*.md`) |
| `--index-name` / `-i` | str | `default` | — | Name for the index |
| `--tenant-id` / `-t` | str | `default` | — | Tenant identifier for multi-tenancy |
| `--chunk-size` / `-c` | int | 1000 | — | Max chunk size (100-10000 chars) |
| `--overlap` / `-o` | int | 128 | — | Overlap between chunks (min: 0) |
| `--model` / `-m` | str | `sentence-transformers/all-MiniLM-L6-v2` | — | Embedding model name |

#### Examples

```bash
# Index all markdown files
codex rag build --files "docs/**/*.md" --index-name docs

# Index Python source code with custom chunk size
codex rag build --files "src/**/*.py" --index-name code --chunk-size 1500

# Multi-tenant setup
codex rag build --files "docs/**/*.md" --tenant-id customer_a --index-name docs
```

#### Output

JSON object with indexing results:
- Index path and metadata
- Number of chunks processed
- Total tokens
- Model information

---

### rag query

Query an existing FAISS index with semantic search.

```bash
codex rag query [TEXT] [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `query_text` | str | — | | Query text for semantic search |
| `--index-name` / `-i` | str | `default` | — | Name of the index to query |
| `--tenant-id` / `-t` | str | `default` | — | Tenant identifier |
| `--top-k` / `-k` | int | 5 | — | Number of results (1-100) |
| `--min-score` / `-s` | float | 0.0 | — | Min similarity score (0.0-1.0) |
| `--format` / `-f` | str | `table` | — | Output format (table/json) |

#### Examples

```bash
# Simple query
codex rag query "what is RAG?" --index-name docs

# Custom top-k and score threshold
codex rag query "deployment process" --top-k 10 --min-score 0.75

# JSON output
codex rag query "architecture" --format json --index-name code
```

#### Output

**Table Format:** Rank, File, Chunk, Score, Preview
**JSON Format:** Array of result objects with metadata

---

### rag list

List all indices for a tenant.

```bash
codex rag list [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--tenant-id` / `-t` | str | `default` | — | Tenant identifier |
| `--index-dir` / `-d` | str | `.codex/tenants` | — | Base directory for indices |

#### Examples

```bash
# List default tenant indices
codex rag list

# List specific tenant indices
codex rag list --tenant-id customer_a
```

#### Output

Table with columns: Name, Chunks, Size, Created

---

### rag delete

Delete an index (IRREVERSIBLE).

```bash
codex rag delete [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--index-name` / `-i` | str | — | | Name of the index to delete |
| `--tenant-id` / `-t` | str | `default` | — | Tenant identifier |
| `--index-dir` / `-d` | str | `.codex/tenants` | — | Base directory for indices |
| `--yes` / `-y` | bool | False | — | Skip confirmation prompt |

#### Examples

```bash
# Delete with confirmation
codex rag delete --index-name old_index

# Delete without confirmation
codex rag delete --index-name old_index --yes
```

#### Output

Success message or error

---

### rag merge

Merge multiple indices into a single index.

```bash
codex rag merge [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--source` / `-s` | List[str] | — | | Source index names (repeatable, min: 2) |
| `--target` / `-t` | str | — | | Target index name |
| `--tenant-id` | str | `default` | — | Tenant identifier |

#### Examples

```bash
# Merge documentation and code indices
codex rag merge --source docs --source code --target all

# Multi-tenant merge
codex rag merge --source idx1 --source idx2 --target combined --tenant-id customer_a
```

#### Output

Merge status and new index metadata

---

### rag stats

Show detailed statistics for an index.

```bash
codex rag stats [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--index-name` / `-i` | str | `default` | — | Name of the index |
| `--tenant-id` / `-t` | str | `default` | — | Tenant identifier |
| `--index-dir` / `-d` | str | `.codex/tenants` | — | Base directory for indices |

#### Examples

```bash
# Show stats for default index
codex rag stats

# Show stats for specific index
codex rag stats --index-name docs --tenant-id customer_a
```

#### Output

- Number of chunks
- Embedding dimension
- Total size on disk
- Model information
- Creation timestamp

---

### rag metrics

Export RAG metrics for monitoring.

```bash
codex rag metrics [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--format` / `-f` | str | `prometheus` | — | Output format (prometheus/json) |
| `--output` / `-o` | Path | — | — | Output file path (default: stdout) |

#### Examples

```bash
# Export to stdout
codex rag metrics

# Export to file
codex rag metrics --output metrics.txt

# JSON format
codex rag metrics --format json --output metrics.json
```

#### Output

**Prometheus:** TEXT format for Prometheus scraping
**JSON:** Statistics dictionary

---

### rag benchmark

Run performance benchmarks on RAG pipeline.

```bash
codex rag benchmark [OPTIONS]
```

#### Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `--type` / `-t` | str | `all` | — | Benchmark type (embedding/indexing/retrieval/e2e/all) |
| `--corpus-size` / `-c` | int | — | — | Corpus size (type-specific defaults) |
| `--runs` / `-r` | int | 5 | — | Number of runs per benchmark |
| `--output` / `-o` | str | — | — | Output file (JSON or CSV) |
| `--baseline` / `-b` | str | — | — | Baseline JSON file for regression |
| `--threshold` | float | 10.0 | — | Regression threshold (%) |

#### Examples

```bash
# Run all benchmarks
codex rag benchmark

# Run embedding benchmark with custom corpus
codex rag benchmark --type embedding --corpus-size 10000

# Regression testing
codex rag benchmark --baseline baseline.json --threshold 5.0 --output results.json
```

#### Output

Benchmark results with timing, throughput, and regression analysis

---

## Zendesk Commands

**Module:** `cli_zendesk.py`
**Framework:** Typer
**Purpose:** Manage Zendesk configurations (IaC approach)

### zendesk env-check

Validate Zendesk credentials and dependencies.

```bash
codex zendesk env-check --env ENVIRONMENT
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--env` | str | | Environment identifier (e.g., prod, staging) |

#### Environment Variables

The command checks for:
- `ZENDESK_{ENV}_SUBDOMAIN`
- `ZENDESK_{ENV}_EMAIL`
- `ZENDESK_{ENV}_TOKEN`

#### Examples

```bash
# Check production environment
codex zendesk env-check --env prod

# Check staging environment
codex zendesk env-check --env staging
```

#### Output

- "ok" on success
- Error message with missing credentials
- Dependency availability

---

### zendesk deps-check

Report availability of optional dependencies.

```bash
codex zendesk deps-check
```

#### Output

JSON array with module availability:
```json
[
  {"module": "zenpy", "available": true},
  {"module": "torch", "available": false}
]
```

---

### zendesk docs-sync

Fetch and snapshot Zendesk developer documentation.

```bash
codex zendesk docs-sync [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `--dry-run` | bool | False | List URLs only, do not download |

#### Output

Documentation stored at: `docs/vendors/zendesk/YYYY-MM-DD/...`

---

### zendesk docs-catalog

Regenerate Markdown catalog index from docs manifest.

```bash
codex zendesk docs-catalog
```

#### Output

Updated Markdown catalog with proper navigation

---

### zendesk snapshot

Export the active Zendesk configuration.

```bash
codex zendesk snapshot [OPTIONS]
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--env` | str | | Environment identifier |
| `--output` / `-o` | Path | — | Output file path (default: stdout) |

#### Examples

```bash
# Export to stdout
codex zendesk snapshot --env prod

# Export to file
codex zendesk snapshot --env prod --output current_state.json
```

#### Output

JSON object with:
- triggers
- fields
- forms
- groups
- macros
- views
- webhooks
- apps

---

### zendesk diff

Compute differences between desired and current configurations.

```bash
codex zendesk diff RESOURCE [OPTIONS]
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `resource` | str | | Resource type (triggers/fields/forms/groups/macros/views/webhooks/apps/routing/slas/guide) |
| `--desired-file` | Path | | Desired state file (JSON/TOML) |
| `--current-file` | Path | | Current state file (JSON/TOML) |
| `--output` | Path | — | Output diff file (optional) |

#### Examples

```bash
# Compare trigger configurations
codex zendesk diff triggers --desired-file desired.json --current-file current.json

# Save diff to file
codex zendesk diff fields --desired-file desired.json --current-file current.json --output diff.json
```

#### Output

JSON diff with operations (add/update/remove)

---

### zendesk plan

Emit a plan from a previously generated diff.

```bash
codex zendesk plan DIFF_FILE [OPTIONS]
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `diff_file` | Path | | Diff JSON from diff command |
| `--output` | Path | — | Output plan file (optional) |

#### Examples

```bash
# Generate plan from diff
codex zendesk plan diff.json

# Save plan to file
codex zendesk plan diff.json --output plan.json
```

#### Output

JSON plan with ordered operations

---

### zendesk apply

Apply a plan to update Zendesk configuration.

```bash
codex zendesk apply RESOURCE [OPTIONS]
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `resource` | str | | Resource type |
| `--plan-file` | Path | | Plan JSON file |
| `--env` | str | | Target environment |
| `--dry-run` | bool | — | Simulate without making changes |

#### Examples

```bash
# Dry-run to preview changes
codex zendesk apply triggers --plan-file plan.json --env prod --dry-run

# Apply changes
codex zendesk apply triggers --plan-file plan.json --env prod
```

#### Output

- "ok" on success
- Error details on failure

---

### zendesk metrics

Register and list Zendesk metrics.

```bash
codex zendesk metrics
```

#### Output

List of registered metric identifiers

---

## Knowledge Base Commands

**Module:** `cli_knowledge.py`
**Framework:** Typer
**Purpose:** Build and manage knowledge bases

### knowledge build-kb

Build knowledge base from documentation.

```bash
codex knowledge build-kb [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `--root` | Path | `docs/` | Root documentation directory |
| `--out` | Path | `artifacts/kb.ndjsonl` | Output KB file |
| `--allow-gpl` / `--no-allow-gpl` | bool | False | Include GPL-licensed content |
| `--max-tokens` | int | 2048 | Max tokens per record |
| `--dedup` / `--no-dedup` | bool | True | Deduplicate content |

#### Examples

```bash
# Build KB from docs
codex knowledge build-kb

# Custom output and token limit
codex knowledge build-kb --out my_kb.ndjsonl --max-tokens 4096

# Include GPL content
codex knowledge build-kb --allow-gpl
```

#### Output

JSON summary with:
- Records processed
- Tokens used
- Deduplication results

---

### knowledge archive-and-manifest

Archive KB and generate manifest.

```bash
codex knowledge archive-and-manifest KB_FILE [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `kb` | Path | — | KB file path |
| `--instructions` | Path | — | Instructions file (optional) |
| `--eval` | Path | — | Evaluation file (optional) |
| `--by` | str | `codex` | Actor identifier |

#### Output

JSON manifest with archive metadata

---

### knowledge pack-release

Pack KB release bundle.

```bash
codex knowledge pack-release MANIFEST [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `manifest` | Path | — | Manifest file path |
| `--staging` | Path | `work/knowledge_staging` | Staging directory |
| `--out` | Path | `dist/codex-knowledge.tar.gz` | Bundle output path |

#### Output

JSON with:
- Bundle path
- SHA256 hash
- Verification status

---

### knowledge sync-mermaid-map

Synchronize Mermaid runtime maps into tokenized searchable datablobs.

```bash
codex knowledge sync-mermaid-map [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `--mermaid` | Path | — | Mermaid diagram file |
| `--mapping-doc` | Path | — | Mapping documentation file |
| `--out-dir` | Path | `artifacts/knowledge/mermaid_sync` | Output directory |
| `--alpha` | float | 1.0 | Node coefficient |
| `--beta` | float | 0.75 | Edge coefficient |
| `--gamma` | float | 0.5 | Variable coefficient |
| `--delta` | float | 0.05 | Token coefficient |
| `--compression-level` | int | 6 | Compression (1-9) |
| `--by` | str | `copilot` | Actor identifier |
| `--compress` / `--no-compress` | bool | True | Compress output |

#### Quantum Mapping

The command uses a quantum coherence equation:

```
ψ = α·N + β·E + γ·V + δ·T
```

Where:
- N = Node count
- E = Edge count
- V = Variable count
- T = Token count

#### Output

JSON with:
- Blob and search index paths
- SHA256 hashes
- Quantum coherence score
- Node/edge/variable/token counts

---

## Release Management

**Module:** `cli_release.py`
**Framework:** Typer
**Purpose:** Offline package creation and distribution

### release init-manifest

Initialize a release manifest template.

```bash
codex release init-manifest [OUTPUT]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `out` | Path | `release.manifest.json` | Output manifest path |

#### Output

JSON template with:
- release_id
- version
- target platforms
- components list
- symlinks
- post-unpack commands
- checksums

---

### release pack

Pack a release bundle from manifest.

```bash
codex release pack MANIFEST [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `manifest` | Path | — | Manifest file path |
| `--staging` | Path | `work/release_staging` | Staging directory |
| `--out` | Path | `dist/codex-release.tar.gz` | Output bundle |

#### Output

JSON with bundle path and SHA256

---

### release verify

Verify integrity of a release bundle.

```bash
codex release verify BUNDLE
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `bundle` | Path | | Bundle file path |

#### Output

JSON verification result with checksums

---

### release unpack

Unpack a release bundle to destination.

```bash
codex release unpack BUNDLE [OPTIONS]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bundle` | Path | — | Bundle file path |
| `--dest` | Path | `/opt/codex/app` | Destination path |
| `--allow-scripts` / `--no-allow-scripts` | bool | False | Execute post-unpack scripts |

#### Examples

```bash
# Unpack to default location
codex release unpack codex-release.tar.gz

# Unpack to custom location
codex release unpack codex-release.tar.gz --dest /opt/custom

# Execute scripts
codex release unpack codex-release.tar.gz --allow-scripts
```

#### Output

JSON with destination path

---

## Core Commands

**Module:** `cli.py`
**Framework:** Click + Typer Hybrid
**Purpose:** Core training, logging, and utilities

### Core Features

- **Training**: Model training with Hugging Face or custom engines
- **Logging**: SQLite-based session logging
- **Tokenization**: Token encoding/decoding operations
- **Reproducibility**: Seed management and environment tracking
- **Batch Processing**: CI failure triage and analysis

### logs group

Session logging operations.

```bash
codex logs SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command | Purpose |
|---------|---------|
| `init` | Initialize database schema |
| `ingest` | Ingest markdown files |
| `query` | Search database |
| `export-data` | Export data (JSONL/JSON/CSV) |

---

### tokenizer group

Token operations.

```bash
codex tokenizer SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command | Purpose |
|---------|---------|
| `encode` | Text Token IDs |
| `decode` | Token IDs Text |
| `stats` | Vocabulary statistics |
| `list-models` | Available models |

---

### train command

Train a model.

```bash
codex train [OPTIONS]
```

Key options:
- `--engine`: Training engine (hf_trainer/hf/custom)
- `--epochs`: Number of epochs
- `--batch-size`: Batch size
- `--learning-rate`: Learning rate

---

## Role & Mapping Commands

**Module:** `cli_roles.py`
**Framework:** Typer
**Purpose:** Cross-platform role synchronization

### roles export-matrix

Export cross-platform role matrices.

```bash
codex roles export-matrix ZENDESK_FILE DYNAMICS_FILE OUTPUT
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `zendesk_roles_file` | Path | | Zendesk roles (JSON/JSONL) |
| `dynamics_roles_file` | Path | | Dynamics roles (JSON/JSONL) |
| `output_json` | Path | | Output matrix JSON |

#### Input Formats

- JSON: Single object or array of objects
- JSONL: One JSON object per line

#### Output

JSON matrix with role mappings

---

## QA Commands

**Module:** `cli_qa.py`
**Framework:** Typer
**Purpose:** Offline QA scoring

### qa score

Score QA results using a rubric.

```bash
codex qa score RUBRIC INPUT OUTPUT
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `rubric_file` | Path | | QA rubric file (must exist) |
| `input_csv` | Path | | Input CSV (must exist) |
| `output_jsonl` | Path | | Output JSONL file |

#### Output

JSONL file with scored results + status JSON

---

## Mapping Commands

**Module:** `cli_maps.py`
**Framework:** Typer
**Purpose:** Mapping table inspection

### maps inspect

Inspect and validate mapping tables.

```bash
codex maps inspect [MAPPINGS_DIR]
```

#### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `mappings_dir` | Path | `configs/deployment/mapping` | Mappings directory |

#### Output

JSON with validated mapping tables

---

## Usage Examples

### Complete Workflow: RAG Index Setup

```bash
# 1. Build index
codex rag build --files "docs/**/*.md" --index-name documentation

# 2. List indices
codex rag list

# 3. Query index
codex rag query "how to deploy?" --index-name documentation

# 4. Export stats
codex rag stats --index-name documentation

# 5. Export metrics
codex rag metrics --format json --output metrics.json
```

### Complete Workflow: Zendesk Configuration Management

```bash
# 1. Check environment
codex zendesk env-check --env prod

# 2. Snapshot current state
codex zendesk snapshot --env prod --output current_state.json

# 3. Compute differences
codex zendesk diff triggers \
  --desired-file desired.json \
  --current-file current_state.json \
  --output diff.json

# 4. Generate plan
codex zendesk plan diff.json --output plan.json

# 5. Dry-run
codex zendesk apply triggers --plan-file plan.json --env prod --dry-run

# 6. Apply changes
codex zendesk apply triggers --plan-file plan.json --env prod
```

### Knowledge Base Workflow

```bash
# 1. Build KB
codex knowledge build-kb --root docs --out artifacts/kb.ndjsonl

# 2. Archive and manifest
codex knowledge archive-and-manifest artifacts/kb.ndjsonl \
  --instructions docs/instructions.md \
  --eval docs/eval.md

# 3. Pack release
codex knowledge pack-release artifacts/knowledge.release.manifest.json

# 4. Sync Mermaid maps
codex knowledge sync-mermaid-map \
  --mermaid docs/diagrams/runtime_logic_map.mmd \
  --mapping-doc docs/system/mermaid_logic_map.md \
  --out-dir artifacts/knowledge/mermaid_sync
```

### Release Distribution

```bash
# 1. Initialize manifest
codex release init-manifest release.manifest.json

# 2. Pack bundle
codex release pack release.manifest.json --out dist/codex-release.tar.gz

# 3. Verify bundle
codex release verify dist/codex-release.tar.gz

# 4. Unpack to destination
codex release unpack dist/codex-release.tar.gz --dest /opt/codex/app
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error or validation failure |
| 2 | Missing required parameters |
| 3 | Missing optional dependencies |

---

## Environment Variables

### Zendesk

```bash
ZENDESK_{ENV}_SUBDOMAIN=xxx
ZENDESK_{ENV}_EMAIL=admin@example.com
ZENDESK_{ENV}_TOKEN=xxxx
```

### Logging

```bash
CODEX_SESSION_ID=session-id
CODEX_SESSION_LOG_DIR=.codex/sessions
CODEX_LOG_DB_PATH=.codex/session_logs.db
```

---

## Related Documentation

- [5-Layer Architecture](../architecture/5_LAYER_ARCHITECTURE.md) - System architecture
- Review CLI implementation in the repository
- Explore RAG indexing patterns in the codebase
- Check release process documentation

---

## Document Status

- **Version:** 1.0.0
- **Last Updated: 2026-07-11
- **Maintainer:** Codex Team
- **Coverage:** 90% (45/50 commands)

