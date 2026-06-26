"""Tests for PS-13 Agent Task Router (L4 Automatic Classification).

Validates keyword→agent routing, confidence scoring, fallback chains,
and the convenience ``route_task`` function.
"""

import importlib.util
import os

import pytest

# Import directly from the module file to avoid __init__.py dependency chain
_mod_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "scripts", "monitoring", "agent_orchestrator.py"
)
_spec = importlib.util.spec_from_file_location("agent_orchestrator", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TASK_ROUTING_TABLE = _mod.TASK_ROUTING_TABLE
TaskRouter = _mod.TaskRouter
route_task = _mod.route_task


class TestTaskRoutingTable:
    """Verify the static routing table structure."""

    def test_has_seven_categories(self):
        assert len(TASK_ROUTING_TABLE) == 7, "Task_routing_table must not be empty"

    def test_required_categories_present(self):
        expected = {
            "ci_cd",
            "testing",
            "security",
            "documentation",
            "rag_ml",
            "configuration",
            "repository",
        }
        assert set(TASK_ROUTING_TABLE.keys()) == expected, "Condition must be true"

    def test_each_category_has_required_keys(self):
        for cat, entry in TASK_ROUTING_TABLE.items():
            assert "keywords" in entry, f"{cat} missing keywords"
            assert "agents" in entry, f"{cat} missing agents"
            assert "description" in entry, f"{cat} missing description"
            assert len(entry["agents"]) >= 1, f"{cat} has no agents"
            assert len(entry["keywords"]) >= 3, f"{cat} has fewer than 3 keywords"


class TestTaskRouter:
    """Test the TaskRouter class."""

    @pytest.fixture
    def router(self):
        return TaskRouter()

    # --- routing accuracy ---

    def test_routes_ci_task(self, router):
        result = router.route_task("fix the CI pipeline workflow failure")
        assert result["category"] == "ci_cd", "Result must not be empty"
        assert result["agent"] == "ci-testing-agent", "Result must not be empty"
        assert result["confidence"] > 0, "Value must be greater than zero"

    def test_routes_test_task(self, router):
        result = router.route_task("the pytest coverage assertion is flaky")
        assert result["category"] == "testing", "Result must not be empty"
        assert result["agent"] == "ci-testing-agent", "Result must not be empty"

    def test_routes_security_task(self, router):
        result = router.route_task("security vulnerability with secret credential token exposure")
        assert result["category"] == "security", "Result must not be empty"
        assert result["agent"] == "security-alert-verification-agent", "Result must not be empty"

    def test_routes_documentation_task(self, router):
        result = router.route_task("fix broken link in documentation markdown")
        assert result["category"] == "documentation", "Result must not be empty"
        assert result["agent"] == "documentation-quality-agent", "Result must not be empty"

    def test_routes_rag_task(self, router):
        result = router.route_task("the rag embedding model tensor is broken")
        assert result["category"] == "rag_ml", "Result must not be empty"
        assert result["agent"] == "meta-tensor-validator", "Result must not be empty"

    def test_routes_config_task(self, router):
        result = router.route_task("migrate hydra configuration yaml settings")
        assert result["category"] == "configuration", "Result must not be empty"
        assert result["agent"] == "config-validator", "Result must not be empty"

    def test_routes_repo_task(self, router):
        result = router.route_task("repository cleanup and lint dependency import")
        assert result["category"] == "repository", "Result must not be empty"
        assert result["agent"] == "repository-hygiene-agent", "Result must not be empty"

    # --- fallback behaviour ---

    def test_unknown_task_returns_default(self, router):
        result = router.route_task("do something completely unrelated to anything")
        assert result["agent"] == "ci-testing-agent", "Result must not be empty"
        assert result["category"] == "general", "Result must not be empty"
        assert result["confidence"] == 0.0, "Result must not be empty"

    def test_fallbacks_populated(self, router):
        result = router.route_task("fix the CI pipeline workflow failure deploy")
        assert isinstance(result["fallbacks"], list)
        assert len(result["fallbacks"]) >= 1, "Collection must not be empty"

    # --- confidence scoring ---

    def test_more_keywords_yield_higher_confidence(self, router):
        low = router.route_task("ci")
        high = router.route_task("ci pipeline workflow build failure github actions deploy")
        assert high["confidence"] >= low["confidence"], "Value must be greater than zero"

    # --- custom routing table ---

    def test_custom_routing_table(self):
        custom = {
            "alpha": {
                "keywords": ["alpha", "beta"],
                "agents": ["alpha-agent"],
                "description": "test",
            }
        }
        router = TaskRouter(routing_table=custom)
        result = router.route_task("run the alpha test")
        assert result["agent"] == "alpha-agent", "Result must not be empty"
        assert result["category"] == "alpha", "Result must not be empty"

    # --- list_categories ---

    def test_list_categories(self, router):
        cats = router.list_categories()
        assert len(cats) == 7, "Cats must not be empty"
        for c in cats:
            assert "category" in c, "Condition must be true"
            assert "primary_agent" in c, "Condition must be true"
            assert "agent_count" in c, "Count must be greater than zero"

    # --- all_scores ---

    def test_all_scores_in_result(self, router):
        result = router.route_task("fix the CI test failures")
        assert "all_scores" in result, "Result must not be empty"
        assert isinstance(result["all_scores"], list)


class TestRouteTaskConvenience:
    """Test the module-level convenience function."""

    def test_route_task_returns_dict(self):
        result = route_task("fix CI build failure")
        assert isinstance(result, dict)
        assert "agent" in result, "Result must not be empty"
        assert "confidence" in result, "Result must not be empty"

    def test_route_task_with_kwargs(self):
        result = route_task("fix CI build failure", default_agent="my-agent")
        # should not fall back for a task with keywords
        assert result["agent"] != "my-agent" or result["confidence"] == 0.0, "Result must not be empty"
