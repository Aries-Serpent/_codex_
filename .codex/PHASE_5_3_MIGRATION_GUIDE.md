# PHASE 5.3: SYMBOL MIGRATION GUIDE

**Target**: _codex_ repository deprecation pathway  
**Version**: v2.0 migration preparation  
**Date**: 2026-07-03  
**Authority**: D-Mode (Full Autonomy)

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Migration Path by Module](#migration-path-by-module)
3. [API Changes](#api-changes)
4. [Code Examples](#code-examples)
5. [Timeline & Versioning](#timeline--versioning)
6. [Troubleshooting](#troubleshooting)

---

## OVERVIEW

This guide documents all deprecated symbols in the _codex_ codebase and provides clear migration paths to modern APIs. It's designed to help both internal teams and external users update their code.

### Migration Strategy

**Phase 1: Current (v1.x)** - Deprecation warnings issued  
**Phase 2: v2.0** - Old APIs still work but strongly discouraged  
**Phase 3: v3.0** - Old APIs removed  

### Key Principles

- ✅ **Backward Compatible**: Old code continues to work in v1.x and v2.0
- ✅ **Clear Migration Paths**: Every deprecated symbol has a direct replacement
- ✅ **Gradual Rollout**: Multiple release cycles for migration
- ✅ **Good Documentation**: Examples and best practices provided

---

## MIGRATION PATH BY MODULE

### 1. CHECKPOINT MODULE REFACTORING

**Status**: ⚠️ DEPRECATED (v1.x) → REMOVAL PLANNED (v3.0)

#### **1.1 Deprecated: `save_checkpoint()` Function**

**Affected Files**: 
- `src/utils/checkpoint.py` (definition)
- 4 downstream files importing this function

**Deprecation Notice**:
```python
# src/utils/checkpoint.py (line 45)
def save_checkpoint(...):
    """
    DEPRECATED: Use codex.checkpoint.save() instead.
    
    This function will be removed in v3.0.
    Migration deadline: Q3 2026
    """
    warnings.warn(
        "src.utils.checkpoint.save_checkpoint is deprecated; use "
        "codex.checkpoint.save() instead",
        DeprecationWarning,
        stacklevel=2
    )
```

#### **Migration Instructions**

**OLD CODE** (Deprecated):
```python
from src.utils.checkpoint import save_checkpoint

# Save model checkpoint
save_checkpoint(
    model=model,
    path="checkpoints/model.pt",
    optimizer=optimizer,
    epoch=42
)
```

**NEW CODE** (Recommended):
```python
from codex.checkpoint import save

# Save model checkpoint
save(
    model=model,
    path="checkpoints/model.pt",
    optimizer=optimizer,
    epoch=42
)
```

**Automatic Migration Script**:
```bash
# Run in your project directory
python -m codex.tools.migrate_checkpoint_imports
```

**Compatibility Layer** (if you can't migrate yet):
```python
# Add to your imports
from src.utils.checkpoint import save_checkpoint as save  # Compatibility alias
```

---

#### **1.2 Deprecated: `load_checkpoint()` Function**

**Status**: ⚠️ DEPRECATED (v1.x)

**Migration Instructions**

**OLD CODE**:
```python
from src.utils.checkpoint import load_checkpoint

model, optimizer, epoch = load_checkpoint(
    model_class=MyModel,
    path="checkpoints/model.pt"
)
```

**NEW CODE**:
```python
from codex.checkpoint import load

loaded_data = load(
    model_class=MyModel,
    path="checkpoints/model.pt"
)

model = loaded_data['model']
optimizer = loaded_data['optimizer']
epoch = loaded_data['epoch']
```

**Key Differences**:
- ✅ New API returns structured dict instead of tuple
- ✅ More explicit about what's being loaded
- ✅ Better error handling and validation

---

#### **1.3 Deprecated: `checkpoint_manager` Variable**

**Status**: ⚠️ DEPRECATED (v1.x)

**OLD CODE**:
```python
from src.utils.checkpoint import checkpoint_manager

checkpoint_manager.save(model, path)
checkpoint_manager.load(model_class, path)
```

**NEW CODE**:
```python
from codex.checkpoint import CheckpointManager

manager = CheckpointManager()
manager.save(model, path=path)
manager.load(model_class=model_class, path=path)
```

---

### 2. TOKENIZATION API REFACTORING

**Status**: ⚠️ DEPRECATED (v1.x) → REMOVAL PLANNED (v3.0)

#### **2.1 Deprecated: `legacy_tokenizer()` Function**

**Affected Files**:
- `src/tokenization/__init__.py` (definition)
- 5 downstream files using this function

**Deprecation Notice**:
```python
# src/tokenization/__init__.py (line 12)
def legacy_tokenizer(...):
    """
    DEPRECATED: Use TokenizerAdapter from codex_ml instead.
    
    Old API based on outdated tokenization approach.
    Migration deadline: Q3 2026
    """
    warnings.warn(
        "src.tokenization.api.legacy_tokenizer is deprecated; use "
        "codex_ml.tokenization.TokenizerAdapter instead",
        DeprecationWarning,
        stacklevel=2
    )
```

**Migration Instructions**

**OLD CODE**:
```python
from src.tokenization import legacy_tokenizer

tokenizer = legacy_tokenizer(model_name="gpt-2")
tokens = tokenizer.encode("Hello, world!")
```

**NEW CODE**:
```python
from codex_ml.tokenization import TokenizerAdapter

tokenizer = TokenizerAdapter(model_name="gpt-2")
tokens = tokenizer.encode("Hello, world!")
```

**Advantages of New API**:
- ✅ Unified tokenization across ML pipeline
- ✅ Better caching and performance
- ✅ Proper CUDA/GPU support
- ✅ Version consistency with ML models

---

#### **2.2 Module Path Change**

**OLD LOCATION**: `src/tokenization/adapter.py`  
**NEW LOCATION**: `src/codex_ml/tokenization/adapter.py`

**Impact**: 
- Files importing from old location: 1
- Status: Compatibility alias added

**Migration**:
```python
# OLD (still works, but deprecated)
from src.tokenization.adapter import TokenizerAdapter

# NEW (recommended)
from codex_ml.tokenization import TokenizerAdapter
```

---

### 3. CONFIGURATION SYSTEM REFACTORING

**Status**: ⚠️ DEPRECATED (v1.x) → REMOVAL PLANNED (v3.0)

#### **3.1 Deprecated Configuration Directories**

**Old Structure**:
```
config/              ← Deprecated (legacy)
config_legacy/       ← Deprecated (very old)
omegaconf/          ← Deprecated (incorrect use)
```

**New Structure**:
```
conf/               ← Primary (Hydra-based)
conf_legacy/        ← Backward compatibility
hydra_extra/        ← Extended configs
```

#### **3.2 Configuration Loading Migration**

**OLD CODE**:
```python
from src.codex_init import load_config

config = load_config(
    config_path="config/",
    config_name="base",
    allow_deprecated=True  # ⚠️ Deprecated
)
```

**NEW CODE**:
```python
from codex.config import load_config

config = load_config(
    config_path="conf/",
    config_name="base"
)
```

**Safer Alternative** (if you need custom logic):
```python
from hydra import compose, initialize_config_dir
from pathlib import Path

config_dir = Path("conf").absolute()

with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
    config = compose(config_name="base")
```

---

#### **3.3 Deprecated Methods in ConfigLoader**

**OLD API**:
```python
loader = ConfigLoader()
config = loader.load_from_deprecated(
    directory="config",
    config_name="base.yaml"
)
```

**NEW API**:
```python
loader = ConfigLoader()
config = loader.load(
    directory="conf",
    config_name="base.yaml"
)
```

---

### 4. LOGGING API UPDATES

**Status**: ✅ NEW API (v1.x+) - No deprecation needed

**Current Best Practice**:
```python
from codex.logging.structured_logger import logger

logger.info("Message", extra={"key": "value"})
logger.error("Error occurred", exc_info=True)
```

**No Migration Needed** - This API is current and stable.

---

## API CHANGES

### Detailed Comparison Table

| Aspect | Old API | New API | Migration Effort | Impact |
|--------|---------|---------|------------------|--------|
| Checkpoint save | `save_checkpoint()` | `checkpoint.save()` | LOW (1 line) | 4 files |
| Checkpoint load | `load_checkpoint()` | `checkpoint.load()` | LOW (2 lines) | 3 files |
| Tokenizer | `legacy_tokenizer()` | `TokenizerAdapter()` | MEDIUM (5 lines) | 5 files |
| Config load | `load_from_deprecated()` | `compose()` | MEDIUM (3 lines) | 6 files |
| Logger | `compat_logger` | `structured_logger` | NONE (already migrated) | 0 files |

---

## CODE EXAMPLES

### Example 1: Complete Migration - Checkpoint Management

**Scenario**: Updating a training script to use new checkpoint API

**BEFORE** (Old code):
```python
# train.py (old style)
import torch
from src.utils.checkpoint import save_checkpoint, load_checkpoint

class Trainer:
    def __init__(self, model, optimizer):
        self.model = model
        self.optimizer = optimizer
        self.start_epoch = 0
    
    def load_latest_checkpoint(self, checkpoint_dir):
        try:
            self.model, self.optimizer, self.start_epoch = load_checkpoint(
                model_class=type(self.model),
                path=f"{checkpoint_dir}/latest.pt"
            )
        except FileNotFoundError:
            print("No checkpoint found, starting fresh")
    
    def save_checkpoint(self, checkpoint_dir, epoch):
        save_checkpoint(
            model=self.model,
            path=f"{checkpoint_dir}/epoch_{epoch}.pt",
            optimizer=self.optimizer,
            epoch=epoch
        )
    
    def train_epoch(self, data_loader, epoch):
        for batch in data_loader:
            # Training logic
            pass
        self.save_checkpoint("./checkpoints", epoch)
```

**AFTER** (New code):
```python
# train.py (new style)
import torch
from codex.checkpoint import CheckpointManager, CheckpointConfig

class Trainer:
    def __init__(self, model, optimizer):
        self.model = model
        self.optimizer = optimizer
        self.start_epoch = 0
        
        # Initialize checkpoint manager with config
        config = CheckpointConfig(
            keep_best=3,
            save_frequency=1,
            validation_metric="loss"
        )
        self.checkpoint_manager = CheckpointManager(config=config)
    
    def load_latest_checkpoint(self, checkpoint_dir):
        """Load latest checkpoint or start fresh"""
        try:
            loaded = self.checkpoint_manager.load_latest(
                checkpoint_dir=checkpoint_dir,
                model_class=type(self.model)
            )
            self.model = loaded['model']
            self.optimizer = loaded['optimizer']
            self.start_epoch = loaded['epoch']
        except FileNotFoundError:
            print("No checkpoint found, starting fresh")
    
    def save_checkpoint(self, checkpoint_dir, epoch, metrics=None):
        """Save checkpoint with validation metrics"""
        self.checkpoint_manager.save(
            checkpoint_dir=checkpoint_dir,
            epoch=epoch,
            model=self.model,
            optimizer=self.optimizer,
            metrics=metrics  # ✨ New: track metrics
        )
    
    def train_epoch(self, data_loader, epoch):
        metrics = {'loss': 0.0}
        for batch in data_loader:
            # Training logic
            pass
        self.save_checkpoint("./checkpoints", epoch, metrics=metrics)
```

**Benefits of Migration**:
- ✅ Better checkpoint management
- ✅ Automatic cleanup of old checkpoints
- ✅ Integration with metrics tracking
- ✅ Clearer API intent

---

### Example 2: Tokenization Migration

**BEFORE**:
```python
from src.tokenization import legacy_tokenizer

# Initialize
tokenizer = legacy_tokenizer("gpt2")

# Use
text = "Hello, world!"
tokens = tokenizer.encode(text)
decoded = tokenizer.decode(tokens)
```

**AFTER**:
```python
from codex_ml.tokenization import TokenizerAdapter

# Initialize
tokenizer = TokenizerAdapter(model_name="gpt2")

# Use (identical API - easy migration!)
text = "Hello, world!"
tokens = tokenizer.encode(text)
decoded = tokenizer.decode(tokens)

# New features available
tokens_with_attention = tokenizer.encode_with_attention_mask(text)
```

---

### Example 3: Configuration Migration

**BEFORE**:
```python
from src.codex_init import load_config

# Load from deprecated directory
config = load_config(
    config_path="config/",
    config_name="training",
    allow_deprecated=True,
    strict_mode=False
)

print(config.batch_size)
```

**AFTER**:
```python
from hydra import compose, initialize_config_dir
from pathlib import Path
import yaml

# Method 1: Use Hydra (recommended)
config_dir = Path("conf").absolute()
with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
    config = compose(config_name="training")

# Method 2: Direct YAML loading (simple approach)
with open("conf/training.yaml") as f:
    config = yaml.safe_load(f)

print(config['batch_size'])
```

---

## TIMELINE & VERSIONING

### Release Schedule

**Current Release: v1.4.x**
```
Status: ✅ ACTIVE
- Old APIs functional with deprecation warnings
- New APIs recommended in all new code
- Migration tools available
- Documentation updated
```

**Planned Release: v2.0** (Q3 2026)
```
Status: 📅 PLANNED
- Old APIs still functional (backward compatible)
- Deprecation warnings become more prominent
- Migration helpers bundled in package
- Migration deadline notifications
```

**Future Release: v3.0** (Q1 2027)
```
Status: 🔮 FUTURE
- Old APIs removed completely
- Codebase cleaned up
- Performance optimizations enabled
- Breaking changes documented
```

### Migration Timeline

| Date | Milestone | Action |
|------|-----------|--------|
| **NOW (v1.4.x)** | Phase 1: Warnings | Deprecation warnings issued |
| **Q2 2026** | Phase 1.5: Communication | Blog post + docs migration guide |
| **Q3 2026** | Phase 2: v2.0 Release | Old APIs still work, new recommended |
| **Q4 2026** | Phase 2.5: Hard deadline | Final call for migration |
| **Q1 2027** | Phase 3: v3.0 Release | Old APIs removed |

### Version Compatibility

**Backward Compatibility Matrix**:

| Your Code | v1.4.x | v2.0 | v3.0 |
|-----------|--------|------|------|
| Old API | ✅ Works | ✅ Works (warns) | ❌ Broken |
| New API | ✅ Works | ✅ Works | ✅ Works |

---

## TROUBLESHOOTING

### Issue: "DeprecationWarning: ... is deprecated"

**Cause**: You're using an old API

**Solution**:
1. Identify which API is deprecated from the warning message
2. Look up the API in this guide (search for "DEPRECATED")
3. Follow the migration instructions
4. Test your code

**Example**:
```python
# Error message:
# DeprecationWarning: src.utils.checkpoint.save_checkpoint is deprecated

# Solution: Replace with
from codex.checkpoint import save
save(model=model, path=path, optimizer=optimizer)
```

---

### Issue: "ModuleNotFoundError: No module named 'src.utils.checkpoint'"

**Cause**: You're importing from old module location

**Solution**:
```python
# OLD (broken)
from src.utils.checkpoint import save_checkpoint

# NEW (correct)
from codex.checkpoint import save
```

---

### Issue: "ImportError: cannot import name 'legacy_tokenizer'"

**Cause**: Module was reorganized

**Solution**:
```python
# OLD (broken)
from src.tokenization import legacy_tokenizer

# NEW (correct)
from codex_ml.tokenization import TokenizerAdapter
```

---

### Issue: "TypeError: load_checkpoint() takes X positional arguments but Y were given"

**Cause**: API signature changed

**Solution**: Review the new API signature and update your call:

```python
# OLD (broken)
load_checkpoint(model_class, path, strict=True, device="cpu")

# NEW (correct)
load(
    model_class=model_class,
    path=path,
    config={'strict': True, 'device': 'cpu'}
)
```

---

## MIGRATION CHECKLIST

Use this checklist to track your migration progress:

- [ ] Audit: Find all deprecated imports in your codebase
- [ ] Plan: Create migration plan for each deprecated API
- [ ] Implement: Update code to use new APIs
- [ ] Test: Run full test suite after migration
- [ ] Verify: Ensure all deprecation warnings are gone
- [ ] Document: Update internal docs with new patterns
- [ ] Deploy: Release updated code

**Find deprecated imports**:
```bash
# Search for deprecated patterns
grep -r "from src.utils.checkpoint" .
grep -r "legacy_tokenizer" .
grep -r "load_from_deprecated" .
```

**Run deprecation check**:
```bash
python -W always -m pytest tests/  # Show all deprecation warnings
```

---

## ADDITIONAL RESOURCES

### Documentation
- 📖 [Checkpoint API Reference](../docs/api/checkpoint.md)
- 📖 [Tokenization Guide](../docs/api/tokenization.md)
- 📖 [Configuration System](../docs/config/hydra-guide.md)

### Tools
- 🔧 [Automated Migration Script](../scripts/migrate_deprecated_imports.py)
- 🔧 [Deprecation Checker](../scripts/check_deprecations.py)
- 🔧 [API Compatibility Layer](../codex/compat/deprecated.py)

### Support
- 💬 [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- 🐛 [Report Issues](https://github.com/Aries-Serpent/_codex_/issues)
- 📧 Contact: @mbaetiong

---

## SUMMARY

This migration guide provides a clear path from deprecated APIs to modern, maintained APIs. While old code will continue to work for several more releases, we encourage all users to migrate at their convenience.

**Key Takeaways**:
- ✅ Migration is **gradual** - you have time
- ✅ All old APIs have **clear replacements**
- ✅ New APIs are **backward compatible**
- ✅ Tools are **provided** to help with migration
- ✅ Support is **available** during transition

---

**Migration Guide Version**: 1.0  
**Last Updated**: 2026-07-03  
**Authority**: D-Mode (Full Autonomy) ✅  
**Campaign**: Phase 3-5 Multi-Agent Deployment

For questions or updates, contact the Reference Updater Agent via GitHub Issues.
