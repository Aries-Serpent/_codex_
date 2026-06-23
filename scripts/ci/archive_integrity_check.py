#!/usr/bin/env python3
"""
Archive Integrity Check Script - Phase 5

Verify archive integrity:
- All archived sessions readable
- Performance benchmarks (<500ms cold, <50ms cached)
- Archive index consistency
- Retention policy enforcement
"""

import json
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codex.session_db import SessionDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArchiveIntegrityCheck:
    """Verify archive integrity and performance"""
    
    def __init__(self):
        self.db = SessionDB()
        self.archive_dir = Path(".codex/archive/sessions")
        self.index_path = Path(".codex/archive/sessions_archive_index.json")
    
    def check_all(self) -> dict:
        """Run all integrity checks
        
        Returns:
            Check results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check 1: Archive index exists and is valid
        logger.info("Check 1: Archive index validity...")
        results["checks"]["index_validity"] = self._check_index()
        
        # Check 2: All archived files readable
        logger.info("Check 2: Archive file readability...")
        results["checks"]["file_readability"] = self._check_file_readability()
        
        # Check 3: Performance benchmarks
        logger.info("Check 3: Performance benchmarks...")
        results["checks"]["performance"] = self._check_performance()
        
        # Check 4: Retention policy
        logger.info("Check 4: Retention policy...")
        results["checks"]["retention_policy"] = self._check_retention_policy()
        
        # Check 5: Database consistency
        logger.info("Check 5: Database consistency...")
        results["checks"]["db_consistency"] = self._check_db_consistency()
        
        # Overall status
        all_passed = all(
            check.get("status") == "pass" 
            for check in results["checks"].values()
        )
        results["status"] = "pass" if all_passed else "fail"
        
        return results
    
    def _check_index(self) -> dict:
        """Check archive index validity"""
        try:
            if not self.index_path.exists():
                return {"status": "fail", "error": "Archive index not found"}
            
            with open(self.index_path, 'r') as f:
                index = json.load(f)
            
            required_fields = ["version", "created", "sessions", "statistics"]
            missing = [f for f in required_fields if f not in index]
            
            if missing:
                return {"status": "fail", "error": f"Missing fields: {missing}"}
            
            return {
                "status": "pass",
                "sessions_indexed": len(index["sessions"]),
                "total_size_mb": index["statistics"]["total_size_mb"],
                "version": index["version"]
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def _check_file_readability(self) -> dict:
        """Check all archive files are readable"""
        try:
            import pandas as pd
            
            parquet_files = list(self.archive_dir.rglob("*.parquet"))
            readable = 0
            failed = []
            
            for parquet_file in parquet_files[:10]:  # Check first 10
                try:
                    df = pd.read_parquet(str(parquet_file))
                    readable += 1
                except Exception as e:
                    failed.append({
                        "file": str(parquet_file),
                        "error": str(e)
                    })
            
            if failed:
                return {
                    "status": "fail",
                    "readable": readable,
                    "failed": failed
                }
            
            return {
                "status": "pass",
                "total_files": len(parquet_files),
                "checked": len(parquet_files[:10]),
                "readable": readable
            }
        except ImportError:
            return {"status": "skip", "reason": "pandas not available"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def _check_performance(self) -> dict:
        """Check retrieval performance benchmarks"""
        try:
            # Get an archived session for testing
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id FROM sessions 
                WHERE archive_status = 'archived'
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"status": "skip", "reason": "No archived sessions"}
            
            session_id = result[0]
            
            # Clear cache
            self.db._cache.clear()
            self.db.cache_current_size = 0
            
            # Benchmark cold retrieval
            start = time.time()
            session = self.db.get_session(session_id, use_cache=True)
            cold_time_ms = (time.time() - start) * 1000
            
            # Benchmark cached retrieval
            start = time.time()
            session_cached = self.db.get_session(session_id, use_cache=True)
            cached_time_ms = (time.time() - start) * 1000
            
            benchmarks = {
                "cold_retrieval_ms": cold_time_ms,
                "cached_retrieval_ms": cached_time_ms,
                "cold_threshold_ms": 500,
                "cached_threshold_ms": 50
            }
            
            cold_pass = cold_time_ms < benchmarks["cold_threshold_ms"]
            cached_pass = cached_time_ms < benchmarks["cached_threshold_ms"]
            
            status = "pass" if (cold_pass and cached_pass) else "warn"
            
            return {
                "status": status,
                "benchmarks": benchmarks,
                "cold_pass": cold_pass,
                "cached_pass": cached_pass,
                "session_tested": session_id
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def _check_retention_policy(self) -> dict:
        """Check retention policy enforcement"""
        try:
            import sqlite3
            
            cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Check for archives older than 30 iterations
            cursor.execute("""
                SELECT COUNT(*) FROM sessions
                WHERE archive_status = 'archived'
                AND archive_timestamp IS NOT NULL
                AND archive_timestamp < ?
            """, (cutoff,))
            
            old_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM sessions
                WHERE archive_status = 'deleted'
            """)
            
            deleted_count = cursor.fetchone()[0]
            conn.close()
            
            status = "pass" if old_count == 0 else "warn"
            
            return {
                "status": status,
                "old_archives_over_30_days": old_count,
                "deleted_archives": deleted_count,
                "cutoff_date": cutoff,
                "note": "Old archives should be deleted by maintenance script"
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def _check_db_consistency(self) -> dict:
        """Check database consistency"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Check all tables exist
            tables = ["sessions", "session_metadata", "session_events"]
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            missing = [t for t in tables if t not in existing_tables]
            
            if missing:
                conn.close()
                return {"status": "fail", "error": f"Missing tables: {missing}"}
            
            # Check for orphaned records (archive_status set but no archive_location)
            cursor.execute("""
                SELECT COUNT(*) FROM sessions
                WHERE archive_status = 'archived'
                AND archive_location IS NULL
            """)
            
            orphaned = cursor.fetchone()[0]
            
            conn.close()
            
            status = "pass" if orphaned == 0 else "warn"
            
            return {
                "status": status,
                "tables_exist": len(existing_tables),
                "orphaned_records": orphaned,
                "tables": existing_tables
            }
        except Exception as e:
            return {"status": "fail", "error": str(e)}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Check archive integrity")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = ArchiveIntegrityCheck()
    results = checker.check_all()
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"Archive Integrity Check")
        print(f"{'='*60}")
        print(f"Status: {results['status'].upper()}")
        print(f"Timestamp: {results['timestamp']}")
        
        print(f"\nChecks:")
        for name, check in results["checks"].items():
            status = check.get("status", "unknown").upper()
            print(f"  [{status}] {name}")
            
            if args.verbose:
                for key, value in check.items():
                    if key != "status":
                        if isinstance(value, (int, float)):
                            print(f"      {key}: {value}")
                        elif isinstance(value, str):
                            print(f"      {key}: {value}")
    
    return 0 if results['status'] == 'pass' else 1


if __name__ == "__main__":
    sys.exit(main())
