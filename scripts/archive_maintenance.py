#!/usr/bin/env python3
"""
Archive Retention Maintenance Script - Phase 5

Delete archived sessions older than 30 iterations per retention policy.
Logs all deletions in retention_log.json for audit trail.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from codex.session_db import SessionDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RetentionMaintenance:
    """Handle archive retention and cleanup"""

    def __init__(self, max_iterations: int = 30):
        """
        Args:
            max_iterations: Max iterations to keep (30 iterations ~ 30 days)
        """
        self.db = SessionDB()
        self.max_iterations = max_iterations
        self.archive_dir = Path(".codex/archive/sessions")
        self.log_path = Path(".codex/archive/retention_log.json")

    def cleanup(self, dry_run: bool = False) -> dict:
        """Clean up old archives

        Args:
            dry_run: Show what would be deleted

        Returns:
            Cleanup results
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=self.max_iterations)).isoformat()

        logger.info(f"Scanning archives older than {self.max_iterations} iterations")
        logger.info(f"Cutoff date: {cutoff_date}")

        # Get candidates from database
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, archive_location, archive_timestamp
            FROM sessions
            WHERE archive_status = 'archived'
            AND archive_timestamp < ?
            ORDER BY archive_timestamp ASC
        """, (cutoff_date,))

        old_sessions = cursor.fetchall()
        conn.close()

        logger.info(f"Found {len(old_sessions)} archives for deletion")

        deleted_count = 0
        failed = []
        deletions = []

        for session_id, archive_location, archive_timestamp in old_sessions:
            if dry_run:
                logger.info(f"[DRY RUN] Would delete: {session_id}")
                deletions.append({
                    "session_id": session_id,
                    "archive_location": archive_location,
                    "archive_timestamp": archive_timestamp,
                    "deleted_at": datetime.utcnow().isoformat()
                })
            else:
                try:
                    # Delete Parquet file
                    if archive_location:
                        archive_path = Path(archive_location)
                        if archive_path.exists():
                            archive_path.unlink()
                            logger.info(f"Deleted: {archive_location}")

                    # Mark as deleted in database
                    self.db.mark_deleted(session_id)
                    deleted_count += 1

                    deletions.append({
                        "session_id": session_id,
                        "archive_location": archive_location,
                        "archive_timestamp": archive_timestamp,
                        "deleted_at": datetime.utcnow().isoformat()
                    })

                except Exception as e:
                    error_type = type(e).__name__
                    logger.error(f"Error deleting {session_id}: <ERROR_TYPE>")
                    failed.append({
                        "session_id": session_id,
                        "error": str(e)
                    })

        result = {
            "status": "success" if not failed else "partial",
            "deleted_count": deleted_count,
            "failed_count": len(failed),
            "total_candidates": len(old_sessions),
            "dry_run": dry_run,
            "max_iterations": self.max_iterations,
            "timestamp": datetime.utcnow().isoformat(),
            "deletions": deletions
        }

        if failed:
            result["failed"] = failed

        # Log to retention log
        if not dry_run:
            self._log_retention(result)

        return result

    def _log_retention(self, result: dict):
        """Log retention cleanup to retention_log.json"""
        try:
            # Load existing log or create new
            if self.log_path.exists():
                with open(self.log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {
                    "version": "1.0",
                    "created": datetime.utcnow().isoformat(),
                    "cleanups": []
                }

            # Add this cleanup
            log_data["cleanups"].append({
                "timestamp": result["timestamp"],
                "deleted_count": result["deleted_count"],
                "total_candidates": result["total_candidates"],
                "max_iterations": result["max_iterations"],
                "deletions_count": len(result["deletions"])
            })

            # Write back
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)

            logger.info(f"Retention log updated: {self.log_path}")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Error logging retention: <ERROR_TYPE>")

    def get_retention_stats(self) -> dict:
        """Get retention statistics"""
        stats = {
            "max_iterations": self.max_iterations,
            "cutoff_date": (datetime.utcnow() - timedelta(days=self.max_iterations)).isoformat(),
            "archive_stats": self.db.get_archive_stats()
        }

        # Get log info
        if self.log_path.exists():
            with open(self.log_path, 'r') as f:
                log_data = json.load(f)
                stats["total_cleanups"] = len(log_data["cleanups"])
                stats["total_deletions"] = sum(c["deleted_count"] for c in log_data["cleanups"])
        else:
            stats["total_cleanups"] = 0
            stats["total_deletions"] = 0

        return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Maintenance for archived sessions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    parser.add_argument("--max-iterations", type=int, default=30,
                        help="Max iterations to keep (default: 30)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--stats", action="store_true", help="Show retention stats")

    args = parser.parse_args()

    maintenance = RetentionMaintenance(max_iterations=args.max_iterations)

    if args.stats:
        stats = maintenance.get_retention_stats()
        if args.json:
            print(json.dumps(stats, indent=2, default=str))
        else:
            print("Retention Policy Statistics:")
            print(f"  Max iterations: {stats['max_iterations']}")
            print(f"  Cutoff date: {stats['cutoff_date']}")
            print(f"  Total cleanups: {stats['total_cleanups']}")
            print(f"  Total deletions: {stats['total_deletions']}")
            print(f"  Current archives: {stats['archive_stats']['archived_sessions']}")
        return 0

    result = maintenance.cleanup(dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print("Archive Retention Cleanup")
        print(f"{'='*60}")
        print(f"Status: {result['status']}")
        print(f"Deleted: {result['deleted_count']}/{result['total_candidates']}")
        print(f"Max iterations: {result['max_iterations']}")
        print(f"Dry run: {result['dry_run']}")

        if result['failed_count'] > 0:
            print(f"\nFailed ({result['failed_count']}):")
            for failed in result['failed']:
                print(f"  - {failed['session_id']}: {failed['error']}")

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
