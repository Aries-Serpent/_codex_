# 🧠 Lane 3.1: ML Training Pipeline Coverage Remediation Brief

**Date:** 2026-06-27T22:22:22Z  
**Status:** ✅ Ready for Execution  
**Lane Owner:** unified-coverage-agent  
**Lane Scope:** `src/codex_ml/training/`  
**Campaign:** Phase 6 Wave 3 — ML Systems Coverage Gap Remediation  

---

## Lane 3.1 Executive Summary

Lane 3.1 focuses on comprehensive coverage remediation for the ML training pipeline, addressing **CRITICAL coverage gaps** that pose direct risks to training correctness, convergence behavior, and production model quality.

### Coverage Baseline
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Lines of Code** | 9,778 | N/A | N/A |
| **Line Coverage** | 9.4% | 60-80% | 50-71 pp |
| **Test Files** | 3 | 1-2 | +0-1 files |
| **Tests** | ~15 | 60-80 | +45-65 tests |
| **Critical Gaps** | 7 | 0 | 7 to close |

### Lane 3.1 Success Criteria
- ✅ **60-80 new tests** written and passing
- ✅ **Coverage:** 9.4% → ≥60%
- ✅ **Pass Rate:** 100% (all tests green)
- ✅ **Zero Regressions:** Existing tests still pass
- ✅ **Timeline:** 20-25 hours (fits Wave 3 schedule)
- ✅ **Ready for Wave 4:** Integration with MyPy hardening

---

## Critical Gaps Analysis

### GAP-3.1.1: Model Training Loop (CRITICAL)
**Risk Level:** 🔴 CRITICAL  
**Coverage Impact:** 2-3%  
**Effort Estimate:** 12-15 tests, 4-5 hours  

**Current State:**
- No unit tests for single training step execution
- Model forward pass untested
- Loss backpropagation untested
- Gradient application untested

**Target State:**
- Test forward pass on mock model with fixed tensor input
- Test backward pass (mock gradients)
- Test gradient accumulation after backward
- Test optimizer.step() invocation

**Test Patterns:**
```python
def test_single_training_step():
    """Training step produces numeric loss and updates params."""
    # Mock: model, optimizer, loss function
    # Invoke: trainer.train_step(batch)
    # Verify: loss > 0, optimizer.step called once, gradients nonzero
    
def test_training_loop_updates_model_weights():
    """Model parameters updated after training step."""
    # Capture initial param values
    # Run training step
    # Verify: at least one param changed

def test_training_with_gradient_accumulation():
    """Gradient accumulation works for scaled loss."""
    # Run 2 steps with accumulation
    # Verify: accumulated gradients match full batch
```

**Success Criteria:**
- [ ] 12-15 tests written
- [ ] All tests passing
- [ ] Coverage increase: +2-3%

---

### GAP-3.1.2: Gradient Accumulation (CRITICAL)
**Risk Level:** 🔴 CRITICAL  
**Coverage Impact:** 1.5-2%  
**Effort Estimate:** 8-10 tests, 3-4 hours  

**Current State:**
- Accumulation logic untested
- Edge cases (zero accumulation, overflow) untested
- Determinism not verified

**Target State:**
- Test accumulation correctness vs. full-batch gradient
- Test accumulation reset at epoch boundary
- Test numerical stability (gradient overflow handling)

**Test Patterns:**
```python
def test_gradient_accumulation_correctness():
    """Accumulated gradients match full-batch gradient."""
    # Run with accumulation_steps=2
    # Compare gradient magnitude vs full batch
    # Verify: difference < epsilon

def test_accumulation_reset_on_zero_step():
    """Gradients reset when accumulation counter zero."""
    # Mock: optimizer with accumulation_steps=4
    # Run 4 steps, verify reset on step 5
    
def test_accumulated_gradient_stability():
    """Large gradients don't overflow accumulation."""
    # Mock large batch (1000 items)
    # Verify: accumulation doesn't NaN/inf
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1.5-2%

---

### GAP-3.1.3: Loss Computation (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 2-3%  
**Effort Estimate:** 10-12 tests, 3-4 hours  

**Current State:**
- Multiple loss functions (CrossEntropy, MSE, BCE) untested
- NaN/inf conditions not caught
- Loss scaling (for mixed precision) untested

**Target State:**
- Test each loss function with valid/invalid inputs
- Test loss computation on mock predictions
- Test loss scaling behavior

**Test Patterns:**
```python
@pytest.mark.parametrize("loss_fn,pred,target", [
    ("cross_entropy", mock_logits, mock_labels),
    ("mse", mock_pred, mock_target),
    ("bce", mock_prob, mock_binary),
])
def test_loss_computation(loss_fn, pred, target):
    """Loss computation produces valid scalar."""
    loss = compute_loss(pred, target, loss_fn)
    assert not torch.isnan(loss)
    assert not torch.isinf(loss)
    assert loss > 0

def test_loss_with_class_weights():
    """Weighted loss reflects class priorities."""
    # Verify: high-weight class produces higher loss
    
def test_loss_scaling_for_mixed_precision():
    """Loss scaled for mixed precision training."""
    # Run with loss scale factor
    # Verify: scaled loss is larger
```

**Success Criteria:**
- [ ] 10-12 tests written
- [ ] All tests passing
- [ ] Coverage increase: +2-3%

---

### GAP-3.1.4: Learning Rate Scheduling (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 1.5-2%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- No validation of learning rate schedules
- Schedule state not tested
- Edge cases (manual LR override, schedule resumption) untested

**Target State:**
- Test LR schedule progression
- Test schedule state preservation
- Test manual LR adjustment

**Test Patterns:**
```python
def test_learning_rate_schedule_progression():
    """Learning rate decreases according to schedule."""
    scheduler = CosineAnnealingLR(optimizer, T_max=10)
    lrs = []
    for _ in range(10):
        lrs.append(optimizer.param_groups[0]['lr'])
        scheduler.step()
    
    # Verify: LR decreases then increases (cosine pattern)
    assert lrs[0] > lrs[5]  # Decreases first half

def test_schedule_with_warmup():
    """Warmup phase increases LR from zero."""
    # Verify: warmup steps have increasing LR
    
def test_lr_schedule_state_dict():
    """Schedule state can be saved/loaded."""
    state = scheduler.state_dict()
    scheduler.load_state_dict(state)
    # Verify: same LR after reload
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1.5-2%

---

### GAP-3.1.5: Checkpoint Management (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- Save/load round-trip not tested
- Partial checkpoints not tested
- Checkpoint corruption not detected

**Target State:**
- Test checkpoint save/load preserves model state
- Test checkpoint resumption (training continues correctly)
- Test incomplete checkpoint handling

**Test Patterns:**
```python
def test_checkpoint_save_and_load(tmp_path):
    """Checkpoint save/load preserves model state exactly."""
    trainer = Trainer(config)
    # Train for 1 step
    trainer.train_step(batch)
    
    # Save checkpoint
    checkpoint_path = tmp_path / 'checkpoint.pt'
    trainer.save_checkpoint(checkpoint_path)
    
    # Load checkpoint into new trainer
    trainer2 = Trainer(config)
    trainer2.load_checkpoint(checkpoint_path)
    
    # Verify: model parameters identical
    for p1, p2 in zip(trainer.model.parameters(), 
                      trainer2.model.parameters()):
        assert torch.allclose(p1, p2)

def test_checkpoint_resumption():
    """Training resumes correctly from checkpoint."""
    # Train to checkpoint at step 5
    # Resume from checkpoint, run 5 more steps
    # Verify: same results as continuous training
    
def test_corrupted_checkpoint_handling():
    """Corrupted checkpoint raises clear error."""
    # Create invalid checkpoint file
    # Verify: load raises ValueError with helpful message
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.1.6: Distributed Training Sync (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- No multi-device synchronization tests
- Gradient synchronization untested
- Device placement not verified

**Target State:**
- Test gradient synchronization in mocked distributed setup
- Test device-aware tensor placement
- Test synchronization barrier behavior

**Test Patterns:**
```python
def test_distributed_gradient_sync(mocker):
    """Gradients synchronized across mock devices."""
    # Mock: 2-device setup
    mocker.patch('torch.distributed.all_reduce')
    
    # Run training step in distributed mode
    # Verify: all_reduce called for each parameter

def test_device_placement():
    """Model and data on correct devices."""
    # Setup: 2 devices (cuda:0, cuda:1)
    # Verify: model on device 0, batch on device 0
    
def test_sync_barrier_at_epoch_boundary():
    """Synchronization barrier at epoch end."""
    # Mock distributed.barrier
    # Run training loop to epoch boundary
    # Verify: barrier called
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.1.7: Error Handling & Edge Cases (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 0.5-1%  
**Effort Estimate:** 6-8 tests, 2 hours  

**Current State:**
- Invalid config error handling untested
- Empty batch handling untested
- Out-of-memory recovery untested

**Target State:**
- Test config validation errors
- Test graceful handling of empty batches
- Test informative error messages

**Test Patterns:**
```python
def test_invalid_config_raises_error():
    """Invalid config raises ValueError."""
    with pytest.raises(ValueError, match="learning_rate must be > 0"):
        config = TrainingConfig(learning_rate=-0.1)

def test_empty_batch_handling():
    """Empty batch handled gracefully."""
    empty_batch = {'inputs': torch.tensor([]).reshape(0, 128)}
    loss = trainer.train_step(empty_batch)
    assert loss == 0 or torch.isnan(loss)

def test_device_mismatch_detection():
    """Device mismatch detected early."""
    # Model on cuda, batch on cpu
    with pytest.raises(RuntimeError, match="expected.*cuda"):
        trainer.train_step(batch)
```

**Success Criteria:**
- [ ] 6-8 tests written
- [ ] All tests passing
- [ ] Coverage increase: +0.5-1%

---

## Test Generation Implementation Guide

### Step 1: Set Up Test File Structure

```python
# tests/codex_ml/test_training_comprehensive.py
"""Comprehensive tests for ML training pipeline (Lane 3.1)."""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Imports from training module
from src.codex_ml.training import Trainer, TrainingConfig
from src.codex_ml.training.losses import compute_loss
from src.codex_ml.training.schedulers import get_scheduler

# ============================================================================
# Fixtures (Shared test setup)
# ============================================================================

@pytest.fixture
def training_config():
    """Standard training config for tests."""
    return TrainingConfig(
        epochs=2,
        batch_size=32,
        learning_rate=1e-4,
        warmup_steps=100,
        accumulation_steps=1
    )

@pytest.fixture
def mock_model():
    """Mock PyTorch model."""
    model = MagicMock()
    model.parameters.return_value = [
        torch.randn(10, 5, requires_grad=True),
        torch.randn(5, 1, requires_grad=True)
    ]
    return model

@pytest.fixture
def mock_batch():
    """Mock training batch."""
    return {
        'input_ids': torch.randn(32, 128),
        'token_type_ids': torch.randint(0, 2, (32, 128)),  # pragma: allowlist secret
        'attention_mask': torch.ones(32, 128),
        'labels': torch.randint(0, 1000, (32,))
    }

@pytest.fixture
def trainer(training_config, mock_model):
    """Trainer instance with mocked components."""
    trainer = Trainer(training_config)
    trainer.model = mock_model
    trainer.optimizer = MagicMock()
    trainer.scheduler = MagicMock()
    return trainer

# ============================================================================
# GAP-3.1.1 Tests: Training Loop
# ============================================================================

class TestTrainingLoop:
    """Tests for basic training loop functionality."""
    
    def test_single_training_step_produces_loss(self, trainer, mock_batch):
        """Single training step produces numeric loss."""
        loss = trainer.train_step(mock_batch)
        assert isinstance(loss, (float, torch.Tensor))
        assert not np.isnan(loss.item() if torch.is_tensor(loss) else loss)
    
    def test_optimizer_step_called(self, trainer, mock_batch):
        """Optimizer.step() called after gradient computation."""
        trainer.train_step(mock_batch)
        assert trainer.optimizer.step.called
    
    def test_backward_called_during_step(self, trainer, mock_batch):
        """Backward pass initiated during training step."""
        mock_loss = MagicMock()
        with patch('torch.Tensor.backward', wraps=mock_loss.backward):
            trainer.train_step(mock_batch)

# Continue with remaining gap tests...
```

### Step 2: Implement Gap Tests

For each GAP section above, implement corresponding test class in the template file. Follow this structure:

```python
class TestGAPName:
    """Tests for specific coverage gap."""
    
    def test_core_functionality(self):
        """Core behavior works."""
        # Setup, invoke, assert
        pass
    
    def test_edge_case_1(self):
        """Edge case 1 handled."""
        pass
    
    def test_edge_case_2(self):
        """Edge case 2 handled."""
        pass
```

### Step 3: Run & Validate

```bash
# Run tests locally
pytest tests/codex_ml/test_training_comprehensive.py -v --tb=short

# Check coverage
pytest tests/codex_ml/test_training_comprehensive.py \
    --cov=src/codex_ml/training --cov-report=term

# Expect: Coverage 9.4% → 60%+
```

---

## Lane 3.1 Success Metrics

### Coverage Metrics
| Module | Baseline | Target | Success |
|--------|----------|--------|---------|
| `src/codex_ml/training/__init__.py` | 5% | 60% | ✅ if ≥60% |
| `src/codex_ml/training/trainer.py` | 12% | 60% | ✅ if ≥60% |
| `src/codex_ml/training/losses.py` | 8% | 60% | ✅ if ≥60% |
| `src/codex_ml/training/schedulers.py` | 10% | 60% | ✅ if ≥60% |
| **Overall** | **9.4%** | **60%** | ✅ if ≥60% |

### Test Metrics
| Metric | Target | Status |
|--------|--------|--------|
| **Tests Written** | 60-80 | ⏳ in_progress |
| **Tests Passing** | 100% | ⏳ in_progress |
| **Pass Rate** | ≥95% | ⏳ in_progress |
| **Execution Time** | <2 min | ⏳ in_progress |

### Quality Metrics
| Metric | Target | Status |
|--------|--------|--------|
| **Mutation Score** | >75% | ⏳ post-execution |
| **Branch Coverage** | >70% | ⏳ post-execution |
| **Assertion Count** | >200 | ⏳ post-execution |

---

## Timeline & Milestones

| Phase | Start | Duration | Tasks | Owner |
|-------|-------|----------|-------|-------|
| **Setup** | T+0h | 1-2h | Fixture setup, test templates | agent |
| **Development Phase 1** | T+2h | 8h | GAP-3.1.1 through GAP-3.1.4 | agent |
| **Checkpoint 1** | T+10h | 2h | Local validation, coverage check | agent |
| **Development Phase 2** | T+12h | 8h | GAP-3.1.5 through GAP-3.1.7 | agent |
| **CI Validation** | T+20h | 4h | Full test suite, coverage report | CI |
| **Sign-off** | T+24h | 1h | Documentation, final metrics | agent |

**Total Duration:** 20-25 hours  
**Parallel with:** Lane 3.2 & Lane 3.3  
**Ready for:** Phase 6 Wave 4  

---

## Dependency & Integration Notes

### Dependencies Within Lane
- ✅ No inter-test dependencies
- ✅ Each GAP can be implemented independently
- ✅ Fixtures fully isolated (no shared state)

### Dependencies Outside Lane
- ✅ No dependency on Lane 3.2 or Lane 3.3
- ✅ Can execute in parallel
- ✅ No shared mock objects or fixtures

### Integration with Wave 3
- Parallel execution with Lane 3.2 & 3.3
- CI gates: 3 validation checkpoints
- No blocking dependencies for Wave 4

---

## Risk Mitigation

### Risk: PyTorch/Transformers Import Failures
**Mitigation:**
- Use MagicMock for model instantiation
- Mock torch.nn.Module instead of inheriting
- Mock optimizer implementations

### Risk: Coverage Target Not Achieved
**Mitigation:**
- Focus on decision points (if/for branches)
- Add edge case tests last (40% → 60% uplift)
- Analyze coverage report to identify gaps

### Risk: Tests Pass Locally But Fail in CI
**Mitigation:**
- Use deterministic seeds for random operations
- Mock all external I/O
- Test with CI environment locally first

---

## Activation Checklist

- [ ] Phase 6 Wave 1 promoted to main
- [ ] Phase 5 Lane 5.1 report reviewed
- [ ] Test file template created
- [ ] Mock fixtures validated
- [ ] CI gates configured
- [ ] Ready for execution

---

**Lane Owner:** unified-coverage-agent  
**Status:** ✅ READY FOR EXECUTION  
**Estimated Completion:** 2026-06-30  

