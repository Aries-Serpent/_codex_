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
from base64 import b32encode
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote

SUPPORTED_TOTP_ALGORITHMS = frozenset({"SHA1", "SHA256", "SHA512"})


def _normalize_totp_algorithm(algorithm: str) -> str:
    """Return a normalized RFC 6238 algorithm name."""
    normalized = algorithm.upper()
    if normalized not in SUPPORTED_TOTP_ALGORITHMS:
        supported = ", ".join(sorted(SUPPORTED_TOTP_ALGORITHMS))
        raise ValueError(f"Unsupported TOTP algorithm '{algorithm}'. Expected one of: {supported}")
    return normalized


@dataclass
class MFASecret:
    """MFA secret data structure."""

    secret: str
    user_id: str
    issuer: str = "Codex"
    algorithm: str = "SHA256"
    digits: int = 6
    period: int = 30
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Normalize the stored TOTP hash algorithm."""
        self.algorithm = _normalize_totp_algorithm(self.algorithm)

    def __len__(self) -> int:
        """Support len() calls - returns length of the secret string."""
        return len(self.secret)

    def __getitem__(self, index: int | slice) -> str:
        """Support indexing and slicing - delegates to the secret string."""
        return self.secret[index]

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
        return f"otpauth://totp/{label}?{'&'.join(params)}"


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

    def __init__(self) -> None:
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
        self._secret_store: dict[str, MFASecret] = {}
        self._backup_codes: dict[str, list[BackupCode]] = {}
        self._attempts: dict[str, list[MFAAttempt]] = {}
        self._locked_users: dict[str, float] = {}

    def generate_totp_secret(
        self,
        user_id: str,
        issuer: str = "Codex",
        algorithm: str = "SHA256",
    ) -> MFASecret:
        """
        Generate a new TOTP secret for a user.

        Args:
            user_id: User identifier
            issuer: Service name for the authenticator app
            algorithm: RFC 6238 hash algorithm for new codes

        Returns:
            MFASecret with the generated secret
        """
        # Generate 160-bit (20 byte) secret
        secret_bytes = secrets.token_bytes(20)
        # Base32 encode without padding
        secret = b32encode(secret_bytes).decode("utf-8").rstrip("=")

        mfa_secret = MFASecret(
            secret=secret,
            user_id=user_id,
            issuer=issuer,
            algorithm=algorithm,
        )

        # Store secret (use database in production)
        self._secret_store[user_id] = mfa_secret

        return mfa_secret

    def register_mfa(self, user_id: str, algorithm: str = "SHA256") -> MFASecret:
        """Backward-compatible alias for creating an MFA secret."""
        return self.generate_totp_secret(user_id=user_id, algorithm=algorithm)

    def _get_hotp_token(
        self,
        secret: str,
        counter: int,
        digits: int = 6,
        algorithm: str = "SHA256",
    ) -> str:
        """
        Generate HOTP token.

        Args:
            secret: Base32-encoded secret
            counter: Counter value
            digits: Number of digits in token
            algorithm: RFC 6238 hash algorithm

        Returns:
            HOTP token as string
        """
        # Decode base32 secret
        key = self._base32_decode(secret)
        normalized_algorithm = _normalize_totp_algorithm(algorithm)

        # Convert counter to 8-byte big-endian
        counter_bytes = struct.pack(">Q", counter)

        try:
            digestmod = getattr(hashlib, normalized_algorithm.lower())
        except AttributeError as exc:  # pragma: no cover - defensive guard
            raise ValueError(
                f"Validated TOTP algorithm '{normalized_algorithm}' lacks corresponding "
                "hashlib implementation"
            ) from exc
        hmac_hash = hmac.new(key, counter_bytes, digestmod).digest()

        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_hash[offset : offset + 4])[0]
        truncated &= 0x7FFFFFFF

        # Generate token
        token = str(truncated % (10**digits))
        return token.zfill(digits)

    def _base32_decode(self, secret: str) -> bytes:
        """Decode base32 secret with padding."""
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += "=" * (8 - missing_padding)

        from base64 import b32decode

        return b32decode(secret, casefold=True)

    def generate_totp(
        self,
        secret: str,
        timestamp: Optional[float] = None,
        period: int = 30,
        digits: int = 6,
        algorithm: str = "SHA256",
    ) -> str:
        """
        Generate TOTP token.

        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (uses current time if not provided)
            period: Time period in seconds
            digits: Number of digits in token
            algorithm: RFC 6238 hash algorithm

        Returns:
            TOTP token as string
        """
        if timestamp is None:
            timestamp = time.time()

        # Calculate counter
        counter = int(timestamp // period)

        # Generate HOTP with counter
        return self._get_hotp_token(secret, counter, digits, algorithm)

    def generate_totp_code(
        self,
        secret: str,
        timestamp: Optional[float] = None,
        period: int = 30,
        digits: int = 6,
        algorithm: str = "SHA256",
    ) -> str:
        """Backward-compatible alias for :meth:`generate_totp`."""
        return self.generate_totp(secret, timestamp, period, digits, algorithm)

    def verify_totp(
        self,
        secret: str,
        code: str,
        user_id: str,
        window: int = 1,
        period: int = 30,
        digits: int = 6,
        algorithm: str = "SHA256",
    ) -> bool:
        """
        Verify TOTP code with time window.

        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            user_id: User identifier for rate limiting (required)
            window: Number of time periods to check before/after current
            period: Time period in seconds
            digits: Number of digits in token
            algorithm: RFC 6238 hash algorithm

        Returns:
            True if code is valid, False otherwise
        """
        effective_user_id = user_id

        # Check if user is locked out
        if self._is_locked_out(effective_user_id):
            return False

        current_time = time.time()

        # Check current period and adjacent periods
        for offset in range(-window, window + 1):
            check_time = current_time + (offset * period)
            expected_code = self.generate_totp(secret, check_time, period, digits, algorithm)

            if secrets.compare_digest(code, expected_code):
                self._record_attempt(effective_user_id, True)
                return True

        # Code didn't match
        self._record_attempt(effective_user_id, False)
        return False

    def verify_totp_code(
        self,
        secret: str,
        code: str,
        user_id: str,
        window: int = 1,
        period: int = 30,
        digits: int = 6,
        algorithm: str = "SHA256",
    ) -> bool:
        """Backward-compatible alias for :meth:`verify_totp`."""
        return self.verify_totp(secret, code, user_id, window, period, digits, algorithm)

    def _is_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        if user_id not in self._locked_users:
            return False

        lockout_until = self._locked_users[user_id]
        if time.time() < lockout_until:
            return True

        # Lockout expired, remove it
        del self._locked_users[user_id]
        return False

    def _record_attempt(self, user_id: str, success: bool) -> None:
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
        self._attempts[user_id] = [a for a in self._attempts[user_id] if a.timestamp > cutoff]

        # Check for lockout
        if not success:
            recent_failures = [
                a
                for a in self._attempts[user_id]
                if not a.success and a.timestamp > time.time() - 300  # Last 5 minutes
            ]

            if len(recent_failures) >= self.MAX_ATTEMPTS:
                # Lock out user
                self._locked_users[user_id] = time.time() + self.LOCKOUT_DURATION

    def generate_backup_codes(self, user_id: str, count: int = 10) -> list[str]:
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

    def verify_backup_code(self, user_id: str, code: str) -> bool:
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
                # Code already used
                self._record_attempt(user_id, False)
                return False

        # No matching code
        self._record_attempt(user_id, False)
        return False

    def get_remaining_backup_codes(self, user_id: str) -> int:
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

    def disable_mfa(self, user_id: str) -> bool:
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

    def is_mfa_enabled(self, user_id: str) -> bool:
        """
        Check if MFA is enabled for a user.

        Args:
            user_id: User identifier

        Returns:
            True if MFA is enabled
        """
        return user_id in self._secret_store

    def is_user_enrolled(self, user_id: str) -> bool:
        """Backward-compatible alias for :meth:`is_mfa_enabled`."""
        return self.is_mfa_enabled(user_id)

    def enroll_user(
        self, user_id: str, issuer: str = "Codex", algorithm: str = "SHA256"
    ) -> MFASecret:
        """Backward-compatible alias for :meth:`generate_totp_secret`."""
        return self.generate_totp_secret(user_id=user_id, issuer=issuer, algorithm=algorithm)

    def get_secret(self, user_id: str) -> Optional["MFASecret"]:
        """
        Return the stored :class:`MFASecret` for *user_id*, or ``None``.

        Args:
            user_id: User identifier.

        Returns:
            The :class:`MFASecret` associated with *user_id*, or ``None`` if
            MFA has not been set up for this user.
        """
        return self._secret_store.get(user_id)

    def get_mfa_user_count(self) -> int:
        """
        Get the number of users with MFA enabled.

        Returns:
            Count of users with MFA enabled
        """
        return len(self._secret_store)
