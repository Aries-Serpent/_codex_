"""Tests for src/codex/cognitive/workflow_optimizer.py — Phase 2 gap-fill.

Covers WorkflowStatus, WorkflowCategory, OptimizationType, WorkflowInfo,
WorkflowRun, WorkflowCheckpoint, WorkflowCategorizer, CacheOptimizer,
RedundancyDetector, ImmutableRegistry, CheckpointManager, and
WorkflowOptimizer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from codex.cognitive.workflow_optimizer import (
    CacheOptimizer,
    CheckpointManager,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    ImmutableComponent,
    ImmutableRegistry,
    OptimizationType,
    RedundancyDetector,
    WorkflowCategorizer,
    WorkflowCategory,
    WorkflowCheckpoint,
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
            category=WorkflowCategory.TESTING,
            triggers=["push", "pull_request"],
            estimated_duration_min=5.0,
            uses_cache=True,
            cache_keys=["pip-cache"],
            dependencies=[],
            outputs=["test-results"],
            is_required=True,
            approval_required=False,
        )

    def test_to_dict_keys(self, wf: WorkflowInfo) -> None:
        d = wf.to_dict()
        assert "name" in d
        assert "category" in d
        assert d["name"] == "ci-tests"
        assert d["category"] == "testing"

    def test_to_dict_uses_cache(self, wf: WorkflowInfo) -> None:
        d = wf.to_dict()
        assert d["uses_cache"] is True


# ---------------------------------------------------------------------------
# WorkflowRun
# ---------------------------------------------------------------------------


class TestWorkflowRun:
    def test_to_dict(self) -> None:
        now = datetime.now(timezone.utc)
        run = WorkflowRun(
            run_id="12345",
            workflow_name="ci-tests",
            status=WorkflowStatus.COMPLETED,
            conclusion="success",
            started_at=now,
            completed_at=now,
            duration_seconds=90.0,
            head_sha="abc123def456",
            branch="main",
        )
        d = run.to_dict()
        assert d["run_id"] == "12345"
        assert d["conclusion"] == "success"
        assert d["duration_seconds"] == pytest.approx(90.0)
        assert d["head_sha"] == "abc123def456"


# ---------------------------------------------------------------------------
# WorkflowCheckpoint
# ---------------------------------------------------------------------------


class TestWorkflowCheckpoint:
    def test_to_dict(self) -> None:
        now = datetime.now(timezone.utc)
        cp = WorkflowCheckpoint(
            checkpoint_id="CP-00001",
            workflow_name="ci-tests",
            step_name="pytest",
            status="completed",
            created_at=now,
            metadata={"tests_passed": 247},
        )
        d = cp.to_dict()
        assert d["checkpoint_id"] == "CP-00001"
        assert d["step_name"] == "pytest"
        assert d["status"] == "completed"
        assert d["metadata"] == {"tests_passed": 247}


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

    def test_categorize_unknown_returns_valid_category(
        self, categorizer: WorkflowCategorizer
    ) -> None:
        result = categorizer.categorize("random-workflow", ".github/workflows/rand.yml")
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
                category=WorkflowCategory.TESTING,
                triggers=["push"],
                estimated_duration_min=3.0,
                uses_cache=False,
                cache_keys=[],
                dependencies=[],
                outputs=[],
                is_required=True,
                approval_required=False,
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
        comp = registry.register(
            name="pyproject.toml",
            path="pyproject.toml",
            checksum="abc123",
            verified_by="ci-workflow",
            reason="Never change threshold manually",
        )
        assert registry.verify(comp.component_id, "abc123") is True

    def test_verify_wrong_checksum(self, registry: ImmutableRegistry) -> None:
        comp = registry.register(
            name="setup.cfg",
            path="setup.cfg",
            checksum="deadbeef",
            verified_by="manual",
            reason="stability",
        )
        assert registry.verify(comp.component_id, "wrong") is False

    def test_verify_unknown_component(self, registry: ImmutableRegistry) -> None:
        assert registry.verify("IMM-NONEXISTENT", "any") is False

    def test_get_all(self, registry: ImmutableRegistry) -> None:
        registry.register(
            name="comp-1",
            path="file1.txt",
            checksum="aaaa",
            verified_by="ci",
            reason="frozen",
        )
        items = registry.get_all()
        assert len(items) >= 1
        assert all(isinstance(c, ImmutableComponent) for c in items)

    def test_save_and_load(self, tmp_path: Path) -> None:
        path = tmp_path / "reg.json"
        reg1 = ImmutableRegistry(registry_path=path)
        comp = reg1.register(
            name="x",
            path="x.txt",
            checksum="sha256x",
            verified_by="manual",
            reason="critical",
        )
        comp_id = comp.component_id
        # save is called automatically by register; reload to verify
        reg2 = ImmutableRegistry(registry_path=path)
        assert reg2.verify(comp_id, "sha256x") is True


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
            status="completed",
            metadata={"tests_passed": 247},
        )
        assert cp.workflow_name == "ci-tests"
        assert cp.step_name == "pytest"
        assert cp.status == "completed"
        assert cp.metadata == {"tests_passed": 247}

    def test_get_latest_checkpoint(self, manager: CheckpointManager) -> None:
        manager.create_checkpoint("wf-a", "step-1", "in_progress")
        manager.create_checkpoint("wf-a", "step-2", "completed")
        latest = manager.get_latest_checkpoint("wf-a")
        assert latest is not None
        assert latest.step_name == "step-2"

    def test_get_latest_nonexistent(self, manager: CheckpointManager) -> None:
        assert manager.get_latest_checkpoint("nonexistent-wf") is None

    def test_get_all_for_workflow(self, manager: CheckpointManager) -> None:
        manager.create_checkpoint("wf-b", "step-1", "done")
        manager.create_checkpoint("wf-b", "step-2", "done")
        manager.create_checkpoint("wf-c", "step-1", "done")
        result = manager.get_all_for_workflow("wf-b")
        assert len(result) == 2

    def test_checkpoint_id_auto_generated(self, manager: CheckpointManager) -> None:
        cp = manager.create_checkpoint("wf-x", "step", "completed")
        assert cp.checkpoint_id.startswith("CP-")

    def test_save_and_reload(self, tmp_path: Path) -> None:
        path = tmp_path / "cp.json"
        mgr1 = CheckpointManager(checkpoint_path=path)
        cp = mgr1.create_checkpoint("wf-persist", "step-x", "done", {"val": 42})
        # save called automatically; reload to verify
        mgr2 = CheckpointManager(checkpoint_path=path)
        loaded = mgr2.get_latest_checkpoint("wf-persist")
        assert loaded is not None
        assert loaded.status == "done"


# ---------------------------------------------------------------------------
# WorkflowOptimizer (integration)
# ---------------------------------------------------------------------------


class TestWorkflowOptimizer:
    @pytest.fixture()
    def opt(self, tmp_path: Path) -> WorkflowOptimizer:
        return WorkflowOptimizer(
            workflows_dir=tmp_path / "nonexistent_workflows",
            knowledge_dir=tmp_path / "knowledge",
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
