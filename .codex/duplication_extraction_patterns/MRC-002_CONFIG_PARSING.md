# Pattern MRC-002: Configuration Parsing Templates Consolidation

## Pattern Overview

**Pattern ID:** MRC-002  
**Category:** Tier 1b - Mid-Complexity Refactorings  
**Timeline:** Week 2 of Phase 6 Wave 2  
**LOC Reduction Target:** 420 lines  
**Status:** ✅ EXTRACTED

## Problem Statement

Configuration parsing is implemented repeatedly across:
- ML training module (`src/codex_ml/config.py`, 2 implementations)
- Core configs module (`src/codex/configs/config.py`, 2 implementations)
- CLI module (`src/codex/cli.py`, 1 implementation)

Common patterns duplicated:
- Config object to dict/JSON/YAML conversion
- Config loading from files
- Config validation against field constraints
- Config serialization/deserialization

## Solution

Created `src/codex/consolidation/config.py` with:
- **BaseConfig**: Abstract base class for all configuration objects
- **ConfigValidator**: Validation utilities for config objects
- **ConfigParser**: Generic configuration parser with validation
- **DefaultConfig**: Default configuration template

## Implementation Details

### Core Classes

```python
class BaseConfig:
    """Base class for all configuration objects."""
    - to_dict(): Convert config to dictionary
    - to_json(): Convert to JSON string
    - to_yaml(): Convert to YAML string
    - from_dict(): Create from dictionary
    - from_json(): Create from JSON string
    - from_yaml(): Create from YAML string
    - from_file(): Load from file (auto-detects format)
    - save_to_file(): Save to file

class ConfigValidator:
    """Validate configuration objects."""
    - validate_required_fields(): Check required fields present
    - validate_field_ranges(): Validate numeric ranges
    - validate_choices(): Validate enum-like choices

class ConfigParser(Generic[T]):
    """Generic configuration parser with validation."""
    - parse(): Parse and validate config
    - parse_file(): Parse from file
    - validate(): Run all validators
```

## Migration Path

### Before (Duplicated)
```python
# src/codex_ml/config.py
@dataclass
class MLConfig:
    batch_size: int = 32
    learning_rate: float = 0.001
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# src/codex/configs/config.py
@dataclass
class AppConfig:
    debug: bool = False
    timeout: int = 30
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
```

### After (Consolidated)
```python
from src.codex.consolidation.config import BaseConfig

@dataclass
class MLConfig(BaseConfig):
    batch_size: int = 32
    learning_rate: float = 0.001

@dataclass
class AppConfig(BaseConfig):
    debug: bool = False
    timeout: int = 30

# Now both have to_dict(), from_dict(), to_json(), to_yaml(), etc.
```

## Metrics

- **Lines Created:** 182 LOC (new consolidation module)
- **Lines to Remove:** 420 LOC (from distributed config files)
- **Net Reduction:** 238 LOC
- **Exports:** 4 (BaseConfig, ConfigValidator, ConfigParser, DefaultConfig)
- **Module Dependencies:** 5 (abc, dataclasses, pathlib, json, yaml)

## Coverage

- ✅ Config object to dict/JSON/YAML conversion
- ✅ Config loading from files (auto-format detection)
- ✅ Config validation (required fields, ranges, choices)
- ✅ Config serialization/deserialization
- ✅ Dataclass and dict-based config support

## Features

### Format Support
- JSON files (.json)
- YAML files (.yaml, .yml)
- Python dictionaries
- Dataclass objects

### Validation
- Required field validation
- Numeric range validation
- Choice/enum validation
- Custom validator support

## Consumers to Update

1. `src/codex_ml/config.py` - Inherit from BaseConfig
2. `src/codex/configs/config.py` - Inherit from BaseConfig
3. `src/codex/cli.py` - Use ConfigParser for config loading
4. ML training modules - Use BaseConfig methods

## Backward Compatibility

✅ All existing config APIs maintained.  
✅ Subclasses automatically get all BaseConfig methods.  
✅ Existing config files work without changes.

## Testing

- Unit tests for format conversions (JSON, YAML, dict)
- Integration tests with real config files
- Validation tests for edge cases
- Performance tests for large configs

## Related Patterns

- **MRC-001** (Test fixtures): Can create mock configs
- **MRC-003** (Mocks): Uses config factory for mock setup
- **LRC-002** (Validation decorators): Can validate configs
