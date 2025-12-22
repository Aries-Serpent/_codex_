"""
Secure pickle loading utilities to prevent arbitrary code execution.

This module provides safe alternatives to pickle.load() that mitigate
CVE-2024-XXXXX and related pickle deserialization vulnerabilities.

Usage:
    from utils.safe_pickle import safe_pickle_load, safe_pickle_dump
    
    # Save securely
    safe_pickle_dump(data, 'data.pkl')
    
    # Load securely
    data = safe_pickle_load('data.pkl')
"""
import hashlib
import hmac
import io
import logging
import os
import pickle
import secrets
from pathlib import Path
from typing import Any, Optional, Set

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
        'builtins': {'int', 'float', 'str', 'list', 'dict', 'tuple', 'set', 'frozenset', 'bool', 'NoneType', 'bytes', 'bytearray'},
        'collections': {'OrderedDict', 'defaultdict', 'Counter', 'deque'},
        'collections.abc': {'Iterable', 'Iterator', 'Mapping', 'MutableMapping', 'Sequence', 'MutableSequence'},
        'numpy': {'ndarray', 'dtype', 'generic', 'number', 'int_', 'float_', 'complex_', 'bool_'},
        'numpy.core.multiarray': {'_reconstruct', 'scalar'},
        'torch': {'Tensor', 'Size', 'dtype', 'device'},
        'torch.storage': {'_TypedStorage', 'TypedStorage', '_LegacyStorage'},
        # Add project-specific safe classes here
        'codex_ml': {'ModelCheckpoint', 'TrainingState'},
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
            if name in self.SAFE_MODULES[module] or '*' in self.SAFE_MODULES.get(module, set()):
                return super().find_class(module, name)
        
        # Log and reject unsafe class
        logger.warning(f"Blocked unpickling of potentially unsafe class: {module}.{name}")
        raise pickle.UnpicklingError(
            f"Class {module}.{name} not in whitelist. "
            f"If this is a trusted class, add it to RestrictedUnpickler.SAFE_MODULES"
        )


def safe_pickle_load(
    file_path: str,
    verify_signature: bool = False,
    secret_key: Optional[bytes] = None,
    use_restricted_unpickler: bool = True,
) -> Any:
    """
    Safely load pickle file with optional signature verification.
    
    Args:
        file_path: Path to pickle file
        verify_signature: Whether to verify HMAC signature (requires signature added during save)
        secret_key: Secret key for HMAC verification (auto-generated if None)
        use_restricted_unpickler: Use RestrictedUnpickler to limit allowed classes
    
    Returns:
        Unpickled object
    
    Raises:
        ValueError: If signature verification fails or file is invalid
        pickle.UnpicklingError: If unsafe class detected with RestrictedUnpickler
        FileNotFoundError: If file doesn't exist
    
    Example:
        >>> data = safe_pickle_load('data.pkl')
        >>> # With signature verification
        >>> data = safe_pickle_load('data.pkl', verify_signature=True)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    if verify_signature:
        if secret_key is None:
            secret_key = _get_secret_key()
        
        # Verify HMAC signature (last 32 bytes)
        if len(data) < 32:
            raise ValueError("File too small to contain HMAC signature")
        
        pickled_data = data[:-32]
        signature = data[-32:]
        
        expected_sig = hmac.new(
            secret_key,
            pickled_data,
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError(
                "HMAC signature verification failed - file may be tampered. "
                "Ensure the same secret key was used for saving and loading."
            )
        
        data = pickled_data
        logger.info(f"✅ HMAC signature verified for {file_path}")
    
    # Unpickle with appropriate unpickler
    if use_restricted_unpickler:
        logger.debug(f"Loading pickle with RestrictedUnpickler: {file_path}")
        return RestrictedUnpickler(io.BytesIO(data)).load()
    else:
        logger.warning(f"Loading pickle WITHOUT restriction (potential security risk): {file_path}")
        return pickle.loads(data)  # nosec B301 - explicitly allowed by caller


def safe_pickle_dump(
    obj: Any,
    file_path: str,
    add_signature: bool = False,
    secret_key: Optional[bytes] = None,
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
    
    pickled_data = pickle.dumps(obj)
    
    if add_signature:
        if secret_key is None:
            secret_key = _get_secret_key()
        
        # Add HMAC signature
        signature = hmac.new(
            secret_key,
            pickled_data,
            hashlib.sha256
        ).digest()
        
        data = pickled_data + signature
        logger.info(f"Added HMAC signature to {file_path}")
    else:
        data = pickled_data
    
    with open(file_path, 'wb') as f:
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
    key_env = os.environ.get('PICKLE_SECRET_KEY')
    if key_env:
        return key_env.encode()
    
    # Try user-specific key file
    key_file = Path.home() / '.codex' / 'pickle.key'
    if key_file.exists():
        return key_file.read_bytes()
    
    # Generate new key
    logger.info(f"Generating new pickle secret key at {key_file}")
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
        'model': """
For ML models, consider:
- safetensors (https://github.com/huggingface/safetensors)
  - Model-specific format without pickle
  - Fast and safe
  - pip install safetensors
  
- HDF5 (h5py)
  - For large numerical arrays
  - pip install h5py
""",
        'config': """
For configuration data, use:
- JSON (json module) - built-in, human-readable
- YAML (pyyaml) - more features than JSON
- TOML (tomli/tomllib) - modern config format
""",
        'data': """
For general data serialization:
- JSON (json module) - simple, standard
- MessagePack (msgpack) - binary JSON alternative
- Protocol Buffers (protobuf) - strongly typed
- Apache Arrow (pyarrow) - columnar data
""",
        'cache': """
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
    'safe_pickle_load',
    'safe_pickle_dump',
    'RestrictedUnpickler',
    'suggest_alternatives',
]
