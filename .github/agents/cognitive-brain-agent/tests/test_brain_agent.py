"""
Tests for Cognitive Brain Agent.

Comprehensive test suite for the brain processor, PDA engine,
aftermath handler, and learning integrator.
"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.pda_engine import (
    PDAEngine,
    PerceptionResult,
    DecisionResult,
    ActionResult,
    AfterMathResult,
)
from agent.aftermath_handler import (
    AfterMathHandler,
    PatternCandidate,
    LearningUpdate,
)
from agent.brain_processor import (
    CognitiveBrainProcessor,
    TaskContext,
    ProcessingResult,
)
from agent.learning_integrator import (
    LearningIntegrator,
    LearningConfig,
    LearningMetrics,
)


class TestPDAEngine:
    """Tests for PDA Engine."""

    def test_create_engine(self):
        """Test creating PDA engine."""
        engine = PDAEngine()
        assert engine._perceiver is None
        assert engine._decider is None
        assert engine._actor is None

    def test_register_perceiver(self):
        """Test registering perceiver."""
        engine = PDAEngine()
        
        @engine.perceiver
        def my_perceiver(input_data):
            return PerceptionResult(features={'key': input_data})
        
        assert engine._perceiver is not None

    def test_register_decider(self):
        """Test registering decider."""
        engine = PDAEngine()
        
        @engine.decider
        def my_decider(perception):
            return DecisionResult(action='test')
        
        assert engine._decider is not None

    def test_register_actor(self):
        """Test registering actor."""
        engine = PDAEngine()
        
        @engine.actor
        def my_actor(decision, context):
            return ActionResult(success=True)
        
        assert engine._actor is not None

    def test_run_full_loop(self):
        """Test running full PDA loop."""
        engine = PDAEngine()
        
        @engine.perceiver
        def perceive(data):
            return PerceptionResult(features={'input': data})
        
        @engine.decider
        def decide(perception):
            return DecisionResult(action='process')
        
        @engine.actor
        def act(decision, ctx):
            return ActionResult(success=True, output='done')
        
        result = engine.run("test_input")
        
        assert result['success'] is True
        assert 'perceive' in result['phases']
        assert 'decide' in result['phases']
        assert 'act' in result['phases']

    def test_run_with_aftermath(self):
        """Test running with aftermath handler."""
        engine = PDAEngine()
        
        @engine.perceiver
        def perceive(data):
            return PerceptionResult()
        
        @engine.decider
        def decide(perception):
            return DecisionResult(action='test')
        
        @engine.actor
        def act(decision, ctx):
            return ActionResult(success=True)
        
        @engine.aftermath
        def aftermath(perception, decision, action):
            return AfterMathResult(reward=1.0, learning_updates=1)
        
        result = engine.run("input")
        
        assert 'aftermath' in result['phases']
        assert result['phases']['aftermath'].reward == 1.0

    def test_get_statistics(self):
        """Test getting statistics."""
        engine = PDAEngine()
        
        @engine.perceiver
        def p(d): return PerceptionResult()
        @engine.decider
        def d(p): return DecisionResult(action='x')
        @engine.actor
        def a(d, c): return ActionResult(success=True)
        
        for _ in range(5):
            engine.run("input")
        
        stats = engine.get_statistics()
        assert stats['runs'] == 5
        assert stats['success_rate'] == 1.0


class TestAfterMathHandler:
    """Tests for AfterMath Handler."""

    def test_create_handler(self):
        """Test creating handler."""
        handler = AfterMathHandler()
        assert handler.reward_weights['success'] == 1.0

    def test_process_success(self):
        """Test processing successful action."""
        handler = AfterMathHandler()
        
        result = handler.process(
            action='approve',
            success=True,
            context={'task_type': 'review'},
            output={'approved': True},
        )
        
        assert result['reward'] > 0
        assert len(result['patterns']) > 0

    def test_process_failure(self):
        """Test processing failed action."""
        handler = AfterMathHandler()
        
        result = handler.process(
            action='approve',
            success=False,
            context={'task_type': 'review'},
            output={'error': 'validation failed'},
        )
        
        assert result['reward'] < handler.reward_weights['success']

    def test_pattern_extraction(self):
        """Test pattern extraction."""
        handler = AfterMathHandler()
        
        handler.process(
            action='analyze',
            success=True,
            context={'task_type': 'code_review'},
            output={},
        )
        
        assert len(handler.patterns_extracted) > 0
        assert handler.patterns_extracted[0].pattern_type == 'success'

    def test_custom_extraction_rule(self):
        """Test custom extraction rule."""
        handler = AfterMathHandler()
        
        def custom_rule(action, success, context, output):
            if action == 'special':
                return PatternCandidate(
                    name='special_pattern',
                    pattern_type='custom',
                    confidence=0.9,
                )
            return None
        
        handler.register_extraction_rule(custom_rule)
        
        result = handler.process(
            action='special',
            success=True,
            context={},
            output={},
        )
        
        assert 'special_pattern' in result['patterns']

    def test_get_statistics(self):
        """Test getting statistics."""
        handler = AfterMathHandler()
        
        for i in range(5):
            handler.process(
                action='test',
                success=i % 2 == 0,
                context={},
                output={},
            )
        
        stats = handler.get_statistics()
        assert stats['patterns_extracted'] == 5
        assert 0 <= stats['success_rate'] <= 1


class TestCognitiveBrainProcessor:
    """Tests for Cognitive Brain Processor."""

    def test_create_processor(self):
        """Test creating processor."""
        processor = CognitiveBrainProcessor()
        assert processor.learning_enabled is True

    def test_register_action_handler(self):
        """Test registering action handler."""
        processor = CognitiveBrainProcessor()
        
        def handler(context):
            return {'handled': True}
        
        processor.register_action_handler('custom', handler)
        assert 'custom' in processor.action_handlers

    def test_process_task(self):
        """Test processing a task."""
        processor = CognitiveBrainProcessor(learning_enabled=False)
        
        context = TaskContext(
            task_id='test-001',
            task_type='review',
            input_data={'file': 'test.py'},
        )
        
        result = processor.process(context)
        
        assert result.task_id == 'test-001'
        assert result.success is True

    def test_process_with_handler(self):
        """Test processing with custom handler."""
        processor = CognitiveBrainProcessor(learning_enabled=False)
        
        def approve_handler(ctx):
            return {'approved': True, 'file': ctx.input_data.get('file')}
        
        processor.register_action_handler('approve', approve_handler)
        
        context = TaskContext(
            task_id='test-002',
            task_type='review',
            input_data={'file': 'example.py'},
        )
        
        result = processor.process(context)
        assert result.success is True

    def test_get_statistics(self):
        """Test getting statistics."""
        processor = CognitiveBrainProcessor(learning_enabled=False)
        
        for i in range(3):
            processor.process(TaskContext(
                task_id=f'task-{i}',
                task_type='test',
                input_data={},
            ))
        
        stats = processor.get_statistics()
        assert stats['total_tasks'] == 3
        assert stats['success_rate'] == 1.0


class TestLearningIntegrator:
    """Tests for Learning Integrator."""

    def test_create_integrator(self):
        """Test creating integrator."""
        integrator = LearningIntegrator()
        assert integrator.initialized is False

    def test_initialize(self):
        """Test initialization."""
        integrator = LearningIntegrator()
        integrator.initialize()
        # May or may not initialize depending on imports
        assert isinstance(integrator.actions, list)

    def test_custom_config(self):
        """Test custom configuration."""
        config = LearningConfig(
            learning_rate=0.2,
            epsilon=0.05,
            target_k1=0.30,
        )
        integrator = LearningIntegrator(config=config)
        
        assert integrator.config.learning_rate == 0.2
        assert integrator.config.epsilon == 0.05
        assert integrator.config.target_k1 == 0.30

    def test_select_action_uninitialized(self):
        """Test action selection when not initialized."""
        integrator = LearningIntegrator()
        integrator.actions = ['action1', 'action2']
        
        action = integrator.select_action({'feature': 1.0})
        assert action == 'action1'  # Default to first action

    def test_process_outcome(self):
        """Test processing outcome."""
        integrator = LearningIntegrator()
        integrator.actions = ['approve']
        
        reward = integrator.process_outcome(
            state={'f': 1},
            action='approve',
            success=True,
        )
        
        assert reward > 0

    def test_get_metrics(self):
        """Test getting metrics."""
        integrator = LearningIntegrator()
        
        metrics = integrator.get_metrics()
        assert isinstance(metrics, LearningMetrics)
        assert metrics.episodes == 0


class TestIntegration:
    """Integration tests for Cognitive Brain Agent."""

    def test_full_processing_flow(self):
        """Test full processing flow."""
        # Create processor
        processor = CognitiveBrainProcessor(learning_enabled=False)
        
        # Register handlers
        processor.register_action_handler('approve', lambda ctx: {'approved': True})
        processor.register_action_handler('reject', lambda ctx: {'rejected': True})
        
        # Process multiple tasks
        results = []
        for i in range(5):
            context = TaskContext(
                task_id=f'task-{i}',
                task_type='review',
                input_data={'complexity': i},
            )
            results.append(processor.process(context))
        
        assert len(results) == 5
        assert all(r.success for r in results)

    def test_pda_with_aftermath(self):
        """Test PDA engine with aftermath processing."""
        engine = PDAEngine()
        handler = AfterMathHandler()
        
        @engine.perceiver
        def perceive(data):
            return PerceptionResult(features={'data': data})
        
        @engine.decider
        def decide(perception):
            return DecisionResult(action='process')
        
        @engine.actor
        def act(decision, ctx):
            return ActionResult(success=True, output={'processed': True})
        
        @engine.aftermath
        def aftermath_phase(perception, decision, action):
            result = handler.process(
                action=decision.action,
                success=action.success,
                context={},
                output=action.output,
            )
            return AfterMathResult(
                reward=result['reward'],
                patterns_extracted=result['patterns'],
            )
        
        result = engine.run({'input': 'test'})
        
        assert result['success']
        assert result['phases']['aftermath'].reward > 0
