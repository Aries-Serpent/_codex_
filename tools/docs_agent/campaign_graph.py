"""Campaign graph construction — builds directed relationship graph from JSONL records."""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import hashlib
import uuid


class CampaignGraphBuilder:
    """Constructs directed graph of campaign entities and relationships."""

    def __init__(self, canonical_dir: str = "docs-data/canonical", output_dir: str = "docs-data/generated"):
        self.canonical_dir = Path(canonical_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all JSONL records
        self.phases = self._load_jsonl("campaign_phases.jsonl")
        self.tracks = self._load_jsonl("campaign_tracks.jsonl")
        self.deliverables = self._load_jsonl("deliverables.jsonl")
        self.agents = self._load_jsonl("agents.jsonl")
        self.metrics = self._load_jsonl("metrics.jsonl")
        self.decisions = self._load_jsonl("decisions.jsonl")
        self.timeline_events = self._load_jsonl("timeline_events.jsonl")
        self.requirements = self._load_jsonl("requirements.jsonl")
        self.documents = self._load_jsonl("documents.jsonl")
        
        # Build relationships
        self.relationships = []

    def _load_jsonl(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSONL file into memory."""
        filepath = self.canonical_dir / filename
        if not filepath.exists():
            return []
        
        records = []
        with open(filepath) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _make_relationship_id(self, source_id: str, target_id: str, rel_type: str) -> str:
        """Generate deterministic relationship ID."""
        source = f"{source_id}::{rel_type}::{target_id}"
        hash_digest = hashlib.md5(source.encode()).hexdigest()
        return str(uuid.UUID(hex=hash_digest))

    def build_phase_to_track_relationships(self):
        """Add Phase → Track relationships."""
        for track in self.tracks:
            if "phase_id" in track:
                rel = {
                    "id": self._make_relationship_id(track["phase_id"], track["id"], "has_track"),
                    "source_id": track["phase_id"],
                    "source_type": "phase",
                    "target_id": track["id"],
                    "target_type": "track",
                    "relationship_type": "has_track",
                    "weight": 1.0,
                    "status": "active"
                }
                self.relationships.append(rel)

    def build_track_to_deliverable_relationships(self):
        """Add Track → Deliverable relationships."""
        for deliverable in self.deliverables:
            if "track_id" in deliverable:
                rel = {
                    "id": self._make_relationship_id(deliverable["track_id"], deliverable["id"], "has_deliverable"),
                    "source_id": deliverable["track_id"],
                    "source_type": "track",
                    "target_id": deliverable["id"],
                    "target_type": "deliverable",
                    "relationship_type": "has_deliverable",
                    "weight": 1.0,
                    "status": "active"
                }
                self.relationships.append(rel)

    def build_deliverable_to_agent_relationships(self):
        """Add Deliverable → Agent relationships (ownership/assignment)."""
        # Simplified: each agent is assigned to the tracks in their phase
        for agent in self.agents:
            if "phase_id" in agent and "assigned_to_tracks" in agent:
                phase_id = agent["phase_id"]
                # Find tracks in this phase
                phase_tracks = [t for t in self.tracks if t.get("phase_id") == phase_id]
                for track in phase_tracks:
                    # Find deliverables in this track
                    track_deliverables = [d for d in self.deliverables if d.get("track_id") == track["id"]]
                    for deliverable in track_deliverables:
                        rel = {
                            "id": self._make_relationship_id(agent["id"], deliverable["id"], "manages"),
                            "source_id": agent["id"],
                            "source_type": "agent",
                            "target_id": deliverable["id"],
                            "target_type": "deliverable",
                            "relationship_type": "manages",
                            "weight": 0.7,
                            "status": "active"
                        }
                        self.relationships.append(rel)

    def build_metric_feedback_relationships(self):
        """Add Metric → Deliverable feedback relationships."""
        for metric in self.metrics:
            if "phase_id" in metric:
                phase_id = metric["phase_id"]
                # Find deliverables in this phase
                phase_deliverables = [d for d in self.deliverables if d.get("phase_id") == phase_id]
                for deliverable in phase_deliverables:
                    rel = {
                        "id": self._make_relationship_id(metric["id"], deliverable["id"], "measures"),
                        "source_id": metric["id"],
                        "source_type": "metric",
                        "target_id": deliverable["id"],
                        "target_type": "deliverable",
                        "relationship_type": "measures",
                        "weight": 0.5,
                        "status": "active"
                    }
                    self.relationships.append(rel)

    def build_requirement_to_deliverable_relationships(self):
        """Add Requirement → Deliverable relationships."""
        for requirement in self.requirements:
            if "phase_id" in requirement:
                phase_id = requirement["phase_id"]
                # Find deliverables in this phase
                phase_deliverables = [d for d in self.deliverables if d.get("phase_id") == phase_id]
                for deliverable in phase_deliverables:
                    rel = {
                        "id": self._make_relationship_id(requirement["id"], deliverable["id"], "constrains"),
                        "source_id": requirement["id"],
                        "source_type": "requirement",
                        "target_id": deliverable["id"],
                        "target_type": "deliverable",
                        "relationship_type": "constrains",
                        "weight": 0.8,
                        "status": "active"
                    }
                    self.relationships.append(rel)

    def build_decision_to_phase_relationships(self):
        """Add Decision → Phase relationships."""
        for decision in self.decisions:
            if "phase_id" in decision:
                rel = {
                    "id": self._make_relationship_id(decision["id"], decision["phase_id"], "gates"),
                    "source_id": decision["id"],
                    "source_type": "decision",
                    "target_id": decision["phase_id"],
                    "target_type": "phase",
                    "relationship_type": "gates",
                    "weight": 1.0,
                    "status": "active"
                }
                self.relationships.append(rel)

    def build_all_relationships(self):
        """Build complete relationship graph."""
        self.build_phase_to_track_relationships()
        self.build_track_to_deliverable_relationships()
        self.build_deliverable_to_agent_relationships()
        self.build_metric_feedback_relationships()
        self.build_requirement_to_deliverable_relationships()
        self.build_decision_to_phase_relationships()
        
        return self.relationships

    def write_relationships_jsonl(self) -> int:
        """Write relationships to JSONL file."""
        output_file = self.output_dir / "relationships.jsonl"
        with open(output_file, "w") as f:
            for rel in self.relationships:
                f.write(json.dumps(rel, default=str) + "\n")
        return len(self.relationships)

    def build_and_export(self) -> Dict[str, int]:
        """Execute complete graph build and export."""
        self.build_all_relationships()
        rel_count = self.write_relationships_jsonl()
        
        return {
            "relationships": rel_count,
            "phases": len(self.phases),
            "tracks": len(self.tracks),
            "deliverables": len(self.deliverables),
            "agents": len(self.agents),
            "metrics": len(self.metrics),
            "decisions": len(self.decisions)
        }


if __name__ == "__main__":
    builder = CampaignGraphBuilder()
    results = builder.build_and_export()
    print("=== Campaign Graph Build Results ===")
    for entity_type, count in results.items():
        print(f"{entity_type}: {count}")
