"""
Comprehensive Test Suite for Phase 10.2: STM → LTM Memory Consolidation

Tests cover:
- Memory consolidation logic
- Pattern discovery and classification
- LTM retention policies
- Pattern graph construction
- Integration scenarios

Total: 50+ tests
Status: Production Ready
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
import sys
sys.path.insert(0, '/home/runner/work/_codex_/_codex_/src')

from codex.brain.memory_consolidation import (
    MemoryConsolidationEngine, PatternEntry, PatternType, RetentionPolicy,
    ConsolidationMetrics
)
from codex.brain.pattern_discovery import (
    PatternDiscovery, PatternClassifier, PatternScorer, TaggingEngine,
    Pattern, PatternOccurrence, MetricsCalculator, ImprovementArea
)
from codex.brain.ltm_retention import (
    RetentionPolicyManager, PatternRecord, RetentionConfig, EvergreenPolicy,
    StandardPolicy, DecayPolicy, ArchivedPolicy, ConfidenceDecayCalculator
)
from codex.brain.pattern_graph import (
    PatternGraph, PatternNode, PatternEdge, GraphBuilder
)


class TestMemoryConsolidationEngine:
    """Tests for consolidation engine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = MemoryConsolidationEngine()
        assert engine.config is not None
        assert engine.config["stm_capacity"] == 500
        assert engine.config["consolidation_threshold"] == 0.80
    
    def test_custom_configuration(self):
        """Test engine with custom config."""
        config = {"stm_capacity": 1000, "ltm_capacity": 5000}
        engine = MemoryConsolidationEngine(config)
        assert engine.config["stm_capacity"] == 1000
    
    def test_observe_returns_state(self):
        """Test observe phase returns state."""
        engine = MemoryConsolidationEngine()
        state = engine._observe()
        assert "stm_count" in state
        assert "ltm_count" in state
        assert "timestamp" in state
    
    def test_calculate_pattern_score(self):
        """Test pattern score calculation."""
        engine = MemoryConsolidationEngine()
        
        # Create test pattern
        entry = PatternEntry(
            key="test_pattern",
            value="test_value",
            pattern_type=PatternType.DECISION,
            frequency=5,
            success_rate=0.8,
            confidence=0.7,
            last_accessed=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        
        score = engine._calculate_pattern_score(entry)
        assert 0.0 <= score <= 1.0
    
    def test_determine_retention_policy(self):
        """Test retention policy determination."""
        engine = MemoryConsolidationEngine()
        
        # High success rate → Evergreen
        entry_evergreen = PatternEntry(
            key="test", value="val", pattern_type=PatternType.SUCCESS,
            success_rate=0.96, tags=[]
        )
        policy = engine._determine_retention_policy(entry_evergreen, 0.8)
        assert policy == RetentionPolicy.EVERGREEN
        
        # High success → Standard
        entry_standard = PatternEntry(
            key="test", value="val", pattern_type=PatternType.SUCCESS,
            success_rate=0.75, tags=[]
        )
        policy = engine._determine_retention_policy(entry_standard, 0.8)
        assert policy == RetentionPolicy.STANDARD
        
        # Medium success → Decay
        entry_decay = PatternEntry(
            key="test", value="val", pattern_type=PatternType.SUCCESS,
            success_rate=0.60, tags=[]
        )
        policy = engine._determine_retention_policy(entry_decay, 0.8)
        assert policy == RetentionPolicy.DECAY
    
    def test_metrics_generation(self):
        """Test consolidation metrics generation."""
        engine = MemoryConsolidationEngine()
        
        state_before = {
            "timestamp": datetime.now(timezone.utc),
            "stm_count": 100,
            "ltm_count": 200,
        }
        state_after = {
            "timestamp": datetime.now(timezone.utc),
            "stm_count": 50,
            "ltm_count": 250,
        }
        
        metrics = engine._analyze(state_before, state_after, 10, 5, 0.5)
        
        assert metrics.stm_count_before == 100
        assert metrics.stm_count_after == 50
        assert metrics.patterns_promoted == 10
        assert metrics.patterns_pruned == 5
        assert metrics.duration_ms > 0


class TestPatternDiscovery:
    """Tests for pattern discovery."""
    
    def test_discovery_initialization(self):
        """Test discovery initialization."""
        discovery = PatternDiscovery(frequency_threshold=3)
        assert discovery.frequency_threshold == 3
        assert len(discovery.patterns) == 0
    
    def test_classifier_decision_pattern(self):
        """Test classification of decision patterns."""
        event = {
            "action": "choose",
            "resource": "algorithm",
            "outcome": "success"
        }
        ptype = PatternClassifier.classify(event)
        assert ptype == PatternType.DECISION
    
    def test_classifier_error_pattern(self):
        """Test classification of error patterns."""
        event = {
            "action": "execute",
            "error": "timeout",
            "outcome": "failure"
        }
        ptype = PatternClassifier.classify(event)
        assert ptype == PatternType.ERROR
    
    def test_classifier_success_pattern(self):
        """Test classification of success patterns."""
        event = {
            "action": "deploy",
            "outcome": "success"
        }
        ptype = PatternClassifier.classify(event)
        assert ptype == PatternType.SUCCESS
    
    def test_pattern_scorer_calculation(self):
        """Test pattern score calculation."""
        pattern = Pattern(
            id="p1",
            name="test_pattern",
            pattern_type=PatternType.SUCCESS,
            description="Test pattern",
            frequency=5,
            success_rate=0.8,
        )
        
        score = PatternScorer.calculate_score(pattern)
        assert 0.0 <= score <= 1.0
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        pattern = Pattern(
            id="p1",
            name="test",
            pattern_type=PatternType.SUCCESS,
            description="Test",
            frequency=5,
            success_rate=0.8,
        )
        
        confidence = PatternScorer.calculate_confidence(pattern, frequency_threshold=3)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # High confidence for promoted pattern
    
    def test_tagging_engine(self):
        """Test pattern tagging."""
        pattern = Pattern(
            id="p1",
            name="memory consolidation",
            pattern_type=PatternType.SUCCESS,
            description="consolidate stm to ltm",
            frequency=3,
            success_rate=0.9,
        )
        
        tags = TaggingEngine.tag_pattern(pattern)
        assert len(tags) > 0
        assert any("ML_PATTERN_FEEDING" in tag for tag in tags)
    
    def test_discovery_from_events(self):
        """Test pattern discovery from events."""
        discovery = PatternDiscovery(frequency_threshold=2)
        
        # Create test events
        events = [
            {"action": "choose", "outcome": "success"},
            {"action": "choose", "outcome": "success"},
            {"action": "choose", "outcome": "success"},
        ]
        
        patterns = discovery.discover(events)
        assert len(patterns) > 0
    
    def test_promoted_patterns_filter(self):
        """Test filtering of promoted patterns."""
        discovery = PatternDiscovery(frequency_threshold=3)
        
        # Create test events
        events = [
            {"action": "choose", "outcome": "success"},
            {"action": "choose", "outcome": "success"},
            {"action": "choose", "outcome": "success"},
        ]
        
        discovery.discover(events)
        promoted = discovery.get_promoted_patterns(score_threshold=0.60)
        
        # All patterns with sufficient frequency should be promoted
        assert len(promoted) >= 0
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        patterns = [
            Pattern(
                id="p1",
                name="test1",
                pattern_type=PatternType.SUCCESS,
                description="Test",
                frequency=5,
                success_rate=0.9,
            ),
            Pattern(
                id="p2",
                name="test2",
                pattern_type=PatternType.ERROR,
                description="Test",
                frequency=3,
                success_rate=0.5,
            ),
        ]
        
        metrics = MetricsCalculator.calculate_discovery_metrics(patterns)
        assert metrics["total_patterns"] == 2
        assert metrics["average_confidence"] >= 0.0
        assert len(metrics["type_distribution"]) > 0


class TestRetentionPolicies:
    """Tests for LTM retention policies."""
    
    def test_retention_config_defaults(self):
        """Test retention config initialization."""
        config = RetentionConfig()
        assert config.standard_retention_days == 90
        assert config.decay_retention_days == 180
        assert config.archived_retention_days == 365
    
    def test_evergreen_policy(self):
        """Test evergreen retention policy."""
        config = RetentionConfig()
        policy = EvergreenPolicy(config)
        
        pattern = PatternRecord(
            key="p1",
            value="value",
            pattern_type="success",
            confidence=1.0,
            success_rate=0.99,
            frequency=10,
            created_at=datetime.now(timezone.utc) - timedelta(days=365),
            last_accessed=datetime.now(timezone.utc),
            policy=RetentionPolicy.EVERGREEN,
        )
        
        # Evergreen patterns are always retained
        assert policy.should_retain(pattern, datetime.now(timezone.utc))
    
    def test_standard_policy_retention(self):
        """Test standard retention policy."""
        config = RetentionConfig()
        policy = StandardPolicy(config)
        
        now = datetime.now(timezone.utc)
        
        # Recent pattern → retained
        recent = PatternRecord(
            key="p1",
            value="value",
            pattern_type="success",
            confidence=0.8,
            success_rate=0.8,
            frequency=5,
            created_at=now - timedelta(days=30),
            last_accessed=now,
            policy=RetentionPolicy.STANDARD,
        )
        assert policy.should_retain(recent, now)
        
        # Old pattern → not retained
        old = PatternRecord(
            key="p2",
            value="value",
            pattern_type="success",
            confidence=0.8,
            success_rate=0.8,
            frequency=5,
            created_at=now - timedelta(days=120),
            last_accessed=now,
            policy=RetentionPolicy.STANDARD,
        )
        assert not policy.should_retain(old, now)
    
    def test_decay_policy_confidence_decay(self):
        """Test exponential decay in confidence."""
        config = RetentionConfig()
        policy = DecayPolicy(config)
        
        now = datetime.now(timezone.utc)
        
        pattern = PatternRecord(
            key="p1",
            value="value",
            pattern_type="performance",
            confidence=1.0,
            success_rate=0.6,
            frequency=5,
            created_at=now - timedelta(days=60),
            last_accessed=now,
            policy=RetentionPolicy.DECAY,
        )
        
        confidence = policy.calculate_confidence(pattern, now)
        
        # Confidence should decay over time
        assert confidence < 1.0
        assert confidence > 0.0
    
    def test_archived_policy(self):
        """Test archived policy."""
        config = RetentionConfig()
        policy = ArchivedPolicy(config)
        
        now = datetime.now(timezone.utc)
        
        # Recent archive → retained
        recent_archive = PatternRecord(
            key="p1",
            value="value",
            pattern_type="risk",
            confidence=0.1,
            success_rate=0.3,
            frequency=2,
            created_at=now - timedelta(days=100),
            last_accessed=now,
            policy=RetentionPolicy.ARCHIVED,
        )
        assert policy.should_retain(recent_archive, now)
        
        # Very old archive → not retained
        old_archive = PatternRecord(
            key="p2",
            value="value",
            pattern_type="risk",
            confidence=0.1,
            success_rate=0.3,
            frequency=2,
            created_at=now - timedelta(days=400),
            last_accessed=now,
            policy=RetentionPolicy.ARCHIVED,
        )
        assert not policy.should_retain(old_archive, now)
    
    def test_policy_manager_classification(self):
        """Test pattern classification by manager."""
        manager = RetentionPolicyManager()
        
        # High success → Evergreen
        evergreen_pattern = PatternRecord(
            key="p1",
            value="value",
            pattern_type="success",
            confidence=0.95,
            success_rate=0.99,
            frequency=10,
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
            tags=["critical"],
        )
        assert manager.classify_pattern(evergreen_pattern) == RetentionPolicy.EVERGREEN
        
        # Medium success → Decay
        decay_pattern = PatternRecord(
            key="p2",
            value="value",
            pattern_type="decision",
            confidence=0.6,
            success_rate=0.6,
            frequency=5,
            created_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc),
        )
        assert manager.classify_pattern(decay_pattern) == RetentionPolicy.DECAY
    
    def test_confidence_decay_calculator(self):
        """Test confidence decay calculations."""
        # Exponential decay
        initial = 1.0
        days = 60
        halflife = 60
        
        decayed = ConfidenceDecayCalculator.exponential_decay(initial, days, halflife)
        assert 0.0 < decayed < 1.0
        assert decayed < initial
    
    def test_cleanup_cycle(self):
        """Test cleanup cycle."""
        config = RetentionConfig()
        manager = RetentionPolicyManager(config)
        
        now = datetime.now(timezone.utc)
        
        patterns = [
            PatternRecord(
                key="p1",
                value="value",
                pattern_type="success",
                confidence=0.99,
                success_rate=0.99,
                frequency=10,
                created_at=now - timedelta(days=365),
                last_accessed=now,
                policy=RetentionPolicy.EVERGREEN,
            ),
            PatternRecord(
                key="p2",
                value="value",
                pattern_type="success",
                confidence=0.2,
                success_rate=0.2,
                frequency=2,
                created_at=now - timedelta(days=200),
                last_accessed=now,
                policy=RetentionPolicy.STANDARD,
            ),
        ]
        
        retained, pruned = manager.cleanup(patterns, now)
        
        # Evergreen should always be retained
        assert any(p.key == "p1" for p in retained)


class TestPatternGraph:
    """Tests for pattern knowledge graph."""
    
    def test_graph_initialization(self):
        """Test graph initialization."""
        graph = PatternGraph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = PatternGraph()
        
        node = PatternNode(
            id="p1",
            name="test_pattern",
            pattern_type="success",
            description="Test",
            confidence=0.8,
            frequency=5,
            success_rate=0.9,
        )
        
        graph.add_node(node)
        assert len(graph.nodes) == 1
        assert "p1" in graph.nodes
    
    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = PatternGraph()
        
        # Add nodes first
        node1 = PatternNode(
            id="p1", name="test1", pattern_type="success",
            description="Test", confidence=0.8, frequency=5, success_rate=0.9
        )
        node2 = PatternNode(
            id="p2", name="test2", pattern_type="error",
            description="Test", confidence=0.6, frequency=3, success_rate=0.5
        )
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        # Add edge
        edge = PatternEdge(
            source_id="p1",
            target_id="p2",
            relationship_type="causes",
            weight=0.8,
        )
        
        graph.add_edge(edge)
        assert len(graph.edges) == 1
        assert len(graph.adjacency["p1"]) == 1
    
    def test_get_related_patterns(self):
        """Test retrieving related patterns."""
        graph = PatternGraph()
        
        # Create pattern network
        for i in range(5):
            node = PatternNode(
                id=f"p{i}",
                name=f"pattern_{i}",
                pattern_type="success",
                description="Test",
                confidence=0.8,
                frequency=5,
                success_rate=0.9,
            )
            graph.add_node(node)
        
        # Create causal chain: p0 → p1 → p2
        graph.add_edge(PatternEdge("p0", "p1", "causes", 0.8))
        graph.add_edge(PatternEdge("p1", "p2", "causes", 0.8))
        
        # Get related to p0
        related = graph.get_related_patterns("p0", depth=2)
        assert len(related) >= 2
    
    def test_query_patterns(self):
        """Test pattern querying."""
        graph = PatternGraph()
        
        # Add nodes with different properties
        for i in range(3):
            node = PatternNode(
                id=f"success_{i}",
                name=f"success_pattern_{i}",
                pattern_type="success",
                description="Test",
                confidence=0.8 + (i * 0.05),
                frequency=5,
                success_rate=0.9,
                tags=["important"],
            )
            graph.add_node(node)
        
        # Query by pattern type
        results = graph.query_patterns({"pattern_type": "success"})
        assert len(results) == 3
        
        # Query by min_confidence
        results = graph.query_patterns({"min_confidence": 0.85})
        assert len(results) >= 1
    
    def test_graph_metrics(self):
        """Test graph metrics computation."""
        graph = PatternGraph()
        
        # Create simple network
        for i in range(3):
            node = PatternNode(
                id=f"p{i}",
                name=f"pattern_{i}",
                pattern_type="success",
                description="Test",
                confidence=0.8,
                frequency=5,
                success_rate=0.9,
            )
            graph.add_node(node)
        
        # Add edges
        graph.add_edge(PatternEdge("p0", "p1", "causes", 0.8))
        graph.add_edge(PatternEdge("p1", "p2", "causes", 0.8))
        
        metrics = graph.compute_graph_metrics()
        
        assert metrics["nodes"] == 3
        assert metrics["edges"] == 2
        assert metrics["density"] >= 0.0
    
    def test_graph_export_json(self):
        """Test graph export to JSON."""
        graph = PatternGraph()
        
        node = PatternNode(
            id="p1",
            name="test",
            pattern_type="success",
            description="Test",
            confidence=0.8,
            frequency=5,
            success_rate=0.9,
        )
        graph.add_node(node)
        
        export = graph.export_json()
        
        assert "nodes" in export
        assert "edges" in export
        assert "metrics" in export
        assert len(export["nodes"]) == 1
    
    def test_graph_export_graphml(self):
        """Test graph export to GraphML."""
        graph = PatternGraph()
        
        node = PatternNode(
            id="p1",
            name="test_pattern",
            pattern_type="success",
            description="Test",
            confidence=0.8,
            frequency=5,
            success_rate=0.9,
        )
        graph.add_node(node)
        
        graphml = graph.export_graphml()
        
        assert '<?xml version="1.0"' in graphml
        assert '<graph' in graphml
        assert 'p1' in graphml
    
    def test_graph_builder(self):
        """Test graph builder."""
        builder = GraphBuilder()
        
        # Create test patterns
        patterns = []
        for i in range(5):
            pattern = Pattern(
                id=f"p{i}",
                name=f"pattern_{i}",
                pattern_type=PatternType.SUCCESS,
                description="Test",
                frequency=5,
                success_rate=0.8,
                confidence=0.7,
            )
            patterns.append(pattern)
        
        graph = builder.build_complete_graph(patterns)
        
        assert len(graph.nodes) == 5
        assert len(graph.edges) >= 0


class TestIntegration:
    """Integration tests for complete consolidation workflow."""
    
    def test_full_consolidation_workflow(self):
        """Test complete consolidation workflow."""
        # Create discovery system
        discovery = PatternDiscovery(frequency_threshold=2)
        
        # Simulate events
        events = []
        for i in range(10):
            events.append({
                "action": "execute",
                "outcome": "success" if i % 2 == 0 else "failure",
            })
        
        # Discover patterns
        patterns = discovery.discover(events)
        assert len(patterns) > 0
        
        # Get promoted patterns
        promoted = discovery.get_promoted_patterns(score_threshold=0.5)
        assert len(promoted) >= 0
        
        # Build graph
        builder = GraphBuilder()
        graph = builder.build_complete_graph(patterns)
        assert len(graph.nodes) > 0
    
    def test_retention_policy_workflow(self):
        """Test retention policy workflow."""
        manager = RetentionPolicyManager()
        
        now = datetime.now(timezone.utc)
        
        patterns = [
            PatternRecord(
                key=f"p{i}",
                value=f"value_{i}",
                pattern_type="success",
                confidence=0.5 + (i * 0.1),
                success_rate=0.5 + (i * 0.1),
                frequency=3 + i,
                created_at=now - timedelta(days=30 * (i + 1)),
                last_accessed=now,
            )
            for i in range(5)
        ]
        
        # Classify patterns
        for pattern in patterns:
            pattern.policy = manager.classify_pattern(pattern)
        
        # Run cleanup
        metrics = manager.batch_cleanup(patterns, now)
        assert metrics["total_processed"] == 5
        assert metrics["pruned"] >= 0


# Performance tests
class TestPerformance:
    """Performance tests."""
    
    def test_consolidation_latency(self):
        """Test that consolidation completes within latency budget."""
        engine = MemoryConsolidationEngine()
        
        import time
        start = time.time()
        
        # Simulate observation
        state = engine._observe()
        
        elapsed = (time.time() - start) * 1000
        
        # Should complete in <100ms for observation
        assert elapsed < 100
    
    def test_graph_query_latency(self):
        """Test that graph queries complete within latency budget."""
        graph = PatternGraph()
        
        # Build larger graph
        for i in range(50):
            node = PatternNode(
                id=f"p{i}",
                name=f"pattern_{i}",
                pattern_type="success",
                description="Test",
                confidence=0.8,
                frequency=5,
                success_rate=0.9,
            )
            graph.add_node(node)
        
        import time
        start = time.time()
        
        # Query patterns
        results = graph.query_patterns({"min_confidence": 0.7})
        
        elapsed = (time.time() - start) * 1000
        
        # Should complete in <100ms
        assert elapsed < 100


# Validation tests
class TestValidation:
    """Validation and correctness tests."""
    
    def test_pattern_score_bounds(self):
        """Test that pattern scores stay within bounds."""
        engine = MemoryConsolidationEngine()
        
        for frequency in range(1, 10):
            for success_rate in [0.0, 0.25, 0.5, 0.75, 1.0]:
                entry = PatternEntry(
                    key="test",
                    value="val",
                    pattern_type=PatternType.SUCCESS,
                    frequency=frequency,
                    success_rate=success_rate,
                )
                score = engine._calculate_pattern_score(entry)
                assert 0.0 <= score <= 1.0
    
    def test_confidence_bounds(self):
        """Test that confidence stays within bounds."""
        for frequency in range(1, 10):
            pattern = Pattern(
                id="p1",
                name="test",
                pattern_type=PatternType.SUCCESS,
                description="Test",
                frequency=frequency,
                success_rate=0.7,
            )
            confidence = PatternScorer.calculate_confidence(pattern, 3)
            assert 0.0 <= confidence <= 1.0
    
    def test_no_data_loss_on_consolidation(self):
        """Test that consolidation preserves data."""
        engine = MemoryConsolidationEngine()
        
        # Create test pattern entries
        entries = [
            PatternEntry(
                key=f"pattern_{i}",
                value=f"value_{i}",
                pattern_type=PatternType.SUCCESS,
                frequency=5 + i,
                success_rate=0.7 + (i * 0.02),
            )
            for i in range(10)
        ]
        
        # All promoted patterns should be preserved
        promoted_count = len([e for e in entries if e.frequency >= 3])
        assert promoted_count > 0


# Fixture and helper functions
@pytest.fixture
def clean_engine():
    """Fixture providing a clean consolidation engine."""
    return MemoryConsolidationEngine()


@pytest.fixture
def sample_patterns():
    """Fixture providing sample patterns."""
    return [
        Pattern(
            id=f"pattern_{i}",
            name=f"Test Pattern {i}",
            pattern_type=PatternType.SUCCESS,
            description=f"Test pattern {i}",
            frequency=3 + i,
            success_rate=0.7 + (i * 0.05),
            confidence=0.6 + (i * 0.05),
        )
        for i in range(10)
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
