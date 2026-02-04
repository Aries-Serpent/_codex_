"""File-based memory storage backends.

Provides JSONL and SQLite implementations of the MemoryProtocol.
"""

from __future__ import annotations

import fcntl
import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any
from uuid import UUID

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


class JSONLMemoryBackend(MemoryProtocol):
    """File-based memory storage using JSONL format.

    Simple, human-readable storage suitable for small to medium memory sets.
    Each line is a JSON object representing one memory entry.

    Args:
        storage_path: Path to the JSONL file
    """

    def xǁJSONLMemoryBackendǁ__init____mutmut_orig(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_1(self, storage_path: Path | str):
        self.storage_path = None
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_2(self, storage_path: Path | str):
        self.storage_path = Path(None)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_3(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=None, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_4(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=None)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_5(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_6(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, )

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_7(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=False, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_8(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=False)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_9(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_10(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = None
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_11(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                None,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_12(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                None,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_13(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                None
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_14(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_15(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_16(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_17(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT & os.O_WRONLY,
                0o600
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_18(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                385
            )
            os.close(fd)

    def xǁJSONLMemoryBackendǁ__init____mutmut_19(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure file exists with secure permissions
        if not self.storage_path.exists():
            # Create with owner-only permissions (0o600) for security
            fd = os.open(
                self.storage_path,
                os.O_CREAT | os.O_WRONLY,
                0o600
            )
            os.close(None)
    
    xǁJSONLMemoryBackendǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁ__init____mutmut_1': xǁJSONLMemoryBackendǁ__init____mutmut_1, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_2': xǁJSONLMemoryBackendǁ__init____mutmut_2, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_3': xǁJSONLMemoryBackendǁ__init____mutmut_3, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_4': xǁJSONLMemoryBackendǁ__init____mutmut_4, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_5': xǁJSONLMemoryBackendǁ__init____mutmut_5, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_6': xǁJSONLMemoryBackendǁ__init____mutmut_6, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_7': xǁJSONLMemoryBackendǁ__init____mutmut_7, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_8': xǁJSONLMemoryBackendǁ__init____mutmut_8, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_9': xǁJSONLMemoryBackendǁ__init____mutmut_9, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_10': xǁJSONLMemoryBackendǁ__init____mutmut_10, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_11': xǁJSONLMemoryBackendǁ__init____mutmut_11, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_12': xǁJSONLMemoryBackendǁ__init____mutmut_12, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_13': xǁJSONLMemoryBackendǁ__init____mutmut_13, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_14': xǁJSONLMemoryBackendǁ__init____mutmut_14, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_15': xǁJSONLMemoryBackendǁ__init____mutmut_15, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_16': xǁJSONLMemoryBackendǁ__init____mutmut_16, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_17': xǁJSONLMemoryBackendǁ__init____mutmut_17, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_18': xǁJSONLMemoryBackendǁ__init____mutmut_18, 
        'xǁJSONLMemoryBackendǁ__init____mutmut_19': xǁJSONLMemoryBackendǁ__init____mutmut_19
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁ__init____mutmut_orig)
    xǁJSONLMemoryBackendǁ__init____mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁ__init__'

    def xǁJSONLMemoryBackendǁstore__mutmut_orig(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_1(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(None, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_2(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, None, encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_3(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding=None) as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_4(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open("a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_5(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_6(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", ) as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_7(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "XXaXX", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_8(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "A", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_9(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="XXutf-8XX") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_10(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="UTF-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_11(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(None, fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_12(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), None)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_13(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_14(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), )
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_15(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(None)
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_16(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) - "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_17(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(None) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_18(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "XX\nXX")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_19(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(None, fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_20(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), None)

    def xǁJSONLMemoryBackendǁstore__mutmut_21(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(fcntl.LOCK_UN)

    def xǁJSONLMemoryBackendǁstore__mutmut_22(self, entry: MemoryEntry) -> None:
        """Append entry to JSONL file with file locking."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry.to_dict()) + "\n")
                f.flush()
            finally:
                fcntl.flock(f.fileno(), )
    
    xǁJSONLMemoryBackendǁstore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁstore__mutmut_1': xǁJSONLMemoryBackendǁstore__mutmut_1, 
        'xǁJSONLMemoryBackendǁstore__mutmut_2': xǁJSONLMemoryBackendǁstore__mutmut_2, 
        'xǁJSONLMemoryBackendǁstore__mutmut_3': xǁJSONLMemoryBackendǁstore__mutmut_3, 
        'xǁJSONLMemoryBackendǁstore__mutmut_4': xǁJSONLMemoryBackendǁstore__mutmut_4, 
        'xǁJSONLMemoryBackendǁstore__mutmut_5': xǁJSONLMemoryBackendǁstore__mutmut_5, 
        'xǁJSONLMemoryBackendǁstore__mutmut_6': xǁJSONLMemoryBackendǁstore__mutmut_6, 
        'xǁJSONLMemoryBackendǁstore__mutmut_7': xǁJSONLMemoryBackendǁstore__mutmut_7, 
        'xǁJSONLMemoryBackendǁstore__mutmut_8': xǁJSONLMemoryBackendǁstore__mutmut_8, 
        'xǁJSONLMemoryBackendǁstore__mutmut_9': xǁJSONLMemoryBackendǁstore__mutmut_9, 
        'xǁJSONLMemoryBackendǁstore__mutmut_10': xǁJSONLMemoryBackendǁstore__mutmut_10, 
        'xǁJSONLMemoryBackendǁstore__mutmut_11': xǁJSONLMemoryBackendǁstore__mutmut_11, 
        'xǁJSONLMemoryBackendǁstore__mutmut_12': xǁJSONLMemoryBackendǁstore__mutmut_12, 
        'xǁJSONLMemoryBackendǁstore__mutmut_13': xǁJSONLMemoryBackendǁstore__mutmut_13, 
        'xǁJSONLMemoryBackendǁstore__mutmut_14': xǁJSONLMemoryBackendǁstore__mutmut_14, 
        'xǁJSONLMemoryBackendǁstore__mutmut_15': xǁJSONLMemoryBackendǁstore__mutmut_15, 
        'xǁJSONLMemoryBackendǁstore__mutmut_16': xǁJSONLMemoryBackendǁstore__mutmut_16, 
        'xǁJSONLMemoryBackendǁstore__mutmut_17': xǁJSONLMemoryBackendǁstore__mutmut_17, 
        'xǁJSONLMemoryBackendǁstore__mutmut_18': xǁJSONLMemoryBackendǁstore__mutmut_18, 
        'xǁJSONLMemoryBackendǁstore__mutmut_19': xǁJSONLMemoryBackendǁstore__mutmut_19, 
        'xǁJSONLMemoryBackendǁstore__mutmut_20': xǁJSONLMemoryBackendǁstore__mutmut_20, 
        'xǁJSONLMemoryBackendǁstore__mutmut_21': xǁJSONLMemoryBackendǁstore__mutmut_21, 
        'xǁJSONLMemoryBackendǁstore__mutmut_22': xǁJSONLMemoryBackendǁstore__mutmut_22
    }
    
    def store(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁstore__mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁstore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁstore__mutmut_orig)
    xǁJSONLMemoryBackendǁstore__mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁstore'

    def xǁJSONLMemoryBackendǁretrieve__mutmut_orig(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_1(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_2(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = None
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_3(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(None, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_4(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, None, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_5(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding=None) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_6(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_7(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_8(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", ) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_9(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "XXrXX", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_10(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "R", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_11(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="XXutf-8XX") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_12(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="UTF-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_13(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_14(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    break
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_15(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = None
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_16(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(None)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_17(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = None

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_18(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(None)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_19(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id or entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_20(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id == query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_21(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        break
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_22(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id or entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_23(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id == query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_24(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        break
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_25(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since or entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_26(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp <= query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_27(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        break

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_28(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = None
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_29(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).upper()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_30(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(None).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_31(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.upper() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_32(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_33(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            break

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_34(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(None)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_35(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(None)
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_36(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(None)
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_37(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    break

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_38(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=None, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_39(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=None)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_40(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_41(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, )
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_42(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: None, reverse=True)
        return matches[:query.limit]

    def xǁJSONLMemoryBackendǁretrieve__mutmut_43(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries by scanning the entire file.

        Note: This is O(n) and suitable for smaller datasets.
        For large-scale use, consider SQLite or vector DB backend.
        """
        if not self.storage_path.exists():
            return []

        matches = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)

                    # Apply filters
                    if query.agent_id and entry.agent_id != query.agent_id:
                        continue
                    if query.session_id and entry.session_id != query.session_id:
                        continue
                    if query.since and entry.timestamp < query.since:
                        continue

                    # Basic text search (case-insensitive substring match)
                    if query.text:
                        content_str = str(entry.content).lower()
                        if query.text.lower() not in content_str:
                            continue

                    matches.append(entry)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.debug(f"Exception: {e}")
                    logger.warning(f"Skipping invalid memory entry: {e}")
                    continue

        # Sort by timestamp descending and limit
        matches.sort(key=lambda x: x.timestamp, reverse=False)
        return matches[:query.limit]
    
    xǁJSONLMemoryBackendǁretrieve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁretrieve__mutmut_1': xǁJSONLMemoryBackendǁretrieve__mutmut_1, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_2': xǁJSONLMemoryBackendǁretrieve__mutmut_2, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_3': xǁJSONLMemoryBackendǁretrieve__mutmut_3, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_4': xǁJSONLMemoryBackendǁretrieve__mutmut_4, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_5': xǁJSONLMemoryBackendǁretrieve__mutmut_5, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_6': xǁJSONLMemoryBackendǁretrieve__mutmut_6, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_7': xǁJSONLMemoryBackendǁretrieve__mutmut_7, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_8': xǁJSONLMemoryBackendǁretrieve__mutmut_8, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_9': xǁJSONLMemoryBackendǁretrieve__mutmut_9, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_10': xǁJSONLMemoryBackendǁretrieve__mutmut_10, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_11': xǁJSONLMemoryBackendǁretrieve__mutmut_11, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_12': xǁJSONLMemoryBackendǁretrieve__mutmut_12, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_13': xǁJSONLMemoryBackendǁretrieve__mutmut_13, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_14': xǁJSONLMemoryBackendǁretrieve__mutmut_14, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_15': xǁJSONLMemoryBackendǁretrieve__mutmut_15, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_16': xǁJSONLMemoryBackendǁretrieve__mutmut_16, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_17': xǁJSONLMemoryBackendǁretrieve__mutmut_17, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_18': xǁJSONLMemoryBackendǁretrieve__mutmut_18, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_19': xǁJSONLMemoryBackendǁretrieve__mutmut_19, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_20': xǁJSONLMemoryBackendǁretrieve__mutmut_20, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_21': xǁJSONLMemoryBackendǁretrieve__mutmut_21, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_22': xǁJSONLMemoryBackendǁretrieve__mutmut_22, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_23': xǁJSONLMemoryBackendǁretrieve__mutmut_23, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_24': xǁJSONLMemoryBackendǁretrieve__mutmut_24, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_25': xǁJSONLMemoryBackendǁretrieve__mutmut_25, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_26': xǁJSONLMemoryBackendǁretrieve__mutmut_26, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_27': xǁJSONLMemoryBackendǁretrieve__mutmut_27, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_28': xǁJSONLMemoryBackendǁretrieve__mutmut_28, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_29': xǁJSONLMemoryBackendǁretrieve__mutmut_29, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_30': xǁJSONLMemoryBackendǁretrieve__mutmut_30, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_31': xǁJSONLMemoryBackendǁretrieve__mutmut_31, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_32': xǁJSONLMemoryBackendǁretrieve__mutmut_32, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_33': xǁJSONLMemoryBackendǁretrieve__mutmut_33, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_34': xǁJSONLMemoryBackendǁretrieve__mutmut_34, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_35': xǁJSONLMemoryBackendǁretrieve__mutmut_35, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_36': xǁJSONLMemoryBackendǁretrieve__mutmut_36, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_37': xǁJSONLMemoryBackendǁretrieve__mutmut_37, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_38': xǁJSONLMemoryBackendǁretrieve__mutmut_38, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_39': xǁJSONLMemoryBackendǁretrieve__mutmut_39, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_40': xǁJSONLMemoryBackendǁretrieve__mutmut_40, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_41': xǁJSONLMemoryBackendǁretrieve__mutmut_41, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_42': xǁJSONLMemoryBackendǁretrieve__mutmut_42, 
        'xǁJSONLMemoryBackendǁretrieve__mutmut_43': xǁJSONLMemoryBackendǁretrieve__mutmut_43
    }
    
    def retrieve(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁretrieve__mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁretrieve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    retrieve.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁretrieve__mutmut_orig)
    xǁJSONLMemoryBackendǁretrieve__mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁretrieve'

    def xǁJSONLMemoryBackendǁdelete__mutmut_orig(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_1(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_2(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return True

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_3(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = None
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_4(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = None
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_5(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = True
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_6(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(None, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_7(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, None, encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_8(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding=None) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_9(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open("r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_10(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_11(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", ) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_12(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "XXrXX", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_13(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "R", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_14(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="XXutf-8XX") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_15(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="UTF-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_16(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(None, fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_17(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), None)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_18(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_19(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), )
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_20(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_21(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        break
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_22(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = None
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_23(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(None)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_24(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(None) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_25(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["XXidXX"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_26(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["ID"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_27(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) != entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_28(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = None
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_29(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = False
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_30(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            break
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_31(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(None)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_32(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(None)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_33(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(None, fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_34(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), None)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_35(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_36(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), )
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_37(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(None, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_38(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, None, encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_39(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding=None) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_40(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open("w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_41(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_42(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", ) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_43(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "XXwXX", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_44(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "W", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_45(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="XXutf-8XX") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_46(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="UTF-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_47(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(None, fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_48(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), None)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_49(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_50(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), )
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_51(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(None)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_52(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(None, fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_53(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), None)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_54(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(fcntl.LOCK_UN)
        
        return found

    def xǁJSONLMemoryBackendǁdelete__mutmut_55(self, entry_id: UUID) -> bool:
        """Delete entry by rewriting file without it (with file locking)."""
        if not self.storage_path.exists():
            return False

        entries = []
        found = False
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if UUID(data["id"]) == entry_id:
                            found = True
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if found
        if found:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), )
        
        return found
    
    xǁJSONLMemoryBackendǁdelete__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁdelete__mutmut_1': xǁJSONLMemoryBackendǁdelete__mutmut_1, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_2': xǁJSONLMemoryBackendǁdelete__mutmut_2, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_3': xǁJSONLMemoryBackendǁdelete__mutmut_3, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_4': xǁJSONLMemoryBackendǁdelete__mutmut_4, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_5': xǁJSONLMemoryBackendǁdelete__mutmut_5, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_6': xǁJSONLMemoryBackendǁdelete__mutmut_6, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_7': xǁJSONLMemoryBackendǁdelete__mutmut_7, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_8': xǁJSONLMemoryBackendǁdelete__mutmut_8, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_9': xǁJSONLMemoryBackendǁdelete__mutmut_9, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_10': xǁJSONLMemoryBackendǁdelete__mutmut_10, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_11': xǁJSONLMemoryBackendǁdelete__mutmut_11, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_12': xǁJSONLMemoryBackendǁdelete__mutmut_12, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_13': xǁJSONLMemoryBackendǁdelete__mutmut_13, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_14': xǁJSONLMemoryBackendǁdelete__mutmut_14, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_15': xǁJSONLMemoryBackendǁdelete__mutmut_15, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_16': xǁJSONLMemoryBackendǁdelete__mutmut_16, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_17': xǁJSONLMemoryBackendǁdelete__mutmut_17, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_18': xǁJSONLMemoryBackendǁdelete__mutmut_18, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_19': xǁJSONLMemoryBackendǁdelete__mutmut_19, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_20': xǁJSONLMemoryBackendǁdelete__mutmut_20, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_21': xǁJSONLMemoryBackendǁdelete__mutmut_21, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_22': xǁJSONLMemoryBackendǁdelete__mutmut_22, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_23': xǁJSONLMemoryBackendǁdelete__mutmut_23, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_24': xǁJSONLMemoryBackendǁdelete__mutmut_24, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_25': xǁJSONLMemoryBackendǁdelete__mutmut_25, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_26': xǁJSONLMemoryBackendǁdelete__mutmut_26, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_27': xǁJSONLMemoryBackendǁdelete__mutmut_27, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_28': xǁJSONLMemoryBackendǁdelete__mutmut_28, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_29': xǁJSONLMemoryBackendǁdelete__mutmut_29, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_30': xǁJSONLMemoryBackendǁdelete__mutmut_30, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_31': xǁJSONLMemoryBackendǁdelete__mutmut_31, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_32': xǁJSONLMemoryBackendǁdelete__mutmut_32, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_33': xǁJSONLMemoryBackendǁdelete__mutmut_33, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_34': xǁJSONLMemoryBackendǁdelete__mutmut_34, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_35': xǁJSONLMemoryBackendǁdelete__mutmut_35, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_36': xǁJSONLMemoryBackendǁdelete__mutmut_36, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_37': xǁJSONLMemoryBackendǁdelete__mutmut_37, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_38': xǁJSONLMemoryBackendǁdelete__mutmut_38, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_39': xǁJSONLMemoryBackendǁdelete__mutmut_39, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_40': xǁJSONLMemoryBackendǁdelete__mutmut_40, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_41': xǁJSONLMemoryBackendǁdelete__mutmut_41, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_42': xǁJSONLMemoryBackendǁdelete__mutmut_42, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_43': xǁJSONLMemoryBackendǁdelete__mutmut_43, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_44': xǁJSONLMemoryBackendǁdelete__mutmut_44, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_45': xǁJSONLMemoryBackendǁdelete__mutmut_45, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_46': xǁJSONLMemoryBackendǁdelete__mutmut_46, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_47': xǁJSONLMemoryBackendǁdelete__mutmut_47, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_48': xǁJSONLMemoryBackendǁdelete__mutmut_48, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_49': xǁJSONLMemoryBackendǁdelete__mutmut_49, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_50': xǁJSONLMemoryBackendǁdelete__mutmut_50, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_51': xǁJSONLMemoryBackendǁdelete__mutmut_51, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_52': xǁJSONLMemoryBackendǁdelete__mutmut_52, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_53': xǁJSONLMemoryBackendǁdelete__mutmut_53, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_54': xǁJSONLMemoryBackendǁdelete__mutmut_54, 
        'xǁJSONLMemoryBackendǁdelete__mutmut_55': xǁJSONLMemoryBackendǁdelete__mutmut_55
    }
    
    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁdelete__mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁdelete__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁdelete__mutmut_orig)
    xǁJSONLMemoryBackendǁdelete__mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁdelete'
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_orig(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_1(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_2(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 1
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_3(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = None
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_4(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = None
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_5(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 1
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_6(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(None, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_7(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, None, encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_8(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding=None) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_9(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open("r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_10(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_11(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", ) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_12(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "XXrXX", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_13(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "R", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_14(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="XXutf-8XX") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_15(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="UTF-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_16(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(None, fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_17(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), None)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_18(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_19(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), )
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_20(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_21(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        break
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_22(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = None
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_23(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(None)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_24(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get(None) == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_25(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("XXsession_idXX") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_26(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("SESSION_ID") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_27(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") != session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_28(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count = 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_29(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count -= 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_30(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 2
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_31(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            break
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_32(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(None)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_33(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(None)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_34(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(None, fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_35(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), None)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_36(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_37(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), )
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_38(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count >= 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_39(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 1:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_40(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(None, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_41(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, None, encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_42(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding=None) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_43(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open("w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_44(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_45(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", ) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_46(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "XXwXX", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_47(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "W", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_48(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="XXutf-8XX") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_49(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="UTF-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_50(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(None, fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_51(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), None)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_52(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_53(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), )
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_54(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(None)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_55(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(None, fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_56(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), None)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_57(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(fcntl.LOCK_UN)
        
        return deleted_count
    
    def xǁJSONLMemoryBackendǁclear_session__mutmut_58(self, session_id: str) -> int:
        """Remove all entries for a session (with file locking)."""
        if not self.storage_path.exists():
            return 0
        
        entries = []
        deleted_count = 0
        
        # Read with shared lock
        with open(self.storage_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == session_id:
                            deleted_count += 1
                            continue
                        entries.append(line)
                    except (json.JSONDecodeError, KeyError):
                        entries.append(line)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Write with exclusive lock if any deleted
        if deleted_count > 0:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.writelines(entries)
                    f.flush()
                finally:
                    fcntl.flock(f.fileno(), )
        
        return deleted_count
    
    xǁJSONLMemoryBackendǁclear_session__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁclear_session__mutmut_1': xǁJSONLMemoryBackendǁclear_session__mutmut_1, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_2': xǁJSONLMemoryBackendǁclear_session__mutmut_2, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_3': xǁJSONLMemoryBackendǁclear_session__mutmut_3, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_4': xǁJSONLMemoryBackendǁclear_session__mutmut_4, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_5': xǁJSONLMemoryBackendǁclear_session__mutmut_5, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_6': xǁJSONLMemoryBackendǁclear_session__mutmut_6, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_7': xǁJSONLMemoryBackendǁclear_session__mutmut_7, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_8': xǁJSONLMemoryBackendǁclear_session__mutmut_8, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_9': xǁJSONLMemoryBackendǁclear_session__mutmut_9, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_10': xǁJSONLMemoryBackendǁclear_session__mutmut_10, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_11': xǁJSONLMemoryBackendǁclear_session__mutmut_11, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_12': xǁJSONLMemoryBackendǁclear_session__mutmut_12, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_13': xǁJSONLMemoryBackendǁclear_session__mutmut_13, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_14': xǁJSONLMemoryBackendǁclear_session__mutmut_14, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_15': xǁJSONLMemoryBackendǁclear_session__mutmut_15, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_16': xǁJSONLMemoryBackendǁclear_session__mutmut_16, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_17': xǁJSONLMemoryBackendǁclear_session__mutmut_17, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_18': xǁJSONLMemoryBackendǁclear_session__mutmut_18, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_19': xǁJSONLMemoryBackendǁclear_session__mutmut_19, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_20': xǁJSONLMemoryBackendǁclear_session__mutmut_20, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_21': xǁJSONLMemoryBackendǁclear_session__mutmut_21, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_22': xǁJSONLMemoryBackendǁclear_session__mutmut_22, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_23': xǁJSONLMemoryBackendǁclear_session__mutmut_23, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_24': xǁJSONLMemoryBackendǁclear_session__mutmut_24, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_25': xǁJSONLMemoryBackendǁclear_session__mutmut_25, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_26': xǁJSONLMemoryBackendǁclear_session__mutmut_26, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_27': xǁJSONLMemoryBackendǁclear_session__mutmut_27, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_28': xǁJSONLMemoryBackendǁclear_session__mutmut_28, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_29': xǁJSONLMemoryBackendǁclear_session__mutmut_29, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_30': xǁJSONLMemoryBackendǁclear_session__mutmut_30, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_31': xǁJSONLMemoryBackendǁclear_session__mutmut_31, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_32': xǁJSONLMemoryBackendǁclear_session__mutmut_32, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_33': xǁJSONLMemoryBackendǁclear_session__mutmut_33, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_34': xǁJSONLMemoryBackendǁclear_session__mutmut_34, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_35': xǁJSONLMemoryBackendǁclear_session__mutmut_35, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_36': xǁJSONLMemoryBackendǁclear_session__mutmut_36, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_37': xǁJSONLMemoryBackendǁclear_session__mutmut_37, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_38': xǁJSONLMemoryBackendǁclear_session__mutmut_38, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_39': xǁJSONLMemoryBackendǁclear_session__mutmut_39, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_40': xǁJSONLMemoryBackendǁclear_session__mutmut_40, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_41': xǁJSONLMemoryBackendǁclear_session__mutmut_41, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_42': xǁJSONLMemoryBackendǁclear_session__mutmut_42, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_43': xǁJSONLMemoryBackendǁclear_session__mutmut_43, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_44': xǁJSONLMemoryBackendǁclear_session__mutmut_44, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_45': xǁJSONLMemoryBackendǁclear_session__mutmut_45, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_46': xǁJSONLMemoryBackendǁclear_session__mutmut_46, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_47': xǁJSONLMemoryBackendǁclear_session__mutmut_47, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_48': xǁJSONLMemoryBackendǁclear_session__mutmut_48, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_49': xǁJSONLMemoryBackendǁclear_session__mutmut_49, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_50': xǁJSONLMemoryBackendǁclear_session__mutmut_50, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_51': xǁJSONLMemoryBackendǁclear_session__mutmut_51, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_52': xǁJSONLMemoryBackendǁclear_session__mutmut_52, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_53': xǁJSONLMemoryBackendǁclear_session__mutmut_53, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_54': xǁJSONLMemoryBackendǁclear_session__mutmut_54, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_55': xǁJSONLMemoryBackendǁclear_session__mutmut_55, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_56': xǁJSONLMemoryBackendǁclear_session__mutmut_56, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_57': xǁJSONLMemoryBackendǁclear_session__mutmut_57, 
        'xǁJSONLMemoryBackendǁclear_session__mutmut_58': xǁJSONLMemoryBackendǁclear_session__mutmut_58
    }
    
    def clear_session(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁclear_session__mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁclear_session__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_session.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁclear_session__mutmut_orig)
    xǁJSONLMemoryBackendǁclear_session__mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁclear_session'
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_orig(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_1(self) -> dict[str, Any]:
        """Get storage statistics."""
        if self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_2(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"XXentry_countXX": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_3(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"ENTRY_COUNT": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_4(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 1, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_5(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "XXsize_bytesXX": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_6(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "SIZE_BYTES": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_7(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 1}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_8(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = None
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_9(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 1
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_10(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(None, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_11(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, None, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_12(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding=None) as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_13(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_14(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_15(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", ) as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_16(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "XXrXX", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_17(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "R", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_18(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="XXutf-8XX") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_19(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="UTF-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_20(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count = 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_21(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count -= 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_22(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 2
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_23(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "XXentry_countXX": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_24(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "ENTRY_COUNT": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_25(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "XXsize_bytesXX": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_26(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "SIZE_BYTES": self.storage_path.stat().st_size,
            "backend": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_27(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "XXbackendXX": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_28(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "BACKEND": "jsonl",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_29(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "XXjsonlXX",
        }
    
    def xǁJSONLMemoryBackendǁget_stats__mutmut_30(self) -> dict[str, Any]:
        """Get storage statistics."""
        if not self.storage_path.exists():
            return {"entry_count": 0, "size_bytes": 0}
        
        entry_count = 0
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_count += 1
        
        return {
            "entry_count": entry_count,
            "size_bytes": self.storage_path.stat().st_size,
            "backend": "JSONL",
        }
    
    xǁJSONLMemoryBackendǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJSONLMemoryBackendǁget_stats__mutmut_1': xǁJSONLMemoryBackendǁget_stats__mutmut_1, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_2': xǁJSONLMemoryBackendǁget_stats__mutmut_2, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_3': xǁJSONLMemoryBackendǁget_stats__mutmut_3, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_4': xǁJSONLMemoryBackendǁget_stats__mutmut_4, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_5': xǁJSONLMemoryBackendǁget_stats__mutmut_5, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_6': xǁJSONLMemoryBackendǁget_stats__mutmut_6, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_7': xǁJSONLMemoryBackendǁget_stats__mutmut_7, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_8': xǁJSONLMemoryBackendǁget_stats__mutmut_8, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_9': xǁJSONLMemoryBackendǁget_stats__mutmut_9, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_10': xǁJSONLMemoryBackendǁget_stats__mutmut_10, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_11': xǁJSONLMemoryBackendǁget_stats__mutmut_11, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_12': xǁJSONLMemoryBackendǁget_stats__mutmut_12, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_13': xǁJSONLMemoryBackendǁget_stats__mutmut_13, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_14': xǁJSONLMemoryBackendǁget_stats__mutmut_14, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_15': xǁJSONLMemoryBackendǁget_stats__mutmut_15, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_16': xǁJSONLMemoryBackendǁget_stats__mutmut_16, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_17': xǁJSONLMemoryBackendǁget_stats__mutmut_17, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_18': xǁJSONLMemoryBackendǁget_stats__mutmut_18, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_19': xǁJSONLMemoryBackendǁget_stats__mutmut_19, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_20': xǁJSONLMemoryBackendǁget_stats__mutmut_20, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_21': xǁJSONLMemoryBackendǁget_stats__mutmut_21, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_22': xǁJSONLMemoryBackendǁget_stats__mutmut_22, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_23': xǁJSONLMemoryBackendǁget_stats__mutmut_23, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_24': xǁJSONLMemoryBackendǁget_stats__mutmut_24, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_25': xǁJSONLMemoryBackendǁget_stats__mutmut_25, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_26': xǁJSONLMemoryBackendǁget_stats__mutmut_26, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_27': xǁJSONLMemoryBackendǁget_stats__mutmut_27, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_28': xǁJSONLMemoryBackendǁget_stats__mutmut_28, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_29': xǁJSONLMemoryBackendǁget_stats__mutmut_29, 
        'xǁJSONLMemoryBackendǁget_stats__mutmut_30': xǁJSONLMemoryBackendǁget_stats__mutmut_30
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJSONLMemoryBackendǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁJSONLMemoryBackendǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁJSONLMemoryBackendǁget_stats__mutmut_orig)
    xǁJSONLMemoryBackendǁget_stats__mutmut_orig.__name__ = 'xǁJSONLMemoryBackendǁget_stats'


class SQLiteMemoryBackend(MemoryProtocol):
    """SQLite-based memory storage for better query performance.
    
    Provides indexed queries and better scalability than JSONL.
    Suitable for production use with thousands of memories.
    
    Args:
        db_path: Path to the SQLite database file
    """
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_orig(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_1(self, db_path: Path | str):
        self.db_path = None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_2(self, db_path: Path | str):
        self.db_path = Path(None)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_3(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=None, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_4(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=None)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_5(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_6(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, )
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_7(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=False, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_8(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=False)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_9(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_10(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = None
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_11(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(None, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_12(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, None, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_13(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, None)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_14(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_15(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_16(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, )
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_17(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT & os.O_WRONLY, 0o600)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_18(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 385)
            os.close(fd)
        
        self._init_db()
    
    def xǁSQLiteMemoryBackendǁ__init____mutmut_19(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database with secure permissions
        if not self.db_path.exists():
            # Create file with owner-only permissions (0o600)
            fd = os.open(self.db_path, os.O_CREAT | os.O_WRONLY, 0o600)
            os.close(None)
        
        self._init_db()
    
    xǁSQLiteMemoryBackendǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁ__init____mutmut_1': xǁSQLiteMemoryBackendǁ__init____mutmut_1, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_2': xǁSQLiteMemoryBackendǁ__init____mutmut_2, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_3': xǁSQLiteMemoryBackendǁ__init____mutmut_3, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_4': xǁSQLiteMemoryBackendǁ__init____mutmut_4, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_5': xǁSQLiteMemoryBackendǁ__init____mutmut_5, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_6': xǁSQLiteMemoryBackendǁ__init____mutmut_6, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_7': xǁSQLiteMemoryBackendǁ__init____mutmut_7, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_8': xǁSQLiteMemoryBackendǁ__init____mutmut_8, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_9': xǁSQLiteMemoryBackendǁ__init____mutmut_9, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_10': xǁSQLiteMemoryBackendǁ__init____mutmut_10, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_11': xǁSQLiteMemoryBackendǁ__init____mutmut_11, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_12': xǁSQLiteMemoryBackendǁ__init____mutmut_12, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_13': xǁSQLiteMemoryBackendǁ__init____mutmut_13, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_14': xǁSQLiteMemoryBackendǁ__init____mutmut_14, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_15': xǁSQLiteMemoryBackendǁ__init____mutmut_15, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_16': xǁSQLiteMemoryBackendǁ__init____mutmut_16, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_17': xǁSQLiteMemoryBackendǁ__init____mutmut_17, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_18': xǁSQLiteMemoryBackendǁ__init____mutmut_18, 
        'xǁSQLiteMemoryBackendǁ__init____mutmut_19': xǁSQLiteMemoryBackendǁ__init____mutmut_19
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁ__init____mutmut_orig)
    xǁSQLiteMemoryBackendǁ__init____mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁ__init__'
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_orig(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_1(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(None) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_2(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(None)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_3(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute(None)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_4(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("XXCREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)XX")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_5(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("create index if not exists idx_agent_id on memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_6(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS IDX_AGENT_ID ON MEMORIES(AGENT_ID)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_7(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute(None)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_8(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("XXCREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)XX")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_9(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("create index if not exists idx_session_id on memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_10(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS IDX_SESSION_ID ON MEMORIES(SESSION_ID)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_11(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute(None)
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_12(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("XXCREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)XX")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_13(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("create index if not exists idx_timestamp on memories(timestamp)")
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁ_init_db__mutmut_14(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT,
                    session_id TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memories(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS IDX_TIMESTAMP ON MEMORIES(TIMESTAMP)")
            conn.commit()
    
    xǁSQLiteMemoryBackendǁ_init_db__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁ_init_db__mutmut_1': xǁSQLiteMemoryBackendǁ_init_db__mutmut_1, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_2': xǁSQLiteMemoryBackendǁ_init_db__mutmut_2, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_3': xǁSQLiteMemoryBackendǁ_init_db__mutmut_3, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_4': xǁSQLiteMemoryBackendǁ_init_db__mutmut_4, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_5': xǁSQLiteMemoryBackendǁ_init_db__mutmut_5, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_6': xǁSQLiteMemoryBackendǁ_init_db__mutmut_6, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_7': xǁSQLiteMemoryBackendǁ_init_db__mutmut_7, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_8': xǁSQLiteMemoryBackendǁ_init_db__mutmut_8, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_9': xǁSQLiteMemoryBackendǁ_init_db__mutmut_9, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_10': xǁSQLiteMemoryBackendǁ_init_db__mutmut_10, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_11': xǁSQLiteMemoryBackendǁ_init_db__mutmut_11, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_12': xǁSQLiteMemoryBackendǁ_init_db__mutmut_12, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_13': xǁSQLiteMemoryBackendǁ_init_db__mutmut_13, 
        'xǁSQLiteMemoryBackendǁ_init_db__mutmut_14': xǁSQLiteMemoryBackendǁ_init_db__mutmut_14
    }
    
    def _init_db(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁ_init_db__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁ_init_db__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _init_db.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁ_init_db__mutmut_orig)
    xǁSQLiteMemoryBackendǁ_init_db__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁ_init_db'
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_orig(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_1(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(None) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_2(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = None
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_3(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = None
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_4(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["XXtimestampXX"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_5(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["TIMESTAMP"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_6(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') or not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_7(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_8(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith(None) and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_9(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('XX+00:00XX') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_10(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_11(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith(None):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_12(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('XXZXX'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_13(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_14(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = None
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_15(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(None)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_16(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_17(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = None
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_18(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=None)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_19(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = None
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_20(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                None,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_21(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                None,
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_22(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_23(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_24(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["XXidXX"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_25(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["ID"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_26(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(None),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_27(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["XXcontentXX"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_28(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["CONTENT"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_29(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get(None),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_30(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("XXagent_idXX"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_31(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("AGENT_ID"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_32(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get(None),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_33(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("XXsession_idXX"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_34(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("SESSION_ID"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_35(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(None),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_36(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get(None, {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_37(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", None)),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_38(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get({})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_39(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", )),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_40(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("XXmetadataXX", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_41(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("METADATA", {})),
                    json.dumps(data.get("embedding")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_42(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(None) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_43(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get(None)) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_44(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("XXembeddingXX")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_45(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("EMBEDDING")) if data.get("embedding") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_46(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get(None) else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_47(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("XXembeddingXX") else None,
                ),
            )
            conn.commit()
    
    def xǁSQLiteMemoryBackendǁstore__mutmut_48(self, entry: MemoryEntry) -> None:
        """Store entry in SQLite with timezone-aware timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            data = entry.to_dict()
            # Ensure timestamp is timezone-aware (UTC)
            timestamp_str = data["timestamp"]
            if not timestamp_str.endswith('+00:00') and not timestamp_str.endswith('Z'):
                # Add UTC timezone if missing
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(timestamp_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamp_str = dt.isoformat()
            
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (id, content, timestamp, agent_id, session_id, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"],
                    json.dumps(data["content"]),
                    timestamp_str,
                    data.get("agent_id"),
                    data.get("session_id"),
                    json.dumps(data.get("metadata", {})),
                    json.dumps(data.get("embedding")) if data.get("EMBEDDING") else None,
                ),
            )
            conn.commit()
    
    xǁSQLiteMemoryBackendǁstore__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁstore__mutmut_1': xǁSQLiteMemoryBackendǁstore__mutmut_1, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_2': xǁSQLiteMemoryBackendǁstore__mutmut_2, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_3': xǁSQLiteMemoryBackendǁstore__mutmut_3, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_4': xǁSQLiteMemoryBackendǁstore__mutmut_4, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_5': xǁSQLiteMemoryBackendǁstore__mutmut_5, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_6': xǁSQLiteMemoryBackendǁstore__mutmut_6, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_7': xǁSQLiteMemoryBackendǁstore__mutmut_7, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_8': xǁSQLiteMemoryBackendǁstore__mutmut_8, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_9': xǁSQLiteMemoryBackendǁstore__mutmut_9, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_10': xǁSQLiteMemoryBackendǁstore__mutmut_10, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_11': xǁSQLiteMemoryBackendǁstore__mutmut_11, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_12': xǁSQLiteMemoryBackendǁstore__mutmut_12, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_13': xǁSQLiteMemoryBackendǁstore__mutmut_13, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_14': xǁSQLiteMemoryBackendǁstore__mutmut_14, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_15': xǁSQLiteMemoryBackendǁstore__mutmut_15, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_16': xǁSQLiteMemoryBackendǁstore__mutmut_16, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_17': xǁSQLiteMemoryBackendǁstore__mutmut_17, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_18': xǁSQLiteMemoryBackendǁstore__mutmut_18, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_19': xǁSQLiteMemoryBackendǁstore__mutmut_19, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_20': xǁSQLiteMemoryBackendǁstore__mutmut_20, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_21': xǁSQLiteMemoryBackendǁstore__mutmut_21, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_22': xǁSQLiteMemoryBackendǁstore__mutmut_22, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_23': xǁSQLiteMemoryBackendǁstore__mutmut_23, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_24': xǁSQLiteMemoryBackendǁstore__mutmut_24, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_25': xǁSQLiteMemoryBackendǁstore__mutmut_25, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_26': xǁSQLiteMemoryBackendǁstore__mutmut_26, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_27': xǁSQLiteMemoryBackendǁstore__mutmut_27, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_28': xǁSQLiteMemoryBackendǁstore__mutmut_28, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_29': xǁSQLiteMemoryBackendǁstore__mutmut_29, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_30': xǁSQLiteMemoryBackendǁstore__mutmut_30, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_31': xǁSQLiteMemoryBackendǁstore__mutmut_31, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_32': xǁSQLiteMemoryBackendǁstore__mutmut_32, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_33': xǁSQLiteMemoryBackendǁstore__mutmut_33, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_34': xǁSQLiteMemoryBackendǁstore__mutmut_34, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_35': xǁSQLiteMemoryBackendǁstore__mutmut_35, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_36': xǁSQLiteMemoryBackendǁstore__mutmut_36, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_37': xǁSQLiteMemoryBackendǁstore__mutmut_37, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_38': xǁSQLiteMemoryBackendǁstore__mutmut_38, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_39': xǁSQLiteMemoryBackendǁstore__mutmut_39, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_40': xǁSQLiteMemoryBackendǁstore__mutmut_40, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_41': xǁSQLiteMemoryBackendǁstore__mutmut_41, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_42': xǁSQLiteMemoryBackendǁstore__mutmut_42, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_43': xǁSQLiteMemoryBackendǁstore__mutmut_43, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_44': xǁSQLiteMemoryBackendǁstore__mutmut_44, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_45': xǁSQLiteMemoryBackendǁstore__mutmut_45, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_46': xǁSQLiteMemoryBackendǁstore__mutmut_46, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_47': xǁSQLiteMemoryBackendǁstore__mutmut_47, 
        'xǁSQLiteMemoryBackendǁstore__mutmut_48': xǁSQLiteMemoryBackendǁstore__mutmut_48
    }
    
    def store(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁstore__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁstore__mutmut_mutants"), args, kwargs, self)
        return result 
    
    store.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁstore__mutmut_orig)
    xǁSQLiteMemoryBackendǁstore__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁstore'
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_orig(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_1(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = None
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_2(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "XXSELECT * FROM memories WHERE 1=1XX"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_3(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "select * from memories where 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_4(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM MEMORIES WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_5(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = None
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_6(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql = " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_7(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql -= " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_8(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += "XX AND agent_id = ?XX"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_9(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " and agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_10(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND AGENT_ID = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_11(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(None)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_12(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql = " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_13(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql -= " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_14(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += "XX AND session_id = ?XX"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_15(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " and session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_16(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND SESSION_ID = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_17(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(None)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_18(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql = " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_19(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql -= " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_20(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += "XX AND timestamp >= ?XX"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_21(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " and timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_22(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND TIMESTAMP >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_23(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(None)
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_24(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql = " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_25(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql -= " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_26(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += "XX AND content LIKE ?XX"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_27(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " and content like ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_28(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND CONTENT LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_29(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(None)
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_30(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql = " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_31(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql -= " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_32(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += "XX ORDER BY timestamp DESC LIMIT ?XX"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_33(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " order by timestamp desc limit ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_34(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY TIMESTAMP DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_35(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(None)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_36(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(None) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_37(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = None
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_38(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = None
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_39(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(None, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_40(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, None)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_41(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_42(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, )
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_43(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = None
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_44(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    None
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_45(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict(None)
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_46(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "XXidXX": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_47(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "ID": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_48(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["XXidXX"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_49(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["ID"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_50(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "XXcontentXX": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_51(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "CONTENT": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_52(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(None),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_53(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["XXcontentXX"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_54(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["CONTENT"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_55(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "XXtimestampXX": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_56(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "TIMESTAMP": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_57(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["XXtimestampXX"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_58(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["TIMESTAMP"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_59(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "XXagent_idXX": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_60(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "AGENT_ID": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_61(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["XXagent_idXX"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_62(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["AGENT_ID"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_63(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "XXsession_idXX": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_64(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "SESSION_ID": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_65(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["XXsession_idXX"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_66(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["SESSION_ID"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_67(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "XXmetadataXX": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_68(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "METADATA": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_69(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(None) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_70(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["XXmetadataXX"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_71(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["METADATA"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_72(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["XXmetadataXX"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_73(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["METADATA"] else {},
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_74(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "XXembeddingXX": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_75(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "EMBEDDING": json.loads(row["embedding"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_76(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(None) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_77(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["XXembeddingXX"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_78(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["EMBEDDING"]) if row["embedding"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_79(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["XXembeddingXX"] else None,
                    })
                )
            
            return entries
    
    def xǁSQLiteMemoryBackendǁretrieve__mutmut_80(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Retrieve entries using SQL queries."""
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query.agent_id:
            sql += " AND agent_id = ?"
            params.append(query.agent_id)
        
        if query.session_id:
            sql += " AND session_id = ?"
            params.append(query.session_id)
        
        if query.since:
            sql += " AND timestamp >= ?"
            params.append(query.since.isoformat())
        
        if query.text:
            sql += " AND content LIKE ?"
            params.append(f"%{query.text}%")
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            
            entries = []
            for row in cursor:
                entries.append(
                    MemoryEntry.from_dict({
                        "id": row["id"],
                        "content": json.loads(row["content"]),
                        "timestamp": row["timestamp"],
                        "agent_id": row["agent_id"],
                        "session_id": row["session_id"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "embedding": json.loads(row["embedding"]) if row["EMBEDDING"] else None,
                    })
                )
            
            return entries
    
    xǁSQLiteMemoryBackendǁretrieve__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁretrieve__mutmut_1': xǁSQLiteMemoryBackendǁretrieve__mutmut_1, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_2': xǁSQLiteMemoryBackendǁretrieve__mutmut_2, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_3': xǁSQLiteMemoryBackendǁretrieve__mutmut_3, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_4': xǁSQLiteMemoryBackendǁretrieve__mutmut_4, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_5': xǁSQLiteMemoryBackendǁretrieve__mutmut_5, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_6': xǁSQLiteMemoryBackendǁretrieve__mutmut_6, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_7': xǁSQLiteMemoryBackendǁretrieve__mutmut_7, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_8': xǁSQLiteMemoryBackendǁretrieve__mutmut_8, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_9': xǁSQLiteMemoryBackendǁretrieve__mutmut_9, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_10': xǁSQLiteMemoryBackendǁretrieve__mutmut_10, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_11': xǁSQLiteMemoryBackendǁretrieve__mutmut_11, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_12': xǁSQLiteMemoryBackendǁretrieve__mutmut_12, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_13': xǁSQLiteMemoryBackendǁretrieve__mutmut_13, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_14': xǁSQLiteMemoryBackendǁretrieve__mutmut_14, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_15': xǁSQLiteMemoryBackendǁretrieve__mutmut_15, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_16': xǁSQLiteMemoryBackendǁretrieve__mutmut_16, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_17': xǁSQLiteMemoryBackendǁretrieve__mutmut_17, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_18': xǁSQLiteMemoryBackendǁretrieve__mutmut_18, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_19': xǁSQLiteMemoryBackendǁretrieve__mutmut_19, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_20': xǁSQLiteMemoryBackendǁretrieve__mutmut_20, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_21': xǁSQLiteMemoryBackendǁretrieve__mutmut_21, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_22': xǁSQLiteMemoryBackendǁretrieve__mutmut_22, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_23': xǁSQLiteMemoryBackendǁretrieve__mutmut_23, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_24': xǁSQLiteMemoryBackendǁretrieve__mutmut_24, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_25': xǁSQLiteMemoryBackendǁretrieve__mutmut_25, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_26': xǁSQLiteMemoryBackendǁretrieve__mutmut_26, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_27': xǁSQLiteMemoryBackendǁretrieve__mutmut_27, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_28': xǁSQLiteMemoryBackendǁretrieve__mutmut_28, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_29': xǁSQLiteMemoryBackendǁretrieve__mutmut_29, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_30': xǁSQLiteMemoryBackendǁretrieve__mutmut_30, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_31': xǁSQLiteMemoryBackendǁretrieve__mutmut_31, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_32': xǁSQLiteMemoryBackendǁretrieve__mutmut_32, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_33': xǁSQLiteMemoryBackendǁretrieve__mutmut_33, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_34': xǁSQLiteMemoryBackendǁretrieve__mutmut_34, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_35': xǁSQLiteMemoryBackendǁretrieve__mutmut_35, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_36': xǁSQLiteMemoryBackendǁretrieve__mutmut_36, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_37': xǁSQLiteMemoryBackendǁretrieve__mutmut_37, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_38': xǁSQLiteMemoryBackendǁretrieve__mutmut_38, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_39': xǁSQLiteMemoryBackendǁretrieve__mutmut_39, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_40': xǁSQLiteMemoryBackendǁretrieve__mutmut_40, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_41': xǁSQLiteMemoryBackendǁretrieve__mutmut_41, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_42': xǁSQLiteMemoryBackendǁretrieve__mutmut_42, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_43': xǁSQLiteMemoryBackendǁretrieve__mutmut_43, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_44': xǁSQLiteMemoryBackendǁretrieve__mutmut_44, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_45': xǁSQLiteMemoryBackendǁretrieve__mutmut_45, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_46': xǁSQLiteMemoryBackendǁretrieve__mutmut_46, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_47': xǁSQLiteMemoryBackendǁretrieve__mutmut_47, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_48': xǁSQLiteMemoryBackendǁretrieve__mutmut_48, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_49': xǁSQLiteMemoryBackendǁretrieve__mutmut_49, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_50': xǁSQLiteMemoryBackendǁretrieve__mutmut_50, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_51': xǁSQLiteMemoryBackendǁretrieve__mutmut_51, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_52': xǁSQLiteMemoryBackendǁretrieve__mutmut_52, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_53': xǁSQLiteMemoryBackendǁretrieve__mutmut_53, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_54': xǁSQLiteMemoryBackendǁretrieve__mutmut_54, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_55': xǁSQLiteMemoryBackendǁretrieve__mutmut_55, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_56': xǁSQLiteMemoryBackendǁretrieve__mutmut_56, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_57': xǁSQLiteMemoryBackendǁretrieve__mutmut_57, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_58': xǁSQLiteMemoryBackendǁretrieve__mutmut_58, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_59': xǁSQLiteMemoryBackendǁretrieve__mutmut_59, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_60': xǁSQLiteMemoryBackendǁretrieve__mutmut_60, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_61': xǁSQLiteMemoryBackendǁretrieve__mutmut_61, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_62': xǁSQLiteMemoryBackendǁretrieve__mutmut_62, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_63': xǁSQLiteMemoryBackendǁretrieve__mutmut_63, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_64': xǁSQLiteMemoryBackendǁretrieve__mutmut_64, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_65': xǁSQLiteMemoryBackendǁretrieve__mutmut_65, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_66': xǁSQLiteMemoryBackendǁretrieve__mutmut_66, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_67': xǁSQLiteMemoryBackendǁretrieve__mutmut_67, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_68': xǁSQLiteMemoryBackendǁretrieve__mutmut_68, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_69': xǁSQLiteMemoryBackendǁretrieve__mutmut_69, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_70': xǁSQLiteMemoryBackendǁretrieve__mutmut_70, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_71': xǁSQLiteMemoryBackendǁretrieve__mutmut_71, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_72': xǁSQLiteMemoryBackendǁretrieve__mutmut_72, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_73': xǁSQLiteMemoryBackendǁretrieve__mutmut_73, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_74': xǁSQLiteMemoryBackendǁretrieve__mutmut_74, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_75': xǁSQLiteMemoryBackendǁretrieve__mutmut_75, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_76': xǁSQLiteMemoryBackendǁretrieve__mutmut_76, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_77': xǁSQLiteMemoryBackendǁretrieve__mutmut_77, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_78': xǁSQLiteMemoryBackendǁretrieve__mutmut_78, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_79': xǁSQLiteMemoryBackendǁretrieve__mutmut_79, 
        'xǁSQLiteMemoryBackendǁretrieve__mutmut_80': xǁSQLiteMemoryBackendǁretrieve__mutmut_80
    }
    
    def retrieve(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁretrieve__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁretrieve__mutmut_mutants"), args, kwargs, self)
        return result 
    
    retrieve.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁretrieve__mutmut_orig)
    xǁSQLiteMemoryBackendǁretrieve__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁretrieve'
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_orig(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_1(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(None) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_2(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = None
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_3(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(None, (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_4(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", None)
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_5(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute((str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_6(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", )
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_7(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("XXDELETE FROM memories WHERE id = ?XX", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_8(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("delete from memories where id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_9(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM MEMORIES WHERE ID = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_10(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(None),))
            conn.commit()
            return cursor.rowcount > 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_11(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount >= 0
    
    def xǁSQLiteMemoryBackendǁdelete__mutmut_12(self, entry_id: UUID) -> bool:
        """Delete entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (str(entry_id),))
            conn.commit()
            return cursor.rowcount > 1
    
    xǁSQLiteMemoryBackendǁdelete__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁdelete__mutmut_1': xǁSQLiteMemoryBackendǁdelete__mutmut_1, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_2': xǁSQLiteMemoryBackendǁdelete__mutmut_2, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_3': xǁSQLiteMemoryBackendǁdelete__mutmut_3, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_4': xǁSQLiteMemoryBackendǁdelete__mutmut_4, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_5': xǁSQLiteMemoryBackendǁdelete__mutmut_5, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_6': xǁSQLiteMemoryBackendǁdelete__mutmut_6, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_7': xǁSQLiteMemoryBackendǁdelete__mutmut_7, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_8': xǁSQLiteMemoryBackendǁdelete__mutmut_8, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_9': xǁSQLiteMemoryBackendǁdelete__mutmut_9, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_10': xǁSQLiteMemoryBackendǁdelete__mutmut_10, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_11': xǁSQLiteMemoryBackendǁdelete__mutmut_11, 
        'xǁSQLiteMemoryBackendǁdelete__mutmut_12': xǁSQLiteMemoryBackendǁdelete__mutmut_12
    }
    
    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁdelete__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁdelete__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁdelete__mutmut_orig)
    xǁSQLiteMemoryBackendǁdelete__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁdelete'
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_orig(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_1(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(None) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_2(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = None
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_3(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(None, (session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_4(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE session_id = ?", None)
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_5(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute((session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_6(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM memories WHERE session_id = ?", )
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_7(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("XXDELETE FROM memories WHERE session_id = ?XX", (session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_8(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("delete from memories where session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount
    
    def xǁSQLiteMemoryBackendǁclear_session__mutmut_9(self, session_id: str) -> int:
        """Delete all entries for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM MEMORIES WHERE SESSION_ID = ?", (session_id,))
            conn.commit()
            return cursor.rowcount
    
    xǁSQLiteMemoryBackendǁclear_session__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁclear_session__mutmut_1': xǁSQLiteMemoryBackendǁclear_session__mutmut_1, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_2': xǁSQLiteMemoryBackendǁclear_session__mutmut_2, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_3': xǁSQLiteMemoryBackendǁclear_session__mutmut_3, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_4': xǁSQLiteMemoryBackendǁclear_session__mutmut_4, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_5': xǁSQLiteMemoryBackendǁclear_session__mutmut_5, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_6': xǁSQLiteMemoryBackendǁclear_session__mutmut_6, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_7': xǁSQLiteMemoryBackendǁclear_session__mutmut_7, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_8': xǁSQLiteMemoryBackendǁclear_session__mutmut_8, 
        'xǁSQLiteMemoryBackendǁclear_session__mutmut_9': xǁSQLiteMemoryBackendǁclear_session__mutmut_9
    }
    
    def clear_session(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁclear_session__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁclear_session__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_session.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁclear_session__mutmut_orig)
    xǁSQLiteMemoryBackendǁclear_session__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁclear_session'
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_orig(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_1(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(None) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_2(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = None
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_3(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(None)
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_4(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("XXSELECT COUNT(*) FROM memoriesXX")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_5(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("select count(*) from memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_6(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM MEMORIES")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_7(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = None
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_8(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[1]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_9(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "XXentry_countXX": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_10(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "ENTRY_COUNT": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_11(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "XXsize_bytesXX": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_12(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "SIZE_BYTES": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_13(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 1,
                "backend": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_14(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "XXbackendXX": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_15(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "BACKEND": "sqlite",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_16(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "XXsqliteXX",
            }
    
    def xǁSQLiteMemoryBackendǁget_stats__mutmut_17(self) -> dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            entry_count = cursor.fetchone()[0]
            
            return {
                "entry_count": entry_count,
                "size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "backend": "SQLITE",
            }
    
    xǁSQLiteMemoryBackendǁget_stats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSQLiteMemoryBackendǁget_stats__mutmut_1': xǁSQLiteMemoryBackendǁget_stats__mutmut_1, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_2': xǁSQLiteMemoryBackendǁget_stats__mutmut_2, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_3': xǁSQLiteMemoryBackendǁget_stats__mutmut_3, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_4': xǁSQLiteMemoryBackendǁget_stats__mutmut_4, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_5': xǁSQLiteMemoryBackendǁget_stats__mutmut_5, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_6': xǁSQLiteMemoryBackendǁget_stats__mutmut_6, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_7': xǁSQLiteMemoryBackendǁget_stats__mutmut_7, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_8': xǁSQLiteMemoryBackendǁget_stats__mutmut_8, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_9': xǁSQLiteMemoryBackendǁget_stats__mutmut_9, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_10': xǁSQLiteMemoryBackendǁget_stats__mutmut_10, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_11': xǁSQLiteMemoryBackendǁget_stats__mutmut_11, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_12': xǁSQLiteMemoryBackendǁget_stats__mutmut_12, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_13': xǁSQLiteMemoryBackendǁget_stats__mutmut_13, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_14': xǁSQLiteMemoryBackendǁget_stats__mutmut_14, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_15': xǁSQLiteMemoryBackendǁget_stats__mutmut_15, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_16': xǁSQLiteMemoryBackendǁget_stats__mutmut_16, 
        'xǁSQLiteMemoryBackendǁget_stats__mutmut_17': xǁSQLiteMemoryBackendǁget_stats__mutmut_17
    }
    
    def get_stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSQLiteMemoryBackendǁget_stats__mutmut_orig"), object.__getattribute__(self, "xǁSQLiteMemoryBackendǁget_stats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_stats.__signature__ = _mutmut_signature(xǁSQLiteMemoryBackendǁget_stats__mutmut_orig)
    xǁSQLiteMemoryBackendǁget_stats__mutmut_orig.__name__ = 'xǁSQLiteMemoryBackendǁget_stats'
