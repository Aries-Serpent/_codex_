# 🔗 BLOCKING ISSUE P1: TRAINING/ML CIRCULAR DEPENDENCIES
**Protocol Extraction & Lazy Import Brief - WEEK 3-4**

**Status**: READY FOR PHASE 3 EXECUTION  
**Authority**: @mbaetiong standing approval  
**Timeline**: 2-3 weeks  
**Target Start**: After 1 week of P0 progress (2026-07-19)  
**Parallel With**: P0 fix (after P0 week 1 milestone)

---

## 🎯 Blocker Overview

**Current State**:
- codex.training module has 15+ circular dependencies with codex_ml submodules
- Prevents clean separation between training pipeline and ML inference
- Blocks Phase 3 (ML package) deployment
- Creates runtime import order dependencies (fragile)

**Impact**:
- ML package cannot isolate training from inference
- Training functionality tightly coupled to specific ML model implementations
- No ability to swap training backends (PyTorch ↔ TensorFlow, etc.)
- Version locking between training and inference components

**Root Cause Pattern**:
```
codex.training.trainer → imports codex_ml.models (model classes)
codex_ml.models → imports codex.training.losses (loss functions)
codex_ml.models → imports codex.training.callbacks (callbacks)
                     
Result: Circular import chain, fragile import ordering required
```

**Solution Approach**: Protocol Extraction + Lazy Loading
- Extract training protocols (abstract interfaces)
- Decouple concrete implementations via protocols
- Use lazy imports for runtime loading
- Enable plugin-style training backend injection

---

## 📊 Current Circular Dependency Analysis

### Dependency Cycles (15+ instances)

**Primary Cycles**:

1. **Model Training Cycle**:
   ```
   codex.training.trainer
     → imports codex_ml.models.ResNet (concrete model)
       → imports codex.training.losses.CrossEntropy
         → imports codex_ml.models.forward_hook (model-specific)
   Result: Cycle with import order dependency
   ```

2. **Callback Cycle**:
   ```
   codex.training.callbacks
     → imports codex_ml.metrics.MetricComputer
       → imports codex.training.checkpointer.CheckpointCallback
   Result: Circular dependency on checkpoint logic
   ```

3. **Optimizer Cycle**:
   ```
   codex_ml.training.optimizer_factory
     → imports codex.training.schedules.LRSchedule
       → imports codex_ml.training.warmup_schedule (concrete impl)
   Result: Scheduler implementation leaks into protocol
   ```

4. **Data Pipeline Cycle**:
   ```
   codex_ml.data.loader
     → imports codex.training.transforms (data transformations)
       → imports codex_ml.data.augmentation (ML-specific augmentation)
   Result: Circular augmentation pipeline
   ```

5. **Safety Integration Cycle** (14+ more):
   ```
   codex_ml.safety.adversarial
     → imports codex.training.defense_mechanisms
       → imports codex_ml.safety.detector.load_model()
   [... similar patterns in 14 other cycles]
   ```

### High-Risk Import Chains

**File**: `codex/training/__init__.py`
```python
# This single import pulls in 15+ circular dependencies
from codex_ml.models import (
    ResNet, LSTM, Transformer,
    ModelFactory, ModelRegistry  # ← These import back to training
)
```

**Files with Circular Imports** (15-20 total):
- codex/training/trainer.py (7 cycles)
- codex/training/callbacks.py (4 cycles)
- codex/training/losses.py (3 cycles)
- codex_ml/models/__init__.py (8 cycles back to training)
- codex_ml/training/optimizer_factory.py (2 cycles)
- codex_ml/data/loader.py (2 cycles)
- codex_ml/safety/adversarial.py (2 cycles)

---

## ✅ Solution Architecture

### Step 1: Extract Training Protocols

**File**: `codex/training/protocols.py` (new)

```python
"""
Protocol definitions for training - zero concrete implementations.
This module has ZERO dependencies on codex_ml.
Used for dependency inversion and plugin injection.
"""

from typing import Protocol, Callable, Any, Dict, List, Optional, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class TrainingBatch:
    """Input batch type - pure data, no ML logic."""
    inputs: Any
    targets: Any
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TrainingMetrics:
    """Output metrics - pure data, no ML logic."""
    loss: float
    accuracy: float
    custom: Dict[str, float]


class Model(Protocol):
    """Protocol for trainable models - implementations inject concrete models."""
    
    def __call__(self, batch: TrainingBatch) -> Any:
        """Forward pass (implemented by concrete model)."""
        ...
    
    def parameters(self) -> List[Any]:
        """Get trainable parameters."""
        ...
    
    def to(self, device: str) -> None:
        """Move model to device."""
        ...


class Loss(Protocol):
    """Protocol for loss functions - no concrete impl."""
    
    def __call__(self, predictions: Any, targets: Any) -> float:
        """Compute loss."""
        ...


class Optimizer(Protocol):
    """Protocol for optimizers - no concrete impl."""
    
    def zero_grad(self) -> None:
        """Zero gradients."""
        ...
    
    def step(self) -> None:
        """Update parameters."""
        ...


class Callback(Protocol):
    """Protocol for training callbacks."""
    
    def on_train_start(self) -> None: ...
    def on_epoch_start(self, epoch: int) -> None: ...
    def on_batch_end(self, batch_idx: int, metrics: TrainingMetrics) -> None: ...
    def on_epoch_end(self, epoch: int, metrics: TrainingMetrics) -> None: ...


class Trainer(ABC):
    """Abstract trainer - implementations can use any backend."""
    
    @abstractmethod
    def fit(self, epochs: int, callbacks: Optional[List[Callback]] = None) -> None:
        """Train model for N epochs."""
        ...
    
    @abstractmethod
    def evaluate(self) -> TrainingMetrics:
        """Evaluate on validation set."""
        ...


# Factory types for runtime injection
ModelFactory = Callable[[str], Model]
LossFactory = Callable[[str], Loss]
OptimizerFactory = Callable[[str], Optimizer]
TrainerFactory = Callable[[Model, Loss, Optimizer], Trainer]
```

**Properties**:
- ✅ Zero concrete implementations (pure protocols)
- ✅ Zero imports from codex_ml
- ✅ Can be imported in isolation
- ✅ Enables dependency injection pattern

---

### Step 2: Update Trainer Implementation

**File**: `codex/training/trainer.py`

**Before** (Circular):
```python
from codex_ml.models import ResNet  # ← Circular import

class StandardTrainer:
    def __init__(self, model):
        self.model = model  # Concrete type ResNet
```

**After** (Protocol-based):
```python
from codex.training.protocols import Model, Loss, Optimizer, Trainer, TrainingBatch, TrainingMetrics

class StandardTrainer(Trainer):
    def __init__(self, 
                 model: Model,          # Protocol, not concrete
                 loss: Loss,            # Protocol, not concrete
                 optimizer: Optimizer): # Protocol, not concrete
        self.model = model
        self.loss = loss
        self.optimizer = optimizer
    
    def fit(self, epochs: int, callbacks=None) -> None:
        for epoch in range(epochs):
            for batch in self.get_batches():
                # Works with ANY model implementing Model protocol
                output = self.model(batch)
                loss = self.loss(output, batch.targets)
```

**Refactoring Pattern**:
```python
# OLD: Type hints with concrete classes → CIRCULAR
def create_model() -> ResNet:
    return ResNet(...)

# NEW: Type hints with protocols → DECOUPLED
def create_model() -> Model:
    return ResNet(...)  # Still creates ResNet, but type is protocol
```

---

### Step 3: Create Lazy Loading Module

**File**: `codex/training/lazy_backends.py` (new)

```python
"""
Lazy loading of ML backends - decouples training from concrete implementations.
Backends are loaded only when explicitly requested, not on import.
"""

from typing import Optional, Dict, Any
from codex.training.protocols import (
    Model, Loss, Optimizer, Trainer, 
    ModelFactory, LossFactory, OptimizerFactory, TrainerFactory
)

# Registry for lazy-loadable backends (no imports yet)
_BACKEND_REGISTRY: Dict[str, Dict[str, Any]] = {
    'pytorch': {
        'model_factory': None,  # Will load from codex_ml.models when needed
        'loss_factory': None,
        'optimizer_factory': None,
        'trainer_factory': None,
    },
    'tensorflow': {
        'model_factory': None,
        'loss_factory': None,
        'optimizer_factory': None,
        'trainer_factory': None,
    },
}


def get_model_factory(backend: str = 'pytorch') -> ModelFactory:
    """Get model factory for backend (lazy loads on demand)."""
    if _BACKEND_REGISTRY[backend]['model_factory'] is None:
        # Lazy import - only happens when explicitly requested
        if backend == 'pytorch':
            from codex_ml.models.pytorch_models import create_pytorch_model
            _BACKEND_REGISTRY[backend]['model_factory'] = create_pytorch_model
        elif backend == 'tensorflow':
            from codex_ml.models.tensorflow_models import create_tensorflow_model
            _BACKEND_REGISTRY[backend]['model_factory'] = create_tensorflow_model
    
    return _BACKEND_REGISTRY[backend]['model_factory']


def get_trainer_factory(backend: str = 'pytorch') -> TrainerFactory:
    """Get trainer factory for backend (lazy loads on demand)."""
    # Similar pattern for trainers
    ...


def create_model(model_type: str, backend: str = 'pytorch', **kwargs) -> Model:
    """Create model using specified backend (lazy loads implementations)."""
    factory = get_model_factory(backend)
    return factory(model_type, **kwargs)


def create_trainer(backend: str = 'pytorch', **kwargs) -> Trainer:
    """Create trainer using specified backend (lazy loads implementations)."""
    factory = get_trainer_factory(backend)
    return factory(**kwargs)
```

**Properties**:
- ✅ Zero imports of codex_ml at module load time
- ✅ Imports only happen when explicitly requested
- ✅ Supports pluggable backends (PyTorch, TensorFlow, etc.)
- ✅ Eliminates circular dependency at import time

---

### Step 4: Refactor codex_ml to Use Protocols

**File**: `codex_ml/models/__init__.py`

**Before** (Circular):
```python
from codex.training.losses import CrossEntropy
from codex.training.callbacks import CheckpointCallback

class ResNet(torch.nn.Module):
    def __init__(self, loss_fn=CrossEntropy):
        self.loss_fn = loss_fn  # ← Imports training, which imports this
```

**After** (Protocol-based):
```python
from codex.training.protocols import Model, Loss

class ResNet(Model):
    """ResNet implementing Model protocol (no training imports)."""
    
    def __init__(self, loss_fn: Optional[Loss] = None):
        self.loss_fn = loss_fn  # Can be ANY Loss implementation
        # No import of codex.training at all
    
    def __call__(self, batch):
        # Uses protocol interface, not concrete types
        ...
    
    def parameters(self):
        return self.weight_params


# Expose via factory
def create_pytorch_model(model_type: str, **kwargs) -> Model:
    if model_type == 'resnet':
        return ResNet(**kwargs)
    # ...
```

---

### Step 5: Create Validation Tests

**File**: `tests/packaging/test_ml_circular_deps.py`

```python
"""
Verify circular dependencies between training and ML are resolved.
"""

import sys
import subprocess
import ast

def test_training_imports_without_models():
    """Verify codex.training can import without loading concrete models."""
    # Remove ML modules from cache
    ml_mods = [m for m in sys.modules if 'codex_ml.models' in m]
    for mod in ml_mods:
        del sys.modules[mod]
    
    # Import training - should NOT import models
    import codex.training
    assert 'codex_ml.models' not in str(sys.modules)


def test_protocol_definition_isolation():
    """Verify protocols have zero imports from codex_ml."""
    from codex.training import protocols
    
    # Parse source and check imports
    source = inspect.getsource(protocols)
    tree = ast.parse(source)
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    # Should have zero imports from codex_ml
    assert not any('codex_ml' in imp for imp in imports)


def test_lazy_loading_prevents_import_cycles():
    """Verify lazy loading prevents circular imports at load time."""
    result = subprocess.run(
        ['python', '-c', 
         'import codex.training.lazy_backends; import codex_ml.models'],
        capture_output=True, text=True
    )
    
    # Should succeed with no import cycle errors
    assert result.returncode == 0, f"Import failed: {result.stderr}"


def test_trainer_works_with_protocol_models():
    """Verify trainer works with protocol-based models."""
    from codex.training.trainer import StandardTrainer
    from codex.training.protocols import Model, Loss, Optimizer, TrainingBatch
    
    # Create mock implementations of protocols
    class MockModel:
        def __call__(self, batch: TrainingBatch):
            return [0.5, 0.3, 0.2]
        
        def parameters(self):
            return []
        
        def to(self, device):
            pass
    
    class MockLoss:
        def __call__(self, predictions, targets):
            return 0.5
    
    class MockOptimizer:
        def zero_grad(self): pass
        def step(self): pass
    
    # Trainer should work with mocks
    trainer = StandardTrainer(MockModel(), MockLoss(), MockOptimizer())
    assert trainer.model is not None
```

**Success Criteria**:
- [ ] test_training_imports_without_models PASSES
- [ ] test_protocol_definition_isolation PASSES
- [ ] test_lazy_loading_prevents_import_cycles PASSES
- [ ] test_trainer_works_with_protocol_models PASSES

---

## 🔄 Refactoring Workflow

### Phase 1: Preparation (2-4 hours)

- [ ] Create codex/training/protocols.py (protocols + dataclasses)
- [ ] Create codex/training/lazy_backends.py (lazy loading)
- [ ] Write test suite (test_ml_circular_deps.py)
- [ ] Map all 15+ circular dependency paths

### Phase 2: Refactoring (6-10 hours)

**Priority 1** (High-impact cycles, 3-4 files):
1. [ ] `codex/training/__init__.py` - Extract model imports
2. [ ] `codex/training/trainer.py` - Use protocols instead of concrete types
3. [ ] `codex_ml/models/__init__.py` - Implement Model protocol

**Priority 2** (Secondary cycles, 5-7 files):
4. [ ] `codex/training/callbacks.py` - Protocol-based callbacks
5. [ ] `codex/training/losses.py` - Loss protocol implementation
6. [ ] `codex_ml/training/optimizer_factory.py` - Optimizer protocol
7. [ ] `codex_ml/data/loader.py` - Data pipeline decoupling

**Priority 3** (Tertiary cycles, 4-6 files):
8. [ ] `codex_ml/safety/adversarial.py` - Safety integration
9. [ ] `codex/training/schedules.py` - Learning rate schedules
10. [ ] Other safety/integration modules (4+ files)

### Phase 3: Validation (3-5 hours)

- [ ] Run test suite: `pytest tests/packaging/test_ml_circular_deps.py -v`
- [ ] Verify no import cycles: `python -m py_compile codex/**/*.py`
- [ ] Check backward compatibility: existing code still works
- [ ] Verify type checking: `mypy codex/training/ codex_ml/`
- [ ] Test lazy loading: confirm models load only on demand

### Phase 4: Documentation (1-2 hours)

- [ ] Update architecture docs on protocol-based design
- [ ] Document backend plugin mechanism
- [ ] Add migration guide for custom trainers
- [ ] Update CHANGELOG.md and .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md

---

## 🎯 Success Metrics (P1 Fix Complete)

### Technical Metrics
- [ ] Zero circular imports detected (static analysis)
- [ ] codex.training imports independently (test passes)
- [ ] codex_ml.models imports independently (test passes)
- [ ] Import order is irrelevant (no fragile ordering)
- [ ] All 15+ dependency cycles resolved
- [ ] ML test suite: 100% pass rate (1000+ tests)

### Architecture Metrics
- [ ] Protocol-based design adopted (10+ modules)
- [ ] Lazy loading prevents import-time coupling
- [ ] Plugin-style backend injection enabled
- [ ] Type checking passes: mypy strict mode

### Distribution Metrics
- [ ] ML package can be built independently
- [ ] Training module can be shipped separately
- [ ] Backend swappability verified (mock backend test)
- [ ] Package size: <1% growth

---

## 📋 Execution Dependencies

**Before Starting P1 Fix**:
- [ ] P0 fix (logging decoupling) has started
- [ ] Phase 1 (Cognitive Brain) is complete
- [ ] Circular dependency chains documented
- [ ] Team has consensus on protocol pattern
- [ ] Backup branch created: `p1-fix-backup`

**Parallel Work**:
- P1 fix starts after 1 week of P0 progress
- Both P0 and P1 fixes run in parallel (2 agents)
- P1 does NOT depend on P0 completion

**Duration Overlap**:
- P0: Weeks 2-3 (10-14 days)
- P1: Weeks 3-4 (10-14 days, starting day 8 of P0)
- Overlap: Days 8-14 (1 week of parallel work)

---

## 🚀 Execution Handoff

**P1 Fix Status**: READY FOR SPECIALIST ASSIGNMENT

**Recommended Agent Assignment**:
- **Primary**: refactoring-protocol-specialist or similar
- **Secondary**: architecture-validation-agent
- **Reviewer**: skills-master-agent (for protocol design review)

**Next Steps After P1 Complete**:
1. Package ML module (Phase 3 delivery)
2. Pre-cache HuggingFace models (~1 GB)
3. Publish aries-serpent-ml-0.1.0
4. Target Phase 3 release: 1 week after P1 completion

---

**Document Status**: P1 Blocker Execution Brief  
**Created**: 2026-07-08 21:30 UTC  
**Authority**: @mbaetiong standing approval  
**Next Review**: After P0 shows 1 week progress (2026-07-19)
