"""
Standard paths for Codex data storage.

Based on REPO_ADMIN_IMPLEMENTATION_DECISIONS.md Section 4.3.3:
- Centralize all Codex data in .codex/ directory
- Provide standard locations for databases, caches, reports
- Support environment variable overrides
"""

import logging
import os

logger = logging.getLogger(__name__)
from pathlib import Path  # noqa: E402
from typing import Optional  # noqa: E402

# Standard locations (relative to repo root)
CODEX_DIR = Path(".codex")
SESSION_LOGS_DB = CODEX_DIR / "session_logs.db"
ANALYSIS_DB = CODEX_DIR / "analysis.db"
METRICS_DB = CODEX_DIR / "metrics.db"
CACHE_DIR = CODEX_DIR / "cache"
REPORTS_DIR = CODEX_DIR / "reports"
CONFIG_DIR = CODEX_DIR / "config"

# Cache subdirectories
PARSED_TREES_CACHE = CACHE_DIR / "parsed_trees"
SIMILARITY_CACHE = CACHE_DIR / "similarity"


def ensure_codex_structure() -> None:
    """Create standard .codex directory structure.

    Creates:
        .codex/
        ├── session_logs.db
        ├── analysis.db
        ├── metrics.db
        ├── cache/
        │   ├── parsed_trees/
        │   └── similarity/
        ├── reports/
        │   └── archive/
        ├── config/
        └── README.md
    """
    dirs = [
        CODEX_DIR,
        CACHE_DIR,
        PARSED_TREES_CACHE,
        SIMILARITY_CACHE,
        REPORTS_DIR,
        REPORTS_DIR / "archive",
        CONFIG_DIR,
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Create README if not exists
    readme = CODEX_DIR / "README.md"
    if not readme.exists():
        readme.write_text("""# Codex Local Data Directory

This directory contains local analysis data and caches.

## Structure
- `session_logs.db` - Session event logs
- `analysis.db` - Code analysis results
- `metrics.db` - Historical code metrics
- `cache/` - Temporary cached data
  - `parsed_trees/` - AST/LibCST caches
  - `similarity/` - AST similarity hashes
- `reports/` - Generated HTML/PDF reports
  - `archive/` - Historical reports
- `config/` - Local configuration overrides

## Gitignore
This entire directory is gitignored except README.md.
Do not commit databases or caches.

## Backup
For backup, preserve `*.db` files. Cache can be regenerated.

## Size Management
- Caches automatically cleaned after 24 hours
- Reports archived after 30 days
- Use `codex-clean-cache` to manually clean

## Environment Variables
- `CODEX_LOG_DB_PATH` - Override session logs location
- `CODEX_ANALYSIS_DB_PATH` - Override analysis DB location
- `CODEX_METRICS_DB_PATH` - Override metrics DB location
""")

    # Create .gitignore if not exists
    gitignore = CODEX_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("""# Codex local data - do not commit
*.db
*.sqlite
cache/
reports/
!README.md
!.gitignore
config/*.yaml
!config/*.example
""")


def get_db_path(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.

    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check

    Returns:
        Path to database file

    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')

        >>> os.environ["CODEX_LOG_DB_PATH"] = os.path.join(tempfile.gettempdir(), "logs.db")
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path(os.path.join(tempfile.gettempdir(), 'logs.db'))
    """
    if env_var and os.getenv(env_var):
        return Path(os.getenv(env_var))  # type: ignore[arg-type]

    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def get_cache_path(cache_type: str) -> Path:
    """Get cache directory path.

    Args:
        cache_type: Type of cache ("parsed_trees", "similarity", etc.)

    Returns:
        Path to cache directory
    """
    ensure_codex_structure()
    return CACHE_DIR / cache_type


def get_report_path(report_name: str, archive: bool = False) -> Path:
    """Get report file path.

    Args:
        report_name: Name of report file
        archive: If True, place in archive/ subdirectory

    Returns:
        Path to report file
    """
    ensure_codex_structure()
    if archive:
        return REPORTS_DIR / "archive" / report_name
    return REPORTS_DIR / report_name


# Convenience functions for standard DB paths
def get_session_logs_db() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", "CODEX_LOG_DB_PATH")


def get_analysis_db() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", "CODEX_ANALYSIS_DB_PATH")


def get_metrics_db() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", "CODEX_METRICS_DB_PATH")
