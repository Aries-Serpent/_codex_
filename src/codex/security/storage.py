"""
Encrypted storage utilities for secrets at rest.

This module provides secure storage mechanisms for sensitive data using
industry-standard encryption (Fernet symmetric encryption).

Security Features:
- AES-128 encryption in CBC mode with HMAC authentication
- Key derivation from passwords using PBKDF2
- Secure file permissions (0o600) for encrypted files

Usage:
    from codex.security.storage import SecureStorage
    
    # Initialize with environment variable key
    storage = SecureStorage()
    
    # Encrypt and store
    storage.store_secret("api_key.enc", api_key)
    
    # Load and decrypt
    api_key = storage.load_secret("api_key.enc")
"""

import os
import stat
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SecureStorage:
    """
    Encrypted storage for sensitive data using Fernet symmetric encryption.
    
    Requires the 'cryptography' package and ENCRYPTION_KEY environment variable.
    
    Example:
        >>> import os
        >>> os.environ['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        >>> storage = SecureStorage()
        >>> storage.store_secret("secret.enc", "my_api_key_12345")
        >>> storage.load_secret("secret.enc")
        'my_api_key_12345'
    """
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize secure storage with encryption key.
        
        Args:
            key: Encryption key (base64-encoded). If None, reads from
                 ENCRYPTION_KEY environment variable.
        
        Raises:
            ImportError: If cryptography package not installed
            ValueError: If no encryption key provided
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography package required for SecureStorage. "
                "Install with: pip install cryptography"
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        return self.fernet.encrypt(data.encode('utf-8'))
    
    def decrypt(self, encrypted: bytes) -> str:
        """
        Decrypt encrypted bytes to string.
        
        Args:
            encrypted: Encrypted bytes
        
        Returns:
            Decrypted plain text string
        
        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        return self.fernet.decrypt(encrypted).decode('utf-8')
    
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
        raise ImportError(
            "cryptography package required. "
            "Install with: pip install cryptography"
        )
    return Fernet.generate_key().decode('utf-8')


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
        raise ImportError(
            "cryptography package required. "
            "Install with: pip install cryptography"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP recommendation 2023
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


__all__ = [
    'SecureStorage',
    'generate_key',
    'derive_key_from_password',
]
