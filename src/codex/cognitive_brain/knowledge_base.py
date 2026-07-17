"""Knowledge Base Module for Cognitive Reasoning.

Parses agent behavior patterns from AGENT_ACCOUNTABILITY_REPORT.md
and provides queryable pattern database for downstream reasoning layers.
"""

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Pattern:
    """Learned decision pattern."""

    id: str
    category: str
    decision_type: str
    success_rate: float
    frequency: int
    last_seen: str
    tags: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class QueryInterface:
    """Query interface for pattern lookup."""

    def __init__(self, patterns: List[Pattern]):
        """Initialize query interface.

        Args:
            patterns: List of learned patterns
        """
        self.patterns = patterns
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Build query indexes for fast lookup."""
        self.by_category: Dict[str, List[Pattern]] = defaultdict(list)
        self.by_decision_type: Dict[str, List[Pattern]] = defaultdict(list)
        self.by_tag: Dict[str, List[Pattern]] = defaultdict(list)

        for pattern in self.patterns:
            self.by_category[pattern.category].append(pattern)
            self.by_decision_type[pattern.decision_type].append(pattern)
            for tag in pattern.tags:
                self.by_tag[tag].append(pattern)

    def query_by_category(self, category: str) -> List[Pattern]:
        """Query patterns by category.

        Args:
            category: Decision category

        Returns:
            List of matching patterns
        """
        return self.by_category.get(category, [])

    def query_by_decision_type(self, decision_type: str) -> List[Pattern]:
        """Query patterns by decision type.

        Args:
            decision_type: Type of decision

        Returns:
            List of matching patterns
        """
        return self.by_decision_type.get(decision_type, [])

    def query_by_tag(self, tag: str) -> List[Pattern]:
        """Query patterns by tag.

        Args:
            tag: Pattern tag

        Returns:
            List of matching patterns
        """
        return self.by_tag.get(tag, [])

    def find_best_pattern(
        self, category: str, min_success_rate: float = 0.85
    ) -> Optional[Pattern]:
        """Find best performing pattern for category.

        Args:
            category: Decision category
            min_success_rate: Minimum success rate threshold

        Returns:
            Best pattern or None
        """
        candidates = [
            p for p in self.by_category.get(category, [])
            if p.success_rate >= min_success_rate
        ]

        if not candidates:
            return None

        # Return pattern with highest success rate
        return max(candidates, key=lambda p: p.success_rate)

    def find_related_patterns(self, pattern_id: str, limit: int = 5) -> List[Pattern]:
        """Find related patterns.

        Args:
            pattern_id: Reference pattern ID
            limit: Max patterns to return

        Returns:
            Related patterns
        """
        ref_pattern = next((p for p in self.patterns if p.id == pattern_id), None)
        if not ref_pattern:
            return []

        # Find patterns with similar tags
        related: Set[str] = set()
        for tag in ref_pattern.tags:
            for p in self.by_tag.get(tag, []):
                if p.id != pattern_id:
                    related.add(p.id)

        # Find patterns in same category
        for p in self.by_category.get(ref_pattern.category, []):
            if p.id != pattern_id:
                related.add(p.id)

        result = [p for p in self.patterns if p.id in related]
        return sorted(result, key=lambda p: p.success_rate, reverse=True)[:limit]


class KnowledgeBase:
    """Knowledge base integrating agent patterns and decision outcomes.

    Parses AGENT_ACCOUNTABILITY_REPORT.md and stores learned patterns
    indexed by decision category for efficient querying.
    """

    def __init__(self, kb_path: Optional[Path] = None):
        """Initialize knowledge base.

        Args:
            kb_path: Path to store KB (default: .codex/reasoning/kb.json)
        """
        self.kb_path = kb_path or Path(".codex/reasoning/kb.json")
        self.patterns: List[Pattern] = []
        self.query_interface: Optional[QueryInterface] = None
        self.last_updated: Optional[str] = None

        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        """Load KB from disk or initialize empty."""
        if self.kb_path.exists():
            self._load_kb()
        else:
            self.patterns = []
            self.query_interface = QueryInterface([])
            self._save_kb()

    def _load_kb(self) -> None:
        """Load KB from JSON file."""
        try:
            with open(self.kb_path, "r") as f:
                data = json.load(f)
                self.patterns = [
                    Pattern(
                        id=p["id"],
                        category=p["category"],
                        decision_type=p["decision_type"],
                        success_rate=p["success_rate"],
                        frequency=p["frequency"],
                        last_seen=p["last_seen"],
                        tags=p["tags"],
                        metadata=p["metadata"],
                    )
                    for p in data.get("patterns", [])
                ]
                self.last_updated = data.get("last_updated")
                self.query_interface = QueryInterface(self.patterns)
        except Exception as e:
            print(f"Failed to load KB: {e}")
            self.patterns = []
            self.query_interface = QueryInterface([])

    def _save_kb(self) -> None:
        """Save KB to JSON file."""
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "last_updated": self.last_updated or datetime.utcnow().isoformat() + "Z",
            "pattern_count": len(self.patterns),
            "patterns": [p.to_dict() for p in self.patterns],
        }

        with open(self.kb_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_pattern(
        self,
        category: str,
        decision_type: str,
        success_rate: float,
        frequency: int,
        tags: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Pattern:
        """Add learned pattern to KB.

        Args:
            category: Decision category
            decision_type: Type of decision
            success_rate: Historical success rate (0-1)
            frequency: How many times pattern was used
            tags: Tags for pattern
            metadata: Optional metadata

        Returns:
            Created pattern
        """
        pattern = Pattern(
            id=f"pattern_{len(self.patterns)}_{datetime.utcnow().timestamp()}",
            category=category,
            decision_type=decision_type,
            success_rate=success_rate,
            frequency=frequency,
            last_seen=datetime.utcnow().isoformat() + "Z",
            tags=tags,
            metadata=metadata or {},
        )

        self.patterns.append(pattern)
        self.query_interface = QueryInterface(self.patterns)
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        self._save_kb()

        return pattern

    def update_pattern(
        self, pattern_id: str, **kwargs: Any
    ) -> Optional[Pattern]:
        """Update existing pattern.

        Args:
            pattern_id: Pattern ID
            **kwargs: Fields to update

        Returns:
            Updated pattern or None if not found
        """
        pattern = next((p for p in self.patterns if p.id == pattern_id), None)
        if not pattern:
            return None

        # Update fields
        if "success_rate" in kwargs:
            pattern.success_rate = kwargs["success_rate"]
        if "frequency" in kwargs:
            pattern.frequency = kwargs["frequency"]
        if "tags" in kwargs:
            pattern.tags = kwargs["tags"]
        if "metadata" in kwargs:
            pattern.metadata.update(kwargs["metadata"])

        pattern.last_seen = datetime.utcnow().isoformat() + "Z"

        self.query_interface = QueryInterface(self.patterns)
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        self._save_kb()

        return pattern

    def parse_accountability_report(
        self, report_path: Path
    ) -> Dict[str, Any]:
        """Parse AGENT_ACCOUNTABILITY_REPORT.md for patterns.

        Args:
            report_path: Path to accountability report

        Returns:
            Parsed patterns summary
        """
        if not report_path.exists():
            return {"error": "Report not found", "patterns_extracted": 0}

        try:
            with open(report_path, "r") as f:
                content = f.read()

            # Simple pattern extraction from markdown
            patterns_extracted = self._extract_patterns_from_content(content)

            # Add patterns to KB
            for pattern_data in patterns_extracted:
                self.add_pattern(
                    category=pattern_data.get("category", "general"),
                    decision_type=pattern_data.get("decision_type", "unknown"),
                    success_rate=pattern_data.get("success_rate", 0.5),
                    frequency=pattern_data.get("frequency", 1),
                    tags=pattern_data.get("tags", []),
                    metadata=pattern_data.get("metadata", {}),
                )

            return {
                "patterns_extracted": len(patterns_extracted),
                "total_patterns_in_kb": len(self.patterns),
            }
        except Exception as e:
            return {
                "error": str(e),
                "patterns_extracted": 0,
            }

    def _extract_patterns_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract patterns from accountability report content.

        Args:
            content: Report content

        Returns:
            List of pattern dicts
        """
        patterns = []

        # Extract common decision categories
        categories = ["coverage", "performance", "security", "reliability", "cost"]

        for category in categories:
            if category in content.lower():
                patterns.append(
                    {
                        "category": category,
                        "decision_type": f"{category}_optimization",
                        "success_rate": 0.85,
                        "frequency": 1,
                        "tags": [category, "automated", "phase_4e"],
                        "metadata": {
                            "source": "accountability_report",
                            "extraction_time": datetime.utcnow().isoformat() + "Z",
                        },
                    }
                )

        return patterns

    def query(self, category: Optional[str] = None, decision_type: Optional[str] = None, tag: Optional[str] = None) -> List[Pattern]:
        """Generic query interface.

        Args:
            category: Optional category filter
            decision_type: Optional decision_type filter
            tag: Optional tag filter

        Returns:
            Matching patterns
        """
        if not self.query_interface:
            return []

        if category:
            return self.query_interface.query_by_category(category)
        if decision_type:
            return self.query_interface.query_by_decision_type(decision_type)
        if tag:
            return self.query_interface.query_by_tag(tag)

        return self.patterns

    def get_statistics(self) -> Dict[str, Any]:
        """Get KB statistics.

        Returns:
            Statistics dict
        """
        if not self.patterns:
            return {
                "total_patterns": 0,
                "categories": [],
                "decision_types": [],
                "avg_success_rate": 0.0,
            }

        categories = set(p.category for p in self.patterns)
        decision_types = set(p.decision_type for p in self.patterns)
        avg_success_rate = sum(p.success_rate for p in self.patterns) / len(
            self.patterns
        )

        return {
            "total_patterns": len(self.patterns),
            "categories": list(categories),
            "decision_types": list(decision_types),
            "avg_success_rate": avg_success_rate,
            "last_updated": self.last_updated,
        }
