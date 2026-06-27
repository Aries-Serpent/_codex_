# 📊 Lane 3.3: ML Data Pipeline Coverage Remediation Brief

**Date:** 2026-06-27T22:22:24Z  
**Status:** ✅ Ready for Execution  
**Lane Owner:** unified-coverage-agent  
**Lane Scope:** `src/codex_ml/data/`  
**Campaign:** Phase 6 Wave 3 — ML Systems Coverage Gap Remediation  

---

## Lane 3.3 Executive Summary

Lane 3.3 addresses critical coverage gaps in the ML data pipeline, focusing on **data loading, preprocessing, batch creation, and serialization**. This lane targets **40-60 new tests** to improve coverage from **8.6% → 60-80%**, ensuring data integrity and determinism.

### Coverage Baseline
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Lines of Code** | 5,984 | N/A | N/A |
| **Line Coverage** | 8.6% | 60-80% | 51-71 pp |
| **Test Files** | 3 | 1-2 | +0-1 files |
| **Tests** | ~12 | 40-60 | +28-48 tests |
| **Critical Gaps** | 7 | 0 | 7 to close |

### Lane 3.3 Success Criteria
- ✅ **40-60 new tests** written and passing
- ✅ **Coverage:** 8.6% → ≥60%
- ✅ **Pass Rate:** 100% (all tests green)
- ✅ **Zero Regressions:** Existing tests still pass
- ✅ **Timeline:** 15-20 hours (fits Wave 3 schedule)
- ✅ **Ready for Wave 4:** Data pipeline stability for training

---

## Critical Gaps Analysis

### GAP-3.3.1: Data Loading (CRITICAL)
**Risk Level:** 🔴 CRITICAL  
**Coverage Impact:** 2-3%  
**Effort Estimate:** 12-15 tests, 4-5 hours  

**Current State:**
- No round-trip load/save tests
- Data shape preservation not verified
- File format conversions untested
- Empty file handling untested

**Target State:**
- Test data loads without corruption
- Test shape/dtype preservation
- Test multiple file formats (CSV, Parquet, HDF5)
- Test edge cases (empty files, single row)

**Test Patterns:**
```python
def test_data_loader_csv_round_trip(tmp_path):
    """CSV data loads and saves without corruption."""
    # Create test CSV
    data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    csv_path = tmp_path / 'test.csv'
    data.to_csv(csv_path, index=False)
    
    # Load and save
    loader = DataLoader(csv_path)
    loaded = loader.load()
    
    # Verify shape preserved
    assert loaded.shape == data.shape
    # Verify values preserved
    assert np.allclose(loaded.values, data.values)

def test_data_loader_parquet_round_trip(tmp_path):
    """Parquet data loads and saves without corruption."""
    # Similar to CSV, but use parquet format
    
def test_data_loader_empty_file():
    """Empty file handled gracefully."""
    empty_file = tmp_path / 'empty.csv'
    empty_file.write_text('')
    
    loader = DataLoader(empty_file)
    data = loader.load()
    assert len(data) == 0 or data.empty

def test_data_loader_single_row():
    """Single row dataset handled correctly."""
    data = pd.DataFrame({'x': [1], 'y': [2]})
    csv_path = tmp_path / 'single.csv'
    data.to_csv(csv_path, index=False)
    
    loaded = DataLoader(csv_path).load()
    assert len(loaded) == 1
    assert loaded.iloc[0]['x'] == 1

def test_dtype_preservation_numeric():
    """Numeric dtypes preserved in load/save."""
    data = pd.DataFrame({'int_col': np.array([1, 2, 3], dtype=np.int32),
                         'float_col': np.array([1.1, 2.2, 3.3], dtype=np.float32)})
    # Save and load
    # Verify: dtypes match or are compatible
```

**Success Criteria:**
- [ ] 12-15 tests written
- [ ] All tests passing
- [ ] Coverage increase: +2-3%

---

### GAP-3.3.2: Preprocessing Pipeline (CRITICAL)
**Risk Level:** 🔴 CRITICAL  
**Coverage Impact:** 2-3%  
**Effort Estimate:** 12-15 tests, 4-5 hours  

**Current State:**
- Transformation consistency not tested
- Preprocessing state not saved/loaded
- Pipeline composition untested
- Determinism not verified

**Target State:**
- Test preprocessing produces consistent results
- Test preprocessing state persistence
- Test chained transformations
- Test determinism with seed

**Test Patterns:**
```python
def test_preprocessing_determinism_with_seed():
    """Preprocessing is deterministic with same seed."""
    preprocessor = Preprocessor(random_seed=42)
    data = np.random.randn(50, 20)
    
    result1 = preprocessor.fit_transform(data)
    result2 = preprocessor.fit_transform(data)
    
    assert np.allclose(result1, result2)

def test_preprocessing_state_persistence():
    """Preprocessing state can be saved and loaded."""
    preprocessor = Preprocessor()
    data = np.random.randn(100, 20)
    preprocessor.fit(data)
    
    # Get state
    state = preprocessor.get_state()
    
    # Create new preprocessor and load state
    preprocessor2 = Preprocessor()
    preprocessor2.set_state(state)
    
    # Transform with both should be identical
    result1 = preprocessor.transform(data)
    result2 = preprocessor2.transform(data)
    assert np.allclose(result1, result2)

def test_preprocessing_pipeline_composition():
    """Multiple preprocessing steps compose correctly."""
    pipeline = Pipeline([
        ('normalize', Normalizer()),
        ('scale', Scaler()),
        ('augment', Augmentor())
    ])
    
    data = np.random.randn(50, 20)
    result = pipeline.fit_transform(data)
    
    # Verify shape preserved
    assert result.shape == data.shape

def test_fit_transform_fit_consistency():
    """fit_transform result matches fit then transform."""
    preprocessor1 = Preprocessor()
    preprocessor2 = Preprocessor()
    
    data = np.random.randn(100, 20)
    
    # Method 1: fit_transform
    result1 = preprocessor1.fit_transform(data)
    
    # Method 2: fit then transform
    preprocessor2.fit(data)
    result2 = preprocessor2.transform(data)
    
    assert np.allclose(result1, result2)
```

**Success Criteria:**
- [ ] 12-15 tests written
- [ ] All tests passing
- [ ] Coverage increase: +2-3%

---

### GAP-3.3.3: Batch Creation (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 1.5-2%  
**Effort Estimate:** 8-10 tests, 3 hours  

**Current State:**
- Edge cases not tested (empty, single item, large batches)
- Batch size validation missing
- Remainder handling untested

**Target State:**
- Test batching with various sizes
- Test edge cases (empty, single item)
- Test remainder batches
- Test batch indexing

**Test Patterns:**
```python
def test_batching_standard_sizes():
    """Batching works with standard batch sizes."""
    batch_creator = BatchCreator(batch_size=32)
    
    for size in [64, 100, 128, 256]:
        data = np.random.randn(size, 10)
        batches = list(batch_creator.create_batches(data))
        
        # All batches except last are full size
        for batch in batches[:-1]:
            assert len(batch) == 32
        
        # Total items recovered
        total = sum(len(b) for b in batches)
        assert total == size

def test_batch_creation_empty_dataset():
    """Empty dataset produces no batches."""
    batch_creator = BatchCreator(batch_size=32)
    data = np.array([]).reshape(0, 10)
    batches = list(batch_creator.create_batches(data))
    assert len(batches) == 0

def test_batch_creation_single_item():
    """Single item creates single batch."""
    batch_creator = BatchCreator(batch_size=32)
    data = np.random.randn(1, 10)
    batches = list(batch_creator.create_batches(data))
    assert len(batches) == 1
    assert len(batches[0]) == 1

def test_batch_creation_not_divisible():
    """Batch size not evenly divisible handled."""
    batch_creator = BatchCreator(batch_size=32)
    data = np.random.randn(100, 10)  # 100 % 32 = 4 remainder
    batches = list(batch_creator.create_batches(data))
    
    # Should have 4 full batches of 32 + 1 batch of 4
    assert len(batches) == 4

def test_batch_shuffle():
    """Shuffled batches are different from sequential."""
    batch_creator = BatchCreator(batch_size=32, shuffle=True, seed=42)
    data = np.arange(100).reshape(100, 1)
    
    batches1 = list(batch_creator.create_batches(data))
    # Extract indices
    indices1 = np.concatenate(batches1).flatten()
    
    # Should not be sequential 0,1,2,...,99
    assert not np.array_equal(indices1, np.arange(100))
```

**Success Criteria:**
- [ ] 8-10 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1.5-2%

---

### GAP-3.3.4: Data Augmentation (HIGH)
**Risk Level:** 🟠 HIGH  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 6-8 tests, 2-3 hours  

**Current State:**
- Augmentation transforms not tested
- Determinism not verified
- Augmentation state not saved/loaded

**Target State:**
- Test augmentation produces valid transforms
- Test determinism with seed
- Test augmentation parameter validation

**Test Patterns:**
```python
def test_augmentation_determinism_with_seed():
    """Augmentation is deterministic with seed."""
    augmentor = Augmentor(random_seed=42)
    data = np.random.randn(10, 224, 224, 3)
    
    result1 = augmentor.augment(data)
    result2 = augmentor.augment(data)
    
    assert np.allclose(result1, result2)

def test_augmentation_changes_data():
    """Augmentation actually modifies data."""
    augmentor = Augmentor(augmentation_rate=1.0)
    data = np.random.randn(10, 224, 224, 3)
    
    augmented = augmentor.augment(data)
    
    # Should be different
    assert not np.allclose(data, augmented, atol=1e-6)

def test_augmentation_preserves_shape():
    """Augmentation preserves input shape."""
    augmentor = Augmentor()
    data = np.random.randn(10, 224, 224, 3)
    
    augmented = augmentor.augment(data)
    
    assert augmented.shape == data.shape

def test_augmentation_parameter_validation():
    """Invalid augmentation parameters rejected."""
    with pytest.raises(ValueError):
        Augmentor(augmentation_rate=1.5)  # Must be 0-1
        
    with pytest.raises(ValueError):
        Augmentor(rotation_angle=-100)  # Out of range
```

**Success Criteria:**
- [ ] 6-8 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.3.5: Serialization & Caching (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 1-1.5%  
**Effort Estimate:** 6-8 tests, 2-3 hours  

**Current State:**
- Serialization format not validated
- Corrupted cache not detected
- Cache invalidation not tested

**Target State:**
- Test serialization/deserialization round-trip
- Test corruption detection
- Test cache validity checks

**Test Patterns:**
```python
def test_serialization_round_trip(tmp_path):
    """Serialized data recovers exactly."""
    data = {'arrays': [np.random.randn(50, 20), np.random.randint(0, 10, 50)],
            'metadata': {'source': 'test', 'version': 1}}
    
    serializer = Serializer()
    path = tmp_path / 'data.pkl'
    
    serializer.save(data, path)
    recovered = serializer.load(path)
    
    assert np.allclose(data['arrays'][0], recovered['arrays'][0])
    assert np.array_equal(data['arrays'][1], recovered['arrays'][1])
    assert data['metadata'] == recovered['metadata']

def test_cache_corruption_detection(tmp_path):
    """Corrupted cache file detected."""
    cache_file = tmp_path / 'cache.pkl'
    cache_file.write_bytes(b'corrupted data here')
    
    with pytest.raises((pickle.UnpicklingError, EOFError, ValueError)):
        serializer = Serializer()
        serializer.load(cache_file)

def test_cache_invalidation_on_version_change():
    """Cache invalidated when version changes."""
    cache_manager = CacheManager(version=1)
    
    # Create cache for version 1
    cache_manager.save({'key': 'value'}, 'test_cache')
    assert cache_manager.exists('test_cache')
    
    # Create new cache manager with different version
    cache_manager2 = CacheManager(version=2)
    
    # Should not find cache from version 1
    assert not cache_manager2.exists('test_cache')
```

**Success Criteria:**
- [ ] 6-8 tests written
- [ ] All tests passing
- [ ] Coverage increase: +1-1.5%

---

### GAP-3.3.6: Memory Efficiency (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 0.5-1%  
**Effort Estimate:** 4-6 tests, 2 hours  

**Current State:**
- Memory usage not validated
- Large dataset handling untested
- Memory leak potential not checked

**Target State:**
- Test memory usage is within bounds
- Test large dataset handling
- Test cleanup on completion

**Test Patterns:**
```python
def test_memory_efficient_batching(mocker):
    """Batching doesn't load entire dataset in memory."""
    # Mock memory tracker
    memory_spy = mocker.spy(memory_module, 'get_memory_usage')
    
    batch_creator = BatchCreator(batch_size=32)
    large_dataset = np.random.randn(10000, 1000)  # ~80MB
    
    batches = batch_creator.create_batches(large_dataset)
    # Iterate through batches
    for batch in batches:
        memory_usage = memory_spy.return_value
        # Memory should stay under 1GB even for 10k items
        assert memory_usage < 1e9

def test_generator_cleanup_on_exception():
    """Generator resources cleaned up on exception."""
    batch_creator = BatchCreator(batch_size=32)
    data = np.random.randn(100, 10)
    
    batches_gen = batch_creator.create_batches(data)
    
    # Iterate and raise exception
    try:
        for i, batch in enumerate(batches_gen):
            if i == 1:
                raise RuntimeError("Test error")
    except RuntimeError:
        pass
    
    # Resources should be cleaned up (no unclosed files, etc)
    # Could verify with pytest warning check for unclosed resources
```

**Success Criteria:**
- [ ] 4-6 tests written
- [ ] All tests passing
- [ ] Coverage increase: +0.5-1%

---

### GAP-3.3.7: Error Handling (MEDIUM)
**Risk Level:** 🟡 MEDIUM  
**Coverage Impact:** 0.5-1%  
**Effort Estimate:** 4-6 tests, 2 hours  

**Current State:**
- Missing file error handling untested
- Permission error handling untested
- Corrupted data error handling untested

**Target State:**
- Test helpful error messages
- Test graceful error recovery
- Test error codes are consistent

**Test Patterns:**
```python
def test_missing_file_error():
    """Missing file raises helpful error."""
    with pytest.raises(FileNotFoundError, match="not found"):
        DataLoader('/path/that/does/not/exist.csv').load()

def test_permission_denied_error():
    """Permission denied shows clear message."""
    with patch('os.access', return_value=False):
        with pytest.raises(PermissionError, match="permission"):
            DataLoader('/restricted/path.csv').load()

def test_corrupted_data_error():
    """Corrupted data detected with helpful message."""
    with pytest.raises((ValueError, RuntimeError), match="corrupt|invalid"):
        # Create file with invalid data
        bad_file = tmp_path / 'bad.csv'
        bad_file.write_text('not,valid,csv,format\nmore,bad')
        loader = DataLoader(bad_file)
        loader.load()  # Should fail

def test_invalid_column_names():
    """Invalid column names detected."""
    with pytest.raises(ValueError, match="column|unexpected"):
        data = pd.DataFrame({'x_col': [1, 2, 3]})
        loader = DataLoader(data)
        # Try to access expected column that doesn't exist
        loader.get_column('y_col')
```

**Success Criteria:**
- [ ] 4-6 tests written
- [ ] All tests passing
- [ ] Coverage increase: +0.5-1%

---

## Test Generation Implementation Guide

### Step 1: Set Up Test File Structure

```python
# tests/codex_ml/test_data_comprehensive.py
"""Comprehensive tests for ML data pipeline (Lane 3.3)."""

import pytest
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Imports from data module
from src.codex_ml.data import (
    DataLoader,
    Preprocessor,
    BatchCreator,
    Augmentor,
    Serializer
)

# ============================================================================
# Fixtures (Shared test setup)
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """Create sample dataframe for tests."""
    return pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'label': np.random.randint(0, 10, 100)
    })

@pytest.fixture
def sample_csv(tmp_path, sample_dataframe):
    """Create sample CSV file."""
    csv_path = tmp_path / 'sample.csv'
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path

@pytest.fixture
def sample_numpy_data():
    """Create sample numpy data."""
    return np.random.randn(100, 20)

# ============================================================================
# GAP-3.3.1 Tests: Data Loading
# ============================================================================

class TestDataLoading:
    """Tests for data loading functionality."""
    
    def test_csv_load_preserves_shape(self, sample_csv, sample_dataframe):
        """CSV load preserves original data shape."""
        loader = DataLoader(sample_csv)
        data = loader.load()
        assert data.shape == sample_dataframe.shape
    
    def test_csv_load_preserves_values(self, sample_csv, sample_dataframe):
        """CSV load preserves data values."""
        loader = DataLoader(sample_csv)
        data = loader.load()
        assert np.allclose(data.values, sample_dataframe.values)

# Continue with remaining gap tests...
```

### Step 2: Implement Gap Tests

For each GAP section, implement corresponding test class with 6-15 tests each.

### Step 3: Run & Validate

```bash
# Run tests locally
pytest tests/codex_ml/test_data_comprehensive.py -v --tb=short

# Check coverage
pytest tests/codex_ml/test_data_comprehensive.py \
    --cov=src/codex_ml/data --cov-report=term

# Expect: Coverage 8.6% → 60%+
```

---

## Lane 3.3 Success Metrics

### Coverage Metrics
| Module | Baseline | Target | Success |
|--------|----------|--------|---------|
| `src/codex_ml/data/__init__.py` | 4% | 60% | ✅ if ≥60% |
| `src/codex_ml/data/loader.py` | 10% | 60% | ✅ if ≥60% |
| `src/codex_ml/data/preprocessor.py` | 8% | 60% | ✅ if ≥60% |
| `src/codex_ml/data/augmentor.py` | 7% | 60% | ✅ if ≥60% |
| **Overall** | **8.6%** | **60%** | ✅ if ≥60% |

### Test Metrics
| Metric | Target | Status |
|--------|--------|--------|
| **Tests Written** | 40-60 | ⏳ in_progress |
| **Tests Passing** | 100% | ⏳ in_progress |
| **Pass Rate** | ≥95% | ⏳ in_progress |
| **Execution Time** | <2 min | ⏳ in_progress |

---

## Timeline & Milestones

| Phase | Start | Duration | Tasks | Owner |
|-------|-------|----------|-------|-------|
| **Setup** | T+0h | 1h | Fixtures, test templates | agent |
| **Development Phase 1** | T+1h | 7h | GAP-3.3.1 through GAP-3.3.4 | agent |
| **Checkpoint 1** | T+8h | 2h | Local validation | agent |
| **Development Phase 2** | T+10h | 5h | GAP-3.3.5 through GAP-3.3.7 | agent |
| **CI Validation** | T+15h | 3h | Full test suite, coverage report | CI |
| **Sign-off** | T+18h | 1-2h | Documentation, metrics | agent |

**Total Duration:** 15-20 hours  
**Parallel with:** Lane 3.1 & Lane 3.2  
**Ready for:** Phase 6 Wave 4  

---

## Integration Notes

### Dependencies Within Lane
- ✅ No inter-test dependencies
- ✅ Each GAP independent
- ✅ Fixtures fully isolated

### Parallel Execution
- ✅ Can run in parallel with Lane 3.1 & 3.2
- ✅ No shared resources
- ✅ Separate test files

---

## Activation Checklist

- [ ] Phase 6 Wave 1 promoted to main
- [ ] Phase 5 Lane 5.1 report reviewed
- [ ] Test file template created
- [ ] Data fixtures prepared
- [ ] Mock objects validated
- [ ] CI gates configured
- [ ] Ready for execution

---

**Lane Owner:** unified-coverage-agent  
**Status:** ✅ READY FOR EXECUTION  
**Estimated Completion:** 2026-06-30  

