"""
Robust JSON Serialization for ML Checkpoints & Metadata

Provides:
- CustomJSONEncoder: Handles torch tensors, numpy arrays, datetime, UUID, Path, Decimal, complex
- safe_json_dumps: Validates data before serialization
- safe_json_dump: File-based serialization with atomic writes
- safe_json_loads: File-based deserialization with error handling
- Backward compatibility for old checkpoint formats

USAGE:
    from codex_ml.utils.json_serialization import CustomJSONEncoder, safe_json_dumps
    
    # Serialize complex types
    data = {'tensor': torch.randn(3, 3), 'timestamp': datetime.now()}
    json_str = safe_json_dumps(data)
    
    # File-based with safety guarantees
    safe_json_dump(data, Path('metadata.json'))
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
import tempfile
import warnings
from collections import OrderedDict
from contextlib import suppress
from dataclasses import asdict, is_dataclass
from datetime import UTC, date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
from uuid import UUID

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except (ImportError, AttributeError):
    np = None  # type: ignore[assignment]
    NUMPY_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = True
except (ImportError, AttributeError):
    torch = None  # type: ignore[assignment]
    TORCH_AVAILABLE = False


class CustomJSONEncoder(json.JSONEncoder):
    """
    Extended JSON encoder supporting ML types and custom objects.

    Handles:
    - torch.Tensor → {'__tensor__': [...], '__dtype__': 'float32', '__shape__': [...]}
    - numpy.ndarray → {'__ndarray__': [...], '__dtype__': 'float32', '__shape__': [...]}
    - numpy scalars (int64, float32, etc.) → Native Python types
    - datetime/date/time → ISO8601 format
    - UUID → String representation
    - Path → String path
    - Decimal → String representation (preserves precision)
    - complex → {'real': float, 'imag': float}
    - Enum → Value
    - dataclass → Dictionary
    - timedelta → {'seconds': float, '__timedelta__': True}
    - bytes → Base64 encoded string
    - set/frozenset → List
    - None/NaN/Inf → Handled safely

    Features:
    - Type markers for round-trip deserialization
    - NaN/Inf handling configurable
    - Comprehensive error logging
    - Graceful degradation (optional repr fallback)
    """

    def __init__(
        self,
        *args: Any,
        allow_nan: bool = False,
        strict_mode: bool = True,
        log_fallbacks: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize the encoder.

        Args:
            allow_nan: If False (default), raise TypeError for NaN/Inf values
            strict_mode: If True, raise errors instead of falling back to repr()
            log_fallbacks: If True, log when fallback repr() is used
            *args, **kwargs: Forwarded to json.JSONEncoder
        """
        super().__init__(*args, allow_nan=allow_nan, **kwargs)
        self.strict_mode = strict_mode
        self.log_fallbacks = log_fallbacks
        self._encoded_types: set[str] = set()

    def default(self, o: Any) -> Any:
        """
        Encode non-standard JSON types.

        Priority:
        1. Type-specific handlers (torch, numpy, datetime, etc.)
        2. Dataclass conversion (asdict)
        3. Fallback to repr() if strict_mode=False and log
        4. Raise TypeError if strict_mode=True
        """
        obj_type = type(o).__name__

        # ──── TORCH TENSORS ────────────────────────────────────────────
        if TORCH_AVAILABLE and isinstance(o, torch.Tensor):
            self._encoded_types.add("torch.Tensor")
            return {
                "__tensor__": True,
                "data": o.detach().cpu().numpy().tolist(),
                "dtype": str(o.dtype),
                "shape": list(o.shape),
                "requires_grad": o.requires_grad,
            }

        # ──── NUMPY ARRAYS ─────────────────────────────────────────────
        if NUMPY_AVAILABLE and isinstance(o, np.ndarray):
            self._encoded_types.add("numpy.ndarray")
            return {
                "__ndarray__": True,
                "data": o.tolist(),
                "dtype": str(o.dtype),
                "shape": list(o.shape),
            }

        # ──── NUMPY SCALARS ────────────────────────────────────────────
        if NUMPY_AVAILABLE and isinstance(o, np.generic):
            self._encoded_types.add(f"numpy.{obj_type}")
            return o.item()

        # ──── DATETIME TYPES ───────────────────────────────────────────
        if isinstance(o, datetime):
            self._encoded_types.add("datetime.datetime")
            return o.isoformat()
        if isinstance(o, date):
            self._encoded_types.add("datetime.date")
            return o.isoformat()
        if isinstance(o, time):
            self._encoded_types.add("datetime.time")
            return o.isoformat()
        if isinstance(o, timedelta):
            self._encoded_types.add("datetime.timedelta")
            return {
                "__timedelta__": True,
                "seconds": o.total_seconds(),
            }

        # ──── UUID ────────────────────────────────────────────────────
        if isinstance(o, UUID):
            self._encoded_types.add("uuid.UUID")
            return str(o)

        # ──── PATH ────────────────────────────────────────────────────
        if isinstance(o, Path):
            self._encoded_types.add("pathlib.Path")
            return str(o)

        # ──── DECIMAL ─────────────────────────────────────────────────
        if isinstance(o, Decimal):
            self._encoded_types.add("decimal.Decimal")
            return str(o)

        # ──── COMPLEX NUMBERS ─────────────────────────────────────────
        if isinstance(o, complex):
            self._encoded_types.add("complex")
            return {
                "__complex__": True,
                "real": float(o.real),
                "imag": float(o.imag),
            }

        # ──── ENUM ────────────────────────────────────────────────────
        if isinstance(o, Enum):
            self._encoded_types.add(f"enum.{o.__class__.__name__}")
            return o.value

        # ──── DATACLASS ────────────────────────────────────────────────
        if is_dataclass(o) and not isinstance(o, type):
            self._encoded_types.add(f"dataclass.{o.__class__.__name__}")
            return asdict(o)

        # ──── BYTES ────────────────────────────────────────────────────
        if isinstance(o, bytes):
            self._encoded_types.add("bytes")
            try:
                return o.decode("utf-8")
            except UnicodeDecodeError:
                import base64

                return {
                    "__bytes_b64__": True,
                    "data": base64.b64encode(o).decode("utf-8"),
                }

        # ──── SET/FROZENSET ────────────────────────────────────────────
        if isinstance(o, (set, frozenset)):
            self._encoded_types.add(f"builtins.{obj_type}")
            return list(o)

        # ──── FALLBACK ────────────────────────────────────────────────
        if self.strict_mode:
            msg = f"Object of type {obj_type} is not JSON serializable"
            raise TypeError(msg)
        else:
            if self.log_fallbacks:
                logger.warning(
                    "Fallback: encoding %s as repr (data may be lost): %s",
                    obj_type,
                    repr(o)[:100],
                )
            self._encoded_types.add(f"fallback.{obj_type}")
            return repr(o)


class CustomJSONDecoder(json.JSONDecoder):
    """
    Decoder for CustomJSONEncoder output.

    Reverses transformations:
    - {'__tensor__': ...} → torch.Tensor
    - {'__ndarray__': ...} → numpy.ndarray
    - {'__complex__': ...} → complex
    - {'__timedelta__': ...} → timedelta
    - {'__bytes_b64__': ...} → bytes
    - ISO8601 strings → datetime/date/time (when type info available)
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize decoder with custom object hook."""
        super().__init__(*args, object_hook=self._object_hook, **kwargs)
        self._decoded_types: set[str] = set()

    def _object_hook(self, obj: dict[str, Any]) -> Any:
        """Decode special objects marked with type indicators."""
        if not isinstance(obj, dict):
            return obj

        # ──── TORCH TENSOR ──────────────────────────────────────────
        if obj.get("__tensor__"):
            self._decoded_types.add("torch.Tensor")
            if not TORCH_AVAILABLE:
                logger.warning("Cannot restore torch.Tensor: torch not available")
                return obj
            try:
                import numpy as np

                data = np.array(obj["data"], dtype=obj.get("dtype", "float32"))
                tensor = torch.from_numpy(data)
                if obj.get("requires_grad"):
                    tensor = tensor.requires_grad_(True)
                return tensor
            except Exception as e:
                logger.error("Failed to decode torch.Tensor: %s", e)
                return obj

        # ──── NUMPY ARRAY ───────────────────────────────────────────
        if obj.get("__ndarray__"):
            self._decoded_types.add("numpy.ndarray")
            if not NUMPY_AVAILABLE:
                logger.warning("Cannot restore numpy.ndarray: numpy not available")
                return obj
            try:
                return np.array(obj["data"], dtype=obj.get("dtype", "float32"))
            except Exception as e:
                logger.error("Failed to decode numpy.ndarray: %s", e)
                return obj

        # ──── COMPLEX NUMBER ────────────────────────────────────────
        if obj.get("__complex__"):
            self._decoded_types.add("complex")
            try:
                return complex(obj.get("real", 0.0), obj.get("imag", 0.0))
            except Exception as e:
                logger.error("Failed to decode complex: %s", e)
                return obj

        # ──── TIMEDELTA ─────────────────────────────────────────────
        if obj.get("__timedelta__"):
            self._decoded_types.add("datetime.timedelta")
            try:
                return timedelta(seconds=obj.get("seconds", 0))
            except Exception as e:
                logger.error("Failed to decode timedelta: %s", e)
                return obj

        # ──── BASE64 BYTES ──────────────────────────────────────────
        if obj.get("__bytes_b64__"):
            self._decoded_types.add("bytes")
            try:
                import base64

                return base64.b64decode(obj.get("data", ""))
            except Exception as e:
                logger.error("Failed to decode bytes: %s", e)
                return obj

        return obj


def _validate_serializable(
    obj: Any, path: str = "", max_depth: int = 50, visited: Optional[set[int]] = None
) -> Optional[str]:
    """
    Validate that an object is JSON-serializable without actually serializing.

    Returns:
        None if serializable, or error message describing the first issue found.

    Args:
        obj: Object to validate
        path: Current path in nested structure (for error messages)
        max_depth: Maximum recursion depth before stopping
        visited: Set of object IDs seen (for cycle detection)
    """
    if visited is None:
        visited = set()

    # Prevent infinite recursion on circular references
    obj_id = id(obj)
    if obj_id in visited:
        return None  # Already validated
    visited.add(obj_id)

    if max_depth <= 0:
        return f"Maximum recursion depth exceeded at {path}"

    # Primitives are always serializable
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return None

    # Check for NaN and Inf
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return f"Non-finite float at {path}: {obj}"

    # Custom types that CustomJSONEncoder handles
    if isinstance(obj, (datetime, date, time, timedelta, UUID, Path, Decimal, complex)):
        return None
    if TORCH_AVAILABLE and isinstance(obj, torch.Tensor):
        return None
    if NUMPY_AVAILABLE and isinstance(obj, (np.ndarray, np.generic)):
        return None
    if isinstance(obj, (bytes, set, frozenset, Enum)):
        return None
    if is_dataclass(obj) and not isinstance(obj, type):
        # Validate dataclass fields
        for field_name, field_value in asdict(obj).items():
            err = _validate_serializable(
                field_value,
                path=f"{path}.{field_name}",
                max_depth=max_depth - 1,
                visited=visited,
            )
            if err:
                return err
        return None

    # Containers
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, (str, int, float, bool, type(None))):
                return f"Non-string dict key at {path}: {type(key).__name__}"
            err = _validate_serializable(
                value,
                path=f"{path}[{repr(key)}]",
                max_depth=max_depth - 1,
                visited=visited,
            )
            if err:
                return err
        return None

    if isinstance(obj, (list, tuple)):
        for idx, item in enumerate(obj):
            err = _validate_serializable(
                item,
                path=f"{path}[{idx}]",
                max_depth=max_depth - 1,
                visited=visited,
            )
            if err:
                return err
        return None

    # Unknown type
    return f"Non-serializable type at {path}: {type(obj).__name__}"


def safe_json_dumps(
    obj: Any,
    *,
    indent: Optional[int] = 2,
    sort_keys: bool = True,
    allow_nan: bool = False,
    strict_mode: bool = True,
    validate_first: bool = True,
    **kwargs: Any,
) -> str:
    """
    Safely serialize object to JSON string.

    Validates before serialization if validate_first=True.
    Uses CustomJSONEncoder for extended type support.

    Args:
        obj: Object to serialize
        indent: JSON indentation level (None for compact)
        sort_keys: Sort dictionary keys
        allow_nan: Allow NaN/Inf in output (not recommended)
        strict_mode: Raise error instead of repr() fallback
        validate_first: Validate object is serializable before encoding
        **kwargs: Additional json.dumps arguments

    Returns:
        JSON string

    Raises:
        TypeError: If object contains non-serializable types (strict_mode=True)
        ValueError: If validation fails
    """
    if validate_first:
        err = _validate_serializable(obj)
        if err:
            raise ValueError(f"Object not JSON serializable: {err}")

    try:
        return json.dumps(
            obj,
            cls=CustomJSONEncoder,
            indent=indent,
            sort_keys=sort_keys,
            allow_nan=allow_nan,
            strict_mode=strict_mode,
            **kwargs,
        )
    except TypeError as e:
        logger.error("JSON serialization failed: %s", e)
        raise


def safe_json_dump(
    obj: Any,
    path: Union[str, Path],
    *,
    indent: Optional[int] = 2,
    sort_keys: bool = True,
    allow_nan: bool = False,
    strict_mode: bool = True,
    validate_first: bool = True,
    atomic: bool = True,
    **kwargs: Any,
) -> Path:
    """
    Safely serialize object to JSON file.

    Uses atomic writes by default (write to temp file, then rename).
    Validates before serialization if validate_first=True.

    Args:
        obj: Object to serialize
        path: File path
        indent: JSON indentation level (None for compact)
        sort_keys: Sort dictionary keys
        allow_nan: Allow NaN/Inf in output (not recommended)
        strict_mode: Raise error instead of repr() fallback
        validate_first: Validate object is serializable before encoding
        atomic: Use atomic write (temp file + rename)
        **kwargs: Additional json.dump arguments

    Returns:
        Path object pointing to the written file

    Raises:
        TypeError: If object contains non-serializable types (strict_mode=True)
        IOError: If write operation fails
    """
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if validate_first:
        err = _validate_serializable(obj)
        if err:
            raise ValueError(f"Object not JSON serializable: {err}")

    json_str = safe_json_dumps(
        obj,
        indent=indent,
        sort_keys=sort_keys,
        allow_nan=allow_nan,
        strict_mode=strict_mode,
        validate_first=False,
        **kwargs,
    )

    if not atomic:
        # Simple write
        target_path.write_text(json_str, encoding="utf-8")
        return target_path

    # Atomic write: write to temp file, then rename
    tmp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=str(target_path.parent),
            delete=False,
            suffix=".tmp",
            encoding="utf-8",
        ) as tmp:
            tmp.write(json_str)
            tmp_path = Path(tmp.name)

        # Atomic rename
        os.replace(str(tmp_path), str(target_path))
        tmp_path = None
        logger.debug("Wrote JSON to %s (atomic)", target_path)
        return target_path

    except (IOError, OSError) as e:
        logger.error("Failed to write JSON to %s: %s", target_path, e)
        raise
    finally:
        if tmp_path is not None and tmp_path.exists():
            with suppress(OSError):
                tmp_path.unlink()


def safe_json_loads(
    text: Union[str, bytes],
    *,
    source: str = "<unknown>",
    strict: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Safely deserialize JSON string.

    Uses CustomJSONDecoder for extended type support.
    Includes detailed error reporting.

    Args:
        text: JSON string or bytes
        source: Source identifier for error messages
        strict: If True, raise on unknown types; if False, pass through
        **kwargs: Additional json.loads arguments

    Returns:
        Deserialized Python object

    Raises:
        json.JSONDecodeError: If JSON is malformed
        ValueError: If text is neither str nor bytes
    """
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.error("Failed to decode bytes as UTF-8 from %s: %s", source, e)
            raise
    elif not isinstance(text, str):
        raise ValueError(f"Expected str or bytes, got {type(text).__name__}")

    try:
        return json.loads(
            text,
            cls=CustomJSONDecoder,
            **kwargs,
        )
    except json.JSONDecodeError as e:
        logger.error("JSON decode error from %s at pos %d: %s", source, e.pos, e.msg)
        raise


def safe_json_load(
    path: Union[str, Path],
    *,
    strict: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Safely deserialize JSON from file.

    Uses CustomJSONDecoder for extended type support.
    Includes detailed error reporting.

    Args:
        path: File path
        strict: If True, raise on unknown types; if False, pass through
        **kwargs: Additional json.loads arguments

    Returns:
        Deserialized Python object

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If JSON is malformed
    """
    target_path = Path(path)
    if not target_path.exists():
        raise FileNotFoundError(f"JSON file not found: {target_path}")

    try:
        text = target_path.read_text(encoding="utf-8")
        return safe_json_loads(text, source=str(target_path), strict=strict, **kwargs)
    except json.JSONDecodeError as e:
        logger.error("JSON decode error in %s at line %d col %d: %s", target_path, e.lineno, e.colno, e.msg)
        raise
    except (IOError, OSError) as e:
        logger.error("Failed to read JSON file %s: %s", target_path, e)
        raise


def upgrade_checkpoint_metadata(
    old_format: dict[str, Any], from_version: str = "1.0", to_version: str = "2.0"
) -> dict[str, Any]:
    """
    Upgrade checkpoint metadata from old schema to new schema.

    Handles backward compatibility by transforming old metadata formats.

    Args:
        old_format: Legacy metadata dictionary
        from_version: Source schema version
        to_version: Target schema version

    Returns:
        Upgraded metadata in new format
    """
    if from_version == to_version:
        return old_format

    if from_version == "1.0" and to_version == "2.0":
        # Example upgrade: add schema_version field if missing
        upgraded = dict(old_format)
        if "_schema_version" not in upgraded:
            upgraded["_schema_version"] = "2.0"
            logger.info("Upgraded checkpoint metadata from v1.0 to v2.0")

        # Ensure timestamp format is ISO8601
        if "created_at" in upgraded and isinstance(upgraded["created_at"], (int, float)):
            try:
                dt = datetime.fromtimestamp(upgraded["created_at"], tz=UTC)
                upgraded["created_at"] = dt.isoformat()
                logger.debug("Converted timestamp to ISO8601 format")
            except (ValueError, OSError) as e:
                logger.warning("Could not convert timestamp: %s", e)

        return upgraded

    # Unknown upgrade path
    logger.warning("No upgrade path from %s to %s; returning original", from_version, to_version)
    return old_format


__all__ = [
    "CustomJSONEncoder",
    "CustomJSONDecoder",
    "safe_json_dumps",
    "safe_json_dump",
    "safe_json_loads",
    "safe_json_load",
    "upgrade_checkpoint_metadata",
    "_validate_serializable",
]
