"""Cryptographic security review module for Phase 3.

This module provides:
1. Verification of proper TLS/SSL configuration
2. Validation of hash algorithms (no MD5, SHA1)
3. Key management best practices
4. Cryptographic strength assessment
5. Secrets detection and validation
"""

from __future__ import annotations

import logging
import os
import re
from enum import Enum
from typing import Optional, Set

logger = logging.getLogger(__name__)


class CryptoStrength(str, Enum):
    """Cryptographic strength level."""

    WEAK = "weak"
    DEPRECATED = "deprecated"
    ACCEPTABLE = "acceptable"
    STRONG = "strong"
    EXCELLENT = "excellent"


class TLSVersion(str, Enum):
    """Supported TLS versions."""

    TLS_10 = "1.0"  # Deprecated
    TLS_11 = "1.1"  # Deprecated
    TLS_12 = "1.2"  # Acceptable
    TLS_13 = "1.3"  # Recommended


class CryptographicReviewer:
    """Review cryptographic configuration for security best practices."""

    # PHASE 3 HARDENING: Define supported algorithms
    WEAK_HASH_ALGORITHMS = {
        "md5": CryptoStrength.WEAK,
        "md4": CryptoStrength.WEAK,
        "sha1": CryptoStrength.WEAK,
    }

    ACCEPTABLE_HASH_ALGORITHMS = {
        "sha256": CryptoStrength.STRONG,
        "sha384": CryptoStrength.STRONG,
        "sha512": CryptoStrength.STRONG,
        "sha3_256": CryptoStrength.EXCELLENT,
        "sha3_512": CryptoStrength.EXCELLENT,
        "blake2b": CryptoStrength.EXCELLENT,
        "blake2s": CryptoStrength.EXCELLENT,
    }

    MINIMUM_KEY_SIZES = {
        "rsa": 2048,
        "dsa": 2048,
        "ecdsa": 256,
        "aes": 128,
    }

    def __init__(self, strict_mode: bool = False):
        """Initialize cryptographic reviewer.

        Parameters
        ----------
        strict_mode : bool
            If True, reject acceptable algorithms and require excellent ones
        """
        self.strict_mode = strict_mode

    def validate_hash_algorithm(self, algorithm: str) -> tuple[bool, CryptoStrength, str]:
        """Validate hash algorithm for security.

        Parameters
        ----------
        algorithm : str
            Hash algorithm name (lowercase)

        Returns
        -------
        tuple[bool, CryptoStrength, str]
            (is_valid, strength, recommendation)
        """
        algo_lower = algorithm.lower()

        # Check for weak algorithms
        if algo_lower in self.WEAK_HASH_ALGORITHMS:
            strength = self.WEAK_HASH_ALGORITHMS[algo_lower]
            return (
                False,
                strength,
                f"CRITICAL: {algorithm} is cryptographically broken. Use SHA-256 or better.",
            )

        # Check for acceptable algorithms
        if algo_lower in self.ACCEPTABLE_HASH_ALGORITHMS:
            strength = self.ACCEPTABLE_HASH_ALGORITHMS[algo_lower]
            if self.strict_mode and strength != CryptoStrength.EXCELLENT:
                return (
                    False,
                    strength,
                    f"STRICT: {algorithm} is acceptable but not excellent. Use SHA-3 or BLAKE2.",
                )
            return (True, strength, f"{algorithm} is acceptable for use.")

        # Unknown algorithm
        return (False, CryptoStrength.DEPRECATED, f"Unknown algorithm: {algorithm}")

    def validate_tls_version(self, version: str) -> tuple[bool, str]:
        """Validate TLS version for security.

        Parameters
        ----------
        version : str
            TLS version (e.g., "1.3", "1.2")

        Returns
        -------
        tuple[bool, str]
            (is_valid, recommendation)
        """
        try:
            tls_version = TLSVersion(version)
        except ValueError:
            return (False, f"Unknown TLS version: {version}")

        if tls_version in (TLSVersion.TLS_10, TLSVersion.TLS_11):
            return (
                False,
                f"CRITICAL: TLS {version} is deprecated and insecure. "
                "Use TLS 1.3 (recommended) or TLS 1.2 (minimum).",
            )

        if tls_version == TLSVersion.TLS_12:
            return (
                True,
                "TLS 1.2 is acceptable but TLS 1.3 is recommended for better security.",
            )

        if tls_version == TLSVersion.TLS_13:
            return (True, "TLS 1.3 is excellent. No issues found.")

        return (False, f"Unexpected TLS version: {version}")

    def validate_key_size(
        self,
        key_type: str,
        key_size: int,
    ) -> tuple[bool, str]:
        """Validate cryptographic key size.

        Parameters
        ----------
        key_type : str
            Key type (rsa, dsa, ecdsa, aes)
        key_size : int
            Key size in bits

        Returns
        -------
        tuple[bool, str]
            (is_valid, recommendation)
        """
        key_type_lower = key_type.lower()

        if key_type_lower not in self.MINIMUM_KEY_SIZES:
            return (False, f"Unknown key type: {key_type}")

        minimum_size = self.MINIMUM_KEY_SIZES[key_type_lower]

        if key_size < minimum_size:
            return (
                False,
                f"CRITICAL: {key_type} key size {key_size} is below minimum {minimum_size}",
            )

        # Warn for keys that are just barely acceptable
        if key_size == minimum_size and key_type_lower in ("rsa", "dsa"):
            return (
                True,
                f"{key_type} key size {key_size} is minimum acceptable. "
                f"Consider using {minimum_size + 1024} for extra security.",
            )

        return (True, f"{key_type} key size {key_size} is acceptable.")

    def scan_for_hardcoded_secrets(
        self,
        file_path: str,
        patterns: Optional[dict[str, str]] = None,
    ) -> list[dict]:
        """Scan file for hardcoded secrets.

        Parameters
        ----------
        file_path : str
            Path to file to scan
        patterns : Optional[dict[str, str]]
            Custom regex patterns for secret detection

        Returns
        -------
        list[dict]
            List of potential secrets found
        """
        if patterns is None:
            patterns = {
                "api_key": r'api[_-]?key\s*=\s*["\']([^\'"]+)["\']',
                "password": r'password\s*=\s*["\']([^\'"]+)["\']',
                "token": r'(token|auth)\s*=\s*["\']([^\'"]+)["\']',
                "aws_key": r'AKIA[0-9A-Z]{16}',
                "private_key": r'-----BEGIN RSA PRIVATE KEY-----',
            }

        secrets = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for secret_type, pattern in patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            secrets.append({
                                "file": file_path,
                                "line": line_num,
                                "type": secret_type,
                                "severity": "CRITICAL",
                            })
                            logger.warning(
                                f"Potential {secret_type} found in {file_path}:{line_num}"
                            )

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return secrets

    def validate_environment_variables(
        self,
        required_vars: Optional[Set[str]] = None,
    ) -> tuple[bool, list[str]]:
        """Validate that sensitive environment variables are set.

        Parameters
        ----------
        required_vars : Optional[Set[str]]
            Required environment variables

        Returns
        -------
        tuple[bool, list[str]]
            (all_present, missing_vars)
        """
        if required_vars is None:
            required_vars = {
                "TLS_CERT_PATH",
                "TLS_KEY_PATH",
                "ENCRYPTION_KEY",
                "HMAC_SECRET",
            }

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
                logger.warning(f"Required environment variable not set: {var}")

        return (len(missing) == 0, missing)


def get_crypto_strength_assessment(algorithms: dict[str, str]) -> dict:
    """Get overall cryptographic strength assessment.

    Parameters
    ----------
    algorithms : dict[str, str]
        Dictionary of algorithm_type -> algorithm_name

    Returns
    -------
    dict
        Assessment with recommendations
    """
    reviewer = CryptographicReviewer()
    assessment = {
        "overall_strength": CryptoStrength.EXCELLENT,
        "algorithms": {},
        "recommendations": [],
    }

    for algo_type, algo_name in algorithms.items():
        if algo_type == "hash":
            is_valid, strength, rec = reviewer.validate_hash_algorithm(algo_name)
            assessment["algorithms"][algo_name] = {
                "valid": is_valid,
                "strength": strength.value,
                "recommendation": rec,
            }
            if not is_valid:
                assessment["overall_strength"] = strength

        elif algo_type == "tls":
            is_valid, rec = reviewer.validate_tls_version(algo_name)
            assessment["algorithms"][algo_name] = {
                "valid": is_valid,
                "recommendation": rec,
            }

    return assessment


# PHASE 3 HARDENING: Default cryptographic configuration
DEFAULT_CRYPTO_CONFIG = {
    "hash_algorithm": "sha256",  # Minimum acceptable
    "hash_algorithm_preferred": "sha3_256",  # Recommended
    "tls_version": "1.3",  # Required for new deployments
    "tls_version_minimum": "1.2",  # Fallback minimum
    "key_size_rsa": 2048,  # Minimum
    "key_size_rsa_preferred": 4096,  # Recommended
}

__all__ = [
    "CryptoStrength",
    "TLSVersion",
    "CryptographicReviewer",
    "get_crypto_strength_assessment",
    "DEFAULT_CRYPTO_CONFIG",
]
