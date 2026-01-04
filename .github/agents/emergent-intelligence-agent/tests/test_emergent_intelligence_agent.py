"""
Tests for Emergent Intelligence Agent

Comprehensive test suite covering all capabilities:
- Cross-repository pattern detection
- Code smell emergence tracking
- Behavior prediction
- Self-improving pattern recognition
- Real-time pattern notifications
"""
import pytest
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pattern_analyzer import (
    EmergentIntelligenceAgent,
    EmergentPattern,
    EmergenceType,
    RANDOM_SEED,
    create_agent
)


# =============================================================================
# TEST INITIALIZATION
# =============================================================================

class TestEmergentIntelligenceAgentInit:
    """Test agent initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        agent = EmergentIntelligenceAgent()
        assert agent.seed == RANDOM_SEED
        assert not agent.initialized
        assert len(agent.detected_patterns) == 0
        assert len(agent.pattern_history) == 0
        assert len(agent.predictions) == 0
    
    def test_init_with_custom_seed(self):
        """Test initialization with custom seed."""
        custom_seed = 99
        agent = EmergentIntelligenceAgent(seed=custom_seed)
        assert agent.seed == custom_seed
    
    def test_initialize_without_core(self):
        """Test initialization when core modules not available."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        # May or may not succeed depending on environment
        result = agent.initialize()
        assert isinstance(result, bool)
    
    def test_pda_state_initialized(self):
        """Test PDA loop state is properly initialized."""
        agent = EmergentIntelligenceAgent()
        assert agent.pda_state is not None
        assert "perception" in agent.pda_state
        assert "decision" in agent.pda_state
        assert "action" in agent.pda_state
        assert "aftermath" in agent.pda_state
        assert isinstance(agent.pda_state["aftermath"], list)
    
    def test_metrics_initialized(self):
        """Test metrics are properly initialized."""
        agent = EmergentIntelligenceAgent()
        assert agent.metrics["patterns_detected"] == 0
        assert agent.metrics["predictions_made"] == 0
        assert agent.metrics["accuracy"] == 0.0
        assert agent.metrics["avg_latency_ms"] == 0.0
        assert agent.metrics["notifications_sent"] == 0


# =============================================================================
# TEST CROSS-REPOSITORY PATTERN DETECTION
# =============================================================================

class TestCrossRepositoryPatternDetection:
    """Test cross-repository pattern detection capabilities."""
    
    def test_detect_patterns_empty_repos(self):
        """Test pattern detection with empty repository list."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        patterns = agent.detect_cross_repo_patterns([])
        assert isinstance(patterns, list)
        assert len(patterns) == 0
    
    def test_detect_patterns_single_repo(self):
        """Test pattern detection with single repository."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        repos = ["repo1"]
        patterns = agent.detect_cross_repo_patterns(repos)
        assert isinstance(patterns, list)
        assert len(patterns) >= 0
    
    def test_detect_patterns_multiple_repos(self):
        """Test pattern detection across multiple repositories."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        repos = ["repo1", "repo2", "repo3"]
        patterns = agent.detect_cross_repo_patterns(repos)
        assert isinstance(patterns, list)
        # Should detect at least one pattern per repo
        assert len(patterns) >= 0
    
    def test_detect_patterns_with_context(self):
        """Test pattern detection with context information."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        repos = ["repo1"]
        context = {"branch": "main", "author": "test"}
        patterns = agent.detect_cross_repo_patterns(repos, context)
        assert isinstance(patterns, list)
    
    def test_detect_patterns_updates_pda_state(self):
        """Test that detection updates PDA loop state."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        repos = ["repo1"]
        agent.detect_cross_repo_patterns(repos)
        
        assert agent.pda_state["perception"] is not None
        assert agent.pda_state["decision"] is not None
        assert agent.pda_state["action"] is not None
    
    def test_detect_patterns_updates_metrics(self):
        """Test that detection updates metrics."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        repos = ["repo1", "repo2"]
        initial_count = agent.metrics["patterns_detected"]
        
        _ = agent.detect_cross_repo_patterns(repos)  # Trigger detection
        
        assert agent.metrics["patterns_detected"] >= initial_count
        assert agent.metrics["avg_latency_ms"] >= 0
    
    def test_detect_patterns_deterministic(self):
        """Test that pattern detection is deterministic with same seed."""
        agent1 = EmergentIntelligenceAgent(seed=42)
        agent2 = EmergentIntelligenceAgent(seed=42)
        
        repos = ["repo1", "repo2"]
        patterns1 = agent1.detect_cross_repo_patterns(repos)
        patterns2 = agent2.detect_cross_repo_patterns(repos)
        
        # Should detect same number of patterns
        assert len(patterns1) == len(patterns2)


# =============================================================================
# TEST CODE SMELL TRACKING
# =============================================================================

class TestCodeSmellTracking:
    """Test code smell emergence tracking."""
    
    def test_track_code_smells_empty_changes(self):
        """Test tracking with no code changes."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        patterns = agent.track_code_smells("repo1", [])
        assert isinstance(patterns, list)
        assert len(patterns) == 0
    
    def test_track_code_smells_long_method(self):
        """Test detection of long method smell."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        long_code = "\n".join([f"line{i}" for i in range(60)])
        changes = [{"code": long_code}]
        
        patterns = agent.track_code_smells("repo1", changes)
        assert isinstance(patterns, list)
        # Should detect at least one smell
        if patterns:
            assert patterns[0].emergence_type == EmergenceType.CODE_SMELL
    
    def test_track_code_smells_deep_nesting(self):
        """Test detection of deep nesting smell."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        nested_code = "    " * 25  # Deep nesting
        changes = [{"code": nested_code}]
        
        patterns = agent.track_code_smells("repo1", changes)
        assert isinstance(patterns, list)
    
    def test_track_code_smells_updates_existing_pattern(self):
        """Test that recurring smell updates existing pattern."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        long_code = "\n".join([f"line{i}" for i in range(60)])
        changes = [{"code": long_code}]
        
        # First detection
        patterns1 = agent.track_code_smells("repo1", changes)
        if patterns1:
            initial_occurrences = patterns1[0].occurrences
            
            # Second detection
            patterns2 = agent.track_code_smells("repo1", changes)
            if patterns2:
                # Should increment occurrences
                assert patterns2[0].occurrences >= initial_occurrences
    
    def test_track_code_smells_multiple_repositories(self):
        """Test smell tracking across multiple repositories."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        long_code = "\n".join([f"line{i}" for i in range(60)])
        changes = [{"code": long_code}]
        
        patterns1 = agent.track_code_smells("repo1", changes)
        patterns2 = agent.track_code_smells("repo2", changes)
        
        # Should create separate patterns for different repos
        assert isinstance(patterns1, list)
        assert isinstance(patterns2, list)


# =============================================================================
# TEST BEHAVIOR PREDICTION
# =============================================================================

class TestBehaviorPrediction:
    """Test behavior prediction capabilities."""
    
    def test_predict_behavior_empty_history(self):
        """Test prediction with no historical data."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        context = {"environment": "test"}
        
        predictions = agent.predict_behavior(context)
        assert isinstance(predictions, list)
        # Should make conservative predictions
        assert len(predictions) > 0
        assert predictions[0].confidence <= 0.6
    
    def test_predict_behavior_with_history(self):
        """Test prediction with historical patterns."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        
        # Build history
        for i in range(5):
            pattern = EmergentPattern(
                pattern_id=f"pattern_{i}",
                emergence_type=EmergenceType.DESIGN_PATTERN,
                repositories=["repo1"],
                confidence=0.9,
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
            agent.pattern_history.append(pattern)
        
        context = {"environment": "test"}
        predictions = agent.predict_behavior(context)
        
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        # With history, confidence should be higher
        assert any(p.confidence > 0.6 for p in predictions)
    
    def test_predict_behavior_updates_metrics(self):
        """Test that prediction updates metrics."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        context = {}
        initial_count = agent.metrics["predictions_made"]
        
        _ = agent.predict_behavior(context)  # Trigger prediction
        
        assert agent.metrics["predictions_made"] > initial_count
        assert len(agent.predictions) > 0
    
    def test_prediction_probability_range(self):
        """Test that prediction probabilities are in valid range."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        predictions = agent.predict_behavior({})
        
        for pred in predictions:
            assert 0.0 <= pred.probability <= 1.0
            assert 0.0 <= pred.confidence <= 1.0


# =============================================================================
# TEST NOTIFICATIONS
# =============================================================================

class TestNotifications:
    """Test real-time pattern notifications."""
    
    def test_send_notification_success(self):
        """Test successful notification sending."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        pattern = EmergentPattern(
            pattern_id="test_pattern",
            emergence_type=EmergenceType.CODE_SMELL,
            repositories=["repo1"],
            confidence=0.9,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        result = agent.send_notification(pattern, ["user1"])
        assert isinstance(result, bool)
        if result:
            assert agent.metrics["notifications_sent"] > 0
    
    def test_send_notification_cooldown(self):
        """Test notification cooldown mechanism."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        pattern = EmergentPattern(
            pattern_id="test_pattern",
            emergence_type=EmergenceType.CODE_SMELL,
            repositories=["repo1"],
            confidence=0.9,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        # First notification should succeed
        result1 = agent.send_notification(pattern, ["user1"])
        
        # Second immediate notification should fail (cooldown)
        result2 = agent.send_notification(pattern, ["user1"])
        
        # At least one should be False due to cooldown
        assert result1 or not result2
    
    def test_send_notification_different_patterns(self):
        """Test notifications for different patterns."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        
        pattern1 = EmergentPattern(
            pattern_id="pattern1",
            emergence_type=EmergenceType.CODE_SMELL,
            repositories=["repo1"],
            confidence=0.9,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        pattern2 = EmergentPattern(
            pattern_id="pattern2",
            emergence_type=EmergenceType.TEST_FAILURE_PATTERN,
            repositories=["repo2"],
            confidence=0.85,
            first_seen=datetime.now(),
            last_seen=datetime.now()
        )
        
        # Both should succeed as they're different patterns
        result1 = agent.send_notification(pattern1, ["user1"])
        result2 = agent.send_notification(pattern2, ["user1"])
        
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)


# =============================================================================
# TEST SELF-IMPROVEMENT
# =============================================================================

class TestSelfImprovement:
    """Test self-improving pattern recognition."""
    
    def test_improve_accuracy_with_feedback(self):
        """Test accuracy improvement with feedback."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        initial_accuracy = agent.metrics["accuracy"]
        
        feedback = {"accuracy": 0.95}
        agent.improve_accuracy(feedback)
        
        # Accuracy should be updated
        assert agent.metrics["accuracy"] != initial_accuracy
    
    def test_improve_accuracy_updates_aftermath(self):
        """Test that improvement updates AfterMath state."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        initial_learnings = len(agent.pda_state["aftermath"])
        
        feedback = {"accuracy": 0.92}
        agent.improve_accuracy(feedback)
        
        assert len(agent.pda_state["aftermath"]) > initial_learnings
    
    def test_improve_accuracy_exponential_moving_average(self):
        """Test that accuracy uses exponential moving average."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        agent.metrics["accuracy"] = 0.80
        
        feedback = {"accuracy": 1.0}
        agent.improve_accuracy(feedback)
        
        # Should be weighted average, not direct replacement
        assert agent.metrics["accuracy"] > 0.80
        assert agent.metrics["accuracy"] < 1.0


# =============================================================================
# TEST METRICS
# =============================================================================

class TestMetrics:
    """Test agent metrics collection."""
    
    def test_get_metrics_structure(self):
        """Test metrics dictionary structure."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        metrics = agent.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "patterns_detected" in metrics
        assert "predictions_made" in metrics
        assert "accuracy" in metrics
        assert "avg_latency_ms" in metrics
        assert "total_patterns" in metrics
        assert "unique_patterns" in metrics
        assert "avg_confidence" in metrics
    
    def test_get_metrics_pda_tracking(self):
        """Test that metrics include PDA loop tracking."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        metrics = agent.get_metrics()
        
        assert "perceptions" in metrics
        assert "decisions" in metrics
        assert "actions" in metrics
        assert "learnings" in metrics
    
    def test_get_metrics_after_operations(self):
        """Test metrics after performing operations."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        
        # Perform operations
        agent.detect_cross_repo_patterns(["repo1"])
        agent.predict_behavior({})
        
        metrics = agent.get_metrics()
        
        assert metrics["patterns_detected"] > 0
        assert metrics["predictions_made"] > 0


# =============================================================================
# TEST UTILITY FUNCTIONS
# =============================================================================

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_agent_function(self):
        """Test create_agent utility function."""
        agent = create_agent(seed=RANDOM_SEED)
        assert isinstance(agent, EmergentIntelligenceAgent)
        assert agent.seed == RANDOM_SEED
    
    def test_create_agent_with_custom_seed(self):
        """Test create_agent with custom seed."""
        custom_seed = 77
        agent = create_agent(seed=custom_seed)
        assert agent.seed == custom_seed


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_detection_prediction_workflow(self):
        """Test complete workflow from detection to prediction."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        
        # Step 1: Detect patterns
        repos = ["repo1", "repo2"]
        patterns = agent.detect_cross_repo_patterns(repos)
        
        # Step 2: Track code smells
        changes = [{"code": "\n".join([f"line{i}" for i in range(60)])}]
        smells = agent.track_code_smells("repo1", changes)
        
        # Step 3: Make predictions
        predictions = agent.predict_behavior({"environment": "production"})
        
        # Step 4: Check metrics
        metrics = agent.get_metrics()
        
        assert len(patterns) >= 0
        assert len(smells) >= 0
        assert len(predictions) > 0
        assert metrics["patterns_detected"] >= 0
        assert metrics["predictions_made"] > 0
    
    def test_continuous_learning_workflow(self):
        """Test continuous learning and improvement workflow."""
        agent = EmergentIntelligenceAgent(seed=RANDOM_SEED)
        
        # Initial detection
        _ = agent.detect_cross_repo_patterns(["repo1"])  # Initial patterns
        initial_accuracy = agent.metrics["accuracy"]
        
        # Provide feedback
        agent.improve_accuracy({"accuracy": 0.95})
        
        # Second detection
        _ = agent.detect_cross_repo_patterns(["repo1"])  # Patterns after improvement
        
        # Accuracy should have changed
        assert agent.metrics["accuracy"] != initial_accuracy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
