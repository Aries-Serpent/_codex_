"""AST baseline management for incremental analysis."""
from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Optional

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


def x__safe_json_loads__mutmut_orig(data: str) -> dict:
    """Safely parse JSON, returning empty dict on failure."""
    try:
        return json.loads(data) if data else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def x__safe_json_loads__mutmut_1(data: str) -> dict:
    """Safely parse JSON, returning empty dict on failure."""
    try:
        return json.loads(None) if data else {}
    except (json.JSONDecodeError, TypeError):
        return {}

x__safe_json_loads__mutmut_mutants : ClassVar[MutantDict] = {
'x__safe_json_loads__mutmut_1': x__safe_json_loads__mutmut_1
}

def _safe_json_loads(*args, **kwargs):
    result = _mutmut_trampoline(x__safe_json_loads__mutmut_orig, x__safe_json_loads__mutmut_mutants, args, kwargs)
    return result 

_safe_json_loads.__signature__ = _mutmut_signature(x__safe_json_loads__mutmut_orig)
x__safe_json_loads__mutmut_orig.__name__ = 'x__safe_json_loads'


class BaselineManager:
    """Manages AST baselines in SQLite database.
    
    Provides persistent storage for AST analysis baselines,
    enabling incremental analysis and change detection.
    """

    def xǁBaselineManagerǁ__init____mutmut_orig(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_1(self, db_path: str = "XX.codex/ast_baseline.dbXX"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_2(self, db_path: str = ".CODEX/AST_BASELINE.DB"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_3(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_4(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(None)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_5(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=None, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_6(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=None)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_7(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_8(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, )
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_9(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=False, exist_ok=True)
        self._init_db()

    def xǁBaselineManagerǁ__init____mutmut_10(self, db_path: str = ".codex/ast_baseline.db"):
        """Initialize baseline manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=False)
        self._init_db()
    
    xǁBaselineManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁ__init____mutmut_1': xǁBaselineManagerǁ__init____mutmut_1, 
        'xǁBaselineManagerǁ__init____mutmut_2': xǁBaselineManagerǁ__init____mutmut_2, 
        'xǁBaselineManagerǁ__init____mutmut_3': xǁBaselineManagerǁ__init____mutmut_3, 
        'xǁBaselineManagerǁ__init____mutmut_4': xǁBaselineManagerǁ__init____mutmut_4, 
        'xǁBaselineManagerǁ__init____mutmut_5': xǁBaselineManagerǁ__init____mutmut_5, 
        'xǁBaselineManagerǁ__init____mutmut_6': xǁBaselineManagerǁ__init____mutmut_6, 
        'xǁBaselineManagerǁ__init____mutmut_7': xǁBaselineManagerǁ__init____mutmut_7, 
        'xǁBaselineManagerǁ__init____mutmut_8': xǁBaselineManagerǁ__init____mutmut_8, 
        'xǁBaselineManagerǁ__init____mutmut_9': xǁBaselineManagerǁ__init____mutmut_9, 
        'xǁBaselineManagerǁ__init____mutmut_10': xǁBaselineManagerǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁBaselineManagerǁ__init____mutmut_orig)
    xǁBaselineManagerǁ__init____mutmut_orig.__name__ = 'xǁBaselineManagerǁ__init__'

    def xǁBaselineManagerǁ_init_db__mutmut_orig(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    file_path TEXT PRIMARY KEY,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER
                )
            """)

            conn.commit()
            logger.debug(f"Initialized baseline database: {self.db_path}")

    def xǁBaselineManagerǁ_init_db__mutmut_1(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(None) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    file_path TEXT PRIMARY KEY,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER
                )
            """)

            conn.commit()
            logger.debug(f"Initialized baseline database: {self.db_path}")

    def xǁBaselineManagerǁ_init_db__mutmut_2(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(None)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER
                )
            """)

            conn.commit()
            logger.debug(f"Initialized baseline database: {self.db_path}")

    def xǁBaselineManagerǁ_init_db__mutmut_3(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    file_path TEXT PRIMARY KEY,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute(None)

            conn.commit()
            logger.debug(f"Initialized baseline database: {self.db_path}")

    def xǁBaselineManagerǁ_init_db__mutmut_4(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    file_path TEXT PRIMARY KEY,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    ast_hash TEXT NOT NULL,
                    node_count INTEGER,
                    complexity INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    version INTEGER
                )
            """)

            conn.commit()
            logger.debug(None)
    
    xǁBaselineManagerǁ_init_db__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁ_init_db__mutmut_1': xǁBaselineManagerǁ_init_db__mutmut_1, 
        'xǁBaselineManagerǁ_init_db__mutmut_2': xǁBaselineManagerǁ_init_db__mutmut_2, 
        'xǁBaselineManagerǁ_init_db__mutmut_3': xǁBaselineManagerǁ_init_db__mutmut_3, 
        'xǁBaselineManagerǁ_init_db__mutmut_4': xǁBaselineManagerǁ_init_db__mutmut_4
    }
    
    def _init_db(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁ_init_db__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁ_init_db__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _init_db.__signature__ = _mutmut_signature(xǁBaselineManagerǁ_init_db__mutmut_orig)
    xǁBaselineManagerǁ_init_db__mutmut_orig.__name__ = 'xǁBaselineManagerǁ_init_db'

    def xǁBaselineManagerǁsave_baseline__mutmut_orig(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_1(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(None) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_2(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = None

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_3(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                None, (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_4(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", None
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_5(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_6(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_7(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "XXSELECT version FROM baselines WHERE file_path = ?XX", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_8(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "select version from baselines where file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_9(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT VERSION FROM BASELINES WHERE FILE_PATH = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_10(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = None

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_11(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] - 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_12(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[1] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_13(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 2) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_14(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 2

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_15(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    None,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_16(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    None,
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_17(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_18(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_19(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                None,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_20(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                None,
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_21(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_22(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_23(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(None),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_24(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata and {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(f"Saved baseline for {file_path} (version {version})")

    def xǁBaselineManagerǁsave_baseline__mutmut_25(
        self,
        file_path: str,
        ast_hash: str,
        node_count: int,
        complexity: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """Save or update baseline for a file.

        Args:
            file_path: Path to source file
            ast_hash: Hash of AST structure
            node_count: Number of AST nodes
            complexity: Cyclomatic complexity
            metadata: Additional metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get current version
            row = conn.execute(
                "SELECT version FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            version = (row[0] + 1) if row else 1

            # Archive old version
            if row:
                conn.execute(
                    """
                    INSERT INTO baseline_history 
                    (file_path, ast_hash, node_count, complexity, timestamp, metadata, version)
                    SELECT file_path, ast_hash, node_count, complexity, timestamp, metadata, version 
                    FROM baselines WHERE file_path = ?
                """,
                    (file_path,),
                )

            # Insert or replace current baseline
            conn.execute(
                """
                INSERT OR REPLACE INTO baselines 
                (file_path, ast_hash, node_count, complexity, metadata, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    file_path,
                    ast_hash,
                    node_count,
                    complexity,
                    json.dumps(metadata or {}),
                    version,
                ),
            )

            conn.commit()
            logger.debug(None)
    
    xǁBaselineManagerǁsave_baseline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁsave_baseline__mutmut_1': xǁBaselineManagerǁsave_baseline__mutmut_1, 
        'xǁBaselineManagerǁsave_baseline__mutmut_2': xǁBaselineManagerǁsave_baseline__mutmut_2, 
        'xǁBaselineManagerǁsave_baseline__mutmut_3': xǁBaselineManagerǁsave_baseline__mutmut_3, 
        'xǁBaselineManagerǁsave_baseline__mutmut_4': xǁBaselineManagerǁsave_baseline__mutmut_4, 
        'xǁBaselineManagerǁsave_baseline__mutmut_5': xǁBaselineManagerǁsave_baseline__mutmut_5, 
        'xǁBaselineManagerǁsave_baseline__mutmut_6': xǁBaselineManagerǁsave_baseline__mutmut_6, 
        'xǁBaselineManagerǁsave_baseline__mutmut_7': xǁBaselineManagerǁsave_baseline__mutmut_7, 
        'xǁBaselineManagerǁsave_baseline__mutmut_8': xǁBaselineManagerǁsave_baseline__mutmut_8, 
        'xǁBaselineManagerǁsave_baseline__mutmut_9': xǁBaselineManagerǁsave_baseline__mutmut_9, 
        'xǁBaselineManagerǁsave_baseline__mutmut_10': xǁBaselineManagerǁsave_baseline__mutmut_10, 
        'xǁBaselineManagerǁsave_baseline__mutmut_11': xǁBaselineManagerǁsave_baseline__mutmut_11, 
        'xǁBaselineManagerǁsave_baseline__mutmut_12': xǁBaselineManagerǁsave_baseline__mutmut_12, 
        'xǁBaselineManagerǁsave_baseline__mutmut_13': xǁBaselineManagerǁsave_baseline__mutmut_13, 
        'xǁBaselineManagerǁsave_baseline__mutmut_14': xǁBaselineManagerǁsave_baseline__mutmut_14, 
        'xǁBaselineManagerǁsave_baseline__mutmut_15': xǁBaselineManagerǁsave_baseline__mutmut_15, 
        'xǁBaselineManagerǁsave_baseline__mutmut_16': xǁBaselineManagerǁsave_baseline__mutmut_16, 
        'xǁBaselineManagerǁsave_baseline__mutmut_17': xǁBaselineManagerǁsave_baseline__mutmut_17, 
        'xǁBaselineManagerǁsave_baseline__mutmut_18': xǁBaselineManagerǁsave_baseline__mutmut_18, 
        'xǁBaselineManagerǁsave_baseline__mutmut_19': xǁBaselineManagerǁsave_baseline__mutmut_19, 
        'xǁBaselineManagerǁsave_baseline__mutmut_20': xǁBaselineManagerǁsave_baseline__mutmut_20, 
        'xǁBaselineManagerǁsave_baseline__mutmut_21': xǁBaselineManagerǁsave_baseline__mutmut_21, 
        'xǁBaselineManagerǁsave_baseline__mutmut_22': xǁBaselineManagerǁsave_baseline__mutmut_22, 
        'xǁBaselineManagerǁsave_baseline__mutmut_23': xǁBaselineManagerǁsave_baseline__mutmut_23, 
        'xǁBaselineManagerǁsave_baseline__mutmut_24': xǁBaselineManagerǁsave_baseline__mutmut_24, 
        'xǁBaselineManagerǁsave_baseline__mutmut_25': xǁBaselineManagerǁsave_baseline__mutmut_25
    }
    
    def save_baseline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁsave_baseline__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁsave_baseline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    save_baseline.__signature__ = _mutmut_signature(xǁBaselineManagerǁsave_baseline__mutmut_orig)
    xǁBaselineManagerǁsave_baseline__mutmut_orig.__name__ = 'xǁBaselineManagerǁsave_baseline'

    def xǁBaselineManagerǁget_baseline__mutmut_orig(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_1(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(None) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_2(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = None

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_3(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                None, (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_4(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", None
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_5(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_6(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_7(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "XXSELECT * FROM baselines WHERE file_path = ?XX", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_8(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "select * from baselines where file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_9(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM BASELINES WHERE FILE_PATH = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_10(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "XXfile_pathXX": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_11(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "FILE_PATH": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_12(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[1],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_13(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "XXast_hashXX": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_14(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "AST_HASH": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_15(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[2],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_16(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "XXnode_countXX": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_17(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "NODE_COUNT": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_18(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[3],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_19(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "XXcomplexityXX": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_20(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "COMPLEXITY": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_21(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[4],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_22(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "XXtimestampXX": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_23(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "TIMESTAMP": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_24(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[5],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_25(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "XXmetadataXX": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_26(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "METADATA": _safe_json_loads(row[5]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_27(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(None),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_28(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[6]),
                    "version": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_29(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "XXversionXX": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_30(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "VERSION": row[6],
                }
        return None

    def xǁBaselineManagerǁget_baseline__mutmut_31(self, file_path: str) -> Optional[dict]:
        """Retrieve baseline for a file.

        Args:
            file_path: Path to source file

        Returns:
            Baseline data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM baselines WHERE file_path = ?", (file_path,)
            ).fetchone()

            if row:
                return {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[7],
                }
        return None
    
    xǁBaselineManagerǁget_baseline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁget_baseline__mutmut_1': xǁBaselineManagerǁget_baseline__mutmut_1, 
        'xǁBaselineManagerǁget_baseline__mutmut_2': xǁBaselineManagerǁget_baseline__mutmut_2, 
        'xǁBaselineManagerǁget_baseline__mutmut_3': xǁBaselineManagerǁget_baseline__mutmut_3, 
        'xǁBaselineManagerǁget_baseline__mutmut_4': xǁBaselineManagerǁget_baseline__mutmut_4, 
        'xǁBaselineManagerǁget_baseline__mutmut_5': xǁBaselineManagerǁget_baseline__mutmut_5, 
        'xǁBaselineManagerǁget_baseline__mutmut_6': xǁBaselineManagerǁget_baseline__mutmut_6, 
        'xǁBaselineManagerǁget_baseline__mutmut_7': xǁBaselineManagerǁget_baseline__mutmut_7, 
        'xǁBaselineManagerǁget_baseline__mutmut_8': xǁBaselineManagerǁget_baseline__mutmut_8, 
        'xǁBaselineManagerǁget_baseline__mutmut_9': xǁBaselineManagerǁget_baseline__mutmut_9, 
        'xǁBaselineManagerǁget_baseline__mutmut_10': xǁBaselineManagerǁget_baseline__mutmut_10, 
        'xǁBaselineManagerǁget_baseline__mutmut_11': xǁBaselineManagerǁget_baseline__mutmut_11, 
        'xǁBaselineManagerǁget_baseline__mutmut_12': xǁBaselineManagerǁget_baseline__mutmut_12, 
        'xǁBaselineManagerǁget_baseline__mutmut_13': xǁBaselineManagerǁget_baseline__mutmut_13, 
        'xǁBaselineManagerǁget_baseline__mutmut_14': xǁBaselineManagerǁget_baseline__mutmut_14, 
        'xǁBaselineManagerǁget_baseline__mutmut_15': xǁBaselineManagerǁget_baseline__mutmut_15, 
        'xǁBaselineManagerǁget_baseline__mutmut_16': xǁBaselineManagerǁget_baseline__mutmut_16, 
        'xǁBaselineManagerǁget_baseline__mutmut_17': xǁBaselineManagerǁget_baseline__mutmut_17, 
        'xǁBaselineManagerǁget_baseline__mutmut_18': xǁBaselineManagerǁget_baseline__mutmut_18, 
        'xǁBaselineManagerǁget_baseline__mutmut_19': xǁBaselineManagerǁget_baseline__mutmut_19, 
        'xǁBaselineManagerǁget_baseline__mutmut_20': xǁBaselineManagerǁget_baseline__mutmut_20, 
        'xǁBaselineManagerǁget_baseline__mutmut_21': xǁBaselineManagerǁget_baseline__mutmut_21, 
        'xǁBaselineManagerǁget_baseline__mutmut_22': xǁBaselineManagerǁget_baseline__mutmut_22, 
        'xǁBaselineManagerǁget_baseline__mutmut_23': xǁBaselineManagerǁget_baseline__mutmut_23, 
        'xǁBaselineManagerǁget_baseline__mutmut_24': xǁBaselineManagerǁget_baseline__mutmut_24, 
        'xǁBaselineManagerǁget_baseline__mutmut_25': xǁBaselineManagerǁget_baseline__mutmut_25, 
        'xǁBaselineManagerǁget_baseline__mutmut_26': xǁBaselineManagerǁget_baseline__mutmut_26, 
        'xǁBaselineManagerǁget_baseline__mutmut_27': xǁBaselineManagerǁget_baseline__mutmut_27, 
        'xǁBaselineManagerǁget_baseline__mutmut_28': xǁBaselineManagerǁget_baseline__mutmut_28, 
        'xǁBaselineManagerǁget_baseline__mutmut_29': xǁBaselineManagerǁget_baseline__mutmut_29, 
        'xǁBaselineManagerǁget_baseline__mutmut_30': xǁBaselineManagerǁget_baseline__mutmut_30, 
        'xǁBaselineManagerǁget_baseline__mutmut_31': xǁBaselineManagerǁget_baseline__mutmut_31
    }
    
    def get_baseline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁget_baseline__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁget_baseline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_baseline.__signature__ = _mutmut_signature(xǁBaselineManagerǁget_baseline__mutmut_orig)
    xǁBaselineManagerǁget_baseline__mutmut_orig.__name__ = 'xǁBaselineManagerǁget_baseline'

    def xǁBaselineManagerǁlist_baselines__mutmut_orig(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_1(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(None) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_2(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = None
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_3(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                None
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_4(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "XXSELECT * FROM baselines ORDER BY file_pathXX"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_5(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "select * from baselines order by file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_6(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM BASELINES ORDER BY FILE_PATH"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_7(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "XXfile_pathXX": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_8(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "FILE_PATH": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_9(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[1],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_10(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "XXast_hashXX": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_11(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "AST_HASH": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_12(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[2],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_13(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "XXnode_countXX": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_14(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "NODE_COUNT": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_15(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[3],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_16(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "XXcomplexityXX": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_17(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "COMPLEXITY": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_18(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[4],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_19(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "XXtimestampXX": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_20(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "TIMESTAMP": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_21(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[5],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_22(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "XXmetadataXX": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_23(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "METADATA": _safe_json_loads(row[5]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_24(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(None),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_25(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[6]),
                    "version": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_26(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "XXversionXX": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_27(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "VERSION": row[6],
                }
                for row in rows
            ]

    def xǁBaselineManagerǁlist_baselines__mutmut_28(self) -> list[dict]:
        """Get all baselines.

        Returns:
            list of baseline records
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM baselines ORDER BY file_path"
            ).fetchall()
            return [
                {
                    "file_path": row[0],
                    "ast_hash": row[1],
                    "node_count": row[2],
                    "complexity": row[3],
                    "timestamp": row[4],
                    "metadata": _safe_json_loads(row[5]),
                    "version": row[7],
                }
                for row in rows
            ]
    
    xǁBaselineManagerǁlist_baselines__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁlist_baselines__mutmut_1': xǁBaselineManagerǁlist_baselines__mutmut_1, 
        'xǁBaselineManagerǁlist_baselines__mutmut_2': xǁBaselineManagerǁlist_baselines__mutmut_2, 
        'xǁBaselineManagerǁlist_baselines__mutmut_3': xǁBaselineManagerǁlist_baselines__mutmut_3, 
        'xǁBaselineManagerǁlist_baselines__mutmut_4': xǁBaselineManagerǁlist_baselines__mutmut_4, 
        'xǁBaselineManagerǁlist_baselines__mutmut_5': xǁBaselineManagerǁlist_baselines__mutmut_5, 
        'xǁBaselineManagerǁlist_baselines__mutmut_6': xǁBaselineManagerǁlist_baselines__mutmut_6, 
        'xǁBaselineManagerǁlist_baselines__mutmut_7': xǁBaselineManagerǁlist_baselines__mutmut_7, 
        'xǁBaselineManagerǁlist_baselines__mutmut_8': xǁBaselineManagerǁlist_baselines__mutmut_8, 
        'xǁBaselineManagerǁlist_baselines__mutmut_9': xǁBaselineManagerǁlist_baselines__mutmut_9, 
        'xǁBaselineManagerǁlist_baselines__mutmut_10': xǁBaselineManagerǁlist_baselines__mutmut_10, 
        'xǁBaselineManagerǁlist_baselines__mutmut_11': xǁBaselineManagerǁlist_baselines__mutmut_11, 
        'xǁBaselineManagerǁlist_baselines__mutmut_12': xǁBaselineManagerǁlist_baselines__mutmut_12, 
        'xǁBaselineManagerǁlist_baselines__mutmut_13': xǁBaselineManagerǁlist_baselines__mutmut_13, 
        'xǁBaselineManagerǁlist_baselines__mutmut_14': xǁBaselineManagerǁlist_baselines__mutmut_14, 
        'xǁBaselineManagerǁlist_baselines__mutmut_15': xǁBaselineManagerǁlist_baselines__mutmut_15, 
        'xǁBaselineManagerǁlist_baselines__mutmut_16': xǁBaselineManagerǁlist_baselines__mutmut_16, 
        'xǁBaselineManagerǁlist_baselines__mutmut_17': xǁBaselineManagerǁlist_baselines__mutmut_17, 
        'xǁBaselineManagerǁlist_baselines__mutmut_18': xǁBaselineManagerǁlist_baselines__mutmut_18, 
        'xǁBaselineManagerǁlist_baselines__mutmut_19': xǁBaselineManagerǁlist_baselines__mutmut_19, 
        'xǁBaselineManagerǁlist_baselines__mutmut_20': xǁBaselineManagerǁlist_baselines__mutmut_20, 
        'xǁBaselineManagerǁlist_baselines__mutmut_21': xǁBaselineManagerǁlist_baselines__mutmut_21, 
        'xǁBaselineManagerǁlist_baselines__mutmut_22': xǁBaselineManagerǁlist_baselines__mutmut_22, 
        'xǁBaselineManagerǁlist_baselines__mutmut_23': xǁBaselineManagerǁlist_baselines__mutmut_23, 
        'xǁBaselineManagerǁlist_baselines__mutmut_24': xǁBaselineManagerǁlist_baselines__mutmut_24, 
        'xǁBaselineManagerǁlist_baselines__mutmut_25': xǁBaselineManagerǁlist_baselines__mutmut_25, 
        'xǁBaselineManagerǁlist_baselines__mutmut_26': xǁBaselineManagerǁlist_baselines__mutmut_26, 
        'xǁBaselineManagerǁlist_baselines__mutmut_27': xǁBaselineManagerǁlist_baselines__mutmut_27, 
        'xǁBaselineManagerǁlist_baselines__mutmut_28': xǁBaselineManagerǁlist_baselines__mutmut_28
    }
    
    def list_baselines(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁlist_baselines__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁlist_baselines__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_baselines.__signature__ = _mutmut_signature(xǁBaselineManagerǁlist_baselines__mutmut_orig)
    xǁBaselineManagerǁlist_baselines__mutmut_orig.__name__ = 'xǁBaselineManagerǁlist_baselines'

    def xǁBaselineManagerǁdelete_baseline__mutmut_orig(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_1(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(None) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_2(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(None, (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_3(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", None)
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_4(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute((file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_5(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", )
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_6(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("XXDELETE FROM baselines WHERE file_path = ?XX", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_7(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("delete from baselines where file_path = ?", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_8(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM BASELINES WHERE FILE_PATH = ?", (file_path,))
            conn.commit()
            logger.debug(f"Deleted baseline for {file_path}")

    def xǁBaselineManagerǁdelete_baseline__mutmut_9(self, file_path: str) -> None:
        """Delete baseline for a file.

        Args:
            file_path: Path to source file
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines WHERE file_path = ?", (file_path,))
            conn.commit()
            logger.debug(None)
    
    xǁBaselineManagerǁdelete_baseline__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁdelete_baseline__mutmut_1': xǁBaselineManagerǁdelete_baseline__mutmut_1, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_2': xǁBaselineManagerǁdelete_baseline__mutmut_2, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_3': xǁBaselineManagerǁdelete_baseline__mutmut_3, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_4': xǁBaselineManagerǁdelete_baseline__mutmut_4, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_5': xǁBaselineManagerǁdelete_baseline__mutmut_5, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_6': xǁBaselineManagerǁdelete_baseline__mutmut_6, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_7': xǁBaselineManagerǁdelete_baseline__mutmut_7, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_8': xǁBaselineManagerǁdelete_baseline__mutmut_8, 
        'xǁBaselineManagerǁdelete_baseline__mutmut_9': xǁBaselineManagerǁdelete_baseline__mutmut_9
    }
    
    def delete_baseline(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁdelete_baseline__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁdelete_baseline__mutmut_mutants"), args, kwargs, self)
        return result 
    
    delete_baseline.__signature__ = _mutmut_signature(xǁBaselineManagerǁdelete_baseline__mutmut_orig)
    xǁBaselineManagerǁdelete_baseline__mutmut_orig.__name__ = 'xǁBaselineManagerǁdelete_baseline'

    def xǁBaselineManagerǁclear_all__mutmut_orig(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_1(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(None) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_2(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(None)
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_3(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("XXDELETE FROM baselinesXX")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_4(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("delete from baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_5(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM BASELINES")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_6(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute(None)
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_7(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("XXDELETE FROM baseline_historyXX")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_8(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("delete from baseline_history")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_9(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM BASELINE_HISTORY")
            conn.commit()
            logger.info("Cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_10(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info(None)

    def xǁBaselineManagerǁclear_all__mutmut_11(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("XXCleared all baselinesXX")

    def xǁBaselineManagerǁclear_all__mutmut_12(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("cleared all baselines")

    def xǁBaselineManagerǁclear_all__mutmut_13(self) -> None:
        """Clear all baselines."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM baselines")
            conn.execute("DELETE FROM baseline_history")
            conn.commit()
            logger.info("CLEARED ALL BASELINES")
    
    xǁBaselineManagerǁclear_all__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁBaselineManagerǁclear_all__mutmut_1': xǁBaselineManagerǁclear_all__mutmut_1, 
        'xǁBaselineManagerǁclear_all__mutmut_2': xǁBaselineManagerǁclear_all__mutmut_2, 
        'xǁBaselineManagerǁclear_all__mutmut_3': xǁBaselineManagerǁclear_all__mutmut_3, 
        'xǁBaselineManagerǁclear_all__mutmut_4': xǁBaselineManagerǁclear_all__mutmut_4, 
        'xǁBaselineManagerǁclear_all__mutmut_5': xǁBaselineManagerǁclear_all__mutmut_5, 
        'xǁBaselineManagerǁclear_all__mutmut_6': xǁBaselineManagerǁclear_all__mutmut_6, 
        'xǁBaselineManagerǁclear_all__mutmut_7': xǁBaselineManagerǁclear_all__mutmut_7, 
        'xǁBaselineManagerǁclear_all__mutmut_8': xǁBaselineManagerǁclear_all__mutmut_8, 
        'xǁBaselineManagerǁclear_all__mutmut_9': xǁBaselineManagerǁclear_all__mutmut_9, 
        'xǁBaselineManagerǁclear_all__mutmut_10': xǁBaselineManagerǁclear_all__mutmut_10, 
        'xǁBaselineManagerǁclear_all__mutmut_11': xǁBaselineManagerǁclear_all__mutmut_11, 
        'xǁBaselineManagerǁclear_all__mutmut_12': xǁBaselineManagerǁclear_all__mutmut_12, 
        'xǁBaselineManagerǁclear_all__mutmut_13': xǁBaselineManagerǁclear_all__mutmut_13
    }
    
    def clear_all(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁBaselineManagerǁclear_all__mutmut_orig"), object.__getattribute__(self, "xǁBaselineManagerǁclear_all__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_all.__signature__ = _mutmut_signature(xǁBaselineManagerǁclear_all__mutmut_orig)
    xǁBaselineManagerǁclear_all__mutmut_orig.__name__ = 'xǁBaselineManagerǁclear_all'


__all__ = ["BaselineManager"]
