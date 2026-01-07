# QA Walkthrough: Structure & Inspection Guide

This walkthrough captures a structured inventory and QA inspection map for the
repository layout, aligned to the canonical grouping, intent, and agent-facing
prompt templates.

---

## 1) Canonical inventory map (structure & order)

### Top-level grouping by domain

**Core code & runtime**
- `src/`, `interfaces/`, `cli/`, `brain_cli.py`, `codex_task_executor.py`, `codex_task_sequence.py`, `codex_utils/`, `codex_ml/`, `cognitive/`, `cognitive_app/`, `workbench/`

**Docs & governance**
- `README.md`, `QUICKSTART.md`, `GLOSSARY.md`, `GOVERNANCE.md`, `CHANGELOG*.md`, `CHANGES.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE*`, `docs/`, `guides/`, `PROMPTS`, `prompts/`, `AGENTS.md*`

**Configs & policies**
- `pyproject.toml`, `setup.cfg`, `mypy.ini`, `pytest.ini`, `mkdocs.yml`, `config/`, `configs/`, `conf/`, `config_legacy/`, `yaml_legacy/`, `policies/`, `schemas/`, `manifests/`, `mappings/`, `codex_*.(yaml|yml)`, `bandit.yaml`, `dvc.yaml`, `sitecustomize.py`

**Pipelines, automation, tooling**
- `scripts/`, `actions/`, `automation/`, `noxfile.py`, `nox_sessions/`, `nox_enhancements.py`, `Makefile*`, `tools/`, `utils/`, `validate_fences.py`, `build_helpers_manifest.py`, `run_codex_env.sh`, `run_codex_task_sequence.sh`

**Testing & quality**
- `tests/`, `conftest.py`, `coverage_reports/`, `baseline_coverage.txt`, `reports/`, `audit_artifacts/`, `artifacts/`, `monitoring/`, `great_expectations/`, `semgrep_rules/`

**Data & models**
- `data/`, `datasets/`, `db/`, `models/`, `tokenization/`, `sentencepiece/`, `transformers/`, `torch/`

**Containers & deployment**
- `Dockerfile*`, `docker/`, `docker-compose*.yml`, `deploy/`, `services/`, `ops/`

**Examples, experiments, notebooks**
- `examples/`, `experiments/`, `notebooks/`, `analysis/`, `benchmarks/`, `baseline/`, `samples/`, `archive/`, `implementation_completed/`, `logs/`, `reports/`

**Assets & misc**
- `assets/`, `audio_cleaner_v1/`, `misc/`, `temp/`, `_codex/`, `_codex_/`, `_codex_reports/`

### Hierarchical outline (root → major dirs → representative subtrees)

```
/workspace/_codex_
├── Core runtime
│   ├── src/
│   ├── interfaces/
│   ├── cli/
│   ├── codex_utils/
│   ├── codex_ml/
│   ├── cognitive/ | cognitive_app/ | workbench/
│   └── brain_cli.py, codex_task_executor.py, codex_task_sequence.py
├── Documentation & policy
│   ├── docs/
│   ├── guides/
│   ├── prompts/ | PROMPTS
│   ├── AGENTS.md, AGENTS.md.original
│   └── README.md, QUICKSTART.md, GLOSSARY.md, GOVERNANCE.md, SECURITY.md, etc.
├── Config & schemas
│   ├── config/ | configs/ | conf/
│   ├── config_legacy/ | yaml_legacy/
│   ├── schemas/ | mappings/ | manifests/
│   └── pyproject.toml, setup.cfg, mypy.ini, pytest.ini, mkdocs.yml, bandit.yaml
├── Tooling & automation
│   ├── scripts/ | automation/ | actions/
│   ├── Makefile*, noxfile.py, nox_sessions/
│   ├── tools/ | utils/
│   └── run_codex_env.sh, run_codex_task_sequence.sh
├── Tests & quality
│   ├── tests/ | conftest.py
│   ├── coverage_reports/ | baseline_coverage.txt
│   ├── reports/ | artifacts/ | audit_artifacts/
│   ├── monitoring/ | great_expectations/ | semgrep_rules/
├── Data & models
│   ├── data/ | datasets/ | db/
│   ├── models/ | tokenization/ | sentencepiece/
│   └── transformers/ | torch/
├── Containers & deployment
│   ├── Dockerfile* | docker/ | docker-compose*.yml
│   ├── deploy/ | services/ | ops/
├── Examples & research
│   ├── examples/ | experiments/ | notebooks/
│   ├── analysis/ | benchmarks/ | baseline/
│   ├── samples/ | archive/ | implementation_completed/
└── Misc
    ├── assets/ | misc/ | temp/ | logs/
    └── _codex/ | _codex_/ | _codex_reports/
```

### Reading order (recommended)

1. **Onboarding docs:** `README.md`, `QUICKSTART.md`, `GLOSSARY.md`
2. **Architecture/guardrails:** `AGENTS.md`, `.codex/guardrails.md`, `docs/agent/OPERATIONAL_GUIDELINES.md`, `docs/admin/GENESIS_SETUP_GUIDE.md`
3. **Core runtime:** `src/`, `interfaces/`, `cli/`, `brain_cli.py`, `codex_task_executor.py`, `codex_task_sequence.py`
4. **Supporting modules:** `codex_utils/`, `codex_ml/`, `cognitive/`, `workbench/`
5. **Tests & monitoring:** `tests/`, `monitoring/`, `great_expectations/`, `semgrep_rules/`
6. **Tooling & automation:** `scripts/`, `noxfile.py`, `Makefile*`, `actions/`, `automation/`
7. **Integrations & deployment:** `docker/`, `Dockerfile*`, `docker-compose*.yml`, `deploy/`, `services/`, `ops/`
8. **Experiments/archive:** `experiments/`, `notebooks/`, `analysis/`, `archive/`, `implementation_completed/`, `logs/`

---

## 2) “Purpose and intent” index

> **Legend:**  
> **Consumers:** Humans / Agents / CI / Runtime  
> **Lifecycle:** Startup / Runtime / Test / Deployment / Doc-only / Legacy  
> **Criticality:** Core / High / Medium / Low

| Path | Intent summary | Primary consumers | Lifecycle | Risk/criticality |
| --- | --- | --- | --- | --- |
| `src/` | Main application/library implementation | Runtime, agents | Runtime | **Core** |
| `interfaces/` | Public APIs & integration surfaces | Runtime, agents, CI | Runtime | **Core** |
| `cli/`, `brain_cli.py` | Command-line entry points | Humans, CI | Startup/Runtime | High |
| `codex_task_executor.py`, `codex_task_sequence.py` | Task orchestration/execution | Runtime, agents | Runtime | High |
| `codex_utils/` | Shared utilities | Runtime, tests | Runtime | Medium |
| `codex_ml/` | ML-specific modules | Runtime | Runtime | Medium–High |
| `cognitive/`, `cognitive_app/` | Cognitive system layers/UI | Runtime, humans | Runtime | Medium |
| `workbench/` | Prototyping/interactive utilities | Humans | Runtime | Medium |
| `tests/`, `conftest.py` | Automated validation | CI, humans | Test | High |
| `monitoring/`, `great_expectations/` | Observability & data validation | CI, runtime | Runtime/Test | Medium |
| `semgrep_rules/` | Static analysis rules | CI | Test/QA | Medium |
| `docs/`, `guides/` | Documentation & processes | Humans, agents | Doc-only | High (governance) |
| `AGENTS.md*` | Agent operational constraints | Agents | Doc-only | **Core (policy)** |
| `README.md`, `QUICKSTART.md` | Onboarding & usage | Humans, agents | Doc-only | High |
| `config/`, `configs/`, `conf/` | Runtime configuration | Runtime, CI | Startup/Runtime | High |
| `config_legacy/`, `yaml_legacy/` | Legacy configuration | Humans, CI | Legacy | Medium |
| `schemas/`, `mappings/` | Data schemas / mappings | Runtime, CI | Runtime/Test | Medium |
| `manifests/` | Build/deploy manifests | CI, runtime | Deployment | Medium |
| `pyproject.toml`, `setup.cfg`, `mypy.ini` | Build/type config | CI, humans | Startup/Test | High |
| `pytest.ini`, `bandit.yaml` | QA configuration | CI | Test | Medium |
| `noxfile.py`, `nox_sessions/` | Automation sessions | CI, humans | Test/Tooling | Medium |
| `Makefile*`, `tools/`, `utils/` | Dev tooling shortcuts | Humans, CI | Tooling | Medium |
| `scripts/`, `automation/`, `actions/` | Behavior automation | CI, humans | Tooling/Deployment | High |
| `Dockerfile*`, `docker/`, `docker-compose*.yml` | Containerization | CI, runtime | Deployment | High |
| `deploy/`, `services/`, `ops/` | Deployment ops | CI, runtime | Deployment | High |
| `data/`, `datasets/`, `db/` | Data storage | Runtime, humans | Runtime | Medium |
| `models/`, `tokenization/`, `sentencepiece/`, `transformers/`, `torch/` | ML assets & deps | Runtime | Runtime | Medium |
| `examples/`, `notebooks/`, `experiments/`, `analysis/`, `benchmarks/`, `baseline/` | R&D and demos | Humans | Legacy/Doc-only | Low |
| `archive/`, `implementation_completed/` | Historical artifacts | Humans | Legacy | Low |
| `logs/`, `reports/`, `artifacts/`, `audit_artifacts/` | Output & audit trails | Humans, CI | Episodic | Medium |
| `_codex/`, `_codex_`, `_codex_reports/` | Internal codex metadata | Agents, CI | Doc-only/Tooling | Medium |
| `assets/`, `misc/`, `temp/` | Auxiliary files | Humans | Low | Low |

---

## 3) Redundancy & overlap analysis

**Potential multiple sources of truth / consolidation candidates:**
1. **Multiple AGENTS.md variants** (`AGENTS.md`, `AGENTS.md.original`, `prompts/AGENTS.md`, `_codex_/AGENTS.md`) risk divergent guidance.

---

## 4) Cognitive‑brain mapping (AI Agent Intuitive Design)

### Memory layers

- **Long‑term memory (durable specs & policies):**  
  `docs/`, `guides/`, `AGENTS.md*`, `.codex/guardrails.md`, `GOVERNANCE.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE*`, `schemas/`, `mappings/`
- **Working memory (current runtime modules & configuration):**  
  `src/`, `interfaces/`, `cli/`, `codex_task_executor.py`, `codex_task_sequence.py`, `config/`, `configs/`, `conf/`, `pyproject.toml`, `setup.cfg`
- **Procedural memory (executable behavior & automation):**  
  `scripts/`, `automation/`, `actions/`, `noxfile.py`, `Makefile*`, `tools/`, `run_codex_env.sh`, `run_codex_task_sequence.sh`
- **Episodic memory (logs, reports, experiments, historical artifacts):**  
  `logs/`, `reports/`, `artifacts/`, `audit_artifacts/`, `experiments/`, `notebooks/`, `analysis/`, `archive/`, `implementation_completed/`

### Cognitive pathways

- **Input (interfaces, CLI, API):**  
  `cli/`, `brain_cli.py`, `interfaces/`, any API modules in `src/`
- **Reasoning (core logic modules):**  
  `src/`, `codex_task_executor.py`, `codex_task_sequence.py`, `codex_utils/`, `codex_ml/`
- **Action/Output (scripts, deploy, integrations):**  
  `scripts/`, `automation/`, `actions/`, `deploy/`, `services/`, `ops/`, Docker assets
- **Self‑monitoring (tests, monitoring, audit):**  
  `tests/`, `monitoring/`, `great_expectations/`, `semgrep_rules/`, `coverage_reports/`

---

## 5) Tailored prompt templates per artifact type

**Markdown docs (`docs/`, `guides/`, root .md files)**
> You are analyzing `<path>`. Explain its purpose, target audience, and how it fits the onboarding/architecture workflow. List key concepts and dependencies (what it references). Propose improvements for clarity or consistency. Generate a revised outline that preserves intent but improves flow. Check for overlap with other docs and propose consolidation.

**Python modules (`src/**/*.py`, `cli/**/*.py`, root scripts)**
> You are analyzing `<path>`. Explain the module’s responsibility, inputs/outputs, and lifecycle role. List key classes/functions and their callers. Identify dependencies and side effects. Propose refactors or guardrails, and draft an equivalent module skeleton that preserves behavior. Check for duplicated functionality elsewhere.

**Config files (YAML/TOML/INI: `config/`, `configs/`, `pyproject.toml`, `mypy.ini`, `pytest.ini`)**
> You are analyzing `<path>`. Explain configuration scope and consumers. Document defaults vs overrides and how this file is loaded. Identify overlapping config sources and conflicts. Propose a canonical consolidation strategy, and draft a minimal config that preserves behavior.

**Shell scripts (`scripts/`, `*.sh`)**
> You are analyzing `<path>`. Describe its purpose, inputs/outputs, environment assumptions, and error handling. Identify calls to external tools. Propose hardening or simplification, and draft a safer equivalent script.

**Docker files (`Dockerfile*`, `docker-compose*.yml`)**
> You are analyzing `<path>`. Describe build/runtime intent and target environment. List dependencies, base images, volumes, ports, and entrypoints. Identify overlap with other Docker assets. Propose consolidation and a canonical build path.

**Tests (`tests/`, `conftest.py`)**
> You are analyzing `<path>`. Explain test scope and coverage goals. List fixtures and dependencies. Identify gaps/edge cases. Propose additional tests and summarize how these tests validate runtime behavior.

**Notebooks/experiments (`notebooks/`, `experiments/`, `analysis/`)**
> You are analyzing `<path>`. Summarize experiment goals and outputs. Identify dependencies, data assumptions, and reproducibility gaps. Propose how to convert core insights into tests/docs or move to archive.

**Data/model assets (`data/`, `datasets/`, `models/`)**
> You are analyzing `<path>`. Explain what the assets represent and how they are consumed. Identify versioning or provenance expectations. Propose validation checks or schemas.

---

## 6) Walkthrough deliverables

### A) Master walkthrough (structure → intent → cognitive mapping → redundancy → prompts)

1. **Structure:** Root layout grouped into core runtime, docs, configs, tooling, tests, deployment, data/models, experiments.
2. **Intent:** Runtime code lives under `src/` + CLI entry points; governance in docs and AGENTS; automation in `scripts/` and CI config.
3. **Cognitive mapping:** Long‑term memory = docs/policy; working memory = runtime code + configs; procedural = scripts/tools; episodic = logs/experiments.
4. **Redundancy:** Multiple config trees, multiple changelogs, multiple AGENTS files, many Docker variants.
5. **Prompt templates:** Tailored for docs, python, configs, shell, Docker, tests, notebooks, data.

### B) Per‑section mini‑briefs

- **Docs (`docs/`, `guides/`, root .md):** Onboarding, governance, policies, and operational rules. Critical for agent compliance.
- **Core runtime (`src/`, `interfaces/`, `cli/`):** Primary runtime logic and interface boundaries. High criticality.
- **Scripts & automation (`scripts/`, `automation/`, `actions/`):** Execution mechanics and CI helpers. Ensure alignment with configs.
- **Configs (`config/`, `configs/`, `conf/`):** Runtime behavior definition. Avoid duplication/contradiction.
- **Tests (`tests/`):** Validation. Should mirror runtime structure and key edge cases.
- **Deployment (`docker*`, `deploy/`, `ops/`):** Environment packaging. Many variants; document canonical path.
- **Experiments (`experiments/`, `notebooks/`, `analysis/`):** R&D; should be clearly separated from runtime and archived when stable.

### C) Agent‑ready prompt library indexed by path/type

| Path/type | Template |
| --- | --- |
| `docs/**/*.md`, root `*.md` | Doc template (purpose, audience, overlap, outline) |
| `src/**/*.py`, `cli/**/*.py` | Python module template (responsibility, deps, skeleton) |
| `config/**/*.yml`, `pyproject.toml`, `*.ini` | Config template (scope, overrides, conflicts) |
| `scripts/**/*.sh` | Script template (inputs/outputs, env, safer rewrite) |
| `Dockerfile*`, `docker-compose*.yml` | Docker template (build intent, overlaps) |
| `tests/**/*.py` | Test template (scope, fixtures, gaps) |
| `notebooks/`, `experiments/` | Experiment template (goals, reproducibility) |
| `data/`, `models/` | Asset template (consumers, validation) |

---

## 7) QA walkthrough execution log (repo-wide traversal)

### Plan scope (deterministic)

1. Enumerate all top-level domains from the canonical inventory.
2. Traverse each domain’s root directory and capture representative immediate entries.
3. Record coverage notes and any follow-up traversal needs.

### Execution (2026-01-07)

**Core runtime & interfaces**
- Traversed: `src/`, `interfaces/`, `cli/`, `codex_utils/`, `codex_ml/`, `cognitive/`, `cognitive_app/`, `workbench/`.
- Representative entries (samples): `src/README.md`, `src/agent/`, `src/agents/`, `interfaces/tokenizer.py`, `cli/ast_upgrade.py`, `codex_utils/json_report.py`, `codex_ml/pipeline.py`, `cognitive/ingestion/`, `cognitive_app/BLUEPRINT_V2.md`, `workbench/INDEX.md`.

**Docs & governance**
- Traversed: `docs/`, `guides/`, `prompts/`, `PROMPTS/`.
- Representative entries (samples): `docs/ADMIN_IMPLEMENTATION_GUIDE.md`, `guides/CODE_STYLE_GUIDE.md`, `prompts/domains/`, `PROMPTS/CHATGPT_SEARCH_RECIPES.md`.

**Config & policy**
- Traversed: `config/`, `configs/`, `conf/`, `config_legacy/`, `yaml_legacy/`.
- Representative entries (samples): `config/DEPRECATED.md`, `configs/CONFIGURATION_STRUCTURE.md`, `conf/config.yaml`, `config_legacy/README.md`, `yaml_legacy/__init__.py`.

**Tooling & automation**
- Traversed: `scripts/`, `automation/`, `actions/`.
- Representative entries (samples): `scripts/AI_SEARCH_README.md`, `automation/codex_ready_executor.py`, `actions/openapi.yaml`.

**Tests & QA**
- Traversed: `tests/`, `monitoring/`, `great_expectations/`, `semgrep_rules/`.
- Representative entries (samples): `tests/README.md`, `monitoring/system_metrics.py`, `great_expectations/checkpoints/`, `semgrep_rules/default.yml`.

**Data & models**
- Traversed: `data/`, `datasets/`, `db/`, `models/`, `tokenization/`, `sentencepiece/`, `transformers/`, `torch/`.
- Representative entries (samples): `data/models/`, `datasets/reasoning/`, `db/schema.sql`, `models/chat_model.py`, `tokenization/loader.py`, `sentencepiece/__init__.py`, `transformers/__init__.py`, `torch/nn/`.

**Containers & deployment**
- Traversed: `docker/`, `deploy/`, `services/`, `ops/`.
- Representative entries (samples): `docker/Dockerfile.cpu`, `deploy/deploy_codex_pipeline.py`, `services/api/`, `ops/threat_model/`.

**Examples, experiments, notebooks**
- Traversed: `examples/`, `experiments/`, `notebooks/`, `analysis/`, `benchmarks/`, `baseline/`, `samples/`, `archive/`, `implementation_completed/`.
- Representative entries (samples): `examples/advanced_physics_demo.py`, `experiments/2025-01-15_smoke.md`, `notebooks/quick_start.ipynb`, `analysis/audit_pipeline.py`, `benchmarks/security_benchmarks.py`, `baseline/README.md`, `samples/README.md`, `archive/removed/`, `implementation_completed/README_STUB.md`.

**Assets & misc**
- Traversed: `assets/`, `misc/`, `temp/`.
- Representative entries (samples): `assets/manifest.json`, `misc/ARCHIVAL_SYSTEM.md`, `temp/bridge_codex_copilot_bridge/`.

### Coverage notes

- Traversal completed at the directory + immediate entry level across all top-level domains.
- Next iteration can deepen file-by-file inspection within each domain (e.g., sample `src/`, `services/`, and `scripts/` modules) if a full artifact-level QA review is required.

---

## 8) File-level sampling (repo-wide, 2026-01-07)

### Plan scope update

- Expand traversal to include file-level sampling (≥3 files per domain).
- Capture brief file notes, plus explicit risks/concerns per domain.
- Use existing repository tooling references as anchors for deterministic planning.

### Core runtime & interfaces

**File checks**
1. `src/README.md` — defines core runtime responsibilities and references ingestion/RAG/MCP components.【F:src/README.md†L1-L5】
2. `interfaces/tokenizer.py` — compatibility wrapper re-exporting `codex_ml` tokenizer adapters.【F:interfaces/tokenizer.py†L1-L9】
3. `cli/README.md` — enumerates CLI entry points and their roles in automation workflows.【F:cli/README.md†L1-L33】
4. `codex_utils/json_report.py` — deterministic JSON report merging utilities and key taxonomy definitions.【F:codex_utils/json_report.py†L1-L32】
5. `codex_ml/pipeline.py` — shim that loads the canonical pipeline from `src/` for editable installs.【F:codex_ml/pipeline.py†L1-L33】

**Risks/concerns**
- `cognitive/ingestion/Note_v2.py` pulls heavy optional dependencies (Streamlit, transformers, KeyBERT); requires dependency guards or docs when used in minimal environments.【F:cognitive/ingestion/Note_v2.py†L1-L13】
- Runtime shims imply dual import paths; ensure packaging keeps `src/` and top-level shims aligned.

### Docs & governance

**File checks**
1. `docs/ADMIN_IMPLEMENTATION_GUIDE.md` — admin checklist and system readiness status; highlights unmet setup tasks.【F:docs/ADMIN_IMPLEMENTATION_GUIDE.md†L1-L23】
2. `guides/CODE_STYLE_GUIDE.md` — coding conventions, line length, and tooling commands (Black/Ruff/isort).【F:guides/CODE_STYLE_GUIDE.md†L1-L33】
3. `prompts/AGENTS.md` — scoped prompt template guidance and security reminders for prompt handling.【F:prompts/AGENTS.md†L1-L33】

**Risks/concerns**
- Several docs declare “implementation required” or “not configured” states; governance docs should be periodically reconciled with current repo status to avoid stale readiness signals.【F:docs/ADMIN_IMPLEMENTATION_GUIDE.md†L1-L33】

### Config & policy

**File checks**
1. `config/DEPRECATED.md` — marks `config/` deprecated and instructs migration to `configs/`.【F:config/DEPRECATED.md†L1-L19】
2. `configs/CONFIGURATION_STRUCTURE.md` — canonical configuration root, includes inventory of legacy shims.【F:configs/CONFIGURATION_STRUCTURE.md†L1-L23】
3. `conf/config.yaml` — deprecated minimal config stub with defaults and seed settings.【F:conf/config.yaml†L1-L11】

**Risks/concerns**
- Multiple config roots require careful migration; tooling referencing legacy paths should be tracked to prevent drift. (`config/`, `conf/`, `config_legacy/`).【F:configs/CONFIGURATION_STRUCTURE.md†L11-L23】

### Tooling & automation

**File checks**
1. `scripts/AI_SEARCH_README.md` — documents repo search/index tooling and indexing pipeline components.【F:scripts/AI_SEARCH_README.md†L1-L33】
2. `automation/codex_ready_executor.py` — offline workflow runner with structured artifacts and staged phases.【F:automation/codex_ready_executor.py†L1-L37】
3. `actions/openapi.yaml` — local actions API spec for offline tooling usage.【F:actions/openapi.yaml†L1-L23】

**Risks/concerns**
- Offline-first tooling is clearly documented but relies on optional dependencies (e.g., `psutil`, `wandb`) and should surface missing-dependency handling consistently.【F:automation/codex_ready_executor.py†L1-L37】

### Tests & QA

**File checks**
1. `tests/README.md` — outlines pytest usage and marker taxonomy for test selection.【F:tests/README.md†L1-L23】
2. `monitoring/system_metrics.py` — optional `psutil` metrics logging; safe no-op when dependency missing.【F:monitoring/system_metrics.py†L1-L41】
3. `semgrep_rules/default.yml` — baseline static analysis rules (eval/exec, yaml.load guard).【F:semgrep_rules/default.yml†L1-L15】

**Risks/concerns**
- `monitoring/system_metrics.py` depends on `psutil`; ensure optional dependency is documented or pinned in environments that require metrics.【F:monitoring/system_metrics.py†L8-L33】

### Data & models

**File checks**
1. `db/schema.sql` — snippet table + FTS5 indexes and triggers for content search.【F:db/schema.sql†L1-L19】
2. `models/chat_model.py` — deprecated shim to `src.models.chat_model` with deprecation warning.【F:models/chat_model.py†L1-L14】
3. `tokenization/loader.py` — deprecated shim re-exporting canonical tokenizer API.【F:tokenization/loader.py†L1-L15】
4. `sentencepiece/__init__.py` — dependency stub that defers to real module if installed.【F:sentencepiece/__init__.py†L1-L33】
5. `torch/__init__.py` — dependency stub that imports real PyTorch or raises clear `ImportError`.【F:torch/__init__.py†L1-L33】

**Risks/concerns**
- Deprecation shims emit warnings; downstream users should migrate to canonical imports to reduce noise.【F:models/chat_model.py†L1-L14】【F:tokenization/loader.py†L1-L15】
- Optional dependency stubs require careful handling in production packaging to avoid accidental shadowing.【F:sentencepiece/__init__.py†L1-L33】【F:torch/__init__.py†L1-L33】

### Containers & deployment

**File checks**
1. `docker/Dockerfile.cpu` — deprecated CPU image uses Python 3.10 and installs pytest/nox for dev tests.【F:docker/Dockerfile.cpu†L1-L17】
2. `deploy/deploy_codex_pipeline.py` — deployment orchestrator with optional monitoring hooks (psutil/pynvml/W&B/MLflow).【F:deploy/deploy_codex_pipeline.py†L1-L36】
3. `services/__init__.py` — service package initializer for API/service apps.【F:services/__init__.py†L1-L1】
4. `ops/threat_model/STRIDE.md` — STRIDE snapshot of security guardrails and mitigations.【F:ops/threat_model/STRIDE.md†L1-L6】

**Risks/concerns**
- Legacy Dockerfiles note deprecation; ensure canonical Dockerfile usage is enforced to avoid drift.【F:docker/Dockerfile.cpu†L1-L3】
- Deployment scripts use optional monitoring libs; missing libs are silently ignored and should be documented for observability expectations.【F:deploy/deploy_codex_pipeline.py†L8-L36】

### Examples, experiments, notebooks

**File checks**
1. `examples/advanced_physics_demo.py` — demo script with optional dependency guards for advanced physics modules.【F:examples/advanced_physics_demo.py†L1-L31】
2. `experiments/2025-01-15_smoke.md` — smoke training loop baseline with reproducibility notes and artifacts list.【F:experiments/2025-01-15_smoke.md†L1-L36】
3. `notebooks/quick_start.ipynb` — notebook with 10 cells and standard Python kernel metadata (validated via JSON parse).【F:notebooks/quick_start.ipynb†L1-L1】
4. `analysis/audit_pipeline.py` — registered pipeline steps for inventory and workflow checks with mutation behavior on README. 【F:analysis/audit_pipeline.py†L1-L28】
5. `benchmarks/security_benchmarks.py` — security utility performance benchmarks and CLI usage guidance.【F:benchmarks/security_benchmarks.py†L1-L29】
6. `baseline/README.md` — baseline scoring metadata for audit regression comparisons.【F:baseline/README.md†L1-L23】
7. `samples/README.md` — local-only validation samples and commands.【F:samples/README.md†L1-L16】
8. `implementation_completed/README_STUB.md` — pointer to full implementation status doc.【F:implementation_completed/README_STUB.md†L1-L2】

**Risks/concerns**
- Notebooks and experiments encode reproducibility assumptions; ensure seeds and artifact paths remain available when referenced in docs.【F:experiments/2025-01-15_smoke.md†L1-L36】
- `analysis/audit_pipeline.py` modifies README in-place; should be run in controlled environments to avoid unintended doc changes.【F:analysis/audit_pipeline.py†L12-L28】

### Assets & misc

**File checks**
1. `assets/manifest.json` — manifest of file hashes for integrity tracking (large registry).【F:assets/manifest.json†L1-L20】
2. `misc/ARCHIVAL_SYSTEM.md` — archival system rules and safe-removal guarantees.【F:misc/ARCHIVAL_SYSTEM.md†L1-L26】
3. `temp/bridge_codex_copilot_bridge/README.md` — temporary bridge scaffold with constraints and layout. 【F:temp/bridge_codex_copilot_bridge/README.md†L1-L24】

**Risks/concerns**
- `assets/manifest.json` is large and should be regenerated via tooling to avoid drift or partial edits.【F:assets/manifest.json†L1-L20】
- `temp/` contains prototype scaffolds; ensure it does not leak into production packaging or CI workflows.【F:temp/bridge_codex_copilot_bridge/README.md†L1-L24】
