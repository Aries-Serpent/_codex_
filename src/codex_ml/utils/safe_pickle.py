"""Secure pickle loading utilities for the codex_ml package."""

from __future__ import annotations

import hashlib
import hmac
import io
import logging
import os
import pickle
import secrets
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RestrictedUnpickler(pickle.Unpickler):
    """Restricted unpickler that only allows whitelisted classes."""

    # This allowlist is intentionally conservative for cache/model metadata use.
    # Broader numpy object graphs should be explicitly reviewed before expansion.
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
        "numpy.core.multiarray": {"_reconstruct", "scalar"},
        "torch": {"Tensor", "Size", "dtype", "device"},
        "torch.storage": {"_TypedStorage", "TypedStorage", "_LegacyStorage"},
        "codex_ml": {"ModelCheckpoint", "TrainingState"},
    }

    def find_class(self, module: str, name: str) -> Any:
        """Only allow whitelisted classes to be unpickled."""
        if module in self.SAFE_MODULES and (
            name in self.SAFE_MODULES[module] or "*" in self.SAFE_MODULES.get(module, set())
        ):
            return super().find_class(module, name)

        logger.warning("Blocked unpickling of potentially unsafe class: %s.%s", module, name)
        raise pickle.UnpicklingError(
            f"Class {module}.{name} not in whitelist. "
            "If this is a trusted class, add it to RestrictedUnpickler.SAFE_MODULES"
        )


def safe_pickle_load(
    file_path: str,
    verify_signature: bool = False,
    secret_key: bytes | None = None,
    use_restricted_unpickler: bool = True,
) -> Any:
    """Safely load a pickle file with optional signature verification."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Pickle file not found: {path}")

    data = path.read_bytes()

    if verify_signature:
        key = secret_key or _get_secret_key()
        if len(data) < 32:
            raise ValueError("File too small to contain HMAC signature")

        pickled_data = data[:-32]
        signature = data[-32:]
        expected_sig = hmac.new(key, pickled_data, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError(
                "HMAC signature verification failed - file may be tampered. "
                "Ensure the same secret key was used for saving and loading."
            )

        data = pickled_data
        logger.info("✅ HMAC signature verified for %s", path)

    if use_restricted_unpickler:
        logger.debug("Loading pickle with RestrictedUnpickler: %s", path)
        return RestrictedUnpickler(io.BytesIO(data)).load()

    logger.warning(
        "Loading pickle WITHOUT restriction (potential security risk): %s. "
        "Use use_restricted_unpickler=True unless the file is fully trusted.",
        path,
    )
    return pickle.loads(data)  # nosec B301 - explicitly allowed by caller


def safe_pickle_dump(
    obj: Any,
    file_path: str,
    add_signature: bool = False,
    secret_key: bytes | None = None,
) -> None:
    """Safely dump an object to pickle with optional HMAC signature."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pickled_data = pickle.dumps(obj)
    if add_signature:
        key = secret_key or _get_secret_key()
        signature = hmac.new(key, pickled_data, hashlib.sha256).digest()
        data = pickled_data + signature
        logger.info("Added HMAC signature to %s", path)
    else:
        data = pickled_data

    path.write_bytes(data)
    logger.debug("Saved pickle to %s (%d bytes)", path, len(data))


def _get_secret_key() -> bytes:
    """Get secret key for HMAC operations."""
    key_env = os.environ.get("PICKLE_SECRET_KEY")
    if key_env:
        return key_env.encode()

    key_file = Path.home() / ".codex" / "pickle.key"
    if key_file.exists():
        return key_file.read_bytes()

    logger.info("Generating new pickle secret key at %s", key_file)
    new_key = secrets.token_bytes(32)
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.write_bytes(new_key)
    key_file.chmod(0o600)
    return new_key


__all__ = ["RestrictedUnpickler", "safe_pickle_dump", "safe_pickle_load"]
