"""Static analysis module."""

from .analyzer import FileAnalysis, StaticReport, analyze

__all__ = ["analyze", "StaticReport", "FileAnalysis"]
