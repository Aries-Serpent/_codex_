# Explain `_codex_` Repository Briefing

**Purpose**: Fast, canonical orientation for contributors and agents working in `Aries-Serpent/_codex_`.

**Source-of-truth inputs used**:
- `README.md`
- `docs/system/CODEBASE_COGNITIVE_MAP.md`
- `docs/system/CODEBASE_DASHBOARD.md`
- `docs/MASTER_INDEX.md`

---

## 1) Repository Purpose

`_codex_` is a modular ML/AI platform that combines:
- model training/evaluation/serving flows,
- large-scale automation and CI governance,
- agent orchestration,
- and a cognitive continuity layer for multi-session operations.

It is designed as both an engineering platform and an agent-operated repository.

---

## 2) Major Subsystems (Core Map)

- **`src/`**  
  Core platform code: ingestion pipeline, RAG, verification, MCP adapters, tooling, and service/runtime modules.

- **`agents/`**  
  Autonomous agent logic and orchestration primitives (workflow routing, optimization, context/state handling).

- **`scripts/`**  
  Operational automation: CI helpers, validation scripts, package tooling, audits, and maintenance utilities.

- **`tests/`**  
  Large mirrored test surface spanning platform, integrations, security, workflows, and regression paths.

- **`docs/`**  
  Canonical architecture, operations, runbooks, policy, and contributor guidance.

- **`.github/workflows/`**  
  CI/CD, governance gates, validation, security scanning, and self-healing automation.

---

## 3) Developer Entry Points (Start Here)

- **Package/runtime contract**: `pyproject.toml`
  - Python requirement: `>=3.12`
  - Packaging metadata and tool configuration (ruff, coverage, mypy, entry points)

- **CLI layer**: `cli/`  
  Plus documented CLI surfaces in `docs/CLI.md`.

- **Task runners / quality entry points**:
- `Makefile`
- `noxfile.py`
- `pytest.ini`

---

## 4) Key Technologies Inventory

- **Language/runtime**: Python (`>=3.12`), plus Node.js helper/task scripts (`package.json`)
- **ML stack**: PyTorch, Transformers, Datasets, PEFT, Accelerate, lm-eval
- **API/serving**: FastAPI, Ray Serve
- **Config/data**: Hydra, OmegaConf, Pydantic, PyYAML, DuckDB/SQLite
- **Quality/security**: pytest, nox, ruff, mypy, GitHub Actions with CodeQL/Semgrep/Bandit
- **Operating model**: heavy automation + agent-driven workflows + cognitive/continuation documentation

---

## 5) CI / Testing Flow (Practical)

1. Local quality commands are routed via `Makefile` and `noxfile.py`.
2. Test behavior and markers are centralized in `pytest.ini`.
3. GitHub Actions enforces workflow gates, security scans, and validation paths.
4. Repository operations rely on explicit, auditable automation scripts under `scripts/`.

---

## 6) Mermaid + Variable Mapping Maintenance Protocol

Treat the following as synchronized references:
- `docs/CODEBASE_MERMAID_MAPS.md`
- `docs/system/CODEBASE_COGNITIVE_MAP.md`
- `docs/system/CODEBASE_DASHBOARD.md`

When architecture/process state changes:
1. Update diagram nodes/edges in the relevant mermaid docs.
2. Reconcile counts/labels (agents/workflows/variables) across all three references.
3. Revalidate variable names against the variable inventory docs before publishing.
4. Ensure prose summary and diagram state match in the same commit.

---

## 7) “/chronicle tips” Recommended Operating Tips

Recommended operating guidance for contributors:
1. Keep explicit phased plans with visible checkpoints.
2. Keep tracked work outputs inside repository paths (not temporary scratch paths).
3. Start sessions from Cognitive Map + Dashboard + Mermaid Maps before edits.
4. When updating architecture docs, update both prose and diagrams in one pass.
5. For large tasks, use: discovery → map update → validation → final summary.

---

## 8) End-to-End Execution Sequence (Applied)

- **Phase A**: Read canonical architecture/index docs and extract current facts.
- **Phase B**: Build concise repository explanation pack (structure, tech, entry points, flow).
- **Phase C**: Cross-check mermaid maps and variable mappings for consistency.
- **Phase D**: Produce chronicle-style recommendations and next-session checklist.
- **Phase E**: Run final consistency pass (no stale counts, no conflicting architecture narrative, no diagram drift).

---

## 9) Where to Go Deeper

- Architecture + cognitive map: `docs/system/CODEBASE_COGNITIVE_MAP.md`
- Live operational status: `docs/system/CODEBASE_DASHBOARD.md`
- Full docs navigation index: `docs/MASTER_INDEX.md`
- High-level repository overview: `README.md`
