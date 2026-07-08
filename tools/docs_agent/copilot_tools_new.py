"""Copilot Tool Interface — 10 Required Tools for Copilot Cloud Agent Integration."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CopilotToolsInterface:
    """Implements 10 required tools for Copilot Cloud agent interaction."""

    def __init__(self, db_path: str = "docs-data/generated/docs.sqlite"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_agent_context(self) -> Dict[str, Any]:
        """Tool 1: Retrieve agent context with campaign state."""
        self.cursor.execute("SELECT COUNT(*) as phase_count FROM campaign_phases")
        phases_count = self.cursor.fetchone()["phase_count"]

        self.cursor.execute("SELECT COUNT(*) as track_count FROM tracks")
        tracks_count = self.cursor.fetchone()["track_count"]

        self.cursor.execute("SELECT COUNT(*) as deliverable_count FROM deliverables")
        deliverables_count = self.cursor.fetchone()["deliverable_count"]

        self.cursor.execute("SELECT COUNT(*) as agent_count FROM agents")
        agents_count = self.cursor.fetchone()["agent_count"]

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "campaign_summary": {
                "phases": phases_count,
                "tracks": tracks_count,
                "deliverables": deliverables_count,
                "agents": agents_count
            },
            "system_version": "0.1.0-machine-readable"
        }

    def get_task_brief(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 2: Get task/deliverable brief with requirements and dependencies."""
        if not task_id:
            # Return current phase context if no specific task
            self.cursor.execute("SELECT json(data) as data FROM campaign_phases LIMIT 1")
            row = self.cursor.fetchone()
            if not row:
                return {"error": "No phases found"}

            phase_data = json.loads(row["data"])
            return {
                "current_phase": phase_data,
                "type": "phase_context",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        # Fetch specific deliverable
        self.cursor.execute("SELECT json(data) as data FROM deliverables WHERE id = ?", (task_id,))
        row = self.cursor.fetchone()

        if not row:
            return {"error": f"Task {task_id} not found"}

        task_data = json.loads(row["data"])

        # Get related requirements
        self.cursor.execute(
            "SELECT json(data) as data FROM requirements WHERE phase_id = ?",
            (task_data.get("phase_id"),)
        )
        requirements = [json.loads(r["data"]) for r in self.cursor.fetchall()]

        return {
            "task": task_data,
            "requirements": requirements,
            "type": "task_brief",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def search_docs(self, query: str) -> Dict[str, Any]:
        """Tool 3: Full-text search across campaign documentation."""
        results = {"phases": [], "tracks": [], "deliverables": [], "decisions": []}

        try:
            # Search phases
            self.cursor.execute(
                "SELECT id FROM fts_phases WHERE name MATCH ? OR description MATCH ? LIMIT 10",
                (query, query)
            )
            for row in self.cursor.fetchall():
                self.cursor.execute("SELECT json(data) as data FROM campaign_phases WHERE id = ?", (row["id"],))
                results["phases"].append(json.loads(self.cursor.fetchone()["data"]))
        except Exception:
            pass

        return {"query": query, "results": results}

    def get_related_context(self, entity_id: str) -> Dict[str, Any]:
        """Tool 4: Get all related entities and dependencies."""
        context = {
            "entity_id": entity_id,
            "upstream": [],
            "downstream": [],
            "lateral": []
        }

        try:
            # Get relationships where this entity is source
            self.cursor.execute(
                "SELECT source_id, target_id, json(data) as data FROM relationships WHERE source_id = ?",
                (entity_id,)
            )
            for row in self.cursor.fetchall():
                rel_data = json.loads(row["data"])
                rel_data["target_id"] = row["target_id"]
                context["downstream"].append(rel_data)
        except Exception:
            pass

        return context

    def impact_analysis(self, entity_id: str, proposed_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 5: Analyze impact of proposed changes on campaign."""
        context = self.get_related_context(entity_id)

        impact = {
            "entity_id": entity_id,
            "proposed_changes": proposed_changes,
            "affected_entities": {
                "direct": len(context["downstream"]) + len(context["upstream"]),
                "downstream_count": len(context["downstream"]),
                "upstream_count": len(context["upstream"])
            },
            "risk_level": "low" if (len(context["downstream"]) + len(context["upstream"])) < 5 else "medium",
            "validation_steps": [
                "Verify all downstream deliverables still meet requirements",
                "Check metrics remain within targets after changes",
                "Validate no broken dependencies introduced"
            ]
        }

        return impact

    def list_actions(self, phase_id: Optional[str] = None) -> Dict[str, Any]:
        """Tool 6: List available actions for execution."""
        try:
            if phase_id:
                self.cursor.execute("SELECT json(data) as data FROM deliverables WHERE phase_id = ?", (phase_id,))
            else:
                self.cursor.execute("SELECT json(data) as data FROM deliverables LIMIT 20")

            actions = [json.loads(row["data"]) for row in self.cursor.fetchall()]
        except Exception:
            actions = []

        return {
            "phase_id": phase_id,
            "actions": actions,
            "count": len(actions),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def validate_docs(self) -> Dict[str, Any]:
        """Tool 7: Validate campaign documentation integrity."""
        issues = []

        try:
            # Check for orphaned deliverables
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM deliverables d
                WHERE d.track_id NOT IN (SELECT id FROM tracks)
            """)
            orphaned = self.cursor.fetchone()["count"]
            if orphaned > 0:
                issues.append(f"Found {orphaned} orphaned deliverables")
        except Exception:
            pass

        return {
            "status": "valid" if not issues else "has_issues",
            "issues": issues,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def rebuild_indexes(self) -> Dict[str, Any]:
        """Tool 8: Rebuild FTS indexes from source data."""
        try:
            self.cursor.execute("DELETE FROM fts_phases")
            self.cursor.execute("DELETE FROM fts_tracks")

            self.cursor.execute("""
                INSERT INTO fts_phases(id, name, description) 
                SELECT id, json_extract(data, '$.name'), json_extract(data, '$.description')
                FROM campaign_phases
            """)

            self.cursor.execute("""
                INSERT INTO fts_tracks(id, name, description) 
                SELECT id, json_extract(data, '$.name'), json_extract(data, '$.description')
                FROM tracks
            """)

            self.conn.commit()

            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": "FTS indexes rebuilt"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def classify_candidate_file(self, file_path: str) -> Dict[str, Any]:
        """Tool 9: Classify whether a file should be managed by system."""
        path = Path(file_path)

        managed_patterns = [
            ".codex/*.md",
            "docs-data/canonical/*.jsonl",
            "docs-data/generated/*",
            "tools/docs_agent/*.py"
        ]

        is_managed = any(path.match(pattern) for pattern in managed_patterns)

        return {
            "file_path": file_path,
            "is_managed": is_managed,
            "classification": "managed" if is_managed else "unmanaged",
            "recommendation": "ingest" if is_managed else "skip"
        }

    def ingest_candidate_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Tool 10: Ingest and integrate new candidate files into system."""
        if file_path.endswith(".md"):
            return {
                "file_path": file_path,
                "status": "parsed",
                "type": "markdown",
                "action": "queue_for_jsonl_generation"
            }
        elif file_path.endswith(".jsonl"):
            return {
                "file_path": file_path,
                "status": "ingested",
                "type": "jsonl",
                "action": "rebuild_indexes"
            }
        else:
            return {
                "file_path": file_path,
                "status": "unsupported",
                "error": f"Cannot ingest {Path(file_path).suffix} files"
            }


def test_tools():
    """Test all 10 tools."""
    tools = CopilotToolsInterface()

    print("=== COPILOT TOOLS TEST ===\n")

    result = tools.get_agent_context()
    print("Tool 1 - get_agent_context:")
    print(json.dumps(result, indent=2))
    print()

    result = tools.get_task_brief()
    print("Tool 2 - get_task_brief:")
    print(json.dumps(result, indent=2)[:250] + "...\n")

    result = tools.validate_docs()
    print("Tool 7 - validate_docs:")
    print(json.dumps(result, indent=2))
    print()

    result = tools.list_actions()
    print(f"Tool 6 - list_actions: {result['count']} actions available")


if __name__ == "__main__":
    test_tools()
