@copilot implement this comprehensive feature and capability completion plan for the **_codex_** repository. Address all **20 high-signal findings** and **15 capability gaps** systematically, with explicit error handling, test gates, and rollback procedures.

**Key Constraints:**
- ✅ Reproducible: Deterministic RNG, checksummed datasets
- ✅ Tested: Coverage ≥70%, gated on CI
- ✅ Auditable: Change log + error capture blocks

---

## 🗺️ Phase 1: Repository Understanding & Mapping

### Task 1.1: Parse Repository Structure
**Objective:** Understand the current codebase and identify implementation locations.

**Steps:**
1. Read and parse:
   - `README.md` (project overview)
   - `pyproject.toml` (dependencies, entry points)
   - `noxfile.py` (local test/lint sessions)
   - `configs/base/hydra.yaml` (base configuration)
   - `src/codex_ml/__init__.py` (public API)

2. Extract and document:
   - Module hierarchy (e.g., `src/codex_ml/training/`, `src/codex_ml/metrics/`)
   - Existing registries and factories (e.g., `common/registry.py`)
   - Hydra config structure and defaults

3. Identify stubs and TODOs:
   - Use regex: `grep -r "NotImplementedError\|TODO\|FIXME\|pass  #" src/`
   - List files and line numbers in a stub inventory

**Success Criteria:**
- Stub inventory file created at `.codex/stub_inventory.txt`
- Module hierarchy documented in `.codex/module_map.md`
- No missing files reported

---

### Task 1.2: Capability Gap Assessment
**Objective:** Map current capabilities against the audit table.

**Steps:**
1. For each capability in the audit table (Tokenization, ChatGPT Codex Modeling, etc.):
   - Verify if core module exists
   - Check for test coverage (`tests/test_<capability>.py`)
   - Note gaps listed in audit

2. Create a detailed capability checklist:
   - Capability name
   - Current status (Implemented / Partially Implemented / Not Implemented)
   - Existing artifacts (file paths)
   - Specific gaps (features/functions missing)

3. Cross-reference against the high-signal findings (items 1–20)

**Success Criteria:**
- Capability checklist written to `.codex/capability_checklist.md`
- All 20 high-signal findings cross-referenced
- Zero unexplained discrepancies

---

## 🔧 Phase 2: Feature Implementation (Atomically)

### ⭐ **HIGH PRIORITY: Missing dtype & device placement hooks**

#### Task 2.1: Add Dtype & Device Mapping Layer
**Objective:** Implement automatic dtype and device placement inference to fix precision mismatch between GPU and CPU.

**Files to Create/Modify:**

**`src/codex_ml/training/device_strategy.py` (NEW)**
```python
# Dtype and device placement utilities
import torch
from typing import Dict, Optional, Literal
from dataclasses import dataclass

@dataclass
class DeviceConfig:
    """Configuration for device and dtype placement."""
    device: str  # "cpu", "cuda", "mps"
    dtype: torch.dtype  # torch.float32, torch.float16, etc.
    mixed_precision: bool = False
    
    @classmethod
    def auto_detect(cls) -> "DeviceConfig":
        """Auto-detect optimal dtype/device based on system."""
        # Implementation: detect CUDA, set dtype accordingly
        pass
    
    def apply_to_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """Apply dtype and device to model."""
        pass
    
    def apply_to_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """Apply dtype and device to tensor."""
        pass

class DeviceMapper:
    """Registry for device/dtype strategies."""
    
    @staticmethod
    def register_strategy(name: str, config: DeviceConfig) -> None:
        pass
    
    @staticmethod
    def get_strategy(name: str) -> DeviceConfig:
        pass
```text

**`tests/training/test_device_strategy.py` (NEW)**
- Test auto-detect on CPU
- Test auto-detect on GPU (if available, skip if not)
- Test dtype conversion (float32 ↔ float16)
- Test device mismatch error handling

**Integration Points:**
- `src/codex_ml/training/unified_training.py`: Call `DeviceConfig.auto_detect()` on trainer init
- `src/codex_ml/interfaces/tokenizer_hf.py`: Ensure tokenizer outputs match model dtype

**Rollback Plan:**
- Revert to float32 fallback if device placement fails
- Add try/except around auto-detect

**Error Capture Block Template:**
```text
:::
Step: Task 2.1 - Add Dtype & Device Mapping
Error: [ERROR_TYPE]: [ERROR_MESSAGE]
File: [FILE_PATH]:[LINE_NUMBER]
Context: [BRIEF_CONTEXT]
Resolution: [HOW_FIXED_OR_DEFERRED]
:::
```text

---

### ⭐ **HIGH PRIORITY: Metrics API Completion**

#### Task 2.2: Implement Complete Metrics Registry & API
**Objective:** Complete missing metric classes (F1, BLEU, token accuracy, recall) and wire evaluation callbacks.

**Files to Create/Modify:**

**`src/codex_ml/metrics/metric_implementations.py` (NEW)**
```python
# Complete metric implementations
import torch
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

class MetricBase(ABC):
    """Abstract base for all metrics."""
    
    def __init__(self, name: str):
        self.name = name
        self.reset()
    
    @abstractmethod
    def update(self, predictions, targets) -> None:
        """Update metric state."""
        pass
    
    @abstractmethod
    def compute(self) -> Dict[str, float]:
        """Compute and return metric value."""
        pass
    
    def reset(self) -> None:
        """Reset metric state."""
        pass

class F1Score(MetricBase):
    """F1 Score implementation."""
    def __init__(self, num_classes: int = 2, average: str = "weighted"):
        super().__init__("f1_score")
        self.num_classes = num_classes
        self.average = average
    
    def update(self, predictions, targets) -> None:
        # Implementation
        pass
    
    def compute(self) -> Dict[str, float]:
        # Implementation
        pass

class BLEUScore(MetricBase):
    """BLEU Score for sequence generation."""
    def __init__(self, n_gram: int = 4):
        super().__init__("bleu_score")
        self.n_gram = n_gram
    
    def update(self, predictions, targets) -> None:
        pass
    
    def compute(self) -> Dict[str, float]:
        pass

class TokenAccuracy(MetricBase):
    """Token-level accuracy."""
    def __init__(self):
        super().__init__("token_accuracy")
    
    def update(self, predictions, targets) -> None:
        pass
    
    def compute(self) -> Dict[str, float]:
        pass

class RecallScore(MetricBase):
    """Recall metric."""
    def __init__(self, num_classes: int = 2, average: str = "weighted"):
        super().__init__("recall_score")
        self.num_classes = num_classes
        self.average = average
    
    def update(self, predictions, targets) -> None:
        pass
    
    def compute(self) -> Dict[str, float]:
        pass
```text

**`src/codex_ml/metrics/api.py` (REFACTOR)**
- Export all metric classes: `from .metric_implementations import *`
- Add `MetricRegistry` factory pattern
- Implement `summarize_ndjson_logs(log_file: str) -> Dict[str, float]`
- Add NDJSON validation

**`src/codex_ml/training/functional_training.py` (MODIFY)**
- Wire validation callbacks after training epoch
- Call metric update/compute in eval loop
- Log metrics to MLflow + console

**Tests:**
- `tests/metrics/test_f1_score.py`: Verify F1 on binary/multiclass
- `tests/metrics/test_bleu_score.py`: Test BLEU calculation
- `tests/metrics/test_token_accuracy.py`: Token-level matching
- `tests/metrics/test_recall_score.py`: Recall calculation
- `tests/metrics/test_ndjson_parsing.py`: Validate NDJSON log parsing

**Integration Checklist:**
- [ ] Metrics imported in `src/codex_ml/__init__.py`
- [ ] Metrics registered in `common/registry.py`
- [ ] Eval callback wired in functional_training.py
- [ ] Tests pass with `nox -s test`
- [ ] Coverage > 80% for metrics module

**Rollback Plan:**
- Keep legacy metrics format if NDJSON parsing fails
- Disable eval callback if metric compute errors

---

### ⭐ **HIGH PRIORITY: MLflow Offline Initialization Guard**

#### Task 2.3: Implement Guarded MLflow Initialization
**Objective:** Prevent hard crashes when MLflow unavailable; enable offline mode.

**Files to Create/Modify:**

**`src/codex_ml/logging/mlflow_guard.py` (NEW)**
```python
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def init_mlflow_safe(offline_mode: bool = None) -> bool:
    """Initialize MLflow with fallback for offline mode.
    
    Returns:
        bool: True if MLflow initialized, False if offline mode.
    """
    if offline_mode is None:
        offline_mode = os.environ.get("CODEX_OFFLINE_MODE", "0") == "1"
    
    if offline_mode:
        logger.info("[codex] MLflow disabled: offline mode active")
        return False
    
    try:
        import mlflow
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.start_run()
        logger.info("[codex] MLflow initialized (local backend)")
        return True
    except Exception as e:
        logger.warning(f"[codex] MLflow initialization failed: {e}")
        logger.info("[codex] Falling back to console logging")
        return False

def log_metric_safe(key: str, value: float, step: int = None) -> None:
    """Log metric safely; no-op if MLflow unavailable."""
    try:
        import mlflow
        mlflow.log_metric(key, value, step=step)
    except Exception:
        logger.debug(f"[codex] Could not log metric {key}={value}")

def log_params_safe(params: dict) -> None:
    """Log parameters safely; no-op if MLflow unavailable."""
    try:
        import mlflow
        mlflow.log_params(params)
    except Exception:
        logger.debug(f"[codex] Could not log params {params}")
```text

**`src/codex_ml/training/unified_training.py` (MODIFY)**
- Call `init_mlflow_safe()` at trainer init
- Replace all `mlflow.log_*` calls with `log_*_safe` wrappers

**`tests/logging/test_mlflow_guard.py` (NEW)**
- Test offline mode detection
- Test MLflow init success (mock)
- Test MLflow init failure fallback
- Test metric logging with MLflow unavailable

**Environment Variable:**
- `CODEX_OFFLINE_MODE=1`: Force offline mode
- Document in `docs/quickstart.md`

**Rollback Plan:**
- Unset `CODEX_OFFLINE_MODE`; requires MLflow

---

### ⭐ **HIGH PRIORITY: Deterministic RNG for Resume Checkpoints**

#### Task 2.4: Implement Reproducible RNG State Capture
**Objective:** Ensure resumed runs produce deterministic results by capturing and restoring RNG state.

**Files to Create/Modify:**

**`src/codex_ml/training/rng_checkpoint.py` (NEW)**
```python
import torch
import random
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any

class RNGState:
    """Capture and restore RNG state across backends."""
    
    def __init__(self):
        self.torch_state = None
        self.numpy_state = None
        self.python_state = None
    
    def capture(self) -> None:
        """Capture current RNG state from all backends."""
        self.torch_state = torch.get_rng_state().cpu().tolist()
        self.numpy_state = np.random.get_state()
        self.python_state = random.getstate()
    
    def restore(self) -> None:
        """Restore RNG state to all backends."""
        torch.set_rng_state(torch.tensor(self.torch_state))
        # numpy state restoration...
        # python state restoration...
    
    def save_to_file(self, path: Path) -> None:
        """Save RNG state to checkpoint file."""
        data = {
            "torch_state": self.torch_state,
            "numpy_state": None,  # Serialize numpy state
            "python_state": None,  # Serialize python state
        }
        with open(path, "w") as f:
            json.dump(data, f)
    
    @classmethod
    def load_from_file(cls, path: Path) -> "RNGState":
        """Load RNG state from checkpoint file."""
        with open(path) as f:
            data = json.load(f)
        state = cls()
        state.torch_state = data["torch_state"]
        # Load numpy/python state...
        return state

def set_seed(seed: int) -> None:
    """Set seed for all backends."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
```text

**`src/codex_ml/training/unified_training.py` (MODIFY)**
- On checkpoint save: `rng_state.capture()` and save to file
- On checkpoint load/resume: `rng_state.restore()` from file

**`tests/training/test_rng_reproducibility.py` (NEW)**
- Test RNG capture/restore produces identical tensors
- Test resumed training produces identical loss curves
- Test multirun with different seeds produces different results

**Validation Test:**
```bash
# Run 1: Complete training
python -m codex.train config=base seed=42

# Run 2: Resume from checkpoint (should produce identical results)
python -m codex.train config=base seed=42 resume_from=outputs/run_1/checkpoint.pt

# Compare loss logs (should be identical)
diff outputs/run_1/metrics.ndjson outputs/run_2/metrics.ndjson
```text

**Rollback Plan:**
- If RNG restore fails, log warning and continue (non-deterministic)
- Disable resume if RNG state file corrupted

---

### **Hydra Sweep Configuration**

#### Task 2.5: Enable Hydra Multirun for Experiment Sweeps
**Objective:** Add sweep templates to enable local experiment sweeps.

**Files to Create/Modify:**

**`configs/base/hydra_sweep.yaml` (NEW)**
```yaml
defaults:
  - override hydra/launcher: basic
  - override hydra/sweeper: basic

hydra:
  sweep:
    dir: outputs/${now:%Y-%m-%d}
    subdir: ${hydra.job.num}
  launcher:
    _target_: hydra._internal.BasicLauncher
  sweeper:
    _target_: hydra._internal.BasicSweeper
```text

**`configs/experiments/sweep_template.yaml` (NEW)**
```yaml
# Template for experiment sweeps
defaults:
  - /base/hydra_sweep

# Example sweep parameters
lr: 1e-4
batch_size: 32
num_epochs: 10
```text

**CLI Usage:**
```bash
# Single run
python -m codex.train config=base

# Sweep multiple hyperparameters
python -m codex.train --multirun config=experiments/sweep_template lr=1e-3,1e-4,1e-5 batch_size=16,32,64
```text

**Tests:**
- `tests/config/test_hydra_sweep.py`: Verify sweep config loads

**Rollback Plan:**
- Revert to `base/hydra.yaml` on config parse error

---

### **Dataset Schema Validation**

#### Task 2.6: Integrate Dataset Schema Validator CLI
**Objective:** Add CLI tool to validate dataset manifests before training.

**Files to Create/Modify:**

**`src/codex_ml/data/validator.py` (NEW)**
```python
import json
from pathlib import Path
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

class DatasetValidator:
    """Validate dataset manifests against schema."""
    
    SCHEMA_PATH = Path(__file__).parent.parent.parent / "configs/schemas/dataset_manifest.schema.json"
    
    @classmethod
    def validate_manifest(cls, manifest_path: Path) -> bool:
        """Validate dataset manifest file."""
        with open(cls.SCHEMA_PATH) as f:
            schema = json.load(f)
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        try:
            validate(instance=manifest, schema=schema)
            logger.info(f"✓ Manifest valid: {manifest_path}")
            return True
        except ValidationError as e:
            logger.error(f"✗ Manifest invalid: {e.message}")
            return False
    
    @classmethod
    def validate_splits(cls, manifest_path: Path) -> bool:
        """Validate that all referenced splits exist."""
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        base_path = manifest_path.parent
        for split_info in manifest.get("splits", []):
            split_path = base_path / split_info["path"]
            if not split_path.exists():
                logger.error(f"✗ Split file missing: {split_path}")
                return False
        
        logger.info("✓ All splits found")
        return True
```text

**`scripts/validate_dataset.py` (NEW)**
```python
import argparse
from pathlib import Path
from src.codex_ml.data.validator import DatasetValidator

def main():
    parser = argparse.ArgumentParser("Validate dataset manifests")
    parser.add_argument("manifest", type=Path, help="Path to dataset manifest JSON")
    parser.add_argument("--check-splits", action="store_true", help="Verify split files exist")
    args = parser.parse_args()
    
    valid = DatasetValidator.validate_manifest(args.manifest)
    if args.check_splits:
        valid = valid and DatasetValidator.validate_splits(args.manifest)
    
    exit(0 if valid else 1)

if __name__ == "__main__":
    main()
```text

**CLI Usage:**
```bash
python scripts/validate_dataset.py data/dataset_manifest.json --check-splits
```text

**Tests:**
- `tests/data/test_validator.py`: Valid/invalid manifests

---

### **Security & Pre-commit Hooks**

#### Task 2.7: Add Bandit & Secretlint Security Scanning
**Objective:** Integrate lightweight security scanning into pre-commit hooks.

**Files to Create/Modify:**

**`.pre-commit-config.yaml` (MODIFY)**
```yaml
repos:
  # ... existing hooks ...
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['--configfile=.bandit.yaml']
        exclude: ^tests/
  
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```text

**`.bandit.yaml` (NEW)**
```yaml
# Bandit security scanning config
exclude_dirs:
  - /tests
  - /notebooks
skips:
  - B101  # assert_used (OK in tests)
```text

**`noxfile.py` (MODIFY)**
- Add session: `nox -s security` to run bandit + gitleaks

**Tests:**
- `tests/security/test_no_hardcoded_secrets.py`: Scan codebase

---

### **Coverage Enforcement**

#### Task 2.8: Enforce Test Coverage Gates
**Objective:** Require ≥70% coverage with automated report generation.

**Files to Create/Modify:**

**`noxfile.py` (MODIFY)**
```python
@nox.session
def test(session):
    """Run unit tests with coverage."""
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
        "-v",
        external=True,
    )
```text

**`pytest.ini` (MODIFY)**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    regression: Regression tests
```text

**Workflow:** Coverage report auto-generated and committed to `.codex/coverage/`

---

### **Unified Task Runner**

#### Task 2.9: Create codex_exec CLI for Task Orchestration
**Objective:** Provide single entry point to orchestrate all Codex tasks.

**Files to Create/Modify:**

**`src/codex_ml/exec/codex_exec.py` (NEW)**
```python
import argparse
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class CodexExecutor:
    """Unified task runner for Codex pipeline."""
    
    TASKS = {
        "validate-dataset": "Validate dataset manifest",
        "train": "Run training pipeline",
        "evaluate": "Run evaluation",
        "export": "Export model",
        "audit": "Run codebase audit",
    }
    
    def __init__(self, offline_mode: bool = False):
        self.offline_mode = offline_mode
    
    def validate_dataset(self, manifest_path: Path) -> bool:
        """Task: validate dataset."""
        from codex_ml.data.validator import DatasetValidator
        return DatasetValidator.validate_manifest(manifest_path)
    
    def train(self, config_name: str, **kwargs) -> bool:
        """Task: training."""
        logger.info(f"Starting training with config={config_name}")
        # Orchestrate training
        return True
    
    def evaluate(self, checkpoint_path: Path) -> bool:
        """Task: evaluation."""
        logger.info(f"Evaluating checkpoint: {checkpoint_path}")
        # Orchestrate evaluation
        return True
    
    def run_task(self, task_name: str, **kwargs) -> bool:
        """Execute a named task."""
        if task_name not in self.TASKS:
            logger.error(f"Unknown task: {task_name}")
            return False
        
        method = getattr(self, task_name.replace("-", "_"))
        return method(**kwargs)

def main():
    parser = argparse.ArgumentParser("Codex Unified Executor")
    parser.add_argument("task", choices=CodexExecutor.TASKS.keys())
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--config", type=str, help="Config name for training")
    parser.add_argument("--manifest", type=Path, help="Dataset manifest path")
    args = parser.parse_args()
    
    executor = CodexExecutor(offline_mode=args.offline)
    success = executor.run_task(args.task, config_name=args.config, manifest_path=args.manifest)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
```text

**CLI Usage:**
```bash
python -m codex_ml.exec.codex_exec validate-dataset --manifest data/manifest.json
python -m codex_ml.exec.codex_exec train --config base --offline
```text

---

## 🧪 Phase 3: Testing & Validation Gates

### Task 3.1: Run Local Test Gates
**Objective:** Verify all implementations pass offline tests.

**Commands:**
```bash
# Lint
nox -s lint

# Unit tests
nox -s test

# Security scan
nox -s security

# Coverage report
pytest --cov=src --cov-report=html

# Full gate
nox -s gates
```text

**Success Criteria:**
- All tests pass
- Coverage ≥70%
- No bandit/secret warnings
- No import errors

---

### Task 3.2: Generate Test Coverage Report
**Objective:** Create automated HTML coverage report.

**Output:** `htmlcov/index.html`

**Review:**
- Identify untested modules
- Add tests for gaps >10%

---

### Task 3.3: Verify Reproducibility
**Objective:** Confirm deterministic training and eval.

**Test:**
```bash
# Run 1
python -m codex.train config=base seed=42 num_epochs=2

# Run 2 (same seed)
python -m codex.train config=base seed=42 num_epochs=2

# Compare loss curves
diff outputs/run_1/metrics.ndjson outputs/run_2/metrics.ndjson
# Should be identical
```text

---

## 📝 Phase 4: Documentation & Change Log

### Task 4.1: Update Documentation
**Objective:** Reflect new features in docs.

**Files to Update:**
- `docs/quickstart.md`: Add offline mode, sweep, validation examples
- `docs/repro.md`: Document RNG checkpoint, seed management
- `docs/metrics.md`: Document new metrics (F1, BLEU, recall)
- `docs/config.md`: Document sweep templates
- `.codex/README.md`: Link to new modules

---

### Task 4.2: Create Change Log
**Objective:** Document all changes with rollback instructions.

**File:** `CHANGES.md`

**Format:**
```markdown
## [2025-11-09] Feature Batch 1: Metrics & MLflow Guard

### Added
- ✅ Metrics API completion: F1, BLEU, token accuracy, recall
- ✅ Guarded MLflow initialization for offline mode
- ✅ Deterministic RNG checkpoint/restore
- ✅ Dataset schema validator CLI
- ✅ Hydra multirun sweep support

### Modified
- `src/codex_ml/training/unified_training.py`: Wired eval callbacks
- `.pre-commit-config.yaml`: Added bandit security scan
- `noxfile.py`: Added coverage gate (≥70%)

### Rollback Instructions

#### Rollback Metrics API:
```bash
git checkout HEAD~1 -- src/codex_ml/metrics/
git checkout HEAD~1 -- tests/metrics/
```text

#### Rollback MLflow Guard:
```bash
rm src/codex_ml/logging/mlflow_guard.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
unset CODEX_OFFLINE_MODE
```text

#### Rollback RNG Checkpoint:
```bash
rm src/codex_ml/training/rng_checkpoint.py
git checkout HEAD~1 -- src/codex_ml/training/unified_training.py
```text

### Test Results
- Coverage: 72% (+5%)
- Tests: 145 passed, 0 failed
- Security: 0 issues (bandit + gitleaks)

---

## ❌ Phase 5: Error Capture & Resolution

### Error Capture Template
Use this format for any encountered errors:

```text
> Step: [TASK_NUMBER]: [TASK_NAME]
> Timestamp: [ISO_8601_UTC]
> Error: [ERROR_TYPE]: [ERROR_MESSAGE]
> File: [FILE_PATH]:[LINE_NUMBER]
> Context: [BRIEF_DESCRIPTION_OF_WHAT_WAS_ATTEMPTED]
> Severity: [CRITICAL|HIGH|MEDIUM|LOW]
> Resolution: [HOW_FIXED_OR_REASON_DEFERRED]
> Rollback: [INSTRUCTION_TO_ROLLBACK_IF_APPLICABLE]
```text

### Common Issues & Resolutions

| Issue | Root Cause | Resolution |
|-------|-----------|-----------|
| `ModuleNotFoundError: No module named 'mlflow'` | MLflow not installed | Install: `pip install mlflow` or defer to offline mode |
| `CUDA out of memory` | Model too large for GPU | Fall back to CPU; add gradient checkpointing |
| `Schema validation fails` | Manifest format mismatch | Regenerate manifest using validator; check schema version |
| `RNG restore fails` | Incompatible state format | Skip restore; log warning; continue non-deterministic |
| `Bandit security warning` | Hardcoded credential or SQL injection | Refactor to use environment variables; review code |

---

## ✅ Phase 6: Finalization & Sign-Off

### Pre-Commit Checklist

- [ ] All 9 main tasks completed
- [ ] All tests passing: `nox -s gates`
- [ ] Coverage ≥70%: `pytest --cov-fail-under=70`
- [ ] Security scan clean: `nox -s security`
- [ ] Documentation updated
- [ ] Change log entries complete
- [ ] Error capture blocks (if any) documented
- [ ] Rollback instructions validated
- [ ] No uncommitted changes in `src/` except new files
- [ ] `git log --oneline` shows atomic commits

### Final Validation

```bash
# Full offline test suite
nox -s lint test security

# Generate coverage HTML
pytest --cov=src --cov-report=html

# Verify reproducibility
python scripts/test_reproducibility.sh

# Create audit report
python .codex/generate_audit_report.py > .codex/AUDIT_REPORT_[DATE].md
```text

### Commit & Tag (Local Only)

```bash
# Commit all changes
git add src/ tests/ configs/ scripts/ docs/ .pre-commit-config.yaml noxfile.py

# Atomic commit
git commit -m "feat: implement metrics API, MLflow guard, RNG checkpoint, sweep templates, validation CLI, security scanning, coverage gates, device strategy, codex_exec"

# Tag
git tag -a "v0.2.0-codex-completion" -m "Codex capability audit completion: 20/20 findings addressed"

```text

---

## 📊 Success Metrics

| Metric | Target | Current → After |
|--------|--------|-----------------|
| Capability Implementation | 20/20 findings | 0/20 → 20/20 ✓ |
| Test Coverage | ≥70% | <70% → ≥72% ✓ |
| Metrics Completeness | 100% | ~40% → 100% ✓ |
| Security Scan | 0 issues | N/A → 0 ✓ |
| Reproducibility | Deterministic | Partial → Full ✓ |
| Documentation | Current | Outdated → Up-to-date ✓ |

---

## 🛠️ Implementation Tool: `codex_update.py`

Provided separately as executable script to automate:
1. AST-based stub detection
2. Patch application via templates
3. Test generation
4. Error capture
5. Change log updates

Execute:
```bash
python .codex/codex_update.py --phase 2 --task metrics --auto-patch --run-tests
```text

---

## 📞 Support & Escalation

For issues or questions:
1. Check error capture blocks in this prompt
2. Review rollback instructions in `CHANGES.md`
3. Run `nox -s gates` to validate state
4. Inspect logs in `.codex/logs/`

------

# 📍 *codex*: Status Update (2025‑11‑09) 

## 1. Repo Map

The `_codex_` repository is an offline‑first machine‑learning environment designed to produce reproducible training runs without remote services.  The top‑level directories include:

| Directory         | Key contents                                                                                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/codex_ml`    | Core library with modules for training (functional and HF‑Trainer loops), unified orchestration, strategy wrappers, data handling, metrics, and registries. |
| `configs/`        | Hydra YAMLs for base configs, experiments, schemas, and defaults.                                                                                           |
| `scripts/`        | Utility scripts for running Codex tasks and pipelines.                                                                                                      |
| `docs/`           | Documentation for reproducibility, metrics, control surface, and audit reports.                                                                             |
| `notebooks/`      | Example notebooks for GPU training and validation.                                                                                                          |
| `requirements/`   | Dependency pinning and environment setup.                                                                                                                   |
| `tools/`          | Execution tools, interface application hooks, and audit helpers.                                                                                            |
| `.codex/notes/`   | Internal audit and codebase notes.                                                                                                                          |
| `_codex_reports/` | Raw audit reports and verification logs.                                                                                                                    |

**Stub and placeholder detection:**

* `tools/apply_interfaces.py` raises `NotImplementedError`
* `scripts/run_codex_tasks.py` contains TODO stubs for unfinished execution paths
* `docs/gaps_report.md` lists incomplete or deferred modules (metrics extensions, dataset schema validation)
* `services/ita/app/hygiene.py` flagged as partially complete (testing harness incomplete)
* `.codex/notes/CODEBASE_AUDIT.md` explicitly marks pending security reviews

## 2. Capability Audit Table

| Capability                   | Status                | Existing Artifacts                                                                                 | Gaps                                         | Risks                                                          | Minimal Patch Plan                                          | Rollback Plan                            |
| ---------------------------- | --------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------- |
| **Tokenization**             | Implemented           | `src/tokenization/train_tokenizer.py`, `src/tokenizer/fast_tokenizer.py`                           | HF integration hooks minimal                 | Inconsistent BPE vs SP config; risk of incompatible model load | Add auto‑detection for tokenizer type; unify vocab registry | Restore previous HF config checkpoint    |
| **ChatGPT Codex Modeling**   | Partially Implemented | `src/codex_ml/interfaces/tokenizer_hf.py`, `src/codex_ml/training/engine.py`                       | Missing dtype & PEFT hooks                   | Risk of improper device allocation                             | Add dtype map + PEFT wrapper                                | Toggle fallback to float32 on CUDA fail  |
| **Training Engine**          | Partially Implemented | `training/unified_training.py`, `training/functional_training.py`, `training/engine_hf_trainer.py` | HF integration partially wired; eval missing | Loss scaling and optimizer drift                               | Add unified trainer registry + eval callback                | Disable optimizer resume if NaN detected |
| **Configuration Management** | Implemented           | `configs/base/hydra.yaml`, CLI: `hydra_entry.py`                                                   | Missing experiment sweep template            | Hard‑coded experiment paths                                    | Add sweep defaults; integrate `hydra.multirun`              | Revert to base.yaml on config fail       |
| **Evaluation & Metrics**     | Partially Implemented | `metrics/api.py`, `metrics/registry.py`, `docs/metrics.md`                                         | Missing metric classes (e.g. F1, recall)     | Unverified NDJSON log parsing                                  | Add metrics factory pattern + NDJSON validation             | Keep legacy metrics format               |
| **Logging & Monitoring**     | Partially Implemented | `monitoring/system_metrics.py`, MLflow hooks                                                       | MLflow off by default                        | Training invisibility in offline mode                          | Add local MLflow server stub                                | Disable tracking if disk full            |
| **Checkpointing & Resume**   | Implemented           | `training/unified_training.py`                                                                     | Resume logic not tested with RNG             | Determinism loss                                               | Add unit test comparing RNG snapshots                       | Keep prior RNG seed if resume fails      |
| **Data Handling**            | Implemented           | `data/hf_datasets.py`, `data/dataset_wrapper.py`, `configs/schemas/dataset_manifest.schema.json`   | None major                                   | I/O latency under streaming                                    | Cache splits pre‑load                                       | Clear cache on corruption                |
| **Security & Safety**        | Partially Implemented | Dependency pinning, `.pre‑commit‑config`, `codex.mk`                                               | No secrets scanning                          | Supply chain risk                                              | Add `bandit` & secretlint pre‑commit hooks                  | Disable scan job if offline              |
| **Internal CI/Test**         | Implemented (local)   | `noxfile.py`, `pytest.ini`                                                                         | Coverage < 80%                               | Missed regressions                                             | Enforce coverage gate in `nox`                              | Revert to last passing commit            |
| **Deployment**               | Implemented           | `Dockerfile`, `pyproject.toml`                                                                     | None critical                                | Build cache inconsistency                                      | Add build args for base image                               | Rebuild pinned base image                |
| **Documentation & Examples** | Partially Implemented | `docs/repro.md`, `docs/control_surface.md`, notebooks                                              | Missing diagrams, outdated quickstart        | Reduced onboarding                                             | Auto‑generate via `mkdocs`                                  | Keep last version in `/archive`          |
| **Experiment Tracking**      | Partially Implemented | MLflow local mode                                                                                  | W&B offline incomplete                       | Experiment metadata loss                                       | Add `experiment_logger.py`                                  | Reuse previous `run_id`                  |
| **Extensibility**            | Implemented           | `common/registry.py`                                                                               | None                                         | Low                                                            | n/a                                                         | n/a                                      |

## 3. High‑Signal Findings

1. Missing dtype and device placement hooks cause precision mismatch between GPU and CPU in hybrid runs.
2. Metrics API partially wired: F1, BLEU, and token accuracy incomplete.
3. `functional_training.py` does not call validation callbacks, breaking metric aggregation.
4. Dataset schema validation lacks integration in the Hydra pipeline.
5. MLflow logger disabled by default; no offline substitute.
6. Bandit and secret scanning missing.
7. Docs need update to reflect unified training.
8. Deterministic RNG not enforced across resume checkpoints.
9. `hydra.multirun` not yet configured for experiment sweeps.
10. `pytest.ini` missing regression test categorization.
11. No GPU stress test in notebooks.
12. Control surface diagrams outdated.
13. Coverage <80%; no automatic report generation.
14. Gaps between `unified_training` and `engine_hf_trainer` abstractions.
15. Dataset caching inconsistent under concurrent loads.
16. Missing safety net for partial resume.
17. Offline MLflow registry absent.
18. Missing dataset manifest validator CLI.
19. Missing system metrics export to JSON.
20. Need a unified task runner (`codex_exec`) to orchestrate.

## 4. Atomic Diffs (Examples)

**Example 1:** Guarded MLflow Initialization

```diff
@@ -1,6 +1,11 @@
 import mlflow
+import os
 try:
     mlflow.start_run()
 except Exception:
-    pass
+    if os.environ.get("CODEX_OFFLINE_MODE", "0") == "1":
+        print("[codex] MLflow disabled: offline mode")
+    else:
+        raise
```text

**Why:** Prevents hard crash when MLflow unavailable.
**Risk:** Missed metrics in offline mode.
**Rollback:** Restore prior import block.
**Tests/docs:** Add offline test in `test_logging.py`.

**Example 2:** Deterministic RNG Resume

```diff
@@ def resume_training(...):
-   rng_state = None
+   import torch
+   rng_state = torch.get_rng_state()
+   torch.manual_seed(int(rng_state.sum()) % 2**32)
```text

**Why:** Ensures resumed runs are deterministic.
**Risk:** Minor perf degradation.
**Rollback:** Disable seed reset.
**Tests/docs:** `test_reproducibility.py`.

**Example 3:** Hydra Sweep Config

```diff
 defaults:
-  - override hydra/job_logging: disabled
+  - override hydra/sweeper: basic
+hydra:
+  sweep:
+    dir: outputs/${now:%Y-%m-%d_%H-%M-%S}
+    subdir: ${hydra.job.name}
```text

**Why:** Enables local experiment sweeps.
**Risk:** Disk usage.
**Rollback:** Disable sweep override.
**Tests/docs:** `test_config_hydra.py`.

## 5. Local Tests & Gates

Offline‑only test gates:

```bash
nox -s lint
nox -s test
pytest --maxfail=1 --disable-warnings -q
pytest --cov=src --cov-report=term-missing
```text

**ML Test Score Categories:**

* **Data:** schema integrity, deterministic splits
* **Model:** loss curve regression, parameter freeze check
* **Infrastructure:** offline MLflow, Hydra CLI launch
* **Regression:** checkpoint replay
* **Performance:** GPU/CPU timing parity

## 6. Reproducibility Checklist

| Item                | Status | Notes                           |
| ------------------- | ------ | ------------------------------- |
| Random seeds fixed  | ✅      | via `torch.manual_seed` wrapper |
| Environment capture | ✅      | `docs/repro.md` guidelines      |
| Dataset manifest    | ✅      | JSON schema validated           |
| Code versioning     | ✅      | via git commit tagging          |
| Results determinism | ⚠️     | RNG restore partial             |
| Offline rebuild     | ✅      | Docker reproducibility verified |

## 7. Deferred Items

| Deferred Component       | Reason                    | Future Plan                       |
| ------------------------ | ------------------------- | --------------------------------- |
| HF Trainer integration   | Complexity & low priority | Merge after PEFT validation       |
| W&B Offline mode         | Dependency overhead       | Re‑enable via local proxy         |
| GPU test notebook        | CUDA resource contention  | Automate nightly offline test     |
| Security scan automation | Bandit dependency         | Integrate lightweight static scan |

## 8. Error Capture Blocks

> Question for ChatGPT @codex 2025‑11‑09:
> While performing [STEP_4: Fetch Hydra YAMLs], encountered the following error:
> `Missing sweep directory config`.
> Context: The Hydra config failed to resolve default overrides.
> What are the possible causes, and how can this be resolved while preserving intended functionality?

## Codex‑Ready Task Sequence (YAML)
Below is a structured plan to implement the missing features and improvements identified above. It outlines sequential phases with explicit error capture and pruning rules. The plan is written in YAML so it can be supplied to chatgpt-codex via the --prompt-file option. Replace example tasks with your actual tasks as needed.

```yaml
**Codex-ready Task Sequence**

# This plan directs Codex through phases to close gaps in the `_codex_` repository.

1. Preparation:
  - Read and parse `README.md`, `noxfile.py`, `pyproject.toml`, and `configs/base/hydra.yaml` to understand current capabilities.
  - Identify stubs and missing features (e.g., empty `metrics/api.py`).
  - Set up local environment variables (`CODEX_OFFLINE=1`) to prevent external calls.

2. Search & Mapping:
  - Recursively scan `src/codex_ml` and `configs` for modules related to metrics, checkpointing, logging, security, and LoRA.  Use Python `ast` to detect functions/classes without implementations or containing `pass`/`TODO`.
  - Compare discovered modules against the capability audit table; map which modules implement which capability.
  - For metrics, locate `metrics/registry.py`, `metrics_base.py`, and CLI helpers; confirm that `metrics/api.py` is stubbed.

3. Best‑Effort Construction:
  - Implement missing `codex_ml.metrics.api` by re‑exporting registry functions and adding a helper to summarise NDJSON logs into CSV/SQLite; write associated tests in `tests/metrics/test_api.py`.
  - Enhance checkpointing by adding a manifest file capturing commit hash, dataset checksum, environment variables (filtered for secrets) and saving it alongside checkpoint files.
  - Extend Hydra configuration by adding new config groups (`train/lora.yaml`, `train/rlhf.yaml`) that expose LoRA/PEFT and RLHF parameters with sensible defaults.
  - Integrate `detect‑secrets` into `.pre-commit-config.yaml` and update `nox` precommit session to run it.
  - Add coverage enforcement in `nox` tests session (`--cov=src --cov-report=xml --cov-fail-under=70`).  Adjust threshold if necessary.

4. Controlled Pruning:
  - After implementing each feature, verify through unit tests (`nox -s tests`) and gating (`nox -s gates`).
  - If a feature cannot be implemented due to missing dependencies or complexity (e.g., RLHF reward model), document the rationale and prune it from the code while keeping the config stub for future work.
  - Maintain a change log (`CHANGES.md`) recording added features and pruned items.

5. Error Capture:
  - For any step that triggers an exception (e.g., missing module, import error), record an error capture block with timestamp and context, following the specified format.  Include at least one error block if you encounter an unhandled error during implementation.

6. Finalisation:
  - Run all `nox` sessions (`tests`, `gates`, `docs_build`, `precommit`) to ensure the repository passes offline gating.
  - Generate an updated status report and capability audit (similar to this audit) to confirm improvements.
  - Commit changes locally; do not push to remote or trigger GitHub Actions.  Provide rollback instructions in `CHANGES.md` for each feature.

Additional Deliverable:

- Provide an executable script `codex_update.py` that automates the scanning, implementation (via templates), test generation, and error capture described above.  The script should:
  1. Parse the repository tree.
  2. Detect stubs and missing features using AST analysis.
  3. Apply patches (using diff templates or simple file writes) to implement features.
  4. Write tests for new modules.
  5. Run `pytest` and capture failures, formatting them into error capture blocks.
  6. Update `CHANGES.md` with a summary of actions.
```text

```