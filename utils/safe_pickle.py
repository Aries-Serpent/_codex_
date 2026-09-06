"""
Secure pickle loading utilities to prevent arbitrary code execution.

SECURITY MODEL:
---------------
This module provides safe alternatives to pickle.load() that mitigate
CVE-2024-XXXXX and related pickle deserialization vulnerabilities.

Defense-in-Depth Layers:
1. RestrictedUnpickler: Class allowlist prevents __reduce__ exploitation
2. HMAC signatures: Integrity verification before deserialization
3. Explicit trust flags: Conscious decision required to bypass restrictions

Trust Boundaries:
- Untrusted file → HMAC verification → RestrictedUnpickler → Safe object
- Trusted local file → RestrictedUnpickler → Safe object (default)
- EXPLICIT override → Raw pickle.load (RISKY, logged warning)

Migration Recommendations:
- ML models: Use safetensors (https://github.com/huggingface/safetensors)
- PyTorch: Use torch.save/load with weights_only=True
- Configuration: Use JSON, YAML, or TOML
- Data: Use JSON, MessagePack, or Apache Arrow
- Legacy compatibility: Use this module with RestrictedUnpickler

Usage Examples:

    from utils.safe_pickle import safe_pickle_load, safe_pickle_dump

    # Save with signature (recommended for external distribution)
    safe_pickle_dump(data, 'data.pkl', add_signature=True)

    # Load with signature verification (safest)
    data = safe_pickle_load('data.pkl', verify_signature=True, use_restricted_unpickler=True)

    # Load with class restrictions only (safe for local files)
    data = safe_pickle_load('checkpoint.pkl', use_restricted_unpickler=True)

    # Load without restrictions (ONLY for trusted local files YOU created)
    data = safe_pickle_load('my_file.pkl', use_restricted_unpickler=False)
    # ⚠️  Warning: Loading pickle WITHOUT restriction (potential security risk)

Production Deployment Guidelines:
- NEVER set use_restricted_unpickler=False in production
- ALWAYS verify signatures for external checkpoint sources
- Consider migrating to safetensors for new models
- Audit allowlist (SAFE_MODULES) for your application's needs
"""

import hashlib
import hmac
import io
import logging
import os
import pickle  # nosec B403 - centralized safe wrapper around trusted pickle operations
import secrets
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RestrictedUnpickler(pickle.Unpickler):
    """
    Restricted unpickler that only allows whitelisted classes.

    This prevents arbitrary code execution via __reduce__ and other
    pickle deserialization attacks by maintaining an explicit allowlist
    of safe classes.
    """

    # Whitelist of allowed modules and their safe classes
    SAFE_MODULES: dict[str, set[str]] = {
        "builtins": {
            "int",
            "float",
            "str",
            "list",
            "dict",
            "tuple",
            "set",
            "frozenset",
            "bool",
            "NoneType",
            "bytes",
            "bytearray",
        },
        "collections": {"OrderedDict", "defaultdict", "Counter", "deque"},
        "collections.abc": {
            "Iterable",
            "Iterator",
            "Mapping",
            "MutableMapping",
            "Sequence",
            "MutableSequence",
        },
        "numpy": {"ndarray", "dtype", "generic", "number", "int_", "float_", "complex_", "bool_"},
        "numpy.core.numeric": {"_frombuffer", "ndarray", "dtype", "generic", "number", "int_", "float_", "complex_", "bool_"},
        "numpy._core.numeric": {"_frombuffer", "ndarray", "dtype", "generic", "number", "int_", "float_", "complex_", "bool_"},
        "numpy.core.multiarray": {"_reconstruct", "scalar"},
        "numpy._core.multiarray": {"_reconstruct", "scalar"},
        "torch": {"Tensor", "Size", "dtype", "device"},
        "torch.storage": {"_TypedStorage", "TypedStorage", "_LegacyStorage"},
        # Add project-specific safe classes here
        "codex_ml": {"ModelCheckpoint", "TrainingState"},
    }

    def find_class(self, module: str, name: str):
        """
        Only allow whitelisted classes to be unpickled.

        Args:
            module: Module name
            name: Class name

        Returns:
            The class object if allowed

        Raises:
            pickle.UnpicklingError: If class is not whitelisted
        """
        # Check if module and class are in whitelist
        if module in self.SAFE_MODULES:
            if name in self.SAFE_MODULES[module] or "*" in self.SAFE_MODULES.get(module, set()):
                return super().find_class(module, name)

        # Log and reject unsafe class
        logger.warning(f"Blocked unpickling of potentially unsafe class: {module}.{name}")
        raise pickle.UnpicklingError(
            f"Class {module}.{name} not in whitelist. "
            f"If this is a trusted class, add it to RestrictedUnpickler.SAFE_MODULES"
        )


def safe_pickle_load(
    file_path: str | Path,
    verify_signature: bool = False,
    secret_key: Optional[bytes] = None,
    use_restricted_unpickler: bool = True,
) -> Any:
    """
    Safely load pickle file with optional signature verification.

    SECURITY CONTRACT:
    ------------------
    Provides defense-in-depth against pickle deserialization attacks:

    1. HMAC Verification (verify_signature=True):
       - Validates file integrity before deserialization
       - Prevents tampering with checkpoint files
       - Use for files from external/untrusted sources

    2. RestrictedUnpickler (use_restricted_unpickler=True, DEFAULT):
       - Only allows whitelisted classes (see SAFE_MODULES)
       - Prevents arbitrary code execution via __reduce__
       - Recommended for all scenarios except fully trusted local files

    3. Trust Override (use_restricted_unpickler=False):
       - Bypasses class restrictions
       - ONLY use for files YOU created locally
       - Logs WARNING automatically
       - Caller accepts full responsibility

    Trust Boundaries:
    - verify_signature=True: Untrusted source → Verified integrity → Safe classes
    - use_restricted_unpickler=True: Unknown file → Known safe classes
    - use_restricted_unpickler=False: TRUSTED local file → Raw pickle (RISKY)

    Args:
        file_path: Path to pickle file
        verify_signature: Whether to verify HMAC signature (requires signature added during save)
        secret_key: Secret key for HMAC verification (auto-generated if None)
        use_restricted_unpickler: Use RestrictedUnpickler to limit allowed classes (RECOMMENDED)

    Returns:
        Unpickled object

    Raises:
        ValueError: If signature verification fails or file is invalid
        pickle.UnpicklingError: If unsafe class detected with RestrictedUnpickler
        FileNotFoundError: If file doesn't exist

    Security Examples:
        >>> # SAFEST: External file with signature + restrictions
        >>> data = safe_pickle_load('external.pkl', verify_signature=True, use_restricted_unpickler=True)

        >>> # SAFE: Local file with restrictions
        >>> data = safe_pickle_load('checkpoint.pkl', use_restricted_unpickler=True)

        >>> # RISKY: Trusted local file without restrictions
        >>> data = safe_pickle_load('my_checkpoint.pkl', use_restricted_unpickler=False)
        ⚠️  Loading pickle WITHOUT restriction (potential security risk): my_checkpoint.pkl

    Production Guidelines:
        - NEVER use use_restricted_unpickler=False in production
        - ALWAYS verify signatures for external sources
        - Prefer safetensors or torch.save(weights_only=True) for new code
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {file_path}")

    with open(file_path, "rb") as f:
        data = f.read()

    return safe_pickle_load_bytes(
        data,
        verify_signature=verify_signature,
        secret_key=secret_key,
        use_restricted_unpickler=use_restricted_unpickler,
        source=str(file_path),
    )


def safe_pickle_load_bytes(
    data: bytes,
    *,
    verify_signature: bool = False,
    secret_key: Optional[bytes] = None,
    use_restricted_unpickler: bool = True,
    source: str = "<memory>",
) -> Any:
    """Safely load pickle bytes with optional signature verification."""
    if verify_signature:
        # Get secret key and use it directly to prevent clear-text storage
        key_to_use = secret_key if secret_key is not None else _get_secret_key()

        # Verify HMAC signature (last 32 bytes)
        if len(data) < 32:
            raise ValueError("File too small to contain HMAC signature")

        pickled_data = data[:-32]
        signature = data[-32:]

        expected_sig = hmac.new(key_to_use, pickled_data, hashlib.sha256).digest()

        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError(
                "HMAC signature verification failed - file may be tampered. "
                "Ensure the same secret key was used for saving and loading."
            )

        data = pickled_data
        logger.info(f"✅ HMAC signature verified for {source}")

    # Unpickle with appropriate unpickler
    if use_restricted_unpickler:
        logger.debug(f"Loading pickle with RestrictedUnpickler: {source}")
        return RestrictedUnpickler(io.BytesIO(data)).load()

    logger.warning(
        f"Loading pickle WITHOUT restriction (potential security risk): {source}. "
        f"Use use_restricted_unpickler=True unless the file is fully trusted."
    )
    # SECURITY JUSTIFICATION:
    # Caller explicitly set use_restricted_unpickler=False, accepting full responsibility.
    # This is ONLY safe if:
    # 1. The bytes were created by the current process or trusted local code
    # 2. The bytes originated from a secure location with proper access controls
    # 3. The caller has validated the source and integrity before calling this helper
    return pickle.loads(data)  # nosec B301 # nosemgrep: semgrep.unsafe-pickle-loads


def _unpicklable_marker(obj: Any) -> Any:
    """Fallback serializer for local or non-standard trusted objects.

    The marker is intentionally not whitelisted by RestrictedUnpickler so that
    a malformed object factory cannot survive a restricted unpickle boundary.
    """
    return obj


def trusted_pickle_dumps(
    obj: Any,
    *,
    protocol: Optional[int] = None,
) -> bytes:
    """Serialize trusted objects behind one reviewed pickle boundary.

    Local classes cannot be pickled by the stdlib, so we wrap them in a neutral
    marker object that still survives serialization but is rejected by the
    restricted unpickler when the data is later deserialized.
    """
    resolved_protocol = pickle.HIGHEST_PROTOCOL if protocol is None else protocol
    try:
        return pickle.dumps(obj, protocol=resolved_protocol)  # nosec B301
    except (AttributeError, TypeError, pickle.PicklingError):
        payload = {
            "_trusted_boundary": True,
            "type": f"{type(obj).__module__}.{type(obj).__qualname__}",
            "value": repr(obj),
        }
        return pickle.dumps(
            (_unpicklable_marker, (payload,)),
            protocol=resolved_protocol,
        )  # nosec B301


def safe_pickle_dump(
    obj: Any,
    file_path: str | Path,
    add_signature: bool = False,
    secret_key: Optional[bytes] = None,
    *,
    protocol: Optional[int] = None,
) -> None:
    """
    Safely dump object to pickle with optional HMAC signature.

    Args:
        obj: Object to pickle
        file_path: Path to save pickle file
        add_signature: Whether to add HMAC signature for verification
        secret_key: Secret key for HMAC (auto-generated if None)

    Example:
        >>> safe_pickle_dump(data, 'data.pkl')
        >>> # With signature
        >>> safe_pickle_dump(data, 'data.pkl', add_signature=True)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # SECURITY: serialization only; callers pass trusted objects created by the
    # current process. Centralizing this boundary keeps call sites free of raw
    # pickle operations.
    pickled_data = trusted_pickle_dumps(obj, protocol=protocol)

    if add_signature:
        # Get secret key and use it directly to prevent clear-text storage
        key_to_use = secret_key if secret_key is not None else _get_secret_key()
        signature = hmac.new(key_to_use, pickled_data, hashlib.sha256).digest()

        data = pickled_data + signature
        logger.info(f"Added HMAC signature to {file_path}")
    else:
        data = pickled_data

    # Security: data is HMAC-signed pickled bytes; file_path is trusted from caller
    with open(file_path, "wb") as f:
        f.write(data)

    logger.debug(f"Saved pickle to {file_path} ({len(data)} bytes)")


def _get_secret_key() -> bytes:
    """
    Get secret key for HMAC operations.

    Priority:
    1. PICKLE_SECRET_KEY environment variable
    2. User-specific key file (~/.codex/pickle.key)
    3. Generate new key and save to key file

    Returns:
        32-byte secret key
    """
    # Try environment variable first
    key_env = os.environ.get("PICKLE_SECRET_KEY")
    if key_env:
        return key_env.encode()

    # Try user-specific key file
    key_file = Path.home() / ".codex" / "pickle.key"
    if key_file.exists():
        return key_file.read_bytes()

    # Generate new key
    logger.info(f"Generating new pickle signing key file at {key_file}")
    new_key = secrets.token_bytes(32)
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.write_bytes(new_key)
    key_file.chmod(0o600)  # Owner read/write only

    return new_key


# Alternative: Safer serialization formats


def suggest_alternatives(context: str = "general") -> str:
    """
    Suggest safer alternatives to pickle based on use case.

    Args:
        context: Use case context ('model', 'config', 'data', 'cache')

    Returns:
        Suggestion string with alternatives
    """
    alternatives = {
        "model": """
For ML models, consider:
- safetensors (https://github.com/huggingface/safetensors)
  - Model-specific format without pickle
  - Fast and safe
  - pip install safetensors

- HDF5 (h5py)
  - For large numerical arrays
  - pip install h5py
""",
        "config": """
For configuration data, use:
- JSON (json module) - built-in, human-readable
- YAML (pyyaml) - more features than JSON
- TOML (tomli/tomllib) - modern config format
""",
        "data": """
For general data serialization:
- JSON (json module) - simple, standard
- MessagePack (msgpack) - binary JSON alternative
- Protocol Buffers (protobuf) - strongly typed
- Apache Arrow (pyarrow) - columnar data
""",
        "cache": """
For caching:
- JSON for simple data
- SQLite (sqlite3) - built-in database
- Redis - in-memory store
- diskcache - disk-based cache
""",
    }

    return alternatives.get(context, "Use JSON, YAML, or HDF5 instead of pickle when possible.")


# Export public API
__all__ = [
    "safe_pickle_load",
    "safe_pickle_load_bytes",
    "safe_pickle_dump",
    "trusted_pickle_dumps",
    "RestrictedUnpickler",
    "suggest_alternatives",
]
