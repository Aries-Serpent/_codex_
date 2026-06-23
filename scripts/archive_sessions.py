#!/usr/bin/env python3
"""
Archive Migration Script - Phase 5

Migrate sessions older than 90 days to Parquet cold storage.
- Identify candidates
- Archive to directory-based storage (YYYY/MM/)
- Verify archive integrity
- Update SQLite status
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from codex.session_db import SessionDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_session_from_jsonl(jsonl_path: str) -> dict:
    """Load session data from JSONL file"""
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
        if not lines:
            return {}
        
        # Parse all lines and merge
        session_data = {}
        for line in lines:
            try:
                data = json.loads(line)
                session_data.update(data)
            except json.JSONDecodeError:
                continue
        
        return session_data


def migrate_sessions(dry_run: bool = False, verbose: bool = False) -> dict:
    """Migrate sessions to archive
    
    Args:
        dry_run: Show what would be archived without doing it
        verbose: Verbose output
        
    Returns:
        Migration results
    """
    db = SessionDB()
    sessions_dir = Path(".codex/sessions")
    
    # Get archive candidates
    candidates = []
    now = datetime.utcnow()
    cutoff = now - timedelta(days=90)
    
    logger.info(f"Scanning {sessions_dir} for archive candidates (>90 days old)")
    
    for jsonl_file in sorted(sessions_dir.glob("session_*.jsonl")):
        try:
            session_data = load_session_from_jsonl(str(jsonl_file))
            session_id = jsonl_file.stem.replace("session_", "")
            
            timestamp_str = session_data.get("timestamp")
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if dt.replace(tzinfo=None) < cutoff:
                        age_days = (now - dt.replace(tzinfo=None)).days
                        candidates.append({
                            "session_id": session_id,
                            "path": jsonl_file,
                            "data": session_data,
                            "timestamp": dt,
                            "age_days": age_days
                        })
                except ValueError:
                    pass
        except Exception as e:
            logger.warning(f"Error reading {jsonl_file}: {e}")
    
    logger.info(f"Found {len(candidates)} archive candidates")
    
    if not candidates:
        return {
            "status": "success",
            "archived_count": 0,
            "total_candidates": len(candidates),
            "details": "No sessions to archive"
        }
    
    archived_count = 0
    failed = []
    
    for candidate in candidates:
        session_id = candidate["session_id"]
        session_data = candidate["data"]
        age_days = candidate["age_days"]
        
        if verbose:
            logger.info(f"Archiving {session_id} (age: {age_days} days)")
        
        if not dry_run:
            try:
                archive_path = db.archive_session(session_id, session_data)
                archived_count += 1
                
                if verbose:
                    logger.info(f"  → {archive_path}")
            except Exception as e:
                logger.error(f"Failed to archive {session_id}: {e}")
                failed.append({"session_id": session_id, "error": str(e)})
    
    if dry_run:
        logger.info(f"DRY RUN: Would archive {len(candidates)} sessions")
        return {
            "status": "success",
            "archived_count": 0,
            "total_candidates": len(candidates),
            "details": "Dry run - no sessions archived",
            "dry_run": True
        }
    
    # Build archive index
    build_archive_index()
    
    result = {
        "status": "success" if not failed else "partial",
        "archived_count": archived_count,
        "total_candidates": len(candidates),
        "failed_count": len(failed),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if failed:
        result["failed"] = failed
    
    # Get stats
    stats = db.get_archive_stats()
    result["archive_stats"] = stats
    
    return result


def build_archive_index():
    """Build archive index JSON for fast lookups"""
    db = SessionDB()
    archive_dir = Path(".codex/archive/sessions")
    
    logger.info("Building archive index...")
    
    archive_index = {
        "version": "1.0",
        "created": datetime.utcnow().isoformat(),
        "sessions": [],
        "statistics": {}
    }
    
    # Scan all parquet files
    total_size = 0
    for parquet_file in sorted(archive_dir.rglob("*.parquet")):
        try:
            import pandas as pd
            df = pd.read_parquet(str(parquet_file))
            
            if len(df) > 0:
                session = df.iloc[0]
                session_id = parquet_file.stem
                file_size = parquet_file.stat().st_size
                total_size += file_size
                
                archive_index["sessions"].append({
                    "session_id": session_id,
                    "archive_location": str(parquet_file.relative_to(Path.cwd())),
                    "file_size_bytes": file_size,
                    "timestamp": str(session.get("timestamp", "")),
                    "created_at": str(parquet_file.stat().st_ctime)
                })
        except Exception as e:
            logger.warning(f"Error indexing {parquet_file}: {e}")
    
    # Add statistics
    archive_index["statistics"] = {
        "total_sessions": len(archive_index["sessions"]),
        "total_size_mb": total_size / (1024 * 1024),
        "retention_policy": "Delete archives >30 iterations old",
        "archive_format": "Parquet (snappy compressed)",
        "partitioning": "YYYY/MM/ by creation_date"
    }
    
    # Write index
    index_path = Path(".codex/archive/sessions_archive_index.json")
    with open(index_path, 'w') as f:
        json.dump(archive_index, f, indent=2, default=str)
    
    logger.info(f"Archive index created: {index_path}")
    logger.info(f"  Sessions: {len(archive_index['sessions'])}")
    logger.info(f"  Total size: {archive_index['statistics']['total_size_mb']:.2f} MB")
    
    return archive_index


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive old sessions to cold storage")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be archived")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--build-index-only", action="store_true", help="Only build archive index")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.build_index_only:
        build_archive_index()
        return 0
    
    result = migrate_sessions(dry_run=args.dry_run, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"Archive Migration Results")
        print(f"{'='*60}")
        print(f"Status: {result['status']}")
        print(f"Archived: {result['archived_count']}/{result['total_candidates']}")
        
        if 'archive_stats' in result:
            stats = result['archive_stats']
            print(f"\nArchive Statistics:")
            print(f"  Active sessions: {stats['active_sessions']}")
            print(f"  Archived sessions: {stats['archived_sessions']}")
            print(f"  Total archive size: {stats['total_archive_size_mb']:.2f} MB")
        
        if 'failed' in result and result['failed']:
            print(f"\nFailed ({len(result['failed'])}):")
            for failed in result['failed']:
                print(f"  - {failed['session_id']}: {failed['error']}")
    
    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
