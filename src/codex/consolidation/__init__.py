"""
Consolidated utilities for duplication elimination.

This module provides centralized implementations of frequently-duplicated patterns
across the codebase, extracted during Phase 6 Wave 2 duplication consolidation campaign.

Pattern Groups:
  - Decorators: Validation, authorization, and error handling decorators
  - Errors: Centralized error handling and wrapping utilities
  - Imports: Consolidated import/export chains

Modules:
  - decorators: @validate, @require_auth, @handle_errors decorators
  - errors: Error wrapping, exception handlers, error response builders
"""

__all__ = []
