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

from .cli_integration import (
    # Core types
    DelegationTask,
    CLIResponse,
    TaskType,
    ModelType,
    
    # Components
    ContextCompressor,
    CopilotCLIExecutor,
    SmartDelegationRouter,
    TokenBudgetManager,
    CascadeOrchestrator,
    
    # Public API
    cascade_task,
    delegate_sync,
    get_orchestrator,
)

# Enhanced modules
from .mcp_server import (
    MCPIntegration,
    MCPServer,
    MCPRequest,
    MCPResponse,
    MCPConnectionMode,
    get_mcp_integration,
    mcp_execute,
)

from .quantum_optimizer import (
    QuantumOptimizer,
    QuantumState,
    get_quantum_optimizer,
)

from .monitoring import (
    CascadeMonitor,
    CascadeMetrics,
    get_monitor,
    record_cascade,
    get_dashboard_data,
)

__version__ = '2.0.0'
__author__ = 'Codex AI System'

__all__ = [
    # Core types
    'DelegationTask',
    'CLIResponse',
    'TaskType',
    'ModelType',
    
    # Core components
    'ContextCompressor',
    'CopilotCLIExecutor',
    'SmartDelegationRouter',
    'TokenBudgetManager',
    'CascadeOrchestrator',
    
    # Core API
    'cascade_task',
    'delegate_sync',
    'get_orchestrator',
    
    # MCP integration
    'MCPIntegration',
    'MCPServer',
    'MCPRequest',
    'MCPResponse',
    'MCPConnectionMode',
    'get_mcp_integration',
    'mcp_execute',
    
    # Quantum optimization
    'QuantumOptimizer',
    'QuantumState',
    'get_quantum_optimizer',
    
    # Monitoring
    'CascadeMonitor',
    'CascadeMetrics',
    'get_monitor',
    'record_cascade',
    'get_dashboard_data',
]
