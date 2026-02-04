# Codex Python Ingestion Pipeline

> A comprehensive pipeline for ingesting, analyzing, transforming, and verifying Python code with LLM-assisted intent inference.

## Overview

The Codex Ingestion Pipeline provides a complete system for processing Python code through the following stages:

1. **Ingest** - Create immutable snapshots from files, ZIPs, or Git URLs
2. **Analyze** - Run static (AST, lint, security) and runtime analysis
3. **Infer Intent** - Use heuristics and LLM to understand code purpose
4. **Transform** - Apply tier-based code transformations
5. **Verify** - Compare behavior and generate tests
6. **Submit** - Create PRs with artifacts and changelog

## Installation

The pipeline is part of the main Codex package:

```bash
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# 1. Create a manifest
cat > manifest.yaml << EOF
version: "1.0"
source:
  type: file
  path: "./my_script.py"
metadata:
  owner: "@username"
  allow_external_llm: true
EOF

# 2. Ingest
python -m codex.cli ingest ./my_script.py --manifest manifest.yaml

# 3. Analyze
python -m codex.cli analyze <snapshot-id>

# 4. Transform (Tier A auto-apply)
python -m codex.cli transform <snapshot-id> --tier A --auto

# 5. Verify
python -m codex.cli verify <snapshot-id> --compare
```

### Python API

```python
from src.codex.ingest import ingest, parse_manifest
from src.codex.analyze.static import analyze
from src.codex.analyze.runtime import SandboxManager, RuntimeTracer
from src.codex.intent import infer_intent
from src.codex.transform.transformer import transform
from src.codex.verify.comparator import compare

# Ingest
snapshot = ingest("./script.py", manifest_path="manifest.yaml")

# Static analysis
report = analyze(snapshot.get_source_dir(), snapshot.snapshot_id)

# Intent inference
intent = infer_intent(report.to_dict(), source_excerpt="...")

# Transform
result = transform(snapshot.get_source_dir(), snapshot.snapshot_id)

# Verify
comparison = compare(baseline_dir, patched_dir)
```

## Pipeline Components

### Ingest (`src/codex/ingest/`)

Creates immutable snapshots of source code.

- **adapter.py** - Ingest from files, directories, ZIPs, Git URLs
- **manifest.py** - Parse and validate ingestion manifests

**Snapshot Structure:**
```
artifacts/<snapshot-id>/
├── source/                 # Original code (immutable)
├── manifest.yaml           # Copy of ingestion manifest
├── snapshot-meta.json      # Timestamp, hash, source info
├── patches/                # Generated patches
├── tests/codex_generated/  # Generated tests
└── llm_provenance/         # LLM call records
```

### Analyze (`src/codex/analyze/`)

Runs static and runtime analysis.

**Static Analysis:**
- AST parsing with libcst
- Complexity metrics (cyclomatic, cognitive)
- Import/export extraction
- Lint checking (ruff integration)
- Security scanning (bandit integration)

**Runtime Analysis:**
- Sandboxed execution with resource limits
- IO capture (stdin, stdout, stderr)
- Function call tracing
- File operation monitoring

### Intent (`src/codex/intent/`)

Infers code intent using heuristics and LLM.

- **inferer.py** - Heuristic detection (CLI, GUI, web service, etc.)
- **llm_client.py** - OpenAI integration with provenance recording

**Detected Code Types:**
- CLI tools (argparse, click, typer)
- GUI apps (tkinter, PyQt, PySide)
- Web services (flask, fastapi, django)
- Data processing (pandas, numpy, polars)
- Networked apps (requests, httpx, socket)

### Transform (`src/codex/transform/`)

Applies tier-based code transformations.

| Tier | Name | Auto-Apply | Examples |
|------|------|------------|----------|
| A | Safe Auto-Apply | ✅ Yes | Formatting, import sorting, pathlib migration |
| B | Apply with Tests | ✅ With tests | Type hints, function extraction |
| C | Suggest Only | ❌ No | Async conversion, API redesign |

### Verify (`src/codex/verify/`)

Compares baseline and patched behavior.

**Comparison Modes:**
- `strict` - Byte-for-byte match
- `fuzzy` - Ignore whitespace, ordering
- `semantic` - Equivalent meaning (timestamps, UUIDs normalized)

### CLI (`src/codex/cli/`)

Command-line interface and PR operator.

**Commands:**
- `ingest` - Create snapshot from source
- `analyze` - Run static+runtime analysis
- `transform` - Apply/propose changes
- `verify` - Compare baseline vs patched
- `list` - List snapshots
- `show` - Show snapshot details

## Schemas

JSON/YAML schemas for validation:

- `schemas/static-report.schema.json` - Static analysis report
- `schemas/ingest-manifest.schema.yaml` - Ingestion manifest
- `schemas/intent.schema.yaml` - Intent specification

## Configuration

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication | Required for LLM |
| `CODEX_LLM_MODEL` | Model for intent inference | `gpt-4o` |
| `CODEX_LLM_RATE_LIMIT_DELAY` | Delay between LLM calls | `1.0` |
| `CODEX_SANDBOX_TIMEOUT` | Max execution time | `60` |

### Manifest Schema

```yaml
version: "1.0"
source:
  type: file | zip | git-url
  path: "<path or URL>"
  ref: "<git ref if git-url>"
entry_point: "<module:function>"
sample_inputs:
  - path: "<input file>"
    description: "<description>"
golden_outputs:
  - input_ref: "<matching input>"
    expected_output: "<output file>"
    comparison_mode: exact | fuzzy | semantic
constraints:
  max_runtime_seconds: 60
  max_memory_mb: 512
  allowed_network: false
metadata:
  owner: "@username"
  privacy: public | private
  allow_external_llm: true
```

## Safety & Security

### Sandboxed Execution

- Resource limits (CPU, memory, timeout)
- Deterministic environment (fixed seeds)
- Network isolation (configurable)
- Temporary workspace isolation

### LLM Safety Guards

- No private data to external LLM (configurable)
- Constrained prompts ("Do not change behavior")
- Provenance recording for all calls
- Rate limiting

### Transformation Safety

- Tier A: Non-invasive, safe by definition
- Tier B: Requires test validation
- Tier C: Human review required

## Documentation

- [Operational Runbook](../../docs/plans/operational_runbook.md) - Step-by-step guide
- [Refactor Rules](transform/refactor-rules.yaml) - Transformation definitions
- [Sample Manifest](ingest/sample-manifest.yaml) - Example manifest
- [Prompt Template](intent/prompt_templates/summarize-intent.md) - LLM prompt

## Tests

Comprehensive test suite with 101 tests:

```bash
# Run all pipeline tests
pytest tests/codex/test_ingest.py
pytest tests/codex/test_analyze.py
pytest tests/codex/test_intent.py
pytest tests/codex/test_transform.py
pytest tests/codex/test_verify.py
pytest tests/codex/test_cli.py
```

## License

Part of the Codex project. See repository root for license.
