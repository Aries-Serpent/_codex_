"""Multi-language AST support via tree-sitter."""

from __future__ import annotations

import importlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LanguageRegistry:
    """Registry for tree-sitter language parsers.

    Provides lazy loading and caching of language parsers
    for multi-language AST analysis.
    """

    # Frozen set of allowed module names for security
    _ALLOWED_MODULES = frozenset(
        {
            "tree_sitter_python",
            "tree_sitter_yaml",
            "tree_sitter_json",
            "tree_sitter_javascript",
            "tree_sitter_typescript",
        }
    )

    LANGUAGES: dict[str, str] = {
        "python": "tree_sitter_python",
        "yaml": "tree_sitter_yaml",
        "json": "tree_sitter_json",
        "javascript": "tree_sitter_javascript",
        "typescript": "tree_sitter_typescript",
    }

    _cache: dict[str, object] = {}

    @classmethod
    def get_language(cls, name: str) -> Optional[object]:
        """Get language parser by name.

        Args:
            name: Language name (e.g., 'python', 'yaml')

        Returns:
            Language parser object or None if not available
        """
        if name in cls._cache:
            return cls._cache[name]

        if name not in cls.LANGUAGES:
            logger.warning(f"Unsupported language: {name}")
            return None

        module_name = cls.LANGUAGES[name]

        # Security: Only allow importing from whitelist
        if module_name not in cls._ALLOWED_MODULES:
            logger.error(f"Module {module_name} not in allowed list")
            return None

        try:
            # Use importlib.import_module for safer importing
            module = importlib.import_module(module_name)

            # Try to get tree-sitter Language
            try:
                from tree_sitter import Language

                lang = Language(module.language())
                cls._cache[name] = lang
                logger.info(f"Loaded language parser for {name}")
                return lang
            except ImportError:
                logger.warning("tree-sitter not installed - install with: pip install tree-sitter")
                return None

        except ImportError:
            logger.warning(f"Tree-sitter module not installed: {module_name}")
            logger.info(f"Install with: pip install {module_name}")
            return None

    @classmethod
    def is_supported(cls, name: str) -> bool:
        """Check if language is supported."""
        return name in cls.LANGUAGES

    @classmethod
    def list_languages(cls) -> list[str]:
        """Get list of supported languages."""
        return list(cls.LANGUAGES.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the language parser cache."""
        cls._cache.clear()


__all__ = ["LanguageRegistry"]
