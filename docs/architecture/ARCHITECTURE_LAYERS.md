# Platform Architecture Layers

**Version**: 1.0  
**Owner**: `codebase-health-guardian`  
**Updated**: 2026-05-27  
**D1 exit criteria**: architecture map + DOMAIN_OWNERSHIP.md + import-linter gate ✅

---

## Layer Hierarchy

```mermaid
flowchart TD
    subgraph L1["Layer 1 — CLI & Entry Points"]
        CLI["cli/\ncodex CLI commands"]
        APPS["apps/\naudio_transcriber_ui\ndev tools"]
        TOOLS["tools/\norchestration runners\nledger / offline CI"]
    end

    subgraph L2["Layer 2 — Application Services"]
        SVC["src/services/\naudio transcription\nmodel serving\nRAG serving"]
        MCP["src/mcp/\nMCP server\nschema / tools"]
        COGNITIVE["scripts/cognitive/\nOODA actions + sensors\ncognitive brain bridge"]
    end

    subgraph L3["Layer 3 — Domain Logic"]
        CODEX["src/codex/\narchive / rag / training\nagent graph"]
        CODEX_ML["src/codex_ml/\nml lifecycle\ncheckpointing / tokenization\ntraining engine"]
        TRAINING["src/training/ + training/\ncheckpoint manager\ntrainer / loss / scheduler"]
    end

    subgraph L4["Layer 4 — Infrastructure / Utilities"]
        UTILS["src/codex_ml/utils/\ncheckpointing\nsafe_pickle / serialization"]
        CONFIG[".codex/config/\nmonitoring.yaml\nrag_quality.yaml\ncompletion_scores.yaml"]
        SCRIPTS["scripts/ci/ scripts/ml/ scripts/rag/\nscripts/observability/\nCI gate scripts"]
    end

    subgraph L5["Layer 5 — Data & Storage"]
        DATA["tests/data/\nbenchmarks/\nreports/\naudit_artifacts/"]
        STORE[".codex/cognitive_brain/\nSQLiteMemory\nworkflow_patterns.jsonl"]
        BASELINE["baseline/\ncapabilities_scored_post_remediation.json"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5

    CLI -.->|"❌ PROHIBITED\ndirect data access"| DATA
    APPS -.->|"❌ PROHIBITED\nskips domain logic"| UTILS
```

---

## Boundary Rules (enforced by `import-linter.yml`)

| Rule | Allowed | Prohibited |
|------|---------|-----------|
| CLI → Services | ✅ | CLI → codex_ml internals directly |
| Services → Domain | ✅ | Services → L5 storage directly |
| Domain → Infra | ✅ | Domain → CLI (upward) |
| Infra → Storage | ✅ | Infra → Services (upward) |
| Tests → Any | ✅ | Production code → tests |

---

## Import Contract (`.importlinter` config)

```ini
[importlinter]
root_package = codex_ml

[importlinter:contract:layers]
name = Layer Hierarchy
type = layers
layers =
    cli | apps | tools
    src.services | src.mcp
    src.codex | src.codex_ml | training
    scripts
    tests
```

Run: `lint-imports --config .importlinter` (enforced by `.github/workflows/import-linter.yml`)

---

## Boundary Tests

Automated boundary tests live in `tests/architecture/test_layer_boundaries.py`.  
Run: `pytest tests/architecture/ -v`

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-05-27 | 1.0 | Initial architecture layer doc — D1 exit criteria #4 |
