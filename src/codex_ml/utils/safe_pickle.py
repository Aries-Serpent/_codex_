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

SIGNED_PICKLE_MAGIC = b"SPKL"
SIGNED_PICKLE_VERSION = 1
SIGNED_PICKLE_ALGO_SHA256 = 1
SIGNED_PICKLE_HEADER_LEN = len(SIGNED_PICKLE_MAGIC) + 2
SIGNED_PICKLE_SIGNATURE_LEN = 32
SIGNED_PICKLE_HEADER = SIGNED_PICKLE_MAGIC + bytes(
    [SIGNED_PICKLE_VERSION, SIGNED_PICKLE_ALGO_SHA256]
)


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
        # NumPy pickles for ndarray/scalar values rely on these reconstruction helpers.
        "numpy.core.multiarray": {"_reconstruct", "scalar"},
        "torch": {"Tensor", "Size", "dtype", "device"},
        # TypedStorage is required to reconstruct trusted tensor cache payloads.
        "torch.storage": {"_TypedStorage", "TypedStorage"},
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
        pickled_data, signature = _split_signed_pickle(data)
        expected_sig = hmac.new(key, pickled_data, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError(
                "HMAC signature verification failed - file may be tampered. "
                "Ensure the same secret key was used for saving and loading."
            )

        data = pickled_data
        logger.debug("Verified HMAC signature for %s", path)

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
        data = _build_signed_pickle(pickled_data, key)
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
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(str(key_file), flags, 0o600)
    except FileExistsError:
        logger.debug("Reusing existing pickle secret key at %s", key_file)
        return key_file.read_bytes()
    with os.fdopen(fd, "wb") as handle:
        handle.write(new_key)
    return new_key


def _build_signed_pickle(pickled_data: bytes, secret_key: bytes) -> bytes:
    """Build a versioned signed pickle payload."""
    signature = hmac.new(secret_key, pickled_data, hashlib.sha256).digest()
    return SIGNED_PICKLE_HEADER + signature + pickled_data


def _split_signed_pickle(data: bytes) -> tuple[bytes, bytes]:
    """Extract payload and signature from signed pickle bytes."""
    if data.startswith(SIGNED_PICKLE_MAGIC):
        if len(data) < SIGNED_PICKLE_HEADER_LEN + SIGNED_PICKLE_SIGNATURE_LEN:
            raise ValueError("Signed pickle too small to contain header and HMAC signature")

        version = data[len(SIGNED_PICKLE_MAGIC)]
        algo = data[len(SIGNED_PICKLE_MAGIC) + 1]
        if version != SIGNED_PICKLE_VERSION:
            raise ValueError(f"Unsupported signed pickle version: {version}")
        if algo != SIGNED_PICKLE_ALGO_SHA256:
            raise ValueError(f"Unsupported signed pickle algorithm id: {algo}")

        signature_start = SIGNED_PICKLE_HEADER_LEN
        signature_end = signature_start + SIGNED_PICKLE_SIGNATURE_LEN
        return data[signature_end:], data[signature_start:signature_end]

    if len(data) < SIGNED_PICKLE_SIGNATURE_LEN:
        raise ValueError("File too small to contain a signed pickle payload")

    return data[:-SIGNED_PICKLE_SIGNATURE_LEN], data[-SIGNED_PICKLE_SIGNATURE_LEN:]


__all__ = ["RestrictedUnpickler", "safe_pickle_dump", "safe_pickle_load"]
