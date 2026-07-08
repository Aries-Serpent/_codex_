#!/usr/bin/env python3
"""
Migrate Redis cache from pickle-serialized data to JSON format.

CWE-502 Remediation: Unsafe pickle.loads() -> json.loads()
"""

import argparse
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PickleToJsonMigrator:
    """Safely migrate pickle-serialized Redis data to JSON format."""

    def __init__(self, redis_url: str = "redis://localhost:6379", dry_run: bool = False):
        """Initialize migrator."""
        self.redis_url = redis_url
        self.dry_run = dry_run
        self.stats = {
            "total_keys": 0,
            "json_keys": 0,
            "pickle_keys": 0,
            "migrated": 0,
            "failed": 0,
            "errors": [],
        }

        try:
            import redis
            self.redis = redis.from_url(redis_url)
            self.redis.ping()
            logger.info(f"Connected to Redis: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    def _serialize_safe(self, obj: Any) -> str:
        """Safely serialize object to JSON string."""
        class SafeEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if hasattr(obj, "__dict__"):
                    return obj.__dict__
                if hasattr(obj, "to_dict"):
                    return obj.to_dict()
                return super().default(obj)
        return json.dumps(obj, cls=SafeEncoder)

    def _deserialize_safe(self, data: bytes) -> Optional[Any]:
        """Safely deserialize pickle data from Redis (trusted source only)."""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Failed to deserialize pickle data: {e}")
            return None

    def migrate(self) -> None:
        """Migrate all pickle data in Redis to JSON format.
        
        Uses SCAN instead of KEYS to avoid blocking large Redis instances.
        """
        if not self.redis:
            logger.error("Cannot migrate: Redis connection failed")
            return

        try:
            # Use SCAN instead of KEYS to avoid blocking production Redis
            # KEYS("*") can block Redis for seconds on large datasets
            all_keys = []
            for key in self.redis.scan_iter(match="*"):
                all_keys.append(key)
            
            self.stats["total_keys"] = len(all_keys)
            logger.info(f"Starting migration of {len(all_keys)} keys...")

            for key in all_keys:
                try:
                    data = self.redis.get(key)
                    if data is None:
                        continue

                    try:
                        json.loads(data.decode("utf-8"))
                        self.stats["json_keys"] += 1
                        logger.debug(f"Key {key} is already JSON")
                        continue
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass

                    obj = self._deserialize_safe(data)
                    if obj is None:
                        self.stats["failed"] += 1
                        self.stats["errors"].append(f"Failed to deserialize {key}")
                        continue

                    try:
                        json_data = self._serialize_safe(obj)
                        self.stats["pickle_keys"] += 1

                        if not self.dry_run:
                            backup_key = f"{key}.pickle-backup"
                            self.redis.set(backup_key, data, ex=86400)
                            ttl = self.redis.ttl(key)
                            if ttl > 0:
                                self.redis.set(key, json_data, ex=ttl)
                            else:
                                self.redis.set(key, json_data)
                            self.stats["migrated"] += 1
                            logger.info(f"Migrated {key}: pickle -> JSON")
                        else:
                            self.stats["migrated"] += 1
                            logger.info(f"[DRY RUN] Would migrate {key}: pickle -> JSON")
                    except (TypeError, ValueError) as e:
                        self.stats["failed"] += 1
                        self.stats["errors"].append(f"Failed to serialize {key}: {e}")
                        logger.error(f"Failed to serialize {key}: {e}")
                except Exception as e:
                    self.stats["failed"] += 1
                    self.stats["errors"].append(f"Error processing {key}: {e}")
                    logger.error(f"Error processing {key}: {e}")
        except Exception as e:
            logger.error(f"Migration failed: {e}")

    def report(self) -> None:
        """Print migration report."""
        print("\n" + "=" * 60)
        print("CACHE MIGRATION REPORT (Pickle to JSON)")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Total keys: {self.stats['total_keys']}")
        print(f"Successfully migrated: {self.stats['migrated']}")
        print(f"Failed: {self.stats['failed']}")
        if self.stats["errors"]:
            print("Errors:", self.stats["errors"][:5])
        print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate Redis cache (CWE-502 remediation)")
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    migrator = PickleToJsonMigrator(redis_url=args.redis_url, dry_run=args.dry_run)
    migrator.migrate()
    migrator.report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
