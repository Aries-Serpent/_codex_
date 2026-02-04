"""Agent memory system for persistent context across invocations.

This module provides a memory abstraction layer that allows agents to:
- Store and retrieve context between invocations
- Maintain conversation history
- Access long-term knowledge
- Support future vector database integration

The system uses a pluggable backend design with file-based storage by default.

Examples:
    Basic usage with default SQLite backend:

    >>> from codex.agents.memory import MemoryManager
    >>>
    >>> manager = MemoryManager(agent_id="assistant-1", session_id="session-123")
    >>> manager.store("User prefers Python over JavaScript", metadata={"importance": "high"})
    >>> memories = manager.recall("programming preferences")
    >>> print(memories[0].content)

    Using JSONL backend for simple file-based storage:

    >>> from codex.agents.memory import JSONLMemoryBackend, MemoryManager
    >>> from pathlib import Path
    >>>
    >>> backend = JSONLMemoryBackend(Path(".codex/memories.jsonl"))
    >>> manager = MemoryManager(backend=backend, agent_id="assistant-1")
    >>> manager.store({"user_id": "alice", "preference": "dark_mode"})
"""

from .backends import JSONLMemoryBackend, SQLiteMemoryBackend
from .manager import MemoryManager
from .protocol import MemoryEntry, MemoryProtocol, MemoryQuery

__all__ = [
    "MemoryProtocol",
    "MemoryEntry",
    "MemoryQuery",
    "JSONLMemoryBackend",
    "SQLiteMemoryBackend",
    "MemoryManager",
]

__version__ = "0.1.0"
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
