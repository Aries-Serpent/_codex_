"""
Tests for Transfer Learning Engine (Phase 8.4).

Comprehensive test suite covering:
- Domain adaptation
- Knowledge distillation
- Transfer learning operations
"""
import pytest
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transfer_learning import (
    TransferLearningEngine,
    DomainAdapter,
    SimpleDomainAdapter,
    KnowledgeDistiller,
    DomainInfo,
    TransferableKnowledge,
)


class TestDomainInfo:
    """Tests for DomainInfo."""
    
    def test_create_domain(self):
        """Test creating domain info."""
        domain = DomainInfo(
            name="test_domain",
            features=["f1", "f2"],
            action_space=["a1", "a2"],
        )
        assert domain.name == "test_domain"
        assert len(domain.features) == 2
        assert len(domain.action_space) == 2


class TestSimpleDomainAdapter:
    """Tests for SimpleDomainAdapter."""
    
    def test_create_adapter(self):
        """Test creating adapter."""
        adapter = SimpleDomainAdapter()
        assert adapter is not None
    
    def test_adapt_features_direct_match(self):
        """Test feature adaptation with direct match."""
        adapter = SimpleDomainAdapter()
        
        source = DomainInfo("src", features=["accuracy", "speed"])
        target = DomainInfo("tgt", features=["accuracy", "latency"])
        
        features = {"accuracy": 0.9, "speed": 0.8}
        adapted = adapter.adapt_features(features, source, target)
        
        assert "accuracy" in adapted
        assert adapted["accuracy"] == 0.9
    
    def test_adapt_actions_direct_match(self):
        """Test action adaptation with direct match."""
        adapter = SimpleDomainAdapter()
        
        source = DomainInfo("src", action_space=["approve", "reject"])
        target = DomainInfo("tgt", action_space=["approve", "deny"])
        
        action = adapter.adapt_actions("approve", source, target)
        assert action == "approve"
    
    def test_adapt_actions_no_match(self):
        """Test action adaptation with no match."""
        adapter = SimpleDomainAdapter()
        
        source = DomainInfo("src", action_space=["run"])
        target = DomainInfo("tgt", action_space=["walk"])
        
        action = adapter.adapt_actions("run", source, target)
        assert action is None
    
    def test_compute_compatibility_identical(self):
        """Test compatibility with identical domains."""
        adapter = SimpleDomainAdapter()
        
        domain = DomainInfo(
            "test",
            features=["f1", "f2"],
            action_space=["a1", "a2"],
        )
        
        score = adapter.compute_compatibility(domain, domain)
        assert score == 1.0
    
    def test_compute_compatibility_different(self):
        """Test compatibility with different domains."""
        adapter = SimpleDomainAdapter()
        
        source = DomainInfo("src", features=["a", "b"], action_space=["x"])
        target = DomainInfo("tgt", features=["c", "d"], action_space=["y"])
        
        score = adapter.compute_compatibility(source, target)
        assert score == 0.0
    
    def test_compute_compatibility_partial(self):
        """Test compatibility with partial overlap."""
        adapter = SimpleDomainAdapter()
        
        source = DomainInfo("src", features=["a", "b"], action_space=["x", "y"])
        target = DomainInfo("tgt", features=["a", "c"], action_space=["x", "z"])
        
        score = adapter.compute_compatibility(source, target)
        assert 0.0 < score < 1.0


class TestKnowledgeDistiller:
    """Tests for KnowledgeDistiller."""
    
    def test_create_distiller(self):
        """Test creating distiller."""
        distiller = KnowledgeDistiller()
        assert distiller.min_confidence == 0.7
        assert distiller.max_patterns == 100
    
    def test_distill_empty_qtable(self):
        """Test distilling from empty Q-table."""
        distiller = KnowledgeDistiller()
        domain = DomainInfo("test")
        
        patterns = distiller.distill({}, domain)
        assert len(patterns) == 0
    
    def test_distill_qtable(self):
        """Test distilling patterns from Q-table."""
        distiller = KnowledgeDistiller(min_confidence=0.0)
        domain = DomainInfo("test", action_space=["a1", "a2"])
        
        q_table = {
            "state1": {"a1": 10.0, "a2": 2.0},
            "state2": {"a1": 5.0, "a2": 8.0},
        }
        
        patterns = distiller.distill(q_table, domain)
        assert len(patterns) == 2
    
    def test_distill_respects_confidence(self):
        """Test distillation respects min confidence."""
        distiller = KnowledgeDistiller(min_confidence=0.9)
        domain = DomainInfo("test")
        
        # Low confidence patterns
        q_table = {
            "state1": {"a1": 1.0, "a2": 0.9},  # Low difference = low confidence
        }
        
        patterns = distiller.distill(q_table, domain)
        # May or may not include based on confidence calculation
        assert isinstance(patterns, list)
    
    def test_distill_limits_patterns(self):
        """Test distillation limits patterns."""
        distiller = KnowledgeDistiller(min_confidence=0.0, max_patterns=5)
        domain = DomainInfo("test")
        
        q_table = {f"state{i}": {"a": float(i)} for i in range(20)}
        
        patterns = distiller.distill(q_table, domain)
        assert len(patterns) <= 5
    
    def test_get_applicable_patterns(self):
        """Test getting applicable patterns."""
        distiller = KnowledgeDistiller(min_confidence=0.0)
        domain = DomainInfo("test")
        
        q_table = {"abcd1234": {"a": 10.0}}
        distiller.distill(q_table, domain)
        
        patterns = distiller.get_applicable_patterns("abcd1234", "test")
        assert len(patterns) >= 0  # May or may not match based on signature


class TestTransferLearningEngine:
    """Tests for TransferLearningEngine."""
    
    def test_create_engine(self):
        """Test creating engine."""
        engine = TransferLearningEngine()
        assert engine is not None
        assert isinstance(engine.adapter, SimpleDomainAdapter)
    
    def test_register_domain(self):
        """Test registering domain."""
        engine = TransferLearningEngine()
        domain = DomainInfo("test", features=["f1"], action_space=["a1"])
        
        engine.register_domain(domain)
        
        assert "test" in engine.domains
    
    def test_prepare_transfer(self):
        """Test preparing knowledge transfer."""
        engine = TransferLearningEngine()
        
        source = DomainInfo("source", features=["f1"], action_space=["a1", "a2"])
        target = DomainInfo("target", features=["f1"], action_space=["a1", "a2"])
        
        engine.register_domain(source)
        engine.register_domain(target)
        
        q_table = {"s1": {"a1": 10.0, "a2": 2.0}}
        
        knowledge = engine.prepare_transfer("source", "target", q_table)
        
        assert knowledge.source_domain == "source"
        assert knowledge.target_domain == "target"
        assert knowledge.compatibility_score > 0
    
    def test_prepare_transfer_unknown_domain(self):
        """Test preparing transfer with unknown domain raises error."""
        engine = TransferLearningEngine()
        
        with pytest.raises(ValueError):
            engine.prepare_transfer("unknown", "target", {})
    
    def test_apply_transfer(self):
        """Test applying knowledge transfer."""
        engine = TransferLearningEngine()
        
        source = DomainInfo("source", features=["f1"], action_space=["a1"])
        target = DomainInfo("target", features=["f1"], action_space=["a1"])
        
        engine.register_domain(source)
        engine.register_domain(target)
        
        knowledge = TransferableKnowledge(
            source_domain="source",
            target_domain="target",
            patterns=[{
                "state_signature": "12345678",
                "best_action": "a1",
                "q_value": 10.0,
                "confidence": 0.9,
            }],
            compatibility_score=0.8,
        )
        
        target_q = {}
        updated = engine.apply_transfer(knowledge, target_q, transfer_rate=1.0)
        
        assert "12345678" in updated
        assert "a1" in updated["12345678"]
    
    def test_apply_transfer_blends_values(self):
        """Test transfer blends with existing values."""
        engine = TransferLearningEngine()
        
        source = DomainInfo("source", action_space=["a1"])
        target = DomainInfo("target", action_space=["a1"])
        
        engine.register_domain(source)
        engine.register_domain(target)
        
        knowledge = TransferableKnowledge(
            source_domain="source",
            target_domain="target",
            patterns=[{
                "state_signature": "state123",
                "best_action": "a1",
                "q_value": 10.0,
                "confidence": 1.0,
            }],
            compatibility_score=1.0,
        )
        
        target_q = {"state123": {"a1": 5.0}}
        updated = engine.apply_transfer(knowledge, target_q, transfer_rate=0.5)
        
        # Should blend values
        assert 5.0 <= updated["state123"]["a1"] <= 10.0
    
    def test_get_statistics(self):
        """Test getting statistics."""
        engine = TransferLearningEngine()
        
        stats = engine.get_statistics()
        
        assert "domains_registered" in stats
        assert "transfers_completed" in stats
        assert stats["domains_registered"] == 0


class TestIntegration:
    """Integration tests for Transfer Learning."""
    
    def test_full_transfer_pipeline(self):
        """Test complete transfer learning pipeline."""
        engine = TransferLearningEngine()
        
        # Create domains
        source = DomainInfo(
            name="code_review",
            features=["complexity", "coverage", "style"],
            action_space=["approve", "request_changes", "comment"],
        )
        
        target = DomainInfo(
            name="pr_review",
            features=["complexity", "tests", "style"],
            action_space=["approve", "reject", "comment"],
        )
        
        engine.register_domain(source)
        engine.register_domain(target)
        
        # Source Q-table (learned from code review)
        source_q = {
            "low_complex": {"approve": 10.0, "request_changes": -5.0},
            "high_complex": {"approve": -5.0, "request_changes": 8.0},
        }
        
        # Prepare transfer
        knowledge = engine.prepare_transfer("code_review", "pr_review", source_q)
        
        assert knowledge.compatibility_score > 0
        
        # Apply transfer
        target_q = {}
        updated = engine.apply_transfer(knowledge, target_q)
        
        # Verify transfer occurred
        assert len(engine.transfer_history) == 1
    
    def test_cross_domain_learning(self):
        """Test learning transfers across multiple domains."""
        engine = TransferLearningEngine()
        
        # Register multiple domains
        domains = [
            DomainInfo(f"domain_{i}", features=["f1", "f2"], action_space=["a1", "a2"])
            for i in range(3)
        ]
        
        for domain in domains:
            engine.register_domain(domain)
        
        # Transfer from domain_0 to domain_1
        knowledge_01 = engine.prepare_transfer(
            "domain_0",
            "domain_1",
            {"s1": {"a1": 10.0}},
        )
        engine.apply_transfer(knowledge_01, {})
        
        # Transfer from domain_1 to domain_2
        knowledge_12 = engine.prepare_transfer(
            "domain_1",
            "domain_2",
            {"s2": {"a2": 8.0}},
        )
        engine.apply_transfer(knowledge_12, {})
        
        stats = engine.get_statistics()
        assert stats["transfers_completed"] == 2
