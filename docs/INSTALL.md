# codex-ml Installation Guide

Welcome to codex-ml v0.1.0! This guide covers installation across three distinct deployment profiles.

## Quick Start

### Core Profile (Lightweight, Offline-First)
```bash
pip install codex-ml[core]
```

**Best for:** Lightweight deployments, offline environments, edge devices  
**Size:** 8-15 MB  
**Entry Points:** 5 core CLI tools  
**Dependencies:** stdlib + config + validation only

### Runtime Profile (ML Inference & Analysis)
```bash
pip install codex-ml[runtime]
```

**Best for:** Production inference, pattern recognition, API services  
**Size:** 20-35 MB  
**Entry Points:** Adds ML pipeline tools  
**Dependencies:** torch, transformers, ray[serve], fastapi

### Full Profile (Development & Everything)
```bash
pip install codex-ml[full]
```

**Best for:** Development, testing, experimentation, research  
**Size:** 100+ MB  
**Entry Points:** All 50+ CLI tools  
**Dependencies:** All dev tools, testing frameworks, ML ecosystem

## Installation Details

### Requirements

- **Python:** 3.12 or higher (required)
- **Pip:** 20.0 or higher (recommended)
- **OS:** Linux, macOS, Windows (with limitations - see platform notes)

### Platform-Specific Notes

#### Linux / macOS
All three profiles install without issues. Full feature support guaranteed.

#### Windows
- **Core profile:** Fully supported
- **Runtime profile:** May have issues with `torch` (check `torch` Windows compatibility)
- **Full profile:** Same torch limitations apply
- **Workaround:** Use WSL2 (Windows Subsystem for Linux) for full compatibility

### Installation Steps

#### 1. Verify Python Version
```bash
python3 --version  # Should be 3.12.x
```

If you have an older version, install Python 3.12:
```bash
# On macOS with Homebrew
brew install python@3.12

# On Ubuntu/Debian
sudo apt-get install python3.12 python3.12-venv

# On Windows
# Download from https://www.python.org/downloads/
```

#### 2. Create Virtual Environment (Optional but Recommended)
```bash
python3.12 -m venv codex-env
source codex-env/bin/activate  # On Windows: codex-env\Scripts\activate
```

#### 3. Install codex-ml with Your Preferred Profile
```bash
# Option A: Core profile (fastest, smallest)
pip install codex-ml[core]

# Option B: Runtime profile (includes ML)
pip install codex-ml[runtime]

# Option C: Full profile (all features)
pip install codex-ml[full]

# Option D: Latest development version (if using git)
pip install -e ".[core]"  # From repository root
```

#### 4. Verify Installation
```bash
# Check installation
pip show codex-ml

# Run smoke tests
pytest tests/smoke/test_install.py -v

# Check CLI entry points
codex-ml --help
codex-ml-cli --help
codex-cli --help
codex-smoke --help
codex-import-ndjson --help

# Check for dependency conflicts
pip check
```

## Core Profile Entry Points

The core profile installs 5 essential CLI tools:

| Command | Module | Purpose |
|---------|--------|---------|
| `codex-ml` | `codex_ml.cli.main` | Main CLI interface |
| `codex-ml-cli` | `codex_ml.cli.main` | Alias for codex-ml |
| `codex-cli` | `codex_ml.cli.simple_cli` | Simplified CLI |
| `codex-smoke` | `codex_cli.app` | Smoke test runner |
| `codex-import-ndjson` | `aries_serpent_core.logging.import_ndjson` | NDJSON import utility |

### Example Usage

```bash
# Get help for any command
codex-ml --help

# Run the app
codex-smoke --help

# Import NDJSON logs
codex-import-ndjson --input logs.ndjson --output converted
```

## Runtime Profile Entry Points

Additional CLI tools available in the runtime profile (builds on core):

| Command | Purpose |
|---------|---------|
| `codex-train` | Training interface |
| `codex-eval` | Evaluation interface |
| `codex-generate` | Code generation |
| `codex-infer` | Model inference |
| `codex-validate-config` | Configuration validation |
| `codex-perf` | Performance benchmarking |
| Plus 15+ additional ML tools |

## Full Profile Entry Points

The full profile includes all CLI tools for development:

- **Code Analysis:** `codex-analyze`, `codex-audit`, `codex-metrics`, `codex-ast`
- **Documentation:** `docs-inventory`, `docs-coverage`, `docs-validate`, `docs-query`
- **Utilities:** `codex-ndjson`, `codex-offline-bootstrap`, `fence-check`
- **Development:** `codex-setup`, `codex-patch-runner`, `codex-workflow`
- **Plus 20+ additional development tools**

## Dependency Management

### Core Profile Dependencies

The core profile includes only essential, offline-first dependencies:

```
hydra-core==1.3.2          # Configuration framework
omegaconf>=2.3             # YAML configuration
pydantic>=2.4              # Data validation
pydantic-settings>=2.14.2  # Settings management
pyyaml>=6.0                # YAML parsing
marshmallow>=3.7.1         # Serialization
typer>=0.12                # CLI framework
click>=8.1                 # CLI building blocks
libcst>=1.0.0              # AST parsing
parso>=0.8.0               # Python parsing
tree-sitter>=0.25.2        # Parser generation
And 8+ other utility/security dependencies
```

**Total:** ~50 dependencies, all pure-Python or lightweight

### Runtime Profile (Additional)

Adds ML-focused dependencies:
- `torch>=2.6.1` - Deep learning
- `transformers>=5.12.1` - NLP models
- `datasets>=5.0.0` - Data loading
- `ray[serve]>=2.9` - Distributed computing
- `fastapi>=0.135.3` - Web services
- Plus 15+ additional ML/data dependencies

### Full Profile (All)

Includes everything for development:
- All core + runtime dependencies
- Testing: pytest, pytest-cov, hypothesis, tox
- Quality: ruff, black, mypy, pre-commit
- ML research: wandb, mlflow, tensorboard
- Data: pandas, scikit-learn, dvc
- Plus 50+ additional development tools

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'codex_ml'"

**Cause:** Installation didn't complete or Python path is misconfigured  
**Solution:**
```bash
# Reinstall
pip install --force-reinstall codex-ml[core]

# Verify Python path
python3 -c "import sys; print(sys.path)"

# Test import
python3 -c "import codex_ml; print(codex_ml.__version__)"
```

### Issue: "pip check" reports conflicts

**Cause:** Incompatible package versions installed  
**Solution:**
```bash
# Clean install in new environment
python3.12 -m venv clean-env
source clean-env/bin/activate
pip install --upgrade pip
pip install codex-ml[core]  # Choose your profile
```

### Issue: Entry points not found ("codex-ml: command not found")

**Cause:** Virtual environment not activated or PATH misconfigured  
**Solution:**
```bash
# Activate virtual environment
source codex-env/bin/activate  # Linux/macOS
# or
codex-env\Scripts\activate  # Windows

# Verify installation
which codex-ml  # Should show path in venv

# Reinstall entry points
pip install --force-reinstall --no-cache-dir codex-ml[core]
```

### Issue: ImportError with ML dependencies

**Cause:** ML dependencies not installed (using core profile)  
**Solution:**
```bash
# Upgrade to runtime profile
pip install codex-ml[runtime]

# Or install specific missing package
pip install torch transformers
```

### Issue: Windows torch installation fails

**Cause:** Windows lacks native torch wheel support  
**Solution:**
```bash
# Option 1: Use CPU-only torch (faster to install)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Option 2: Use WSL2 (Windows Subsystem for Linux)
# Install WSL2, then install normally

# Option 3: Use core profile instead (doesn't require torch)
pip install codex-ml[core]
```

## Post-Installation Verification

### 1. Run Smoke Tests
```bash
pytest tests/smoke/test_install.py -v

# Expected output:
# test_install.py::TestInstallation::test_package_imports PASSED
# test_install.py::TestInstallation::test_core_profile_entry_points PASSED
# test_install.py::TestInstallation::test_dependency_versions PASSED
# ... (10+ tests total)
```

### 2. Check Dependencies
```bash
pip check

# Expected output:
# No broken requirements found.
```

### 3. Test Entry Points
```bash
# Core profile (should all work)
codex-ml --help
codex-ml-cli --help
codex-cli --help
codex-smoke --help
codex-import-ndjson --help

# Runtime profile (if installed)
codex-train --help
codex-eval --help

# Full profile (if installed)
codex-analyze --help
docs-inventory --help
```

### 4. Verify Package Version
```bash
python3 -c "import codex_ml; print(f'codex-ml {codex_ml.__version__}')"

# Expected: codex-ml 0.1.0
```

## Upgrading codex-ml

### From Previous Version
```bash
# Check current version
pip show codex-ml | grep Version

# Upgrade to latest
pip install --upgrade codex-ml[core]  # Specify your profile

# Verify upgrade
pip show codex-ml | grep Version
```

### Switching Profiles

```bash
# You can upgrade from core to runtime
pip install codex-ml[runtime]

# Or downgrade to lighter profile
pip uninstall codex-ml[runtime]
pip install codex-ml[core]
```

## Uninstalling codex-ml

```bash
pip uninstall codex-ml
```

## Getting Help

### Built-in Help
```bash
# All CLI tools support --help
codex-ml --help
codex-ml-cli --help
codex-cli --help
```

### Documentation
- **README:** Main project overview (README.md)
- **QUICKSTART_BY_PROFILE.md:** Profile-specific quick start guides
- **Source Code:** In `src/codex_ml/`
- **Tests:** Examples in `tests/`

### Reporting Issues
If you encounter problems:

1. **Check this guide** - Most common issues are covered in Troubleshooting
2. **Run smoke tests** - `pytest tests/smoke/test_install.py -v`
3. **Check pip errors** - `pip install codex-ml[core] -v` for verbose output
4. **Report with details:**
   - Python version: `python3 --version`
   - Pip version: `pip --version`
   - OS and version: `uname -a` (Linux/macOS) or `ver` (Windows)
   - Installation command used
   - Full error message

## Version History

### v0.1.0 (Current)
- Three-profile packaging strategy (core, runtime, full)
- 5 core entry points
- Full ML inference support in runtime profile
- Complete development toolkit in full profile

### Planned Improvements
- Profile-specific documentation
- Automated installation validation
- Wheel pre-builds for faster installation
- Docker images for each profile

## FAQ

**Q: Which profile should I use?**  
A: Start with `[core]` if unsure. It's the smallest and has the fewest dependencies. Upgrade to `[runtime]` when you need ML features, or `[full]` for development.

**Q: Can I mix profiles?**  
A: Not recommended. Install one profile at a time. To switch, uninstall and reinstall with a different profile.

**Q: Does the core profile work offline?**  
A: Yes! Once installed, all core functionality works offline. No internet required for runtime.

**Q: Can I install only specific entry points?**  
A: No, but you can selectively run only the tools you need. Entry points are lightweight aliases.

**Q: What's the minimum disk space needed?**  
A: ~50 MB for core profile, ~150 MB for runtime, ~500+ MB for full profile (including pip cache).

**Q: How do I verify all dependencies are correctly installed?**  
A: Run `pip check` and `pytest tests/smoke/test_install.py -v`

## Support & License

codex-ml is released under the MIT License. For support, see CONTRIBUTING.md.
