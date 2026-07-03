"""Tests for src/codex/cognitive/workflow_optimizer.py — Phase 2 gap-fill.

Covers WorkflowStatus, WorkflowCategory, OptimizationType, WorkflowInfo,
WorkflowRun, WorkflowCategorizer, CacheOptimizer, RedundancyDetector,
ImmutableRegistry, CheckpointManager, and WorkflowOptimizer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from codex.cognitive.workflow_optimizer import (
    CacheOptimizer,
    CheckpointManager,
    ImmutableComponent,
    ImmutableRegistry,
    OptimizationType,
    RedundancyDetector,
    WorkflowAnalyzer,
    WorkflowCategorizer,
    WorkflowCategory,
    WorkflowInfo,
    WorkflowOptimizer,
    WorkflowRun,
    WorkflowStatus,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_workflow_status_values(self) -> None:
        assert WorkflowStatus.QUEUED.value == "queued"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.PENDING_APPROVAL.value == "pending_approval"

    def test_workflow_category_values(self) -> None:
        assert WorkflowCategory.SECURITY.value == "security"
        assert WorkflowCategory.TESTING.value == "testing"
        assert WorkflowCategory.BUILD.value == "build"

    def test_optimization_type_values(self) -> None:
        assert OptimizationType.CONSOLIDATION.value == "consolidation"
        assert OptimizationType.CACHING.value == "caching"


# ---------------------------------------------------------------------------
# WorkflowInfo
# ---------------------------------------------------------------------------


class TestWorkflowInfo:
    @pytest.fixture()
    def wf(self) -> WorkflowInfo:
        return WorkflowInfo(
            name="ci-tests",
            path=".github/workflows/ci.yml",
            status=WorkflowStatus.COMPLETED,
            category=WorkflowCategory.TESTING,
            run_count=10,
            avg_duration_seconds=120.0,
        )

    def test_to_dict_keys(self, wf: WorkflowInfo) -> None:
        d = wf.to_dict()
        assert "name" in d
        assert "status" in d
        assert "category" in d
        assert d["name"] == "ci-tests"
        assert d["status"] == "completed"

    def test_to_dict_category(self, wf: WorkflowInfo) -> None:
        d = wf.to_dict()
        assert d["category"] == "testing"


# ---------------------------------------------------------------------------
# WorkflowRun
# ---------------------------------------------------------------------------


class TestWorkflowRun:
    def test_to_dict(self) -> None:
        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            run_id=12345,
            workflow_name="ci-tests",
            status=WorkflowStatus.COMPLETED,
            started_at=now,
            completed_at=now,
            duration_seconds=90.0,
            conclusion="success",
        )
        d = run.to_dict()
        assert d["run_id"] == 12345
        assert d["conclusion"] == "success"
        assert d["duration_seconds"] == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# WorkflowCategorizer
# ---------------------------------------------------------------------------


class TestWorkflowCategorizer:
    @pytest.fixture()
    def categorizer(self) -> WorkflowCategorizer:
        return WorkflowCategorizer()

    @pytest.mark.parametrize(
        "name,path,expected",
        [
            ("codeql-analysis", ".github/workflows/codeql.yml", WorkflowCategory.SECURITY),
            ("run-tests", ".github/workflows/tests.yml", WorkflowCategory.TESTING),
            ("build-package", ".github/workflows/build.yml", WorkflowCategory.BUILD),
            ("deploy-prod", ".github/workflows/deploy.yml", WorkflowCategory.DEPLOYMENT),
            (
                "generate-docs",
                ".github/workflows/docs.yml",
                WorkflowCategory.DOCUMENTATION,
            ),
        ],
    )
    def test_categorize_by_name(
        self,
        categorizer: WorkflowCategorizer,
        name: str,
        path: str,
        expected: WorkflowCategory,
    ) -> None:
        result = categorizer.categorize(name, path)
        assert result == expected

    def test_categorize_unknown_falls_back_to_other(
        self, categorizer: WorkflowCategorizer
    ) -> None:
        result = categorizer.categorize("random-workflow", ".github/workflows/rand.yml")
        # Should return a valid category without raising
        assert isinstance(result, WorkflowCategory)


# ---------------------------------------------------------------------------
# CacheOptimizer
# ---------------------------------------------------------------------------


class TestCacheOptimizer:
    @pytest.fixture()
    def optimizer(self) -> CacheOptimizer:
        return CacheOptimizer()

    def test_analyze_empty_list(self, optimizer: CacheOptimizer) -> None:
        result = optimizer.analyze_cache_usage([])
        assert isinstance(result, dict)

    def test_analyze_returns_dict(self, optimizer: CacheOptimizer) -> None:
        wfs = [
            WorkflowInfo(
                name="ci",
                path=".github/workflows/ci.yml",
                status=WorkflowStatus.COMPLETED,
                category=WorkflowCategory.TESTING,
                run_count=5,
                avg_duration_seconds=60.0,
            )
        ]
        result = optimizer.analyze_cache_usage(wfs)
        assert isinstance(result, dict)

    def test_recommend_cache_improvements(self, optimizer: CacheOptimizer) -> None:
        analysis = optimizer.analyze_cache_usage([])
        recs = optimizer.recommend_cache_improvements(analysis)
        assert isinstance(recs, list)


# ---------------------------------------------------------------------------
# RedundancyDetector
# ---------------------------------------------------------------------------


class TestRedundancyDetector:
    @pytest.fixture()
    def detector(self) -> RedundancyDetector:
        return RedundancyDetector()

    def test_find_similar_empty_list(self, detector: RedundancyDetector) -> None:
        groups = detector.find_similar_workflows([])
        assert isinstance(groups, list)
        assert groups == []

    def test_recommend_consolidations_empty(self, detector: RedundancyDetector) -> None:
        recs = detector.recommend_consolidations([])
        assert isinstance(recs, list)


# ---------------------------------------------------------------------------
# ImmutableRegistry
# ---------------------------------------------------------------------------


class TestImmutableRegistry:
    @pytest.fixture()
    def registry(self, tmp_path: Path) -> ImmutableRegistry:
        return ImmutableRegistry(registry_path=tmp_path / "immutable.json")

    def test_register_and_verify(self, registry: ImmutableRegistry) -> None:
        registry.register(
            component_id="pyproject.toml",
            path=".github/CODEOWNERS",
            checksum="abc123",
            protected_by="branch-protection",
        )
        assert registry.verify("pyproject.toml", "abc123") is True

    def test_verify_wrong_checksum(self, registry: ImmutableRegistry) -> None:
        registry.register(
            component_id="setup.cfg",
            path="setup.cfg",
            checksum="deadbeef",
            protected_by="manual",
        )
        assert registry.verify("setup.cfg", "wrong") is False

    def test_verify_unknown_component(self, registry: ImmutableRegistry) -> None:
        assert registry.verify("nonexistent", "any") is False

    def test_get_all(self, registry: ImmutableRegistry) -> None:
        registry.register(
            component_id="comp-1",
            path="file1.txt",
            checksum="aaaa",
            protected_by="ci",
        )
        items = registry.get_all()
        assert len(items) >= 1
        assert all(isinstance(c, ImmutableComponent) for c in items)

    def test_save_and_load(self, tmp_path: Path) -> None:
        path = tmp_path / "reg.json"
        reg1 = ImmutableRegistry(registry_path=path)
        reg1.register("comp-x", "x.txt", "sha256x", "manual")
        reg1.save()

        reg2 = ImmutableRegistry(registry_path=path)
        assert reg2.verify("comp-x", "sha256x") is True


# ---------------------------------------------------------------------------
# CheckpointManager
# ---------------------------------------------------------------------------


class TestCheckpointManager:
    @pytest.fixture()
    def manager(self, tmp_path: Path) -> CheckpointManager:
        return CheckpointManager(checkpoint_path=tmp_path / "checkpoints.json")

    def test_create_checkpoint(self, manager: CheckpointManager) -> None:
        cp = manager.create_checkpoint(
            workflow_name="ci-tests",
            step_name="pytest",
            state={"tests_passed": 247},
        )
        assert cp.workflow_name == "ci-tests"
        assert cp.step_name == "pytest"
        assert cp.state == {"tests_passed": 247}

    def test_get_latest_checkpoint(self, manager: CheckpointManager) -> None:
        manager.create_checkpoint("wf-a", "step-1", {"count": 1})
        manager.create_checkpoint("wf-a", "step-2", {"count": 2})
        latest = manager.get_latest_checkpoint("wf-a")
        assert latest is not None
        assert latest.step_name == "step-2"

    def test_get_latest_nonexistent(self, manager: CheckpointManager) -> None:
        assert manager.get_latest_checkpoint("nonexistent-wf") is None

    def test_get_all_for_workflow(self, manager: CheckpointManager) -> None:
        manager.create_checkpoint("wf-b", "step-1", {})
        manager.create_checkpoint("wf-b", "step-2", {})
        manager.create_checkpoint("wf-c", "step-1", {})
        result = manager.get_all_for_workflow("wf-b")
        assert len(result) == 2

    def test_save_and_reload(self, tmp_path: Path) -> None:
        path = tmp_path / "cp.json"
        mgr1 = CheckpointManager(checkpoint_path=path)
        mgr1.create_checkpoint("wf-persist", "step-x", {"val": 42})
        mgr1.save()

        mgr2 = CheckpointManager(checkpoint_path=path)
        cp = mgr2.get_latest_checkpoint("wf-persist")
        assert cp is not None
        assert cp.state == {"val": 42}


# ---------------------------------------------------------------------------
# WorkflowOptimizer (integration)
# ---------------------------------------------------------------------------


class TestWorkflowOptimizer:
    @pytest.fixture()
    def opt(self, tmp_path: Path) -> WorkflowOptimizer:
        return WorkflowOptimizer(
            workflows_dir=tmp_path / "nonexistent_workflows",
            immutable_registry_path=tmp_path / "immutable.json",
            checkpoint_path=tmp_path / "checkpoints.json",
        )

    def test_scan_returns_int(self, opt: WorkflowOptimizer) -> None:
        count = opt.scan()
        assert isinstance(count, int)

    def test_get_pending_approval_workflows(self, opt: WorkflowOptimizer) -> None:
        result = opt.get_pending_approval_workflows()
        assert isinstance(result, list)

    def test_analyze_all_returns_dict(self, opt: WorkflowOptimizer) -> None:
        result = opt.analyze_all()
        assert isinstance(result, dict)

    def test_get_recommendations_returns_list(self, opt: WorkflowOptimizer) -> None:
        result = opt.get_recommendations()
        assert isinstance(result, list)
