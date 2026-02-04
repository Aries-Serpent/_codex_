"""SQLite connection pooling and patch helpers.

This module monkey-patches :func:`sqlite3.connect` to reuse connections based on
database path, process, thread, and optional ``CODEX_SESSION_ID``. Pooling is
enabled via the ``CODEX_SQLITE_POOL`` environment variable and applies several
pragmas aimed at improving concurrent write performance. All pooled connections
remain open for the duration of the interpreter and are closed automatically on
interpreter exit.

Limitations:

* Connections are cached **per thread**; they are not shared between threads
  or processes. Sharing a connection across threads is not supported by the
  underlying :mod:`sqlite3` driver and may result in race conditions.
* Calling :meth:`sqlite3.Connection.close` on a pooled connection leaves a
  closed instance in the pool. Avoid ``with sqlite3.connect(...)`` blocks or
  explicit ``close()`` calls when pooling is enabled.
"""

import atexit
import logging
logger = logging.getLogger(__name__)
import os
import sqlite3
import threading

_ORIG_CONNECT = sqlite3.connect
_POOL_ENABLED_ENV = "CODEX_SQLITE_POOL"  # "1" enables pooling
_SESSION_ENV = "CODEX_SESSION_ID"  # optional logical session id

# Key: (db_path, pid, tid, session_id)
_CONN_POOL: dict[tuple[str, int, int, str], sqlite3.Connection] = {}
_POOL_LOCK = threading.RLock()
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


class PooledConnectionProxy:
    """Thin proxy that removes itself from the pool on ``close``."""

    def xǁPooledConnectionProxyǁ__init____mutmut_orig(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_1(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__(None, conn)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_2(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", None)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_3(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__(conn)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_4(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", )
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_5(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("XX_connXX", conn)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_6(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_CONN", conn)
        super().__setattr__("_key", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_7(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__(None, key)

    def xǁPooledConnectionProxyǁ__init____mutmut_8(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__("_key", None)

    def xǁPooledConnectionProxyǁ__init____mutmut_9(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__(key)

    def xǁPooledConnectionProxyǁ__init____mutmut_10(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__("_key", )

    def xǁPooledConnectionProxyǁ__init____mutmut_11(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__("XX_keyXX", key)

    def xǁPooledConnectionProxyǁ__init____mutmut_12(self, conn: sqlite3.Connection, key: tuple[str, int, int, str]):
        super().__setattr__("_conn", conn)
        super().__setattr__("_KEY", key)
    
    xǁPooledConnectionProxyǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPooledConnectionProxyǁ__init____mutmut_1': xǁPooledConnectionProxyǁ__init____mutmut_1, 
        'xǁPooledConnectionProxyǁ__init____mutmut_2': xǁPooledConnectionProxyǁ__init____mutmut_2, 
        'xǁPooledConnectionProxyǁ__init____mutmut_3': xǁPooledConnectionProxyǁ__init____mutmut_3, 
        'xǁPooledConnectionProxyǁ__init____mutmut_4': xǁPooledConnectionProxyǁ__init____mutmut_4, 
        'xǁPooledConnectionProxyǁ__init____mutmut_5': xǁPooledConnectionProxyǁ__init____mutmut_5, 
        'xǁPooledConnectionProxyǁ__init____mutmut_6': xǁPooledConnectionProxyǁ__init____mutmut_6, 
        'xǁPooledConnectionProxyǁ__init____mutmut_7': xǁPooledConnectionProxyǁ__init____mutmut_7, 
        'xǁPooledConnectionProxyǁ__init____mutmut_8': xǁPooledConnectionProxyǁ__init____mutmut_8, 
        'xǁPooledConnectionProxyǁ__init____mutmut_9': xǁPooledConnectionProxyǁ__init____mutmut_9, 
        'xǁPooledConnectionProxyǁ__init____mutmut_10': xǁPooledConnectionProxyǁ__init____mutmut_10, 
        'xǁPooledConnectionProxyǁ__init____mutmut_11': xǁPooledConnectionProxyǁ__init____mutmut_11, 
        'xǁPooledConnectionProxyǁ__init____mutmut_12': xǁPooledConnectionProxyǁ__init____mutmut_12
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPooledConnectionProxyǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁPooledConnectionProxyǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁPooledConnectionProxyǁ__init____mutmut_orig)
    xǁPooledConnectionProxyǁ__init____mutmut_orig.__name__ = 'xǁPooledConnectionProxyǁ__init__'

    def xǁPooledConnectionProxyǁ__getattr____mutmut_orig(self, name):  # pragma: no cover - simple delegation
        return getattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__getattr____mutmut_1(self, name):  # pragma: no cover - simple delegation
        return getattr(None, name)

    def xǁPooledConnectionProxyǁ__getattr____mutmut_2(self, name):  # pragma: no cover - simple delegation
        return getattr(self._conn, None)

    def xǁPooledConnectionProxyǁ__getattr____mutmut_3(self, name):  # pragma: no cover - simple delegation
        return getattr(name)

    def xǁPooledConnectionProxyǁ__getattr____mutmut_4(self, name):  # pragma: no cover - simple delegation
        return getattr(self._conn, )
    
    xǁPooledConnectionProxyǁ__getattr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPooledConnectionProxyǁ__getattr____mutmut_1': xǁPooledConnectionProxyǁ__getattr____mutmut_1, 
        'xǁPooledConnectionProxyǁ__getattr____mutmut_2': xǁPooledConnectionProxyǁ__getattr____mutmut_2, 
        'xǁPooledConnectionProxyǁ__getattr____mutmut_3': xǁPooledConnectionProxyǁ__getattr____mutmut_3, 
        'xǁPooledConnectionProxyǁ__getattr____mutmut_4': xǁPooledConnectionProxyǁ__getattr____mutmut_4
    }
    
    def __getattr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPooledConnectionProxyǁ__getattr____mutmut_orig"), object.__getattribute__(self, "xǁPooledConnectionProxyǁ__getattr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __getattr__.__signature__ = _mutmut_signature(xǁPooledConnectionProxyǁ__getattr____mutmut_orig)
    xǁPooledConnectionProxyǁ__getattr____mutmut_orig.__name__ = 'xǁPooledConnectionProxyǁ__getattr__'

    def __setattr__(self, name, value):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__setattr__(name, value)
        else:
            setattr(self._conn, name, value)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_orig(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_1(self, name):  # pragma: no cover - simple delegation
        if name not in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_2(self, name):  # pragma: no cover - simple delegation
        if name in {"XX_connXX", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_3(self, name):  # pragma: no cover - simple delegation
        if name in {"_CONN", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_4(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "XX_keyXX"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_5(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_KEY"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_6(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(None)
        else:
            delattr(self._conn, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_7(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(None, name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_8(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, None)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_9(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(name)

    def xǁPooledConnectionProxyǁ__delattr____mutmut_10(self, name):  # pragma: no cover - simple delegation
        if name in {"_conn", "_key"}:
            super().__delattr__(name)
        else:
            delattr(self._conn, )
    
    xǁPooledConnectionProxyǁ__delattr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPooledConnectionProxyǁ__delattr____mutmut_1': xǁPooledConnectionProxyǁ__delattr____mutmut_1, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_2': xǁPooledConnectionProxyǁ__delattr____mutmut_2, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_3': xǁPooledConnectionProxyǁ__delattr____mutmut_3, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_4': xǁPooledConnectionProxyǁ__delattr____mutmut_4, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_5': xǁPooledConnectionProxyǁ__delattr____mutmut_5, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_6': xǁPooledConnectionProxyǁ__delattr____mutmut_6, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_7': xǁPooledConnectionProxyǁ__delattr____mutmut_7, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_8': xǁPooledConnectionProxyǁ__delattr____mutmut_8, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_9': xǁPooledConnectionProxyǁ__delattr____mutmut_9, 
        'xǁPooledConnectionProxyǁ__delattr____mutmut_10': xǁPooledConnectionProxyǁ__delattr____mutmut_10
    }
    
    def __delattr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPooledConnectionProxyǁ__delattr____mutmut_orig"), object.__getattribute__(self, "xǁPooledConnectionProxyǁ__delattr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __delattr__.__signature__ = _mutmut_signature(xǁPooledConnectionProxyǁ__delattr____mutmut_orig)
    xǁPooledConnectionProxyǁ__delattr____mutmut_orig.__name__ = 'xǁPooledConnectionProxyǁ__delattr__'

    def __enter__(self):  # pragma: no cover - simple delegation
        # Replicate sqlite3.Connection context manager semantics without closing
        self._conn.__enter__()
        return self

    def xǁPooledConnectionProxyǁ__exit____mutmut_orig(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_1(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is not None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_2(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning(None, exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_3(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=None)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_4(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning(exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_5(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", )
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_6(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("XXException occurredXX", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_7(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_8(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("EXCEPTION OCCURRED", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_9(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=False)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_10(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning(None, exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_11(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=None)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_12(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning(exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_13(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", )
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_14(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("XXException occurredXX", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_15(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_16(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("EXCEPTION OCCURRED", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_17(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=False)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_18(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(None)
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_19(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(None, exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_20(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=None)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_21(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_22(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", )
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_23(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=False)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return False

    def xǁPooledConnectionProxyǁ__exit____mutmut_24(self, exc_type, exc, tb):  # pragma: no cover - simple delegation
        # Mirror sqlite3 behaviour: commit on success, rollback on error.
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                # Mirror sqlite behaviour which would raise the exception; allow
                # propagation to caller.
                raise
        else:
            try:
                self._conn.rollback()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        # Returning False ensures exceptions propagate like the standard
        # sqlite3 context manager.
        return True
    
    xǁPooledConnectionProxyǁ__exit____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPooledConnectionProxyǁ__exit____mutmut_1': xǁPooledConnectionProxyǁ__exit____mutmut_1, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_2': xǁPooledConnectionProxyǁ__exit____mutmut_2, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_3': xǁPooledConnectionProxyǁ__exit____mutmut_3, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_4': xǁPooledConnectionProxyǁ__exit____mutmut_4, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_5': xǁPooledConnectionProxyǁ__exit____mutmut_5, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_6': xǁPooledConnectionProxyǁ__exit____mutmut_6, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_7': xǁPooledConnectionProxyǁ__exit____mutmut_7, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_8': xǁPooledConnectionProxyǁ__exit____mutmut_8, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_9': xǁPooledConnectionProxyǁ__exit____mutmut_9, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_10': xǁPooledConnectionProxyǁ__exit____mutmut_10, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_11': xǁPooledConnectionProxyǁ__exit____mutmut_11, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_12': xǁPooledConnectionProxyǁ__exit____mutmut_12, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_13': xǁPooledConnectionProxyǁ__exit____mutmut_13, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_14': xǁPooledConnectionProxyǁ__exit____mutmut_14, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_15': xǁPooledConnectionProxyǁ__exit____mutmut_15, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_16': xǁPooledConnectionProxyǁ__exit____mutmut_16, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_17': xǁPooledConnectionProxyǁ__exit____mutmut_17, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_18': xǁPooledConnectionProxyǁ__exit____mutmut_18, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_19': xǁPooledConnectionProxyǁ__exit____mutmut_19, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_20': xǁPooledConnectionProxyǁ__exit____mutmut_20, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_21': xǁPooledConnectionProxyǁ__exit____mutmut_21, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_22': xǁPooledConnectionProxyǁ__exit____mutmut_22, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_23': xǁPooledConnectionProxyǁ__exit____mutmut_23, 
        'xǁPooledConnectionProxyǁ__exit____mutmut_24': xǁPooledConnectionProxyǁ__exit____mutmut_24
    }
    
    def __exit__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPooledConnectionProxyǁ__exit____mutmut_orig"), object.__getattribute__(self, "xǁPooledConnectionProxyǁ__exit____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __exit__.__signature__ = _mutmut_signature(xǁPooledConnectionProxyǁ__exit____mutmut_orig)
    xǁPooledConnectionProxyǁ__exit____mutmut_orig.__name__ = 'xǁPooledConnectionProxyǁ__exit__'

    def xǁPooledConnectionProxyǁclose__mutmut_orig(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_1(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(None, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_2(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_3(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, )
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_4(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(None)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_5(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(None)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_6(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(None)
                    logger.warning(f"ValueError: {e}", exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_7(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(None, exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_8(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=None)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_9(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(exc_info=True)
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_10(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", )
        return self._conn.close()

    def xǁPooledConnectionProxyǁclose__mutmut_11(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError as e:
                    logger.debug(f"ValueError: {e}")
                    logger.warning(f"ValueError: {e}", exc_info=False)
        return self._conn.close()
    
    xǁPooledConnectionProxyǁclose__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPooledConnectionProxyǁclose__mutmut_1': xǁPooledConnectionProxyǁclose__mutmut_1, 
        'xǁPooledConnectionProxyǁclose__mutmut_2': xǁPooledConnectionProxyǁclose__mutmut_2, 
        'xǁPooledConnectionProxyǁclose__mutmut_3': xǁPooledConnectionProxyǁclose__mutmut_3, 
        'xǁPooledConnectionProxyǁclose__mutmut_4': xǁPooledConnectionProxyǁclose__mutmut_4, 
        'xǁPooledConnectionProxyǁclose__mutmut_5': xǁPooledConnectionProxyǁclose__mutmut_5, 
        'xǁPooledConnectionProxyǁclose__mutmut_6': xǁPooledConnectionProxyǁclose__mutmut_6, 
        'xǁPooledConnectionProxyǁclose__mutmut_7': xǁPooledConnectionProxyǁclose__mutmut_7, 
        'xǁPooledConnectionProxyǁclose__mutmut_8': xǁPooledConnectionProxyǁclose__mutmut_8, 
        'xǁPooledConnectionProxyǁclose__mutmut_9': xǁPooledConnectionProxyǁclose__mutmut_9, 
        'xǁPooledConnectionProxyǁclose__mutmut_10': xǁPooledConnectionProxyǁclose__mutmut_10, 
        'xǁPooledConnectionProxyǁclose__mutmut_11': xǁPooledConnectionProxyǁclose__mutmut_11
    }
    
    def close(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPooledConnectionProxyǁclose__mutmut_orig"), object.__getattribute__(self, "xǁPooledConnectionProxyǁclose__mutmut_mutants"), args, kwargs, self)
        return result 
    
    close.__signature__ = _mutmut_signature(xǁPooledConnectionProxyǁclose__mutmut_orig)
    xǁPooledConnectionProxyǁclose__mutmut_orig.__name__ = 'xǁPooledConnectionProxyǁclose'


def x__key__mutmut_orig(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, "")
    return (database, pid, tid, sid)


def x__key__mutmut_1(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = None
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, "")
    return (database, pid, tid, sid)


def x__key__mutmut_2(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = None
    sid = os.getenv(_SESSION_ENV, "")
    return (database, pid, tid, sid)


def x__key__mutmut_3(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = None
    return (database, pid, tid, sid)


def x__key__mutmut_4(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(None, "")
    return (database, pid, tid, sid)


def x__key__mutmut_5(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, None)
    return (database, pid, tid, sid)


def x__key__mutmut_6(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv("")
    return (database, pid, tid, sid)


def x__key__mutmut_7(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, )
    return (database, pid, tid, sid)


def x__key__mutmut_8(database: str) -> tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, "XXXX")
    return (database, pid, tid, sid)

x__key__mutmut_mutants : ClassVar[MutantDict] = {
'x__key__mutmut_1': x__key__mutmut_1, 
    'x__key__mutmut_2': x__key__mutmut_2, 
    'x__key__mutmut_3': x__key__mutmut_3, 
    'x__key__mutmut_4': x__key__mutmut_4, 
    'x__key__mutmut_5': x__key__mutmut_5, 
    'x__key__mutmut_6': x__key__mutmut_6, 
    'x__key__mutmut_7': x__key__mutmut_7, 
    'x__key__mutmut_8': x__key__mutmut_8
}

def _key(*args, **kwargs):
    result = _mutmut_trampoline(x__key__mutmut_orig, x__key__mutmut_mutants, args, kwargs)
    return result 

_key.__signature__ = _mutmut_signature(x__key__mutmut_orig)
x__key__mutmut_orig.__name__ = 'x__key'


def x__apply_pragmas__mutmut_orig(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_1(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = None
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_2(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute(None)
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_3(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("XXPRAGMA journal_mode=WAL;XX")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_4(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("pragma journal_mode=wal;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_5(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA JOURNAL_MODE=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_6(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute(None)
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_7(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("XXPRAGMA synchronous=NORMAL;XX")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_8(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("pragma synchronous=normal;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_9(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA SYNCHRONOUS=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_10(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute(None)
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_11(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("XXPRAGMA temp_store=MEMORY;XX")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_12(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("pragma temp_store=memory;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_13(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA TEMP_STORE=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_14(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute(None)
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_15(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("XXPRAGMA mmap_size=30000000000;XX")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_16(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("pragma mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_17(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA MMAP_SIZE=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def x__apply_pragmas__mutmut_18(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception(None, e)


def x__apply_pragmas__mutmut_19(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", None)


def x__apply_pragmas__mutmut_20(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception(e)


def x__apply_pragmas__mutmut_21(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", )


def x__apply_pragmas__mutmut_22(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("XXsqlite PRAGMA failure: %sXX", e)


def x__apply_pragmas__mutmut_23(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite pragma failure: %s", e)


def x__apply_pragmas__mutmut_24(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("SQLITE PRAGMA FAILURE: %S", e)

x__apply_pragmas__mutmut_mutants : ClassVar[MutantDict] = {
'x__apply_pragmas__mutmut_1': x__apply_pragmas__mutmut_1, 
    'x__apply_pragmas__mutmut_2': x__apply_pragmas__mutmut_2, 
    'x__apply_pragmas__mutmut_3': x__apply_pragmas__mutmut_3, 
    'x__apply_pragmas__mutmut_4': x__apply_pragmas__mutmut_4, 
    'x__apply_pragmas__mutmut_5': x__apply_pragmas__mutmut_5, 
    'x__apply_pragmas__mutmut_6': x__apply_pragmas__mutmut_6, 
    'x__apply_pragmas__mutmut_7': x__apply_pragmas__mutmut_7, 
    'x__apply_pragmas__mutmut_8': x__apply_pragmas__mutmut_8, 
    'x__apply_pragmas__mutmut_9': x__apply_pragmas__mutmut_9, 
    'x__apply_pragmas__mutmut_10': x__apply_pragmas__mutmut_10, 
    'x__apply_pragmas__mutmut_11': x__apply_pragmas__mutmut_11, 
    'x__apply_pragmas__mutmut_12': x__apply_pragmas__mutmut_12, 
    'x__apply_pragmas__mutmut_13': x__apply_pragmas__mutmut_13, 
    'x__apply_pragmas__mutmut_14': x__apply_pragmas__mutmut_14, 
    'x__apply_pragmas__mutmut_15': x__apply_pragmas__mutmut_15, 
    'x__apply_pragmas__mutmut_16': x__apply_pragmas__mutmut_16, 
    'x__apply_pragmas__mutmut_17': x__apply_pragmas__mutmut_17, 
    'x__apply_pragmas__mutmut_18': x__apply_pragmas__mutmut_18, 
    'x__apply_pragmas__mutmut_19': x__apply_pragmas__mutmut_19, 
    'x__apply_pragmas__mutmut_20': x__apply_pragmas__mutmut_20, 
    'x__apply_pragmas__mutmut_21': x__apply_pragmas__mutmut_21, 
    'x__apply_pragmas__mutmut_22': x__apply_pragmas__mutmut_22, 
    'x__apply_pragmas__mutmut_23': x__apply_pragmas__mutmut_23, 
    'x__apply_pragmas__mutmut_24': x__apply_pragmas__mutmut_24
}

def _apply_pragmas(*args, **kwargs):
    result = _mutmut_trampoline(x__apply_pragmas__mutmut_orig, x__apply_pragmas__mutmut_mutants, args, kwargs)
    return result 

_apply_pragmas.__signature__ = _mutmut_signature(x__apply_pragmas__mutmut_orig)
x__apply_pragmas__mutmut_orig.__name__ = 'x__apply_pragmas'


def x_pooled_connect__mutmut_orig(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_1(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(None, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_2(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, None) not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_3(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv("0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_4(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, ) not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_5(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "XX0XX") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_6(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_7(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("XX1XX", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_8(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "XXtrueXX", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_9(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "TRUE", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_10(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "XXTRUEXX", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_11(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "true", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_12(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "XXyesXX", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_13(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "YES", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_14(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "XXYESXX"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_15(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "yes"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_16(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(None, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_17(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(*args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_18(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_19(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, )

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_20(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = None
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_21(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(None)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_22(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault(None, False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_23(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", None)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_24(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault(False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_25(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", )

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_26(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("XXcheck_same_threadXX", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_27(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("CHECK_SAME_THREAD", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_28(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", True)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_29(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = None
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_30(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(None)
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_31(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(None))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_32(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = None
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_33(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(None)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_34(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is not None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_35(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = None
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_36(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(None, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_37(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(*args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_38(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_39(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, )
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_40(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(None)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_41(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = None
        return PooledConnectionProxy(conn, k)


def x_pooled_connect__mutmut_42(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(None, k)


def x_pooled_connect__mutmut_43(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, None)


def x_pooled_connect__mutmut_44(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(k)


def x_pooled_connect__mutmut_45(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, )

x_pooled_connect__mutmut_mutants : ClassVar[MutantDict] = {
'x_pooled_connect__mutmut_1': x_pooled_connect__mutmut_1, 
    'x_pooled_connect__mutmut_2': x_pooled_connect__mutmut_2, 
    'x_pooled_connect__mutmut_3': x_pooled_connect__mutmut_3, 
    'x_pooled_connect__mutmut_4': x_pooled_connect__mutmut_4, 
    'x_pooled_connect__mutmut_5': x_pooled_connect__mutmut_5, 
    'x_pooled_connect__mutmut_6': x_pooled_connect__mutmut_6, 
    'x_pooled_connect__mutmut_7': x_pooled_connect__mutmut_7, 
    'x_pooled_connect__mutmut_8': x_pooled_connect__mutmut_8, 
    'x_pooled_connect__mutmut_9': x_pooled_connect__mutmut_9, 
    'x_pooled_connect__mutmut_10': x_pooled_connect__mutmut_10, 
    'x_pooled_connect__mutmut_11': x_pooled_connect__mutmut_11, 
    'x_pooled_connect__mutmut_12': x_pooled_connect__mutmut_12, 
    'x_pooled_connect__mutmut_13': x_pooled_connect__mutmut_13, 
    'x_pooled_connect__mutmut_14': x_pooled_connect__mutmut_14, 
    'x_pooled_connect__mutmut_15': x_pooled_connect__mutmut_15, 
    'x_pooled_connect__mutmut_16': x_pooled_connect__mutmut_16, 
    'x_pooled_connect__mutmut_17': x_pooled_connect__mutmut_17, 
    'x_pooled_connect__mutmut_18': x_pooled_connect__mutmut_18, 
    'x_pooled_connect__mutmut_19': x_pooled_connect__mutmut_19, 
    'x_pooled_connect__mutmut_20': x_pooled_connect__mutmut_20, 
    'x_pooled_connect__mutmut_21': x_pooled_connect__mutmut_21, 
    'x_pooled_connect__mutmut_22': x_pooled_connect__mutmut_22, 
    'x_pooled_connect__mutmut_23': x_pooled_connect__mutmut_23, 
    'x_pooled_connect__mutmut_24': x_pooled_connect__mutmut_24, 
    'x_pooled_connect__mutmut_25': x_pooled_connect__mutmut_25, 
    'x_pooled_connect__mutmut_26': x_pooled_connect__mutmut_26, 
    'x_pooled_connect__mutmut_27': x_pooled_connect__mutmut_27, 
    'x_pooled_connect__mutmut_28': x_pooled_connect__mutmut_28, 
    'x_pooled_connect__mutmut_29': x_pooled_connect__mutmut_29, 
    'x_pooled_connect__mutmut_30': x_pooled_connect__mutmut_30, 
    'x_pooled_connect__mutmut_31': x_pooled_connect__mutmut_31, 
    'x_pooled_connect__mutmut_32': x_pooled_connect__mutmut_32, 
    'x_pooled_connect__mutmut_33': x_pooled_connect__mutmut_33, 
    'x_pooled_connect__mutmut_34': x_pooled_connect__mutmut_34, 
    'x_pooled_connect__mutmut_35': x_pooled_connect__mutmut_35, 
    'x_pooled_connect__mutmut_36': x_pooled_connect__mutmut_36, 
    'x_pooled_connect__mutmut_37': x_pooled_connect__mutmut_37, 
    'x_pooled_connect__mutmut_38': x_pooled_connect__mutmut_38, 
    'x_pooled_connect__mutmut_39': x_pooled_connect__mutmut_39, 
    'x_pooled_connect__mutmut_40': x_pooled_connect__mutmut_40, 
    'x_pooled_connect__mutmut_41': x_pooled_connect__mutmut_41, 
    'x_pooled_connect__mutmut_42': x_pooled_connect__mutmut_42, 
    'x_pooled_connect__mutmut_43': x_pooled_connect__mutmut_43, 
    'x_pooled_connect__mutmut_44': x_pooled_connect__mutmut_44, 
    'x_pooled_connect__mutmut_45': x_pooled_connect__mutmut_45
}

def pooled_connect(*args, **kwargs):
    result = _mutmut_trampoline(x_pooled_connect__mutmut_orig, x_pooled_connect__mutmut_mutants, args, kwargs)
    return result 

pooled_connect.__signature__ = _mutmut_signature(x_pooled_connect__mutmut_orig)
x_pooled_connect__mutmut_orig.__name__ = 'x_pooled_connect'


def x_enable_pooling__mutmut_orig():
    sqlite3.connect = pooled_connect


def x_enable_pooling__mutmut_1():
    sqlite3.connect = None

x_enable_pooling__mutmut_mutants : ClassVar[MutantDict] = {
'x_enable_pooling__mutmut_1': x_enable_pooling__mutmut_1
}

def enable_pooling(*args, **kwargs):
    result = _mutmut_trampoline(x_enable_pooling__mutmut_orig, x_enable_pooling__mutmut_mutants, args, kwargs)
    return result 

enable_pooling.__signature__ = _mutmut_signature(x_enable_pooling__mutmut_orig)
x_enable_pooling__mutmut_orig.__name__ = 'x_enable_pooling'


def x_disable_pooling__mutmut_orig():
    sqlite3.connect = _ORIG_CONNECT


def x_disable_pooling__mutmut_1():
    sqlite3.connect = None

x_disable_pooling__mutmut_mutants : ClassVar[MutantDict] = {
'x_disable_pooling__mutmut_1': x_disable_pooling__mutmut_1
}

def disable_pooling(*args, **kwargs):
    result = _mutmut_trampoline(x_disable_pooling__mutmut_orig, x_disable_pooling__mutmut_mutants, args, kwargs)
    return result 

disable_pooling.__signature__ = _mutmut_signature(x_disable_pooling__mutmut_orig)
x_disable_pooling__mutmut_orig.__name__ = 'x_disable_pooling'


def x_auto_enable_from_env__mutmut_orig():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_1():
    if os.getenv(None, "0") in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_2():
    if os.getenv(_POOL_ENABLED_ENV, None) in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_3():
    if os.getenv("0") in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_4():
    if os.getenv(_POOL_ENABLED_ENV, ) in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_5():
    if os.getenv(_POOL_ENABLED_ENV, "XX0XX") in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_6():
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_7():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("XX1XX", "true", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_8():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "XXtrueXX", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_9():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "TRUE", "TRUE", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_10():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "XXTRUEXX", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_11():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "true", "yes", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_12():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "XXyesXX", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_13():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "YES", "YES"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_14():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "yes", "XXYESXX"):
        enable_pooling()


def x_auto_enable_from_env__mutmut_15():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "yes", "yes"):
        enable_pooling()

x_auto_enable_from_env__mutmut_mutants : ClassVar[MutantDict] = {
'x_auto_enable_from_env__mutmut_1': x_auto_enable_from_env__mutmut_1, 
    'x_auto_enable_from_env__mutmut_2': x_auto_enable_from_env__mutmut_2, 
    'x_auto_enable_from_env__mutmut_3': x_auto_enable_from_env__mutmut_3, 
    'x_auto_enable_from_env__mutmut_4': x_auto_enable_from_env__mutmut_4, 
    'x_auto_enable_from_env__mutmut_5': x_auto_enable_from_env__mutmut_5, 
    'x_auto_enable_from_env__mutmut_6': x_auto_enable_from_env__mutmut_6, 
    'x_auto_enable_from_env__mutmut_7': x_auto_enable_from_env__mutmut_7, 
    'x_auto_enable_from_env__mutmut_8': x_auto_enable_from_env__mutmut_8, 
    'x_auto_enable_from_env__mutmut_9': x_auto_enable_from_env__mutmut_9, 
    'x_auto_enable_from_env__mutmut_10': x_auto_enable_from_env__mutmut_10, 
    'x_auto_enable_from_env__mutmut_11': x_auto_enable_from_env__mutmut_11, 
    'x_auto_enable_from_env__mutmut_12': x_auto_enable_from_env__mutmut_12, 
    'x_auto_enable_from_env__mutmut_13': x_auto_enable_from_env__mutmut_13, 
    'x_auto_enable_from_env__mutmut_14': x_auto_enable_from_env__mutmut_14, 
    'x_auto_enable_from_env__mutmut_15': x_auto_enable_from_env__mutmut_15
}

def auto_enable_from_env(*args, **kwargs):
    result = _mutmut_trampoline(x_auto_enable_from_env__mutmut_orig, x_auto_enable_from_env__mutmut_mutants, args, kwargs)
    return result 

auto_enable_from_env.__signature__ = _mutmut_signature(x_auto_enable_from_env__mutmut_orig)
x_auto_enable_from_env__mutmut_orig.__name__ = 'x_auto_enable_from_env'


@atexit.register
def _close_all():
    """Best-effort cleanup of pooled connections on interpreter shutdown."""

    with _POOL_LOCK:
        for k, conn in list(_CONN_POOL.items()):
            try:
                conn.close()
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)
        _CONN_POOL.clear()
