"""Complete test suite for cascade delegation system.

Tests all components with mocking for CLI availability.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_integration import (
    CascadeOrchestrator,
    CLIResponse,
    ContextCompressor,
    CopilotCLIExecutor,
    DelegationTask,
    ModelType,
    SmartDelegationRouter,
    TaskType,
    TokenBudgetManager,
    cascade_task,
    delegate_sync,
    get_orchestrator,
)


class TestContextCompressor:
    """Tests for context compression."""
    
    def test_abbreviates_keys(self):
        """Test key abbreviation."""
        compressor = ContextCompressor()
        context = {
            'requirements': ['test1', 'test2'],
            'description': 'Long description here',
            'language': 'python'
        }
        result = compressor.compress(context)
        
        assert 'reqs' in result
        assert 'desc' in result
        assert 'lang' in result
        assert result['reqs'] == ['test1', 'test2']
    
    def test_compresses_long_code(self):
        """Test code compression."""
        compressor = ContextCompressor(max_code_lines=20)
        long_code = '\n'.join([f'line {i}' for i in range(100)])
        context = {'code': long_code}
        
        result = compressor.compress(context)
        
        # Should be compressed
        assert len(result['code'].split('\n')) < 50
        assert '[code truncated]' in result['code'] or '[truncated]' in result['code']
    
    def test_compresses_lists(self):
        """Test list compression."""
        compressor = ContextCompressor()
        long_list = list(range(50))
        context = {'items': long_list}
        
        result = compressor.compress(context)
        
        # Should be compressed
        assert len(result['items']) <= compressor.max_list_items + 1  # +1 for marker
    
    def test_preserves_short_content(self):
        """Test that short content is not compressed."""
        compressor = ContextCompressor()
        context = {
            'code': 'def test(): pass',
            'items': [1, 2, 3]
        }
        
        result = compressor.compress(context)
        
        assert result['code'] == 'def test(): pass'
        assert result['items'] == [1, 2, 3]


class TestCopilotCLIExecutor:
    """Tests for CLI executor."""
    
    def test_cli_verification(self):
        """Test CLI availability check."""
        executor = CopilotCLIExecutor()
        # Should not crash regardless of CLI availability
        assert isinstance(executor.cli_available, bool)
    
    @pytest.mark.asyncio
    async def test_execute_with_unavailable_cli(self):
        """Test execution when CLI is unavailable."""
        executor = CopilotCLIExecutor()
        executor.cli_available = False
        
        task = DelegationTask(
            task_id='test_task',
            task_type=TaskType.CODE_REVIEW,
            context={'code': 'def test(): pass'}
        )
        
        response = await executor.execute(task)
        
        assert response.task_id == 'test_task'
        assert response.status == 'fallback'
        assert 'fallback mode' in response.output
    
    def test_prompt_generation_review(self):
        """Test review prompt generation."""
        executor = CopilotCLIExecutor()
        context = {'code': 'def hello():\n    print("hi")', 'lang': 'python'}
        
        prompt = executor._prompt_review(context)
        
        assert 'Review' in prompt
        assert 'def hello' in prompt
        assert '```python' in prompt
    
    def test_prompt_generation_debug(self):
        """Test debug prompt generation."""
        executor = CopilotCLIExecutor()
        context = {'err': 'AttributeError: None', 'code': 'x.process()'}
        
        prompt = executor._prompt_debug(context)
        
        assert 'Debug' in prompt
        assert 'AttributeError' in prompt
        assert 'x.process()' in prompt


class TestSmartDelegationRouter:
    """Tests for smart delegation routing."""
    
    def test_routes_simple_tasks_to_mini(self):
        """Test routing of simple tasks."""
        router = SmartDelegationRouter()
        
        task = DelegationTask(
            task_id='simple',
            task_type=TaskType.DOCUMENTATION,
            context={'code': 'def test(): pass'}
        )
        
        agent, model = router.route(task)
        
        assert agent == 'cli'
        assert model == ModelType.GPT_4O_MINI
    
    def test_routes_complex_tasks_to_claude(self):
        """Test routing of complex tasks."""
        router = SmartDelegationRouter()
        
        # Create large code to trigger complexity
        large_code = '\n'.join([f'def func_{i}(): pass' for i in range(200)])
        
        task = DelegationTask(
            task_id='complex',
            task_type=TaskType.SECURITY_SCAN,
            context={'code': large_code, 'requirements': ['security']}
        )
        
        agent, model = router.route(task)
        
        # Should route to more capable model
        assert agent == 'cli'
        assert model in [ModelType.CLAUDE_SONNET, ModelType.DEFAULT]
    
    def test_routes_very_complex_to_primary(self):
        """Test routing of very complex tasks to primary agent."""
        router = SmartDelegationRouter()
        
        # Create extremely large code
        huge_code = '\n'.join([f'def func_{i}(): pass' for i in range(1000)])
        
        task = DelegationTask(
            task_id='very_complex',
            task_type=TaskType.REFACTOR,
            context={'code': huge_code, 'requirements': ['security', 'architecture']}
        )
        
        agent, model = router.route(task)
        
        # Very complex should stay with primary
        assert agent == 'primary'
    
    def test_complexity_assessment(self):
        """Test complexity scoring."""
        router = SmartDelegationRouter()
        
        simple_task = DelegationTask('t1', TaskType.TEST_GENERATION, {'code': 'x=1'})
        complex_task = DelegationTask('t2', TaskType.SECURITY_SCAN, {'code': 'x'*10000})
        
        simple_score = router._assess_complexity(simple_task)
        complex_score = router._assess_complexity(complex_task)
        
        assert simple_score < complex_score


class TestTokenBudgetManager:
    """Tests for token budget management."""
    
    def test_initial_budget(self):
        """Test initial budget state."""
        manager = TokenBudgetManager(monthly_budget=10000)
        
        status = manager.get_budget_status()
        
        assert status['total'] == 10000
        assert status['used'] == 0
        assert status['remaining'] == 10000
        assert status['utilization'] == 0.0
    
    def test_records_usage(self):
        """Test usage recording."""
        manager = TokenBudgetManager(monthly_budget=10000)
        
        manager.record_usage('task1', 500)
        manager.record_usage('task2', 300)
        
        status = manager.get_budget_status()
        
        assert status['used'] == 800
        assert status['remaining'] == 9200
        assert len(manager.usage_log) == 2
    
    def test_priority_allocation(self):
        """Test priority-based allocation."""
        manager = TokenBudgetManager(monthly_budget=10000)
        
        high_priority = DelegationTask('t1', TaskType.SECURITY_SCAN, {}, priority=1)
        low_priority = DelegationTask('t2', TaskType.DOCUMENTATION, {}, priority=3)
        
        high_alloc = manager.allocate(high_priority)
        low_alloc = manager.allocate(low_priority)
        
        assert high_alloc > low_alloc
    
    def test_allocation_respects_remaining_budget(self):
        """Test that allocation respects remaining budget."""
        manager = TokenBudgetManager(monthly_budget=1000)
        manager.record_usage('task1', 900)
        
        task = DelegationTask('t2', TaskType.CODE_REVIEW, {}, priority=1)
        allocation = manager.allocate(task)
        
        # Should allocate less than normal due to low remaining budget
        assert allocation < 4000


class TestCascadeOrchestrator:
    """Tests for cascade orchestration."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = CascadeOrchestrator()
        
        assert orchestrator.compressor is not None
        assert orchestrator.executor is not None
        assert orchestrator.router is not None
        assert orchestrator.budget_manager is not None
    
    def test_decomposes_pr_review(self):
        """Test PR review decomposition."""
        orchestrator = CascadeOrchestrator()
        
        task = {
            'id': 'pr_123',
            'type': 'full_pr_review',
            'files': [
                {'path': 'a.py', 'content': 'code1', 'language': 'python'},
                {'path': 'b.py', 'content': 'code2', 'language': 'python'},
            ]
        }
        
        subtasks = orchestrator._decompose(task)
        
        assert len(subtasks) == 2
        assert all(st.task_type == TaskType.CODE_REVIEW for st in subtasks)
    
    def test_aggregates_results(self):
        """Test result aggregation."""
        orchestrator = CascadeOrchestrator()
        
        results = [
            {
                'task_id': 'task1',
                'status': 'success',
                'output': 'Output 1',
                'error': None
            },
            {
                'task_id': 'task2',
                'status': 'success',
                'output': 'Output 2',
                'error': None
            }
        ]
        
        aggregated = orchestrator._aggregate(results)
        
        assert 'task1' in aggregated
        assert 'task2' in aggregated
        assert aggregated['task1']['status'] == 'success'
    
    def test_verification_all_success(self):
        """Test verification with all successful."""
        orchestrator = CascadeOrchestrator()
        
        results = {
            'task1': {'status': 'success', 'output': 'ok', 'error': None},
            'task2': {'status': 'success', 'output': 'ok', 'error': None}
        }
        
        verification = orchestrator._verify(results, {})
        
        assert verification['status'] == 'verified'
        assert verification['confidence'] == 1.0
        assert verification['successful'] == 2
    
    def test_verification_partial_success(self):
        """Test verification with partial success."""
        orchestrator = CascadeOrchestrator()
        
        results = {
            'task1': {'status': 'success', 'output': 'ok', 'error': None},
            'task2': {'status': 'failed', 'output': '', 'error': 'Error'},
            'task3': {'status': 'success', 'output': 'ok', 'error': None}
        }
        
        verification = orchestrator._verify(results, {})
        
        assert verification['status'] == 'partial'
        assert verification['confidence'] == 2/3
        assert len(verification['recommendations']) > 0
    
    @pytest.mark.asyncio
    async def test_cascade_full_flow(self):
        """Test complete cascade flow."""
        orchestrator = CascadeOrchestrator()
        
        task = {
            'id': 'test_cascade',
            'type': 'generic',
            'context': {'prompt': 'Test prompt'}
        }
        
        results = await orchestrator.cascade(task)
        
        assert 'task_id' in results
        assert 'subtasks' in results
        assert 'verification' in results
        assert 'total_tokens' in results
        assert 'budget_status' in results


class TestPublicAPI:
    """Tests for public API functions."""
    
    def test_get_orchestrator_singleton(self):
        """Test singleton pattern."""
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        
        assert orch1 is orch2
    
    @pytest.mark.asyncio
    async def test_cascade_task_async(self):
        """Test async cascade task."""
        task = {
            'id': 'api_test',
            'type': 'generic',
            'context': {'prompt': 'Test'}
        }
        
        results = await cascade_task(task)
        
        assert results is not None
        assert 'task_id' in results
    
    def test_delegate_sync(self):
        """Test synchronous delegation."""
        task = {
            'id': 'sync_test',
            'type': 'generic',
            'context': {'prompt': 'Test'}
        }
        
        results = delegate_sync(task)
        
        assert results is not None
        assert 'task_id' in results


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_pr_review_flow(self):
        """Test complete PR review flow."""
        orchestrator = CascadeOrchestrator()
        
        task = {
            'id': 'pr_456',
            'type': 'full_pr_review',
            'files': [
                {
                    'path': 'example.py',
                    'content': 'def hello():\n    print("world")',
                    'language': 'python'
                }
            ],
            'requirements': ['Check code quality', 'Review best practices']
        }
        
        results = await orchestrator.cascade(task)
        
        # Verify structure
        assert results['task_id'] == 'pr_456'
        assert len(results['subtasks']) > 0
        assert 'verification' in results
        assert results['verification']['total_subtasks'] > 0
        
        # Verify budget tracking
        assert 'budget_status' in results
        assert results['budget_status']['used'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
