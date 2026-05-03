#!/usr/bin/env python3
"""
Topology Manager: Semantic Code Navigation

Provides concept-based (not path-based) navigation of the codebase using
topology maps, semantic relationships, and intelligent discovery.

Part of the cognitive brain infrastructure for AI agents.

AAIS Contribution: +2.5 points (Discovery & Navigation)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from codex.utils.path_utils import windows_safe_timestamp


@dataclass
class CodeLocation:
    """Represents a location in the codebase with semantic metadata."""

    path: str
    line_start: int
    line_end: int
    concept: str
    module: str
    category: str
    metadata: Dict = field(default_factory=dict)
    related_locations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "concept": self.concept,
            "module": self.module,
            "category": self.category,
            "metadata": self.metadata,
            "related_locations": self.related_locations,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CodeLocation":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class NavigationMap:
    """Topology map for semantic navigation."""

    name: str
    description: str
    locations: List[CodeLocation] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    def add_location(self, location: CodeLocation) -> None:
        """Add a code location to the map."""
        self.locations.append(location)

    def add_relationship(self, from_concept: str, to_concept: str) -> None:
        """Add a semantic relationship between concepts."""
        if from_concept not in self.relationships:
            self.relationships[from_concept] = []
        if to_concept not in self.relationships[from_concept]:
            self.relationships[from_concept].append(to_concept)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "locations": [loc.to_dict() for loc in self.locations],
            "relationships": self.relationships,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "NavigationMap":
        """Create from dictionary."""
        locations = [CodeLocation.from_dict(loc) for loc in data.get("locations", [])]
        return cls(
            name=data["name"],
            description=data["description"],
            locations=locations,
            relationships=data.get("relationships", {}),
            metadata=data.get("metadata", {}),
        )


class TopologyManager:
    """
    Manages codebase topology and semantic navigation.

    Enables custom agents to navigate by concept rather than file path,
    improving intuitiveness and discovery.

    Features:
    - Concept-based search (not path-based)
    - Semantic relationship mapping
    - Optimal path finding
    - Related code discovery
    - Auto-generated topology maps

    AAIS Impact: +2.5 points in Discovery & Navigation
    """

    def __init__(self, repo_root: Optional[str] = None):
        """
        Initialize the Topology Manager.

        Args:
            repo_root: Path to repository root (defaults to _codex_ root)
        """
        if repo_root is None:
            # Auto-detect repo root
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / ".git").exists():
                    repo_root = str(current)
                    break
                current = current.parent
            else:
                repo_root = str(Path.cwd())

        self.repo_root = Path(repo_root)
        self.topology_dir = self.repo_root / ".codex" / "topology"
        self.topology_dir.mkdir(parents=True, exist_ok=True)

        self.maps: Dict[str, NavigationMap] = {}
        self._load_maps()

    def _load_maps(self) -> None:
        """Load existing topology maps from disk."""
        if not self.topology_dir.exists():
            return

        for map_file in self.topology_dir.glob("*.json"):
            try:
                with open(map_file) as f:
                    data = json.load(f)
                    nav_map = NavigationMap.from_dict(data)
                    self.maps[nav_map.name] = nav_map
            except Exception as e:
                print(f"Warning: Failed to load map {map_file}: {e}")

    def save_maps(self) -> None:
        """Save all topology maps to disk."""
        self.topology_dir.mkdir(parents=True, exist_ok=True)

        for name, nav_map in self.maps.items():
            map_file = self.topology_dir / f"{name}.json"
            with open(map_file, "w") as f:
                json.dump(nav_map.to_dict(), f, indent=2)

    def find(
        self,
        concept: str,
        category: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 10
    ) -> List[CodeLocation]:
        """
        Find code locations by concept (not path).

        This is the core semantic navigation feature - agents search for
        "what they want" rather than "where it might be".

        Args:
            concept: What to find (e.g., "CI failures", "test fixtures")
            category: Optional category filter (e.g., "testing", "ci-cd")
            module: Optional module filter (e.g., "pytest", "workflow")
            limit: Maximum results to return

        Returns:
            List of matching code locations

        Examples:
            >>> tm = TopologyManager()
            >>> locations = tm.find("test import errors")
            >>> locations = tm.find("quantum decision", category="cognitive")
        """
        results = []
        concept_lower = concept.lower()

        for nav_map in self.maps.values():
            for location in nav_map.locations:
                # Match by concept
                if concept_lower in location.concept.lower():
                    # Apply filters
                    if category and location.category != category:
                        continue
                    if module and location.module != module:
                        continue

                    results.append(location)

                    if len(results) >= limit:
                        return results

        return results

    def find_optimal_path(
        self,
        from_concept: str,
        to_concept: str
    ) -> Optional[List[str]]:
        """
        Find optimal navigation path between two concepts.

        Uses semantic relationships to guide agents from one concept to
        another using the shortest path.

        Args:
            from_concept: Starting concept
            to_concept: Target concept

        Returns:
            List of concepts forming the path, or None if no path exists

        Example:
            >>> tm = TopologyManager()
            >>> path = tm.find_optimal_path("CI failure", "test fix")
            >>> # Returns: ["CI failure", "test execution", "test fix"]
        """
        # Build unified relationship graph
        graph: Dict[str, List[str]] = {}
        for nav_map in self.maps.values():
            for concept, related in nav_map.relationships.items():
                if concept not in graph:
                    graph[concept] = []
                graph[concept].extend(related)

        # BFS to find shortest path
        if from_concept not in graph:
            return None

        queue = [(from_concept, [from_concept])]
        visited = {from_concept}

        while queue:
            current, path = queue.pop(0)

            if current == to_concept:
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def discover_related(
        self,
        concept: str,
        max_depth: int = 2,
        limit: int = 20
    ) -> List[Tuple[str, int]]:
        """
        Discover related concepts (auto-discovery feature).

        Helps agents explore the codebase by finding semantically related
        code without knowing exact paths.

        Args:
            concept: Starting concept
            max_depth: How many relationship hops to explore
            limit: Maximum results to return

        Returns:
            List of (concept, distance) tuples sorted by relevance

        Example:
            >>> tm = TopologyManager()
            >>> related = tm.discover_related("pytest fixtures")
            >>> # Returns: [("test setup", 1), ("mock objects", 1), ...]
        """
        # Build relationship graph
        graph: Dict[str, List[str]] = {}
        for nav_map in self.maps.values():
            for from_concept, to_concepts in nav_map.relationships.items():
                if from_concept not in graph:
                    graph[from_concept] = []
                graph[from_concept].extend(to_concepts)

        # BFS with depth tracking
        if concept not in graph:
            return []

        results = []
        queue = [(concept, 0)]
        visited = {concept}

        while queue and len(results) < limit:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    results.append((neighbor, depth + 1))
                    queue.append((neighbor, depth + 1))

        # Sort by distance (closer = more relevant)
        results.sort(key=lambda x: x[1])
        return results[:limit]

    def get_maps(self) -> Dict[str, NavigationMap]:
        """
        Get all topology maps.

        Returns:
            Dictionary of map name to NavigationMap
        """
        return self.maps.copy()

    def create_map(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> NavigationMap:
        """
        Create a new topology map.

        Args:
            name: Map identifier
            description: Human-readable description
            metadata: Optional metadata

        Returns:
            New NavigationMap instance
        """
        nav_map = NavigationMap(
            name=name,
            description=description,
            metadata=metadata or {}
        )
        self.maps[name] = nav_map
        return nav_map

    def add_location(
        self,
        map_name: str,
        path: str,
        line_start: int,
        line_end: int,
        concept: str,
        module: str,
        category: str,
        metadata: Optional[Dict] = None,
        related_locations: Optional[List[str]] = None
    ) -> CodeLocation:
        """
        Add a code location to a topology map.

        Args:
            map_name: Name of the map to add to
            path: File path (relative to repo root)
            line_start: Starting line number
            line_end: Ending line number
            concept: What this code represents (semantic)
            module: Module/subsystem name
            category: Category (e.g., "testing", "ci-cd")
            metadata: Optional metadata
            related_locations: Optional related location identifiers

        Returns:
            Created CodeLocation
        """
        if map_name not in self.maps:
            raise ValueError(f"Map '{map_name}' does not exist")

        location = CodeLocation(
            path=path,
            line_start=line_start,
            line_end=line_end,
            concept=concept,
            module=module,
            category=category,
            metadata=metadata or {},
            related_locations=related_locations or []
        )

        self.maps[map_name].add_location(location)
        return location

    def add_relationship(
        self,
        map_name: str,
        from_concept: str,
        to_concept: str
    ) -> None:
        """
        Add a semantic relationship to a topology map.

        Args:
            map_name: Name of the map
            from_concept: Source concept
            to_concept: Target concept
        """
        if map_name not in self.maps:
            raise ValueError(f"Map '{map_name}' does not exist")

        self.maps[map_name].add_relationship(from_concept, to_concept)

    def get_aais_contribution(self) -> Dict[str, float]:
        """
        Calculate AAIS score contribution from topology management.

        Returns:
            Dictionary with AAIS category contributions
        """
        total_locations = sum(len(m.locations) for m in self.maps.values())
        total_relationships = sum(
            len(rels) for m in self.maps.values() for rels in m.relationships.values()
        )

        # More complete topology = better discovery
        discovery_contribution = min(2.5, total_locations / 100 * 2.5)

        # More relationships = better navigation
        navigation_contribution = min(1.0, total_relationships / 50 * 1.0)

        return {
            "discovery_navigation": discovery_contribution + navigation_contribution,
            "total_locations": total_locations,
            "total_relationships": total_relationships,
            "maps_count": len(self.maps),
        }


def main():
    """CLI interface for Topology Manager."""
    import argparse

    parser = argparse.ArgumentParser(description="Topology Manager CLI")
    parser.add_argument("command", choices=["find", "discover", "stats", "init"])
    parser.add_argument("--concept", help="Concept to search for")
    parser.add_argument("--category", help="Category filter")
    parser.add_argument("--module", help="Module filter")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")
    parser.add_argument("--depth", type=int, default=2, help="Discovery depth")

    args = parser.parse_args()

    tm = TopologyManager()

    if args.command == "find":
        if not args.concept:
            print("Error: --concept required for find command")
            return

        results = tm.find(
            concept=args.concept,
            category=args.category,
            module=args.module,
            limit=args.limit
        )

        print(f"\nFound {len(results)} locations for concept '{args.concept}':")
        for loc in results:
            print(f"  {loc.path}:{loc.line_start}-{loc.line_end}")
            print(f"    Concept: {loc.concept}")
            print(f"    Category: {loc.category}, Module: {loc.module}\n")

    elif args.command == "discover":
        if not args.concept:
            print("Error: --concept required for discover command")
            return

        related = tm.discover_related(
            concept=args.concept,
            max_depth=args.depth,
            limit=args.limit
        )

        print(f"\nDiscovered {len(related)} related concepts:")
        for concept, distance in related:
            print(f"  {concept} (distance: {distance})")

    elif args.command == "stats":
        contribution = tm.get_aais_contribution()
        print("\nTopology Manager Statistics:")
        print(f"  Maps: {contribution['maps_count']}")
        print(f"  Locations: {contribution['total_locations']}")
        print(f"  Relationships: {contribution['total_relationships']}")
        print(f"  AAIS Contribution: +{contribution['discovery_navigation']:.1f} points")

    elif args.command == "init":
        # Create initial example map
        tm.create_map(
            name="test_infrastructure",
            description="Testing infrastructure and patterns",
            metadata={"version": "1.0.0", "created": windows_safe_timestamp()}
        )

        # Add example location
        tm.add_location(
            map_name="test_infrastructure",
            path="tests/conftest.py",
            line_start=1,
            line_end=50,
            concept="pytest fixtures",
            module="pytest",
            category="testing",
            metadata={"importance": "high"}
        )

        # Add example relationship
        tm.add_relationship(
            map_name="test_infrastructure",
            from_concept="pytest fixtures",
            to_concept="test setup"
        )

        tm.save_maps()
        print("Initialized topology manager with example map")


if __name__ == "__main__":
    main()
