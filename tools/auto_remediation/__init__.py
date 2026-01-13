"""
Auto-Remediation Package.

Provides intelligent fix generation, automated PR creation, and fix verification
for security vulnerabilities detected by the ML threat detector.
"""

__version__ = "1.0.0"

from .fix_generator import FixContext, FixStrategy, GeneratedFix, IntelligentFixGenerator
from .pr_generator import AutomatedPRGenerator, PRConfig, PRMetadata
from .verifier import FixVerifier, PreFixSnapshot, PostFixSnapshot, VerificationResult

__all__ = [
    "FixContext",
    "FixStrategy",
    "GeneratedFix",
    "IntelligentFixGenerator",
    "AutomatedPRGenerator",
    "PRConfig",
    "PRMetadata",
    "FixVerifier",
    "PreFixSnapshot",
    "PostFixSnapshot",
    "VerificationResult",
]
