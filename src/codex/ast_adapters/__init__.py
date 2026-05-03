"""
AST Adapters for multi-language code analysis.

Provides standardized AST representation across Python, YAML, JSON, SQL and other languages.
"""

from .base_adapter import BaseASTAdapter, StandardizedASTNode
from .json_adapter import JSONASTAdapter
from .yaml_adapter import YAMLASTAdapter

try:
    from .python_adapter import PythonASTAdapter

    _PYTHON_ADAPTER_AVAILABLE = True
except ImportError:  # pragma: no cover — libcst optional dependency
    _PYTHON_ADAPTER_AVAILABLE = False

try:
    from .sql_adapter import SQLASTAdapter

    _SQL_ADAPTER_AVAILABLE = True
except ImportError:  # pragma: no cover — sqlparse optional dependency
    _SQL_ADAPTER_AVAILABLE = False

__all__ = [
    "BaseASTAdapter",
    "JSONASTAdapter",
    "StandardizedASTNode",
    "YAMLASTAdapter",
]

if _PYTHON_ADAPTER_AVAILABLE:
    __all__ += ["PythonASTAdapter"]

if _SQL_ADAPTER_AVAILABLE:
    __all__ += ["SQLASTAdapter"]
