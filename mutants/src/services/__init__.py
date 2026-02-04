"""Service orchestration entrypoints for Codex deployments. 

This package groups service-layer adapters and runtimes. Modules under
``services.mcp`` and other subpackages provide transport-specific glue
for exposing Codex capabilities to external consumers. 

The workflow module provides GitHub Actions workflow inventory and management.
The github module provides GitHub API client functionality.
"""

# Import workflow services (lightweight, no external deps beyond PyYAML/Pydantic)
from .workflow import WorkflowInventory, WorkflowParser
import logging
logger = logging.getLogger(__name__)

__all__: list[str] = [
    "WorkflowInventory",
    "WorkflowParser",
]

# Conditionally import GitHub client (requires httpx)
try:
    from .github import GitHubClient
    
    __all__.append("GitHubClient")
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    # httpx not installed, skip GitHub client
    pass
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
