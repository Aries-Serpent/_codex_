"""
Metric Storage Module

Provides dual storage (JSON + SQLite) for duplication metrics with
historical tracking and query capabilities.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Optional

from .duplication import DuplicationRatio

logger = logging.getLogger(__name__)

# Default storage locations
DEFAULT_JSON_DIR = Path(".codex/metrics/json")
DEFAULT_SQLITE_PATH = Path(".codex/metrics/duplication.db")
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


class MetricStorage:
    """Dual storage backend for duplication metrics"""

    def xǁMetricStorageǁ__init____mutmut_orig(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_1(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = False,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_2(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = False,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_3(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = None
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_4(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir and DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_5(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = None
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_6(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path and DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_7(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = None
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_8(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = None

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_9(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=None, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_10(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=None)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_11(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_12(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, )

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_13(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=False, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_14(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=False)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_15(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=None, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_16(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=None)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_17(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_18(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, )
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_19(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=False, exist_ok=True)
            self._init_database()

    def xǁMetricStorageǁ__init____mutmut_20(
        self,
        json_dir: Optional[Path] = None,
        sqlite_path: Optional[Path] = None,
        enable_json: bool = True,
        enable_sqlite: bool = True,
    ):
        """
        Initialize metric storage

        Args:
            json_dir: Directory for JSON files (default: .codex/metrics/json)
            sqlite_path: Path to SQLite database (default: .codex/metrics/duplication.db)
            enable_json: Whether to enable JSON storage
            enable_sqlite: Whether to enable SQLite storage
        """
        self.json_dir = json_dir or DEFAULT_JSON_DIR
        self.sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
        self.enable_json = enable_json
        self.enable_sqlite = enable_sqlite

        if self.enable_json:
            self.json_dir.mkdir(parents=True, exist_ok=True)

        if self.enable_sqlite:
            self.sqlite_path.parent.mkdir(parents=True, exist_ok=False)
            self._init_database()
    
    xǁMetricStorageǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁ__init____mutmut_1': xǁMetricStorageǁ__init____mutmut_1, 
        'xǁMetricStorageǁ__init____mutmut_2': xǁMetricStorageǁ__init____mutmut_2, 
        'xǁMetricStorageǁ__init____mutmut_3': xǁMetricStorageǁ__init____mutmut_3, 
        'xǁMetricStorageǁ__init____mutmut_4': xǁMetricStorageǁ__init____mutmut_4, 
        'xǁMetricStorageǁ__init____mutmut_5': xǁMetricStorageǁ__init____mutmut_5, 
        'xǁMetricStorageǁ__init____mutmut_6': xǁMetricStorageǁ__init____mutmut_6, 
        'xǁMetricStorageǁ__init____mutmut_7': xǁMetricStorageǁ__init____mutmut_7, 
        'xǁMetricStorageǁ__init____mutmut_8': xǁMetricStorageǁ__init____mutmut_8, 
        'xǁMetricStorageǁ__init____mutmut_9': xǁMetricStorageǁ__init____mutmut_9, 
        'xǁMetricStorageǁ__init____mutmut_10': xǁMetricStorageǁ__init____mutmut_10, 
        'xǁMetricStorageǁ__init____mutmut_11': xǁMetricStorageǁ__init____mutmut_11, 
        'xǁMetricStorageǁ__init____mutmut_12': xǁMetricStorageǁ__init____mutmut_12, 
        'xǁMetricStorageǁ__init____mutmut_13': xǁMetricStorageǁ__init____mutmut_13, 
        'xǁMetricStorageǁ__init____mutmut_14': xǁMetricStorageǁ__init____mutmut_14, 
        'xǁMetricStorageǁ__init____mutmut_15': xǁMetricStorageǁ__init____mutmut_15, 
        'xǁMetricStorageǁ__init____mutmut_16': xǁMetricStorageǁ__init____mutmut_16, 
        'xǁMetricStorageǁ__init____mutmut_17': xǁMetricStorageǁ__init____mutmut_17, 
        'xǁMetricStorageǁ__init____mutmut_18': xǁMetricStorageǁ__init____mutmut_18, 
        'xǁMetricStorageǁ__init____mutmut_19': xǁMetricStorageǁ__init____mutmut_19, 
        'xǁMetricStorageǁ__init____mutmut_20': xǁMetricStorageǁ__init____mutmut_20
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMetricStorageǁ__init____mutmut_orig)
    xǁMetricStorageǁ__init____mutmut_orig.__name__ = 'xǁMetricStorageǁ__init__'

    def xǁMetricStorageǁ_init_database__mutmut_orig(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_1(self):
        """Initialize SQLite database schema"""
        conn = None
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_2(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(None)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_3(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = None

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_4(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                None
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_5(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                None
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_6(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                None
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_7(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                None
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_8(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                None
            )

            conn.commit()
            logger.info(f"Initialized SQLite database at {self.sqlite_path}")

        finally:
            conn.close()

    def xǁMetricStorageǁ_init_database__mutmut_9(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Metrics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    commit_sha TEXT,
                    ratio REAL NOT NULL,
                    total_lines INTEGER NOT NULL,
                    duplicate_lines INTEGER NOT NULL,
                    files_scanned INTEGER,
                    files_with_duplicates INTEGER
                )
            """
            )

            # Duplicate blocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS duplicate_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    severity TEXT,
                    clone_type TEXT,
                    num_occurrences INTEGER,
                    FOREIGN KEY (metric_id) REFERENCES metrics(id)
                )
            """
            )

            # Occurrences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS occurrences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES duplicate_blocks(id)
                )
            """
            )

            # Create indexes for common queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics(timestamp)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_blocks_metric
                ON duplicate_blocks(metric_id)
            """
            )

            conn.commit()
            logger.info(None)

        finally:
            conn.close()
    
    xǁMetricStorageǁ_init_database__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁ_init_database__mutmut_1': xǁMetricStorageǁ_init_database__mutmut_1, 
        'xǁMetricStorageǁ_init_database__mutmut_2': xǁMetricStorageǁ_init_database__mutmut_2, 
        'xǁMetricStorageǁ_init_database__mutmut_3': xǁMetricStorageǁ_init_database__mutmut_3, 
        'xǁMetricStorageǁ_init_database__mutmut_4': xǁMetricStorageǁ_init_database__mutmut_4, 
        'xǁMetricStorageǁ_init_database__mutmut_5': xǁMetricStorageǁ_init_database__mutmut_5, 
        'xǁMetricStorageǁ_init_database__mutmut_6': xǁMetricStorageǁ_init_database__mutmut_6, 
        'xǁMetricStorageǁ_init_database__mutmut_7': xǁMetricStorageǁ_init_database__mutmut_7, 
        'xǁMetricStorageǁ_init_database__mutmut_8': xǁMetricStorageǁ_init_database__mutmut_8, 
        'xǁMetricStorageǁ_init_database__mutmut_9': xǁMetricStorageǁ_init_database__mutmut_9
    }
    
    def _init_database(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁ_init_database__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁ_init_database__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _init_database.__signature__ = _mutmut_signature(xǁMetricStorageǁ_init_database__mutmut_orig)
    xǁMetricStorageǁ_init_database__mutmut_orig.__name__ = 'xǁMetricStorageǁ_init_database'

    def xǁMetricStorageǁsave__mutmut_orig(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_1(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = None

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_2(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp and datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_3(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(None).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_4(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = None

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_5(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = None
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_6(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(None, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_7(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, None, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_8(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, None)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_9(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_10(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_11(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, )
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_12(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = None

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_13(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["XXjson_pathXX"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_14(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["JSON_PATH"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_15(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(None)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_16(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = None
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_17(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(None, commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_18(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, None, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_19(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, None)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_20(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(commit_sha, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_21(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, timestamp)
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_22(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, )
            result["sqlite_id"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_23(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["sqlite_id"] = None

        return result

    def xǁMetricStorageǁsave__mutmut_24(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["XXsqlite_idXX"] = metric_id

        return result

    def xǁMetricStorageǁsave__mutmut_25(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Save duplication metrics to storage

        Args:
            ratio: DuplicationRatio object to save
            commit_sha: Optional git commit SHA
            timestamp: Optional timestamp (ISO format, defaults to now)

        Returns:
            Dictionary with saved file paths/IDs
        """
        timestamp = timestamp or datetime.now(UTC).isoformat()

        result = {}

        if self.enable_json:
            json_path = self._save_json(ratio, commit_sha, timestamp)
            result["json_path"] = str(json_path)

        if self.enable_sqlite:
            metric_id = self._save_sqlite(ratio, commit_sha, timestamp)
            result["SQLITE_ID"] = metric_id

        return result
    
    xǁMetricStorageǁsave__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁsave__mutmut_1': xǁMetricStorageǁsave__mutmut_1, 
        'xǁMetricStorageǁsave__mutmut_2': xǁMetricStorageǁsave__mutmut_2, 
        'xǁMetricStorageǁsave__mutmut_3': xǁMetricStorageǁsave__mutmut_3, 
        'xǁMetricStorageǁsave__mutmut_4': xǁMetricStorageǁsave__mutmut_4, 
        'xǁMetricStorageǁsave__mutmut_5': xǁMetricStorageǁsave__mutmut_5, 
        'xǁMetricStorageǁsave__mutmut_6': xǁMetricStorageǁsave__mutmut_6, 
        'xǁMetricStorageǁsave__mutmut_7': xǁMetricStorageǁsave__mutmut_7, 
        'xǁMetricStorageǁsave__mutmut_8': xǁMetricStorageǁsave__mutmut_8, 
        'xǁMetricStorageǁsave__mutmut_9': xǁMetricStorageǁsave__mutmut_9, 
        'xǁMetricStorageǁsave__mutmut_10': xǁMetricStorageǁsave__mutmut_10, 
        'xǁMetricStorageǁsave__mutmut_11': xǁMetricStorageǁsave__mutmut_11, 
        'xǁMetricStorageǁsave__mutmut_12': xǁMetricStorageǁsave__mutmut_12, 
        'xǁMetricStorageǁsave__mutmut_13': xǁMetricStorageǁsave__mutmut_13, 
        'xǁMetricStorageǁsave__mutmut_14': xǁMetricStorageǁsave__mutmut_14, 
        'xǁMetricStorageǁsave__mutmut_15': xǁMetricStorageǁsave__mutmut_15, 
        'xǁMetricStorageǁsave__mutmut_16': xǁMetricStorageǁsave__mutmut_16, 
        'xǁMetricStorageǁsave__mutmut_17': xǁMetricStorageǁsave__mutmut_17, 
        'xǁMetricStorageǁsave__mutmut_18': xǁMetricStorageǁsave__mutmut_18, 
        'xǁMetricStorageǁsave__mutmut_19': xǁMetricStorageǁsave__mutmut_19, 
        'xǁMetricStorageǁsave__mutmut_20': xǁMetricStorageǁsave__mutmut_20, 
        'xǁMetricStorageǁsave__mutmut_21': xǁMetricStorageǁsave__mutmut_21, 
        'xǁMetricStorageǁsave__mutmut_22': xǁMetricStorageǁsave__mutmut_22, 
        'xǁMetricStorageǁsave__mutmut_23': xǁMetricStorageǁsave__mutmut_23, 
        'xǁMetricStorageǁsave__mutmut_24': xǁMetricStorageǁsave__mutmut_24, 
        'xǁMetricStorageǁsave__mutmut_25': xǁMetricStorageǁsave__mutmut_25
    }
    
    def save(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁsave__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁsave__mutmut_mutants"), args, kwargs, self)
        return result 
    
    save.__signature__ = _mutmut_signature(xǁMetricStorageǁsave__mutmut_orig)
    xǁMetricStorageǁsave__mutmut_orig.__name__ = 'xǁMetricStorageǁsave'

    def xǁMetricStorageǁ_save_json__mutmut_orig(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_1(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = None
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_2(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(None, "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_3(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", None)
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_4(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace("-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_5(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", )
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_6(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(None, "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_7(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", None).replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_8(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace("-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_9(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", ).replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_10(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace("XX:XX", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_11(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "XX-XX").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_12(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace("XX.XX", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_13(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "XX-XX")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_14(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = None
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_15(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = None

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_16(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir * filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_17(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = None

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_18(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "XXtimestampXX": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_19(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "TIMESTAMP": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_20(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "XXcommit_shaXX": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_21(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "COMMIT_SHA": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_22(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "XXduplication_ratioXX": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_23(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "DUPLICATION_RATIO": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_24(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "XXtotal_linesXX": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_25(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "TOTAL_LINES": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_26(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "XXduplicate_linesXX": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_27(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "DUPLICATE_LINES": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_28(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "XXfiles_scannedXX": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_29(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "FILES_SCANNED": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_30(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "XXfiles_with_duplicatesXX": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_31(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "FILES_WITH_DUPLICATES": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_32(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "XXduplicate_blocksXX": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_33(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "DUPLICATE_BLOCKS": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_34(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "XXsummaryXX": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_35(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "SUMMARY": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_36(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "XXnum_blocksXX": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_37(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "NUM_BLOCKS": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_38(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "XXavg_block_sizeXX": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_39(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "AVG_BLOCK_SIZE": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_40(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks) * len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_41(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(None)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_42(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] - 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_43(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] + b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_44(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[2] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_45(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[1] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_46(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 2 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_47(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 1
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_48(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(None, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_49(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, None) as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_50(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open("w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_51(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, ) as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_52(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "XXwXX") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_53(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "W") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_54(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(None, f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_55(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, None, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_56(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=None)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_57(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(f, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_58(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, indent=2)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_59(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, )

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_60(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=3)

        logger.info(f"Saved JSON metrics to {filepath}")
        return filepath

    def xǁMetricStorageǁ_save_json__mutmut_61(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> Path:
        """Save metrics to JSON file"""
        # Create filename from timestamp
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        filename = f"duplication_{safe_timestamp}.json"
        filepath = self.json_dir / filename

        # Build JSON structure
        data = {
            "timestamp": timestamp,
            "commit_sha": commit_sha,
            "duplication_ratio": ratio.ratio,
            "total_lines": ratio.total_lines,
            "duplicate_lines": ratio.duplicate_lines,
            "files_scanned": ratio.files_scanned,
            "files_with_duplicates": ratio.files_with_duplicates,
            "duplicate_blocks": [block.to_dict() for block in ratio.duplicate_blocks],
            "summary": {
                "num_blocks": len(ratio.duplicate_blocks),
                "avg_block_size": (
                    sum(b.lines[1] - b.lines[0] + 1 for b in ratio.duplicate_blocks)
                    / len(ratio.duplicate_blocks)
                    if ratio.duplicate_blocks
                    else 0
                ),
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(None)
        return filepath
    
    xǁMetricStorageǁ_save_json__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁ_save_json__mutmut_1': xǁMetricStorageǁ_save_json__mutmut_1, 
        'xǁMetricStorageǁ_save_json__mutmut_2': xǁMetricStorageǁ_save_json__mutmut_2, 
        'xǁMetricStorageǁ_save_json__mutmut_3': xǁMetricStorageǁ_save_json__mutmut_3, 
        'xǁMetricStorageǁ_save_json__mutmut_4': xǁMetricStorageǁ_save_json__mutmut_4, 
        'xǁMetricStorageǁ_save_json__mutmut_5': xǁMetricStorageǁ_save_json__mutmut_5, 
        'xǁMetricStorageǁ_save_json__mutmut_6': xǁMetricStorageǁ_save_json__mutmut_6, 
        'xǁMetricStorageǁ_save_json__mutmut_7': xǁMetricStorageǁ_save_json__mutmut_7, 
        'xǁMetricStorageǁ_save_json__mutmut_8': xǁMetricStorageǁ_save_json__mutmut_8, 
        'xǁMetricStorageǁ_save_json__mutmut_9': xǁMetricStorageǁ_save_json__mutmut_9, 
        'xǁMetricStorageǁ_save_json__mutmut_10': xǁMetricStorageǁ_save_json__mutmut_10, 
        'xǁMetricStorageǁ_save_json__mutmut_11': xǁMetricStorageǁ_save_json__mutmut_11, 
        'xǁMetricStorageǁ_save_json__mutmut_12': xǁMetricStorageǁ_save_json__mutmut_12, 
        'xǁMetricStorageǁ_save_json__mutmut_13': xǁMetricStorageǁ_save_json__mutmut_13, 
        'xǁMetricStorageǁ_save_json__mutmut_14': xǁMetricStorageǁ_save_json__mutmut_14, 
        'xǁMetricStorageǁ_save_json__mutmut_15': xǁMetricStorageǁ_save_json__mutmut_15, 
        'xǁMetricStorageǁ_save_json__mutmut_16': xǁMetricStorageǁ_save_json__mutmut_16, 
        'xǁMetricStorageǁ_save_json__mutmut_17': xǁMetricStorageǁ_save_json__mutmut_17, 
        'xǁMetricStorageǁ_save_json__mutmut_18': xǁMetricStorageǁ_save_json__mutmut_18, 
        'xǁMetricStorageǁ_save_json__mutmut_19': xǁMetricStorageǁ_save_json__mutmut_19, 
        'xǁMetricStorageǁ_save_json__mutmut_20': xǁMetricStorageǁ_save_json__mutmut_20, 
        'xǁMetricStorageǁ_save_json__mutmut_21': xǁMetricStorageǁ_save_json__mutmut_21, 
        'xǁMetricStorageǁ_save_json__mutmut_22': xǁMetricStorageǁ_save_json__mutmut_22, 
        'xǁMetricStorageǁ_save_json__mutmut_23': xǁMetricStorageǁ_save_json__mutmut_23, 
        'xǁMetricStorageǁ_save_json__mutmut_24': xǁMetricStorageǁ_save_json__mutmut_24, 
        'xǁMetricStorageǁ_save_json__mutmut_25': xǁMetricStorageǁ_save_json__mutmut_25, 
        'xǁMetricStorageǁ_save_json__mutmut_26': xǁMetricStorageǁ_save_json__mutmut_26, 
        'xǁMetricStorageǁ_save_json__mutmut_27': xǁMetricStorageǁ_save_json__mutmut_27, 
        'xǁMetricStorageǁ_save_json__mutmut_28': xǁMetricStorageǁ_save_json__mutmut_28, 
        'xǁMetricStorageǁ_save_json__mutmut_29': xǁMetricStorageǁ_save_json__mutmut_29, 
        'xǁMetricStorageǁ_save_json__mutmut_30': xǁMetricStorageǁ_save_json__mutmut_30, 
        'xǁMetricStorageǁ_save_json__mutmut_31': xǁMetricStorageǁ_save_json__mutmut_31, 
        'xǁMetricStorageǁ_save_json__mutmut_32': xǁMetricStorageǁ_save_json__mutmut_32, 
        'xǁMetricStorageǁ_save_json__mutmut_33': xǁMetricStorageǁ_save_json__mutmut_33, 
        'xǁMetricStorageǁ_save_json__mutmut_34': xǁMetricStorageǁ_save_json__mutmut_34, 
        'xǁMetricStorageǁ_save_json__mutmut_35': xǁMetricStorageǁ_save_json__mutmut_35, 
        'xǁMetricStorageǁ_save_json__mutmut_36': xǁMetricStorageǁ_save_json__mutmut_36, 
        'xǁMetricStorageǁ_save_json__mutmut_37': xǁMetricStorageǁ_save_json__mutmut_37, 
        'xǁMetricStorageǁ_save_json__mutmut_38': xǁMetricStorageǁ_save_json__mutmut_38, 
        'xǁMetricStorageǁ_save_json__mutmut_39': xǁMetricStorageǁ_save_json__mutmut_39, 
        'xǁMetricStorageǁ_save_json__mutmut_40': xǁMetricStorageǁ_save_json__mutmut_40, 
        'xǁMetricStorageǁ_save_json__mutmut_41': xǁMetricStorageǁ_save_json__mutmut_41, 
        'xǁMetricStorageǁ_save_json__mutmut_42': xǁMetricStorageǁ_save_json__mutmut_42, 
        'xǁMetricStorageǁ_save_json__mutmut_43': xǁMetricStorageǁ_save_json__mutmut_43, 
        'xǁMetricStorageǁ_save_json__mutmut_44': xǁMetricStorageǁ_save_json__mutmut_44, 
        'xǁMetricStorageǁ_save_json__mutmut_45': xǁMetricStorageǁ_save_json__mutmut_45, 
        'xǁMetricStorageǁ_save_json__mutmut_46': xǁMetricStorageǁ_save_json__mutmut_46, 
        'xǁMetricStorageǁ_save_json__mutmut_47': xǁMetricStorageǁ_save_json__mutmut_47, 
        'xǁMetricStorageǁ_save_json__mutmut_48': xǁMetricStorageǁ_save_json__mutmut_48, 
        'xǁMetricStorageǁ_save_json__mutmut_49': xǁMetricStorageǁ_save_json__mutmut_49, 
        'xǁMetricStorageǁ_save_json__mutmut_50': xǁMetricStorageǁ_save_json__mutmut_50, 
        'xǁMetricStorageǁ_save_json__mutmut_51': xǁMetricStorageǁ_save_json__mutmut_51, 
        'xǁMetricStorageǁ_save_json__mutmut_52': xǁMetricStorageǁ_save_json__mutmut_52, 
        'xǁMetricStorageǁ_save_json__mutmut_53': xǁMetricStorageǁ_save_json__mutmut_53, 
        'xǁMetricStorageǁ_save_json__mutmut_54': xǁMetricStorageǁ_save_json__mutmut_54, 
        'xǁMetricStorageǁ_save_json__mutmut_55': xǁMetricStorageǁ_save_json__mutmut_55, 
        'xǁMetricStorageǁ_save_json__mutmut_56': xǁMetricStorageǁ_save_json__mutmut_56, 
        'xǁMetricStorageǁ_save_json__mutmut_57': xǁMetricStorageǁ_save_json__mutmut_57, 
        'xǁMetricStorageǁ_save_json__mutmut_58': xǁMetricStorageǁ_save_json__mutmut_58, 
        'xǁMetricStorageǁ_save_json__mutmut_59': xǁMetricStorageǁ_save_json__mutmut_59, 
        'xǁMetricStorageǁ_save_json__mutmut_60': xǁMetricStorageǁ_save_json__mutmut_60, 
        'xǁMetricStorageǁ_save_json__mutmut_61': xǁMetricStorageǁ_save_json__mutmut_61
    }
    
    def _save_json(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁ_save_json__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁ_save_json__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _save_json.__signature__ = _mutmut_signature(xǁMetricStorageǁ_save_json__mutmut_orig)
    xǁMetricStorageǁ_save_json__mutmut_orig.__name__ = 'xǁMetricStorageǁ_save_json'

    def xǁMetricStorageǁ_save_sqlite__mutmut_orig(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_1(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = None
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_2(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(None)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_3(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = None

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_4(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                None,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_5(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                None,
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_6(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_7(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_8(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = None

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_9(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    None,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_10(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    None,
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_11(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_12(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_13(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[1],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_14(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[2],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_15(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = None

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_16(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        None,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_17(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        None,
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_18(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_19(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_20(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["XXfileXX"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_21(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["FILE"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_22(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["XXstartXX"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_23(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["START"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_24(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["XXendXX"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_25(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["END"],
                        ),
                    )

            conn.commit()
            logger.info(f"Saved SQLite metrics with ID {metric_id}")
            return metric_id

        finally:
            conn.close()

    def xǁMetricStorageǁ_save_sqlite__mutmut_26(
        self,
        ratio: DuplicationRatio,
        commit_sha: Optional[str],
        timestamp: str,
    ) -> int:
        """Save metrics to SQLite database"""
        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Insert metric record
            cursor.execute(
                """
                INSERT INTO metrics (
                    timestamp, commit_sha, ratio, total_lines, duplicate_lines,
                    files_scanned, files_with_duplicates
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    commit_sha,
                    ratio.ratio,
                    ratio.total_lines,
                    ratio.duplicate_lines,
                    ratio.files_scanned,
                    ratio.files_with_duplicates,
                ),
            )

            metric_id = cursor.lastrowid

            # Insert duplicate blocks
            for block in ratio.duplicate_blocks:
                cursor.execute(
                    """
                    INSERT INTO duplicate_blocks (
                        metric_id, hash, start_line, end_line, severity,
                        clone_type, num_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        block.hash,
                        block.lines[0],
                        block.lines[1],
                        block.severity,
                        block.clone_type,
                        len(block.occurrences),
                    ),
                )

                block_id = cursor.lastrowid

                # Insert occurrences
                for occ in block.occurrences:
                    cursor.execute(
                        """
                        INSERT INTO occurrences (
                            block_id, file_path, start_line, end_line
                        ) VALUES (?, ?, ?, ?)
                    """,
                        (
                            block_id,
                            occ["file"],
                            occ["start"],
                            occ["end"],
                        ),
                    )

            conn.commit()
            logger.info(None)
            return metric_id

        finally:
            conn.close()
    
    xǁMetricStorageǁ_save_sqlite__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁ_save_sqlite__mutmut_1': xǁMetricStorageǁ_save_sqlite__mutmut_1, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_2': xǁMetricStorageǁ_save_sqlite__mutmut_2, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_3': xǁMetricStorageǁ_save_sqlite__mutmut_3, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_4': xǁMetricStorageǁ_save_sqlite__mutmut_4, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_5': xǁMetricStorageǁ_save_sqlite__mutmut_5, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_6': xǁMetricStorageǁ_save_sqlite__mutmut_6, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_7': xǁMetricStorageǁ_save_sqlite__mutmut_7, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_8': xǁMetricStorageǁ_save_sqlite__mutmut_8, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_9': xǁMetricStorageǁ_save_sqlite__mutmut_9, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_10': xǁMetricStorageǁ_save_sqlite__mutmut_10, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_11': xǁMetricStorageǁ_save_sqlite__mutmut_11, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_12': xǁMetricStorageǁ_save_sqlite__mutmut_12, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_13': xǁMetricStorageǁ_save_sqlite__mutmut_13, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_14': xǁMetricStorageǁ_save_sqlite__mutmut_14, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_15': xǁMetricStorageǁ_save_sqlite__mutmut_15, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_16': xǁMetricStorageǁ_save_sqlite__mutmut_16, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_17': xǁMetricStorageǁ_save_sqlite__mutmut_17, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_18': xǁMetricStorageǁ_save_sqlite__mutmut_18, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_19': xǁMetricStorageǁ_save_sqlite__mutmut_19, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_20': xǁMetricStorageǁ_save_sqlite__mutmut_20, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_21': xǁMetricStorageǁ_save_sqlite__mutmut_21, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_22': xǁMetricStorageǁ_save_sqlite__mutmut_22, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_23': xǁMetricStorageǁ_save_sqlite__mutmut_23, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_24': xǁMetricStorageǁ_save_sqlite__mutmut_24, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_25': xǁMetricStorageǁ_save_sqlite__mutmut_25, 
        'xǁMetricStorageǁ_save_sqlite__mutmut_26': xǁMetricStorageǁ_save_sqlite__mutmut_26
    }
    
    def _save_sqlite(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁ_save_sqlite__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁ_save_sqlite__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _save_sqlite.__signature__ = _mutmut_signature(xǁMetricStorageǁ_save_sqlite__mutmut_orig)
    xǁMetricStorageǁ_save_sqlite__mutmut_orig.__name__ = 'xǁMetricStorageǁ_save_sqlite'

    def xǁMetricStorageǁload_latest__mutmut_orig(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_1(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite and not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_2(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_3(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_4(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = None
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_5(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(None)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_6(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = None

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_7(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                None
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_8(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = None
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_9(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_10(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = None

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_11(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "XXidXX": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_12(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "ID": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_13(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "XXtimestampXX": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_14(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "TIMESTAMP": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_15(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "XXcommit_shaXX": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_16(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "COMMIT_SHA": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_17(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "XXratioXX": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_18(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "RATIO": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_19(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "XXtotal_linesXX": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_20(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "TOTAL_LINES": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_21(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "XXduplicate_linesXX": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_22(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "DUPLICATE_LINES": duplicate_lines,
                "files_scanned": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_23(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "XXfiles_scannedXX": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_24(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "FILES_SCANNED": files_scanned,
                "files_with_duplicates": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_25(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "XXfiles_with_duplicatesXX": files_with_duplicates,
            }

        finally:
            conn.close()

    def xǁMetricStorageǁload_latest__mutmut_26(self) -> Optional[dict[str, Any]]:
        """Load most recent metrics from SQLite"""
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return None

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            # Get latest metric
            cursor.execute(
                """
                SELECT id, timestamp, commit_sha, ratio, total_lines,
                       duplicate_lines, files_scanned, files_with_duplicates
                FROM metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                metric_id,
                timestamp,
                commit_sha,
                ratio,
                total_lines,
                duplicate_lines,
                files_scanned,
                files_with_duplicates,
            ) = row

            return {
                "id": metric_id,
                "timestamp": timestamp,
                "commit_sha": commit_sha,
                "ratio": ratio,
                "total_lines": total_lines,
                "duplicate_lines": duplicate_lines,
                "files_scanned": files_scanned,
                "FILES_WITH_DUPLICATES": files_with_duplicates,
            }

        finally:
            conn.close()
    
    xǁMetricStorageǁload_latest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁload_latest__mutmut_1': xǁMetricStorageǁload_latest__mutmut_1, 
        'xǁMetricStorageǁload_latest__mutmut_2': xǁMetricStorageǁload_latest__mutmut_2, 
        'xǁMetricStorageǁload_latest__mutmut_3': xǁMetricStorageǁload_latest__mutmut_3, 
        'xǁMetricStorageǁload_latest__mutmut_4': xǁMetricStorageǁload_latest__mutmut_4, 
        'xǁMetricStorageǁload_latest__mutmut_5': xǁMetricStorageǁload_latest__mutmut_5, 
        'xǁMetricStorageǁload_latest__mutmut_6': xǁMetricStorageǁload_latest__mutmut_6, 
        'xǁMetricStorageǁload_latest__mutmut_7': xǁMetricStorageǁload_latest__mutmut_7, 
        'xǁMetricStorageǁload_latest__mutmut_8': xǁMetricStorageǁload_latest__mutmut_8, 
        'xǁMetricStorageǁload_latest__mutmut_9': xǁMetricStorageǁload_latest__mutmut_9, 
        'xǁMetricStorageǁload_latest__mutmut_10': xǁMetricStorageǁload_latest__mutmut_10, 
        'xǁMetricStorageǁload_latest__mutmut_11': xǁMetricStorageǁload_latest__mutmut_11, 
        'xǁMetricStorageǁload_latest__mutmut_12': xǁMetricStorageǁload_latest__mutmut_12, 
        'xǁMetricStorageǁload_latest__mutmut_13': xǁMetricStorageǁload_latest__mutmut_13, 
        'xǁMetricStorageǁload_latest__mutmut_14': xǁMetricStorageǁload_latest__mutmut_14, 
        'xǁMetricStorageǁload_latest__mutmut_15': xǁMetricStorageǁload_latest__mutmut_15, 
        'xǁMetricStorageǁload_latest__mutmut_16': xǁMetricStorageǁload_latest__mutmut_16, 
        'xǁMetricStorageǁload_latest__mutmut_17': xǁMetricStorageǁload_latest__mutmut_17, 
        'xǁMetricStorageǁload_latest__mutmut_18': xǁMetricStorageǁload_latest__mutmut_18, 
        'xǁMetricStorageǁload_latest__mutmut_19': xǁMetricStorageǁload_latest__mutmut_19, 
        'xǁMetricStorageǁload_latest__mutmut_20': xǁMetricStorageǁload_latest__mutmut_20, 
        'xǁMetricStorageǁload_latest__mutmut_21': xǁMetricStorageǁload_latest__mutmut_21, 
        'xǁMetricStorageǁload_latest__mutmut_22': xǁMetricStorageǁload_latest__mutmut_22, 
        'xǁMetricStorageǁload_latest__mutmut_23': xǁMetricStorageǁload_latest__mutmut_23, 
        'xǁMetricStorageǁload_latest__mutmut_24': xǁMetricStorageǁload_latest__mutmut_24, 
        'xǁMetricStorageǁload_latest__mutmut_25': xǁMetricStorageǁload_latest__mutmut_25, 
        'xǁMetricStorageǁload_latest__mutmut_26': xǁMetricStorageǁload_latest__mutmut_26
    }
    
    def load_latest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁload_latest__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁload_latest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load_latest.__signature__ = _mutmut_signature(xǁMetricStorageǁload_latest__mutmut_orig)
    xǁMetricStorageǁload_latest__mutmut_orig.__name__ = 'xǁMetricStorageǁload_latest'

    def xǁMetricStorageǁquery_history__mutmut_orig(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_1(
        self,
        limit: int = 11,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_2(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite and not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_3(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_4(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_5(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = None
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_6(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(None)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_7(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = None

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_8(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    None,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_9(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    None,
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_10(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_11(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_12(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    None,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_13(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    None,
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_14(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_15(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_16(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = None
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_17(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    None
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_18(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "XXidXX": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_19(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "ID": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_20(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[1],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_21(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "XXtimestampXX": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_22(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "TIMESTAMP": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_23(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[2],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_24(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "XXcommit_shaXX": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_25(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "COMMIT_SHA": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_26(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[3],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_27(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "XXratioXX": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_28(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "RATIO": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_29(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[4],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_30(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "XXtotal_linesXX": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_31(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "TOTAL_LINES": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_32(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[5],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_33(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "XXduplicate_linesXX": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_34(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "DUPLICATE_LINES": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_35(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[6],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_36(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "XXfiles_scannedXX": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_37(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "FILES_SCANNED": row[6],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_38(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[7],
                        "files_with_duplicates": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_39(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "XXfiles_with_duplicatesXX": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_40(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "FILES_WITH_DUPLICATES": row[7],
                    }
                )

            return results

        finally:
            conn.close()

    def xǁMetricStorageǁquery_history__mutmut_41(
        self,
        limit: int = 10,
        since: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query historical metrics

        Args:
            limit: Maximum number of records to return
            since: Optional ISO timestamp to filter from

        Returns:
            list of metric records
        """
        if not self.enable_sqlite or not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cursor = conn.cursor()

            if since:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (since, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, timestamp, commit_sha, ratio, total_lines,
                           duplicate_lines, files_scanned, files_with_duplicates
                    FROM metrics
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "id": row[0],
                        "timestamp": row[1],
                        "commit_sha": row[2],
                        "ratio": row[3],
                        "total_lines": row[4],
                        "duplicate_lines": row[5],
                        "files_scanned": row[6],
                        "files_with_duplicates": row[8],
                    }
                )

            return results

        finally:
            conn.close()
    
    xǁMetricStorageǁquery_history__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMetricStorageǁquery_history__mutmut_1': xǁMetricStorageǁquery_history__mutmut_1, 
        'xǁMetricStorageǁquery_history__mutmut_2': xǁMetricStorageǁquery_history__mutmut_2, 
        'xǁMetricStorageǁquery_history__mutmut_3': xǁMetricStorageǁquery_history__mutmut_3, 
        'xǁMetricStorageǁquery_history__mutmut_4': xǁMetricStorageǁquery_history__mutmut_4, 
        'xǁMetricStorageǁquery_history__mutmut_5': xǁMetricStorageǁquery_history__mutmut_5, 
        'xǁMetricStorageǁquery_history__mutmut_6': xǁMetricStorageǁquery_history__mutmut_6, 
        'xǁMetricStorageǁquery_history__mutmut_7': xǁMetricStorageǁquery_history__mutmut_7, 
        'xǁMetricStorageǁquery_history__mutmut_8': xǁMetricStorageǁquery_history__mutmut_8, 
        'xǁMetricStorageǁquery_history__mutmut_9': xǁMetricStorageǁquery_history__mutmut_9, 
        'xǁMetricStorageǁquery_history__mutmut_10': xǁMetricStorageǁquery_history__mutmut_10, 
        'xǁMetricStorageǁquery_history__mutmut_11': xǁMetricStorageǁquery_history__mutmut_11, 
        'xǁMetricStorageǁquery_history__mutmut_12': xǁMetricStorageǁquery_history__mutmut_12, 
        'xǁMetricStorageǁquery_history__mutmut_13': xǁMetricStorageǁquery_history__mutmut_13, 
        'xǁMetricStorageǁquery_history__mutmut_14': xǁMetricStorageǁquery_history__mutmut_14, 
        'xǁMetricStorageǁquery_history__mutmut_15': xǁMetricStorageǁquery_history__mutmut_15, 
        'xǁMetricStorageǁquery_history__mutmut_16': xǁMetricStorageǁquery_history__mutmut_16, 
        'xǁMetricStorageǁquery_history__mutmut_17': xǁMetricStorageǁquery_history__mutmut_17, 
        'xǁMetricStorageǁquery_history__mutmut_18': xǁMetricStorageǁquery_history__mutmut_18, 
        'xǁMetricStorageǁquery_history__mutmut_19': xǁMetricStorageǁquery_history__mutmut_19, 
        'xǁMetricStorageǁquery_history__mutmut_20': xǁMetricStorageǁquery_history__mutmut_20, 
        'xǁMetricStorageǁquery_history__mutmut_21': xǁMetricStorageǁquery_history__mutmut_21, 
        'xǁMetricStorageǁquery_history__mutmut_22': xǁMetricStorageǁquery_history__mutmut_22, 
        'xǁMetricStorageǁquery_history__mutmut_23': xǁMetricStorageǁquery_history__mutmut_23, 
        'xǁMetricStorageǁquery_history__mutmut_24': xǁMetricStorageǁquery_history__mutmut_24, 
        'xǁMetricStorageǁquery_history__mutmut_25': xǁMetricStorageǁquery_history__mutmut_25, 
        'xǁMetricStorageǁquery_history__mutmut_26': xǁMetricStorageǁquery_history__mutmut_26, 
        'xǁMetricStorageǁquery_history__mutmut_27': xǁMetricStorageǁquery_history__mutmut_27, 
        'xǁMetricStorageǁquery_history__mutmut_28': xǁMetricStorageǁquery_history__mutmut_28, 
        'xǁMetricStorageǁquery_history__mutmut_29': xǁMetricStorageǁquery_history__mutmut_29, 
        'xǁMetricStorageǁquery_history__mutmut_30': xǁMetricStorageǁquery_history__mutmut_30, 
        'xǁMetricStorageǁquery_history__mutmut_31': xǁMetricStorageǁquery_history__mutmut_31, 
        'xǁMetricStorageǁquery_history__mutmut_32': xǁMetricStorageǁquery_history__mutmut_32, 
        'xǁMetricStorageǁquery_history__mutmut_33': xǁMetricStorageǁquery_history__mutmut_33, 
        'xǁMetricStorageǁquery_history__mutmut_34': xǁMetricStorageǁquery_history__mutmut_34, 
        'xǁMetricStorageǁquery_history__mutmut_35': xǁMetricStorageǁquery_history__mutmut_35, 
        'xǁMetricStorageǁquery_history__mutmut_36': xǁMetricStorageǁquery_history__mutmut_36, 
        'xǁMetricStorageǁquery_history__mutmut_37': xǁMetricStorageǁquery_history__mutmut_37, 
        'xǁMetricStorageǁquery_history__mutmut_38': xǁMetricStorageǁquery_history__mutmut_38, 
        'xǁMetricStorageǁquery_history__mutmut_39': xǁMetricStorageǁquery_history__mutmut_39, 
        'xǁMetricStorageǁquery_history__mutmut_40': xǁMetricStorageǁquery_history__mutmut_40, 
        'xǁMetricStorageǁquery_history__mutmut_41': xǁMetricStorageǁquery_history__mutmut_41
    }
    
    def query_history(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMetricStorageǁquery_history__mutmut_orig"), object.__getattribute__(self, "xǁMetricStorageǁquery_history__mutmut_mutants"), args, kwargs, self)
        return result 
    
    query_history.__signature__ = _mutmut_signature(xǁMetricStorageǁquery_history__mutmut_orig)
    xǁMetricStorageǁquery_history__mutmut_orig.__name__ = 'xǁMetricStorageǁquery_history'
