# Codex Ingestion Pipeline Operations Runbook

> Generated: Previous Cycle-12-17 | Author: mbaetiong

## Overview

This runbook provides step-by-step instructions for operating the Codex Python Ingestion Pipeline. The pipeline ingests, analyzes, transforms, and verifies Python code with LLM-assisted intent inference.

## Prerequisites

- Python 3.11+
- `pip install -e .[codex]` (includes codex dependencies)
- `OPENAI_API_KEY` environment variable set (optional, for LLM features)
- Docker (optional, for sandboxed execution)

## Quick Start

```bash
# 1. Create a manifest for your script
cat > manifest.yaml << EOF
version: "1.0"
source:
  type: file
  path: "./my_script.py"
metadata:
  owner: "@yourusername"
  allow_external_llm: true
EOF

# 2. Ingest
python -m codex.cli ingest ./my_script.py --manifest manifest.yaml

# 3. Analyze
python -m codex.cli analyze <snapshot-id>

# 4. Transform (auto-apply Tier A)
python -m codex.cli transform <snapshot-id> --tier A --auto

# 5. Verify
python -m codex.cli verify <snapshot-id> --compare

# 6. List snapshots
python -m codex.cli list
```

## CLI Reference

| Command | Description | Common Flags |
|---------|-------------|--------------|
| `codex ingest` | Create snapshot from source | `--manifest`, `--snapshot-id` |
| `codex analyze` | Run static+runtime analysis | `--static-only`, `--runtime-only` |
| `codex transform` | Apply/propose changes | `--tier`, `--auto`, `--dry-run` |
| `codex verify` | Compare baseline vs patched | `--tolerance`, `--compare` |
| `codex list` | List snapshots | `--status` |
| `codex show` | Show snapshot details | `--json` |

## Pipeline Steps

### Step 1: Ingest

Creates an immutable snapshot of the source code.

```bash
python -m codex.cli ingest ./my_script.py --manifest manifest.yaml
```

**Output:** `artifacts/<timestamp>-<hash>/`

**Snapshot Structure:**
```
artifacts/20251217-abc123/
├── source/                 # Original code (immutable)
├── manifest.yaml           # Copy of ingestion manifest
├── snapshot-meta.json      # Timestamp, hash, source info
├── patches/                # Populated by transform
├── tests/codex_generated/  # Populated by verify
└── llm_provenance/         # LLM call records
```

### Step 2: Analyze

Runs static analysis on the snapshot.

```bash
python -m codex.cli analyze 20251217-abc123
```

**Output:** `artifacts/<snapshot>/static-report.json`

**Analysis includes:**
- AST parsing and complexity metrics
- Import/export analysis
- Lint checking with ruff
- Security scanning with bandit

### Step 3: Transform

Generates and optionally applies transformations.

```bash
# Dry run (default)
python -m codex.cli transform 20251217-abc123

# Auto-apply Tier A changes
python -m codex.cli transform 20251217-abc123 --tier A --auto --no-dry-run
```

**Tier Classification:**

| Tier | Name | Auto-Apply | Examples |
|------|------|------------|----------|
| A | Safe Auto-Apply | ✅ Yes | Black formatting, isort, pathlib migration |
| B | Apply with Tests | ✅ With tests | Type hints, function extraction |
| C | Suggest Only | ❌ No | Async conversion, API redesign |

### Step 4: Verify

Compares baseline and patched behavior.

```bash
python -m codex.cli verify 20251217-abc123 --compare
```

**Comparison Modes:**

| Mode | Tolerance | Use Case |
|------|-----------|----------|
| `strict` | Byte-for-byte match | Formatting changes only |
| `fuzzy` | Ignore whitespace, ordering | Refactoring changes |
| `semantic` | Equivalent meaning | Algorithm changes |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication | Required for LLM |
| `CODEX_LLM_MODEL` | Model for intent inference | `gpt-4o` |
| `CODEX_LLM_RATE_LIMIT_DELAY` | Delay between LLM calls | `1.0` |
| `CODEX_SANDBOX_TIMEOUT` | Max execution time | `60` |

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| "Snapshot not found" | Invalid snapshot ID | Run `codex list` to see available |
| "LLM rate limit" | Too many API calls | Increase `CODEX_LLM_RATE_LIMIT_DELAY` |
| "Behavioral divergence" | Transform changed behavior | Review `behavior-diff.json` |
| "Security blocker" | Critical finding detected | Review findings, adjust code |

## Rollback Procedure

If a transformation introduces issues:

```bash
# Revert to original source
cp -r artifacts/<snapshot>/source/* ./

# Or restore specific files
git checkout HEAD -- <affected-files>
```

## Best Practices

1. **Always use manifests** - Documents intent and constraints
2. **Start with Tier A** - Safe, automatic improvements
3. **Review Tier B carefully** - Requires test validation
4. **Never auto-apply Tier C** - Always requires human review
5. **Keep snapshots** - Immutable history for auditing
6. **Monitor LLM costs** - Check provenance for token usage

## Safety Guarantees

- **Immutable snapshots** - Original code is never modified
- **Tier-based safety** - Automatic changes are low-risk
- **Behavior verification** - Detects output divergence
- **Provenance tracking** - All LLM calls are recorded
- **Rollback capability** - Easy to revert changes

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `artifacts/<snapshot>/` for diagnostic information
- Check `llm_provenance/` for LLM call details
