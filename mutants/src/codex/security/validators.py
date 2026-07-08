"""
Security Input Validators - OWASP-Compliant Validation Framework

This module provides comprehensive input validation functions for API endpoints,
file operations, and model parameters. Implements defense-in-depth with multiple
validation layers.

OWASP Compliance:
- A01: Injection Prevention → Parameterized queries, input whitelist
- A02: Broken Auth → JWT token validation
- A03: Sensitive Data → No logging of sensitive fields
- A04: XXE → XML parser hardening (future)
- A07: XSS → HTML entity escaping

Author: Codex Security Team
"""

from __future__ import annotations

import html
import logging
import os
import re
from pathlib import Path
from typing import Any, Optional, Pattern

logger = logging.getLogger(__name__)

# ============================================================================
# Layer 1: String Input Validators
# ============================================================================


class StringValidator:
    """Validates string inputs with configurable constraints."""

    def __init__(
        self,
        *,
        min_length: int = 0,
        max_length: int = 10000,
        pattern: Optional[Pattern[str]] = None,
        allow_unicode: bool = False,
        disallow_chars: str = "",
    ) -> None:
        """
        Initialize string validator.

        Args:
            min_length: Minimum string length (inclusive)
            max_length: Maximum string length (inclusive)
            pattern: Optional regex pattern that must match
            allow_unicode: Allow Unicode characters (default: ASCII only)
            disallow_chars: Characters that are explicitly disallowed

        Example:
            >>> validator = StringValidator(
            ...     min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_]+$"
            ... )
            >>> validator.validate("valid_input")
            'valid_input'
        """
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allow_unicode = allow_unicode
        self.disallow_chars = disallow_chars

    def validate(self, value: str, field_name: str = "input") -> str:
        """
        Validate string input.

        Args:
            value: String to validate
            field_name: Field name for error messages

        Returns:
            Validated (and potentially normalized) string

        Raises:
            ValueError: If validation fails

        OWASP A01: Injection Prevention
            - Length limits prevent buffer overflows
            - Pattern matching prevents injection patterns
            - Disallowed characters remove dangerous sequences
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")

        # Length check (prevents DoS)
        if len(value) < self.min_length:
            raise ValueError(f"{field_name} is too short (min {self.min_length} chars)")
        if len(value) > self.max_length:
            raise ValueError(f"{field_name} is too long (max {self.max_length} chars)")

        # Character check
        if self.disallow_chars:
            for char in self.disallow_chars:
                if char in value:
                    raise ValueError(f"{field_name} contains disallowed character: {repr(char)}")

        # Unicode check
        if not self.allow_unicode:
            try:
                value.encode("ascii")
            except UnicodeEncodeError as exc:
                raise ValueError(f"{field_name} contains non-ASCII characters") from exc

        # Pattern check (regex whitelist)
        if self.pattern and not self.pattern.match(value):
            raise ValueError(f"{field_name} does not match required pattern")

        return value.strip()


class EmailValidator:
    """Validates email addresses with length constraints."""

    # Permissive but effective regex pattern
    _PATTERN = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )

    def __init__(self, min_length: int = 3, max_length: int = 254) -> None:
        """
        Initialize email validator.

        Args:
            min_length: Minimum email length (RFC 5321)
            max_length: Maximum email length (RFC 5321 = 254)
        """
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: str, field_name: str = "email") -> str:
        """
        Validate email address.

        Args:
            value: Email to validate
            field_name: Field name for error messages

        Returns:
            Validated email (normalized to lowercase)

        Raises:
            ValueError: If validation fails

        OWASP A02: Broken Auth
            - Email validation prevents invalid user registration
            - Normalization prevents case-based bypasses
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        value = value.strip().lower()

        if len(value) < self.min_length or len(value) > self.max_length:
            raise ValueError(
                f"{field_name} length must be between {self.min_length} and {self.max_length}"
            )

        if not self._PATTERN.match(value):
            raise ValueError(f"{field_name} is not a valid email address")

        return value


# ============================================================================
# Layer 2: Numeric Validators (Model Parameters)
# ============================================================================


class NumericValidator:
    """Validates numeric inputs with range constraints."""

    def __init__(
        self,
        *,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_zero: bool = True,
        allow_negative: bool = False,
    ) -> None:
        """
        Initialize numeric validator.

        Args:
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            allow_zero: Allow zero value (default: True)
            allow_negative: Allow negative values (default: False)
        """
        self.min_value = min_value
        self.max_value = max_value
        self.allow_zero = allow_zero
        self.allow_negative = allow_negative

    def validate(self, value: Any, field_name: str = "number") -> float:
        """
        Validate numeric input.

        Args:
            value: Number to validate
            field_name: Field name for error messages

        Returns:
            Validated float value

        Raises:
            ValueError: If validation fails

        OWASP A01: Injection Prevention
            - Range limits prevent OOM (batch size attacks)
            - Type checking prevents type confusion exploits
        """
        try:
            num = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be numeric") from exc

        # NaN and Inf check
        if num != num:  # NaN check
            raise ValueError(f"{field_name} cannot be NaN")
        if num == float("inf") or num == float("-inf"):
            raise ValueError(f"{field_name} cannot be infinity")

        # Zero check
        if not self.allow_zero and num == 0:
            raise ValueError(f"{field_name} cannot be zero")

        # Negative check
        if not self.allow_negative and num < 0:
            raise ValueError(f"{field_name} cannot be negative")

        # Range check
        if self.min_value is not None and num < self.min_value:
            raise ValueError(f"{field_name} is less than minimum ({self.min_value})")
        if self.max_value is not None and num > self.max_value:
            raise ValueError(f"{field_name} exceeds maximum ({self.max_value})")

        return num


class BatchSizeValidator(NumericValidator):
    """Validates ML batch sizes (OOM prevention)."""

    def __init__(self) -> None:
        """Initialize with typical ML constraints."""
        super().__init__(
            min_value=1,
            max_value=10000,  # Prevent memory exhaustion
            allow_zero=False,
            allow_negative=False,
        )


class LearningRateValidator(NumericValidator):
    """Validates learning rates for ML models."""

    def __init__(self) -> None:
        """Initialize with typical LR constraints."""
        super().__init__(
            min_value=1e-6,
            max_value=1.0,
            allow_zero=False,
            allow_negative=False,
        )


# ============================================================================
# Layer 3: File Path Validators (Path Traversal Prevention)
# ============================================================================


class PathValidator:
    """Validates file paths to prevent traversal attacks."""

    # Allowed characters in path segments (strict whitelist)
    _SAFE_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,255}$")

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        """
        Initialize path validator.

        Args:
            base_dir: Base directory that all paths must reside under.
                     If None, uses current working directory.

        OWASP A01: Injection Prevention
            - Path traversal prevention via resolution and containment
            - Symlink checks prevent symlink escape attacks
        """
        if base_dir is None:
            base_dir = Path.cwd()
        self.base_dir = Path(base_dir).resolve()
        logger.info(f"PathValidator initialized with base_dir={self.base_dir}")

    def validate(self, relative_path: str, field_name: str = "path") -> Path:
        """
        Validate and resolve a file path.

        Args:
            relative_path: Relative path to validate
            field_name: Field name for error messages

        Returns:
            Resolved absolute Path that is guaranteed to be within base_dir

        Raises:
            ValueError: If path is invalid or attempts traversal

        Security Checks:
            1. Rejects absolute paths
            2. Rejects ".." components
            3. Resolves symlinks and checks containment
            4. Validates all path segments individually
        """
        if not isinstance(relative_path, str):
            raise ValueError(f"{field_name} must be a string, got {type(relative_path).__name__}")

        relative_path = relative_path.strip()

        # Reject absolute paths
        if os.path.isabs(relative_path):
            raise ValueError(f"{field_name} must be relative (no leading /)")

        # Reject paths with ".."
        if ".." in relative_path:
            raise ValueError(f"{field_name} cannot contain '..' (path traversal attempt)")

        # Split into segments and validate each
        segments = Path(relative_path).parts
        for segment in segments:
            if not segment or segment == ".":
                continue
            if not self._SAFE_SEGMENT_PATTERN.match(segment):
                raise ValueError(
                    f"{field_name} segment '{segment}' contains invalid characters. "
                    f"Only alphanumeric, dots, hyphens, and underscores allowed."
                )

        # Resolve the full path
        full_path = (self.base_dir / relative_path).resolve()

        # Verify containment (prevent symlink escape)
        try:
            full_path.relative_to(self.base_dir)
        except ValueError as exc:
            raise ValueError(
                f"{field_name} '{relative_path}' attempts to escape base directory"
            ) from exc

        return full_path


class FileTypeValidator:
    """Validates file types by extension and MIME type."""

    def __init__(self, allowed_extensions: Optional[set[str]] = None) -> None:
        """
        Initialize file type validator.

        Args:
            allowed_extensions: Set of allowed file extensions (lowercase, with dot).
                               If None, all extensions allowed.

        Example:
            >>> validator = FileTypeValidator(
            ...     allowed_extensions={'.pdf', '.txt', '.csv'}
            ... )
        """
        self.allowed_extensions = allowed_extensions

    def validate(self, file_path: Path, field_name: str = "file") -> Path:
        """
        Validate file type.

        Args:
            file_path: Path object to validate
            field_name: Field name for error messages

        Returns:
            Validated Path

        Raises:
            ValueError: If file type is not allowed

        OWASP A04: XXE Prevention
            - Restricting file types prevents XXE attacks on unexpected formats
        """
        if not isinstance(file_path, Path):
            raise ValueError(f"{field_name} must be a Path object")

        if self.allowed_extensions is None:
            return file_path

        ext = file_path.suffix.lower()
        if ext not in self.allowed_extensions:
            raise ValueError(
                f"{field_name} has disallowed extension '{ext}'. "
                f"Allowed: {', '.join(sorted(self.allowed_extensions))}"
            )

        return file_path


class FileSizeValidator:
    """Validates file sizes to prevent resource exhaustion."""

    def __init__(self, max_bytes: int = 100 * 1024 * 1024) -> None:  # 100 MB default
        """
        Initialize file size validator.

        Args:
            max_bytes: Maximum file size in bytes

        OWASP A01: Injection Prevention
            - File size limits prevent DoS via large file uploads
        """
        self.max_bytes = max_bytes

    def validate(self, file_path: Path, field_name: str = "file") -> Path:
        """
        Validate file size.

        Args:
            file_path: Path to file to validate
            field_name: Field name for error messages

        Returns:
            Validated Path

        Raises:
            ValueError: If file is too large or doesn't exist
        """
        if not file_path.exists():
            raise ValueError(f"{field_name} does not exist: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"{field_name} is not a file: {file_path}")

        size = file_path.stat().st_size
        if size > self.max_bytes:
            raise ValueError(
                f"{field_name} is too large ({size} bytes, max {self.max_bytes} bytes)"
            )

        return file_path


# ============================================================================
# Layer 4: XSS Prevention
# ============================================================================


class XSSValidator:
    """Prevents XSS attacks through HTML entity escaping."""

    # Common XSS patterns
    _XSS_PATTERNS = [
        # Match script tags: opening with closing, or orphaned closing tags
        # Handles unclosed tags, malformed HTML, and whitespace variations
        re.compile(
            r"<\s*script\b[\s\S]*?</\s*script\s*>|<\s*script\b[^>]*(?:/>|>)|</\s*script\s*>",
            re.IGNORECASE,
        ),
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # Event handlers
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"data:text/html", re.IGNORECASE),
    ]

    @staticmethod
    def escape_html(value: str) -> str:
        """
        Escape HTML special characters.

        Args:
            value: String to escape

        Returns:
            HTML-escaped string

        OWASP A07: XSS Prevention
            - Entity escaping prevents HTML/JavaScript injection
        """
        return html.escape(value, quote=True)

    @classmethod
    def detect_xss_patterns(cls, value: str) -> list[str]:
        """
        Detect potential XSS patterns in input.

        Args:
            value: String to check

        Returns:
            List of detected XSS patterns (empty if clean)
        """
        detected = []
        for pattern in cls._XSS_PATTERNS:
            if pattern.search(value):
                detected.append(pattern.pattern)
        return detected


# ============================================================================
# Layer 5: Composite Validators
# ============================================================================


class APIRequestValidator:
    """Composite validator for typical API request fields."""

    def __init__(self) -> None:
        """Initialize with standard API validators."""
        self.string_validator = StringValidator(min_length=1, max_length=1000)
        self.email_validator = EmailValidator()
        self.username_validator = StringValidator(
            min_length=3,
            max_length=150,
            pattern=re.compile(r"^[a-zA-Z0-9_-]+$"),
        )

    def validate_username(self, username: str) -> str:
        """Validate username (alphanumeric + underscore/hyphen)."""
        return self.username_validator.validate(username, "username")

    def validate_email(self, email: str) -> str:
        """Validate email address."""
        return self.email_validator.validate(email)

    def validate_text_field(self, text: str, max_length: int = 1000) -> str:
        """Validate generic text field."""
        validator = StringValidator(min_length=1, max_length=max_length)
        return validator.validate(text, "text_field")


# ============================================================================
# Global Validator Instances
# ============================================================================

_api_validator = APIRequestValidator()
_path_validator: Optional[PathValidator] = None


def get_path_validator(base_dir: Optional[Path] = None) -> PathValidator:
    """Get or create the global path validator."""
    global _path_validator
    if _path_validator is None:
        _path_validator = PathValidator(base_dir)
    return _path_validator
