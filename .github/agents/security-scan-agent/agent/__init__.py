"""
Security Scan Agent package.

Provides security scanning, SARIF parsing, false positive filtering, and PR annotation.
"""

from .annotator import Annotation, PRAnnotator
from .filter import FalsePositiveFilter, FilterRule
from .parser import Finding, Location, ParsedSARIF, SARIFParser
from .scanner import ScanResult, SecurityScanner

__all__ = [
    # Scanner
    "SecurityScanner",
    "ScanResult",
    # Parser
    "SARIFParser",
    "ParsedSARIF",
    "Finding",
    "Location",
    # Filter
    "FalsePositiveFilter",
    "FilterRule",
    # Annotator
    "PRAnnotator",
    "Annotation",
]
