#!/usr/bin/env python3
"""
Har Ingest

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/har_ingest.py [options]

    Examples:
    $ python scripts/cognitive/har_ingest.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Ensure package imports
sys.path.insert(0, os.getcwd())


@dataclass
class IngestContext:
    """Context for HAR file ingestion"""
    src_path: Path
    db_path: Path
    dry_run: bool
    ndjson_path: Path
    repo_root: Path
    raw_har: Optional[dict[str, Any]] = None
    total_entries: int = 0
    pages_count: int = 0
    meta_creator: Optional[str] = None
    meta_browser: Optional[str] = None
    normalized: Optional[list[dict[str, Any]]] = None
    pages_jsonl_path: Optional[Path] = None


class HARIngestor:
    """HAR file ingestion pipeline for cognitive brain"""

    def __init__(self, context: IngestContext):
        self.context = context

    def validate_file(self) -> bool:
        """Phase 1: Validate file path and basic checks"""
        if not self.context.src_path.exists():
            print(f"❌ File not found: {self.context.src_path}")
            return False

        if not self.context.src_path.is_file():
            print(f"❌ Not a file: {self.context.src_path}")
            return False

        if self.context.src_path.suffix.lower() != '.har':
            print("⚠️  Warning: File doesn't have .har extension")

        file_size = self.context.src_path.stat().st_size
        if file_size == 0:
            print("❌ File is empty")
            return False

        print(f"✅ File validation passed: {file_size} bytes")
        return True

    def validate_schema(self) -> bool:
        """Phase 2: JSON schema check"""
        try:
            with open(self.context.src_path, encoding='utf-8') as f:
                self.context.raw_har = json.load(f)

            # Validate minimal HAR structure
            if 'log' not in self.context.raw_har:
                print("❌ Missing 'log' key in HAR file")
                return False

            log = self.context.raw_har['log']
            if 'entries' not in log:
                print("❌ Missing 'entries' in HAR log")
                return False

            self.context.total_entries = len(log['entries'])
            self.context.pages_count = len(log.get('pages', []))

            # Extract metadata
            if 'creator' in log:
                self.context.meta_creator = log['creator'].get('name', 'unknown')
            if 'browser' in log:
                self.context.meta_browser = log['browser'].get('name', 'unknown')

            print("✅ Schema validation passed")
            print(f"   Entries: {self.context.total_entries}")
            print(f"   Pages: {self.context.pages_count}")
            print(f"   Creator: {self.context.meta_creator}")
            print(f"   Browser: {self.context.meta_browser}")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Schema validation error: {e}")
            return False

    def parse_entries(self) -> bool:
        """Phase 3: Parse and normalize entries"""
        if not self.context.raw_har:
            print("❌ No HAR data to parse")
            return False

        try:
            entries = self.context.raw_har['log']['entries']
            self.context.normalized = []

            for idx, entry in enumerate(entries):
                normalized_entry = {
                    'index': idx,
                    'started_datetime': entry.get('startedDateTime'),
                    'time': entry.get('time'),
                    'request_method': entry.get('request', {}).get('method'),
                    'request_url': entry.get('request', {}).get('url'),
                    'response_status': entry.get('response', {}).get('status'),
                    'response_status_text': entry.get('response', {}).get('statusText'),
                    'response_size': entry.get('response', {}).get('bodySize', 0),
                    'server_ip': entry.get('serverIPAddress'),
                    'connection': entry.get('connection')
                }
                self.context.normalized.append(normalized_entry)

            print(f"✅ Parsed {len(self.context.normalized)} entries")
            return True

        except Exception as e:
            print(f"❌ Parse error: {e}")
            return False

    def write_to_db(self) -> bool:
        """Phase 4: Write to SQLite (APPLY only; DRY_RUN skips)"""
        if self.context.dry_run:
            print("🔍 DRY_RUN mode: Skipping database write")
            return True

        try:
            # Create database directory if needed
            self.context.db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.context.db_path)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS har_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT,
                    ingestion_time TEXT,
                    entry_index INTEGER,
                    started_datetime TEXT,
                    time REAL,
                    request_method TEXT,
                    request_url TEXT,
                    response_status INTEGER,
                    response_status_text TEXT,
                    response_size INTEGER,
                    server_ip TEXT,
                    connection TEXT
                )
            """)

            # Insert entries
            ingestion_time = datetime.now(timezone.utc).isoformat()
            for entry in self.context.normalized or []:
                cursor.execute("""
                    INSERT INTO har_entries (
                        source_file, ingestion_time, entry_index,
                        started_datetime, time, request_method, request_url,
                        response_status, response_status_text, response_size,
                        server_ip, connection
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(self.context.src_path),
                    ingestion_time,
                    entry['index'],
                    entry['started_datetime'],
                    entry['time'],
                    entry['request_method'],
                    entry['request_url'],
                    entry['response_status'],
                    entry['response_status_text'],
                    entry['response_size'],
                    entry['server_ip'],
                    entry['connection']
                ))

            conn.commit()
            conn.close()

            print(f"✅ Wrote {len(self.context.normalized or [])} entries to database")
            return True

        except Exception as e:
            print(f"❌ Database write error: {e}")
            return False

    def emit_metrics(self) -> bool:
        """Phase 5: Emit metrics as NDJSON"""
        try:
            metrics = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'event_type': 'har_ingestion',
                'source_file': str(self.context.src_path),
                'total_entries': self.context.total_entries,
                'pages_count': self.context.pages_count,
                'creator': self.context.meta_creator,
                'browser': self.context.meta_browser,
                'dry_run': self.context.dry_run,
                'success': True
            }

            # Append to NDJSON
            self.context.ndjson_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.context.ndjson_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')

            print(f"✅ Metrics emitted to {self.context.ndjson_path}")
            return True

        except Exception as e:
            print(f"❌ Metrics emission error: {e}")
            return False

    def run(self) -> bool:
        """Execute all phases"""
        print("\n🧠 HAR Ingestion Pipeline")
        print(f"{'='*60}")
        print(f"Source: {self.context.src_path}")
        print(f"Mode: {'DRY_RUN' if self.context.dry_run else 'APPLY'}")
        print(f"{'='*60}\n")

        phases = [
            ("Validate File", self.validate_file),
            ("Validate Schema", self.validate_schema),
            ("Parse Entries", self.parse_entries),
            ("Write to DB", self.write_to_db),
            ("Emit Metrics", self.emit_metrics)
        ]

        for phase_name, phase_func in phases:
            print(f"\n📍 Phase: {phase_name}")
            if not phase_func():
                print(f"\n❌ Pipeline failed at: {phase_name}")
                return False

        print(f"\n{'='*60}")
        print("✅ HAR Ingestion Pipeline Complete")
        print(f"{'='*60}\n")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="HAR ingestion pipeline for cognitive brain"
    )
    parser.add_argument(
        "har_file",
        type=Path,
        help="Path to HAR file to ingest"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("databases/har_ingest.db"),
        help="Path to SQLite database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate writes without touching database"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write to database (disables dry-run)"
    )
    parser.add_argument(
        "--ndjson",
        type=Path,
        default=Path("cognitive/metrics/har_ingestion.ndjson"),
        help="Path to NDJSON metrics file"
    )

    args = parser.parse_args()

    # --apply overrides --dry-run; if neither is explicitly set, default to dry-run.
    # This honours both flags: --dry-run keeps dry_run=True, --apply sets dry_run=False.
    if args.apply:
        dry_run = False
    else:
        dry_run = args.dry_run

    context = IngestContext(
        src_path=args.har_file,
        db_path=args.db,
        dry_run=dry_run,
        ndjson_path=args.ndjson,
        repo_root=Path.cwd()
    )

    ingestor = HARIngestor(context)
    success = ingestor.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
