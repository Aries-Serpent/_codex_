# Newcomer Guide to _codex_

Welcome to **_codex_**! This guide will help you understand the repository structure, get started quickly, and navigate the codebase effectively.

## Table of Contents

1. [What is _codex_?](#what-is-codex)
2. [Repository Structure](#repository-structure)
3. [Quick Start](#quick-start)
4. [Key Concepts](#key-concepts)
5. [Common Workflows](#common-workflows)
6. [Zendesk Support Administration](#zendesk-support-administration)
7. [Testing and Quality](#testing-and-quality)
8. [Getting Help](#getting-help)
9. [Next Steps](#next-steps)

## What is _codex_?

**_codex_** is a comprehensive ML training, evaluation, and plugin framework with specialized support for:

- **Machine Learning Workflows**: Training models with LoRA, curriculum learning, and reasoning templates
- **Zendesk Administration**: Configuration-as-code for Zendesk Support workflows
- **Data Quality**: Built-in validation using Great Expectations
- **Logging & Observability**: Session tracking, metrics, and monitoring
- **CLI Tools**: Rich command-line interfaces for all major operations

### Key Features

- **Local-first**: Designed for offline/local workflows with no CI required
- **Modular**: Plugin architecture for extensibility
- **Reproducible**: Deterministic seeding, checkpoint management, and manifest tracking
- **Configuration-driven**: Hydra-based configuration system

## Repository Structure

```text
_codex_/
├── src/                    # Main source code
│   ├── codex/             # Core codex modules
│   ├── codex_ml/          # ML training and evaluation
│   ├── codex_cli/         # CLI applications
│   └── training/          # Training utilities
├── docs/                   # Comprehensive documentation
│   ├── runbooks/          # Operational runbooks
│   ├── guides/            # How-to guides
│   ├── templates/         # Reusable templates
│   └── checklists/        # Verification checklists
├── configs/               # Hydra configuration files
├── tests/                 # Test suite
├── cli/                   # CLI entry points
├── tools/                 # Utility scripts
├── scripts/               # Automation scripts
├── examples/              # Example code and configs
└── .codex/                # Local automation artifacts
```text

### Important Directories

| Directory | Purpose |
|-----------|---------|
| `src/codex/` | Core functionality: logging, CLI, Zendesk integration |
| `src/codex_ml/` | ML training, evaluation, metrics, and plugins |
| `docs/` | All documentation (start with `docs/README_ROOT.md`) |
| `configs/` | Hydra configurations for training and evaluation |
| `tests/` | Comprehensive test suite |
| `cli/` | Command-line interface implementations |
| `examples/` | Working examples and sample configurations |

## Quick Start

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Git**
- (Optional) Docker for containerized workflows

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Aries-Serpent/_codex_.git
   cd _codex_
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   # Option 1: Install with dev dependencies
   pip install -e '.[dev]'
   
   # Option 2: Install specific extras
   pip install -e '.[ml,cli,logging]'
   
   # Option 3: Minimal installation
   pip install -e .
   ```

4. **Verify installation**:
   ```bash
   codex --help
   codex-train --help
   codex-eval --help
   ```

### First Steps

1. **Explore the documentation**:
   ```bash
   # Serve docs locally
   pip install -r docs/requirements.txt
   mkdocs serve
   # Visit http://localhost:8000
   ```

2. **Run a quick training test**:
   ```bash
   codex-train experiment=debug training.max_epochs=1 \
     training.batch_size=2 \
     data.train_path=data/train.jsonl \
     data.eval_path=data/eval.jsonl \
     logging.mlflow_enable=false \
     training.output_dir=artifacts/runs/quickstart
   ```

3. **Check repository status**:
   ```bash
   codex-status-audit --skip-audit
   ```

## Key Concepts

### 1. Configuration Management (Hydra)

_codex_ uses [Hydra](https://hydra.cc/) for configuration management:

- **Base configs**: `configs/` directory
- **Override syntax**: `key=value` on command line
- **Config groups**: `+group=option` syntax
- **Composition**: Hierarchical configuration merging

**Example**:
```bash
codex-train +reasoning=baseline \
  curriculum.phase_schedule=starter \
  training.max_steps=500
```text

### 2. Plugin System

_codex_ has an extensible plugin architecture:

- **Entry points**: Defined in `pyproject.toml`
- **Plugin types**: tokenizers, models, metrics, data loaders, trainers
- **Discovery**: `codex-list-plugins`

**Example plugin registration**:
```python
# In pyproject.toml
[project.entry-points."codex_ml.metrics"]
my_metric = "my_package.metrics:my_metric_function"
```text

### 3. Logging and Sessions

Session-based logging tracks all operations:

- **Session ID**: Set via `CODEX_SESSION_ID`
- **Log storage**: `.codex/sessions/` (NDJSON format)
- **Database**: SQLite at `.codex/session_logs.db`
- **Roles**: `system`, `user`, `assistant`, `tool`

**Useful commands**:
```bash
python -m codex.logging.session_logger  # Record events
python -m codex.logging.viewer          # View sessions
python -m codex.logging.query_logs      # Search logs
```text

### 4. Checkpointing and Reproducibility

Built-in checkpoint management:

- **Automatic saving**: Via `--checkpoint_dir` and `--save_steps`
- **Resume capability**: Load from existing checkpoints
- **Metadata tracking**: Git commit, environment info
- **Deterministic seeding**: Reproducible results

### 5. Quality Gates

Local quality gates (no CI required):

- **Fences**: `python tools/validate_fences.py`
- **Schema validation**: `python tools/schema_validate.py`
- **Pre-commit hooks**: `pre-commit run --files <files>`
- **Tests**: `nox -s tests`

## Common Workflows

### Training a Model

```bash
# Basic training
codex-train \
  training.max_epochs=3 \
  training.batch_size=16 \
  data.train_path=data/train.jsonl \
  data.eval_path=data/eval.jsonl \
  training.output_dir=artifacts/runs/my_model

# Training with LoRA
codex-train \
  --lora-r 8 \
  --lora-alpha 16 \
  --lora-dropout 0.05 \
  --precision bf16 \
  training.output_dir=artifacts/runs/lora_model

# Training with reasoning templates
codex-train +reasoning=baseline \
  curriculum.phase_schedule=starter \
  logging.reasoning_trace=true \
  training.output_dir=artifacts/runs/reasoning
```text

### Evaluating a Model

```bash
# Basic evaluation
codex-eval \
  --config configs/evaluation/base.yaml \
  --metrics-only

# Reasoning evaluation
codex evaluate \
  --config configs/evaluation/reasoning.yaml \
  --log-metrics .codex/metrics/reasoning.ndjson \
  --run-id my-eval-run
```text

### Managing Configurations

```bash
# List available reasoning templates
codex reasoning-templates list

# Explain a specific template
codex reasoning-templates explain baseline

# Validate a configuration
codex-validate-config --config configs/training/base.yaml
```text

### Running Tests

```bash
# Run all tests
nox -s tests

# Run specific test modules
pytest tests/test_training.py -v

# Run with coverage
pytest --cov=src/codex_ml tests/

# Offline tests
HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  nox -s tests_offline
```text

### Pre-commit Checks

```bash
# Install pre-commit hooks
pre-commit install

# Run on changed files
pre-commit run --files <file1> <file2>

# Run all hooks on all files
pre-commit run --all-files

# Individual tools
black src/ --line-length 100
ruff check src/
isort src/
mypy src/
```text

## Zendesk Support Administration

_codex_ provides comprehensive tools for managing Zendesk Support as code. See the dedicated [Zendesk Newcomer Guide](docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md) for details.

### Zendesk Resources

- **[Zendesk Configuration-as-Code Guide](docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md)** - Complete admin workflow guide
- **[AI Agent App Builder Mathematical Model](docs/zendesk/AI_AGENT_APP_BUILDER.md)** - Physics-inspired optimization framework for AI Agent App Builder (not ZAF)
- **[Workflow Diagrams](docs/zendesk/WORKFLOW_DIAGRAMS.md)** - Visual workflow guides and decision trees
- **[Quick Start Script](examples/zendesk/quickstart.sh)** - Interactive setup automation
- **[Examples & Templates](examples/zendesk/README.md)** - Configuration examples and templates

### Quick Zendesk Workflow

1. **Snapshot current state**:
   ```bash
   codex zendesk snapshot --env=dev
   ```

2. **Create desired state** in `configs/desired/zendesk/`

3. **Generate diff**:
   ```bash
   codex zendesk diff triggers \
     --desired-file configs/desired/triggers.json \
     --current-file snapshot/dev/latest/triggers.json \
     --output diffs/triggers_diff.json
   ```

4. **Apply changes**:
   ```bash
   codex zendesk apply triggers plans/triggers_plan.json --env=dev
   ```

5. **Verify**:
   ```bash
   codex zendesk metrics
   ```

### Key Zendesk Resources

- [Zendesk Admin Workflow](docs/runbooks/zendesk_admin_workflow.md)
- [End-to-End Support Workflows Plan](docs/runbooks/zendesk_e2e_support_workflows_plan.md)
- [AI Agent App Builder Guide](docs/zendesk/AI_AGENT_APP_BUILDER.md) - Mathematical optimization framework
- [Workflow Diagrams](docs/zendesk/WORKFLOW_DIAGRAMS.md) - Visual guides
- [Zendesk First Cycle Verification](docs/checklists/zendesk_first_cycle_verification.md)
- [Zendesk API Reference](docs/zendesk_api_reference.md)

## Testing and Quality

### Running the Test Suite

```bash
# Full test suite with nox
nox -s tests

# Specific test markers
pytest -m smoke          # Quick smoke tests
pytest -m integration    # Integration tests
pytest -m slow           # Resource-intensive tests
```text

### Code Quality Tools

| Tool | Purpose | Command |
|------|---------|---------|
| **Black** | Code formatting | `black src/ --line-length 100` |
| **Ruff** | Linting | `ruff check src/` |
| **isort** | Import sorting | `isort src/` |
| **mypy** | Type checking | `mypy src/` |
| **pytest** | Testing | `pytest tests/` |

### Quality Gates

Before committing:

1. **Format code**: `black src/ tests/`
2. **Lint**: `ruff check src/ tests/`
3. **Type check**: `mypy src/`
4. **Run tests**: `nox -s tests`
5. **Pre-commit**: `pre-commit run --files <changed_files>`

## Getting Help

### Documentation Resources

1. **Start here**: [docs/README_ROOT.md](docs/README_ROOT.md)
2. **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Changelog**: [docs/CHANGELOG.md](docs/CHANGELOG.md)
5. **CLI Reference**: [docs/CLI.md](docs/CLI.md)

### Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Missing dependencies | `pip install -e '.[dev,test]'` |
| Import errors | Check `PYTHONPATH` and virtual environment |
| Hydra config errors | Verify config file exists in `configs/` |
| Test failures | Check if optional deps installed or mocked |
| Database lock errors | Set `CODEX_SQLITE_POOL=1` |

See [docs/troubleshooting.md](docs/troubleshooting.md) for more.

### Environment Variables

Key environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `CODEX_SESSION_ID` | Session identifier | Auto-generated |
| `CODEX_SESSION_LOG_DIR` | Log directory | `.codex/sessions` |
| `CODEX_LOG_DB_PATH` | SQLite database path | `.codex/session_logs.db` |
| `CODEX_SQLITE_POOL` | Enable connection pooling | `0` (disabled) |

See `.github/copilot-instructions.md` for complete list.

### Getting Support

- **Issues**: Repository-specific policy changes
- **Discussions**: Architecture reviews, questions
- **Maintainers**: Tag `@maintainer` in forums
- **Security**: Follow escalation path in CONTRIBUTING.md

## Next Steps

### For ML Engineers

1. Review [docs/guides/reasoning_overview.md](docs/guides/reasoning_overview.md)
2. Explore [docs/examples/lora_quickstart.md](docs/examples/lora_quickstart.md)
3. Study [docs/examples/training-configs.md](docs/examples/training-configs.md)
4. Read [docs/resume_cookbook.md](docs/resume_cookbook.md)
5. Check [docs/plugins.md](docs/plugins.md)

### For Support/DevOps Engineers

1. Start with [docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md](docs/zendesk/ZENDESK_NEWCOMER_GUIDE.md)
2. Run [examples/zendesk/quickstart.sh](examples/zendesk/quickstart.sh) for interactive setup
3. Review [docs/zendesk/WORKFLOW_DIAGRAMS.md](docs/zendesk/WORKFLOW_DIAGRAMS.md) for visual guides
4. Study [docs/runbooks/zendesk_admin_workflow.md](docs/runbooks/zendesk_admin_workflow.md)
5. Study [docs/runbooks/zendesk_e2e_support_workflows_plan.md](docs/runbooks/zendesk_e2e_support_workflows_plan.md)
6. Practice with examples in `examples/zendesk/`
7. Review [docs/checklists/zendesk_first_cycle_verification.md](docs/checklists/zendesk_first_cycle_verification.md)

### For Zendesk App Developers

1. Read [docs/zendesk/AI_AGENT_APP_BUILDER.md](docs/zendesk/AI_AGENT_APP_BUILDER.md) - Mathematical model
2. Understand location manifold and capacity fields ($\mathcal{L}$, $\mathbf{s}(\ell)$)
3. Learn capability spectrum ($\phi_d$ for each dimension)
4. Study security constraints and forbidden operations ($\mathcal{F}$)
5. Calculate feature feasibility ($\Psi_i$) using the formulas
6. Apply optimization framework (minimize action $\mathcal{S}$)
7. Review worked examples (wizard, real-time monitor, bulk export)

### For Contributors

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Review [docs/templates/](docs/templates/) for workflow templates
3. Study [docs/QUALITY_GATES.md](docs/QUALITY_GATES.md)
4. Check [docs/How_We_Release.md](docs/How_We_Release.md)
5. Explore [noxfile.py](noxfile.py) for automation tasks

### Learning Paths

#### Path 1: Quick Start (1 hour)
1. Install and verify setup
2. Run quickstart training example
3. Explore docs locally with mkdocs
4. Run test suite

#### Path 2: ML Workflow Deep Dive (4-8 hours)
1. Study Hydra configuration system
2. Train model with various configurations
3. Implement custom metric plugin
4. Create evaluation pipeline
5. Experiment with LoRA and reasoning templates

#### Path 3: Zendesk Administration (4-8 hours)
1. Understand Zendesk workflow concepts
2. Set up Zendesk environment
3. Practice snapshot/diff/apply cycle
4. Create custom desired state configurations
5. Implement monitoring and verification

## Useful Commands Reference

### CLI Entry Points

```bash
codex                    # Main CLI
codex-train             # Training entry point
codex-eval              # Evaluation entry point
codex-ml                # ML CLI
codex-cli               # Alternative CLI
codex-generate          # Generation utilities
codex-infer             # Inference
codex-validate-config   # Config validation
codex-list-plugins      # Plugin discovery
codex-status-audit      # Repository audit
codex-task-sequence     # Task automation
```text

### Common Operations

```bash
# Repository status
codex-status-audit
codex repo-map --reasoning

# Training
codex-train --help
codex-train experiment=debug

# Evaluation
codex-eval --help
codex evaluate --config configs/evaluation/base.yaml

# Zendesk
codex zendesk --help
codex zendesk snapshot --env=dev

# Logging
python -m codex.logging.viewer
python -m codex.logging.query_logs

# Quality checks
fence-check
pre-commit run --all-files
nox -s tests
```text

## Additional Resources

### Documentation Categories

- **Runbooks**: Step-by-step operational guides (`docs/runbooks/`)
- **Guides**: Conceptual how-to guides (`docs/guides/`)
- **Templates**: Reusable templates (`docs/templates/`)
- **Examples**: Working examples (`docs/examples/`)
- **Checklists**: Verification checklists (`docs/checklists/`)
- **Reference**: API and technical reference (`docs/reference/`)

### Key Configuration Files

- `pyproject.toml`: Package configuration, dependencies, entry points
- `noxfile.py`: Test and automation sessions
- `.pre-commit-config.yaml`: Pre-commit hooks
- `mkdocs.yml`: Documentation site configuration
- `conftest.py`: Pytest configuration and fixtures

### Repository Conventions

1. **Local-first**: No GitHub Actions by default
2. **Quality gates**: Run locally via pre-commit and nox
3. **Artifacts**: Keep in `.codex/` directory
4. **Documentation**: Follow Diátaxis framework
5. **Testing**: Use pytest with appropriate markers

---

**Welcome to _codex_!** We're excited to have you here. If you have questions or need help, don't hesitate to ask in discussions or open an issue.

Happy coding! 🚀
