"""
GitHub Copilot CLI Cascade Delegation Package.

This package enables GitHub Copilot Agent to delegate tasks to
Copilot CLI as a co-partner for token optimization and model specialization.

Example Usage:
    >>> from copilot_cascade import cascade_task
    >>> import asyncio
    >>> 
    >>> task = {
    ...     'id': 'pr_123',
    ...     'type': 'full_pr_review',
    ...     'files': [{'path': 'test.py', 'content': 'code', 'language': 'python'}]
    ... }
    >>> 
    >>> results = asyncio.run(cascade_task(task))
    >>> print(results['verification']['confidence'])
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

__version__ = '1.0.0'
__author__ = 'Codex AI System'

__all__ = [
    # Types
    'DelegationTask',
    'CLIResponse',
    'TaskType',
    'ModelType',
    
    # Components
    'ContextCompressor',
    'CopilotCLIExecutor',
    'SmartDelegationRouter',
    'TokenBudgetManager',
    'CascadeOrchestrator',
    
    # Public API
    'cascade_task',
    'delegate_sync',
    'get_orchestrator',
]
