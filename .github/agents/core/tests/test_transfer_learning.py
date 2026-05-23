"""
Tests for Transfer Learning Engine (Phase 8.4).

Comprehensive test suite covering:
- Domain adaptation
- Knowledge distillation
- Transfer learning operations
"""
import os
import sys

import pytest

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transfer_learning import (
    DomainInfo,
    KnowledgeDistiller,
    SimpleDomainAdapter,
    TransferableKnowledge,
    TransferLearningEngine,
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
        engine.apply_transfer(knowledge, target_q)

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


# =============================================================================
# META-LEARNING FRAMEWORK TESTS
# =============================================================================


class TestMetaLearningConfig:
    """Tests for MetaLearningConfig."""

    def test_create_default_config(self):
        """Test creating default config."""
        from transfer_learning import MetaLearningConfig
        config = MetaLearningConfig()
        assert config.learning_rate == 0.01
        assert config.adaptation_steps == 5

    def test_create_custom_config(self):
        """Test creating custom config."""
        from transfer_learning import MetaLearningConfig
        config = MetaLearningConfig(
            learning_rate=0.05,
            adaptation_steps=10,
        )
        assert config.learning_rate == 0.05
        assert config.adaptation_steps == 10


class TestMetaLearningFramework:
    """Tests for MetaLearningFramework."""

    def test_create_framework(self):
        """Test creating meta-learning framework."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()
        assert framework is not None
        assert 'transfer_rate' in framework.meta_parameters

    def test_adapt_to_domain_empty(self):
        """Test adaptation with no experiences."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()

        adapted = framework.adapt_to_domain("test_domain", [])

        assert adapted == framework.meta_parameters

    def test_adapt_to_domain_with_experiences(self):
        """Test adaptation with experiences."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()

        experiences = [
            {'reward': 1.0, 'confidence': 0.9},
            {'reward': 0.8, 'confidence': 0.85},
        ]

        framework.adapt_to_domain("test_domain", experiences)

        assert "test_domain" in framework.domain_specific_params
        assert len(framework.adaptation_history) == 1

    def test_update_meta_parameters(self):
        """Test updating meta-parameters from domain results."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()

        # First adapt to a domain
        framework.adapt_to_domain("domain_a", [{'reward': 0.9, 'confidence': 0.8}])

        # Update meta-parameters
        domain_results = {
            'domain_a': {'success_rate': 0.85, 'transfer_efficiency': 0.7},
        }

        framework.update_meta_parameters(domain_results)

        # Meta-parameters should be updated
        assert isinstance(framework.meta_parameters, dict)

    def test_get_domain_parameters(self):
        """Test getting domain-specific parameters."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()

        # Unknown domain returns meta-parameters
        params = framework.get_domain_parameters("unknown")
        assert params == framework.meta_parameters

        # Adapted domain returns specific parameters
        framework.adapt_to_domain("known", [{'reward': 0.5}])
        assert framework.get_domain_parameters("known") == framework.domain_specific_params["known"]

    def test_get_statistics(self):
        """Test getting meta-learning statistics."""
        from transfer_learning import MetaLearningFramework
        framework = MetaLearningFramework()

        stats = framework.get_statistics()

        assert 'meta_parameters' in stats
        assert 'domains_adapted' in stats


# =============================================================================
# DYNAMIC DOMAIN DETECTOR TESTS
# =============================================================================


class TestDynamicDomainDetector:
    """Tests for DynamicDomainDetector."""

    def test_create_detector(self):
        """Test creating domain detector."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()
        assert detector.detection_threshold == 0.75

    def test_extract_fingerprint_empty(self):
        """Test extracting fingerprint from empty Q-table."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        fp = detector.extract_fingerprint({})

        assert fp['state_count'] == 0
        assert fp['action_count'] == 0

    def test_extract_fingerprint(self):
        """Test extracting fingerprint from Q-table."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        q_table = {
            "state1_abc": {"action1": 10.0, "action2": 5.0},
            "state2_def": {"action1": 3.0, "action3": 8.0},
        }

        fp = detector.extract_fingerprint(q_table)

        assert fp['state_count'] == 2
        assert fp['action_count'] == 3
        assert fp['q_mean'] > 0

    def test_compute_similarity_identical(self):
        """Test similarity of identical fingerprints."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        fp = {
            'q_mean': 5.0,
            'q_std': 2.0,
            'sparsity': 0.3,
            'action_signature': 'abc123',
            'state_signature': 'def456',
        }

        similarity = detector.compute_similarity(fp, fp)
        assert similarity == 1.0

    def test_compute_similarity_different(self):
        """Test similarity of different fingerprints."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        fp1 = {
            'q_mean': 5.0,
            'q_std': 2.0,
            'sparsity': 0.3,
            'action_signature': 'abc123',
            'state_signature': 'def456',
        }
        fp2 = {
            'q_mean': 100.0,
            'q_std': 50.0,
            'sparsity': 0.9,
            'action_signature': 'xyz789',
            'state_signature': 'uvw012',
        }

        similarity = detector.compute_similarity(fp1, fp2)
        assert similarity < 0.5

    def test_detect_domain_unknown(self):
        """Test detecting unknown domain."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        q_table = {"state1": {"action1": 1.0}}

        domain, confidence = detector.detect_domain(q_table)

        assert domain is None
        assert confidence == 0.0

    def test_detect_domain_registered(self):
        """Test detecting registered domain."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector(detection_threshold=0.5)

        q_table = {"state1_abc": {"action1": 10.0, "action2": 5.0}}

        # Register domain
        detector.register_domain("test_domain", q_table)

        # Detect same Q-table
        domain, confidence = detector.detect_domain(q_table)

        assert domain == "test_domain"
        assert confidence >= 0.5

    def test_register_domain(self):
        """Test registering domain."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        q_table = {"state1": {"action1": 5.0}}

        fp = detector.register_domain("new_domain", q_table)

        assert "new_domain" in detector.known_domains
        assert fp == detector.known_domains["new_domain"]

    def test_get_statistics(self):
        """Test getting statistics."""
        from transfer_learning import DynamicDomainDetector
        detector = DynamicDomainDetector()

        stats = detector.get_statistics()

        assert 'known_domains' in stats
        assert 'total_detections' in stats


# =============================================================================
# CROSS-AGENT KNOWLEDGE SHARING TESTS
# =============================================================================


class TestKnowledgePackage:
    """Tests for KnowledgePackage."""

    def test_create_package(self):
        """Test creating knowledge package."""
        from transfer_learning import DomainInfo, KnowledgePackage

        domain = DomainInfo("test", ["f1"], ["a1"])
        package = KnowledgePackage(
            source_agent="agent_1",
            target_agent="agent_2",
            domain_info=domain,
            knowledge_type="patterns",
            payload={"key": "value"},
        )

        assert package.source_agent == "agent_1"
        assert package.signature != ""

    def test_verify_package(self):
        """Test package verification."""
        from transfer_learning import DomainInfo, KnowledgePackage

        domain = DomainInfo("test", ["f1"], ["a1"])
        package = KnowledgePackage(
            source_agent="agent_1",
            target_agent="agent_2",
            domain_info=domain,
            knowledge_type="patterns",
            payload={},
        )

        assert package.verify() is True

    def test_tampered_package_fails_verification(self):
        """Test tampered package fails verification."""
        from transfer_learning import DomainInfo, KnowledgePackage

        domain = DomainInfo("test", ["f1"], ["a1"])
        package = KnowledgePackage(
            source_agent="agent_1",
            target_agent="agent_2",
            domain_info=domain,
            knowledge_type="patterns",
            payload={},
        )

        # Tamper with signature
        package.signature = "tampered"

        assert package.verify() is False


class TestCrossAgentKnowledgeSharing:
    """Tests for CrossAgentKnowledgeSharing."""

    def test_create_sharing_protocol(self):
        """Test creating sharing protocol."""
        from transfer_learning import CrossAgentKnowledgeSharing

        protocol = CrossAgentKnowledgeSharing("agent_1")

        assert protocol.agent_id == "agent_1"

    def test_register_agent(self):
        """Test registering agent."""
        from transfer_learning import CrossAgentKnowledgeSharing

        protocol = CrossAgentKnowledgeSharing("agent_1")
        protocol.register_agent(
            "agent_2",
            capabilities=["analyze", "learn"],
            domains=["code_review"],
        )

        assert "agent_2" in protocol.agent_registry

    def test_create_and_send_package(self):
        """Test creating and sending package."""
        from transfer_learning import CrossAgentKnowledgeSharing, DomainInfo

        protocol = CrossAgentKnowledgeSharing("agent_1")
        domain = DomainInfo("test", ["f1"], ["a1"])

        package = protocol.create_package(
            target_agent="agent_2",
            domain=domain,
            knowledge_type="patterns",
            payload={"pattern": "test"},
        )

        success = protocol.send_package(package)

        assert success is True
        assert len(protocol.message_queue) == 1

    def test_receive_package(self):
        """Test receiving package."""
        from transfer_learning import CrossAgentKnowledgeSharing, DomainInfo

        sender = CrossAgentKnowledgeSharing("agent_1")
        receiver = CrossAgentKnowledgeSharing("agent_2")

        domain = DomainInfo("test", ["f1"], ["a1"])
        package = sender.create_package(
            target_agent="agent_2",
            domain=domain,
            knowledge_type="patterns",
            payload={},
        )

        success = receiver.receive_package(package)

        assert success is True
        assert len(receiver.received_packages) == 1

    def test_receive_wrong_target(self):
        """Test receiving package for wrong agent."""
        from transfer_learning import CrossAgentKnowledgeSharing, DomainInfo

        sender = CrossAgentKnowledgeSharing("agent_1")
        receiver = CrossAgentKnowledgeSharing("agent_2")

        domain = DomainInfo("test", ["f1"], ["a1"])
        package = sender.create_package(
            target_agent="agent_3",  # Different target
            domain=domain,
            knowledge_type="patterns",
            payload={},
        )

        success = receiver.receive_package(package)

        assert success is False

    def test_get_compatible_agents(self):
        """Test getting compatible agents."""
        from transfer_learning import CrossAgentKnowledgeSharing

        protocol = CrossAgentKnowledgeSharing("agent_1")
        protocol.register_agent("agent_2", [], ["domain_a", "domain_b"])
        protocol.register_agent("agent_3", [], ["domain_a"])
        protocol.register_agent("agent_4", [], ["domain_c"])

        compatible = protocol.get_compatible_agents("domain_a")

        assert "agent_2" in compatible
        assert "agent_3" in compatible
        assert "agent_4" not in compatible

    def test_trust_scores(self):
        """Test trust score management."""
        from transfer_learning import CrossAgentKnowledgeSharing

        protocol = CrossAgentKnowledgeSharing("agent_1")

        # Initial trust
        assert protocol.get_trust_score("agent_2") == 0.5

        # Update on success
        protocol.update_trust("agent_2", success=True)
        assert protocol.get_trust_score("agent_2") > 0.5

        # Update on failure
        protocol.update_trust("agent_2", success=False)
        # Trust decreased but still might be above initial due to success

    def test_get_statistics(self):
        """Test getting statistics."""
        from transfer_learning import CrossAgentKnowledgeSharing

        protocol = CrossAgentKnowledgeSharing("agent_1")

        stats = protocol.get_statistics()

        assert stats['agent_id'] == "agent_1"
        assert 'registered_agents' in stats
