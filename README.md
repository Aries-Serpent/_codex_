# `_codex_`
> Offline‑first ML repo with reproducible training, schema‑validated configs, and daily status reporting (v1.2).

## 🤖 Codex Quick-Index (For AI Agents)

**New to this repository as an AI agent (Copilot, ChatGPT, etc.)?**

**Start here:** [AGENTS.md](AGENTS.md) → Pointer to comprehensive agent guide  
**Machine index:** [_codex_/codex_index.yaml](_codex_/codex_index.yaml) → Primary files, priorities, orchestration map  
**Continuation:** [AGENT_CONTINUATION_PROMPT.md](AGENT_CONTINUATION_PROMPT.md) → Resume protocol for multi-step tasks

**Optimization:** Following the wavepoint order in AGENTS.md reduces repository traversal time by 62%.

---

## Status & CI Badges

- Status Validation: ![Status Validation](https://github.com/Aries-Serpent/_codex_/actions/workflows/status_validation.yml/badge.svg)
- Security Gates: ![Security Gates](https://github.com/Aries-Serpent/_codex_/actions/workflows/security_gates.yml/badge.svg)
- Nox Quality Gates: ![Nox Gates](https://github.com/Aries-Serpent/_codex_/actions/workflows/nox_gates.yml/badge.svg)
- Semgrep SAST: ![Semgrep](https://github.com/Aries-Serpent/_codex_/actions/workflows/semgrep.yml/badge.svg)

## Documentation

All primary documentation now lives in the [`docs/`](docs/) directory.

### API Reference

📚 **[API Documentation](docs/api/README.md)** - Comprehensive API reference auto-generated from source code docstrings

To build API docs locally:
```bash
# Using nox (recommended - deterministic offline build)
nox -s docs_build

# Or using the build script directly
bash scripts/docs_build.sh

# Skip optional modules (faster, no ML dependencies required)
SKIP_OPTIONAL=1 nox -s docs_build

# Strict mode (fail if any modules missing - for CI)
FAIL_ON_MISSING=1 bash scripts/docs_build.sh
```text

**Build Modes:**
- **Default**: Includes all available modules (core + optional ML when installed)
- **Skip Optional** (`SKIP_OPTIONAL=1`): Only core modules, no ML dependencies needed
- **Strict** (`FAIL_ON_MISSING=1`): Fail build if any requested modules are unavailable

**Note:** The API documentation script automatically includes optional packages like `codex_ml` when their dependencies are installed. For complete API documentation including the ML framework:

```bash
# Install optional ML dependencies
pip install -e .[ml]

# Build full documentation
nox -s docs_build
```text

View the generated docs at `artifacts/docs/api/index.html` or serve locally:
```bash
python -m http.server -d artifacts/docs/api 8000
```text

### New to _codex_?

👉 **Start here**: [`NEWCOMER_GUIDE.md`](NEWCOMER_GUIDE.md) - Comprehensive onboarding guide for all newcomers

### Quick Links - Status & Validation

- **Status Update Generator**: [tools/generate_status_update.py](tools/generate_status_update.py) - Automated JSON status report generator
- **Status Update Schema**: [schemas/codex_status_update.schema.json](schemas/codex_status_update.schema.json) - JSON Schema v1.2
- **Status Update Guide**: [tools/README_status_update.md](tools/README_status_update.md) - Usage and integration guide
- **Status Template**: [codex_status_template_v1.2.md](docs/templates/status/codex_status_template_v1.2.md)
- **Status Schema (JSON)**: [codex_status_template.schema_v1.2.json](docs/templates/status/codex_status_template.schema_v1.2.json)
- **Authoring (Quickstart)**: [authoring_quickstart_v1.2.md](docs/templates/status/authoring_quickstart_v1.2.md)
- **Validation Guides**: [docs/validation](docs/validation)
- **Ops Workflow**: [status_reports.md](docs/ops/status_reports.md)

### Quick Links - General

- **General Onboarding**: [`NEWCOMER_GUIDE.md`](NEWCOMER_GUIDE.md)
- **Zendesk Administration**: [`docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md`](docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md)
- **Project Overview**: [`docs/README_ROOT.md`](docs/README_ROOT.md)
- **Contribution Guidelines**: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- **Changelog**: [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
- **Operational Templates**: [`docs/templates/README.md`](docs/templates/README.md)

### Local DoD (short)

```bash
# Run all quality gates
nox -s lint typecheck tests gates

# Validate status schema
pytest -q tests/status/test_example_report_schema.py

# Validate configs
python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml
```text

## Local Gates & Status Reports

This repository ships **local-only** quality gates (no CI) and a local status reporter:

- See **docs/ops/local_gates.md** for running fences, evaluator, schema checks, and the selection guard.
- See **docs/ops/status_reports.md** for generating a reusable **STATUS_REPORT.md** (including template mode, `--verbose`, and `--save-logs`).

Quick start:
```bash
python tools/status_report.py --summary samples/assistant_message_summary.sample.json --selected 3 --out STATUS_REPORT.md
```text

### Repository Status Audit

Generate a comprehensive status update audit report for the Codex repository:

```bash
# Generate JSON status update (new schema-based generator)
codex-status-audit --generate
# Output: .codex/status/_codex_status_update-YYYY-MM-DD.json

# Or use the direct script
python tools/generate_status_update.py

# Full audit and report (legacy)
codex-status-audit

# Quick regeneration with existing artifacts
codex-status-audit --skip-audit

# Compare against baseline
codex-status-audit --baseline audit_artifacts/capabilities_scored.json.baseline
```text

The new JSON-based status update generator provides:
- Automated repository analysis
- 8 capability checks with gap analysis
- Reproducibility controls audit
- Test infrastructure status
- Security assessment
- Schema validation (v1.2)

See **[tools/README_status_update.md](tools/README_status_update.md)** for the new generator documentation.  
See **[docs/cli/status_audit.md](docs/cli/status_audit.md)** for legacy audit tool usage.

## Candidate Selection (local-only)

You can generate a local selection recommendation across 1–4 assistant variants:

```bash
python tools/selection_report.py \
  --summary samples/assistant_message_summary.sample.json \
  --out SELECTION_REPORT.md
```text

This runs the evaluator and enforces required selection-guard signals, then explains the tie-break.

## Quickstart

```bash
codex-train experiment=debug training.max_epochs=1 training.batch_size=2 \
  data.train_path=data/train.jsonl data.eval_path=data/eval.jsonl \
  logging.tensorboard=false logging.mlflow_enable=false \
  training.output_dir=artifacts/runs/quickstart
codex reasoning-templates list
codex-train +reasoning=baseline curriculum.phase_schedule=starter \
  logging.reasoning_trace=true training.output_dir=artifacts/runs/reasoning-starter
codex evaluate --config configs/evaluation/reasoning.yaml --metrics-only
```text

### Offline-first environment bootstrap

```bash
# 1) Create and activate a virtualenv (any tool)
python -m venv .venv && . .venv/bin/activate

# 2) Install dev tools
pip install -r requirements-dev.txt

# 3) (Optional) Sync minimal runtime deps from a lockfile if provided
if [ -f requirements/lock.txt ]; then
  pip install -r requirements/lock.txt
fi

# 4) Sanity gates
python tools/validate_fences.py
python tools/schema_validate.py \
  --data manifests/selection_guard_rules.json --schema schemas/selection_guard_rules.schema.json \
  --data manifests/codex_eval_rules.v3.json --schema schemas/codex_eval_rules.v3.schema.json

# Optional: selection and status one-liners
python tools/selection_report.py --summary samples/assistant_message_summary.sample.json --out SELECTION_REPORT.md
python tools/status_report.py    --summary samples/assistant_message_summary.sample.json --selected 3 \
                                 --template docs/templates/status_update.md \
                                 --branch my/branch --pr 1234 --verbose --save-logs --out STATUS_REPORT.md
```text

---

## 🔍 Search Index

Quick access to key repository areas via GitHub search. Click any link or use the search patterns with ChatGPT/Copilot.

### Core Components

| Component | Search Query | Description |
|-----------|--------------|-------------|
| **ML Training Core** | [`path:src/codex_ml/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex_ml%2F+language%3APython) | Training engine, LoRA/QLoRA, model initialization |
| **CLI Commands** | [`path:src/codex/cli.py OR path:cli/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex%2Fcli.py+OR+path%3Acli%2F) | Command-line interface and entry points |
| **Logging & Telemetry** | [`path:src/codex/logging/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Asrc%2Fcodex%2Flogging%2F) | Session tracking, SQLite backend, query engine |
| **Services & APIs** | [`path:services/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aservices%2F+language%3APython) | Microservices, adapters, API endpoints |
| **Interfaces & Contracts** | [`path:interfaces/ (Protocol OR pydantic)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Ainterfaces%2F+%28Protocol+OR+pydantic%29) | Type definitions, protocols, schemas |

### Configuration & Data

| Area | Search Query | Description |
|------|--------------|-------------|
| **Hydra Configs** | [`path:config/ OR path:configs/ extension:yaml`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aconfig%2F+OR+path%3Aconfigs%2F+extension%3Ayaml) | Hydra configuration files |
| **Schemas** | [`path:schemas/ (extension:json OR extension:yaml)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Aschemas%2F+%28extension%3Ajson+OR+extension%3Ayaml%29) | Data validation schemas |
| **Data Quality** | [`path:great_expectations/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Agreat_expectations%2F) | Great Expectations configurations |
| **Project Config** | [`filename:pyproject.toml OR filename:noxfile.py`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3Apyproject.toml+OR+filename%3Anoxfile.py) | Project dependencies and build config |

### Documentation & Governance

| Document Type | Search Query | Description |
|---------------|--------------|-------------|
| **Architecture** | [`path:docs/ARCHITECTURE.md OR path:docs/arch/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2FARCHITECTURE.md+OR+path%3Adocs%2Farch%2F) | System architecture, C4 diagrams |
| **ADRs** | [`path:docs/decision_records/ filename:*.md`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2Fdecision_records%2F+filename%3A*.md) | Architecture Decision Records |
| **Security & Policy** | [`filename:SECURITY.md OR path:docs/security/`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ASECURITY.md+OR+path%3Adocs%2Fsecurity%2F) | Security policy, vulnerability reporting |
| **Code Owners** | [`filename:CODEOWNERS`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ACODEOWNERS) | Repository ownership mapping |
| **API Documentation** | [`path:docs/api/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adocs%2Fapi%2F) | API references and guides |
| **Prompts & Recipes** | [`path:PROMPTS/ OR path:docs/prompts/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3APROMPTS%2F+OR+path%3Adocs%2Fprompts%2F) | ChatGPT search recipes, prompt templates |

### CI/CD & Workflows

| Area | Search Query | Description |
|------|--------------|-------------|
| **GitHub Workflows** | [`path:.github/workflows/ extension:yml`](https://github.com/Aries-Serpent/_codex_/search?q=path%3A.github%2Fworkflows%2F+extension%3Ayml) | CI/CD workflow definitions |
| **Issue Templates** | [`path:.github/ISSUE_TEMPLATE/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3A.github%2FISSUE_TEMPLATE%2F) | Bug reports, feature requests |
| **Dependabot** | [`filename:dependabot.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3Adependabot.yml) | Dependency update configuration |
| **Pre-commit Hooks** | [`filename:.pre-commit-config.yaml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3A.pre-commit-config.yaml) | Linting and formatting hooks |

### Testing & Quality

| Category | Search Query | Description |
|----------|--------------|-------------|
| **Test Files** | [`path:tests/ language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Atests%2F+language%3APython) | All test modules |
| **Test Functions** | [`"def test_" language:Python`](https://github.com/Aries-Serpent/_codex_/search?q=%22def+test_%22+language%3APython) | Individual test functions |
| **Fixtures** | [`"@pytest.fixture" OR "conftest.py"`](https://github.com/Aries-Serpent/_codex_/search?q=%22%40pytest.fixture%22+OR+%22conftest.py%22) | Test fixtures and configuration |
| **Linter Configs** | [`filename:.ruff.toml OR filename:.bandit.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3A.ruff.toml+OR+filename%3A.bandit.yml) | Code quality configuration |

### Deployment & Docker

| Resource | Search Query | Description |
|----------|--------------|-------------|
| **Dockerfiles** | [`filename:Dockerfile OR filename:docker-compose.yml`](https://github.com/Aries-Serpent/_codex_/search?q=filename%3ADockerfile+OR+filename%3Adocker-compose.yml) | Container definitions |
| **Deployment** | [`path:deploy/ OR path:manifests/`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Adeploy%2F+OR+path%3Amanifests%2F) | Deployment configurations |
| **Scripts** | [`path:scripts/ (language:Python OR language:Shell)`](https://github.com/Aries-Serpent/_codex_/search?q=path%3Ascripts%2F+%28language%3APython+OR+language%3AShell%29) | Automation and utility scripts |

### Advanced Search Patterns

```text
# Find all configuration entry points
filename:pyproject.toml OR filename:setup.py OR filename:noxfile.py

# Locate error handling patterns
path:src/ "try:" language:Python

# Find logging usage
path:src/ ("logging.info" OR "logger.error") language:Python

# Search for security-sensitive code
("password" OR "secret" OR "api_key" OR "token") language:Python

# Find deprecation notices
("deprecated" OR "DEPRECATED" OR "TODO: remove") in:file

# Locate all README files
filename:README.md

# Find Mermaid diagrams
path:docs/ "mermaid" in:file
```text

### Quick Navigation

- **Getting Started**: Start with [`NEWCOMER_GUIDE.md`](NEWCOMER_GUIDE.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Security**: Report vulnerabilities via [SECURITY.md](SECURITY.md)
- **Search Help**: Full guide in [PROMPTS/CHATGPT_SEARCH_RECIPES.md](PROMPTS/CHATGPT_SEARCH_RECIPES.md)

---

**For more search patterns and ChatGPT/Copilot guidance**, see [PROMPTS/CHATGPT_SEARCH_RECIPES.md](PROMPTS/CHATGPT_SEARCH_RECIPES.md).

## Building Docker images locally

To reproduce the CI image builds locally (recommended to use linux/amd64 platform to match published wheels):

- CPU image:

```bash
docker build --platform=linux/amd64 -f Dockerfile -t codex-ml:cpu-local .
```

- GPU image (requires NVIDIA container toolkit and compatible CUDA runtime):

```bash
docker build --platform=linux/amd64 -f Dockerfile.gpu -t codex-ml:gpu-local .
```

Notes:
- If you set `ALLOW_MULTIARCH` to `true` in the workflow, CI will attempt arm64 builds; ensure that required Python wheels exist for that platform.

### Build cache and per-arch wheels

- The Dockerfiles use BuildKit cache mounts to speed up Python package downloads:
  - Ensure BuildKit is enabled (default on GitHub Actions; locally: export DOCKER_BUILDKIT=1).
- CI uses docker/build-push-action cache-to/cache-from to reuse layers across runs.
- Per-arch wheel builds:
  - The workflow uploads wheelhouse artifacts for each enabled platform (amd64 always; arm64 only when ALLOW_MULTIARCH='true').
  - Review artifacts in the Actions run to validate wheel availability on each platform before enabling multi-arch pushes.
