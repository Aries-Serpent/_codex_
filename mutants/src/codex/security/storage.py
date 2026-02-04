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

import os
import stat
from pathlib import Path
from typing import Optional, Literal

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


EncryptionAlgorithm = Literal['fernet', 'aes-gcm', 'chacha20']
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
    
    def xǁSecureStorageǁ__init____mutmut_orig(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_1(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'XXfernetXX'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_2(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'FERNET'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_3(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography package required for SecureStorage. "
                "Install with: pip install cryptography"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_4(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                None
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_5(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "XXcryptography package required for SecureStorage. XX"
                "Install with: pip install cryptography"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_6(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "cryptography package required for securestorage. "
                "Install with: pip install cryptography"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_7(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "CRYPTOGRAPHY PACKAGE REQUIRED FOR SECURESTORAGE. "
                "Install with: pip install cryptography"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_8(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "XXInstall with: pip install cryptographyXX"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_9(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "install with: pip install cryptography"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_10(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
                "INSTALL WITH: PIP INSTALL CRYPTOGRAPHY"
            )
        
        # Validate algorithm early before any state is set
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_11(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_12(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('XXfernetXX', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_13(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('FERNET', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_14(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'XXaes-gcmXX', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_15(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'AES-GCM', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_16(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'XXchacha20XX'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_17(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'CHACHA20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_18(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                None
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_19(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is not None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_20(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = None
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_21(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv(None)
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_22(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("XXENCRYPTION_KEYXX")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_23(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("encryption_key")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_24(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_25(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                None
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_26(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "XXEncryption key required. Set ENCRYPTION_KEY environment XX"
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_27(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "encryption key required. set encryption_key environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_28(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "ENCRYPTION KEY REQUIRED. SET ENCRYPTION_KEY ENVIRONMENT "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_29(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "XXvariable or pass key parameter.XX"
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_30(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "VARIABLE OR PASS KEY PARAMETER."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_31(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = None
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_32(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm != 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_33(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'XXfernetXX':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_34(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'FERNET':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_35(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = None
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_36(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(None)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_37(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm != 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_38(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'XXaes-gcmXX':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_39(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'AES-GCM':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_40(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = None
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_41(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(None, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_42(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=None)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_43(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_44(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, )
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_45(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=33)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_46(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = None
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_47(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(None)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_48(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm != 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_49(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'XXchacha20XX':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_50(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'CHACHA20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_51(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = None
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_52(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(None, length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_53(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=None)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_54(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(length=32)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_55(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, )
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_56(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=33)
            self.cipher = ChaCha20Poly1305(key_bytes)
    
    def xǁSecureStorageǁ__init____mutmut_57(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = None
    
    def xǁSecureStorageǁ__init____mutmut_58(
        self, 
        key: Optional[str] = None,
        algorithm: EncryptionAlgorithm = 'fernet'
    ):
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
        if algorithm not in ('fernet', 'aes-gcm', 'chacha20'):
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. "
                f"Use 'fernet', 'aes-gcm', or 'chacha20'."
            )
        
        if key is None:
            key = os.getenv("ENCRYPTION_KEY")
        
        if not key:
            raise ValueError(
                "Encryption key required. Set ENCRYPTION_KEY environment "
                "variable or pass key parameter."
            )
        
        self.algorithm = algorithm
        
        if algorithm == 'fernet':
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        elif algorithm == 'aes-gcm':
            # AES-GCM requires 32-byte (256-bit) key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = AESGCM(key_bytes)
        elif algorithm == 'chacha20':
            # ChaCha20-Poly1305 requires 32-byte key
            key_bytes = self._ensure_key_bytes(key, length=32)
            self.cipher = ChaCha20Poly1305(None)
    
    xǁSecureStorageǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁ__init____mutmut_1': xǁSecureStorageǁ__init____mutmut_1, 
        'xǁSecureStorageǁ__init____mutmut_2': xǁSecureStorageǁ__init____mutmut_2, 
        'xǁSecureStorageǁ__init____mutmut_3': xǁSecureStorageǁ__init____mutmut_3, 
        'xǁSecureStorageǁ__init____mutmut_4': xǁSecureStorageǁ__init____mutmut_4, 
        'xǁSecureStorageǁ__init____mutmut_5': xǁSecureStorageǁ__init____mutmut_5, 
        'xǁSecureStorageǁ__init____mutmut_6': xǁSecureStorageǁ__init____mutmut_6, 
        'xǁSecureStorageǁ__init____mutmut_7': xǁSecureStorageǁ__init____mutmut_7, 
        'xǁSecureStorageǁ__init____mutmut_8': xǁSecureStorageǁ__init____mutmut_8, 
        'xǁSecureStorageǁ__init____mutmut_9': xǁSecureStorageǁ__init____mutmut_9, 
        'xǁSecureStorageǁ__init____mutmut_10': xǁSecureStorageǁ__init____mutmut_10, 
        'xǁSecureStorageǁ__init____mutmut_11': xǁSecureStorageǁ__init____mutmut_11, 
        'xǁSecureStorageǁ__init____mutmut_12': xǁSecureStorageǁ__init____mutmut_12, 
        'xǁSecureStorageǁ__init____mutmut_13': xǁSecureStorageǁ__init____mutmut_13, 
        'xǁSecureStorageǁ__init____mutmut_14': xǁSecureStorageǁ__init____mutmut_14, 
        'xǁSecureStorageǁ__init____mutmut_15': xǁSecureStorageǁ__init____mutmut_15, 
        'xǁSecureStorageǁ__init____mutmut_16': xǁSecureStorageǁ__init____mutmut_16, 
        'xǁSecureStorageǁ__init____mutmut_17': xǁSecureStorageǁ__init____mutmut_17, 
        'xǁSecureStorageǁ__init____mutmut_18': xǁSecureStorageǁ__init____mutmut_18, 
        'xǁSecureStorageǁ__init____mutmut_19': xǁSecureStorageǁ__init____mutmut_19, 
        'xǁSecureStorageǁ__init____mutmut_20': xǁSecureStorageǁ__init____mutmut_20, 
        'xǁSecureStorageǁ__init____mutmut_21': xǁSecureStorageǁ__init____mutmut_21, 
        'xǁSecureStorageǁ__init____mutmut_22': xǁSecureStorageǁ__init____mutmut_22, 
        'xǁSecureStorageǁ__init____mutmut_23': xǁSecureStorageǁ__init____mutmut_23, 
        'xǁSecureStorageǁ__init____mutmut_24': xǁSecureStorageǁ__init____mutmut_24, 
        'xǁSecureStorageǁ__init____mutmut_25': xǁSecureStorageǁ__init____mutmut_25, 
        'xǁSecureStorageǁ__init____mutmut_26': xǁSecureStorageǁ__init____mutmut_26, 
        'xǁSecureStorageǁ__init____mutmut_27': xǁSecureStorageǁ__init____mutmut_27, 
        'xǁSecureStorageǁ__init____mutmut_28': xǁSecureStorageǁ__init____mutmut_28, 
        'xǁSecureStorageǁ__init____mutmut_29': xǁSecureStorageǁ__init____mutmut_29, 
        'xǁSecureStorageǁ__init____mutmut_30': xǁSecureStorageǁ__init____mutmut_30, 
        'xǁSecureStorageǁ__init____mutmut_31': xǁSecureStorageǁ__init____mutmut_31, 
        'xǁSecureStorageǁ__init____mutmut_32': xǁSecureStorageǁ__init____mutmut_32, 
        'xǁSecureStorageǁ__init____mutmut_33': xǁSecureStorageǁ__init____mutmut_33, 
        'xǁSecureStorageǁ__init____mutmut_34': xǁSecureStorageǁ__init____mutmut_34, 
        'xǁSecureStorageǁ__init____mutmut_35': xǁSecureStorageǁ__init____mutmut_35, 
        'xǁSecureStorageǁ__init____mutmut_36': xǁSecureStorageǁ__init____mutmut_36, 
        'xǁSecureStorageǁ__init____mutmut_37': xǁSecureStorageǁ__init____mutmut_37, 
        'xǁSecureStorageǁ__init____mutmut_38': xǁSecureStorageǁ__init____mutmut_38, 
        'xǁSecureStorageǁ__init____mutmut_39': xǁSecureStorageǁ__init____mutmut_39, 
        'xǁSecureStorageǁ__init____mutmut_40': xǁSecureStorageǁ__init____mutmut_40, 
        'xǁSecureStorageǁ__init____mutmut_41': xǁSecureStorageǁ__init____mutmut_41, 
        'xǁSecureStorageǁ__init____mutmut_42': xǁSecureStorageǁ__init____mutmut_42, 
        'xǁSecureStorageǁ__init____mutmut_43': xǁSecureStorageǁ__init____mutmut_43, 
        'xǁSecureStorageǁ__init____mutmut_44': xǁSecureStorageǁ__init____mutmut_44, 
        'xǁSecureStorageǁ__init____mutmut_45': xǁSecureStorageǁ__init____mutmut_45, 
        'xǁSecureStorageǁ__init____mutmut_46': xǁSecureStorageǁ__init____mutmut_46, 
        'xǁSecureStorageǁ__init____mutmut_47': xǁSecureStorageǁ__init____mutmut_47, 
        'xǁSecureStorageǁ__init____mutmut_48': xǁSecureStorageǁ__init____mutmut_48, 
        'xǁSecureStorageǁ__init____mutmut_49': xǁSecureStorageǁ__init____mutmut_49, 
        'xǁSecureStorageǁ__init____mutmut_50': xǁSecureStorageǁ__init____mutmut_50, 
        'xǁSecureStorageǁ__init____mutmut_51': xǁSecureStorageǁ__init____mutmut_51, 
        'xǁSecureStorageǁ__init____mutmut_52': xǁSecureStorageǁ__init____mutmut_52, 
        'xǁSecureStorageǁ__init____mutmut_53': xǁSecureStorageǁ__init____mutmut_53, 
        'xǁSecureStorageǁ__init____mutmut_54': xǁSecureStorageǁ__init____mutmut_54, 
        'xǁSecureStorageǁ__init____mutmut_55': xǁSecureStorageǁ__init____mutmut_55, 
        'xǁSecureStorageǁ__init____mutmut_56': xǁSecureStorageǁ__init____mutmut_56, 
        'xǁSecureStorageǁ__init____mutmut_57': xǁSecureStorageǁ__init____mutmut_57, 
        'xǁSecureStorageǁ__init____mutmut_58': xǁSecureStorageǁ__init____mutmut_58
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSecureStorageǁ__init____mutmut_orig)
    xǁSecureStorageǁ__init____mutmut_orig.__name__ = 'xǁSecureStorageǁ__init__'
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_orig(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_1(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = None
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_2(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(None)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_3(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) != length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_4(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = None
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_5(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(None)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_6(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) != length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_7(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = None
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_8(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode(None)
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_9(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('XXutf-8XX')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_10(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('UTF-8')
        
        import hashlib
        return hashlib.sha256(key).digest()[:length]
    
    def xǁSecureStorageǁ_ensure_key_bytes__mutmut_11(self, key: str, length: int) -> bytes:
        """
        Convert key string to bytes of specified length.
        
        Args:
            key: Key string (base64 or hex)
            length: Required key length in bytes
        
        Returns:
            Key bytes of required length
        """
        from base64 import urlsafe_b64decode
        import binascii
        
        # Try base64 decode first
        try:
            key_bytes = urlsafe_b64decode(key)
            if len(key_bytes) == length:
                return key_bytes
        except (binascii.Error, ValueError):
            # Expected when key is not base64-encoded
            pass
        
        # Try hex decode
        try:
            key_bytes = bytes.fromhex(key)
            if len(key_bytes) == length:
                return key_bytes
        except (ValueError, AttributeError):
            # Expected when key is not hex-encoded
            pass
        
        # Hash the key to get required length
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        import hashlib
        return hashlib.sha256(None).digest()[:length]
    
    xǁSecureStorageǁ_ensure_key_bytes__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁ_ensure_key_bytes__mutmut_1': xǁSecureStorageǁ_ensure_key_bytes__mutmut_1, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_2': xǁSecureStorageǁ_ensure_key_bytes__mutmut_2, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_3': xǁSecureStorageǁ_ensure_key_bytes__mutmut_3, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_4': xǁSecureStorageǁ_ensure_key_bytes__mutmut_4, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_5': xǁSecureStorageǁ_ensure_key_bytes__mutmut_5, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_6': xǁSecureStorageǁ_ensure_key_bytes__mutmut_6, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_7': xǁSecureStorageǁ_ensure_key_bytes__mutmut_7, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_8': xǁSecureStorageǁ_ensure_key_bytes__mutmut_8, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_9': xǁSecureStorageǁ_ensure_key_bytes__mutmut_9, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_10': xǁSecureStorageǁ_ensure_key_bytes__mutmut_10, 
        'xǁSecureStorageǁ_ensure_key_bytes__mutmut_11': xǁSecureStorageǁ_ensure_key_bytes__mutmut_11
    }
    
    def _ensure_key_bytes(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁ_ensure_key_bytes__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁ_ensure_key_bytes__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _ensure_key_bytes.__signature__ = _mutmut_signature(xǁSecureStorageǁ_ensure_key_bytes__mutmut_orig)
    xǁSecureStorageǁ_ensure_key_bytes__mutmut_orig.__name__ = 'xǁSecureStorageǁ_ensure_key_bytes'
    
    def xǁSecureStorageǁencrypt__mutmut_orig(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_1(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = None
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_2(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode(None)
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_3(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('XXutf-8XX')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_4(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('UTF-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_5(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm != 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_6(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'XXfernetXX':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_7(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'FERNET':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_8(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(None)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_9(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm not in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_10(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('XXaes-gcmXX', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_11(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('AES-GCM', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_12(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'XXchacha20XX'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_13(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'CHACHA20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_14(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = None  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_15(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(None)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_16(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(13)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_17(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = None
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_18(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(None, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_19(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, None, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_20(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_21(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_22(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, )
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_23(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce - ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
    
    def xǁSecureStorageǁencrypt__mutmut_24(self, data: str) -> bytes:
        """
        Encrypt string data.
        
        Args:
            data: Plain text string to encrypt
        
        Returns:
            Encrypted bytes
        """
        data_bytes = data.encode('utf-8')
        
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data_bytes)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Generate random nonce
            nonce = os.urandom(12)  # 96-bit nonce for GCM/ChaCha20
            ciphertext = self.cipher.encrypt(nonce, data_bytes, None)
            # Prepend nonce to ciphertext
            return nonce + ciphertext
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(None)
        
    
    xǁSecureStorageǁencrypt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁencrypt__mutmut_1': xǁSecureStorageǁencrypt__mutmut_1, 
        'xǁSecureStorageǁencrypt__mutmut_2': xǁSecureStorageǁencrypt__mutmut_2, 
        'xǁSecureStorageǁencrypt__mutmut_3': xǁSecureStorageǁencrypt__mutmut_3, 
        'xǁSecureStorageǁencrypt__mutmut_4': xǁSecureStorageǁencrypt__mutmut_4, 
        'xǁSecureStorageǁencrypt__mutmut_5': xǁSecureStorageǁencrypt__mutmut_5, 
        'xǁSecureStorageǁencrypt__mutmut_6': xǁSecureStorageǁencrypt__mutmut_6, 
        'xǁSecureStorageǁencrypt__mutmut_7': xǁSecureStorageǁencrypt__mutmut_7, 
        'xǁSecureStorageǁencrypt__mutmut_8': xǁSecureStorageǁencrypt__mutmut_8, 
        'xǁSecureStorageǁencrypt__mutmut_9': xǁSecureStorageǁencrypt__mutmut_9, 
        'xǁSecureStorageǁencrypt__mutmut_10': xǁSecureStorageǁencrypt__mutmut_10, 
        'xǁSecureStorageǁencrypt__mutmut_11': xǁSecureStorageǁencrypt__mutmut_11, 
        'xǁSecureStorageǁencrypt__mutmut_12': xǁSecureStorageǁencrypt__mutmut_12, 
        'xǁSecureStorageǁencrypt__mutmut_13': xǁSecureStorageǁencrypt__mutmut_13, 
        'xǁSecureStorageǁencrypt__mutmut_14': xǁSecureStorageǁencrypt__mutmut_14, 
        'xǁSecureStorageǁencrypt__mutmut_15': xǁSecureStorageǁencrypt__mutmut_15, 
        'xǁSecureStorageǁencrypt__mutmut_16': xǁSecureStorageǁencrypt__mutmut_16, 
        'xǁSecureStorageǁencrypt__mutmut_17': xǁSecureStorageǁencrypt__mutmut_17, 
        'xǁSecureStorageǁencrypt__mutmut_18': xǁSecureStorageǁencrypt__mutmut_18, 
        'xǁSecureStorageǁencrypt__mutmut_19': xǁSecureStorageǁencrypt__mutmut_19, 
        'xǁSecureStorageǁencrypt__mutmut_20': xǁSecureStorageǁencrypt__mutmut_20, 
        'xǁSecureStorageǁencrypt__mutmut_21': xǁSecureStorageǁencrypt__mutmut_21, 
        'xǁSecureStorageǁencrypt__mutmut_22': xǁSecureStorageǁencrypt__mutmut_22, 
        'xǁSecureStorageǁencrypt__mutmut_23': xǁSecureStorageǁencrypt__mutmut_23, 
        'xǁSecureStorageǁencrypt__mutmut_24': xǁSecureStorageǁencrypt__mutmut_24
    }
    
    def encrypt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁencrypt__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁencrypt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    encrypt.__signature__ = _mutmut_signature(xǁSecureStorageǁencrypt__mutmut_orig)
    xǁSecureStorageǁencrypt__mutmut_orig.__name__ = 'xǁSecureStorageǁencrypt'
    def xǁSecureStorageǁdecrypt__mutmut_orig(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_1(self, encrypted: bytes) -> str:
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
        if self.algorithm != 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_2(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'XXfernetXX':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_3(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'FERNET':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_4(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode(None)
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_5(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(None).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_6(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('XXutf-8XX')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_7(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('UTF-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_8(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm not in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_9(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('XXaes-gcmXX', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_10(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('AES-GCM', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_11(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'XXchacha20XX'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_12(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'CHACHA20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_13(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = None
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_14(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:13]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_15(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = None
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_16(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[13:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_17(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = None
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_18(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(None, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_19(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, None, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_20(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_21(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_22(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, )
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_23(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode(None)
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_24(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('XXutf-8XX')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_25(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('UTF-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    def xǁSecureStorageǁdecrypt__mutmut_26(self, encrypted: bytes) -> str:
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
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted).decode('utf-8')
        elif self.algorithm in ('aes-gcm', 'chacha20'):
            # Extract nonce (first 12 bytes)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        else:
            # Should never reach here due to validation in __init__
            raise ValueError(None)
    
    xǁSecureStorageǁdecrypt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁdecrypt__mutmut_1': xǁSecureStorageǁdecrypt__mutmut_1, 
        'xǁSecureStorageǁdecrypt__mutmut_2': xǁSecureStorageǁdecrypt__mutmut_2, 
        'xǁSecureStorageǁdecrypt__mutmut_3': xǁSecureStorageǁdecrypt__mutmut_3, 
        'xǁSecureStorageǁdecrypt__mutmut_4': xǁSecureStorageǁdecrypt__mutmut_4, 
        'xǁSecureStorageǁdecrypt__mutmut_5': xǁSecureStorageǁdecrypt__mutmut_5, 
        'xǁSecureStorageǁdecrypt__mutmut_6': xǁSecureStorageǁdecrypt__mutmut_6, 
        'xǁSecureStorageǁdecrypt__mutmut_7': xǁSecureStorageǁdecrypt__mutmut_7, 
        'xǁSecureStorageǁdecrypt__mutmut_8': xǁSecureStorageǁdecrypt__mutmut_8, 
        'xǁSecureStorageǁdecrypt__mutmut_9': xǁSecureStorageǁdecrypt__mutmut_9, 
        'xǁSecureStorageǁdecrypt__mutmut_10': xǁSecureStorageǁdecrypt__mutmut_10, 
        'xǁSecureStorageǁdecrypt__mutmut_11': xǁSecureStorageǁdecrypt__mutmut_11, 
        'xǁSecureStorageǁdecrypt__mutmut_12': xǁSecureStorageǁdecrypt__mutmut_12, 
        'xǁSecureStorageǁdecrypt__mutmut_13': xǁSecureStorageǁdecrypt__mutmut_13, 
        'xǁSecureStorageǁdecrypt__mutmut_14': xǁSecureStorageǁdecrypt__mutmut_14, 
        'xǁSecureStorageǁdecrypt__mutmut_15': xǁSecureStorageǁdecrypt__mutmut_15, 
        'xǁSecureStorageǁdecrypt__mutmut_16': xǁSecureStorageǁdecrypt__mutmut_16, 
        'xǁSecureStorageǁdecrypt__mutmut_17': xǁSecureStorageǁdecrypt__mutmut_17, 
        'xǁSecureStorageǁdecrypt__mutmut_18': xǁSecureStorageǁdecrypt__mutmut_18, 
        'xǁSecureStorageǁdecrypt__mutmut_19': xǁSecureStorageǁdecrypt__mutmut_19, 
        'xǁSecureStorageǁdecrypt__mutmut_20': xǁSecureStorageǁdecrypt__mutmut_20, 
        'xǁSecureStorageǁdecrypt__mutmut_21': xǁSecureStorageǁdecrypt__mutmut_21, 
        'xǁSecureStorageǁdecrypt__mutmut_22': xǁSecureStorageǁdecrypt__mutmut_22, 
        'xǁSecureStorageǁdecrypt__mutmut_23': xǁSecureStorageǁdecrypt__mutmut_23, 
        'xǁSecureStorageǁdecrypt__mutmut_24': xǁSecureStorageǁdecrypt__mutmut_24, 
        'xǁSecureStorageǁdecrypt__mutmut_25': xǁSecureStorageǁdecrypt__mutmut_25, 
        'xǁSecureStorageǁdecrypt__mutmut_26': xǁSecureStorageǁdecrypt__mutmut_26
    }
    
    def decrypt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁdecrypt__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁdecrypt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    decrypt.__signature__ = _mutmut_signature(xǁSecureStorageǁdecrypt__mutmut_orig)
    xǁSecureStorageǁdecrypt__mutmut_orig.__name__ = 'xǁSecureStorageǁdecrypt'
    
    def xǁSecureStorageǁstore_secret__mutmut_orig(self, filepath: str, secret: str) -> None:
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
    
    def xǁSecureStorageǁstore_secret__mutmut_1(self, filepath: str, secret: str) -> None:
        """
        Encrypt and store secret to file with secure permissions.
        
        Args:
            filepath: Path to encrypted file (will be created)
            secret: Secret data to encrypt and store
        
        Note:
            File permissions are set to 0o600 (owner read/write only)
        """
        encrypted = None
        
        # Write encrypted data
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_2(self, filepath: str, secret: str) -> None:
        """
        Encrypt and store secret to file with secure permissions.
        
        Args:
            filepath: Path to encrypted file (will be created)
            secret: Secret data to encrypt and store
        
        Note:
            File permissions are set to 0o600 (owner read/write only)
        """
        encrypted = self.encrypt(None)
        
        # Write encrypted data
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_3(self, filepath: str, secret: str) -> None:
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
        path = None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_4(self, filepath: str, secret: str) -> None:
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
        path = Path(None)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_5(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(parents=None, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_6(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(parents=True, exist_ok=None)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_7(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_8(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(parents=True, )
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_9(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(parents=False, exist_ok=True)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_10(self, filepath: str, secret: str) -> None:
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
        path.parent.mkdir(parents=True, exist_ok=False)
        path.write_bytes(encrypted)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_11(self, filepath: str, secret: str) -> None:
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
        path.write_bytes(None)
        
        # Set secure file permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_12(self, filepath: str, secret: str) -> None:
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
        os.chmod(None, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_13(self, filepath: str, secret: str) -> None:
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
        os.chmod(filepath, None)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_14(self, filepath: str, secret: str) -> None:
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
        os.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_15(self, filepath: str, secret: str) -> None:
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
        os.chmod(filepath, )  # 0o600
    
    def xǁSecureStorageǁstore_secret__mutmut_16(self, filepath: str, secret: str) -> None:
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
        os.chmod(filepath, stat.S_IRUSR & stat.S_IWUSR)  # 0o600
    
    xǁSecureStorageǁstore_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁstore_secret__mutmut_1': xǁSecureStorageǁstore_secret__mutmut_1, 
        'xǁSecureStorageǁstore_secret__mutmut_2': xǁSecureStorageǁstore_secret__mutmut_2, 
        'xǁSecureStorageǁstore_secret__mutmut_3': xǁSecureStorageǁstore_secret__mutmut_3, 
        'xǁSecureStorageǁstore_secret__mutmut_4': xǁSecureStorageǁstore_secret__mutmut_4, 
        'xǁSecureStorageǁstore_secret__mutmut_5': xǁSecureStorageǁstore_secret__mutmut_5, 
        'xǁSecureStorageǁstore_secret__mutmut_6': xǁSecureStorageǁstore_secret__mutmut_6, 
        'xǁSecureStorageǁstore_secret__mutmut_7': xǁSecureStorageǁstore_secret__mutmut_7, 
        'xǁSecureStorageǁstore_secret__mutmut_8': xǁSecureStorageǁstore_secret__mutmut_8, 
        'xǁSecureStorageǁstore_secret__mutmut_9': xǁSecureStorageǁstore_secret__mutmut_9, 
        'xǁSecureStorageǁstore_secret__mutmut_10': xǁSecureStorageǁstore_secret__mutmut_10, 
        'xǁSecureStorageǁstore_secret__mutmut_11': xǁSecureStorageǁstore_secret__mutmut_11, 
        'xǁSecureStorageǁstore_secret__mutmut_12': xǁSecureStorageǁstore_secret__mutmut_12, 
        'xǁSecureStorageǁstore_secret__mutmut_13': xǁSecureStorageǁstore_secret__mutmut_13, 
        'xǁSecureStorageǁstore_secret__mutmut_14': xǁSecureStorageǁstore_secret__mutmut_14, 
        'xǁSecureStorageǁstore_secret__mutmut_15': xǁSecureStorageǁstore_secret__mutmut_15, 
        'xǁSecureStorageǁstore_secret__mutmut_16': xǁSecureStorageǁstore_secret__mutmut_16
    }
    
    def store_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁstore_secret__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁstore_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store_secret.__signature__ = _mutmut_signature(xǁSecureStorageǁstore_secret__mutmut_orig)
    xǁSecureStorageǁstore_secret__mutmut_orig.__name__ = 'xǁSecureStorageǁstore_secret'
    
    def xǁSecureStorageǁload_secret__mutmut_orig(self, filepath: str) -> str:
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
    
    def xǁSecureStorageǁload_secret__mutmut_1(self, filepath: str) -> str:
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
        path = None
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {filepath}")
        
        encrypted = path.read_bytes()
        return self.decrypt(encrypted)
    
    def xǁSecureStorageǁload_secret__mutmut_2(self, filepath: str) -> str:
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
        path = Path(None)
        if not path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {filepath}")
        
        encrypted = path.read_bytes()
        return self.decrypt(encrypted)
    
    def xǁSecureStorageǁload_secret__mutmut_3(self, filepath: str) -> str:
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
        if path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {filepath}")
        
        encrypted = path.read_bytes()
        return self.decrypt(encrypted)
    
    def xǁSecureStorageǁload_secret__mutmut_4(self, filepath: str) -> str:
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
            raise FileNotFoundError(None)
        
        encrypted = path.read_bytes()
        return self.decrypt(encrypted)
    
    def xǁSecureStorageǁload_secret__mutmut_5(self, filepath: str) -> str:
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
        
        encrypted = None
        return self.decrypt(encrypted)
    
    def xǁSecureStorageǁload_secret__mutmut_6(self, filepath: str) -> str:
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
        return self.decrypt(None)
    
    xǁSecureStorageǁload_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁload_secret__mutmut_1': xǁSecureStorageǁload_secret__mutmut_1, 
        'xǁSecureStorageǁload_secret__mutmut_2': xǁSecureStorageǁload_secret__mutmut_2, 
        'xǁSecureStorageǁload_secret__mutmut_3': xǁSecureStorageǁload_secret__mutmut_3, 
        'xǁSecureStorageǁload_secret__mutmut_4': xǁSecureStorageǁload_secret__mutmut_4, 
        'xǁSecureStorageǁload_secret__mutmut_5': xǁSecureStorageǁload_secret__mutmut_5, 
        'xǁSecureStorageǁload_secret__mutmut_6': xǁSecureStorageǁload_secret__mutmut_6
    }
    
    def load_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁload_secret__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁload_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load_secret.__signature__ = _mutmut_signature(xǁSecureStorageǁload_secret__mutmut_orig)
    xǁSecureStorageǁload_secret__mutmut_orig.__name__ = 'xǁSecureStorageǁload_secret'
    
    def xǁSecureStorageǁsecret_exists__mutmut_orig(self, filepath: str) -> bool:
        """
        Check if encrypted secret file exists.
        
        Args:
            filepath: Path to check
        
        Returns:
            True if file exists, False otherwise
        """
        return Path(filepath).exists()
    
    def xǁSecureStorageǁsecret_exists__mutmut_1(self, filepath: str) -> bool:
        """
        Check if encrypted secret file exists.
        
        Args:
            filepath: Path to check
        
        Returns:
            True if file exists, False otherwise
        """
        return Path(None).exists()
    
    xǁSecureStorageǁsecret_exists__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSecureStorageǁsecret_exists__mutmut_1': xǁSecureStorageǁsecret_exists__mutmut_1
    }
    
    def secret_exists(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSecureStorageǁsecret_exists__mutmut_orig"), object.__getattribute__(self, "xǁSecureStorageǁsecret_exists__mutmut_mutants"), args, kwargs, self)
        return result 
    
    secret_exists.__signature__ = _mutmut_signature(xǁSecureStorageǁsecret_exists__mutmut_orig)
    xǁSecureStorageǁsecret_exists__mutmut_orig.__name__ = 'xǁSecureStorageǁsecret_exists'


def x_generate_key__mutmut_orig() -> str:
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


def x_generate_key__mutmut_1() -> str:
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
    if CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package required. "
            "Install with: pip install cryptography"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_2() -> str:
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
            None
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_3() -> str:
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
            "XXcryptography package required. XX"
            "Install with: pip install cryptography"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_4() -> str:
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
            "CRYPTOGRAPHY PACKAGE REQUIRED. "
            "Install with: pip install cryptography"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_5() -> str:
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
            "XXInstall with: pip install cryptographyXX"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_6() -> str:
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
            "install with: pip install cryptography"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_7() -> str:
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
            "INSTALL WITH: PIP INSTALL CRYPTOGRAPHY"
        )
    return Fernet.generate_key().decode('utf-8')


def x_generate_key__mutmut_8() -> str:
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
    return Fernet.generate_key().decode(None)


def x_generate_key__mutmut_9() -> str:
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
    return Fernet.generate_key().decode('XXutf-8XX')


def x_generate_key__mutmut_10() -> str:
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
    return Fernet.generate_key().decode('UTF-8')

x_generate_key__mutmut_mutants : ClassVar[MutantDict] = {
'x_generate_key__mutmut_1': x_generate_key__mutmut_1, 
    'x_generate_key__mutmut_2': x_generate_key__mutmut_2, 
    'x_generate_key__mutmut_3': x_generate_key__mutmut_3, 
    'x_generate_key__mutmut_4': x_generate_key__mutmut_4, 
    'x_generate_key__mutmut_5': x_generate_key__mutmut_5, 
    'x_generate_key__mutmut_6': x_generate_key__mutmut_6, 
    'x_generate_key__mutmut_7': x_generate_key__mutmut_7, 
    'x_generate_key__mutmut_8': x_generate_key__mutmut_8, 
    'x_generate_key__mutmut_9': x_generate_key__mutmut_9, 
    'x_generate_key__mutmut_10': x_generate_key__mutmut_10
}

def generate_key(*args, **kwargs):
    result = _mutmut_trampoline(x_generate_key__mutmut_orig, x_generate_key__mutmut_mutants, args, kwargs)
    return result 

generate_key.__signature__ = _mutmut_signature(x_generate_key__mutmut_orig)
x_generate_key__mutmut_orig.__name__ = 'x_generate_key'


def x_derive_key_from_password__mutmut_orig(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_1(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    if CRYPTO_AVAILABLE:
        raise ImportError(
            "cryptography package required. "
            "Install with: pip install cryptography"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_2(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            None
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_3(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            "XXcryptography package required. XX"
            "Install with: pip install cryptography"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_4(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            "CRYPTOGRAPHY PACKAGE REQUIRED. "
            "Install with: pip install cryptography"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_5(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            "XXInstall with: pip install cryptographyXX"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_6(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            "install with: pip install cryptography"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_7(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
            "INSTALL WITH: PIP INSTALL CRYPTOGRAPHY"
        )
    
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_8(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    if salt is not None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_9(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
        salt = None
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_10(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
        salt = os.urandom(None)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_11(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
        salt = os.urandom(17)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_12(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = None
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_13(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=None,
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_14(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=None,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_15(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_16(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=None,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_17(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=None
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_18(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_19(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_20(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_21(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_22(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_23(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=33,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_24(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600001,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_25(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = None
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_26(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(None)
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_27(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode(None))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_28(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('XXutf-8XX'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_29(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('UTF-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_30(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode(None), salt


def x_derive_key_from_password__mutmut_31(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(None).decode('utf-8'), salt


def x_derive_key_from_password__mutmut_32(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('XXutf-8XX'), salt


def x_derive_key_from_password__mutmut_33(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
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
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP recommendation 2023 (updated from 480,000)
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    # Fernet expects base64-encoded 32-byte key
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(key).decode('UTF-8'), salt

x_derive_key_from_password__mutmut_mutants : ClassVar[MutantDict] = {
'x_derive_key_from_password__mutmut_1': x_derive_key_from_password__mutmut_1, 
    'x_derive_key_from_password__mutmut_2': x_derive_key_from_password__mutmut_2, 
    'x_derive_key_from_password__mutmut_3': x_derive_key_from_password__mutmut_3, 
    'x_derive_key_from_password__mutmut_4': x_derive_key_from_password__mutmut_4, 
    'x_derive_key_from_password__mutmut_5': x_derive_key_from_password__mutmut_5, 
    'x_derive_key_from_password__mutmut_6': x_derive_key_from_password__mutmut_6, 
    'x_derive_key_from_password__mutmut_7': x_derive_key_from_password__mutmut_7, 
    'x_derive_key_from_password__mutmut_8': x_derive_key_from_password__mutmut_8, 
    'x_derive_key_from_password__mutmut_9': x_derive_key_from_password__mutmut_9, 
    'x_derive_key_from_password__mutmut_10': x_derive_key_from_password__mutmut_10, 
    'x_derive_key_from_password__mutmut_11': x_derive_key_from_password__mutmut_11, 
    'x_derive_key_from_password__mutmut_12': x_derive_key_from_password__mutmut_12, 
    'x_derive_key_from_password__mutmut_13': x_derive_key_from_password__mutmut_13, 
    'x_derive_key_from_password__mutmut_14': x_derive_key_from_password__mutmut_14, 
    'x_derive_key_from_password__mutmut_15': x_derive_key_from_password__mutmut_15, 
    'x_derive_key_from_password__mutmut_16': x_derive_key_from_password__mutmut_16, 
    'x_derive_key_from_password__mutmut_17': x_derive_key_from_password__mutmut_17, 
    'x_derive_key_from_password__mutmut_18': x_derive_key_from_password__mutmut_18, 
    'x_derive_key_from_password__mutmut_19': x_derive_key_from_password__mutmut_19, 
    'x_derive_key_from_password__mutmut_20': x_derive_key_from_password__mutmut_20, 
    'x_derive_key_from_password__mutmut_21': x_derive_key_from_password__mutmut_21, 
    'x_derive_key_from_password__mutmut_22': x_derive_key_from_password__mutmut_22, 
    'x_derive_key_from_password__mutmut_23': x_derive_key_from_password__mutmut_23, 
    'x_derive_key_from_password__mutmut_24': x_derive_key_from_password__mutmut_24, 
    'x_derive_key_from_password__mutmut_25': x_derive_key_from_password__mutmut_25, 
    'x_derive_key_from_password__mutmut_26': x_derive_key_from_password__mutmut_26, 
    'x_derive_key_from_password__mutmut_27': x_derive_key_from_password__mutmut_27, 
    'x_derive_key_from_password__mutmut_28': x_derive_key_from_password__mutmut_28, 
    'x_derive_key_from_password__mutmut_29': x_derive_key_from_password__mutmut_29, 
    'x_derive_key_from_password__mutmut_30': x_derive_key_from_password__mutmut_30, 
    'x_derive_key_from_password__mutmut_31': x_derive_key_from_password__mutmut_31, 
    'x_derive_key_from_password__mutmut_32': x_derive_key_from_password__mutmut_32, 
    'x_derive_key_from_password__mutmut_33': x_derive_key_from_password__mutmut_33
}

def derive_key_from_password(*args, **kwargs):
    result = _mutmut_trampoline(x_derive_key_from_password__mutmut_orig, x_derive_key_from_password__mutmut_mutants, args, kwargs)
    return result 

derive_key_from_password.__signature__ = _mutmut_signature(x_derive_key_from_password__mutmut_orig)
x_derive_key_from_password__mutmut_orig.__name__ = 'x_derive_key_from_password'


__all__ = [
    'SecureStorage',
    'generate_key',
    'derive_key_from_password',
]
