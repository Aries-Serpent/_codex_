"""Zendesk App Framework legacy tooling."""

from .reader import ZAFParseError, read_zaf, scaffold_template

__all__ = ["ZAFParseError", "read_zaf", "scaffold_template"]
