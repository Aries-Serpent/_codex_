"""
Multi-Factor Authentication provider for Codex platform.

Implements TOTP-based MFA compatible with authenticator apps,
backup codes, and recovery mechanisms.

Security Warning:
    This implementation uses in-memory storage for demonstration purposes.
    For production use, you MUST replace in-memory stores with:
    - Encrypted database storage for secrets and backup codes
    - Redis or similar for attempts and lockouts
    - Proper encryption at rest for all sensitive data
"""

import hashlib
import hmac
import secrets
import struct
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from base64 import b32encode
from urllib.parse import quote
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


@dataclass
class MFASecret:
    """MFA secret data structure."""
    secret: str
    user_id: str
    issuer: str = "Codex"
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    created_at: float = field(default_factory=time.time)
    
    def get_provisioning_uri(self, account_name: str) -> str:
        """
        Generate provisioning URI for QR code.
        
        Args:
            account_name: User account name/email
        
        Returns:
            otpauth:// URI for QR code generation
        """
        params = [
            f"secret={self.secret}",
            f"issuer={quote(self.issuer)}",
            f"algorithm={self.algorithm}",
            f"digits={self.digits}",
            f"period={self.period}",
        ]
        
        label = f"{quote(self.issuer)}:{quote(account_name)}"
        uri = f"otpauth://totp/{label}?{'&'.join(params)}"
        return uri


@dataclass
class BackupCode:
    """Backup code data structure."""
    code: str
    code_hash: str
    used: bool = False
    used_at: Optional[float] = None


@dataclass
class MFAAttempt:
    """MFA verification attempt tracking."""
    user_id: str
    timestamp: float
    success: bool


class MFAProvider:
    """
    Multi-Factor Authentication provider.
    
    Implements TOTP (Time-based One-Time Password) authentication
    compatible with Google Authenticator, Authy, and similar apps.
    Includes backup codes and rate limiting for security.
    """
    
    # Rate limiting configuration
    MAX_ATTEMPTS = 3
    LOCKOUT_DURATION = 900  # 15 minutes in seconds
    
    def xǁMFAProviderǁ__init____mutmut_orig(self):
        """
        Initialize MFA provider.
        
        Warning:
            Uses in-memory storage for development/testing only.
            Production deployments MUST use:
            - Encrypted database for secrets and backup codes
            - Redis/Memcached for attempts and lockouts
            - Proper encryption at rest for all sensitive data
        """
        # DEVELOPMENT ONLY - Replace with encrypted database in production
        self._secret_store: Dict[str, MFASecret] = {}
        self._backup_codes: Dict[str, List[BackupCode]] = {}
        self._attempts: Dict[str, List[MFAAttempt]] = {}
        self._locked_users: Dict[str, float] = {}
    
    def xǁMFAProviderǁ__init____mutmut_1(self):
        """
        Initialize MFA provider.
        
        Warning:
            Uses in-memory storage for development/testing only.
            Production deployments MUST use:
            - Encrypted database for secrets and backup codes
            - Redis/Memcached for attempts and lockouts
            - Proper encryption at rest for all sensitive data
        """
        # DEVELOPMENT ONLY - Replace with encrypted database in production
        self._secret_store: Dict[str, MFASecret] = None
        self._backup_codes: Dict[str, List[BackupCode]] = {}
        self._attempts: Dict[str, List[MFAAttempt]] = {}
        self._locked_users: Dict[str, float] = {}
    
    def xǁMFAProviderǁ__init____mutmut_2(self):
        """
        Initialize MFA provider.
        
        Warning:
            Uses in-memory storage for development/testing only.
            Production deployments MUST use:
            - Encrypted database for secrets and backup codes
            - Redis/Memcached for attempts and lockouts
            - Proper encryption at rest for all sensitive data
        """
        # DEVELOPMENT ONLY - Replace with encrypted database in production
        self._secret_store: Dict[str, MFASecret] = {}
        self._backup_codes: Dict[str, List[BackupCode]] = None
        self._attempts: Dict[str, List[MFAAttempt]] = {}
        self._locked_users: Dict[str, float] = {}
    
    def xǁMFAProviderǁ__init____mutmut_3(self):
        """
        Initialize MFA provider.
        
        Warning:
            Uses in-memory storage for development/testing only.
            Production deployments MUST use:
            - Encrypted database for secrets and backup codes
            - Redis/Memcached for attempts and lockouts
            - Proper encryption at rest for all sensitive data
        """
        # DEVELOPMENT ONLY - Replace with encrypted database in production
        self._secret_store: Dict[str, MFASecret] = {}
        self._backup_codes: Dict[str, List[BackupCode]] = {}
        self._attempts: Dict[str, List[MFAAttempt]] = None
        self._locked_users: Dict[str, float] = {}
    
    def xǁMFAProviderǁ__init____mutmut_4(self):
        """
        Initialize MFA provider.
        
        Warning:
            Uses in-memory storage for development/testing only.
            Production deployments MUST use:
            - Encrypted database for secrets and backup codes
            - Redis/Memcached for attempts and lockouts
            - Proper encryption at rest for all sensitive data
        """
        # DEVELOPMENT ONLY - Replace with encrypted database in production
        self._secret_store: Dict[str, MFASecret] = {}
        self._backup_codes: Dict[str, List[BackupCode]] = {}
        self._attempts: Dict[str, List[MFAAttempt]] = {}
        self._locked_users: Dict[str, float] = None
    
    xǁMFAProviderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁ__init____mutmut_1': xǁMFAProviderǁ__init____mutmut_1, 
        'xǁMFAProviderǁ__init____mutmut_2': xǁMFAProviderǁ__init____mutmut_2, 
        'xǁMFAProviderǁ__init____mutmut_3': xǁMFAProviderǁ__init____mutmut_3, 
        'xǁMFAProviderǁ__init____mutmut_4': xǁMFAProviderǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMFAProviderǁ__init____mutmut_orig)
    xǁMFAProviderǁ__init____mutmut_orig.__name__ = 'xǁMFAProviderǁ__init__'
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_orig(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_1(self, user_id: str, issuer: str = "XXCodexXX") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_2(self, user_id: str, issuer: str = "codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_3(self, user_id: str, issuer: str = "CODEX") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_4(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = None
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_5(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(None)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_6(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(21)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_7(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = None
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_8(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip(None)
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_9(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').lstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_10(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode(None).rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_11(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(None).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_12(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('XXutf-8XX').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_13(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('UTF-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_14(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('XX=XX')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_15(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = None
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_16(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=None,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_17(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=None,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_18(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=None,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_19(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_20(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_21(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret
        
        return mfa_secret
    
    def xǁMFAProviderǁgenerate_totp_secret__mutmut_22(self, user_id: str, issuer: str = "Codex") -> MFASecret:
        """
        Generate a new TOTP secret for a user.
        
        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
        
        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode('utf-8').rstrip('=')
        
        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
        )
        
        # Store secret (use database in production)
        self._secret_store[user_id] = None
        
        return mfa_secret
    
    xǁMFAProviderǁgenerate_totp_secret__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁgenerate_totp_secret__mutmut_1': xǁMFAProviderǁgenerate_totp_secret__mutmut_1, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_2': xǁMFAProviderǁgenerate_totp_secret__mutmut_2, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_3': xǁMFAProviderǁgenerate_totp_secret__mutmut_3, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_4': xǁMFAProviderǁgenerate_totp_secret__mutmut_4, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_5': xǁMFAProviderǁgenerate_totp_secret__mutmut_5, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_6': xǁMFAProviderǁgenerate_totp_secret__mutmut_6, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_7': xǁMFAProviderǁgenerate_totp_secret__mutmut_7, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_8': xǁMFAProviderǁgenerate_totp_secret__mutmut_8, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_9': xǁMFAProviderǁgenerate_totp_secret__mutmut_9, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_10': xǁMFAProviderǁgenerate_totp_secret__mutmut_10, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_11': xǁMFAProviderǁgenerate_totp_secret__mutmut_11, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_12': xǁMFAProviderǁgenerate_totp_secret__mutmut_12, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_13': xǁMFAProviderǁgenerate_totp_secret__mutmut_13, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_14': xǁMFAProviderǁgenerate_totp_secret__mutmut_14, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_15': xǁMFAProviderǁgenerate_totp_secret__mutmut_15, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_16': xǁMFAProviderǁgenerate_totp_secret__mutmut_16, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_17': xǁMFAProviderǁgenerate_totp_secret__mutmut_17, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_18': xǁMFAProviderǁgenerate_totp_secret__mutmut_18, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_19': xǁMFAProviderǁgenerate_totp_secret__mutmut_19, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_20': xǁMFAProviderǁgenerate_totp_secret__mutmut_20, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_21': xǁMFAProviderǁgenerate_totp_secret__mutmut_21, 
        'xǁMFAProviderǁgenerate_totp_secret__mutmut_22': xǁMFAProviderǁgenerate_totp_secret__mutmut_22
    }
    
    def generate_totp_secret(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁgenerate_totp_secret__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁgenerate_totp_secret__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_totp_secret.__signature__ = _mutmut_signature(xǁMFAProviderǁgenerate_totp_secret__mutmut_orig)
    xǁMFAProviderǁgenerate_totp_secret__mutmut_orig.__name__ = 'xǁMFAProviderǁgenerate_totp_secret'
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_orig(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_1(self, secret: str, counter: int, digits: int = 7) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_2(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = None
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_3(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(None)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_4(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = None
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_5(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack(None, counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_6(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', None)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_7(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack(counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_8(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', )
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_9(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('XX>QXX', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_10(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_11(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = None
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_12(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(None, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_13(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, None, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_14(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, None).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_15(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_16(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_17(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, ).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_18(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = None
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_19(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] | 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_20(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[+1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_21(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-2] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_22(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 16
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_23(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = None
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_24(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack(None, hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_25(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', None)[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_26(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack(hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_27(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', )[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_28(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('XX>IXX', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_29(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>i', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_30(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset - 4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_31(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+5])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_32(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[1]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_33(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated = 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_34(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated |= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_35(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 2147483648
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_36(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = None
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_37(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(None)
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_38(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated / (10 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_39(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 * digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_40(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (11 ** digits))
        return token.zfill(digits)
    
    def xǁMFAProviderǁ_get_hotp_token__mutmut_41(self, secret: str, counter: int, digits: int = 6) -> str:
        """
        Generate HOTP token.
        
        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
        
        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        
        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        truncated &= 0x7FFFFFFF
        
        # Generate token
        token = str(truncated % (10 ** digits))
        return token.zfill(None)
    
    xǁMFAProviderǁ_get_hotp_token__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁ_get_hotp_token__mutmut_1': xǁMFAProviderǁ_get_hotp_token__mutmut_1, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_2': xǁMFAProviderǁ_get_hotp_token__mutmut_2, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_3': xǁMFAProviderǁ_get_hotp_token__mutmut_3, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_4': xǁMFAProviderǁ_get_hotp_token__mutmut_4, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_5': xǁMFAProviderǁ_get_hotp_token__mutmut_5, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_6': xǁMFAProviderǁ_get_hotp_token__mutmut_6, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_7': xǁMFAProviderǁ_get_hotp_token__mutmut_7, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_8': xǁMFAProviderǁ_get_hotp_token__mutmut_8, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_9': xǁMFAProviderǁ_get_hotp_token__mutmut_9, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_10': xǁMFAProviderǁ_get_hotp_token__mutmut_10, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_11': xǁMFAProviderǁ_get_hotp_token__mutmut_11, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_12': xǁMFAProviderǁ_get_hotp_token__mutmut_12, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_13': xǁMFAProviderǁ_get_hotp_token__mutmut_13, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_14': xǁMFAProviderǁ_get_hotp_token__mutmut_14, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_15': xǁMFAProviderǁ_get_hotp_token__mutmut_15, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_16': xǁMFAProviderǁ_get_hotp_token__mutmut_16, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_17': xǁMFAProviderǁ_get_hotp_token__mutmut_17, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_18': xǁMFAProviderǁ_get_hotp_token__mutmut_18, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_19': xǁMFAProviderǁ_get_hotp_token__mutmut_19, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_20': xǁMFAProviderǁ_get_hotp_token__mutmut_20, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_21': xǁMFAProviderǁ_get_hotp_token__mutmut_21, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_22': xǁMFAProviderǁ_get_hotp_token__mutmut_22, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_23': xǁMFAProviderǁ_get_hotp_token__mutmut_23, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_24': xǁMFAProviderǁ_get_hotp_token__mutmut_24, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_25': xǁMFAProviderǁ_get_hotp_token__mutmut_25, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_26': xǁMFAProviderǁ_get_hotp_token__mutmut_26, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_27': xǁMFAProviderǁ_get_hotp_token__mutmut_27, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_28': xǁMFAProviderǁ_get_hotp_token__mutmut_28, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_29': xǁMFAProviderǁ_get_hotp_token__mutmut_29, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_30': xǁMFAProviderǁ_get_hotp_token__mutmut_30, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_31': xǁMFAProviderǁ_get_hotp_token__mutmut_31, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_32': xǁMFAProviderǁ_get_hotp_token__mutmut_32, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_33': xǁMFAProviderǁ_get_hotp_token__mutmut_33, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_34': xǁMFAProviderǁ_get_hotp_token__mutmut_34, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_35': xǁMFAProviderǁ_get_hotp_token__mutmut_35, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_36': xǁMFAProviderǁ_get_hotp_token__mutmut_36, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_37': xǁMFAProviderǁ_get_hotp_token__mutmut_37, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_38': xǁMFAProviderǁ_get_hotp_token__mutmut_38, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_39': xǁMFAProviderǁ_get_hotp_token__mutmut_39, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_40': xǁMFAProviderǁ_get_hotp_token__mutmut_40, 
        'xǁMFAProviderǁ_get_hotp_token__mutmut_41': xǁMFAProviderǁ_get_hotp_token__mutmut_41
    }
    
    def _get_hotp_token(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁ_get_hotp_token__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁ_get_hotp_token__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _get_hotp_token.__signature__ = _mutmut_signature(xǁMFAProviderǁ_get_hotp_token__mutmut_orig)
    xǁMFAProviderǁ_get_hotp_token__mutmut_orig.__name__ = 'xǁMFAProviderǁ_get_hotp_token'
    
    def xǁMFAProviderǁ_base32_decode__mutmut_orig(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_1(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = None
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_2(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) / 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_3(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 9
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_4(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret = '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_5(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret -= '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_6(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' / (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_7(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += 'XX=XX' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_8(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 + missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_9(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (9 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_10(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(None, casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_11(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=None)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_12(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(casefold=True)
    
    def xǁMFAProviderǁ_base32_decode__mutmut_13(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, )
    
    def xǁMFAProviderǁ_base32_decode__mutmut_14(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += '=' * (8 - missing_padding)
        
        from base64 import b32decode
        return b32decode(secret, casefold=False)
    
    xǁMFAProviderǁ_base32_decode__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁ_base32_decode__mutmut_1': xǁMFAProviderǁ_base32_decode__mutmut_1, 
        'xǁMFAProviderǁ_base32_decode__mutmut_2': xǁMFAProviderǁ_base32_decode__mutmut_2, 
        'xǁMFAProviderǁ_base32_decode__mutmut_3': xǁMFAProviderǁ_base32_decode__mutmut_3, 
        'xǁMFAProviderǁ_base32_decode__mutmut_4': xǁMFAProviderǁ_base32_decode__mutmut_4, 
        'xǁMFAProviderǁ_base32_decode__mutmut_5': xǁMFAProviderǁ_base32_decode__mutmut_5, 
        'xǁMFAProviderǁ_base32_decode__mutmut_6': xǁMFAProviderǁ_base32_decode__mutmut_6, 
        'xǁMFAProviderǁ_base32_decode__mutmut_7': xǁMFAProviderǁ_base32_decode__mutmut_7, 
        'xǁMFAProviderǁ_base32_decode__mutmut_8': xǁMFAProviderǁ_base32_decode__mutmut_8, 
        'xǁMFAProviderǁ_base32_decode__mutmut_9': xǁMFAProviderǁ_base32_decode__mutmut_9, 
        'xǁMFAProviderǁ_base32_decode__mutmut_10': xǁMFAProviderǁ_base32_decode__mutmut_10, 
        'xǁMFAProviderǁ_base32_decode__mutmut_11': xǁMFAProviderǁ_base32_decode__mutmut_11, 
        'xǁMFAProviderǁ_base32_decode__mutmut_12': xǁMFAProviderǁ_base32_decode__mutmut_12, 
        'xǁMFAProviderǁ_base32_decode__mutmut_13': xǁMFAProviderǁ_base32_decode__mutmut_13, 
        'xǁMFAProviderǁ_base32_decode__mutmut_14': xǁMFAProviderǁ_base32_decode__mutmut_14
    }
    
    def _base32_decode(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁ_base32_decode__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁ_base32_decode__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _base32_decode.__signature__ = _mutmut_signature(xǁMFAProviderǁ_base32_decode__mutmut_orig)
    xǁMFAProviderǁ_base32_decode__mutmut_orig.__name__ = 'xǁMFAProviderǁ_base32_decode'
    
    def xǁMFAProviderǁgenerate_totp__mutmut_orig(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_1(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 31, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_2(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 7) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_3(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is not None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_4(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = None
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_5(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = None
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_6(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(None)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_7(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp / period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_8(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(None, counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_9(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, None, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_10(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, None)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_11(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(counter, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_12(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, digits)
    
    def xǁMFAProviderǁgenerate_totp__mutmut_13(self, secret: str, timestamp: Optional[float] = None, 
                     period: int = 30, digits: int = 6) -> str:
        """
        Generate TOTP token.
        
        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate counter
        counter = int(timestamp // period)
        
        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, )
    
    xǁMFAProviderǁgenerate_totp__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁgenerate_totp__mutmut_1': xǁMFAProviderǁgenerate_totp__mutmut_1, 
        'xǁMFAProviderǁgenerate_totp__mutmut_2': xǁMFAProviderǁgenerate_totp__mutmut_2, 
        'xǁMFAProviderǁgenerate_totp__mutmut_3': xǁMFAProviderǁgenerate_totp__mutmut_3, 
        'xǁMFAProviderǁgenerate_totp__mutmut_4': xǁMFAProviderǁgenerate_totp__mutmut_4, 
        'xǁMFAProviderǁgenerate_totp__mutmut_5': xǁMFAProviderǁgenerate_totp__mutmut_5, 
        'xǁMFAProviderǁgenerate_totp__mutmut_6': xǁMFAProviderǁgenerate_totp__mutmut_6, 
        'xǁMFAProviderǁgenerate_totp__mutmut_7': xǁMFAProviderǁgenerate_totp__mutmut_7, 
        'xǁMFAProviderǁgenerate_totp__mutmut_8': xǁMFAProviderǁgenerate_totp__mutmut_8, 
        'xǁMFAProviderǁgenerate_totp__mutmut_9': xǁMFAProviderǁgenerate_totp__mutmut_9, 
        'xǁMFAProviderǁgenerate_totp__mutmut_10': xǁMFAProviderǁgenerate_totp__mutmut_10, 
        'xǁMFAProviderǁgenerate_totp__mutmut_11': xǁMFAProviderǁgenerate_totp__mutmut_11, 
        'xǁMFAProviderǁgenerate_totp__mutmut_12': xǁMFAProviderǁgenerate_totp__mutmut_12, 
        'xǁMFAProviderǁgenerate_totp__mutmut_13': xǁMFAProviderǁgenerate_totp__mutmut_13
    }
    
    def generate_totp(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁgenerate_totp__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁgenerate_totp__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_totp.__signature__ = _mutmut_signature(xǁMFAProviderǁgenerate_totp__mutmut_orig)
    xǁMFAProviderǁgenerate_totp__mutmut_orig.__name__ = 'xǁMFAProviderǁgenerate_totp'
    
    def xǁMFAProviderǁverify_totp__mutmut_orig(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_1(self, secret: str, code: str, user_id: str,
                   window: int = 2, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_2(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 31, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_3(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 7) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_4(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(None):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_5(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return True
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_6(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = None
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_7(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(None, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_8(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, None):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_9(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_10(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, ):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_11(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(+window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_12(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window - 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_13(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 2):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_14(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = None
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_15(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time - (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_16(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset / period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_17(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = None
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_18(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(None, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_19(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, None, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_20(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, None, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_21(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, None)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_22(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_23(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_24(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_25(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, )
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_26(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(None, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_27(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, None):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_28(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_29(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, ):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_30(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(None, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_31(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, None)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_32(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_33(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, )
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_34(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, False)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_35(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return False
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_36(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(None, False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_37(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, None)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_38(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(False)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_39(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, )
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_40(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, True)
        return False
    
    def xǁMFAProviderǁverify_totp__mutmut_41(self, secret: str, code: str, user_id: str,
                   window: int = 1, period: int = 30, digits: int = 6) -> bool:
        """
        Verify TOTP code with time window.
        
        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
        
        Returns:
            True if code is valid, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        current_time = time.time()
        
        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits)
            
            if secrets.compare_digest(code, expected_code):
                self._record_attempt(user_id, True)
                return True
        
        # Code didn't match
        self._record_attempt(user_id, False)
        return True
    
    xǁMFAProviderǁverify_totp__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁverify_totp__mutmut_1': xǁMFAProviderǁverify_totp__mutmut_1, 
        'xǁMFAProviderǁverify_totp__mutmut_2': xǁMFAProviderǁverify_totp__mutmut_2, 
        'xǁMFAProviderǁverify_totp__mutmut_3': xǁMFAProviderǁverify_totp__mutmut_3, 
        'xǁMFAProviderǁverify_totp__mutmut_4': xǁMFAProviderǁverify_totp__mutmut_4, 
        'xǁMFAProviderǁverify_totp__mutmut_5': xǁMFAProviderǁverify_totp__mutmut_5, 
        'xǁMFAProviderǁverify_totp__mutmut_6': xǁMFAProviderǁverify_totp__mutmut_6, 
        'xǁMFAProviderǁverify_totp__mutmut_7': xǁMFAProviderǁverify_totp__mutmut_7, 
        'xǁMFAProviderǁverify_totp__mutmut_8': xǁMFAProviderǁverify_totp__mutmut_8, 
        'xǁMFAProviderǁverify_totp__mutmut_9': xǁMFAProviderǁverify_totp__mutmut_9, 
        'xǁMFAProviderǁverify_totp__mutmut_10': xǁMFAProviderǁverify_totp__mutmut_10, 
        'xǁMFAProviderǁverify_totp__mutmut_11': xǁMFAProviderǁverify_totp__mutmut_11, 
        'xǁMFAProviderǁverify_totp__mutmut_12': xǁMFAProviderǁverify_totp__mutmut_12, 
        'xǁMFAProviderǁverify_totp__mutmut_13': xǁMFAProviderǁverify_totp__mutmut_13, 
        'xǁMFAProviderǁverify_totp__mutmut_14': xǁMFAProviderǁverify_totp__mutmut_14, 
        'xǁMFAProviderǁverify_totp__mutmut_15': xǁMFAProviderǁverify_totp__mutmut_15, 
        'xǁMFAProviderǁverify_totp__mutmut_16': xǁMFAProviderǁverify_totp__mutmut_16, 
        'xǁMFAProviderǁverify_totp__mutmut_17': xǁMFAProviderǁverify_totp__mutmut_17, 
        'xǁMFAProviderǁverify_totp__mutmut_18': xǁMFAProviderǁverify_totp__mutmut_18, 
        'xǁMFAProviderǁverify_totp__mutmut_19': xǁMFAProviderǁverify_totp__mutmut_19, 
        'xǁMFAProviderǁverify_totp__mutmut_20': xǁMFAProviderǁverify_totp__mutmut_20, 
        'xǁMFAProviderǁverify_totp__mutmut_21': xǁMFAProviderǁverify_totp__mutmut_21, 
        'xǁMFAProviderǁverify_totp__mutmut_22': xǁMFAProviderǁverify_totp__mutmut_22, 
        'xǁMFAProviderǁverify_totp__mutmut_23': xǁMFAProviderǁverify_totp__mutmut_23, 
        'xǁMFAProviderǁverify_totp__mutmut_24': xǁMFAProviderǁverify_totp__mutmut_24, 
        'xǁMFAProviderǁverify_totp__mutmut_25': xǁMFAProviderǁverify_totp__mutmut_25, 
        'xǁMFAProviderǁverify_totp__mutmut_26': xǁMFAProviderǁverify_totp__mutmut_26, 
        'xǁMFAProviderǁverify_totp__mutmut_27': xǁMFAProviderǁverify_totp__mutmut_27, 
        'xǁMFAProviderǁverify_totp__mutmut_28': xǁMFAProviderǁverify_totp__mutmut_28, 
        'xǁMFAProviderǁverify_totp__mutmut_29': xǁMFAProviderǁverify_totp__mutmut_29, 
        'xǁMFAProviderǁverify_totp__mutmut_30': xǁMFAProviderǁverify_totp__mutmut_30, 
        'xǁMFAProviderǁverify_totp__mutmut_31': xǁMFAProviderǁverify_totp__mutmut_31, 
        'xǁMFAProviderǁverify_totp__mutmut_32': xǁMFAProviderǁverify_totp__mutmut_32, 
        'xǁMFAProviderǁverify_totp__mutmut_33': xǁMFAProviderǁverify_totp__mutmut_33, 
        'xǁMFAProviderǁverify_totp__mutmut_34': xǁMFAProviderǁverify_totp__mutmut_34, 
        'xǁMFAProviderǁverify_totp__mutmut_35': xǁMFAProviderǁverify_totp__mutmut_35, 
        'xǁMFAProviderǁverify_totp__mutmut_36': xǁMFAProviderǁverify_totp__mutmut_36, 
        'xǁMFAProviderǁverify_totp__mutmut_37': xǁMFAProviderǁverify_totp__mutmut_37, 
        'xǁMFAProviderǁverify_totp__mutmut_38': xǁMFAProviderǁverify_totp__mutmut_38, 
        'xǁMFAProviderǁverify_totp__mutmut_39': xǁMFAProviderǁverify_totp__mutmut_39, 
        'xǁMFAProviderǁverify_totp__mutmut_40': xǁMFAProviderǁverify_totp__mutmut_40, 
        'xǁMFAProviderǁverify_totp__mutmut_41': xǁMFAProviderǁverify_totp__mutmut_41
    }
    
    def verify_totp(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁverify_totp__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁverify_totp__mutmut_mutants"), args, kwargs, self)
        return result 
    
    verify_totp.__signature__ = _mutmut_signature(xǁMFAProviderǁverify_totp__mutmut_orig)
    xǁMFAProviderǁverify_totp__mutmut_orig.__name__ = 'xǁMFAProviderǁverify_totp'
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_orig(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False
        
        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_1(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id in self._locked_users:
            return False
        
        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_2(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return True
        
        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_3(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False
        
        lockout_until = None
        if time.time() < lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_4(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False
        
        lockout_until = self._locked_users[user_id]
        if time.time() <= lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_5(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False
        
        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return False
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False
    
    def xǁMFAProviderǁ_is_locked_out__mutmut_6(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False
        
        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return True
        
        # Lockout expired, remove it
        del self._locked_users[user_id]
        return True
    
    xǁMFAProviderǁ_is_locked_out__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁ_is_locked_out__mutmut_1': xǁMFAProviderǁ_is_locked_out__mutmut_1, 
        'xǁMFAProviderǁ_is_locked_out__mutmut_2': xǁMFAProviderǁ_is_locked_out__mutmut_2, 
        'xǁMFAProviderǁ_is_locked_out__mutmut_3': xǁMFAProviderǁ_is_locked_out__mutmut_3, 
        'xǁMFAProviderǁ_is_locked_out__mutmut_4': xǁMFAProviderǁ_is_locked_out__mutmut_4, 
        'xǁMFAProviderǁ_is_locked_out__mutmut_5': xǁMFAProviderǁ_is_locked_out__mutmut_5, 
        'xǁMFAProviderǁ_is_locked_out__mutmut_6': xǁMFAProviderǁ_is_locked_out__mutmut_6
    }
    
    def _is_locked_out(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁ_is_locked_out__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁ_is_locked_out__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _is_locked_out.__signature__ = _mutmut_signature(xǁMFAProviderǁ_is_locked_out__mutmut_orig)
    xǁMFAProviderǁ_is_locked_out__mutmut_orig.__name__ = 'xǁMFAProviderǁ_is_locked_out'
    
    def xǁMFAProviderǁ_record_attempt__mutmut_orig(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_1(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = None
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_2(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=None,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_3(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=None,
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_4(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=None,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_5(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_6(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_7(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_8(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_9(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = None
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_10(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(None)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_11(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = None
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_12(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() + 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_13(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3601
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_14(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = None
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_15(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp >= cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_16(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_17(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = None
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_18(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success or a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_19(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_20(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp >= time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_21(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() + 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_22(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 301  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_23(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) > self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION
    
    def xǁMFAProviderǁ_record_attempt__mutmut_24(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = None
    
    def xǁMFAProviderǁ_record_attempt__mutmut_25(self, user_id: str, success: bool):
        """Record MFA verification attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            timestamp=time.time(),
            success=success,
        )
        
        if user_id not in self._attempts:
            self._attempts[user_id] = []
        
        self._attempts[user_id].append(attempt)
        
        # Clean old attempts (keep last hour)
        cutoff = time.time() - 3600
        self._attempts[user_id] = [
            a for a in self._attempts[user_id] if a.timestamp > cutoff
        ]
        
        # Check for lockout
        if not success:
            recent_failures = [
                a for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]
            
            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() - self.LOCKOUT_DURATION
    
    xǁMFAProviderǁ_record_attempt__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁ_record_attempt__mutmut_1': xǁMFAProviderǁ_record_attempt__mutmut_1, 
        'xǁMFAProviderǁ_record_attempt__mutmut_2': xǁMFAProviderǁ_record_attempt__mutmut_2, 
        'xǁMFAProviderǁ_record_attempt__mutmut_3': xǁMFAProviderǁ_record_attempt__mutmut_3, 
        'xǁMFAProviderǁ_record_attempt__mutmut_4': xǁMFAProviderǁ_record_attempt__mutmut_4, 
        'xǁMFAProviderǁ_record_attempt__mutmut_5': xǁMFAProviderǁ_record_attempt__mutmut_5, 
        'xǁMFAProviderǁ_record_attempt__mutmut_6': xǁMFAProviderǁ_record_attempt__mutmut_6, 
        'xǁMFAProviderǁ_record_attempt__mutmut_7': xǁMFAProviderǁ_record_attempt__mutmut_7, 
        'xǁMFAProviderǁ_record_attempt__mutmut_8': xǁMFAProviderǁ_record_attempt__mutmut_8, 
        'xǁMFAProviderǁ_record_attempt__mutmut_9': xǁMFAProviderǁ_record_attempt__mutmut_9, 
        'xǁMFAProviderǁ_record_attempt__mutmut_10': xǁMFAProviderǁ_record_attempt__mutmut_10, 
        'xǁMFAProviderǁ_record_attempt__mutmut_11': xǁMFAProviderǁ_record_attempt__mutmut_11, 
        'xǁMFAProviderǁ_record_attempt__mutmut_12': xǁMFAProviderǁ_record_attempt__mutmut_12, 
        'xǁMFAProviderǁ_record_attempt__mutmut_13': xǁMFAProviderǁ_record_attempt__mutmut_13, 
        'xǁMFAProviderǁ_record_attempt__mutmut_14': xǁMFAProviderǁ_record_attempt__mutmut_14, 
        'xǁMFAProviderǁ_record_attempt__mutmut_15': xǁMFAProviderǁ_record_attempt__mutmut_15, 
        'xǁMFAProviderǁ_record_attempt__mutmut_16': xǁMFAProviderǁ_record_attempt__mutmut_16, 
        'xǁMFAProviderǁ_record_attempt__mutmut_17': xǁMFAProviderǁ_record_attempt__mutmut_17, 
        'xǁMFAProviderǁ_record_attempt__mutmut_18': xǁMFAProviderǁ_record_attempt__mutmut_18, 
        'xǁMFAProviderǁ_record_attempt__mutmut_19': xǁMFAProviderǁ_record_attempt__mutmut_19, 
        'xǁMFAProviderǁ_record_attempt__mutmut_20': xǁMFAProviderǁ_record_attempt__mutmut_20, 
        'xǁMFAProviderǁ_record_attempt__mutmut_21': xǁMFAProviderǁ_record_attempt__mutmut_21, 
        'xǁMFAProviderǁ_record_attempt__mutmut_22': xǁMFAProviderǁ_record_attempt__mutmut_22, 
        'xǁMFAProviderǁ_record_attempt__mutmut_23': xǁMFAProviderǁ_record_attempt__mutmut_23, 
        'xǁMFAProviderǁ_record_attempt__mutmut_24': xǁMFAProviderǁ_record_attempt__mutmut_24, 
        'xǁMFAProviderǁ_record_attempt__mutmut_25': xǁMFAProviderǁ_record_attempt__mutmut_25
    }
    
    def _record_attempt(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁ_record_attempt__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁ_record_attempt__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _record_attempt.__signature__ = _mutmut_signature(xǁMFAProviderǁ_record_attempt__mutmut_orig)
    xǁMFAProviderǁ_record_attempt__mutmut_orig.__name__ = 'xǁMFAProviderǁ_record_attempt'
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_orig(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_1(self, user_id: str, count: int = 11) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_2(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = None
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_3(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = None
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_4(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(None):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_5(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = None
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_6(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).lower()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_7(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(None).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_8(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(5).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_9(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = None
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_10(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:5]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_11(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[5:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_12(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = None
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_13(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(None).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_14(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = None
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_15(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=None,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_16(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=None,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_17(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_18(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_19(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(None)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_20(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(None)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = backup_codes
        
        return codes
    
    def xǁMFAProviderǁgenerate_backup_codes__mutmut_21(self, user_id: str, count: int = 10) -> List[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            user_id: User identifier
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes (show to user only once)
        """
        codes = []
        backup_codes = []
        
        for _ in range(count):
            # Generate 8-character code (format: XXXX-XXXX)
            code = secrets.token_hex(4).upper()
            formatted_code = f"{code[:4]}-{code[4:]}"
            
            # Hash for storage
            code_hash = hashlib.sha256(formatted_code.encode()).hexdigest()
            
            backup_code = BackupCode(
                code=formatted_code,
                code_hash=code_hash,
            )
            
            codes.append(formatted_code)
            backup_codes.append(backup_code)
        
        # Store backup codes (use database in production)
        self._backup_codes[user_id] = None
        
        return codes
    
    xǁMFAProviderǁgenerate_backup_codes__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁgenerate_backup_codes__mutmut_1': xǁMFAProviderǁgenerate_backup_codes__mutmut_1, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_2': xǁMFAProviderǁgenerate_backup_codes__mutmut_2, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_3': xǁMFAProviderǁgenerate_backup_codes__mutmut_3, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_4': xǁMFAProviderǁgenerate_backup_codes__mutmut_4, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_5': xǁMFAProviderǁgenerate_backup_codes__mutmut_5, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_6': xǁMFAProviderǁgenerate_backup_codes__mutmut_6, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_7': xǁMFAProviderǁgenerate_backup_codes__mutmut_7, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_8': xǁMFAProviderǁgenerate_backup_codes__mutmut_8, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_9': xǁMFAProviderǁgenerate_backup_codes__mutmut_9, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_10': xǁMFAProviderǁgenerate_backup_codes__mutmut_10, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_11': xǁMFAProviderǁgenerate_backup_codes__mutmut_11, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_12': xǁMFAProviderǁgenerate_backup_codes__mutmut_12, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_13': xǁMFAProviderǁgenerate_backup_codes__mutmut_13, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_14': xǁMFAProviderǁgenerate_backup_codes__mutmut_14, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_15': xǁMFAProviderǁgenerate_backup_codes__mutmut_15, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_16': xǁMFAProviderǁgenerate_backup_codes__mutmut_16, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_17': xǁMFAProviderǁgenerate_backup_codes__mutmut_17, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_18': xǁMFAProviderǁgenerate_backup_codes__mutmut_18, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_19': xǁMFAProviderǁgenerate_backup_codes__mutmut_19, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_20': xǁMFAProviderǁgenerate_backup_codes__mutmut_20, 
        'xǁMFAProviderǁgenerate_backup_codes__mutmut_21': xǁMFAProviderǁgenerate_backup_codes__mutmut_21
    }
    
    def generate_backup_codes(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁgenerate_backup_codes__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁgenerate_backup_codes__mutmut_mutants"), args, kwargs, self)
        return result 
    
    generate_backup_codes.__signature__ = _mutmut_signature(xǁMFAProviderǁgenerate_backup_codes__mutmut_orig)
    xǁMFAProviderǁgenerate_backup_codes__mutmut_orig.__name__ = 'xǁMFAProviderǁgenerate_backup_codes'
    
    def xǁMFAProviderǁverify_backup_code__mutmut_orig(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_1(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(None):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_2(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return True
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_3(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_4(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(None, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_5(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, None)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_6(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_7(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, )
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_8(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, True)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_9(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return True
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_10(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = None
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_11(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(None).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_12(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(None, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_13(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, None):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_14(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_15(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, ):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_16(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_17(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = None
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_18(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = False
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_19(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = None
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_20(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(None, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_21(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, None)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_22(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_23(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, )
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_24(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, False)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_25(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return False
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_26(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(None, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_27(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, None)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_28(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_29(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, )
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_30(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, True)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_31(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return True
        
        # No matching code
        self._record_attempt(user_id, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_32(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(None, False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_33(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, None)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_34(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(False)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_35(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, )
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_36(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, True)
        return False
    
    def xǁMFAProviderǁverify_backup_code__mutmut_37(self, user_id: str, code: str) -> bool:
        """
        Verify and consume a backup code.
        
        Args:
            user_id: User identifier
            code: Backup code to verify
        
        Returns:
            True if code is valid and not used, False otherwise
        """
        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False
        
        if user_id not in self._backup_codes:
            self._record_attempt(user_id, False)
            return False
        
        # Hash the provided code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find matching code
        for backup_code in self._backup_codes[user_id]:
            if secrets.compare_digest(backup_code.code_hash, code_hash):
                if not backup_code.used:
                    # Mark as used
                    backup_code.used = True
                    backup_code.used_at = time.time()
                    self._record_attempt(user_id, True)
                    return True
                else:
                    # Code already used
                    self._record_attempt(user_id, False)
                    return False
        
        # No matching code
        self._record_attempt(user_id, False)
        return True
    
    xǁMFAProviderǁverify_backup_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁverify_backup_code__mutmut_1': xǁMFAProviderǁverify_backup_code__mutmut_1, 
        'xǁMFAProviderǁverify_backup_code__mutmut_2': xǁMFAProviderǁverify_backup_code__mutmut_2, 
        'xǁMFAProviderǁverify_backup_code__mutmut_3': xǁMFAProviderǁverify_backup_code__mutmut_3, 
        'xǁMFAProviderǁverify_backup_code__mutmut_4': xǁMFAProviderǁverify_backup_code__mutmut_4, 
        'xǁMFAProviderǁverify_backup_code__mutmut_5': xǁMFAProviderǁverify_backup_code__mutmut_5, 
        'xǁMFAProviderǁverify_backup_code__mutmut_6': xǁMFAProviderǁverify_backup_code__mutmut_6, 
        'xǁMFAProviderǁverify_backup_code__mutmut_7': xǁMFAProviderǁverify_backup_code__mutmut_7, 
        'xǁMFAProviderǁverify_backup_code__mutmut_8': xǁMFAProviderǁverify_backup_code__mutmut_8, 
        'xǁMFAProviderǁverify_backup_code__mutmut_9': xǁMFAProviderǁverify_backup_code__mutmut_9, 
        'xǁMFAProviderǁverify_backup_code__mutmut_10': xǁMFAProviderǁverify_backup_code__mutmut_10, 
        'xǁMFAProviderǁverify_backup_code__mutmut_11': xǁMFAProviderǁverify_backup_code__mutmut_11, 
        'xǁMFAProviderǁverify_backup_code__mutmut_12': xǁMFAProviderǁverify_backup_code__mutmut_12, 
        'xǁMFAProviderǁverify_backup_code__mutmut_13': xǁMFAProviderǁverify_backup_code__mutmut_13, 
        'xǁMFAProviderǁverify_backup_code__mutmut_14': xǁMFAProviderǁverify_backup_code__mutmut_14, 
        'xǁMFAProviderǁverify_backup_code__mutmut_15': xǁMFAProviderǁverify_backup_code__mutmut_15, 
        'xǁMFAProviderǁverify_backup_code__mutmut_16': xǁMFAProviderǁverify_backup_code__mutmut_16, 
        'xǁMFAProviderǁverify_backup_code__mutmut_17': xǁMFAProviderǁverify_backup_code__mutmut_17, 
        'xǁMFAProviderǁverify_backup_code__mutmut_18': xǁMFAProviderǁverify_backup_code__mutmut_18, 
        'xǁMFAProviderǁverify_backup_code__mutmut_19': xǁMFAProviderǁverify_backup_code__mutmut_19, 
        'xǁMFAProviderǁverify_backup_code__mutmut_20': xǁMFAProviderǁverify_backup_code__mutmut_20, 
        'xǁMFAProviderǁverify_backup_code__mutmut_21': xǁMFAProviderǁverify_backup_code__mutmut_21, 
        'xǁMFAProviderǁverify_backup_code__mutmut_22': xǁMFAProviderǁverify_backup_code__mutmut_22, 
        'xǁMFAProviderǁverify_backup_code__mutmut_23': xǁMFAProviderǁverify_backup_code__mutmut_23, 
        'xǁMFAProviderǁverify_backup_code__mutmut_24': xǁMFAProviderǁverify_backup_code__mutmut_24, 
        'xǁMFAProviderǁverify_backup_code__mutmut_25': xǁMFAProviderǁverify_backup_code__mutmut_25, 
        'xǁMFAProviderǁverify_backup_code__mutmut_26': xǁMFAProviderǁverify_backup_code__mutmut_26, 
        'xǁMFAProviderǁverify_backup_code__mutmut_27': xǁMFAProviderǁverify_backup_code__mutmut_27, 
        'xǁMFAProviderǁverify_backup_code__mutmut_28': xǁMFAProviderǁverify_backup_code__mutmut_28, 
        'xǁMFAProviderǁverify_backup_code__mutmut_29': xǁMFAProviderǁverify_backup_code__mutmut_29, 
        'xǁMFAProviderǁverify_backup_code__mutmut_30': xǁMFAProviderǁverify_backup_code__mutmut_30, 
        'xǁMFAProviderǁverify_backup_code__mutmut_31': xǁMFAProviderǁverify_backup_code__mutmut_31, 
        'xǁMFAProviderǁverify_backup_code__mutmut_32': xǁMFAProviderǁverify_backup_code__mutmut_32, 
        'xǁMFAProviderǁverify_backup_code__mutmut_33': xǁMFAProviderǁverify_backup_code__mutmut_33, 
        'xǁMFAProviderǁverify_backup_code__mutmut_34': xǁMFAProviderǁverify_backup_code__mutmut_34, 
        'xǁMFAProviderǁverify_backup_code__mutmut_35': xǁMFAProviderǁverify_backup_code__mutmut_35, 
        'xǁMFAProviderǁverify_backup_code__mutmut_36': xǁMFAProviderǁverify_backup_code__mutmut_36, 
        'xǁMFAProviderǁverify_backup_code__mutmut_37': xǁMFAProviderǁverify_backup_code__mutmut_37
    }
    
    def verify_backup_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁverify_backup_code__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁverify_backup_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    verify_backup_code.__signature__ = _mutmut_signature(xǁMFAProviderǁverify_backup_code__mutmut_orig)
    xǁMFAProviderǁverify_backup_code__mutmut_orig.__name__ = 'xǁMFAProviderǁverify_backup_code'
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_orig(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id not in self._backup_codes:
            return 0
        
        return sum(1 for code in self._backup_codes[user_id] if not code.used)
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_1(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id in self._backup_codes:
            return 0
        
        return sum(1 for code in self._backup_codes[user_id] if not code.used)
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_2(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id not in self._backup_codes:
            return 1
        
        return sum(1 for code in self._backup_codes[user_id] if not code.used)
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_3(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id not in self._backup_codes:
            return 0
        
        return sum(None)
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_4(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id not in self._backup_codes:
            return 0
        
        return sum(2 for code in self._backup_codes[user_id] if not code.used)
    
    def xǁMFAProviderǁget_remaining_backup_codes__mutmut_5(self, user_id: str) -> int:
        """
        Get count of remaining (unused) backup codes.
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of unused backup codes
        """
        if user_id not in self._backup_codes:
            return 0
        
        return sum(1 for code in self._backup_codes[user_id] if code.used)
    
    xǁMFAProviderǁget_remaining_backup_codes__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁget_remaining_backup_codes__mutmut_1': xǁMFAProviderǁget_remaining_backup_codes__mutmut_1, 
        'xǁMFAProviderǁget_remaining_backup_codes__mutmut_2': xǁMFAProviderǁget_remaining_backup_codes__mutmut_2, 
        'xǁMFAProviderǁget_remaining_backup_codes__mutmut_3': xǁMFAProviderǁget_remaining_backup_codes__mutmut_3, 
        'xǁMFAProviderǁget_remaining_backup_codes__mutmut_4': xǁMFAProviderǁget_remaining_backup_codes__mutmut_4, 
        'xǁMFAProviderǁget_remaining_backup_codes__mutmut_5': xǁMFAProviderǁget_remaining_backup_codes__mutmut_5
    }
    
    def get_remaining_backup_codes(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁget_remaining_backup_codes__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁget_remaining_backup_codes__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_remaining_backup_codes.__signature__ = _mutmut_signature(xǁMFAProviderǁget_remaining_backup_codes__mutmut_orig)
    xǁMFAProviderǁget_remaining_backup_codes__mutmut_orig.__name__ = 'xǁMFAProviderǁget_remaining_backup_codes'
    
    def xǁMFAProviderǁdisable_mfa__mutmut_orig(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_1(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = None
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_2(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = True
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_3(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id not in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_4(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = None
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_5(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = False
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_6(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id not in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_7(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = None
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_8(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = False
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_9(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id not in self._attempts:
            del self._attempts[user_id]
        
        if user_id in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    def xǁMFAProviderǁdisable_mfa__mutmut_10(self, user_id: str) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA was disabled
        """
        removed = False
        
        if user_id in self._secret_store:
            del self._secret_store[user_id]
            removed = True
        
        if user_id in self._backup_codes:
            del self._backup_codes[user_id]
            removed = True
        
        if user_id in self._attempts:
            del self._attempts[user_id]
        
        if user_id not in self._locked_users:
            del self._locked_users[user_id]
        
        return removed
    
    xǁMFAProviderǁdisable_mfa__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁdisable_mfa__mutmut_1': xǁMFAProviderǁdisable_mfa__mutmut_1, 
        'xǁMFAProviderǁdisable_mfa__mutmut_2': xǁMFAProviderǁdisable_mfa__mutmut_2, 
        'xǁMFAProviderǁdisable_mfa__mutmut_3': xǁMFAProviderǁdisable_mfa__mutmut_3, 
        'xǁMFAProviderǁdisable_mfa__mutmut_4': xǁMFAProviderǁdisable_mfa__mutmut_4, 
        'xǁMFAProviderǁdisable_mfa__mutmut_5': xǁMFAProviderǁdisable_mfa__mutmut_5, 
        'xǁMFAProviderǁdisable_mfa__mutmut_6': xǁMFAProviderǁdisable_mfa__mutmut_6, 
        'xǁMFAProviderǁdisable_mfa__mutmut_7': xǁMFAProviderǁdisable_mfa__mutmut_7, 
        'xǁMFAProviderǁdisable_mfa__mutmut_8': xǁMFAProviderǁdisable_mfa__mutmut_8, 
        'xǁMFAProviderǁdisable_mfa__mutmut_9': xǁMFAProviderǁdisable_mfa__mutmut_9, 
        'xǁMFAProviderǁdisable_mfa__mutmut_10': xǁMFAProviderǁdisable_mfa__mutmut_10
    }
    
    def disable_mfa(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁdisable_mfa__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁdisable_mfa__mutmut_mutants"), args, kwargs, self)
        return result 
    
    disable_mfa.__signature__ = _mutmut_signature(xǁMFAProviderǁdisable_mfa__mutmut_orig)
    xǁMFAProviderǁdisable_mfa__mutmut_orig.__name__ = 'xǁMFAProviderǁdisable_mfa'
    
    def xǁMFAProviderǁis_mfa_enabled__mutmut_orig(self, user_id: str) -> bool:
        """
        Check if MFA is enabled for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA is enabled
        """
        return user_id in self._secret_store
    
    def xǁMFAProviderǁis_mfa_enabled__mutmut_1(self, user_id: str) -> bool:
        """
        Check if MFA is enabled for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if MFA is enabled
        """
        return user_id not in self._secret_store
    
    xǁMFAProviderǁis_mfa_enabled__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMFAProviderǁis_mfa_enabled__mutmut_1': xǁMFAProviderǁis_mfa_enabled__mutmut_1
    }
    
    def is_mfa_enabled(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMFAProviderǁis_mfa_enabled__mutmut_orig"), object.__getattribute__(self, "xǁMFAProviderǁis_mfa_enabled__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_mfa_enabled.__signature__ = _mutmut_signature(xǁMFAProviderǁis_mfa_enabled__mutmut_orig)
    xǁMFAProviderǁis_mfa_enabled__mutmut_orig.__name__ = 'xǁMFAProviderǁis_mfa_enabled'
    
    def get_mfa_user_count(self) -> int:
        """
        Get the number of users with MFA enabled.
        
        Returns:
            Count of users with MFA enabled
        """
        return len(self._secret_store)
