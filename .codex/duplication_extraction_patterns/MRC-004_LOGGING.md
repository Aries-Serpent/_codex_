# Pattern MRC-004: Logging Setup Patterns Consolidation

**Status:** ✅ EXTRACTED  
**LOC Reduction Target:** 340 lines  
**Lines Created:** 260 LOC (new consolidation module)  
**Net Reduction:** 80 LOC

## Overview

Consolidated logging initialization patterns from CLI (3), ML training (2), and async runtime (1) into `src/codex/consolidation/logging_bootstrap.py`.

## Key Classes

- **LogLevel**: Enum for log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **LogFormats**: Predefined log formats (SIMPLE, DETAILED, JSON, CONTEXT)
- **LoggerBootstrap**: Static methods for logger configuration
  - configure_console_logging()
  - configure_file_logging()
  - configure_dual_logging()
  - configure_syslog_logging()
- **ContextLogger**: Logger with context-aware formatting
- **LoggingConfig**: Configuration class for logging setup

## Features

- Multiple output targets (console, file, syslog, dual)
- Rotating file handlers
- Predefined and custom formats
- Context tracking
- Easy one-line setup

## Pattern

```python
# Before: Duplicated setup
import logging
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# After: Unified bootstrap
from src.codex.consolidation.logging_bootstrap import LoggerBootstrap
logger = LoggerBootstrap.configure_console_logging(__name__)
```

## Consumers

- CLI modules
- ML training scripts
- Async utilities
- API services
