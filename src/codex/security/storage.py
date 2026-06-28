"""
Encrypted storage utilities for secrets at rest.

This module provides secure storage mechanisms for sensitive data using
industry-standard encryption algorithms.

Supported Encryption:
- Fernet (AES-128-CBC + HMAC-SHA256) - Default, recommended
- AES-256-GCM (Advanced Encryption Standard with Galois/Counter Mode)
- ChaCha20-Poly1305 (Modern stream cipher with authentication)

Security Features:
- Key derivation from passwords using PBKDF2
- Secure file permissions (0o600) for encrypted files
- Multiple encryption algorithms for different use cases

Usage:
    from codex.security.storage import SecureStorage

    # Default: Fernet encryption
    storage = SecureStorage()
    storage.store_secret("api_key.enc", api_key)

    # AES-256-GCM encryption
    storage = SecureStorage(algorithm='aes-gcm')
    storage.store_secret("db_password.enc", password)

    # ChaCha20-Poly1305 encryption (faster on systems without AES-NI)
    storage = SecureStorage(algorithm='chacha20')
    storage.store_secret("secret.enc", data)
"""

import logging
import os
import stat
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union, cast

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    if TYPE_CHECKING:  # Stubs-only imports so type checkers know the types
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

if TYPE_CHECKING:
    _CipherType = Union[Fernet, AESGCM, ChaCha20Poly1305]


EncryptionAlgorithm = Literal["fernet", "aes-gcm", "chacha20"]


class SecureStorage:
    """
    Encrypted storage for sensitive data with multiple encryption algorithms.

    Supports:
    - Fernet: AES-128-CBC + HMAC-SHA256 (default, balanced)
    - AES-GCM: AES-256-GCM (fast with AES-NI hardware)
    - ChaCha20: ChaCha20-Poly1305 (fast without AES-NI)

    Requires the 'cryptography' package and ENCRYPTION_KEY environment variable.

    Example:
        >>> import os
        >>> from codex.security.storage import generate_key
        >>> os.environ['ENCRYPTION_KEY'] = generate_key()
        >>>
        >>> # Default Fernet encryption
        >>> storage = SecureStorage()
        >>> storage.store_secret("secret.enc", "my_api_key_12345")
        >>> storage.load_secret("secret.enc")
        'my_api_key_12345'
        >>>
        >>> # AES-256-GCM encryption
        >>> storage_gcm = SecureStorage(algorithm='aes-gcm')
        >>> storage_gcm.store_secret("secret_gcm.enc", "sensitive_data")
    """

    def __init__(self, key: Optional[str] = None, algorithm: EncryptionAlgorithm = "fernet"):
        """
        Initialize secure storage with encryption key and algorithm.

        Args:
            key: Encryption key (base64-encoded for Fernet, raw bytes for others).
                 If None, reads from ENCRYPTION_KEY environment variable.
            algorithm: Encryption algorithm to use:
                - 'fernet': Fernet (AES-128-CBC + HMAC) - recommended
                - 'aes-gcm': AES-256-GCM - fast with AES-NI
                - 'chacha20': ChaCha20-Poly1305 - fast without AES-NI

        Raises:
            ImportError: If cryptography package not installed
            ValueError: If no encryption key provided or invalid algorithm
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography package required for SecureStorage. "
                "Install with: pip install cryptography"
            )

        # Validate algorithm early before any state is set
        if algorithm not in ("fernet", "aes-gcm", "chacha20"):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. Use 'fernet', 'aes-gcm', or 'chacha20'."
            )

        if key is None:
            key = os.getenv("ENCRYPTION_KEY")

        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )

        self.algorithm = algorithm
        self.cipher: _CipherType

        if algorithm == "fernet":
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == "aes-gcm":
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == "chacha20":
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)

    def _ensure_key_bytes(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.

        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes

        Returns:
            Key bytes of required length
        """
        import binascii
        from base64 import urlsafe_b64decode

        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            logger.debug("Suppressed exception in handler", exc_info=True)
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            logger.debug("Suppressed exception in handler", exc_info=True)
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode("utf-8")  # type: ignore[assignment]

        import hashlib

        return hashlib.sha256(key).digest()[:length]  # type: ignore[arg-type]

    def encrypt(self, data: str) -> bytes:
        """
        Encrypt string data.

        Args:
            data: Plain text string to encrypt

        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode("utf-8")

        if self.algorithm == "fernet":
            return cast(Fernet, self.cipher).encrypt(data_bytes)
        if self.algorithm in ("aes-gcm", "chacha20"):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            aead_cipher = cast(AESGCM | ChaCha20Poly1305, self.cipher)
            ciphertext = aead_cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        # Should never reach here due to validation in __init__
        raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def decrypt(self, encrypted: bytes) -> str:
        """
        Decrypt encrypted bytes to string.

        Args:
            encrypted: Encrypted bytes

        Returns:
            Decrypted plain text string

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails (Fernet)
            cryptography.exceptions.InvalidTag: If authentication fails (GCM/ChaCha20)
        """
        if self.algorithm == "fernet":
            return cast(Fernet, self.cipher).decrypt(encrypted).decode("utf-8")
        if self.algorithm in ("aes-gcm", "chacha20"):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            aead_cipher = cast(AESGCM | ChaCha20Poly1305, self.cipher)
            plaintext = aead_cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        # Should never reach here due to validation in __init__
        raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def store_secret(self, filepath: str, secret: str) -> None:
        """
        Encrypt and store secret to file with secure permissions.

        Args:
            filepath: Path to encrypted file (will be created)
            secret: Secret data to encrypt and store

        Note:
            File permissions are set to 0o600 (owner read/write only)
        """
        encrypted = self.encrypt(secret)

        # Write encrypted data
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)

        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600

    def load_secret(self, filepath: str) -> str:
        """
        Load and decrypt secret from file.

        Args:
            filepath: Path to encrypted file

        Returns:
            Decrypted secret data

        Raises:
            FileNotFoundError: If file doesn't exist
            cryptography.fernet.InvalidToken: If decryption fails
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {filepath}")

        encrypted = path.read_bytes()
        return self.decrypt(encrypted)

    def secret_exists(self, filepath: str) -> bool:
        """
        Check if encrypted secret file exists.

        Args:
            filepath: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(filepath).exists()


def generate_key() -> str:
    """
    Generate a new encryption key for use with SecureStorage.

    Returns:
        Base64-encoded encryption key

    Example:
        >>> from codex.security.storage import generate_key
        >>> key = generate_key()
        >>> # Store this key securely (e.g., in environment variable)
        >>> # DO NOT commit to version control
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("cryptography package required. Install with: pip install cryptography")
    return Fernet.generate_key().decode("utf-8")


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
    """
    Derive an encryption key from a password using PBKDF2.

    Args:
        password: Password to derive key from
        salt: Optional salt (if None, generates random salt)

    Returns:
        Tuple of (base64_key, salt_bytes)

    Note:
        Store the salt securely - you'll need it to derive the same key again.

    Example:
        >>> key, salt = derive_key_from_password("my_password")
        >>> # Store salt securely
        >>> # To recreate key: key2, _ = derive_key_from_password("my_password", salt)
    """
    if not CRYPTO_AVAILABLE:
        raise ImportError("cryptography package required. Install with: pip install cryptography")

    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend(),
    )

    key = kdf.derive(password.encode("utf-8"))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode

    return urlsafe_b64encode(key).decode("utf-8"), salt


__all__ = [
    "SecureStorage",
    "derive_key_from_password",
    "generate_key",
]
