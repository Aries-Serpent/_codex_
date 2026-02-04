"""
Session-based caching utilities for Codex processing optimization.

Purpose:
  Reduce file I/O overhead by caching frequently accessed files
  and memoizing search results during a session.

References:
  - Analysis finding: 24+ duplicate file reads per session
  - Unix principle: Cache results, avoid redundant I/O

Classes:
  - FileCache: Mtime-aware file content cache
  - SearchCache: Memoization decorator for search operations
"""

from __future__ import annotations

import hashlib
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

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


class FileCache:
    """Mtime-aware file content cache for session optimization.

    Usage:
        cache = FileCache()
        cache.add("scripts/survey.sh")
        content = cache.get("scripts/survey.sh")  # Returns cached content
        cache.invalidate_if_modified("scripts/survey.sh")  # Refresh if changed
    """

    def xǁFileCacheǁ__init____mutmut_orig(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("FileCache initialized")

    def xǁFileCacheǁ__init____mutmut_1(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = None
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("FileCache initialized")

    def xǁFileCacheǁ__init____mutmut_2(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = None
        self._file_shas: dict[str, str] = {}
        logger.info("FileCache initialized")

    def xǁFileCacheǁ__init____mutmut_3(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = None
        logger.info("FileCache initialized")

    def xǁFileCacheǁ__init____mutmut_4(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info(None)

    def xǁFileCacheǁ__init____mutmut_5(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("XXFileCache initializedXX")

    def xǁFileCacheǁ__init____mutmut_6(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("filecache initialized")

    def xǁFileCacheǁ__init____mutmut_7(self):
        """Initialize file cache."""
        self._file_contents: dict[str, str] = {}
        self._file_mtimes: dict[str, float] = {}
        self._file_shas: dict[str, str] = {}
        logger.info("FILECACHE INITIALIZED")
    
    xǁFileCacheǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁ__init____mutmut_1': xǁFileCacheǁ__init____mutmut_1, 
        'xǁFileCacheǁ__init____mutmut_2': xǁFileCacheǁ__init____mutmut_2, 
        'xǁFileCacheǁ__init____mutmut_3': xǁFileCacheǁ__init____mutmut_3, 
        'xǁFileCacheǁ__init____mutmut_4': xǁFileCacheǁ__init____mutmut_4, 
        'xǁFileCacheǁ__init____mutmut_5': xǁFileCacheǁ__init____mutmut_5, 
        'xǁFileCacheǁ__init____mutmut_6': xǁFileCacheǁ__init____mutmut_6, 
        'xǁFileCacheǁ__init____mutmut_7': xǁFileCacheǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁFileCacheǁ__init____mutmut_orig)
    xǁFileCacheǁ__init____mutmut_orig.__name__ = 'xǁFileCacheǁ__init__'

    def xǁFileCacheǁadd__mutmut_orig(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_1(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = None
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_2(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(None)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_3(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_4(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(None)
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_5(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return True

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_6(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(None, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_7(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, None, encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_8(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding=None) as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_9(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open("r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_10(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_11(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", ) as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_12(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "XXrXX", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_13(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "R", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_14(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="XXutf-8XX") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_15(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="UTF-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_16(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = None

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_17(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = None
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_18(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = None

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_19(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(None).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_20(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = None
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_21(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = None
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_22(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = None

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_23(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(None)
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_24(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return False
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_25(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(None)
            logger.error(f"Failed to cache file {file_path}: {e}")
            return False

    def xǁFileCacheǁadd__mutmut_26(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(None)
            return False

    def xǁFileCacheǁadd__mutmut_27(self, file_path: str) -> bool:
        """Add file to cache. Returns True if successful, False if file not found."""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            stat = path.stat()
            sha = hashlib.sha256(content.encode()).hexdigest()

            self._file_contents[file_path] = content
            self._file_mtimes[file_path] = stat.st_mtime
            self._file_shas[file_path] = sha

            logger.debug(f"Cached file ({len(content)} bytes): {file_path}")
            return True
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Failed to cache file {file_path}: {e}")
            return True
    
    xǁFileCacheǁadd__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁadd__mutmut_1': xǁFileCacheǁadd__mutmut_1, 
        'xǁFileCacheǁadd__mutmut_2': xǁFileCacheǁadd__mutmut_2, 
        'xǁFileCacheǁadd__mutmut_3': xǁFileCacheǁadd__mutmut_3, 
        'xǁFileCacheǁadd__mutmut_4': xǁFileCacheǁadd__mutmut_4, 
        'xǁFileCacheǁadd__mutmut_5': xǁFileCacheǁadd__mutmut_5, 
        'xǁFileCacheǁadd__mutmut_6': xǁFileCacheǁadd__mutmut_6, 
        'xǁFileCacheǁadd__mutmut_7': xǁFileCacheǁadd__mutmut_7, 
        'xǁFileCacheǁadd__mutmut_8': xǁFileCacheǁadd__mutmut_8, 
        'xǁFileCacheǁadd__mutmut_9': xǁFileCacheǁadd__mutmut_9, 
        'xǁFileCacheǁadd__mutmut_10': xǁFileCacheǁadd__mutmut_10, 
        'xǁFileCacheǁadd__mutmut_11': xǁFileCacheǁadd__mutmut_11, 
        'xǁFileCacheǁadd__mutmut_12': xǁFileCacheǁadd__mutmut_12, 
        'xǁFileCacheǁadd__mutmut_13': xǁFileCacheǁadd__mutmut_13, 
        'xǁFileCacheǁadd__mutmut_14': xǁFileCacheǁadd__mutmut_14, 
        'xǁFileCacheǁadd__mutmut_15': xǁFileCacheǁadd__mutmut_15, 
        'xǁFileCacheǁadd__mutmut_16': xǁFileCacheǁadd__mutmut_16, 
        'xǁFileCacheǁadd__mutmut_17': xǁFileCacheǁadd__mutmut_17, 
        'xǁFileCacheǁadd__mutmut_18': xǁFileCacheǁadd__mutmut_18, 
        'xǁFileCacheǁadd__mutmut_19': xǁFileCacheǁadd__mutmut_19, 
        'xǁFileCacheǁadd__mutmut_20': xǁFileCacheǁadd__mutmut_20, 
        'xǁFileCacheǁadd__mutmut_21': xǁFileCacheǁadd__mutmut_21, 
        'xǁFileCacheǁadd__mutmut_22': xǁFileCacheǁadd__mutmut_22, 
        'xǁFileCacheǁadd__mutmut_23': xǁFileCacheǁadd__mutmut_23, 
        'xǁFileCacheǁadd__mutmut_24': xǁFileCacheǁadd__mutmut_24, 
        'xǁFileCacheǁadd__mutmut_25': xǁFileCacheǁadd__mutmut_25, 
        'xǁFileCacheǁadd__mutmut_26': xǁFileCacheǁadd__mutmut_26, 
        'xǁFileCacheǁadd__mutmut_27': xǁFileCacheǁadd__mutmut_27
    }
    
    def add(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁadd__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁadd__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add.__signature__ = _mutmut_signature(xǁFileCacheǁadd__mutmut_orig)
    xǁFileCacheǁadd__mutmut_orig.__name__ = 'xǁFileCacheǁadd'

    def xǁFileCacheǁget__mutmut_orig(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path not in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def xǁFileCacheǁget__mutmut_1(self, file_path: str, auto_refresh: bool = False) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path not in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def xǁFileCacheǁget__mutmut_2(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(None)

        if file_path not in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def xǁFileCacheǁget__mutmut_3(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def xǁFileCacheǁget__mutmut_4(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path not in self._file_contents:
            logger.warning(None)
            return None

        logger.debug(f"Cache hit: {file_path}")
        return self._file_contents[file_path]

    def xǁFileCacheǁget__mutmut_5(self, file_path: str, auto_refresh: bool = True) -> Optional[str]:
        """Retrieve cached content. If auto_refresh, validates mtime first."""
        if auto_refresh:
            self.invalidate_if_modified(file_path)

        if file_path not in self._file_contents:
            logger.warning(f"Cache miss: {file_path} (not cached)")
            return None

        logger.debug(None)
        return self._file_contents[file_path]
    
    xǁFileCacheǁget__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁget__mutmut_1': xǁFileCacheǁget__mutmut_1, 
        'xǁFileCacheǁget__mutmut_2': xǁFileCacheǁget__mutmut_2, 
        'xǁFileCacheǁget__mutmut_3': xǁFileCacheǁget__mutmut_3, 
        'xǁFileCacheǁget__mutmut_4': xǁFileCacheǁget__mutmut_4, 
        'xǁFileCacheǁget__mutmut_5': xǁFileCacheǁget__mutmut_5
    }
    
    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁget__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁget__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get.__signature__ = _mutmut_signature(xǁFileCacheǁget__mutmut_orig)
    xǁFileCacheǁget__mutmut_orig.__name__ = 'xǁFileCacheǁget'

    def xǁFileCacheǁinvalidate_if_modified__mutmut_orig(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_1(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_2(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return True

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_3(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = None
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_4(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(None)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_5(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_6(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(None)
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_7(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(None)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_8(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return True

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_9(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = None
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_10(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime == self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_11(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(None)
            self.clear(file_path)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_12(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(None)
            return self.add(file_path)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_13(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(None)

        return False

    def xǁFileCacheǁinvalidate_if_modified__mutmut_14(self, file_path: str) -> bool:
        """Check if file modified since caching. Refresh if needed. Returns True if refreshed."""
        if file_path not in self._file_mtimes:
            return False

        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cached file no longer exists: {file_path}")
            self.clear(file_path)
            return False

        current_mtime = path.stat().st_mtime
        if current_mtime != self._file_mtimes[file_path]:
            logger.info(f"File modified, refreshing cache: {file_path}")
            self.clear(file_path)
            return self.add(file_path)

        return True
    
    xǁFileCacheǁinvalidate_if_modified__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁinvalidate_if_modified__mutmut_1': xǁFileCacheǁinvalidate_if_modified__mutmut_1, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_2': xǁFileCacheǁinvalidate_if_modified__mutmut_2, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_3': xǁFileCacheǁinvalidate_if_modified__mutmut_3, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_4': xǁFileCacheǁinvalidate_if_modified__mutmut_4, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_5': xǁFileCacheǁinvalidate_if_modified__mutmut_5, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_6': xǁFileCacheǁinvalidate_if_modified__mutmut_6, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_7': xǁFileCacheǁinvalidate_if_modified__mutmut_7, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_8': xǁFileCacheǁinvalidate_if_modified__mutmut_8, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_9': xǁFileCacheǁinvalidate_if_modified__mutmut_9, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_10': xǁFileCacheǁinvalidate_if_modified__mutmut_10, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_11': xǁFileCacheǁinvalidate_if_modified__mutmut_11, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_12': xǁFileCacheǁinvalidate_if_modified__mutmut_12, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_13': xǁFileCacheǁinvalidate_if_modified__mutmut_13, 
        'xǁFileCacheǁinvalidate_if_modified__mutmut_14': xǁFileCacheǁinvalidate_if_modified__mutmut_14
    }
    
    def invalidate_if_modified(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁinvalidate_if_modified__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁinvalidate_if_modified__mutmut_mutants"), args, kwargs, self)
        return result 
    
    invalidate_if_modified.__signature__ = _mutmut_signature(xǁFileCacheǁinvalidate_if_modified__mutmut_orig)
    xǁFileCacheǁinvalidate_if_modified__mutmut_orig.__name__ = 'xǁFileCacheǁinvalidate_if_modified'

    def xǁFileCacheǁget_sha__mutmut_orig(self, file_path: str) -> Optional[str]:
        """Retrieve cached SHA256 hash of file."""
        return self._file_shas.get(file_path)

    def xǁFileCacheǁget_sha__mutmut_1(self, file_path: str) -> Optional[str]:
        """Retrieve cached SHA256 hash of file."""
        return self._file_shas.get(None)
    
    xǁFileCacheǁget_sha__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁget_sha__mutmut_1': xǁFileCacheǁget_sha__mutmut_1
    }
    
    def get_sha(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁget_sha__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁget_sha__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_sha.__signature__ = _mutmut_signature(xǁFileCacheǁget_sha__mutmut_orig)
    xǁFileCacheǁget_sha__mutmut_orig.__name__ = 'xǁFileCacheǁget_sha'

    def xǁFileCacheǁclear__mutmut_orig(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_1(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(None, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_2(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_3(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, )
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_4(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(None, None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_5(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(None)
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_6(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, )
        self._file_shas.pop(file_path, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_7(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(None, None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_8(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(None)
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_9(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, )
        logger.debug(f"Cleared cache: {file_path}")

    def xǁFileCacheǁclear__mutmut_10(self, file_path: str) -> None:
        """Remove file from cache."""
        self._file_contents.pop(file_path, None)
        self._file_mtimes.pop(file_path, None)
        self._file_shas.pop(file_path, None)
        logger.debug(None)
    
    xǁFileCacheǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁclear__mutmut_1': xǁFileCacheǁclear__mutmut_1, 
        'xǁFileCacheǁclear__mutmut_2': xǁFileCacheǁclear__mutmut_2, 
        'xǁFileCacheǁclear__mutmut_3': xǁFileCacheǁclear__mutmut_3, 
        'xǁFileCacheǁclear__mutmut_4': xǁFileCacheǁclear__mutmut_4, 
        'xǁFileCacheǁclear__mutmut_5': xǁFileCacheǁclear__mutmut_5, 
        'xǁFileCacheǁclear__mutmut_6': xǁFileCacheǁclear__mutmut_6, 
        'xǁFileCacheǁclear__mutmut_7': xǁFileCacheǁclear__mutmut_7, 
        'xǁFileCacheǁclear__mutmut_8': xǁFileCacheǁclear__mutmut_8, 
        'xǁFileCacheǁclear__mutmut_9': xǁFileCacheǁclear__mutmut_9, 
        'xǁFileCacheǁclear__mutmut_10': xǁFileCacheǁclear__mutmut_10
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁclear__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁFileCacheǁclear__mutmut_orig)
    xǁFileCacheǁclear__mutmut_orig.__name__ = 'xǁFileCacheǁclear'

    def xǁFileCacheǁclear_all__mutmut_orig(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info("Cache cleared (all files)")

    def xǁFileCacheǁclear_all__mutmut_1(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info(None)

    def xǁFileCacheǁclear_all__mutmut_2(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info("XXCache cleared (all files)XX")

    def xǁFileCacheǁclear_all__mutmut_3(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info("cache cleared (all files)")

    def xǁFileCacheǁclear_all__mutmut_4(self) -> None:
        """Clear entire cache."""
        self._file_contents.clear()
        self._file_mtimes.clear()
        self._file_shas.clear()
        logger.info("CACHE CLEARED (ALL FILES)")
    
    xǁFileCacheǁclear_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁclear_all__mutmut_1': xǁFileCacheǁclear_all__mutmut_1, 
        'xǁFileCacheǁclear_all__mutmut_2': xǁFileCacheǁclear_all__mutmut_2, 
        'xǁFileCacheǁclear_all__mutmut_3': xǁFileCacheǁclear_all__mutmut_3, 
        'xǁFileCacheǁclear_all__mutmut_4': xǁFileCacheǁclear_all__mutmut_4
    }
    
    def clear_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁclear_all__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁclear_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_all.__signature__ = _mutmut_signature(xǁFileCacheǁclear_all__mutmut_orig)
    xǁFileCacheǁclear_all__mutmut_orig.__name__ = 'xǁFileCacheǁclear_all'

    def xǁFileCacheǁstats__mutmut_orig(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_1(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "XXcached_filesXX": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_2(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "CACHED_FILES": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_3(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "XXtotal_size_bytesXX": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_4(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "TOTAL_SIZE_BYTES": sum(len(c) for c in self._file_contents.values()),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_5(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(None),
            "files": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_6(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "XXfilesXX": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_7(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "FILES": list(self._file_contents.keys()),
        }

    def xǁFileCacheǁstats__mutmut_8(self) -> dict[str, Any]:
        """Return cache statistics."""
        return {
            "cached_files": len(self._file_contents),
            "total_size_bytes": sum(len(c) for c in self._file_contents.values()),
            "files": list(None),
        }
    
    xǁFileCacheǁstats__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁFileCacheǁstats__mutmut_1': xǁFileCacheǁstats__mutmut_1, 
        'xǁFileCacheǁstats__mutmut_2': xǁFileCacheǁstats__mutmut_2, 
        'xǁFileCacheǁstats__mutmut_3': xǁFileCacheǁstats__mutmut_3, 
        'xǁFileCacheǁstats__mutmut_4': xǁFileCacheǁstats__mutmut_4, 
        'xǁFileCacheǁstats__mutmut_5': xǁFileCacheǁstats__mutmut_5, 
        'xǁFileCacheǁstats__mutmut_6': xǁFileCacheǁstats__mutmut_6, 
        'xǁFileCacheǁstats__mutmut_7': xǁFileCacheǁstats__mutmut_7, 
        'xǁFileCacheǁstats__mutmut_8': xǁFileCacheǁstats__mutmut_8
    }
    
    def stats(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁFileCacheǁstats__mutmut_orig"), object.__getattribute__(self, "xǁFileCacheǁstats__mutmut_mutants"), args, kwargs, self)
        return result 
    
    stats.__signature__ = _mutmut_signature(xǁFileCacheǁstats__mutmut_orig)
    xǁFileCacheǁstats__mutmut_orig.__name__ = 'xǁFileCacheǁstats'


class SearchCache:
    """Memoization decorator for search operations.

    Usage:
        cache = SearchCache()

        @cache.memoize
        def find_files(pattern, scope):
            return subprocess.run(['find', scope, '-name', pattern]).stdout

        result1 = find_files('*.py', '/src')  # Executes search
        result2 = find_files('*.py', '/src')  # Returns cached result
    """

    def xǁSearchCacheǁ__init____mutmut_orig(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info("SearchCache initialized")

    def xǁSearchCacheǁ__init____mutmut_1(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = None
        logger.info("SearchCache initialized")

    def xǁSearchCacheǁ__init____mutmut_2(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info(None)

    def xǁSearchCacheǁ__init____mutmut_3(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info("XXSearchCache initializedXX")

    def xǁSearchCacheǁ__init____mutmut_4(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info("searchcache initialized")

    def xǁSearchCacheǁ__init____mutmut_5(self):
        """Initialize search cache."""
        self._cache: dict[str, Any] = {}
        logger.info("SEARCHCACHE INITIALIZED")
    
    xǁSearchCacheǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSearchCacheǁ__init____mutmut_1': xǁSearchCacheǁ__init____mutmut_1, 
        'xǁSearchCacheǁ__init____mutmut_2': xǁSearchCacheǁ__init____mutmut_2, 
        'xǁSearchCacheǁ__init____mutmut_3': xǁSearchCacheǁ__init____mutmut_3, 
        'xǁSearchCacheǁ__init____mutmut_4': xǁSearchCacheǁ__init____mutmut_4, 
        'xǁSearchCacheǁ__init____mutmut_5': xǁSearchCacheǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSearchCacheǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSearchCacheǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSearchCacheǁ__init____mutmut_orig)
    xǁSearchCacheǁ__init____mutmut_orig.__name__ = 'xǁSearchCacheǁ__init__'

    def memoize(self, func: Callable) -> Callable:
        """Decorator to memoize function results."""

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if key in self._cache:
                logger.debug(f"Search cache hit: {func.__name__}")
                return self._cache[key]

            result = func(*args, **kwargs)
            self._cache[key] = result
            logger.debug(f"Search cached: {func.__name__}")
            return result

        return wrapper

    def xǁSearchCacheǁclear__mutmut_orig(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("Search cache cleared")

    def xǁSearchCacheǁclear__mutmut_1(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info(None)

    def xǁSearchCacheǁclear__mutmut_2(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("XXSearch cache clearedXX")

    def xǁSearchCacheǁclear__mutmut_3(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("search cache cleared")

    def xǁSearchCacheǁclear__mutmut_4(self) -> None:
        """Clear search cache."""
        self._cache.clear()
        logger.info("SEARCH CACHE CLEARED")
    
    xǁSearchCacheǁclear__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSearchCacheǁclear__mutmut_1': xǁSearchCacheǁclear__mutmut_1, 
        'xǁSearchCacheǁclear__mutmut_2': xǁSearchCacheǁclear__mutmut_2, 
        'xǁSearchCacheǁclear__mutmut_3': xǁSearchCacheǁclear__mutmut_3, 
        'xǁSearchCacheǁclear__mutmut_4': xǁSearchCacheǁclear__mutmut_4
    }
    
    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSearchCacheǁclear__mutmut_orig"), object.__getattribute__(self, "xǁSearchCacheǁclear__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear.__signature__ = _mutmut_signature(xǁSearchCacheǁclear__mutmut_orig)
    xǁSearchCacheǁclear__mutmut_orig.__name__ = 'xǁSearchCacheǁclear'
