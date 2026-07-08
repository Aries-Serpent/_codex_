"""SQLite + FTS Query Layer — Builds indexed searchable database from JSONL records."""

import sqlite3
import json
from pathlib import Path
from typing import Dict


class SQLiteIndexBuilder:
    """Builds SQLite database with FTS indexing for campaign data."""

    def __init__(
        self, canonical_dir: str = "docs-data/canonical", output_dir: str = "docs-data/generated"
    ):
        self.canonical_dir = Path(canonical_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.output_dir / "docs.sqlite"

        # Create/connect database
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

    def create_schema(self):
        """Create database schema for campaign data."""

        # Use flexible JSON schema approach
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_phases (
                id TEXT PRIMARY KEY,
                data TEXT  -- JSON serialized
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                phase_id TEXT,
                data TEXT,  -- JSON serialized
                FOREIGN KEY(phase_id) REFERENCES campaign_phases(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliverables (
                id TEXT PRIMARY KEY,
                phase_id TEXT,
                track_id TEXT,
                data TEXT,  -- JSON serialized
                FOREIGN KEY(phase_id) REFERENCES campaign_phases(id),
                FOREIGN KEY(track_id) REFERENCES tracks(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                phase_id TEXT,
                data TEXT,  -- JSON serialized
                FOREIGN KEY(phase_id) REFERENCES campaign_phases(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                phase_id TEXT,
                data TEXT,  -- JSON serialized
                FOREIGN KEY(phase_id) REFERENCES campaign_phases(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                data TEXT  -- JSON serialized
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY,
                phase_id TEXT,
                data TEXT,  -- JSON serialized
                FOREIGN KEY(phase_id) REFERENCES campaign_phases(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                data TEXT  -- JSON serialized
            )
        """)

        # FTS tables
        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_phases USING fts5(
                id UNINDEXED,
                name,
                description
            )
        """)

        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_tracks USING fts5(
                id UNINDEXED,
                name,
                description
            )
        """)

        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_deliverables USING fts5(
                id UNINDEXED,
                name
            )
        """)

        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_decisions USING fts5(
                id UNINDEXED,
                description,
                rationale
            )
        """)

        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_metrics USING fts5(
                id UNINDEXED,
                metric_name
            )
        """)

        self.conn.commit()

    def load_jsonl_into_table(self, jsonl_filename: str, table_name: str):
        """Load JSONL file into database table."""
        filepath = self.canonical_dir / jsonl_filename
        if not filepath.exists():
            return 0

        count = 0
        with open(filepath) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    record_id = record.get("id")
                    phase_id = record.get("phase_id")
                    track_id = record.get("track_id")

                    # Store record as JSON in data column
                    data_json = json.dumps(record, default=str)

                    if table_name in ["campaign_phases", "decisions"]:
                        sql = f"INSERT OR REPLACE INTO {table_name} (id, data) VALUES (?, ?)"
                        self.cursor.execute(sql, (record_id, data_json))
                    elif table_name in ["tracks", "agents", "metrics", "requirements"]:
                        sql = f"INSERT OR REPLACE INTO {table_name} (id, phase_id, data) VALUES (?, ?, ?)"
                        self.cursor.execute(sql, (record_id, phase_id, data_json))
                    elif table_name == "deliverables":
                        sql = f"INSERT OR REPLACE INTO {table_name} (id, phase_id, track_id, data) VALUES (?, ?, ?, ?)"
                        self.cursor.execute(sql, (record_id, phase_id, track_id, data_json))
                    elif table_name == "relationships":
                        source_id = record.get("source_id")
                        target_id = record.get("target_id")
                        sql = f"INSERT OR REPLACE INTO {table_name} (id, source_id, target_id, data) VALUES (?, ?, ?, ?)"
                        self.cursor.execute(sql, (record_id, source_id, target_id, data_json))

                    count += 1

        self.conn.commit()
        return count

    def populate_fts_tables(self):
        """Populate FTS virtual tables from base tables."""

        # Build FTS tables - extract searchable fields from JSON
        self.cursor.execute("""
            INSERT INTO fts_phases(id, name, description)
            SELECT id,
                   json_extract(data, '$.name') as name,
                   json_extract(data, '$.description') as description
            FROM campaign_phases
        """)

        self.cursor.execute("""
            INSERT INTO fts_tracks(id, name, description)
            SELECT id,
                   json_extract(data, '$.name') as name,
                   json_extract(data, '$.description') as description
            FROM tracks
        """)

        self.cursor.execute("""
            INSERT INTO fts_deliverables(id, name)
            SELECT id, json_extract(data, '$.name') as name
            FROM deliverables
        """)

        self.cursor.execute("""
            INSERT INTO fts_decisions(id, description, rationale)
            SELECT id,
                   json_extract(data, '$.description') as description,
                   json_extract(data, '$.rationale') as rationale
            FROM decisions
        """)

        self.cursor.execute("""
            INSERT INTO fts_metrics(id, metric_name)
            SELECT id, json_extract(data, '$.metric_name') as metric_name
            FROM metrics
        """)

        self.conn.commit()

    def build_and_populate(self) -> Dict[str, int]:
        """Build schema and populate from JSONL."""
        results = {}

        # Create schema
        self.create_schema()

        # Load data
        results["campaign_phases"] = self.load_jsonl_into_table(
            "campaign_phases.jsonl", "campaign_phases"
        )
        results["tracks"] = self.load_jsonl_into_table("campaign_tracks.jsonl", "tracks")
        results["deliverables"] = self.load_jsonl_into_table("deliverables.jsonl", "deliverables")
        results["agents"] = self.load_jsonl_into_table("agents.jsonl", "agents")
        results["metrics"] = self.load_jsonl_into_table("metrics.jsonl", "metrics")
        results["decisions"] = self.load_jsonl_into_table("decisions.jsonl", "decisions")
        results["requirements"] = self.load_jsonl_into_table("requirements.jsonl", "requirements")
        results["relationships"] = self.load_jsonl_into_table(
            "relationships.jsonl", "relationships"
        )

        # Populate FTS
        self.populate_fts_tables()
        results["fts_tables"] = "populated"

        self.conn.close()
        return results


if __name__ == "__main__":
    builder = SQLiteIndexBuilder()
    results = builder.build_and_populate()
    print("=== SQLite Index Build Results ===")
    for entity_type, count in results.items():
        if isinstance(count, int):
            print(f"{entity_type}: {count} records")
        else:
            print(f"{entity_type}: {count}")
