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


# ============================================================================
# Enhanced Module Tests
# ============================================================================

class TestMCPIntegration:
    """Tests for MCP server integration."""

    def test_mock_mode_initialization(self):
        """Test MCP integration in mock mode."""
        from mcp_server import MCPConnectionMode, MCPIntegration

        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        assert mcp.mode == MCPConnectionMode.MOCK
        assert len(mcp.servers) >= 2  # At least github and codex_physics

    @pytest.mark.asyncio
    async def test_mock_connection(self):
        """Test mock MCP connection."""
        from mcp_server import MCPConnectionMode, MCPIntegration

        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        connected = await mcp.connect('github')
        assert connected is True
        assert 'github' in mcp.active_connections

    @pytest.mark.asyncio
    async def test_mock_execution(self):
        """Test mock MCP execution."""
        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest

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
        from mcp_server import MCPConnectionMode, MCPIntegration

        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        capabilities = mcp.get_available_capabilities()

        assert 'github' in capabilities
        assert 'repository_access' in capabilities['github']

    def test_statistics(self):
        """Test MCP statistics."""
        from mcp_server import MCPConnectionMode, MCPIntegration

        mcp = MCPIntegration(mode=MCPConnectionMode.MOCK)
        stats = mcp.get_statistics()

        assert 'mode' in stats
        assert 'registered_servers' in stats
        assert stats['mode'] == 'mock'


class TestQuantumOptimizer:
    """Tests for quantum-inspired optimization."""

    def test_superposition_creation(self):
        """Test creating task superposition."""
        from quantum_optimizer import get_quantum_optimizer

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


class TestMCPRealTransport:
    """Tests for the JSON-RPC 2.0 real-mode transport (IMP-004)."""

    @pytest.mark.asyncio
    async def test_real_mode_http_scheme_not_supported(self):
        """Non-HTTP/HTTPS endpoint returns an error response without making network calls."""
        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.REAL)
        # Override server URL with non-HTTP scheme (mcp:// as in default servers)
        server = MCPServer(
            name="test",
            url="mcp://localhost:9999/tools",
            capabilities=["file_operations"],
        )
        mcp.servers["test"] = server

        request = MCPRequest(
            server_name="test",
            capability="file_operations",
            payload={"action": "list"},
        )
        # Bypass connect() by patching active_connections
        mcp.active_connections["test"] = True

        response = await mcp._execute_real(request, server)
        assert response.status == "error"
        assert "Unsupported endpoint scheme" in (response.error or "")

    @pytest.mark.asyncio
    async def test_real_mode_jsonrpc_error_response(self, monkeypatch):
        """A JSON-RPC error in the response body is surfaced as status=error."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.REAL)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
        )

        error_body = json.dumps({
            "jsonrpc": "2.0",
            "id": "req-1",
            "error": {"code": -32601, "message": "Method not found"},
        }).encode()

        mock_resp = mock.MagicMock()
        mock_resp.read = mock.Mock(return_value=error_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_real(request, server)
        assert response.status == "error"
        assert "Method not found" in (response.error or "")

    @pytest.mark.asyncio
    async def test_real_mode_jsonrpc_success(self, monkeypatch):
        """A valid JSON-RPC 2.0 success response is returned as status=success."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.REAL)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
            auth_token="test-token",
        )

        success_body = json.dumps({
            "jsonrpc": "2.0",
            "id": "req-2",
            "result": {"branches": ["main", "develop"], "access_granted": True},
        }).encode()

        mock_resp = mock.MagicMock()
        mock_resp.read = mock.Mock(return_value=success_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_real(request, server)
        assert response.status == "success"
        assert response.data is not None
        assert "branches" in response.data

    @pytest.mark.asyncio
    async def test_real_mode_codex_mcp_endpoint_env_var(self, monkeypatch):
        """CODEX_MCP_ENDPOINT env var overrides server.url."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        monkeypatch.setenv("CODEX_MCP_ENDPOINT", "https://staging.copilot.example.com/mcp/")

        mcp = MCPIntegration(mode=MCPConnectionMode.REAL)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",  # This should be overridden
            capabilities=["repository_access"],
        )

        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            mock_resp = mock.MagicMock()
            mock_resp.read = mock.Mock(return_value=json.dumps({
                "jsonrpc": "2.0", "id": "req-3",
                "result": {"ok": True},
            }).encode())
            mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
            mock_resp.__exit__ = mock.Mock(return_value=False)
            return mock_resp

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_real(request, server)
        assert response.status == "success"
        assert captured.get("url") == "https://staging.copilot.example.com/mcp/"

    @pytest.mark.asyncio
    async def test_real_mode_http_error(self, monkeypatch):
        """urllib.error.HTTPError from the transport is handled as status=error."""
        import urllib.error
        import urllib.request

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.REAL)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
        )

        import unittest.mock as mock
        from io import BytesIO

        def fake_urlopen(req, timeout):
            hdrs = mock.MagicMock()
            raise urllib.error.HTTPError(
                url="https://api.githubcopilot.com/mcp/",
                code=401,
                msg="Unauthorized",
                hdrs=hdrs,
                fp=BytesIO(b'{"message": "Unauthorized"}'),
            )

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_real(request, server)
        assert response.status == "error"
        assert "401" in (response.error or "")

    def test_http_post_json_static_method(self, monkeypatch):
        """_http_post_json sends correct Content-Type and Authorization headers."""
        import json
        import unittest.mock as mock
        import urllib.request

        from mcp_server import MCPIntegration

        captured = {}

        def fake_urlopen(req, timeout):
            captured["headers"] = dict(req.headers)
            captured["data"] = json.loads(req.data)
            mock_resp = mock.MagicMock()
            mock_resp.read = mock.Mock(return_value=json.dumps({"ok": True}).encode())
            mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
            mock_resp.__exit__ = mock.Mock(return_value=False)
            return mock_resp

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        result = MCPIntegration._http_post_json(
            "https://example.com/mcp/",
            {"jsonrpc": "2.0", "method": "tools/test"},
            auth_token="my-token",
        )
        assert result == {"ok": True}
        headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
        assert "authorization" in headers_lower
        assert headers_lower["authorization"] == "Bearer my-token"
        assert captured["data"]["jsonrpc"] == "2.0"

    def test_http_post_json_rejects_non_http_scheme(self):
        """_http_post_json raises ValueError for non-HTTP/HTTPS URLs."""
        from mcp_server import MCPIntegration

        with pytest.raises(ValueError, match="http"):
            MCPIntegration._http_post_json(
                "mcp://localhost:9090/tools",
                {"jsonrpc": "2.0", "method": "tools/test"},
            )


class TestMCPStreamingTransport:
    """Unit tests for JSON-RPC 2.0 streaming transport via Server-Sent Events (IMP-005).

    These tests cover ``MCPConnectionMode.STREAMING`` and ``_execute_streaming()``,
    requested in the PR review (copilot-pull-request-reviewer, mcp_server.py:240-244).

    Coverage areas:
    - SSE frame parsing (single frame, multi-frame, ``_streaming_chunks`` counter)
    - Transparent fallback when server returns plain JSON instead of SSE
    - Error handling: JSON-RPC error frame, HTTP error, empty stream, bad scheme
    - Env-var override: ``CODEX_MCP_ENDPOINT`` routes request to staging endpoint
    - Mode selection: ``MCP_STREAMING_MODE=true`` auto-selects STREAMING mode
    - Static-method contract: ``_http_post_json_streaming`` header, scheme rejection
    """

    # ------------------------------------------------------------------ #
    # _execute_streaming — unit-level tests                                #
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    async def test_streaming_unsupported_scheme_returns_error(self):
        """Non-HTTP/HTTPS endpoint returns an error without making network calls."""
        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="test",
            url="mcp://localhost:9999/tools",
            capabilities=["file_operations"],
        )
        mcp.servers["test"] = server

        request = MCPRequest(
            server_name="test",
            capability="file_operations",
            payload={"action": "list"},
        )
        mcp.active_connections["test"] = True

        response = await mcp._execute_streaming(request, server)
        assert response.status == "error"
        assert "Unsupported endpoint scheme" in (response.error or "")

    @pytest.mark.asyncio
    async def test_streaming_sse_success(self, monkeypatch):
        """SSE stream with multiple data frames returns last frame as success."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
            auth_token="test-token",
        )

        # Simulate an SSE response with two data frames
        sse_body = (
            b"data: {\"jsonrpc\": \"2.0\", \"id\": \"r1\", \"result\": {\"partial\": true}}\n"
            b"\n"
            b"data: {\"jsonrpc\": \"2.0\", \"id\": \"r1\", \"result\": {\"branches\": [\"main\"], \"access_granted\": true}}\n"
            b"\n"
        )

        mock_resp = mock.MagicMock()
        mock_resp.headers.get = mock.Mock(return_value="text/event-stream")
        mock_resp.read = mock.Mock(return_value=sse_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_streaming(request, server)
        assert response.status == "success"
        assert response.data is not None
        assert response.data.get("branches") == ["main"]

    @pytest.mark.asyncio
    async def test_streaming_sse_jsonrpc_error_frame(self, monkeypatch):
        """SSE stream that ends with an error frame is surfaced as status=error."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
        )

        sse_body = (
            b"data: {\"jsonrpc\": \"2.0\", \"id\": \"r1\", \"error\": {\"code\": -32601, \"message\": \"Method not found\"}}\n"
        )

        mock_resp = mock.MagicMock()
        mock_resp.headers.get = mock.Mock(return_value="text/event-stream")
        mock_resp.read = mock.Mock(return_value=sse_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_streaming(request, server)
        assert response.status == "error"
        assert "Method not found" in (response.error or "")

    @pytest.mark.asyncio
    async def test_streaming_fallback_plain_json(self, monkeypatch):
        """Server returning plain JSON (non-SSE) is handled transparently."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
        )

        # Server responds with plain JSON — no SSE
        plain_body = json.dumps({
            "jsonrpc": "2.0",
            "id": "r1",
            "result": {"ok": True, "plain": True},
        }).encode()

        mock_resp = mock.MagicMock()
        mock_resp.headers.get = mock.Mock(return_value="application/json")
        mock_resp.read = mock.Mock(return_value=plain_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_streaming(request, server)
        assert response.status == "success"
        assert response.data is not None
        assert response.data.get("ok") is True

    @pytest.mark.asyncio
    async def test_streaming_http_error(self, monkeypatch):
        """urllib.error.HTTPError from transport is handled as status=error."""
        import unittest.mock as mock
        import urllib.error
        import urllib.request
        from io import BytesIO

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            capabilities=["repository_access"],
        )

        def fake_urlopen(req, timeout):
            hdrs = mock.MagicMock()
            raise urllib.error.HTTPError(
                url="https://api.githubcopilot.com/mcp/",
                code=503,
                msg="Service Unavailable",
                hdrs=hdrs,
                fp=BytesIO(b"Service Unavailable"),
            )

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_streaming(request, server)
        assert response.status == "error"
        assert "503" in (response.error or "")

    @pytest.mark.asyncio
    async def test_streaming_codex_mcp_endpoint_env_override(self, monkeypatch):
        """CODEX_MCP_ENDPOINT env var overrides server.url in streaming mode."""
        import json
        import unittest.mock as mock

        from mcp_server import MCPConnectionMode, MCPIntegration, MCPRequest, MCPServer

        monkeypatch.setenv("CODEX_MCP_ENDPOINT", "https://staging.mcp.example.com/stream/")

        mcp = MCPIntegration(mode=MCPConnectionMode.STREAMING)
        server = MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",  # should be overridden
            capabilities=["repository_access"],
        )

        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            mock_resp = mock.MagicMock()
            mock_resp.headers.get = mock.Mock(return_value="application/json")
            mock_resp.read = mock.Mock(return_value=json.dumps({
                "jsonrpc": "2.0",
                "id": "r-env",
                "result": {"env_override": True},
            }).encode())
            mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
            mock_resp.__exit__ = mock.Mock(return_value=False)
            return mock_resp

        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        request = MCPRequest(
            server_name="github",
            capability="repository_access",
            payload={"repo": "owner/repo"},
        )

        response = await mcp._execute_streaming(request, server)
        assert response.status == "success"
        assert captured.get("url") == "https://staging.mcp.example.com/stream/"

    # ------------------------------------------------------------------ #
    # MCPIntegration mode selection                                         #
    # ------------------------------------------------------------------ #

    def test_streaming_mode_set_via_env(self, monkeypatch):
        """MCP_STREAMING_MODE=true selects STREAMING mode automatically."""
        from mcp_server import MCPConnectionMode, MCPIntegration

        monkeypatch.setenv("MCP_STREAMING_MODE", "true")
        monkeypatch.delenv("MCP_REAL_MODE", raising=False)

        mcp = MCPIntegration()
        assert mcp.mode == MCPConnectionMode.STREAMING

    def test_real_mode_not_overridden_by_streaming_env_false(self, monkeypatch):
        """MCP_STREAMING_MODE=false with MCP_REAL_MODE=true selects REAL mode."""
        from mcp_server import MCPConnectionMode, MCPIntegration

        monkeypatch.setenv("MCP_STREAMING_MODE", "false")
        monkeypatch.setenv("MCP_REAL_MODE", "true")

        mcp = MCPIntegration()
        assert mcp.mode == MCPConnectionMode.REAL

    # ------------------------------------------------------------------ #
    # _http_post_json_streaming — static-method unit tests                 #
    # ------------------------------------------------------------------ #

    def test_http_post_json_streaming_rejects_non_http(self):
        """_http_post_json_streaming raises ValueError for non-HTTP/HTTPS URLs."""
        from mcp_server import MCPIntegration

        with pytest.raises(ValueError, match="http"):
            MCPIntegration._http_post_json_streaming(
                "mcp://localhost:9090/tools",
                {"jsonrpc": "2.0", "method": "tools/test"},
            )

    def test_http_post_json_streaming_sends_accept_sse_header(self, monkeypatch):
        """_http_post_json_streaming sends Accept: text/event-stream header."""
        import json
        import unittest.mock as mock
        import urllib.request

        from mcp_server import MCPIntegration

        captured = {}

        def fake_urlopen(req, timeout):
            captured["headers"] = dict(req.headers)
            mock_resp = mock.MagicMock()
            mock_resp.headers.get = mock.Mock(return_value="application/json")
            mock_resp.read = mock.Mock(return_value=json.dumps({"result": {"ok": True}}).encode())
            mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
            mock_resp.__exit__ = mock.Mock(return_value=False)
            return mock_resp

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        MCPIntegration._http_post_json_streaming(
            "https://example.com/mcp/",
            {"jsonrpc": "2.0", "method": "tools/test"},
        )
        headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
        assert "accept" in headers_lower
        assert "text/event-stream" in headers_lower["accept"]

    def test_http_post_json_streaming_empty_sse_stream_returns_error(self, monkeypatch):
        """SSE response with no parseable data frames returns error dict."""
        import unittest.mock as mock
        import urllib.request

        from mcp_server import MCPIntegration

        mock_resp = mock.MagicMock()
        mock_resp.headers.get = mock.Mock(return_value="text/event-stream")
        # Only comment lines and DONE — no valid data
        mock_resp.read = mock.Mock(return_value=b": ping\ndata: [DONE]\n")
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        result = MCPIntegration._http_post_json_streaming(
            "https://example.com/mcp/",
            {"jsonrpc": "2.0", "method": "tools/test"},
        )
        assert "error" in result
        assert "no parseable data" in result["error"]["message"].lower()

    def test_http_post_json_streaming_chunk_count_in_result(self, monkeypatch):
        """_streaming_chunks counter reflects the number of SSE frames received."""
        import json
        import unittest.mock as mock
        import urllib.request

        from mcp_server import MCPIntegration

        frames = [
            json.dumps({"jsonrpc": "2.0", "id": "r", "result": {"n": i}}).encode()
            for i in range(3)
        ]
        sse_body = b"\n".join(b"data: " + f for f in frames) + b"\n"

        mock_resp = mock.MagicMock()
        mock_resp.headers.get = mock.Mock(return_value="text/event-stream")
        mock_resp.read = mock.Mock(return_value=sse_body)
        mock_resp.__enter__ = mock.Mock(return_value=mock_resp)
        mock_resp.__exit__ = mock.Mock(return_value=False)

        monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: mock_resp)

        result = MCPIntegration._http_post_json_streaming(
            "https://example.com/mcp/",
            {"jsonrpc": "2.0", "method": "tools/test"},
        )
        assert result["_streaming_chunks"] == 3
        # Last frame wins
        assert result["result"]["n"] == 2


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
