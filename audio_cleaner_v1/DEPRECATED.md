# Audio Cleaner v1 - DEPRECATED

**Status:** DEPRECATED as of 2026-01-09  
**Replaced By:** `src/services/audio/`

---

## Migration Notice

This directory has been deprecated as part of **PS-08: Microservice Root Cleanup**.

The audio cleaner functionality has been moved to conform with the monolith architecture:

### New Locations

| Old Path | New Path |
|----------|----------|
| `audio_cleaner_v1/src/` | `src/services/audio/` |
| `audio_cleaner_v1/config/` | `configs/services/` |
| `audio_cleaner_v1/tests/` | `tests/services/audio/` |

### Updated Import Paths

**Before:**
```python
from audio_cleaner_v1.src.core import AudioCleaner
from audio_cleaner_v1.src.cli.smart_cli import main
```

**After:**
```python
from services.audio.core import AudioCleaner
from services.audio.cli.smart_cli import main
```

### Updated CLI Usage

**Before:**
```bash
python -m audio_cleaner_v1.src.cli.smart_cli /path/to/audio.mp3
```

**After:**
```bash
python -m services.audio.cli.smart_cli /path/to/audio.mp3
```

---

## Why This Change?

Per the Cognitive Brain Architecture:

1. **Monolith Structure:** All services should live under `src/services/`
2. **Clean Repository Root:** No microservice directories at root level
3. **Consistent Configuration:** All configs under `configs/`
4. **Unified Testing:** All tests under `tests/`

---

## Timeline

- **Deprecated:** 2026-01-09
- **Removal Scheduled:** v3.0.0 (after verification of all consumers migrated)

---

## DO NOT USE

This directory is retained only for backward compatibility during migration.
All new development should use `src/services/audio/`.

---

**Maintained By:** GitHub Copilot  
**Migration Planset:** PS-08
