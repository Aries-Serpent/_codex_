#!/usr/bin/env python3
"""
Test Meta Learning

Purpose:
    Test script for meta_learning

Usage:
    python scripts/cognitive/tests/test_meta_learning.py [options]

    Examples:
    $ python scripts/cognitive/tests/test_meta_learning.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Assume meta_learning_engine exists
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from meta_learning_engine import (  # noqa: E402
        MetaLearningEngine,
        Pattern,
        SharedMemory,
    )
except ImportError:
    MetaLearningEngine = None
    Pattern = None
    SharedMemory = None


class TestMetaLearningEngine:
    """Test meta-learning engine functionality"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def engine(self, temp_dir):
        if MetaLearningEngine is None:
            pytest.skip("MetaLearningEngine not available")
        return MetaLearningEngine(memory_dir=temp_dir)

    def test_engine_initialization(self, engine):
        """Test meta-learning engine initializes correctly"""
        assert engine is not None
        assert hasattr(engine, 'shared_memory')
        assert hasattr(engine, 'pattern_library')

    def test_pattern_storage(self, engine):
        """Test storing patterns in pattern library"""
        pattern = {
            'name': 'test_pattern',
            'type': 'success',
            'context': 'test_context',
            'effectiveness': 0.85,
            'usage_count': 1
        }

        result = engine.store_pattern(pattern)
        assert result is True

        # Verify retrieval
        retrieved = engine.get_pattern('test_pattern')
        assert retrieved is not None
        assert retrieved['effectiveness'] == 0.85

    def test_pattern_similarity_detection(self, engine):
        """Test finding similar patterns"""
        # Store multiple patterns
        patterns = [
            {'name': 'p1', 'type': 'success', 'context': 'code_review', 'effectiveness': 0.9},
            {'name': 'p2', 'type': 'success', 'context': 'code_refactor', 'effectiveness': 0.8},
            {'name': 'p3', 'type': 'failure', 'context': 'deployment', 'effectiveness': 0.3}
        ]

        for p in patterns:
            engine.store_pattern(p)

        # Find similar to p1
        similar = engine.find_similar_patterns('p1', min_similarity=0.5)
        assert len(similar) >= 1
        assert any(p['name'] == 'p2' for p in similar)

    def test_knowledge_transfer(self, engine):
        """Test knowledge transfer between agents"""
        source_agent = 'agent_1'
        target_agents = ['agent_2', 'agent_3']

        # Store knowledge from source
        knowledge = {
            'pattern': 'optimization_pattern',
            'learned_at': '2026-01-04',
            'confidence': 0.92
        }

        engine.store_knowledge(source_agent, knowledge)

        # Transfer to targets
        result = engine.transfer_knowledge(source_agent, target_agents)
        assert result['success'] is True
        assert len(result['transferred_to']) == 2


class TestSharedMemory:
    """Test shared memory architecture"""

    @pytest.fixture
    def memory(self, tmp_path):
        if SharedMemory is None:
            pytest.skip("SharedMemory not available")
        return SharedMemory(storage_path=tmp_path / "memory.json")

    def test_memory_read_write(self, memory):
        """Test reading and writing to shared memory"""
        key = 'test_key'
        value = {'data': 'test_value', 'timestamp': '2026-01-04'}

        memory.write(key, value)
        retrieved = memory.read(key)

        assert retrieved == value

    def test_memory_persistence(self, tmp_path):
        """Test memory persists across instances"""
        if SharedMemory is None:
            pytest.skip("SharedMemory not available")

        storage_path = tmp_path / "memory.json"

        # First instance
        memory1 = SharedMemory(storage_path=storage_path)
        memory1.write('persist_key', {'value': 123})

        # Second instance
        memory2 = SharedMemory(storage_path=storage_path)
        retrieved = memory2.read('persist_key')

        assert retrieved['value'] == 123

    def test_memory_concurrent_access(self, memory):
        """Test concurrent memory access handling"""
        # Simulate concurrent writes
        keys = [f'key_{i}' for i in range(10)]
        values = [{'value': i} for i in range(10)]

        for k, v in zip(keys, values):
            memory.write(k, v)

        # Verify all written
        for k, v in zip(keys, values):
            assert memory.read(k) == v


class TestPatternLibrary:
    """Test pattern library functionality"""

    def test_pattern_effectiveness_tracking(self):
        """Test tracking pattern effectiveness over time"""
        if Pattern is None:
            pytest.skip("Pattern class not available")

        pattern = Pattern(
            name='test_effectiveness',
            type='optimization',
            initial_effectiveness=0.75
        )

        # Simulate usage with outcomes
        pattern.record_usage(success=True)
        pattern.record_usage(success=True)
        pattern.record_usage(success=False)

        # Effectiveness should update based on outcomes
        assert pattern.effectiveness != 0.75
        assert pattern.usage_count == 3

    def test_pattern_expiry(self):
        """Test pattern expiry based on age or low effectiveness"""
        if Pattern is None:
            pytest.skip("Pattern class not available")

        old_pattern = Pattern(
            name='old_pattern',
            type='optimization',
            created_at='2024-01-01',
            effectiveness=0.3
        )

        # Check if pattern should be archived/removed
        assert old_pattern.should_expire(threshold=0.5, max_age_days=365)


class TestExternalIngestion:
    """Test external repository ingestion"""

    @pytest.fixture
    def engine(self, tmp_path):
        if MetaLearningEngine is None:
            pytest.skip("MetaLearningEngine not available")
        return MetaLearningEngine(memory_dir=tmp_path)

    def test_capability_detection(self, engine):
        """Test detecting capabilities from external code"""
        mock_code = """
        def screen_capture():
            pass

        def image_processing():
            pass

        def file_io():
            pass
        """

        capabilities = engine.detect_capabilities(mock_code)
        assert len(capabilities) >= 2
        assert any('screen_capture' in c for c in capabilities)

    def test_integration_strategy_generation(self, engine):
        """Test generating integration strategies"""
        capabilities = ['screen_capture', 'gif_encoding', 'image_processing']

        strategy = engine.generate_integration_strategy(
            capabilities=capabilities,
            language='C++',
            target_language='Python'
        )

        assert strategy is not None
        assert 'conversion_method' in strategy
        assert 'adapter_pattern' in strategy

    def test_lesson_extraction(self, engine):
        """Test extracting lessons from integration"""
        integration_result = {
            'success': True,
            'method': 'ctypes_wrapper',
            'challenges': ['memory_management', 'type_conversion'],
            'time_spent': 240
        }

        lessons = engine.extract_lessons(integration_result)
        assert len(lessons) > 0
        assert all('title' in line_item and 'description' in line_item for line_item in lessons)


# Integration tests
class TestMetaLearningIntegration:
    """Test end-to-end meta-learning workflows"""

    def test_full_learning_cycle(self, tmp_path):
        """Test complete learning cycle: store, retrieve, apply, improve"""
        if MetaLearningEngine is None:
            pytest.skip("MetaLearningEngine not available")

        engine = MetaLearningEngine(memory_dir=tmp_path)

        # 1. Store initial pattern
        pattern = {
            'name': 'code_review_pattern',
            'type': 'success',
            'context': 'pull_request_review',
            'actions': ['check_tests', 'verify_docs', 'review_security'],
            'effectiveness': 0.80
        }
        engine.store_pattern(pattern)

        # 2. Apply pattern and record outcome
        outcome = {'success': True, 'time_saved': 15}
        engine.record_pattern_outcome('code_review_pattern', outcome)

        # 3. Retrieve updated pattern
        updated = engine.get_pattern('code_review_pattern')
        assert updated['usage_count'] >= 1

        # 4. Transfer to other agents
        result = engine.transfer_knowledge('agent_1', ['agent_2'])
        assert result['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
