"""Rust Error Validator Agent - Scans for panic risks in Rust code."""

__version__ = "1.0.0"

from .agent import RustErrorValidator, Finding

__all__ = ['RustErrorValidator', 'Finding']
