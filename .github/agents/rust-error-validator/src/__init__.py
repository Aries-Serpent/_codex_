"""Rust Error Validator Agent - Scans for panic risks in Rust code."""

__version__ = "1.0.0"

from .agent import Finding, RustErrorValidator

__all__ = ['RustErrorValidator', 'Finding']
