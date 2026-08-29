"""Zendesk App Framework (ZAF) legacy package interpreters."""

from __future__ import annotations

from .reader import ZendeskAppPackageError, read_zaf, scaffold_template

__all__ = [
    "ZendeskAppPackageError",
    "read_zaf",
    "scaffold_template",
]
