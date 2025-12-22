"""Complete test suite for cascade delegation system.

Tests all components with mocking for CLI availability.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_integration import (
    CascadeOrchestrator,
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


class TestIntegrationPRFlow:
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


# ============================================================================
# Enhanced Module Tests
# ============================================================================

class TestMCPIntegration:
    """Tests for MCP server integration."""
    
    def test_mock_mode_initialization(self):
        """Test MCP integration in mock mode."""
        from mcp_server import MCPIntegration, MCPConnectionMode
        
        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        assert mcp.mode == MCPConnectionMode.MOCK
        assert len(mcp.servers) >= 2  # At least github and codex_physics
    
    @pytest.mark.asyncio
    async def test_mock_connection(self):
        """Test mock MCP connection."""
        from mcp_server import MCPIntegration, MCPConnectionMode
        
        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        connected = await mcp.connect('github')
        assert connected is True
        assert 'github' in mcp.active_connections
    
    @pytest.mark.asyncio
    async def test_mock_execution(self):
        """Test mock MCP execution."""
        from mcp_server import MCPIntegration, MCPRequest, MCPConnectionMode
        
        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        
        request = MCPRequest(
            server_name='github',
            capability='repository_access',
            payload={'repo': 'test/repo'}
        )
        
        response = await mcp.execute(request)
        assert response.status == 'success'
        assert response.data is not None
        assert 'repository' in response.data
    
    def test_capability_listing(self):
        """Test getting available capabilities."""
        from mcp_server import MCPIntegration, MCPConnectionMode
        
        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        capabilities = mcp.get_available_capabilities()
        
        assert 'github' in capabilities
        assert 'repository_access' in capabilities['github']
    
    def test_statistics(self):
        """Test MCP statistics."""
        from mcp_server import MCPIntegration, MCPConnectionMode
        
        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        stats = mcp.get_statistics()
        
        assert 'mode' in stats
        assert 'registered_servers' in stats
        assert stats['mode'] == 'mock'


class TestQuantumOptimizer:
    """Tests for quantum-inspired optimization."""
    
    def test_superposition_creation(self):
        """Test creating task superposition."""
        from quantum_optimizer import QuantumOptimizer, get_quantum_optimizer
        
        optimizer = get_quantum_optimizer()
        
        # Create mock tasks
        tasks = [
            type('Task', (), {'task_id': 't1', 'task_type': 'documentation', 'context': {'code': 'x' * 100}})(),
            type('Task', (), {'task_id': 't2', 'task_type': 'security_scan', 'context': {'code': 'y' * 500}})(),
            type('Task', (), {'task_id': 't3', 'task_type': 'test', 'context': {'code': 'z' * 50}})(),
        ]
        
        superposition = optimizer.create_superposition(tasks)
        
        assert len(superposition) == 3
        assert all(isinstance(item, tuple) for item in superposition)
        assert all(len(item) == 2 for item in superposition)
        
        # Check probabilities sum to ~1.0
        total_prob = sum(prob for _, prob in superposition)
        assert abs(total_prob - 1.0) < 0.01
    
    def test_entanglement_detection(self):
        """Test detecting task entanglement."""
        from quantum_optimizer import QuantumOptimizer
        
        optimizer = QuantumOptimizer()
        
        # Create entangled tasks (shared context)
        task1 = type('Task', (), {
            'task_id': 't1',
            'context': {'file': 'main.py', 'function': 'process', 'language': 'python'}
        })()
        
        task2 = type('Task', (), {
            'task_id': 't2',
            'context': {'file': 'main.py', 'function': 'handle', 'language': 'python'}
        })()
        
        entanglement = optimizer.detect_entanglement(task1, task2)
        
        # Should detect strong entanglement (3 shared keys)
        assert entanglement > 0.5
    
    def test_quantum_tunneling(self):
        """Test quantum tunneling through barriers."""
        from quantum_optimizer import QuantumOptimizer
        
        optimizer = QuantumOptimizer()
        
        # Create blocked task with low barrier
        blocked_task = type('Task', (), {
            'task_id': 'blocked',
            'task_type': 'test',
            'context': {'code': 'test'},
            'priority': 1
        })()
        
        # Try tunneling (may or may not succeed due to probability)
        tunneled = optimizer.quantum_tunnel(blocked_task)
        
        # If it succeeded, check properties
        if tunneled is not None:
            assert hasattr(tunneled, 'tunneled')
            assert tunneled.tunneled is True
    
    def test_chaos_exploration(self):
        """Test chaotic exploration."""
        from quantum_optimizer import QuantumOptimizer
        
        optimizer = QuantumOptimizer()
        
        state = {'param': 1.0, 'value': 0.5}
        perturbed = optimizer.apply_chaos_exploration(state)
        
        assert 'exploration_factor' in perturbed
        assert perturbed['param'] == 1.0  # Original preserved
    
    def test_statistics(self):
        """Test quantum optimizer statistics."""
        from quantum_optimizer import QuantumOptimizer
        
        optimizer = QuantumOptimizer()
        stats = optimizer.get_statistics()
        
        assert 'superposition_threshold' in stats
        assert 'entangled_pairs' in stats
        assert 'physics_integration' in stats


class TestCascadeMonitoring:
    """Tests for cascade performance monitoring."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            assert monitor.metrics.total_cascades == 0
    
    def test_record_cascade(self):
        """Test recording cascade results."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            
            results = {
                'task_id': 'test_123',
                'total_tokens': 1500,
                'total_time': 2.5,
                'subtasks': [
                    {'model': 'gpt-4o-mini', 'status': 'success'},
                    {'model': 'claude-3-5-sonnet-20241022', 'status': 'success'}
                ],
                'verification': {
                    'status': 'verified',
                    'confidence': 0.92
                }
            }
            
            monitor.record_cascade(results)
            
            assert monitor.metrics.total_cascades == 1
            assert monitor.metrics.successful_cascades == 1
            assert monitor.metrics.total_tokens == 1500
    
    def test_dashboard_data(self):
        """Test getting dashboard data."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            
            # Record some cascades
            for i in range(5):
                results = {
                    'task_id': f'test_{i}',
                    'total_tokens': 1000 + i * 100,
                    'total_time': 1.0 + i * 0.5,
                    'subtasks': [{'model': 'gpt-4o-mini', 'status': 'success'}],
                    'verification': {'status': 'verified', 'confidence': 0.9}
                }
                monitor.record_cascade(results)
            
            dashboard = monitor.get_dashboard_data()
            
            assert 'summary' in dashboard
            assert dashboard['summary']['total_cascades'] == 5
            assert dashboard['summary']['success_rate'] == 100.0
    
    def test_error_classification(self):
        """Test error type classification."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            
            assert monitor._classify_error("Connection timeout") == 'timeout'
            assert monitor._classify_error("Auth failed") == 'authentication'
            assert monitor._classify_error("File not found") == 'not_found'
            assert monitor._classify_error("Rate limit exceeded") == 'rate_limit'
    
    def test_statistics_export(self):
        """Test exporting detailed statistics."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            
            # Add some data
            for i in range(10):
                results = {
                    'task_id': f'test_{i}',
                    'total_tokens': 1000,
                    'total_time': 1.5,
                    'subtasks': [],
                    'verification': {'status': 'verified'}
                }
                monitor.record_cascade(results)
            
            stats = monitor.get_detailed_statistics()
            
            assert stats['total_samples'] == 10
            assert 'tokens' in stats
            assert 'time' in stats


class TestIntegration:
    """Integration tests for complete cascade system."""
    
    @pytest.mark.asyncio
    async def test_full_cascade_with_monitoring(self):
        """Test complete cascade with monitoring."""
        from monitoring import CascadeMonitor
        
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = CascadeMonitor(log_dir=tmpdir)
            
            task = {
                'id': 'integration_test',
                'type': 'code_review',
                'files': [
                    {
                        'path': 'test.py',
                        'content': 'def test(): pass',
                        'language': 'python'
                    }
                ]
            }
            
            # Run cascade
            results = await cascade_task(task)
            
            # Record in monitor
            monitor.record_cascade(results)
            
            # Verify monitoring
            assert monitor.metrics.total_cascades == 1
            dashboard = monitor.get_dashboard_data()
            assert dashboard['summary']['total_cascades'] == 1
    
    def test_quantum_with_cascade(self):
        """Test quantum optimizer with cascade tasks."""
        from quantum_optimizer import get_quantum_optimizer
        
        optimizer = get_quantum_optimizer()
        orchestrator = get_orchestrator()
        
        # Create sample tasks
        task_dict = {
            'id': 'quantum_test',
            'type': 'code_review',
            'files': [
                {'path': 'a.py', 'content': 'code1', 'language': 'python'},
                {'path': 'b.py', 'content': 'code2', 'language': 'python'}
            ]
        }
        
        # Decompose
        subtasks = orchestrator._decompose(task_dict)
        
        # Apply quantum optimization
        if subtasks:
            superposition = optimizer.create_superposition(subtasks)
            assert len(superposition) > 0


# Run all tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
