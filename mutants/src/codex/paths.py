"""
Standard paths for Codex data storage.

Based on REPO_ADMIN_IMPLEMENTATION_DECISIONS.md Section 4.3.3:
- Centralize all Codex data in .codex/ directory
- Provide standard locations for databases, caches, reports
- Support environment variable overrides
"""

import os
import logging
logger = logging.getLogger(__name__)
from pathlib import Path
from typing import Optional

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


def x_ensure_codex_structure__mutmut_orig():
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


def x_ensure_codex_structure__mutmut_1():
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
    dirs = None
    
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


def x_ensure_codex_structure__mutmut_2():
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
        REPORTS_DIR * "archive",
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


def x_ensure_codex_structure__mutmut_3():
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
        REPORTS_DIR / "XXarchiveXX",
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


def x_ensure_codex_structure__mutmut_4():
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
        REPORTS_DIR / "ARCHIVE",
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


def x_ensure_codex_structure__mutmut_5():
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
        d.mkdir(parents=None, exist_ok=True)
    
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


def x_ensure_codex_structure__mutmut_6():
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
        d.mkdir(parents=True, exist_ok=None)
    
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


def x_ensure_codex_structure__mutmut_7():
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
        d.mkdir(exist_ok=True)
    
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


def x_ensure_codex_structure__mutmut_8():
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
        d.mkdir(parents=True, )
    
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


def x_ensure_codex_structure__mutmut_9():
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
        d.mkdir(parents=False, exist_ok=True)
    
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


def x_ensure_codex_structure__mutmut_10():
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
        d.mkdir(parents=True, exist_ok=False)
    
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


def x_ensure_codex_structure__mutmut_11():
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
    readme = None
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


def x_ensure_codex_structure__mutmut_12():
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
    readme = CODEX_DIR * "README.md"
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


def x_ensure_codex_structure__mutmut_13():
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
    readme = CODEX_DIR / "XXREADME.mdXX"
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


def x_ensure_codex_structure__mutmut_14():
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
    readme = CODEX_DIR / "readme.md"
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


def x_ensure_codex_structure__mutmut_15():
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
    readme = CODEX_DIR / "README.MD"
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


def x_ensure_codex_structure__mutmut_16():
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
    if readme.exists():
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


def x_ensure_codex_structure__mutmut_17():
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
        readme.write_text(None)
    
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


def x_ensure_codex_structure__mutmut_18():
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
    gitignore = None
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


def x_ensure_codex_structure__mutmut_19():
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
    gitignore = CODEX_DIR * ".gitignore"
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


def x_ensure_codex_structure__mutmut_20():
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
    gitignore = CODEX_DIR / "XX.gitignoreXX"
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


def x_ensure_codex_structure__mutmut_21():
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
    gitignore = CODEX_DIR / ".GITIGNORE"
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


def x_ensure_codex_structure__mutmut_22():
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
    if gitignore.exists():
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


def x_ensure_codex_structure__mutmut_23():
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
        gitignore.write_text(None)

x_ensure_codex_structure__mutmut_mutants : ClassVar[MutantDict] = {
'x_ensure_codex_structure__mutmut_1': x_ensure_codex_structure__mutmut_1, 
    'x_ensure_codex_structure__mutmut_2': x_ensure_codex_structure__mutmut_2, 
    'x_ensure_codex_structure__mutmut_3': x_ensure_codex_structure__mutmut_3, 
    'x_ensure_codex_structure__mutmut_4': x_ensure_codex_structure__mutmut_4, 
    'x_ensure_codex_structure__mutmut_5': x_ensure_codex_structure__mutmut_5, 
    'x_ensure_codex_structure__mutmut_6': x_ensure_codex_structure__mutmut_6, 
    'x_ensure_codex_structure__mutmut_7': x_ensure_codex_structure__mutmut_7, 
    'x_ensure_codex_structure__mutmut_8': x_ensure_codex_structure__mutmut_8, 
    'x_ensure_codex_structure__mutmut_9': x_ensure_codex_structure__mutmut_9, 
    'x_ensure_codex_structure__mutmut_10': x_ensure_codex_structure__mutmut_10, 
    'x_ensure_codex_structure__mutmut_11': x_ensure_codex_structure__mutmut_11, 
    'x_ensure_codex_structure__mutmut_12': x_ensure_codex_structure__mutmut_12, 
    'x_ensure_codex_structure__mutmut_13': x_ensure_codex_structure__mutmut_13, 
    'x_ensure_codex_structure__mutmut_14': x_ensure_codex_structure__mutmut_14, 
    'x_ensure_codex_structure__mutmut_15': x_ensure_codex_structure__mutmut_15, 
    'x_ensure_codex_structure__mutmut_16': x_ensure_codex_structure__mutmut_16, 
    'x_ensure_codex_structure__mutmut_17': x_ensure_codex_structure__mutmut_17, 
    'x_ensure_codex_structure__mutmut_18': x_ensure_codex_structure__mutmut_18, 
    'x_ensure_codex_structure__mutmut_19': x_ensure_codex_structure__mutmut_19, 
    'x_ensure_codex_structure__mutmut_20': x_ensure_codex_structure__mutmut_20, 
    'x_ensure_codex_structure__mutmut_21': x_ensure_codex_structure__mutmut_21, 
    'x_ensure_codex_structure__mutmut_22': x_ensure_codex_structure__mutmut_22, 
    'x_ensure_codex_structure__mutmut_23': x_ensure_codex_structure__mutmut_23
}

def ensure_codex_structure(*args, **kwargs):
    result = _mutmut_trampoline(x_ensure_codex_structure__mutmut_orig, x_ensure_codex_structure__mutmut_mutants, args, kwargs)
    return result 

ensure_codex_structure.__signature__ = _mutmut_signature(x_ensure_codex_structure__mutmut_orig)
x_ensure_codex_structure__mutmut_orig.__name__ = 'x_ensure_codex_structure'


def x_get_db_path__mutmut_orig(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var and os.getenv(env_var):
        return Path(os.getenv(env_var))
    
    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def x_get_db_path__mutmut_1(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var or os.getenv(env_var):
        return Path(os.getenv(env_var))
    
    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def x_get_db_path__mutmut_2(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var and os.getenv(None):
        return Path(os.getenv(env_var))
    
    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def x_get_db_path__mutmut_3(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var and os.getenv(env_var):
        return Path(None)
    
    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def x_get_db_path__mutmut_4(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var and os.getenv(env_var):
        return Path(os.getenv(None))
    
    ensure_codex_structure()
    return CODEX_DIR / f"{name}.db"


def x_get_db_path__mutmut_5(name: str, env_var: Optional[str] = None) -> Path:
    """Get database path with environment variable override.
    
    Args:
        name: Database name (e.g., "session_logs", "analysis", "metrics")
        env_var: Optional environment variable to check
    
    Returns:
        Path to database file
    
    Examples:
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('.codex/session_logs.db')
        
        >>> os.environ["CODEX_LOG_DB_PATH"] = "/tmp/logs.db"
        >>> get_db_path("session_logs", "CODEX_LOG_DB_PATH")
        Path('/tmp/logs.db')
    """
    if env_var and os.getenv(env_var):
        return Path(os.getenv(env_var))
    
    ensure_codex_structure()
    return CODEX_DIR * f"{name}.db"

x_get_db_path__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_db_path__mutmut_1': x_get_db_path__mutmut_1, 
    'x_get_db_path__mutmut_2': x_get_db_path__mutmut_2, 
    'x_get_db_path__mutmut_3': x_get_db_path__mutmut_3, 
    'x_get_db_path__mutmut_4': x_get_db_path__mutmut_4, 
    'x_get_db_path__mutmut_5': x_get_db_path__mutmut_5
}

def get_db_path(*args, **kwargs):
    result = _mutmut_trampoline(x_get_db_path__mutmut_orig, x_get_db_path__mutmut_mutants, args, kwargs)
    return result 

get_db_path.__signature__ = _mutmut_signature(x_get_db_path__mutmut_orig)
x_get_db_path__mutmut_orig.__name__ = 'x_get_db_path'


def x_get_cache_path__mutmut_orig(cache_type: str) -> Path:
    """Get cache directory path.
    
    Args:
        cache_type: Type of cache ("parsed_trees", "similarity", etc.)
    
    Returns:
        Path to cache directory
    """
    ensure_codex_structure()
    return CACHE_DIR / cache_type


def x_get_cache_path__mutmut_1(cache_type: str) -> Path:
    """Get cache directory path.
    
    Args:
        cache_type: Type of cache ("parsed_trees", "similarity", etc.)
    
    Returns:
        Path to cache directory
    """
    ensure_codex_structure()
    return CACHE_DIR * cache_type

x_get_cache_path__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_cache_path__mutmut_1': x_get_cache_path__mutmut_1
}

def get_cache_path(*args, **kwargs):
    result = _mutmut_trampoline(x_get_cache_path__mutmut_orig, x_get_cache_path__mutmut_mutants, args, kwargs)
    return result 

get_cache_path.__signature__ = _mutmut_signature(x_get_cache_path__mutmut_orig)
x_get_cache_path__mutmut_orig.__name__ = 'x_get_cache_path'


def x_get_report_path__mutmut_orig(report_name: str, archive: bool = False) -> Path:
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


def x_get_report_path__mutmut_1(report_name: str, archive: bool = True) -> Path:
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


def x_get_report_path__mutmut_2(report_name: str, archive: bool = False) -> Path:
    """Get report file path.
    
    Args:
        report_name: Name of report file
        archive: If True, place in archive/ subdirectory
    
    Returns:
        Path to report file
    """
    ensure_codex_structure()
    if archive:
        return REPORTS_DIR / "archive" * report_name
    return REPORTS_DIR / report_name


def x_get_report_path__mutmut_3(report_name: str, archive: bool = False) -> Path:
    """Get report file path.
    
    Args:
        report_name: Name of report file
        archive: If True, place in archive/ subdirectory
    
    Returns:
        Path to report file
    """
    ensure_codex_structure()
    if archive:
        return REPORTS_DIR * "archive" / report_name
    return REPORTS_DIR / report_name


def x_get_report_path__mutmut_4(report_name: str, archive: bool = False) -> Path:
    """Get report file path.
    
    Args:
        report_name: Name of report file
        archive: If True, place in archive/ subdirectory
    
    Returns:
        Path to report file
    """
    ensure_codex_structure()
    if archive:
        return REPORTS_DIR / "XXarchiveXX" / report_name
    return REPORTS_DIR / report_name


def x_get_report_path__mutmut_5(report_name: str, archive: bool = False) -> Path:
    """Get report file path.
    
    Args:
        report_name: Name of report file
        archive: If True, place in archive/ subdirectory
    
    Returns:
        Path to report file
    """
    ensure_codex_structure()
    if archive:
        return REPORTS_DIR / "ARCHIVE" / report_name
    return REPORTS_DIR / report_name


def x_get_report_path__mutmut_6(report_name: str, archive: bool = False) -> Path:
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
    return REPORTS_DIR * report_name

x_get_report_path__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_report_path__mutmut_1': x_get_report_path__mutmut_1, 
    'x_get_report_path__mutmut_2': x_get_report_path__mutmut_2, 
    'x_get_report_path__mutmut_3': x_get_report_path__mutmut_3, 
    'x_get_report_path__mutmut_4': x_get_report_path__mutmut_4, 
    'x_get_report_path__mutmut_5': x_get_report_path__mutmut_5, 
    'x_get_report_path__mutmut_6': x_get_report_path__mutmut_6
}

def get_report_path(*args, **kwargs):
    result = _mutmut_trampoline(x_get_report_path__mutmut_orig, x_get_report_path__mutmut_mutants, args, kwargs)
    return result 

get_report_path.__signature__ = _mutmut_signature(x_get_report_path__mutmut_orig)
x_get_report_path__mutmut_orig.__name__ = 'x_get_report_path'


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_orig() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", "CODEX_LOG_DB_PATH")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_1() -> Path:
    """Get session logs database path."""
    return get_db_path(None, "CODEX_LOG_DB_PATH")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_2() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", None)


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_3() -> Path:
    """Get session logs database path."""
    return get_db_path("CODEX_LOG_DB_PATH")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_4() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", )


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_5() -> Path:
    """Get session logs database path."""
    return get_db_path("XXsession_logsXX", "CODEX_LOG_DB_PATH")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_6() -> Path:
    """Get session logs database path."""
    return get_db_path("SESSION_LOGS", "CODEX_LOG_DB_PATH")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_7() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", "XXCODEX_LOG_DB_PATHXX")


# Convenience functions for standard DB paths
def x_get_session_logs_db__mutmut_8() -> Path:
    """Get session logs database path."""
    return get_db_path("session_logs", "codex_log_db_path")

x_get_session_logs_db__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_session_logs_db__mutmut_1': x_get_session_logs_db__mutmut_1, 
    'x_get_session_logs_db__mutmut_2': x_get_session_logs_db__mutmut_2, 
    'x_get_session_logs_db__mutmut_3': x_get_session_logs_db__mutmut_3, 
    'x_get_session_logs_db__mutmut_4': x_get_session_logs_db__mutmut_4, 
    'x_get_session_logs_db__mutmut_5': x_get_session_logs_db__mutmut_5, 
    'x_get_session_logs_db__mutmut_6': x_get_session_logs_db__mutmut_6, 
    'x_get_session_logs_db__mutmut_7': x_get_session_logs_db__mutmut_7, 
    'x_get_session_logs_db__mutmut_8': x_get_session_logs_db__mutmut_8
}

def get_session_logs_db(*args, **kwargs):
    result = _mutmut_trampoline(x_get_session_logs_db__mutmut_orig, x_get_session_logs_db__mutmut_mutants, args, kwargs)
    return result 

get_session_logs_db.__signature__ = _mutmut_signature(x_get_session_logs_db__mutmut_orig)
x_get_session_logs_db__mutmut_orig.__name__ = 'x_get_session_logs_db'


def x_get_analysis_db__mutmut_orig() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", "CODEX_ANALYSIS_DB_PATH")


def x_get_analysis_db__mutmut_1() -> Path:
    """Get analysis database path."""
    return get_db_path(None, "CODEX_ANALYSIS_DB_PATH")


def x_get_analysis_db__mutmut_2() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", None)


def x_get_analysis_db__mutmut_3() -> Path:
    """Get analysis database path."""
    return get_db_path("CODEX_ANALYSIS_DB_PATH")


def x_get_analysis_db__mutmut_4() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", )


def x_get_analysis_db__mutmut_5() -> Path:
    """Get analysis database path."""
    return get_db_path("XXanalysisXX", "CODEX_ANALYSIS_DB_PATH")


def x_get_analysis_db__mutmut_6() -> Path:
    """Get analysis database path."""
    return get_db_path("ANALYSIS", "CODEX_ANALYSIS_DB_PATH")


def x_get_analysis_db__mutmut_7() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", "XXCODEX_ANALYSIS_DB_PATHXX")


def x_get_analysis_db__mutmut_8() -> Path:
    """Get analysis database path."""
    return get_db_path("analysis", "codex_analysis_db_path")

x_get_analysis_db__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_analysis_db__mutmut_1': x_get_analysis_db__mutmut_1, 
    'x_get_analysis_db__mutmut_2': x_get_analysis_db__mutmut_2, 
    'x_get_analysis_db__mutmut_3': x_get_analysis_db__mutmut_3, 
    'x_get_analysis_db__mutmut_4': x_get_analysis_db__mutmut_4, 
    'x_get_analysis_db__mutmut_5': x_get_analysis_db__mutmut_5, 
    'x_get_analysis_db__mutmut_6': x_get_analysis_db__mutmut_6, 
    'x_get_analysis_db__mutmut_7': x_get_analysis_db__mutmut_7, 
    'x_get_analysis_db__mutmut_8': x_get_analysis_db__mutmut_8
}

def get_analysis_db(*args, **kwargs):
    result = _mutmut_trampoline(x_get_analysis_db__mutmut_orig, x_get_analysis_db__mutmut_mutants, args, kwargs)
    return result 

get_analysis_db.__signature__ = _mutmut_signature(x_get_analysis_db__mutmut_orig)
x_get_analysis_db__mutmut_orig.__name__ = 'x_get_analysis_db'


def x_get_metrics_db__mutmut_orig() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", "CODEX_METRICS_DB_PATH")


def x_get_metrics_db__mutmut_1() -> Path:
    """Get metrics database path."""
    return get_db_path(None, "CODEX_METRICS_DB_PATH")


def x_get_metrics_db__mutmut_2() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", None)


def x_get_metrics_db__mutmut_3() -> Path:
    """Get metrics database path."""
    return get_db_path("CODEX_METRICS_DB_PATH")


def x_get_metrics_db__mutmut_4() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", )


def x_get_metrics_db__mutmut_5() -> Path:
    """Get metrics database path."""
    return get_db_path("XXmetricsXX", "CODEX_METRICS_DB_PATH")


def x_get_metrics_db__mutmut_6() -> Path:
    """Get metrics database path."""
    return get_db_path("METRICS", "CODEX_METRICS_DB_PATH")


def x_get_metrics_db__mutmut_7() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", "XXCODEX_METRICS_DB_PATHXX")


def x_get_metrics_db__mutmut_8() -> Path:
    """Get metrics database path."""
    return get_db_path("metrics", "codex_metrics_db_path")

x_get_metrics_db__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_metrics_db__mutmut_1': x_get_metrics_db__mutmut_1, 
    'x_get_metrics_db__mutmut_2': x_get_metrics_db__mutmut_2, 
    'x_get_metrics_db__mutmut_3': x_get_metrics_db__mutmut_3, 
    'x_get_metrics_db__mutmut_4': x_get_metrics_db__mutmut_4, 
    'x_get_metrics_db__mutmut_5': x_get_metrics_db__mutmut_5, 
    'x_get_metrics_db__mutmut_6': x_get_metrics_db__mutmut_6, 
    'x_get_metrics_db__mutmut_7': x_get_metrics_db__mutmut_7, 
    'x_get_metrics_db__mutmut_8': x_get_metrics_db__mutmut_8
}

def get_metrics_db(*args, **kwargs):
    result = _mutmut_trampoline(x_get_metrics_db__mutmut_orig, x_get_metrics_db__mutmut_mutants, args, kwargs)
    return result 

get_metrics_db.__signature__ = _mutmut_signature(x_get_metrics_db__mutmut_orig)
x_get_metrics_db__mutmut_orig.__name__ = 'x_get_metrics_db'
