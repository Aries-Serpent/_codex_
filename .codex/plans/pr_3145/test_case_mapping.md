# Test Case Mapping for Tokenization Coverage
> Generated: 2026-02-04T14:40:00Z | Author: copilot-agent
> Target: 70% coverage for src/tokenization/ module

---

## 🎯 Executive Summary

**Current Coverage**: 25.00% (112/448 lines)
**Target Coverage**: 70.00%
**Gap**: 45.00 percentage points
**Tests Required**: 12+ comprehensive tests

---

## 🔴 CRITICAL Priority: cli.py (12.45% → 70%)

**Gap**: 57.55 percentage points | **Lines Needed**: ~120

### Test Cases

1. **Test: CLI Fallback Initialization**
   - **Target**: Lines 27-100 (FallbackTyper class)
   - **Coverage Impact**: ~20 lines
   - **Description**: Test fallback CLI when typer is not available
   - **Assertions**:
     - Verify FallbackTyper initialization
     - Test command registration
     - Test help text printing

2. **Test: CLI Command Registration**
   - **Target**: Lines 36-42 (command decorator)
   - **Coverage Impact**: ~7 lines
   - **Description**: Test command registration mechanism
   - **Assertions**:
     - Verify command names registered correctly
     - Test signature extraction
     - Test decorator functionality

3. **Test: CLI Argument Parsing**
   - **Target**: Lines 66-89 (argument parsing)
   - **Coverage Impact**: ~24 lines
   - **Description**: Test CLI argument parsing and type conversion
   - **Assertions**:
     - Verify Path conversion
     - Test parameter matching
     - Test help flag handling

4. **Test: CLI Error Handling**
   - **Target**: Lines 73-76 (unknown command)
   - **Coverage Impact**: ~4 lines
   - **Description**: Test CLI error messages for invalid commands
   - **Assertions**:
     - Verify error message for unknown command
     - Test SystemExit with code 1
     - Test stderr output

5. **Test: Real Typer Integration** (if available)
   - **Target**: Lines beyond 100 (actual CLI commands)
   - **Coverage Impact**: ~60 lines
   - **Description**: Test actual tokenizer CLI commands
   - **Assertions**:
     - Test tokenizer inspection commands
     - Test encode/decode commands
     - Test vocabulary commands

---

## 🟡 HIGH Priority: loader.py (20.41% → 70%)

**Gap**: 49.59 percentage points | **Lines Needed**: ~15

### Test Cases

6. **Test: Special Token Defaults**
   - **Target**: Lines 30-36 (_ensure_special_tokens)
   - **Coverage Impact**: ~7 lines
   - **Description**: Test special token configuration
   - **Assertions**:
     - Verify pad_token fallback logic
     - Test eos_token fallback
     - Test add_special_tokens call

7. **Test: Load from File Path**
   - **Target**: Lines 39-43 (_load_from_file)
   - **Coverage Impact**: ~5 lines
   - **Description**: Test loading tokenizer from JSON file
   - **Assertions**:
     - Verify Tokenizer.from_file call
     - Test PreTrainedTokenizerFast wrapping
     - Test model_max_length setting

8. **Test: Load from Model Name (Remote)**
   - **Target**: Lines 49-57 (_load_from_model_name)
   - **Coverage Impact**: ~9 lines
   - **Description**: Test loading from HuggingFace model name
   - **Assertions**:
     - Verify load_from_pretrained call with allow_remote=True
     - Test cache_dir usage
     - Test local_files_only flag

9. **Test: Load from Model Name (Offline)**
   - **Target**: Lines 49-57 (_load_from_model_name with allow_remote=False)
   - **Coverage Impact**: ~5 lines (branch)
   - **Description**: Test offline loading behavior
   - **Assertions**:
     - Verify local_files_only=True when allow_remote=False
     - Test FileNotFoundError for missing files

10. **Test: Config Validation Errors**
    - **Target**: Lines 90-98 (error paths)
    - **Coverage Impact**: ~9 lines
    - **Description**: Test error handling for invalid configs
    - **Assertions**:
      - Test FileNotFoundError for missing tokenizer_file
      - Test ValueError for missing config keys

---

## 🟡 HIGH Priority: train_tokenizer.py (20.53% → 70%)

**Gap**: 49.47 percentage points | **Lines Needed**: ~68

### Test Cases

11. **Test: Tokenizer Training Workflow**
    - **Target**: Main training function lines
    - **Coverage Impact**: ~30 lines
    - **Description**: Test end-to-end tokenizer training
    - **Assertions**:
      - Verify training data processing
      - Test vocabulary building
      - Test model saving

12. **Test: Training Configuration**
    - **Target**: Config parsing lines
    - **Coverage Impact**: ~20 lines
    - **Description**: Test training configuration parsing
    - **Assertions**:
      - Verify config validation
      - Test default values
      - Test error handling

---

## 🟢 MEDIUM Priority: api.py (64.52% → 70%)

**Gap**: 5.48 percentage points | **Lines Needed**: ~1

### Test Cases

13. **Test: Import Error Fallbacks**
    - **Target**: Lines 59, 65-69 (exception handling)
    - **Coverage Impact**: ~6 lines
    - **Description**: Test fallback behavior when imports fail
    - **Assertions**:
      - Verify placeholder classes raise ImportError
      - Test error messages
      - Test deprecation warnings

14. **Test: Legacy Proxy Attribute Access**
    - **Target**: Lines 79, 87 (getattr paths)
    - **Coverage Impact**: ~2 lines
    - **Description**: Test legacy proxy forwarding
    - **Assertions**:
      - Verify attribute forwarding with warnings
      - Test ImportError when adapter unavailable

---

## ✅ COMPLETE: sentencepiece_adapter.py (83.33%)

**Status**: Already above 70% target

### Optional Enhancement

15. **Test: SentencePiece Error Paths** (Optional)
    - **Target**: Lines 44-45
    - **Coverage Impact**: ~2 lines
    - **Description**: Complete remaining coverage
    - **Assertions**:
      - Test specific error conditions

---

## ✅ COMPLETE: adapter.py (100%)

**Status**: Full coverage achieved - no tests needed

---

## 📊 Implementation Priority Matrix

| Priority | File | Tests | Lines | Effort | Impact |
|----------|------|-------|-------|--------|--------|
| 🔴 P1 | cli.py | 5 | ~115 | High | Critical |
| 🟡 P2 | loader.py | 5 | ~35 | Medium | High |
| 🟡 P3 | train_tokenizer.py | 2 | ~50 | Medium | High |
| 🟢 P4 | api.py | 2 | ~8 | Low | Medium |

**Total**: 14 tests mapped (exceeds 10 minimum requirement)

---

## 🎯 Coverage Projection

If all tests implemented successfully:

| File | Current | Projected | Change |
|------|---------|-----------|--------|
| cli.py | 12.45% | 70%+ | +57.55% |
| loader.py | 20.41% | 75%+ | +54.59% |
| train_tokenizer.py | 20.53% | 65%+ | +44.47% |
| api.py | 64.52% | 75%+ | +10.48% |
| **OVERALL** | **25.00%** | **70%+** | **+45%** |

---

## 🧪 Test Development Patterns

**Reference**: `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md`

### Pattern 1: Configuration Testing
```python
def test_loader_with_file_path(tmp_path):
    """Test loading tokenizer from file path."""
    config = {"tokenizer_file": str(tmp_path / "tokenizer.json")}
    # Create mock tokenizer file
    # Call load_tokenizer
    # Assert special tokens configured
```

### Pattern 2: Error Path Testing
```python
def test_loader_missing_file():
    """Test FileNotFoundError for missing tokenizer file."""
    config = {"tokenizer_file": "/nonexistent/path.json"}
    with pytest.raises(FileNotFoundError, match="tokenizer file not found"):
        load_tokenizer(config)
```

### Pattern 3: Mock External Dependencies
```python
@patch('src.tokenization.loader.AutoTokenizer')
def test_loader_remote(mock_tokenizer):
    """Test loading from HuggingFace model name."""
    config = {"model_name": "bert-base-uncased"}
    mock_tokenizer.from_pretrained.return_value = MagicMock()
    result = load_tokenizer(config, allow_remote=True)
    assert mock_tokenizer.from_pretrained.called
```

---

## 🚀 Implementation Roadmap

### Phase 1: Critical Priority (Pre-commit 5-6)
- Implement tests 1-5 for cli.py
- Target: cli.py from 12% → 70%

### Phase 2: High Priority (Pre-commit 7)
- Implement tests 6-12 for loader.py and train_tokenizer.py
- Target: loader.py from 20% → 75%, train_tokenizer.py from 20% → 65%

### Phase 3: Medium Priority (Pre-commit 8)
- Implement tests 13-14 for api.py
- Target: api.py from 64% → 75%

### Phase 4: Validation
- Run full coverage report
- Verify 70%+ overall coverage achieved
- Document any remaining gaps

---

## ✅ Success Criteria

- [ ] All 14 test cases implemented
- [ ] Each test has at least 3 assertions
- [ ] Overall coverage ≥70%
- [ ] All critical files (cli.py, loader.py) ≥70%
- [ ] No new failing tests introduced
- [ ] Tests follow patterns in TEST_DEVELOPMENT_PATTERNS.md

---

**Next Phase**: Pre-commit 5-8 - Comprehensive Test Implementation
**Plan**: `.codex/plans/pr_3145/02_comprehensive_test_implementation.md`

---

**Status**: ✅ Complete
**Generated**: 2026-02-04T14:40:00Z
**Artifacts**: 14 test cases mapped, 203+ lines to cover
