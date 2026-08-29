"""Secure pickle loading utilities for the codex_ml package.

SECURITY MODEL:
---------------
This module provides safe alternatives to direct pickle usage for ML checkpoint scenarios.

Trust Boundaries:
1. RestrictedUnpickler: Enforces class allowlist to prevent arbitrary code execution
2. HMAC signatures: Verifies checkpoint integrity before deserialization
3. Explicit trust flags: use_restricted_unpickler must be consciously disabled

Usage Guidelines:
- ALWAYS use RestrictedUnpickler for untrusted sources (default behavior)
- ONLY set use_restricted_unpickler=False for checkpoints YOU created locally
- ALWAYS verify HMAC signatures for checkpoints from external sources
- PREFER torch.save(weights_only=True) or safetensors for new code

Example - Safe Loading:
    >>> from codex_ml.utils.safe_pickle import safe_pickle_load
    >>> # Load with class restrictions (safe)
    >>> data = safe_pickle_load("checkpoint.pkl", use_restricted_unpickler=True)
    >>>
    >>> # Load with signature verification (safest)
    >>> data = safe_pickle_load("signed.pkl", verify_signature=True, use_restricted_unpickler=True)

Example - Trusted Source (use with caution):
    >>> # Only if you KNOW the checkpoint was created by your code
    >>> data = safe_pickle_load("my_local_checkpoint.pkl", use_restricted_unpickler=False)
    >>> # Warning will be logged automatically

Migration Path:
- For new ML models: Use safetensors (pip install safetensors)
- For PyTorch models: Use torch.save/torch.load with weights_only=True
- For legacy compatibility: Use this module with RestrictedUnpickler
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import io
import logging
import os
import pickle  # nosec B403 — centralized safe wrapper around trusted pickle operations
import secrets
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

ENCRYPTED_PICKLE_HEADER = b"SPK2"

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
        "numpy._core.multiarray": {"_reconstruct", "scalar"},
        "torch": {"Tensor", "Size", "dtype", "device"},
        # Private `torch.storage` helpers remain necessary to reconstruct trusted
        # tensor cache payloads; `_TypedStorage` is still emitted by tensor
        # pickles on supported torch versions.
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
    """Safely load a pickle file with optional signature verification.

    SECURITY CONTRACT:
    ------------------
    This function provides defense-in-depth against pickle deserialization attacks:

    1. RestrictedUnpickler (default): Only allows whitelisted classes
       - Prevents arbitrary code execution via __reduce__
       - See SAFE_MODULES constant for allowed classes

    2. HMAC verification (optional): Ensures file integrity
       - Prevents tampering with checkpoint files
       - Use for checkpoints from external/untrusted sources

    3. Explicit trust override: use_restricted_unpickler=False
       - ONLY use for files YOU created locally
       - Logs warning when disabled
       - Caller accepts full responsibility for file trust

    Trust Boundaries:
    - verify_signature=True: Untrusted filesystem → Verified trusted source
    - use_restricted_unpickler=True: Unknown classes → Known safe classes
    - use_restricted_unpickler=False: TRUSTED source → Raw deserialization (RISKY)

    Args:
        file_path: Path to pickle file to load
        verify_signature: Enable HMAC signature verification (recommended for external sources)
        secret_key: HMAC key (auto-generated if None, shared across saves/loads)
        use_restricted_unpickler: Enable class allowlist (STRONGLY recommended)

    Returns:
        Deserialized Python object

    Raises:
        FileNotFoundError: File does not exist
        ValueError: HMAC signature verification failed
        pickle.UnpicklingError: Restricted class detected (when use_restricted_unpickler=True)

    Examples:
        >>> # Safest: Load with restrictions and verification
        >>> data = safe_pickle_load("external.pkl", verify_signature=True, use_restricted_unpickler=True)

        >>> # Safe: Load with restrictions only
        >>> data = safe_pickle_load("checkpoint.pkl", use_restricted_unpickler=True)

        >>> # Risky: Load without restrictions (local trusted files only)
        >>> data = safe_pickle_load("my_checkpoint.pkl", use_restricted_unpickler=False)
        ⚠️  Loading pickle WITHOUT restriction (potential security risk): ...
    """  # noqa: E501
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Pickle file not found: {path}")

    return safe_pickle_load_bytes(
        path.read_bytes(),
        verify_signature=verify_signature,
        secret_key=secret_key,
        use_restricted_unpickler=use_restricted_unpickler,
        source=str(path),
    )


def safe_pickle_load_bytes(
    data: bytes,
    *,
    verify_signature: bool = False,
    secret_key: bytes | None = None,
    use_restricted_unpickler: bool = True,
    source: str = "<memory>",
) -> Any:
    key = secret_key or _get_secret_key()
    if data.startswith(ENCRYPTED_PICKLE_HEADER):
        data = _decrypt_pickle_payload(data, key)
    """Safely load pickle bytes with the same controls as :func:`safe_pickle_load`."""
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
        logger.debug("Verified HMAC signature for %s", source)

    if use_restricted_unpickler:
        logger.debug("Loading pickle with RestrictedUnpickler: %s", source)
        return RestrictedUnpickler(io.BytesIO(data)).load()

    logger.warning(
        "Loading pickle WITHOUT restriction (potential security risk): %s. "
        "Use use_restricted_unpickler=True unless the file is fully trusted.",
        source,
    )
    # SECURITY JUSTIFICATION:
    # Caller explicitly set use_restricted_unpickler=False, accepting full responsibility
    # for the trust boundary. This is ONLY safe if:
    # 1. The bytes were created by the current process or trusted local code
    # 2. The bytes came from a secure location with proper access controls
    # 3. The caller validated the source and integrity before calling this helper
    return pickle.loads(data)  # nosec B301 # nosemgrep: semgrep.unsafe-pickle-loads


def trusted_pickle_dumps(obj: Any, *, protocol: int | None = None) -> bytes:
    """Serialize trusted in-memory objects behind one audited pickle boundary.

    SECURITY NOTE:
        Callers are responsible for ensuring *obj* was created by trusted local
        code and is not derived from attacker-controlled state. This helper is
        only safe for reviewed compatibility boundaries where pickle output must
        remain interoperable with existing checkpoint consumers.
    """
    resolved_protocol = pickle.HIGHEST_PROTOCOL if protocol is None else protocol
    return pickle.dumps(
        obj, protocol=resolved_protocol
    )  # nosec B301 # nosemgrep: semgrep_rules.py-pickle-dump


def safe_pickle_dump(
    obj: Any,
    file_path: str,
    add_signature: bool = False,
    secret_key: bytes | None = None,
    *,
    protocol: int | None = None,
) -> None:
    """Safely dump an object to pickle with optional HMAC signature."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # SECURITY: serialization only; callers pass trusted objects created by the
    # current process. Centralizing the pickle boundary here keeps surrounding
    # checkpoint code on safer abstractions.
    pickled_data = trusted_pickle_dumps(obj, protocol=protocol)
    key = secret_key or _get_secret_key()
    if add_signature:
        data = _build_signed_pickle(pickled_data, key)
        logger.info("Added HMAC signature to %s", path)
    else:
        data = pickled_data

    encrypted_data = _encrypt_pickle_payload(data, key)

    # Security: payload is encrypted (and optionally signed) pickle bytes; path is trusted from caller  # noqa: E501
    path.write_bytes(encrypted_data)
    logger.debug("Saved pickle to %s (%d bytes)", path, len(encrypted_data))


def _get_secret_key() -> bytes:
    """Get secret key for HMAC operations."""
    key_env = os.environ.get("PICKLE_SECRET_KEY")
    if key_env:
        return key_env.encode()

    key_file = Path.home() / ".codex" / "pickle.key"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    new_key = secrets.token_bytes(32)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(str(key_file), flags, 0o600)
    except FileExistsError:
        logger.debug("Using existing pickle signing key file at %s", key_file)
        return key_file.read_bytes()
    except OSError as exc:
        raise OSError(f"Unable to create pickle signing key file at {key_file}: {exc}") from exc
    logger.info("Generating new pickle signing key file at %s", key_file)
    with os.fdopen(fd, "wb") as handle:
        handle.write(new_key)
    return new_key


def _coerce_fernet_key(secret_key: bytes) -> bytes:
    """Convert raw secret bytes into a valid Fernet key."""
    try:
        decoded = base64.urlsafe_b64decode(secret_key)
        if len(decoded) == 32:
            return secret_key
    except (binascii.Error, ValueError, TypeError):
        # Input is not a valid urlsafe-base64 Fernet key; derive a stable key below.
        pass
    return base64.urlsafe_b64encode(hashlib.sha256(secret_key).digest())


def _encrypt_pickle_payload(payload: bytes, secret_key: bytes) -> bytes:
    """Encrypt payload before storing it at rest."""
    fernet = Fernet(_coerce_fernet_key(secret_key))
    return ENCRYPTED_PICKLE_HEADER + fernet.encrypt(payload)


def _decrypt_pickle_payload(data: bytes, secret_key: bytes) -> bytes:
    """Decrypt an encrypted payload produced by _encrypt_pickle_payload."""
    token = data[len(ENCRYPTED_PICKLE_HEADER) :]
    fernet = Fernet(_coerce_fernet_key(secret_key))
    try:
        return fernet.decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Encrypted pickle payload could not be decrypted") from exc


def _build_signed_pickle(pickled_data: bytes, secret_key: bytes) -> bytes:
    """Build a versioned signed pickle payload."""
    signature = hmac.new(secret_key, pickled_data, hashlib.sha256).digest()
    return SIGNED_PICKLE_HEADER + signature + pickled_data


def _split_signed_pickle(data: bytes) -> tuple[bytes, bytes]:
    """Return ``(pickled_data, signature)`` from versioned or legacy signed bytes.

    Files without the ``SPKL`` header are treated as legacy payloads that append
    the HMAC digest to the end of the pickled byte stream.
    """
    if data.startswith(SIGNED_PICKLE_MAGIC):
        if len(data) < SIGNED_PICKLE_HEADER_LEN + SIGNED_PICKLE_SIGNATURE_LEN:
            raise ValueError("Signed pickle too small to contain header and HMAC signature")

        version = data[len(SIGNED_PICKLE_MAGIC)]
        algo = data[len(SIGNED_PICKLE_MAGIC) + 1]
        if version != SIGNED_PICKLE_VERSION:
            raise ValueError(
                f"Unsupported signed pickle version: {version} (expected {SIGNED_PICKLE_VERSION})"
            )
        if algo != SIGNED_PICKLE_ALGO_SHA256:
            raise ValueError(f"Unsupported signed pickle algorithm id: {algo}")

        signature_start = SIGNED_PICKLE_HEADER_LEN
        signature_end = signature_start + SIGNED_PICKLE_SIGNATURE_LEN
        return data[signature_end:], data[signature_start:signature_end]

    if len(data) < SIGNED_PICKLE_SIGNATURE_LEN:
        raise ValueError("File too small to contain a signed pickle payload")

    return data[:-SIGNED_PICKLE_SIGNATURE_LEN], data[-SIGNED_PICKLE_SIGNATURE_LEN:]


__all__ = [
    "RestrictedUnpickler",
    "safe_pickle_dump",
    "safe_pickle_load",
    "safe_pickle_load_bytes",
    "trusted_pickle_dumps",
]
