"""
Tests for Topology Manager - Semantic Code Navigation

Tests the topology manager's ability to provide concept-based navigation
and semantic code discovery.
"""

import tempfile
from pathlib import Path

import pytest

from scripts.cognitive.topology_manager import (
    CodeLocation,
    NavigationMap,
    TopologyManager,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        # Create .git to mark as repo root
        (repo_path / ".git").mkdir()
        (repo_path / ".codex").mkdir()
        (repo_path / ".codex" / "topology").mkdir(parents=True)
        yield str(repo_path)


@pytest.fixture
def topology_manager(temp_repo):
    """Create a TopologyManager instance for testing."""
    return TopologyManager(repo_root=temp_repo)


@pytest.fixture
def sample_map(topology_manager):
    """Create a sample navigation map with test data."""
    nav_map = topology_manager.create_map(
        name="test_map", description="Test navigation map", metadata={"version": "1.0.0"}
    )

    # Add sample locations
    topology_manager.add_location(
        map_name="test_map",
        path="tests/test_example.py",
        line_start=10,
        line_end=20,
        concept="pytest fixtures",
        module="pytest",
        category="testing",
    )

    topology_manager.add_location(
        map_name="test_map",
        path="tests/conftest.py",
        line_start=1,
        line_end=50,
        concept="test setup",
        module="pytest",
        category="testing",
    )

    topology_manager.add_location(
        map_name="test_map",
        path="src/utils/test_helpers.py",
        line_start=100,
        line_end=150,
        concept="mock objects",
        module="unittest",
        category="testing",
    )

    # Add relationships
    topology_manager.add_relationship("test_map", "pytest fixtures", "test setup")
    topology_manager.add_relationship("test_map", "test setup", "mock objects")

    return nav_map


class TestCodeLocation:
    """Test CodeLocation dataclass."""

    def test_code_location_creation(self):
        """Test creating a CodeLocation."""
        location = CodeLocation(
            path="src/example.py",
            line_start=10,
            line_end=20,
            concept="test fixture",
            module="pytest",
            category="testing",
        )

        assert location.path == "src/example.py", "path is not valid"
        assert location.line_start == 10, "line_start is not valid"
        assert location.line_end == 20, "line_end is not valid"
        assert location.concept == "test fixture", "concept is not valid"
        assert location.module == "pytest", "module is not valid"
        assert location.category == "testing", "category is not valid"

    def test_code_location_serialization(self):
        """Test CodeLocation to_dict and from_dict."""
        location = CodeLocation(
            path="src/example.py",
            line_start=10,
            line_end=20,
            concept="test fixture",
            module="pytest",
            category="testing",
            metadata={"importance": "high"},
            related_locations=["loc1", "loc2"],
        )

        # Serialize
        data = location.to_dict()
        assert data["path"] == "src/example.py", "Data must not be empty"
        assert data["concept"] == "test fixture", "Data must not be empty"
        assert data["metadata"]["importance"] == "high", "Data must not be empty"

        # Deserialize
        restored = CodeLocation.from_dict(data)
        assert restored.path == location.path, "path is not valid"
        assert restored.concept == location.concept, "concept is not valid"
        assert restored.metadata == location.metadata, "Data must not be empty"


class TestNavigationMap:
    """Test NavigationMap class."""

    def test_navigation_map_creation(self):
        """Test creating a NavigationMap."""
        nav_map = NavigationMap(name="test_map", description="Test map")

        assert nav_map.name == "test_map", "name is not valid"
        assert nav_map.description == "Test map", "description is not valid"
        assert len(nav_map.locations) == 0, "Collection must not be empty"
        assert len(nav_map.relationships) == 0, "Collection must not be empty"

    def test_add_location(self):
        """Test adding locations to a map."""
        nav_map = NavigationMap(name="test", description="Test")
        location = CodeLocation(
            path="test.py",
            line_start=1,
            line_end=10,
            concept="test",
            module="test",
            category="test",
        )

        nav_map.add_location(location)
        assert len(nav_map.locations) == 1, "Collection must not be empty"
        assert nav_map.locations[0] == location, "Condition must be true"

    def test_add_relationship(self):
        """Test adding relationships between concepts."""
        nav_map = NavigationMap(name="test", description="Test")

        nav_map.add_relationship("concept_a", "concept_b")
        nav_map.add_relationship("concept_a", "concept_c")

        assert "concept_a" in nav_map.relationships, "Condition must be true"
        assert "concept_b" in nav_map.relationships["concept_a"], "Condition must be true"
        assert "concept_c" in nav_map.relationships["concept_a"], "Condition must be true"

    def test_navigation_map_serialization(self):
        """Test NavigationMap to_dict and from_dict."""
        nav_map = NavigationMap(name="test", description="Test map")

        location = CodeLocation(
            path="test.py",
            line_start=1,
            line_end=10,
            concept="test concept",
            module="test",
            category="test",
        )
        nav_map.add_location(location)
        nav_map.add_relationship("concept_a", "concept_b")

        # Serialize
        data = nav_map.to_dict()
        assert data["name"] == "test", "Data must not be empty"
        assert len(data["locations"]) == 1, "Collection must not be empty"
        assert "concept_a" in data["relationships"], "Data must not be empty"

        # Deserialize
        restored = NavigationMap.from_dict(data)
        assert restored.name == nav_map.name, "name is not valid"
        assert len(restored.locations) == len(nav_map.locations), "Collection must not be empty"
        assert restored.relationships == nav_map.relationships, "relationships is not valid"


class TestTopologyManager:
    """Test TopologyManager class."""

    def test_initialization(self, topology_manager, temp_repo):
        """Test TopologyManager initialization."""
        assert topology_manager.repo_root == Path(temp_repo), "repo_root is not valid"
        assert topology_manager.topology_dir.exists(), "Condition must be true"
        assert isinstance(topology_manager.maps, dict)

    def test_create_map(self, topology_manager):
        """Test creating a new navigation map."""
        nav_map = topology_manager.create_map(
            name="ci_cd", description="CI/CD infrastructure map", metadata={"version": "1.0.0"}
        )

        assert nav_map.name == "ci_cd", "name is not valid"
        assert nav_map.description == "CI/CD infrastructure map", "description is not valid"
        assert "ci_cd" in topology_manager.maps, "Condition must be true"

    def test_add_location(self, topology_manager):
        """Test adding a location to a map."""
        topology_manager.create_map("test_map", "Test")

        location = topology_manager.add_location(
            map_name="test_map",
            path="src/test.py",
            line_start=10,
            line_end=20,
            concept="test fixture",
            module="pytest",
            category="testing",
        )

        assert location.path == "src/test.py", "path is not valid"
        assert location.concept == "test fixture", "concept is not valid"
        assert len(topology_manager.maps["test_map"].locations) == 1, "Collection must not be empty"

    def test_add_location_to_nonexistent_map(self, topology_manager):
        """Test adding location to non-existent map raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            topology_manager.add_location(
                map_name="nonexistent",
                path="test.py",
                line_start=1,
                line_end=10,
                concept="test",
                module="test",
                category="test",
            )

    def test_find_by_concept(self, topology_manager, sample_map):
        """Test finding locations by concept."""
        # Find pytest fixtures
        results = topology_manager.find("pytest fixtures")
        assert len(results) == 1, "Results must not be empty"
        assert results[0].concept == "pytest fixtures", "Result must not be empty"

        # Find test setup
        results = topology_manager.find("test setup")
        assert len(results) == 1, "Results must not be empty"
        assert results[0].path == "tests/conftest.py", "Result must not be empty"

    def test_find_with_category_filter(self, topology_manager, sample_map):
        """Test finding with category filter."""
        results = topology_manager.find("test", category="testing")
        assert len(results) > 0, "Results must not be empty"
        assert all(loc.category == "testing" for loc in results), "Result must not be empty"

    def test_find_with_module_filter(self, topology_manager, sample_map):
        """Test finding with module filter."""
        results = topology_manager.find("test", module="pytest")
        assert len(results) == 2, "Results must not be empty"
        assert all(loc.module == "pytest" for loc in results), "Result must not be empty"

    def test_find_with_limit(self, topology_manager, sample_map):
        """Test finding with result limit."""
        results = topology_manager.find("test", limit=1)
        assert len(results) == 1, "Results must not be empty"

    def test_find_optimal_path(self, topology_manager, sample_map):
        """Test finding optimal navigation path."""
        path = topology_manager.find_optimal_path("pytest fixtures", "mock objects")

        assert path is not None, "path must be initialized"
        assert path[0] == "pytest fixtures", "Condition must be true"
        assert path[-1] == "mock objects", "Object must be initialized"
        assert "test setup" in path, "Condition must be true"

    def test_find_optimal_path_no_connection(self, topology_manager, sample_map):
        """Test finding path when no connection exists."""
        path = topology_manager.find_optimal_path("pytest fixtures", "nonexistent concept")

        assert path is None, "path is not valid"

    def test_discover_related(self, topology_manager, sample_map):
        """Test discovering related concepts."""
        related = topology_manager.discover_related("pytest fixtures", max_depth=2)

        assert len(related) > 0, "Related must not be empty"
        # Should find test setup (distance 1) and mock objects (distance 2)
        concepts = [concept for concept, _ in related]
        assert "test setup" in concepts, "Condition must be true"
        assert "mock objects" in concepts, "Object must be initialized"

    def test_discover_related_with_limit(self, topology_manager, sample_map):
        """Test discovering related concepts with limit."""
        related = topology_manager.discover_related("pytest fixtures", limit=1)
        assert len(related) == 1, "Related must not be empty"

    def test_save_and_load_maps(self, topology_manager, sample_map, temp_repo):
        """Test saving and loading topology maps."""
        # Save maps
        topology_manager.save_maps()

        # Verify file was created
        map_file = Path(temp_repo) / ".codex" / "topology" / "test_map.json"
        assert map_file.exists(), "Condition must be true"

        # Create new manager and verify it loads the map
        new_manager = TopologyManager(repo_root=temp_repo)
        assert "test_map" in new_manager.maps, "Condition must be true"
        assert len(new_manager.maps["test_map"].locations) == 3, "Collection must not be empty"

    def test_get_maps(self, topology_manager, sample_map):
        """Test getting all maps."""
        maps = topology_manager.get_maps()
        assert "test_map" in maps, "Condition must be true"
        assert isinstance(maps["test_map"], NavigationMap)

    def test_get_aais_contribution(self, topology_manager, sample_map):
        """Test calculating AAIS contribution."""
        contribution = topology_manager.get_aais_contribution()

        assert "discovery_navigation" in contribution, "Condition must be true"
        assert "total_locations" in contribution, "Condition must be true"
        assert "total_relationships" in contribution, "Condition must be true"
        assert "maps_count" in contribution, "Count must be greater than zero"

        assert contribution["total_locations"] == 3, "Condition must be true"
        assert contribution["total_relationships"] == 2, "Condition must be true"
        assert contribution["maps_count"] == 1, "Count must be greater than zero"
        assert contribution["discovery_navigation"] > 0, "Value must be greater than zero"


class TestTopologyManagerIntegration:
    """Integration tests for real-world usage scenarios."""

    def test_ci_failure_navigation_scenario(self, topology_manager):
        """Test navigating from CI failure to test fix."""
        # Create CI/CD map
        topology_manager.create_map(name="ci_cd", description="CI/CD infrastructure")

        # Add CI failure location
        topology_manager.add_location(
            map_name="ci_cd",
            path=".github/workflows/test.yml",
            line_start=10,
            line_end=30,
            concept="CI test failure",
            module="github-actions",
            category="ci-cd",
        )

        # Add test execution location
        topology_manager.add_location(
            map_name="ci_cd",
            path="tests/test_suite.py",
            line_start=1,
            line_end=100,
            concept="test execution",
            module="pytest",
            category="testing",
        )

        # Add test fix location
        topology_manager.add_location(
            map_name="ci_cd",
            path="tests/fixtures/fix_helpers.py",
            line_start=20,
            line_end=50,
            concept="test fix patterns",
            module="pytest",
            category="testing",
        )

        # Add relationships
        topology_manager.add_relationship("ci_cd", "CI test failure", "test execution")
        topology_manager.add_relationship("ci_cd", "test execution", "test fix patterns")

        # Find optimal path
        path = topology_manager.find_optimal_path("CI test failure", "test fix patterns")

        assert path is not None, "path must be initialized"
        assert len(path) == 3, "Path must not be empty"
        assert path == ["CI test failure", "test execution", "test fix patterns"]

    def test_concept_discovery_scenario(self, topology_manager):
        """Test discovering related testing concepts."""
        # Create testing map
        topology_manager.create_map(name="testing", description="Testing infrastructure")

        # Add various testing concepts
        concepts = [
            ("pytest fixtures", "pytest"),
            ("mock objects", "unittest"),
            ("test data builders", "factory"),
            ("assertion helpers", "pytest"),
            ("test parametrization", "pytest"),
        ]

        for i, (concept, module) in enumerate(concepts):
            topology_manager.add_location(
                map_name="testing",
                path=f"tests/test_{i}.py",
                line_start=1,
                line_end=100,
                concept=concept,
                module=module,
                category="testing",
            )

        # Create web of relationships
        topology_manager.add_relationship("testing", "pytest fixtures", "mock objects")
        topology_manager.add_relationship("testing", "pytest fixtures", "test data builders")
        topology_manager.add_relationship("testing", "mock objects", "assertion helpers")
        topology_manager.add_relationship("testing", "test data builders", "test parametrization")

        # Discover related concepts from pytest fixtures
        related = topology_manager.discover_related("pytest fixtures", max_depth=2)

        # Should find mock objects and test data builders at distance 1
        # Should find assertion helpers and test parametrization at distance 2
        assert len(related) >= 4, "Related must not be empty"

        concepts_found = {concept for concept, _ in related}
        assert "mock objects" in concepts_found, "Object must be initialized"
        assert "test data builders" in concepts_found, "Data must not be empty"
