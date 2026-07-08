"""Tests for Meta-Cognitive Reflection Layer.

Tests the meta-cognitive reflection capabilities including:
- Reflection creation and storage
- Strategy pattern identification
- Meta-knowledge management
- Self-assessment report generation
"""

import pytest


class TestReflectionType:
    """Tests for ReflectionType enum."""

    def test_reflection_types_exist(self):
        """Test that all reflection types are defined."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import ReflectionType

            assert hasattr(ReflectionType, "DECISION")
            assert hasattr(ReflectionType, "STRATEGY")
            assert hasattr(ReflectionType, "OUTCOME")
            assert hasattr(ReflectionType, "PATTERN")
            assert hasattr(ReflectionType, "ERROR")
            assert hasattr(ReflectionType, "SUCCESS")
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflection_type_values(self):
        """Test reflection type string values."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import ReflectionType

            assert ReflectionType.DECISION.value == "decision", "Value must be initialized"
            assert ReflectionType.ERROR.value == "error", "Value must be initialized"
            assert ReflectionType.SUCCESS.value == "success", "Value must be initialized"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")


class TestQualityAssessment:
    """Tests for QualityAssessment enum."""

    def test_quality_assessments_exist(self):
        """Test that all quality assessments are defined."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import QualityAssessment

            assert hasattr(QualityAssessment, "EXCELLENT")
            assert hasattr(QualityAssessment, "GOOD")
            assert hasattr(QualityAssessment, "ADEQUATE")
            assert hasattr(QualityAssessment, "POOR")
            assert hasattr(QualityAssessment, "FAILED")
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_quality_values(self):
        """Test quality assessment string values."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import QualityAssessment

            assert QualityAssessment.EXCELLENT.value == "excellent", "Value must be initialized"
            assert QualityAssessment.FAILED.value == "failed", "Value must be initialized"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")


class TestReflection:
    """Tests for Reflection dataclass."""

    def test_reflection_creation(self):
        """Test creating a Reflection instance."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                QualityAssessment,
                Reflection,
                ReflectionType,
            )

            reflection = Reflection(
                reflection_id="test_001",
                reflection_type=ReflectionType.DECISION,
                subject="Code review approach",
                observation="Used line-by-line review",
                analysis="Effective for catching bugs",
                learning="Continue this approach",
                quality=QualityAssessment.GOOD,
            )

            assert reflection.reflection_id == "test_001", "reflection_id is not valid"
            assert reflection.subject == "Code review approach", "subject is not valid"
            assert reflection.quality == QualityAssessment.GOOD, "quality is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflection_str(self):
        """Test Reflection string representation."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                QualityAssessment,
                Reflection,
                ReflectionType,
            )

            reflection = Reflection(
                reflection_id="test_002",
                reflection_type=ReflectionType.ERROR,
                subject="Error handling",
                observation="Missed edge case",
                analysis="Need better testing",
                learning="Add more test cases",
                quality=QualityAssessment.POOR,
            )

            string_repr = str(reflection)
            assert "Error handling" in string_repr, "Error should be raised or set"
            assert "poor" in string_repr.lower(), "Condition must be true"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")


class TestStrategyPattern:
    """Tests for StrategyPattern dataclass."""

    def test_pattern_creation(self):
        """Test creating a StrategyPattern."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import StrategyPattern

            pattern = StrategyPattern(
                pattern_id="pattern_001",
                condition="When debugging",
                behavior="Use logging first",
                effectiveness=0.85,
            )

            assert pattern.pattern_id == "pattern_001", "pattern_id is not valid"
            assert pattern.effectiveness == 0.85, "effectiveness is not valid"
            assert pattern.occurrences == 0, "occurrences is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")


class TestMetaKnowledge:
    """Tests for MetaKnowledge dataclass."""

    def test_meta_knowledge_creation(self):
        """Test creating MetaKnowledge."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import MetaKnowledge

            knowledge = MetaKnowledge(
                domain="Python",
                strength_assessment=0.9,
                confidence=0.8,
                evidence=["Completed 100+ Python PRs"],
            )

            assert knowledge.domain == "Python", "domain is not valid"
            assert knowledge.strength_assessment == 0.9, "strength_assessment is not valid"
            assert len(knowledge.evidence) == 1, "Collection must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")


class TestMetaCognitiveReflectionLayer:
    """Tests for MetaCognitiveReflectionLayer class."""

    def test_layer_initialization(self):
        """Test layer initialization."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-1")

            assert layer.agent_id == "test-agent-1", "agent_id is not valid"
            assert len(layer.reflections) == 0, "Collection must not be empty"
            assert len(layer.strategy_patterns) == 0, "Collection must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflect_method(self):
        """Test creating reflections."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-2")

            reflection = layer.reflect(
                reflection_type=ReflectionType.DECISION,
                subject="API Design",
                observation="Used REST pattern",
                analysis="Works well for CRUD",
                learning="Consider GraphQL for complex queries",
                quality=QualityAssessment.GOOD,
            )

            assert len(layer.reflections) == 1, "Collection must not be empty"
            assert reflection.subject == "API Design", "subject is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflect_on_decision(self):
        """Test reflect_on_decision convenience method."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-3")

            reflection = layer.reflect_on_decision(
                subject="Test strategy",
                observation="Used TDD",
                analysis="Found bugs early",
                learning="Continue TDD practice",
                quality=QualityAssessment.EXCELLENT,
            )

            assert reflection.reflection_type == ReflectionType.DECISION, "reflection_type is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflect_on_error(self):
        """Test reflect_on_error convenience method."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-4")

            reflection = layer.reflect_on_error(
                subject="Production bug",
                observation="Missed validation",
                analysis="Input not sanitized",
                learning="Add input validation",
                quality=QualityAssessment.POOR,
            )

            assert reflection.reflection_type == ReflectionType.ERROR, "Error should be raised or set"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_reflect_on_success(self):
        """Test reflect_on_success convenience method."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-5")

            reflection = layer.reflect_on_success(
                subject="Feature launch",
                observation="Zero downtime",
                analysis="Good preparation",
                learning="Keep same approach",
                quality=QualityAssessment.EXCELLENT,
            )

            assert reflection.reflection_type == ReflectionType.SUCCESS, "reflection_type is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_record_strategy_pattern_new(self):
        """Test recording a new strategy pattern."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-6")

            pattern = layer.record_strategy_pattern(
                pattern_id="debug_pattern",
                condition="When debugging",
                behavior="Add logging first",
                effectiveness=0.9,
            )

            assert pattern.pattern_id == "debug_pattern", "pattern_id is not valid"
            assert pattern.occurrences == 1, "occurrences is not valid"
            assert len(layer.strategy_patterns) == 1, "Collection must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_record_strategy_pattern_update(self):
        """Test updating an existing strategy pattern."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-7")

            # Record first time
            layer.record_strategy_pattern(
                pattern_id="test_pattern",
                condition="When testing",
                behavior="Write test first",
                effectiveness=0.8,
            )

            # Record second time
            pattern = layer.record_strategy_pattern(
                pattern_id="test_pattern",
                condition="When testing",
                behavior="Write test first",
                effectiveness=1.0,
            )

            assert pattern.occurrences == 2, "occurrences is not valid"
            # Weighted average: 0.8 * 0.7 + 1.0 * 0.3 = 0.86
            assert 0.85 <= pattern.effectiveness <= 0.87, "85 is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_identify_strategy_patterns(self):
        """Test pattern identification from reflections."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-8")

            # Add multiple reflections on same subject
            layer.reflect(
                ReflectionType.DECISION,
                subject="Code review",
                observation="Review 1",
                analysis="Analysis 1",
                learning="Learning 1",
                quality=QualityAssessment.GOOD,
            )

            layer.reflect(
                ReflectionType.DECISION,
                subject="Code review",
                observation="Review 2",
                analysis="Analysis 2",
                learning="Learning 2",
                quality=QualityAssessment.EXCELLENT,
            )

            patterns = layer.identify_strategy_patterns()

            assert len(patterns) >= 1, "Patterns must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_update_meta_knowledge_new(self):
        """Test updating meta-knowledge for a new domain."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-9")

            knowledge = layer.update_meta_knowledge(
                domain="Python",
                strength_assessment=0.85,
                confidence=0.9,
                evidence=["Completed Python certification"],
            )

            assert knowledge.domain == "Python", "domain is not valid"
            assert knowledge.strength_assessment == 0.85, "strength_assessment is not valid"
            assert len(layer.meta_knowledge) == 1, "Collection must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_update_meta_knowledge_existing(self):
        """Test updating existing meta-knowledge."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-10")

            # First update
            layer.update_meta_knowledge(
                domain="JavaScript",
                strength_assessment=0.6,
                confidence=0.7,
            )

            # Second update
            knowledge = layer.update_meta_knowledge(
                domain="JavaScript",
                strength_assessment=0.9,
                confidence=0.8,
                evidence=["Completed JS project"],
            )

            # Weighted average: 0.6 * 0.7 + 0.9 * 0.3 = 0.69
            assert 0.68 <= knowledge.strength_assessment <= 0.70, "68 is not valid"
            assert len(knowledge.evidence) == 1, "Collection must not be empty"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_get_strengths(self):
        """Test getting strength domains."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-11")

            layer.update_meta_knowledge("Strong Domain", 0.9, 0.8)
            layer.update_meta_knowledge("Weak Domain", 0.3, 0.8)

            strengths = layer.get_strengths(threshold=0.7)

            assert len(strengths) == 1, "Strengths must not be empty"
            assert strengths[0].domain == "Strong Domain", "domain is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_get_weaknesses(self):
        """Test getting weakness domains."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-12")

            layer.update_meta_knowledge("Strong Domain", 0.9, 0.8)
            layer.update_meta_knowledge("Weak Domain", 0.3, 0.8)

            weaknesses = layer.get_weaknesses(threshold=0.5)

            assert len(weaknesses) == 1, "Weaknesses must not be empty"
            assert weaknesses[0].domain == "Weak Domain", "domain is not valid"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_generate_self_assessment_report(self):
        """Test report generation."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-13")

            # Add some data
            layer.reflect(
                ReflectionType.SUCCESS,
                subject="Test task",
                observation="Completed",
                analysis="Went well",
                learning="Keep it up",
                quality=QualityAssessment.GOOD,
            )
            layer.update_meta_knowledge("Python", 0.9, 0.95)
            layer.update_meta_knowledge("Rust", 0.3, 0.6)

            report = layer.generate_self_assessment_report()

            assert "test-agent-13" in report, "Condition must be true"
            assert "STRENGTHS" in report, "Condition must be true"
            assert "AREAS FOR IMPROVEMENT" in report, "Condition must be true"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")

    def test_get_stats(self):
        """Test getting statistics."""
        try:
            from src.cognitive_brain.meta_cognitive_reflection import (
                MetaCognitiveReflectionLayer,
                QualityAssessment,
                ReflectionType,
            )

            layer = MetaCognitiveReflectionLayer("test-agent-14")

            layer.reflect(
                ReflectionType.DECISION,
                subject="Test",
                observation="Obs",
                analysis="Ana",
                learning="Learn",
                quality=QualityAssessment.GOOD,
            )

            stats = layer.get_stats()

            assert stats["agent_id"] == "test-agent-14", "Condition must be true"
            assert stats["total_reflections"] == 1, "Condition must be true"
            assert "good" in stats["reflections_by_quality"], "Condition must be true"
        except ImportError:
            pytest.skip("meta_cognitive_reflection module not available")
