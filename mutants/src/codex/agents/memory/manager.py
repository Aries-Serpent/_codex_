"""High-level memory manager for agent memory operations.

Provides a convenient API for agents to interact with the memory system.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from .backends import SQLiteMemoryBackend
from .protocol import MemoryEntry, MemoryProtocol, MemoryQuery

logger = logging.getLogger(__name__)
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


class MemoryManager:
    """High-level manager for agent memory operations.
    
    Provides a simple API for storing and retrieving memories with automatic
    session management and context tracking.
    
    Args:
        backend: Memory storage backend (defaults to SQLite)
        agent_id: ID of the agent using this manager
        session_id: Current session ID (optional)
    
    Examples:
        >>> manager = MemoryManager(agent_id="assistant-1")
        >>> manager.store("User prefers concise responses", metadata={"importance": "high"})
        >>> memories = manager.recall("user preferences")
    """
    
    def xǁMemoryManagerǁ__init____mutmut_orig(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_1(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is not None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_2(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = None
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_3(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir and Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_4(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(None)
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_5(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path("XX.codex/agent_memoryXX")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_6(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".CODEX/AGENT_MEMORY")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_7(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=None, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_8(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=None)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_9(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_10(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, )
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_11(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=False, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_12(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=False)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_13(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = None
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_14(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(None)
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_15(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir * "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_16(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "XXmemories.dbXX")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_17(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "MEMORIES.DB")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_18(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = None
        self.agent_id = agent_id
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_19(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = None
        self.session_id = session_id
    
    def xǁMemoryManagerǁ__init____mutmut_20(
        self,
        backend: Optional[MemoryProtocol] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[Path] = None,
    ):
        if backend is None:
            # Default to SQLite backend
            storage_dir = storage_dir or Path(".codex/agent_memory")
            storage_dir.mkdir(parents=True, exist_ok=True)
            backend = SQLiteMemoryBackend(storage_dir / "memories.db")
        
        self.backend = backend
        self.agent_id = agent_id
        self.session_id = None
    
    xǁMemoryManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁ__init____mutmut_1': xǁMemoryManagerǁ__init____mutmut_1, 
        'xǁMemoryManagerǁ__init____mutmut_2': xǁMemoryManagerǁ__init____mutmut_2, 
        'xǁMemoryManagerǁ__init____mutmut_3': xǁMemoryManagerǁ__init____mutmut_3, 
        'xǁMemoryManagerǁ__init____mutmut_4': xǁMemoryManagerǁ__init____mutmut_4, 
        'xǁMemoryManagerǁ__init____mutmut_5': xǁMemoryManagerǁ__init____mutmut_5, 
        'xǁMemoryManagerǁ__init____mutmut_6': xǁMemoryManagerǁ__init____mutmut_6, 
        'xǁMemoryManagerǁ__init____mutmut_7': xǁMemoryManagerǁ__init____mutmut_7, 
        'xǁMemoryManagerǁ__init____mutmut_8': xǁMemoryManagerǁ__init____mutmut_8, 
        'xǁMemoryManagerǁ__init____mutmut_9': xǁMemoryManagerǁ__init____mutmut_9, 
        'xǁMemoryManagerǁ__init____mutmut_10': xǁMemoryManagerǁ__init____mutmut_10, 
        'xǁMemoryManagerǁ__init____mutmut_11': xǁMemoryManagerǁ__init____mutmut_11, 
        'xǁMemoryManagerǁ__init____mutmut_12': xǁMemoryManagerǁ__init____mutmut_12, 
        'xǁMemoryManagerǁ__init____mutmut_13': xǁMemoryManagerǁ__init____mutmut_13, 
        'xǁMemoryManagerǁ__init____mutmut_14': xǁMemoryManagerǁ__init____mutmut_14, 
        'xǁMemoryManagerǁ__init____mutmut_15': xǁMemoryManagerǁ__init____mutmut_15, 
        'xǁMemoryManagerǁ__init____mutmut_16': xǁMemoryManagerǁ__init____mutmut_16, 
        'xǁMemoryManagerǁ__init____mutmut_17': xǁMemoryManagerǁ__init____mutmut_17, 
        'xǁMemoryManagerǁ__init____mutmut_18': xǁMemoryManagerǁ__init____mutmut_18, 
        'xǁMemoryManagerǁ__init____mutmut_19': xǁMemoryManagerǁ__init____mutmut_19, 
        'xǁMemoryManagerǁ__init____mutmut_20': xǁMemoryManagerǁ__init____mutmut_20
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMemoryManagerǁ__init____mutmut_orig)
    xǁMemoryManagerǁ__init____mutmut_orig.__name__ = 'xǁMemoryManagerǁ__init__'
    
    def xǁMemoryManagerǁstore__mutmut_orig(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_1(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = None
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_2(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=None,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_3(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=None,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_4(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=None,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_5(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=None,
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_6(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_7(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_8(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_9(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_10(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id and self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_11(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata and {},
        )
        
        self.backend.store(entry)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_12(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(None)
        logger.debug(f"Stored memory: {entry.id}")
        return entry
    
    def xǁMemoryManagerǁstore__mutmut_13(
        self,
        content: str | dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> MemoryEntry:
        """Store a new memory.
        
        Args:
            content: The memory content (text or structured data)
            metadata: Optional metadata (importance, tags, etc.)
            session_id: Override session ID for this memory
            
        Returns:
            The stored memory entry
        """
        entry = MemoryEntry(
            content=content,
            agent_id=self.agent_id,
            session_id=session_id or self.session_id,
            metadata=metadata or {},
        )
        
        self.backend.store(entry)
        logger.debug(None)
        return entry
    
    xǁMemoryManagerǁstore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁstore__mutmut_1': xǁMemoryManagerǁstore__mutmut_1, 
        'xǁMemoryManagerǁstore__mutmut_2': xǁMemoryManagerǁstore__mutmut_2, 
        'xǁMemoryManagerǁstore__mutmut_3': xǁMemoryManagerǁstore__mutmut_3, 
        'xǁMemoryManagerǁstore__mutmut_4': xǁMemoryManagerǁstore__mutmut_4, 
        'xǁMemoryManagerǁstore__mutmut_5': xǁMemoryManagerǁstore__mutmut_5, 
        'xǁMemoryManagerǁstore__mutmut_6': xǁMemoryManagerǁstore__mutmut_6, 
        'xǁMemoryManagerǁstore__mutmut_7': xǁMemoryManagerǁstore__mutmut_7, 
        'xǁMemoryManagerǁstore__mutmut_8': xǁMemoryManagerǁstore__mutmut_8, 
        'xǁMemoryManagerǁstore__mutmut_9': xǁMemoryManagerǁstore__mutmut_9, 
        'xǁMemoryManagerǁstore__mutmut_10': xǁMemoryManagerǁstore__mutmut_10, 
        'xǁMemoryManagerǁstore__mutmut_11': xǁMemoryManagerǁstore__mutmut_11, 
        'xǁMemoryManagerǁstore__mutmut_12': xǁMemoryManagerǁstore__mutmut_12, 
        'xǁMemoryManagerǁstore__mutmut_13': xǁMemoryManagerǁstore__mutmut_13
    }
    
    def store(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁstore__mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁstore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store.__signature__ = _mutmut_signature(xǁMemoryManagerǁstore__mutmut_orig)
    xǁMemoryManagerǁstore__mutmut_orig.__name__ = 'xǁMemoryManagerǁstore'
    
    def xǁMemoryManagerǁrecall__mutmut_orig(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_1(
        self,
        query_text: Optional[str] = None,
        limit: int = 11,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_2(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = None
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_3(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=None,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_4(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=None,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_5(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=None,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_6(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=None,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_7(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_8(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_9(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_10(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_11(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id and self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_12(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_13(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = None
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_14(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(None)
        logger.debug(f"Recalled {len(results)} memories for query: {query_text}")
        return results
    
    def xǁMemoryManagerǁrecall__mutmut_15(
        self,
        query_text: Optional[str] = None,
        limit: int = 10,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> list[MemoryEntry]:
        """Retrieve memories matching the query.
        
        Args:
            query_text: Text to search for in memory content
            limit: Maximum number of results
            session_id: Filter by session ID (None = current session)
            agent_id: Filter by agent ID (None = current agent)
            
        Returns:
            list of matching memories, sorted by relevance
        """
        query = MemoryQuery(
            text=query_text,
            agent_id=agent_id or self.agent_id,
            session_id=session_id if session_id is not None else self.session_id,
            limit=limit,
        )
        
        results = self.backend.retrieve(query)
        logger.debug(None)
        return results
    
    xǁMemoryManagerǁrecall__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁrecall__mutmut_1': xǁMemoryManagerǁrecall__mutmut_1, 
        'xǁMemoryManagerǁrecall__mutmut_2': xǁMemoryManagerǁrecall__mutmut_2, 
        'xǁMemoryManagerǁrecall__mutmut_3': xǁMemoryManagerǁrecall__mutmut_3, 
        'xǁMemoryManagerǁrecall__mutmut_4': xǁMemoryManagerǁrecall__mutmut_4, 
        'xǁMemoryManagerǁrecall__mutmut_5': xǁMemoryManagerǁrecall__mutmut_5, 
        'xǁMemoryManagerǁrecall__mutmut_6': xǁMemoryManagerǁrecall__mutmut_6, 
        'xǁMemoryManagerǁrecall__mutmut_7': xǁMemoryManagerǁrecall__mutmut_7, 
        'xǁMemoryManagerǁrecall__mutmut_8': xǁMemoryManagerǁrecall__mutmut_8, 
        'xǁMemoryManagerǁrecall__mutmut_9': xǁMemoryManagerǁrecall__mutmut_9, 
        'xǁMemoryManagerǁrecall__mutmut_10': xǁMemoryManagerǁrecall__mutmut_10, 
        'xǁMemoryManagerǁrecall__mutmut_11': xǁMemoryManagerǁrecall__mutmut_11, 
        'xǁMemoryManagerǁrecall__mutmut_12': xǁMemoryManagerǁrecall__mutmut_12, 
        'xǁMemoryManagerǁrecall__mutmut_13': xǁMemoryManagerǁrecall__mutmut_13, 
        'xǁMemoryManagerǁrecall__mutmut_14': xǁMemoryManagerǁrecall__mutmut_14, 
        'xǁMemoryManagerǁrecall__mutmut_15': xǁMemoryManagerǁrecall__mutmut_15
    }
    
    def recall(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁrecall__mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁrecall__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recall.__signature__ = _mutmut_signature(xǁMemoryManagerǁrecall__mutmut_orig)
    xǁMemoryManagerǁrecall__mutmut_orig.__name__ = 'xǁMemoryManagerǁrecall'
    
    def xǁMemoryManagerǁrecall_all__mutmut_orig(self, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            list of all memories
        """
        return self.recall(query_text=None, limit=limit)
    
    def xǁMemoryManagerǁrecall_all__mutmut_1(self, limit: int = 101) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            list of all memories
        """
        return self.recall(query_text=None, limit=limit)
    
    def xǁMemoryManagerǁrecall_all__mutmut_2(self, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            list of all memories
        """
        return self.recall(query_text=None, limit=None)
    
    def xǁMemoryManagerǁrecall_all__mutmut_3(self, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            list of all memories
        """
        return self.recall(limit=limit)
    
    def xǁMemoryManagerǁrecall_all__mutmut_4(self, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve all memories for current agent/session.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            list of all memories
        """
        return self.recall(query_text=None, )
    
    xǁMemoryManagerǁrecall_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁrecall_all__mutmut_1': xǁMemoryManagerǁrecall_all__mutmut_1, 
        'xǁMemoryManagerǁrecall_all__mutmut_2': xǁMemoryManagerǁrecall_all__mutmut_2, 
        'xǁMemoryManagerǁrecall_all__mutmut_3': xǁMemoryManagerǁrecall_all__mutmut_3, 
        'xǁMemoryManagerǁrecall_all__mutmut_4': xǁMemoryManagerǁrecall_all__mutmut_4
    }
    
    def recall_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁrecall_all__mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁrecall_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    recall_all.__signature__ = _mutmut_signature(xǁMemoryManagerǁrecall_all__mutmut_orig)
    xǁMemoryManagerǁrecall_all__mutmut_orig.__name__ = 'xǁMemoryManagerǁrecall_all'
    
    def xǁMemoryManagerǁclear_session__mutmut_orig(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_1(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = None
        if not sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_2(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id and self.session_id
        if not sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_3(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_4(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError(None)
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_5(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("XXNo session_id specifiedXX")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_6(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("no session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_7(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("NO SESSION_ID SPECIFIED")
        
        count = self.backend.clear_session(sid)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_8(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session_id specified")
        
        count = None
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_9(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(None)
        logger.info(f"Cleared {count} memories from session {sid}")
        return count
    
    def xǁMemoryManagerǁclear_session__mutmut_10(self, session_id: Optional[str] = None) -> int:
        """Clear all memories for a session.
        
        Args:
            session_id: Session to clear (defaults to current session)
            
        Returns:
            Number of memories deleted
        """
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session_id specified")
        
        count = self.backend.clear_session(sid)
        logger.info(None)
        return count
    
    xǁMemoryManagerǁclear_session__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁclear_session__mutmut_1': xǁMemoryManagerǁclear_session__mutmut_1, 
        'xǁMemoryManagerǁclear_session__mutmut_2': xǁMemoryManagerǁclear_session__mutmut_2, 
        'xǁMemoryManagerǁclear_session__mutmut_3': xǁMemoryManagerǁclear_session__mutmut_3, 
        'xǁMemoryManagerǁclear_session__mutmut_4': xǁMemoryManagerǁclear_session__mutmut_4, 
        'xǁMemoryManagerǁclear_session__mutmut_5': xǁMemoryManagerǁclear_session__mutmut_5, 
        'xǁMemoryManagerǁclear_session__mutmut_6': xǁMemoryManagerǁclear_session__mutmut_6, 
        'xǁMemoryManagerǁclear_session__mutmut_7': xǁMemoryManagerǁclear_session__mutmut_7, 
        'xǁMemoryManagerǁclear_session__mutmut_8': xǁMemoryManagerǁclear_session__mutmut_8, 
        'xǁMemoryManagerǁclear_session__mutmut_9': xǁMemoryManagerǁclear_session__mutmut_9, 
        'xǁMemoryManagerǁclear_session__mutmut_10': xǁMemoryManagerǁclear_session__mutmut_10
    }
    
    def clear_session(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁclear_session__mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁclear_session__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_session.__signature__ = _mutmut_signature(xǁMemoryManagerǁclear_session__mutmut_orig)
    xǁMemoryManagerǁclear_session__mutmut_orig.__name__ = 'xǁMemoryManagerǁclear_session'
    
    def get_stats(self) -> dict[str, Any]:
        """Get memory storage statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.backend.get_stats()
    
    def xǁMemoryManagerǁset_session__mutmut_orig(self, session_id: str) -> None:
        """Change the current session ID.
        
        Args:
            session_id: New session ID
        """
        self.session_id = session_id
        logger.debug(f"Session changed to: {session_id}")
    
    def xǁMemoryManagerǁset_session__mutmut_1(self, session_id: str) -> None:
        """Change the current session ID.
        
        Args:
            session_id: New session ID
        """
        self.session_id = None
        logger.debug(f"Session changed to: {session_id}")
    
    def xǁMemoryManagerǁset_session__mutmut_2(self, session_id: str) -> None:
        """Change the current session ID.
        
        Args:
            session_id: New session ID
        """
        self.session_id = session_id
        logger.debug(None)
    
    xǁMemoryManagerǁset_session__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMemoryManagerǁset_session__mutmut_1': xǁMemoryManagerǁset_session__mutmut_1, 
        'xǁMemoryManagerǁset_session__mutmut_2': xǁMemoryManagerǁset_session__mutmut_2
    }
    
    def set_session(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMemoryManagerǁset_session__mutmut_orig"), object.__getattribute__(self, "xǁMemoryManagerǁset_session__mutmut_mutants"), args, kwargs, self)
        return result 
    
    set_session.__signature__ = _mutmut_signature(xǁMemoryManagerǁset_session__mutmut_orig)
    xǁMemoryManagerǁset_session__mutmut_orig.__name__ = 'xǁMemoryManagerǁset_session'
