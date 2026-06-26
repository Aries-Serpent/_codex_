"""
Tests for Long-term Plan 4: Cross-Session Learning Optimization.

This module contains tests for:
- Phase 4.1: Knowledge Distillation (knowledge_distiller.py)
- Phase 4.2: Context Compression (context_compressor.py)
- Phase 4.3: Retrieval Optimization (retrieval_optimizer.py)
- Phase 4.4: Workflow Optimization (workflow_optimizer.py)
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path


# ============================================================================
# Phase 4.1: Knowledge Distillation Tests
# ============================================================================
class TestKnowledgeType:
    """Test KnowledgeType enum."""

    def test_knowledge_types_exist(self):
        """Test all knowledge types are defined."""
        from codex.cognitive.knowledge_distiller import KnowledgeType

        assert hasattr(KnowledgeType, "FACTUAL")
        assert hasattr(KnowledgeType, "PROCEDURAL")
        assert hasattr(KnowledgeType, "CONTEXTUAL")
        assert hasattr(KnowledgeType, "DECISION")
        assert hasattr(KnowledgeType, "PATTERN")

    def test_knowledge_type_values(self):
        """Test knowledge type values."""
        from codex.cognitive.knowledge_distiller import KnowledgeType

        assert KnowledgeType.FACTUAL.value == "factual", "Value must be initialized"
        assert KnowledgeType.PROCEDURAL.value == "procedural", "Value must be initialized"


class TestKnowledgePriority:
    """Test KnowledgePriority enum."""

    def test_priority_levels_exist(self):
        """Test all priority levels are defined."""
        from codex.cognitive.knowledge_distiller import KnowledgePriority

        assert hasattr(KnowledgePriority, "CRITICAL")
        assert hasattr(KnowledgePriority, "HIGH")
        assert hasattr(KnowledgePriority, "MEDIUM")
        assert hasattr(KnowledgePriority, "LOW")


class TestKnowledgeItem:
    """Test KnowledgeItem dataclass."""

    def test_knowledge_item_creation(self):
        """Test creating a knowledge item."""
        from codex.cognitive.knowledge_distiller import (
            KnowledgeItem,
            KnowledgePriority,
            KnowledgeType,
        )

        now = datetime.now(timezone.utc)
        item = KnowledgeItem(
            id="KN-00001",
            knowledge_type=KnowledgeType.FACTUAL,
            priority=KnowledgePriority.HIGH,
            content="Test content",
            source="test",
            session_id="session-1",
            created_at=now,
            last_accessed=now,
        )

        assert item.id == "KN-00001", "Item must not be empty"
        assert item.knowledge_type == KnowledgeType.FACTUAL, "Item must not be empty"
        assert item.priority == KnowledgePriority.HIGH, "Item must not be empty"
        assert item.content == "Test content", "Content must not be empty"

    def test_knowledge_item_to_dict(self):
        """Test converting knowledge item to dict."""
        from codex.cognitive.knowledge_distiller import (
            KnowledgeItem,
            KnowledgePriority,
            KnowledgeType,
        )

        now = datetime.now(timezone.utc)
        item = KnowledgeItem(
            id="KN-00001",
            knowledge_type=KnowledgeType.FACTUAL,
            priority=KnowledgePriority.HIGH,
            content="Test content",
            source="test",
            session_id="session-1",
            created_at=now,
            last_accessed=now,
            tags=["test"],
        )

        data = item.to_dict()
        assert data["id"] == "KN-00001", "Data must not be empty"
        assert data["knowledge_type"] == "factual", "Data must not be empty"
        assert data["priority"] == "high", "Data must not be empty"
        assert "test" in data["tags"], "Data must not be empty"

    def test_knowledge_item_from_dict(self):
        """Test creating knowledge item from dict."""
        from codex.cognitive.knowledge_distiller import (
            KnowledgeItem,
            KnowledgePriority,
            KnowledgeType,
        )

        now = datetime.now(timezone.utc)
        data = {
            "id": "KN-00001",
            "knowledge_type": "factual",
            "priority": "high",
            "content": "Test content",
            "source": "test",
            "session_id": "session-1",
            "created_at": now.isoformat(),
            "last_accessed": now.isoformat(),
        }

        item = KnowledgeItem.from_dict(data)
        assert item.id == "KN-00001", "Item must not be empty"
        assert item.knowledge_type == KnowledgeType.FACTUAL, "Item must not be empty"
        assert item.priority == KnowledgePriority.HIGH, "Item must not be empty"


class TestKnowledgeStore:
    """Test KnowledgeStore class."""

    def test_store_creation(self):
        """Test creating a knowledge store."""
        from codex.cognitive.knowledge_distiller import KnowledgeStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            store = KnowledgeStore(store_path)
            assert store.count() == 0, "Count must be greater than zero"

    def test_store_add_and_get(self):
        """Test adding and getting items."""
        from codex.cognitive.knowledge_distiller import (
            KnowledgeItem,
            KnowledgePriority,
            KnowledgeStore,
            KnowledgeType,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            store = KnowledgeStore(store_path)

            now = datetime.now(timezone.utc)
            item = KnowledgeItem(
                id="KN-00001",
                knowledge_type=KnowledgeType.FACTUAL,
                priority=KnowledgePriority.HIGH,
                content="Test content",
                source="test",
                session_id="session-1",
                created_at=now,
                last_accessed=now,
            )

            store.add(item)
            assert store.count() == 1, "Count must be greater than zero"

            retrieved = store.get("KN-00001")
            assert retrieved is not None, "retrieved must be initialized"
            assert retrieved.content == "Test content", "Content must not be empty"

    def test_store_search(self):
        """Test searching the store."""
        from codex.cognitive.knowledge_distiller import (
            KnowledgeItem,
            KnowledgePriority,
            KnowledgeStore,
            KnowledgeType,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            store = KnowledgeStore(store_path)

            now = datetime.now(timezone.utc)
            item = KnowledgeItem(
                id="KN-00001",
                knowledge_type=KnowledgeType.FACTUAL,
                priority=KnowledgePriority.HIGH,
                content="pytest error in tests",
                source="test",
                session_id="session-1",
                created_at=now,
                last_accessed=now,
            )
            store.add(item)

            results = store.search("pytest")
            assert len(results) == 1, "Results must not be empty"
            assert results[0].id == "KN-00001", "Result must not be empty"


class TestLearningExtractor:
    """Test LearningExtractor class."""

    def test_extract_from_text(self):
        """Test extracting learnings from text."""
        from codex.cognitive.knowledge_distiller import LearningExtractor

        extractor = LearningExtractor()
        text = "The issue was a missing import.\nFixed by adding the import."
        learnings = extractor.extract_from_text(text)

        assert len(learnings) >= 1, "Learnings must not be empty"

    def test_extract_from_commit_messages(self):
        """Test extracting from commit messages."""
        from codex.cognitive.knowledge_distiller import LearningExtractor

        extractor = LearningExtractor()
        messages = [
            "Fix pytest collection error",
            "Add new feature for testing",
        ]
        learnings = extractor.extract_from_commit_messages(messages)

        assert len(learnings) >= 1, "Learnings must not be empty"


class TestKnowledgeDistiller:
    """Test KnowledgeDistiller class."""

    def test_distiller_creation(self):
        """Test creating a distiller."""
        from codex.cognitive.knowledge_distiller import KnowledgeDistiller

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            distiller = KnowledgeDistiller(store_path)
            assert distiller.store is not None, "store must be initialized"

    def test_distill_from_session(self):
        """Test distilling from a session."""
        from codex.cognitive.knowledge_distiller import KnowledgeDistiller

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            distiller = KnowledgeDistiller(store_path)

            items = distiller.distill_from_session(
                session_id="test-session",
                files_modified=["src/test.py", "tests/test_test.py"],
                commit_messages=["Fix pytest error", "Add new test"],
            )

            assert len(items) > 0, "Items must not be empty"

    def test_add_critical_knowledge(self):
        """Test adding critical knowledge."""
        from codex.cognitive.knowledge_distiller import KnowledgeDistiller

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            distiller = KnowledgeDistiller(store_path)

            item = distiller.add_critical_knowledge(
                content="Critical security fix required",
                source="security_scan",
                session_id="test-session",
                tags=["security"],
            )

            assert item is not None, "item must be initialized"
            assert "security" in item.tags, "Item must not be empty"


# ============================================================================
# Phase 4.2: Context Compression Tests
# ============================================================================
class TestCompressionStrategy:
    """Test CompressionStrategy enum."""

    def test_strategies_exist(self):
        """Test all strategies are defined."""
        from codex.cognitive.context_compressor import CompressionStrategy

        assert hasattr(CompressionStrategy, "EXTRACTIVE")
        assert hasattr(CompressionStrategy, "ABSTRACTIVE")
        assert hasattr(CompressionStrategy, "HYBRID")


class TestContextType:
    """Test ContextType enum."""

    def test_context_types_exist(self):
        """Test all context types are defined."""
        from codex.cognitive.context_compressor import ContextType

        assert hasattr(ContextType, "SESSION_LOG")
        assert hasattr(ContextType, "COMMIT_HISTORY")
        assert hasattr(ContextType, "FILE_CHANGES")
        assert hasattr(ContextType, "DECISIONS")


class TestCompressedContext:
    """Test CompressedContext dataclass."""

    def test_compressed_context_creation(self):
        """Test creating compressed context."""
        from codex.cognitive.context_compressor import CompressedContext, ContextType

        ctx = CompressedContext(
            context_id="CTX-00001",
            context_type=ContextType.SESSION_LOG,
            original_size=1000,
            compressed_size=200,
            compression_ratio=0.2,
            summary="Test summary",
            key_points=["Point 1", "Point 2"],
            preserved_items=[],
            created_at=datetime.now(timezone.utc),
            source_session="session-1",
        )

        assert ctx.context_id == "CTX-00001", "context_id is not valid"
        assert ctx.compression_ratio == 0.2, "compression_ratio is not valid"

    def test_compressed_context_to_dict(self):
        """Test converting to dict."""
        from codex.cognitive.context_compressor import CompressedContext, ContextType

        ctx = CompressedContext(
            context_id="CTX-00001",
            context_type=ContextType.SESSION_LOG,
            original_size=1000,
            compressed_size=200,
            compression_ratio=0.2,
            summary="Test summary",
            key_points=["Point 1"],
            preserved_items=[],
            created_at=datetime.now(timezone.utc),
            source_session="session-1",
        )

        data = ctx.to_dict()
        assert data["context_id"] == "CTX-00001", "Data must not be empty"
        assert data["context_type"] == "session_log", "Data must not be empty"


class TestTokenEstimator:
    """Test TokenEstimator class."""

    def test_estimate_tokens(self):
        """Test token estimation."""
        from codex.cognitive.context_compressor import TokenEstimator

        text = "This is a test string with some words."
        tokens = TokenEstimator.estimate_tokens(text)
        assert tokens > 0, "tokens must be greater than zero"
        assert tokens < len(text), "Text must not be empty"


class TestKeyPointExtractor:
    """Test KeyPointExtractor class."""

    def test_extract_key_points(self):
        """Test extracting key points."""
        from codex.cognitive.context_compressor import KeyPointExtractor

        extractor = KeyPointExtractor()
        text = "Fixed the bug in module.\nDecided to use new approach."
        points = extractor.extract(text, max_points=5)

        assert isinstance(points, (list, tuple, set, dict))  # May or may not find points


class TestExtractiveSummarizer:
    """Test ExtractiveSummarizer class."""

    def test_summarize_text(self):
        """Test summarizing text."""
        from codex.cognitive.context_compressor import ExtractiveSummarizer

        summarizer = ExtractiveSummarizer(target_ratio=0.3)
        text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
        summary = summarizer.summarize(text, max_sentences=2)

        assert len(summary) > 0, "Summary must not be empty"
        assert len(summary) < len(text), "Summary must not be empty"


class TestContextCompressor:
    """Test ContextCompressor class."""

    def test_compressor_creation(self):
        """Test creating a compressor."""
        from codex.cognitive.context_compressor import ContextCompressor

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "context_index.json"
            compressor = ContextCompressor(index_path)
            assert compressor.index is not None, "index must be initialized"

    def test_compress_session_log(self):
        """Test compressing a session log."""
        from codex.cognitive.context_compressor import ContextCompressor

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "context_index.json"
            compressor = ContextCompressor(index_path)

            log = "This is a long session log. " * 50
            ctx = compressor.compress_session_log(log, "session-1")

            assert ctx is not None, "ctx must be initialized"
            assert ctx.compression_ratio < 1.0, "compression_ratio is not valid"

    def test_compress_commit_history(self):
        """Test compressing commit history."""
        from codex.cognitive.context_compressor import ContextCompressor

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "context_index.json"
            compressor = ContextCompressor(index_path)

            commits = [
                {"sha": "abc123", "message": "Fix bug"},
                {"sha": "def456", "message": "Add feature"},
            ]
            ctx = compressor.compress_commit_history(commits, "session-1")

            assert ctx is not None, "ctx must be initialized"
            assert "2 commits" in ctx.summary, "Condition must be true"

    def test_get_compression_stats(self):
        """Test getting compression stats."""
        from codex.cognitive.context_compressor import ContextCompressor

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "context_index.json"
            compressor = ContextCompressor(index_path)

            stats = compressor.get_compression_stats()
            assert "total_contexts" in stats, "Condition must be true"


# ============================================================================
# Phase 4.3: Retrieval Optimization Tests
# ============================================================================
class TestRetrievalStrategy:
    """Test RetrievalStrategy enum."""

    def test_strategies_exist(self):
        """Test all strategies are defined."""
        from codex.cognitive.retrieval_optimizer import RetrievalStrategy

        assert hasattr(RetrievalStrategy, "PROACTIVE")
        assert hasattr(RetrievalStrategy, "REACTIVE")
        assert hasattr(RetrievalStrategy, "HYBRID")


class TestTaskType:
    """Test TaskType enum."""

    def test_task_types_exist(self):
        """Test all task types are defined."""
        from codex.cognitive.retrieval_optimizer import TaskType

        assert hasattr(TaskType, "BUG_FIX")
        assert hasattr(TaskType, "FEATURE")
        assert hasattr(TaskType, "TESTING")
        assert hasattr(TaskType, "SECURITY")


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""

    def test_retrieval_result_creation(self):
        """Test creating a retrieval result."""
        from codex.cognitive.retrieval_optimizer import (
            RetrievalResult,
            RetrievalStrategy,
        )

        result = RetrievalResult(
            query="pytest error",
            items=[{"id": "1", "content": "test"}],
            retrieval_time_ms=10.5,
            strategy_used=RetrievalStrategy.REACTIVE,
            cache_hit=False,
            relevance_scores=[0.8],
        )

        assert result.query == "pytest error", "Result must not be empty"
        assert len(result.items) == 1, "Collection must not be empty"

    def test_retrieval_result_to_dict(self):
        """Test converting to dict."""
        from codex.cognitive.retrieval_optimizer import (
            RetrievalResult,
            RetrievalStrategy,
        )

        result = RetrievalResult(
            query="test",
            items=[],
            retrieval_time_ms=5.0,
            strategy_used=RetrievalStrategy.PROACTIVE,
            cache_hit=True,
            relevance_scores=[],
        )

        data = result.to_dict()
        assert data["query"] == "test", "Data must not be empty"
        assert data["cache_hit"] is True, "Data must not be empty"


class TestRetrievalMetrics:
    """Test RetrievalMetrics class."""

    def test_metrics_record(self):
        """Test recording metrics."""
        from codex.cognitive.retrieval_optimizer import (
            RetrievalMetrics,
            RetrievalResult,
            RetrievalStrategy,
        )

        metrics = RetrievalMetrics()
        result = RetrievalResult(
            query="test",
            items=[{"id": "1"}],
            retrieval_time_ms=10.0,
            strategy_used=RetrievalStrategy.REACTIVE,
            cache_hit=True,
            relevance_scores=[0.9],
        )

        metrics.record(result)
        assert metrics.total_queries == 1, "total_queries is not valid"
        assert metrics.cache_hits == 1, "cache_hits is not valid"
        assert metrics.cache_hit_rate == 1.0, "cache_hit_rate is not valid"


class TestRetrievalCache:
    """Test RetrievalCache class."""

    def test_cache_set_and_get(self):
        """Test setting and getting cache."""
        from codex.cognitive.retrieval_optimizer import RetrievalCache

        cache = RetrievalCache(max_size=10)
        cache.set("key1", [{"id": "1"}])

        result = cache.get("key1")
        assert result is not None, "result must be initialized"
        assert len(result) == 1, "Result must not be empty"

    def test_cache_expiry(self):
        """Test cache expiry."""
        from codex.cognitive.retrieval_optimizer import RetrievalCache

        cache = RetrievalCache(max_size=10)
        cache.set("key1", [{"id": "1"}])

        result = cache.get("key1", max_age_seconds=0)
        assert result is None, "Result must not be empty"


class TestTaskTypeDetector:
    """Test TaskTypeDetector class."""

    def test_detect_bug_fix(self):
        """Test detecting bug fix task."""
        from codex.cognitive.retrieval_optimizer import TaskType, TaskTypeDetector

        detector = TaskTypeDetector()
        task_type = detector.detect("Fix the error in module")
        assert task_type == TaskType.BUG_FIX, "task_type is not valid"

    def test_detect_security(self):
        """Test detecting security task."""
        from codex.cognitive.retrieval_optimizer import TaskType, TaskTypeDetector

        detector = TaskTypeDetector()
        task_type = detector.detect("Address security vulnerability")
        assert task_type == TaskType.SECURITY, "task_type is not valid"


class TestRetrievalOptimizer:
    """Test RetrievalOptimizer class."""

    def test_optimizer_creation(self):
        """Test creating an optimizer."""
        from codex.cognitive.retrieval_optimizer import RetrievalOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            optimizer = RetrievalOptimizer(store_path)
            assert optimizer is not None, "optimizer must be initialized"

    def test_get_session_startup_context(self):
        """Test getting session startup context."""
        from codex.cognitive.retrieval_optimizer import RetrievalOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            optimizer = RetrievalOptimizer(store_path)

            context = optimizer.get_session_startup_context(task_hint="fix bug")
            assert "critical" in context, "Condition must be true"
            assert "recent" in context, "Condition must be true"

    def test_retrieve(self):
        """Test retrieval."""
        from codex.cognitive.retrieval_optimizer import RetrievalOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            optimizer = RetrievalOptimizer(store_path)
            optimizer.initialize()

            result = optimizer.retrieve("pytest error")
            assert result is not None, "result must be initialized"
            assert result.query == "pytest error", "Result must not be empty"

    def test_get_metrics(self):
        """Test getting metrics."""
        from codex.cognitive.retrieval_optimizer import RetrievalOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"
            optimizer = RetrievalOptimizer(store_path)

            metrics = optimizer.get_metrics()
            assert "total_queries" in metrics, "Condition must be true"


# ============================================================================
# Phase 4.4: Workflow Optimization Tests
# ============================================================================
class TestWorkflowStatus:
    """Test WorkflowStatus enum."""

    def test_statuses_exist(self):
        """Test all statuses are defined."""
        from codex.cognitive.workflow_optimizer import WorkflowStatus

        assert hasattr(WorkflowStatus, "QUEUED")
        assert hasattr(WorkflowStatus, "IN_PROGRESS")
        assert hasattr(WorkflowStatus, "COMPLETED")
        assert hasattr(WorkflowStatus, "FAILED")
        assert hasattr(WorkflowStatus, "ACTION_REQUIRED")
        assert hasattr(WorkflowStatus, "PENDING_APPROVAL")


class TestWorkflowCategory:
    """Test WorkflowCategory enum."""

    def test_categories_exist(self):
        """Test all categories are defined."""
        from codex.cognitive.workflow_optimizer import WorkflowCategory

        assert hasattr(WorkflowCategory, "SECURITY")
        assert hasattr(WorkflowCategory, "TESTING")
        assert hasattr(WorkflowCategory, "QUALITY")
        assert hasattr(WorkflowCategory, "BUILD")
        assert hasattr(WorkflowCategory, "DOCUMENTATION")


class TestOptimizationType:
    """Test OptimizationType enum."""

    def test_types_exist(self):
        """Test all optimization types are defined."""
        from codex.cognitive.workflow_optimizer import OptimizationType

        assert hasattr(OptimizationType, "CONSOLIDATION")
        assert hasattr(OptimizationType, "CACHING")
        assert hasattr(OptimizationType, "PARALLELIZATION")
        assert hasattr(OptimizationType, "CHECKPOINT")


class TestWorkflowInfo:
    """Test WorkflowInfo dataclass."""

    def test_workflow_info_creation(self):
        """Test creating workflow info."""
        from codex.cognitive.workflow_optimizer import WorkflowCategory, WorkflowInfo

        info = WorkflowInfo(
            name="CodeQL",
            path=".github/workflows/codeql.yml",
            category=WorkflowCategory.SECURITY,
            triggers=["push", "pull_request"],
            estimated_duration_min=5.0,
            uses_cache=True,
            cache_keys=["codeql-cache"],
            dependencies=[],
            outputs=["sarif"],
            is_required=True,
            approval_required=False,
        )

        assert info.name == "CodeQL", "name is not valid"
        assert info.category == WorkflowCategory.SECURITY, "category is not valid"

    def test_workflow_info_to_dict(self):
        """Test converting to dict."""
        from codex.cognitive.workflow_optimizer import WorkflowCategory, WorkflowInfo

        info = WorkflowInfo(
            name="Test",
            path=".github/workflows/test.yml",
            category=WorkflowCategory.TESTING,
            triggers=["push"],
            estimated_duration_min=3.0,
            uses_cache=False,
            cache_keys=[],
            dependencies=[],
            outputs=[],
            is_required=False,
            approval_required=False,
        )

        data = info.to_dict()
        assert data["name"] == "Test", "Data must not be empty"
        assert data["category"] == "testing", "Data must not be empty"


class TestOptimizationRecommendation:
    """Test OptimizationRecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        from codex.cognitive.workflow_optimizer import (
            OptimizationRecommendation,
            OptimizationType,
        )

        rec = OptimizationRecommendation(
            optimization_type=OptimizationType.CACHING,
            target_workflows=["test.yml", "build.yml"],
            description="Add caching",
            estimated_savings_min=5.0,
            priority=1,
            implementation_effort="low",
            code_changes=["Add cache step"],
        )

        assert rec.optimization_type == OptimizationType.CACHING, "optimization_type is not valid"
        assert len(rec.target_workflows) == 2, "Collection must not be empty"


class TestWorkflowCategorizer:
    """Test WorkflowCategorizer class."""

    def test_categorize_security(self):
        """Test categorizing security workflows."""
        from codex.cognitive.workflow_optimizer import (
            WorkflowCategorizer,
            WorkflowCategory,
        )

        categorizer = WorkflowCategorizer()
        category = categorizer.categorize("codeql-analysis", "codeql.yml")
        assert category == WorkflowCategory.SECURITY, "category is not valid"

    def test_categorize_testing(self):
        """Test categorizing testing workflows."""
        from codex.cognitive.workflow_optimizer import (
            WorkflowCategorizer,
            WorkflowCategory,
        )

        categorizer = WorkflowCategorizer()
        category = categorizer.categorize("pytest-tests", "test.yml")
        assert category == WorkflowCategory.TESTING, "category is not valid"


class TestCacheOptimizer:
    """Test CacheOptimizer class."""

    def test_analyze_cache_usage(self):
        """Test analyzing cache usage."""
        from codex.cognitive.workflow_optimizer import (
            CacheOptimizer,
            WorkflowCategory,
            WorkflowInfo,
        )

        optimizer = CacheOptimizer()
        workflows = [
            WorkflowInfo(
                name="Test1",
                path="test1.yml",
                category=WorkflowCategory.TESTING,
                triggers=["push"],
                estimated_duration_min=3.0,
                uses_cache=True,
                cache_keys=["pip-cache"],
                dependencies=[],
                outputs=[],
                is_required=False,
                approval_required=False,
            ),
            WorkflowInfo(
                name="Test2",
                path="test2.yml",
                category=WorkflowCategory.TESTING,
                triggers=["push"],
                estimated_duration_min=3.0,
                uses_cache=False,
                cache_keys=[],
                dependencies=[],
                outputs=[],
                is_required=False,
                approval_required=False,
            ),
        ]

        analysis = optimizer.analyze_cache_usage(workflows)
        assert analysis["total_workflows"] == 2, "Condition must be true"
        assert analysis["using_cache"] == 1, "Condition must be true"
        assert analysis["not_using_cache"] == 1, "Condition must be true"


class TestImmutableRegistry:
    """Test ImmutableRegistry class."""

    def test_registry_creation(self):
        """Test creating a registry."""
        from codex.cognitive.workflow_optimizer import ImmutableRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "immutable_registry.json"
            registry = ImmutableRegistry(registry_path)
            assert len(registry.get_all()) == 0, "Collection must not be empty"

    def test_register_component(self):
        """Test registering a component."""
        from codex.cognitive.workflow_optimizer import ImmutableRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "immutable_registry.json"
            registry = ImmutableRegistry(registry_path)

            comp = registry.register(
                name="Core Module",
                path="src/core.py",
                checksum="abc123",
                verified_by="security-scan",
                reason="Security-critical component",
            )

            assert comp.component_id.startswith("IMM-"), "Condition must be true"
            assert len(registry.get_all()) == 1, "Collection must not be empty"

    def test_verify_component(self):
        """Test verifying a component."""
        from codex.cognitive.workflow_optimizer import ImmutableRegistry

        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "immutable_registry.json"
            registry = ImmutableRegistry(registry_path)

            comp = registry.register(
                name="Test",
                path="test.py",
                checksum="abc123",
                verified_by="test",
                reason="Test",
            )

            assert registry.verify(comp.component_id, "abc123") is True
            assert registry.verify(comp.component_id, "wrong") is False


class TestCheckpointManager:
    """Test CheckpointManager class."""

    def test_manager_creation(self):
        """Test creating a manager."""
        from codex.cognitive.workflow_optimizer import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cp_path = Path(tmpdir) / "checkpoints.json"
            manager = CheckpointManager(cp_path)
            assert manager is not None, "manager must be initialized"

    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        from codex.cognitive.workflow_optimizer import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cp_path = Path(tmpdir) / "checkpoints.json"
            manager = CheckpointManager(cp_path)

            cp = manager.create_checkpoint(
                workflow_name="test-workflow",
                step_name="build",
                status="completed",
                metadata={"output": "success"},
            )

            assert cp.checkpoint_id.startswith("CP-"), "Condition must be true"
            assert cp.workflow_name == "test-workflow", "workflow_name is not valid"

    def test_get_latest_checkpoint(self):
        """Test getting latest checkpoint."""
        from codex.cognitive.workflow_optimizer import CheckpointManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cp_path = Path(tmpdir) / "checkpoints.json"
            manager = CheckpointManager(cp_path)

            manager.create_checkpoint("wf1", "step1", "completed")
            manager.create_checkpoint("wf1", "step2", "completed")

            latest = manager.get_latest_checkpoint("wf1")
            assert latest is not None, "latest must be initialized"
            assert latest.step_name == "step2", "step_name is not valid"


class TestWorkflowOptimizer:
    """Test WorkflowOptimizer class."""

    def test_optimizer_creation(self):
        """Test creating an optimizer."""
        from codex.cognitive.workflow_optimizer import WorkflowOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = WorkflowOptimizer(
                workflows_dir=Path(tmpdir) / "workflows",
                knowledge_dir=Path(tmpdir) / "knowledge",
            )
            assert optimizer is not None, "optimizer must be initialized"

    def test_analyze_all_empty(self):
        """Test analyzing with no workflows."""
        from codex.cognitive.workflow_optimizer import WorkflowOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = WorkflowOptimizer(
                workflows_dir=Path(tmpdir) / "workflows",
                knowledge_dir=Path(tmpdir) / "knowledge",
            )

            analysis = optimizer.analyze_all()
            assert analysis["total_workflows"] == 0, "Condition must be true"

    def test_get_optimization_report(self):
        """Test generating optimization report."""
        from codex.cognitive.workflow_optimizer import WorkflowOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = WorkflowOptimizer(
                workflows_dir=Path(tmpdir) / "workflows",
                knowledge_dir=Path(tmpdir) / "knowledge",
            )

            report = optimizer.get_optimization_report()
            assert "Workflow Optimization Report" in report, "Condition must be true"


# ============================================================================
# Integration Tests
# ============================================================================
class TestPlan4Integration:
    """Integration tests for Plan 4 components."""

    def test_knowledge_to_retrieval_flow(self):
        """Test knowledge distillation to retrieval flow."""
        from codex.cognitive.knowledge_distiller import KnowledgeDistiller
        from codex.cognitive.retrieval_optimizer import RetrievalOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "knowledge_store.json"

            # Distill knowledge
            distiller = KnowledgeDistiller(store_path)
            distiller.distill_from_session(
                session_id="test-session",
                files_modified=["src/test.py"],
                commit_messages=["Fix pytest error in collection"],
            )

            # Retrieve knowledge
            optimizer = RetrievalOptimizer(store_path)
            optimizer.initialize()

            context = optimizer.get_session_startup_context()
            assert context is not None, "context must be initialized"

    def test_context_compression_flow(self):
        """Test context compression and retrieval."""
        from codex.cognitive.context_compressor import ContextCompressor

        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "context_index.json"
            compressor = ContextCompressor(index_path)

            # Compress session log
            log = "Session started. Fixed bug. Added tests. Session ended. " * 10
            _ = compressor.compress_session_log(log, "session-1")  # Result used implicitly

            # Get startup context
            startup = compressor.get_session_startup_context(max_tokens=500)
            assert startup is not None, "startup must be initialized"

            # Check stats
            stats = compressor.get_compression_stats()
            assert stats["total_contexts"] == 1, "Condition must be true"
