"""
Configuration for secret detection patterns and thresholds.

This module provides configurable patterns for secret detection,
allowing for customization and extension without modifying core code.
"""

from typing import Dict, List, Pattern
import re


# Entropy threshold for high-entropy string detection
ENTROPY_THRESHOLD = 4.5

# Minimum length for potential secrets
MIN_SECRET_LENGTH = 16

# Maximum length for potential secrets (to avoid false positives on large data)
MAX_SECRET_LENGTH = 512


class SecretPatterns:
    """
    Configurable secret detection patterns.
    
    Provides regex patterns for detecting various types of secrets
    with configurable exclusion patterns for common false positives.
    """
    
    # Core secret patterns with flexible matching and placeholder filtering
    PATTERNS: Dict[str, str] = {
        # API key with negative lookahead for placeholders
        "api_key": r'(?i)(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?(?!(?:YOUR_|your_|example|test|REPLACE|dummy|placeholder))([a-zA-Z0-9_\-]{16,})["\']?',
        "password": r'(?i)(?:password|passwd|pwd)["\']?\s*[:=]\s*["\'](?!(?:YOUR_|your_|example|test|password))([^"\']{8,})["\']',
        "token": r'(?i)(?:token|access[_-]?token)["\']?\s*[:=]\s*["\']?(?!(?:YOUR_|your_|example|test))([a-zA-Z0-9_\-\.]{20,})["\']?',
        "secret": r'(?i)(?:secret|secret[_-]?key)["\']?\s*[:=]\s*["\']?(?!(?:YOUR_|your_|example|test))([a-zA-Z0-9_\-]{16,})["\']?',
        "aws_access_key": r'(?i)(?:aws[_-]?access[_-]?key[_-]?id|AWS_ACCESS_KEY_ID)["\']?\s*[:=]\s*["\']?(?!(?:YOUR_|your_|AKIAIOSFODNN7EXAMPLE))([A-Z0-9]{20})["\']?',
        "aws_secret_key": r'(?i)(?:aws[_-]?secret[_-]?access[_-]?key|AWS_SECRET_ACCESS_KEY)["\']?\s*[:=]\s*["\']?(?!(?:YOUR_|your_|wJalrXUtnFEMI))([A-Za-z0-9/+=]{40})["\']?',
        # Fixed: GitHub token with word boundaries for standalone detection
        "github_token": r'\b((?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,})\b',
        "private_key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
        "slack_token": r'\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,})\b',
        "stripe_key": r'\b((?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24,})\b',
        "jwt": r'\b(eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*)\b',
        "bearer_token": r'(?i)bearer\s+([a-zA-Z0-9\-_\.]{20,})',
    }
    
    # Placeholder patterns that should NOT be flagged as secrets
    PLACEHOLDER_PATTERNS: List[str] = [
        r'(?i)example',
        r'(?i)placeholder',
        r'(?i)your[_-]?',
        r'(?i)xxx+',
        r'(?i)yyy+',
        r'(?i)zzz+',
        r'(?i)test[_-]?',
        r'(?i)dummy',
        r'(?i)fake',
        r'(?i)sample',
        r'(?i)template',
        r'(?i)<[^>]+>',  # HTML-like placeholders
        r'\$\{[^}]+\}',  # Variable substitution
        r'%[A-Z_]+%',    # Environment variable style
    ]
    
    # File extensions that commonly contain secrets (prioritize these)
    HIGH_RISK_EXTENSIONS: List[str] = [
        '.env', '.env.local', '.env.production', '.env.development',
        '.key', '.pem', '.p12', '.pfx', '.pkcs12',
        '.credentials', '.secret', '.secrets',
        'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
    ]
    
    # File patterns to exclude from secret scanning
    EXCLUDED_FILE_PATTERNS: List[str] = [
        r'\.git/',
        r'node_modules/',
        r'__pycache__/',
        r'\.pyc$',
        r'\.egg-info/',
        r'dist/',
        r'build/',
        r'\.test\.',
        r'\.example$',
        r'\.sample$',
        r'\.template$',
    ]
    
    @classmethod
    def get_compiled_patterns(cls) -> Dict[str, Pattern]:
        """Get compiled regex patterns for secret detection."""
        return {
            name: re.compile(pattern)
            for name, pattern in cls.PATTERNS.items()
        }
    
    @classmethod
    def get_compiled_placeholder_patterns(cls) -> List[Pattern]:
        """Get compiled regex patterns for placeholder detection."""
        return [re.compile(pattern) for pattern in cls.PLACEHOLDER_PATTERNS]
    
    @classmethod
    def is_placeholder(cls, value: str) -> bool:
        """
        Check if a value matches placeholder patterns.
        
        Args:
            value: String to check
            
        Returns:
            True if value appears to be a placeholder
        """
        placeholder_patterns = cls.get_compiled_placeholder_patterns()
        return any(pattern.search(value) for pattern in placeholder_patterns)
    
    @classmethod
    def is_high_risk_file(cls, filename: str) -> bool:
        """
        Check if a filename indicates high risk for secrets.
        
        Args:
            filename: File name or path to check
            
        Returns:
            True if file is high risk
        """
        filename_lower = filename.lower()
        return any(
            filename_lower.endswith(ext) or ext in filename_lower
            for ext in cls.HIGH_RISK_EXTENSIONS
        )
    
    @classmethod
    def should_exclude_file(cls, filepath: str) -> bool:
        """
        Check if a file should be excluded from scanning.
        
        Args:
            filepath: File path to check
            
        Returns:
            True if file should be excluded
        """
        return any(
            re.search(pattern, filepath)
            for pattern in cls.EXCLUDED_FILE_PATTERNS
        )


def calculate_entropy(data: str) -> float:
    """
    Calculate Shannon entropy of a string.
    
    Higher entropy indicates more randomness, which is characteristic
    of secrets, tokens, and cryptographic keys.
    
    Args:
        data: String to analyze
        
    Returns:
        Entropy value (bits per character)
    """
    if not data:
        return 0.0
    
    import math
    from collections import Counter
    
    # Count character frequencies
    counts = Counter(data)
    
    # Calculate entropy
    entropy = 0.0
    length = len(data)
    
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    return entropy


def has_high_entropy(value: str, threshold: float = ENTROPY_THRESHOLD) -> bool:
    """
    Check if a string has high entropy (likely a secret).
    
    Args:
        value: String to check
        threshold: Entropy threshold (default: 4.5)
        
    Returns:
        True if entropy exceeds threshold
    """
    if len(value) < MIN_SECRET_LENGTH:
        return False
    
    if len(value) > MAX_SECRET_LENGTH:
        return False
    
    entropy = calculate_entropy(value)
    return entropy >= threshold
