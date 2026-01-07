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
