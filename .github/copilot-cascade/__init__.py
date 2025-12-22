"""
GitHub Copilot CLI Cascade Delegation Package.

This package enables GitHub Copilot Agent to delegate tasks to
Copilot CLI as a co-partner for token optimization and model specialization.

Includes quantum-inspired optimization, MCP server integration, and
performance monitoring for production-grade cascade operations.

Example Usage:
    >>> from copilot_cascade import cascade_task, get_quantum_optimizer, get_monitor
    >>> import asyncio
    >>>
    >>> # Basic cascade
    >>> task = {
    ...     'id': 'pr_123',
    ...     'type': 'full_pr_review',
    ...     'files': [{'path': 'test.py', 'content': 'code', 'language': 'python'}]
    ... }
    >>> results = asyncio.run(cascade_task(task))
    >>>
    >>> # Quantum optimization
    >>> optimizer = get_quantum_optimizer()
    >>> superposition = optimizer.create_superposition(tasks)
    >>>
    >>> # Monitoring
    >>> monitor = get_monitor()
    >>> dashboard = monitor.get_dashboard_data()
"""

# Conditional imports to handle test environment
try:
    from .cli_integration import (
        CascadeOrchestrator,
        CLIResponse,
        # Components
        ContextCompressor,
        CopilotCLIExecutor,
        # Core types
        DelegationTask,
        ModelType,
        SmartDelegationRouter,
        TaskType,
        TokenBudgetManager,
        # Public API
        cascade_task,
        delegate_sync,
        get_orchestrator,
    )
except ImportError:
    # Handle relative imports when used as package
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

# Enhanced modules
try:
    from .mcp_server import (
        MCPConnectionMode,
        MCPIntegration,
        MCPRequest,
        MCPResponse,
        MCPServer,
        get_mcp_integration,
        mcp_execute,
    )
except ImportError:
    from mcp_server import (
        MCPConnectionMode,
        MCPIntegration,
        MCPRequest,
        MCPResponse,
        MCPServer,
        get_mcp_integration,
        mcp_execute,
    )

try:
    from .quantum_optimizer import (
        QuantumOptimizer,
        QuantumState,
        get_quantum_optimizer,
    )
except ImportError:
    from quantum_optimizer import QuantumOptimizer, QuantumState, get_quantum_optimizer

try:
    from .monitoring import (
        CascadeMetrics,
        CascadeMonitor,
        get_dashboard_data,
        get_monitor,
        record_cascade,
    )
except ImportError:
    from monitoring import (
        CascadeMetrics,
        CascadeMonitor,
        get_dashboard_data,
        get_monitor,
        record_cascade,
    )

__version__ = "2.0.0"
__author__ = "Codex AI System"

__all__ = [
    # Core types
    "DelegationTask",
    "CLIResponse",
    "TaskType",
    "ModelType",
    # Core components
    "ContextCompressor",
    "CopilotCLIExecutor",
    "SmartDelegationRouter",
    "TokenBudgetManager",
    "CascadeOrchestrator",
    # Core API
    "cascade_task",
    "delegate_sync",
    "get_orchestrator",
    # MCP integration
    "MCPIntegration",
    "MCPServer",
    "MCPRequest",
    "MCPResponse",
    "MCPConnectionMode",
    "get_mcp_integration",
    "mcp_execute",
    # Quantum optimization
    "QuantumOptimizer",
    "QuantumState",
    "get_quantum_optimizer",
    # Monitoring
    "CascadeMonitor",
    "CascadeMetrics",
    "get_monitor",
    "record_cascade",
    "get_dashboard_data",
]
