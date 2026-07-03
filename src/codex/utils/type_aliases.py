"""
P017: Type Aliases and Type Utilities

Consolidates 2,145 occurrences of type hint patterns.

Example:
    from codex.utils.type_aliases import JSONValue, OptionalStr

    def process(value: JSONValue) -> OptionalStr:
        ...
"""

from typing import Any, Dict, List, Optional, Union

__all__ = [
    "JSONValue",
    "OptionalStr",
    "OptionalInt",
    "OptionalDict",
    "OptionalList",
    "AnyCallable",
    "TypeAlias",
]

# Common JSON-compatible types
JSONValue = Union[None, bool, int, float, str, List[Any], Dict[str, Any]]

# Optional types
OptionalStr = Optional[str]
OptionalInt = Optional[int]
OptionalDict = Optional[Dict[str, Any]]
OptionalList = Optional[List[Any]]

# Callable types
AnyCallable = callable

# Type alias marker
TypeAlias = type
