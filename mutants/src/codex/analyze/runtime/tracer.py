"""
Runtime Tracer - Capture execution traces and behavior.

Provides runtime analysis capabilities:
- Function call tracing
- IO capture (stdin, stdout, stderr)
- File operation monitoring
- Network access detection

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Bounded trace collection
- Memory-efficient streaming
- Timeout protection
- Deterministic execution
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .sandbox import SandboxConfig, SandboxManager

logger = logging.getLogger(__name__)

# Safeguards: Trace limits
MAX_TRACE_ENTRIES = 10000
MAX_CALL_DEPTH = 100
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


@dataclass
class TraceEntry:
    """A single trace entry."""
    timestamp: float
    event_type: str  # call, return, exception
    function_name: str
    filename: str
    lineno: int
    args: Optional[dict[str, Any]] = None
    return_value: Optional[Any] = None


@dataclass
class RuntimeReport:
    """Runtime analysis report.
    
    Contains execution results and traces for analyzed code.
    
    Attributes:
        snapshot_id: Snapshot being analyzed
        timestamp: When analysis was performed
        sandbox_config: Sandbox configuration used
        execution_results: Results of each execution
        call_traces: Function call traces (if enabled)
    """
    snapshot_id: str
    timestamp: datetime
    sandbox_config: dict[str, Any]
    execution_results: list[dict[str, Any]] = field(default_factory=list)
    call_traces: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "sandbox_config": self.sandbox_config,
            "execution_results": self.execution_results,
        }
    
    def save(self, path: Path) -> None:
        """Save report to JSON file."""
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


class RuntimeTracer:
    """Trace runtime behavior of Python code.
    
    Executes code in a sandboxed environment and captures:
    - Standard output and error
    - Exit codes
    - Execution duration
    - Function call traces (optional)
    
    Example:
        >>> tracer = RuntimeTracer("test-snapshot")
        >>> report = tracer.analyze(Path("source/"), sample_inputs=[Path("input.txt")])
        >>> print(f"Executed {len(report.execution_results)} samples")
    
    Safeguards:
    - Sandboxed execution with resource limits
    - Deterministic environment
    - Bounded trace collection
    """
    
    def xǁRuntimeTracerǁ__init____mutmut_orig(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = snapshot_id
        self.config = sandbox_config or SandboxConfig()
        self.sandbox = SandboxManager(self.config)
    
    def xǁRuntimeTracerǁ__init____mutmut_1(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = None
        self.config = sandbox_config or SandboxConfig()
        self.sandbox = SandboxManager(self.config)
    
    def xǁRuntimeTracerǁ__init____mutmut_2(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = snapshot_id
        self.config = None
        self.sandbox = SandboxManager(self.config)
    
    def xǁRuntimeTracerǁ__init____mutmut_3(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = snapshot_id
        self.config = sandbox_config and SandboxConfig()
        self.sandbox = SandboxManager(self.config)
    
    def xǁRuntimeTracerǁ__init____mutmut_4(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = snapshot_id
        self.config = sandbox_config or SandboxConfig()
        self.sandbox = None
    
    def xǁRuntimeTracerǁ__init____mutmut_5(
        self,
        snapshot_id: str,
        sandbox_config: Optional[SandboxConfig] = None,
    ):
        """Initialize runtime tracer.
        
        Args:
            snapshot_id: ID of snapshot being analyzed
            sandbox_config: Optional sandbox configuration
        """
        self.snapshot_id = snapshot_id
        self.config = sandbox_config or SandboxConfig()
        self.sandbox = SandboxManager(None)
    
    xǁRuntimeTracerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRuntimeTracerǁ__init____mutmut_1': xǁRuntimeTracerǁ__init____mutmut_1, 
        'xǁRuntimeTracerǁ__init____mutmut_2': xǁRuntimeTracerǁ__init____mutmut_2, 
        'xǁRuntimeTracerǁ__init____mutmut_3': xǁRuntimeTracerǁ__init____mutmut_3, 
        'xǁRuntimeTracerǁ__init____mutmut_4': xǁRuntimeTracerǁ__init____mutmut_4, 
        'xǁRuntimeTracerǁ__init____mutmut_5': xǁRuntimeTracerǁ__init____mutmut_5
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRuntimeTracerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRuntimeTracerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRuntimeTracerǁ__init____mutmut_orig)
    xǁRuntimeTracerǁ__init____mutmut_orig.__name__ = 'xǁRuntimeTracerǁ__init__'
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_orig(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_1(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = None
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_2(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "XXmain.pyXX",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_3(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "MAIN.PY",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_4(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "XX__main__.pyXX",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_5(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__MAIN__.PY",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_6(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "XXapp.pyXX",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_7(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "APP.PY",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_8(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "XXrun.pyXX",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_9(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "RUN.PY",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_10(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "XXcli.pyXX",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_11(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "CLI.PY",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_12(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir * candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_13(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = None
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_14(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(None)
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_15(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob(None))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_16(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("XX*.pyXX"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_17(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.PY"))
        if py_files:
            return py_files[0].name
        
        return None
    
    def xǁRuntimeTracerǁ_find_entry_point__mutmut_18(self, source_dir: Path) -> Optional[str]:
        """Find the entry point script.
        
        Looks for common entry point patterns.
        
        Args:
            source_dir: Source directory
            
        Returns:
            Entry point filename or None
        """
        candidates = [
            "main.py",
            "__main__.py",
            "app.py",
            "run.py",
            "cli.py",
        ]
        
        for candidate in candidates:
            if (source_dir / candidate).exists():
                return candidate
        
        # Fall back to first .py file
        py_files = list(source_dir.glob("*.py"))
        if py_files:
            return py_files[1].name
        
        return None
    
    xǁRuntimeTracerǁ_find_entry_point__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRuntimeTracerǁ_find_entry_point__mutmut_1': xǁRuntimeTracerǁ_find_entry_point__mutmut_1, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_2': xǁRuntimeTracerǁ_find_entry_point__mutmut_2, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_3': xǁRuntimeTracerǁ_find_entry_point__mutmut_3, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_4': xǁRuntimeTracerǁ_find_entry_point__mutmut_4, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_5': xǁRuntimeTracerǁ_find_entry_point__mutmut_5, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_6': xǁRuntimeTracerǁ_find_entry_point__mutmut_6, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_7': xǁRuntimeTracerǁ_find_entry_point__mutmut_7, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_8': xǁRuntimeTracerǁ_find_entry_point__mutmut_8, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_9': xǁRuntimeTracerǁ_find_entry_point__mutmut_9, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_10': xǁRuntimeTracerǁ_find_entry_point__mutmut_10, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_11': xǁRuntimeTracerǁ_find_entry_point__mutmut_11, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_12': xǁRuntimeTracerǁ_find_entry_point__mutmut_12, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_13': xǁRuntimeTracerǁ_find_entry_point__mutmut_13, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_14': xǁRuntimeTracerǁ_find_entry_point__mutmut_14, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_15': xǁRuntimeTracerǁ_find_entry_point__mutmut_15, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_16': xǁRuntimeTracerǁ_find_entry_point__mutmut_16, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_17': xǁRuntimeTracerǁ_find_entry_point__mutmut_17, 
        'xǁRuntimeTracerǁ_find_entry_point__mutmut_18': xǁRuntimeTracerǁ_find_entry_point__mutmut_18
    }
    
    def _find_entry_point(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRuntimeTracerǁ_find_entry_point__mutmut_orig"), object.__getattribute__(self, "xǁRuntimeTracerǁ_find_entry_point__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _find_entry_point.__signature__ = _mutmut_signature(xǁRuntimeTracerǁ_find_entry_point__mutmut_orig)
    xǁRuntimeTracerǁ_find_entry_point__mutmut_orig.__name__ = 'xǁRuntimeTracerǁ_find_entry_point'
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_orig(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_1(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = None
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_2(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                None,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_3(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                None,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_4(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=None,
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_5(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_6(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_7(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_8(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["XX--helpXX"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_9(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--HELP"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_10(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 or result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_11(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code != 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_12(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 1 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_13(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(None)
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_14(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug(None, entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_15(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", None, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_16(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, None)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_17(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug(entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_18(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_19(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, )
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_20(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("XXHelp detection failed for %s: %sXX", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_21(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("help detection failed for %s: %s", entry_point, exc)
        
        return None
    
    def xǁRuntimeTracerǁ_detect_argparse_help__mutmut_22(self, source_dir: Path, entry_point: str) -> Optional[str]:
        """Try to get help output from CLI scripts.
        
        Args:
            source_dir: Source directory
            entry_point: Entry point script
            
        Returns:
            Help output or None
        """
        try:
            result = self.sandbox.execute_in_tempdir(
                source_dir,
                entry_point,
                args=["--help"],
            )
            if result.exit_code == 0 and result.stdout:
                return result.stdout
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("HELP DETECTION FAILED FOR %S: %S", entry_point, exc)
        
        return None
    
    xǁRuntimeTracerǁ_detect_argparse_help__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_1': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_1, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_2': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_2, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_3': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_3, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_4': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_4, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_5': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_5, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_6': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_6, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_7': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_7, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_8': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_8, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_9': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_9, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_10': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_10, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_11': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_11, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_12': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_12, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_13': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_13, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_14': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_14, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_15': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_15, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_16': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_16, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_17': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_17, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_18': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_18, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_19': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_19, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_20': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_20, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_21': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_21, 
        'xǁRuntimeTracerǁ_detect_argparse_help__mutmut_22': xǁRuntimeTracerǁ_detect_argparse_help__mutmut_22
    }
    
    def _detect_argparse_help(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRuntimeTracerǁ_detect_argparse_help__mutmut_orig"), object.__getattribute__(self, "xǁRuntimeTracerǁ_detect_argparse_help__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _detect_argparse_help.__signature__ = _mutmut_signature(xǁRuntimeTracerǁ_detect_argparse_help__mutmut_orig)
    xǁRuntimeTracerǁ_detect_argparse_help__mutmut_orig.__name__ = 'xǁRuntimeTracerǁ_detect_argparse_help'
    
    def xǁRuntimeTracerǁanalyze__mutmut_orig(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_1(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = True,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_2(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = None
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_3(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(None)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_4(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = None
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_5(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(None)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_6(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_7(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning(None, source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_8(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", None)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_9(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning(source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_10(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", )
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_11(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("XXNo entry point found in %sXX", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_12(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("no entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_13(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("NO ENTRY POINT FOUND IN %S", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_14(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=None,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_15(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=None,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_16(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config=None,
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_17(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=None,
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_18(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_19(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_20(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_21(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_22(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "XXtimeout_secondsXX": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_23(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "TIMEOUT_SECONDS": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_24(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "XXmemory_limit_mbXX": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_25(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "MEMORY_LIMIT_MB": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_26(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "XXnetwork_enabledXX": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_27(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "NETWORK_ENABLED": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_28(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "XXinput_refXX": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_29(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "INPUT_REF": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_30(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "XX(no entry point)XX",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_31(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(NO ENTRY POINT)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_32(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "XXexit_codeXX": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_33(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "EXIT_CODE": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_34(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": +1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_35(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -2,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_36(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "XXerrorXX": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_37(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "ERROR": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_38(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "XXNo entry point foundXX",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_39(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "no entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_40(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "NO ENTRY POINT FOUND",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_41(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info(None, entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_42(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", None)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_43(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info(entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_44(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", )
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_45(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("XXFound entry point: %sXX", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_46(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_47(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("FOUND ENTRY POINT: %S", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_48(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = None
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_49(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = None
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_50(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(None, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_51(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, None)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_52(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_53(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, )
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_54(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append(None)
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_55(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "XXinput_refXX": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_56(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "INPUT_REF": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_57(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "XX(--help probe)XX",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_58(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--HELP PROBE)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_59(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "XXexit_codeXX": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_60(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "EXIT_CODE": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_61(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 1,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_62(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "XXstdout_snapshotXX": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_63(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "STDOUT_SNAPSHOT": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_64(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5001],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_65(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "XXduration_msXX": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_66(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "DURATION_MS": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_67(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 1,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_68(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = None
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_69(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(None)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_70(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = ""
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_71(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = None
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_72(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding=None)
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_73(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="XXutf-8XX")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_74(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="UTF-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_75(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(None)
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_76(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning(None, input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_77(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", None, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_78(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, None)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_79(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning(input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_80(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_81(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, )
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_82(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("XXCould not read input file %s: %sXX", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_83(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_84(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("COULD NOT READ INPUT FILE %S: %S", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_85(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = None
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_86(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        None,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_87(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=None,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_88(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_89(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_90(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir * entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_91(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = None
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_92(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        None,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_93(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        None,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_94(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=None,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_95(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_96(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_97(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_98(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append(None)
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_99(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "XXinput_refXX": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_100(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "INPUT_REF": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_101(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = None
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_102(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(None)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_103(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir * entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_104(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = None
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_105(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(None, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_106(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, None)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_107(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_108(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, )
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_109(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append(None)
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_110(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "XXinput_refXX": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_111(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "INPUT_REF": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_112(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "XX(no input)XX",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_113(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(NO INPUT)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_114(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=None,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_115(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=None,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_116(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config=None,
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_117(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=None,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_118(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_119(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_120(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_121(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            )
    
    def xǁRuntimeTracerǁanalyze__mutmut_122(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "XXtimeout_secondsXX": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_123(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "TIMEOUT_SECONDS": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_124(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "XXmemory_limit_mbXX": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_125(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "MEMORY_LIMIT_MB": self.config.memory_limit_mb,
                "network_enabled": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_126(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "XXnetwork_enabledXX": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    def xǁRuntimeTracerǁanalyze__mutmut_127(
        self,
        source_dir: Path,
        sample_inputs: Optional[list[Path]] = None,
        enable_tracing: bool = False,
    ) -> RuntimeReport:
        """Analyze runtime behavior of source code.
        
        Executes the code with provided sample inputs and captures
        execution results.
        
        Args:
            source_dir: Directory containing source files
            sample_inputs: Optional list of input files
            enable_tracing: Whether to enable call tracing
            
        Returns:
            RuntimeReport with execution results
        """
        now = datetime.now(timezone.utc)
        
        # Find entry point
        entry_point = self._find_entry_point(source_dir)
        if not entry_point:
            logger.warning("No entry point found in %s", source_dir)
            return RuntimeReport(
                snapshot_id=self.snapshot_id,
                timestamp=now,
                sandbox_config={
                    "timeout_seconds": self.config.timeout_seconds,
                    "memory_limit_mb": self.config.memory_limit_mb,
                    "network_enabled": self.config.network_enabled,
                },
                execution_results=[{
                    "input_ref": "(no entry point)",
                    "exit_code": -1,
                    "error": "No entry point found",
                }],
            )
        
        logger.info("Found entry point: %s", entry_point)
        
        execution_results: list[dict[str, Any]] = []
        
        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append({
                "input_ref": "(--help probe)",
                "exit_code": 0,
                "stdout_snapshot": help_output[:5000],
                "duration_ms": 0,
            })
        
        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None
                
                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        logger.warning("Could not read input file %s: %s", input_file, e)
                
                if enable_tracing:
                    result = self.sandbox.execute_with_tracing(
                        source_dir / entry_point,
                        stdin_input=stdin_input,
                    )
                else:
                    result = self.sandbox.execute_in_tempdir(
                        source_dir,
                        entry_point,
                        stdin_input=stdin_input,
                    )
                
                execution_results.append({
                    "input_ref": input_ref,
                    **result.to_dict(),
                })
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)
            
            execution_results.append({
                "input_ref": "(no input)",
                **result.to_dict(),
            })
        
        return RuntimeReport(
            snapshot_id=self.snapshot_id,
            timestamp=now,
            sandbox_config={
                "timeout_seconds": self.config.timeout_seconds,
                "memory_limit_mb": self.config.memory_limit_mb,
                "NETWORK_ENABLED": self.config.network_enabled,
            },
            execution_results=execution_results,
        )
    
    xǁRuntimeTracerǁanalyze__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRuntimeTracerǁanalyze__mutmut_1': xǁRuntimeTracerǁanalyze__mutmut_1, 
        'xǁRuntimeTracerǁanalyze__mutmut_2': xǁRuntimeTracerǁanalyze__mutmut_2, 
        'xǁRuntimeTracerǁanalyze__mutmut_3': xǁRuntimeTracerǁanalyze__mutmut_3, 
        'xǁRuntimeTracerǁanalyze__mutmut_4': xǁRuntimeTracerǁanalyze__mutmut_4, 
        'xǁRuntimeTracerǁanalyze__mutmut_5': xǁRuntimeTracerǁanalyze__mutmut_5, 
        'xǁRuntimeTracerǁanalyze__mutmut_6': xǁRuntimeTracerǁanalyze__mutmut_6, 
        'xǁRuntimeTracerǁanalyze__mutmut_7': xǁRuntimeTracerǁanalyze__mutmut_7, 
        'xǁRuntimeTracerǁanalyze__mutmut_8': xǁRuntimeTracerǁanalyze__mutmut_8, 
        'xǁRuntimeTracerǁanalyze__mutmut_9': xǁRuntimeTracerǁanalyze__mutmut_9, 
        'xǁRuntimeTracerǁanalyze__mutmut_10': xǁRuntimeTracerǁanalyze__mutmut_10, 
        'xǁRuntimeTracerǁanalyze__mutmut_11': xǁRuntimeTracerǁanalyze__mutmut_11, 
        'xǁRuntimeTracerǁanalyze__mutmut_12': xǁRuntimeTracerǁanalyze__mutmut_12, 
        'xǁRuntimeTracerǁanalyze__mutmut_13': xǁRuntimeTracerǁanalyze__mutmut_13, 
        'xǁRuntimeTracerǁanalyze__mutmut_14': xǁRuntimeTracerǁanalyze__mutmut_14, 
        'xǁRuntimeTracerǁanalyze__mutmut_15': xǁRuntimeTracerǁanalyze__mutmut_15, 
        'xǁRuntimeTracerǁanalyze__mutmut_16': xǁRuntimeTracerǁanalyze__mutmut_16, 
        'xǁRuntimeTracerǁanalyze__mutmut_17': xǁRuntimeTracerǁanalyze__mutmut_17, 
        'xǁRuntimeTracerǁanalyze__mutmut_18': xǁRuntimeTracerǁanalyze__mutmut_18, 
        'xǁRuntimeTracerǁanalyze__mutmut_19': xǁRuntimeTracerǁanalyze__mutmut_19, 
        'xǁRuntimeTracerǁanalyze__mutmut_20': xǁRuntimeTracerǁanalyze__mutmut_20, 
        'xǁRuntimeTracerǁanalyze__mutmut_21': xǁRuntimeTracerǁanalyze__mutmut_21, 
        'xǁRuntimeTracerǁanalyze__mutmut_22': xǁRuntimeTracerǁanalyze__mutmut_22, 
        'xǁRuntimeTracerǁanalyze__mutmut_23': xǁRuntimeTracerǁanalyze__mutmut_23, 
        'xǁRuntimeTracerǁanalyze__mutmut_24': xǁRuntimeTracerǁanalyze__mutmut_24, 
        'xǁRuntimeTracerǁanalyze__mutmut_25': xǁRuntimeTracerǁanalyze__mutmut_25, 
        'xǁRuntimeTracerǁanalyze__mutmut_26': xǁRuntimeTracerǁanalyze__mutmut_26, 
        'xǁRuntimeTracerǁanalyze__mutmut_27': xǁRuntimeTracerǁanalyze__mutmut_27, 
        'xǁRuntimeTracerǁanalyze__mutmut_28': xǁRuntimeTracerǁanalyze__mutmut_28, 
        'xǁRuntimeTracerǁanalyze__mutmut_29': xǁRuntimeTracerǁanalyze__mutmut_29, 
        'xǁRuntimeTracerǁanalyze__mutmut_30': xǁRuntimeTracerǁanalyze__mutmut_30, 
        'xǁRuntimeTracerǁanalyze__mutmut_31': xǁRuntimeTracerǁanalyze__mutmut_31, 
        'xǁRuntimeTracerǁanalyze__mutmut_32': xǁRuntimeTracerǁanalyze__mutmut_32, 
        'xǁRuntimeTracerǁanalyze__mutmut_33': xǁRuntimeTracerǁanalyze__mutmut_33, 
        'xǁRuntimeTracerǁanalyze__mutmut_34': xǁRuntimeTracerǁanalyze__mutmut_34, 
        'xǁRuntimeTracerǁanalyze__mutmut_35': xǁRuntimeTracerǁanalyze__mutmut_35, 
        'xǁRuntimeTracerǁanalyze__mutmut_36': xǁRuntimeTracerǁanalyze__mutmut_36, 
        'xǁRuntimeTracerǁanalyze__mutmut_37': xǁRuntimeTracerǁanalyze__mutmut_37, 
        'xǁRuntimeTracerǁanalyze__mutmut_38': xǁRuntimeTracerǁanalyze__mutmut_38, 
        'xǁRuntimeTracerǁanalyze__mutmut_39': xǁRuntimeTracerǁanalyze__mutmut_39, 
        'xǁRuntimeTracerǁanalyze__mutmut_40': xǁRuntimeTracerǁanalyze__mutmut_40, 
        'xǁRuntimeTracerǁanalyze__mutmut_41': xǁRuntimeTracerǁanalyze__mutmut_41, 
        'xǁRuntimeTracerǁanalyze__mutmut_42': xǁRuntimeTracerǁanalyze__mutmut_42, 
        'xǁRuntimeTracerǁanalyze__mutmut_43': xǁRuntimeTracerǁanalyze__mutmut_43, 
        'xǁRuntimeTracerǁanalyze__mutmut_44': xǁRuntimeTracerǁanalyze__mutmut_44, 
        'xǁRuntimeTracerǁanalyze__mutmut_45': xǁRuntimeTracerǁanalyze__mutmut_45, 
        'xǁRuntimeTracerǁanalyze__mutmut_46': xǁRuntimeTracerǁanalyze__mutmut_46, 
        'xǁRuntimeTracerǁanalyze__mutmut_47': xǁRuntimeTracerǁanalyze__mutmut_47, 
        'xǁRuntimeTracerǁanalyze__mutmut_48': xǁRuntimeTracerǁanalyze__mutmut_48, 
        'xǁRuntimeTracerǁanalyze__mutmut_49': xǁRuntimeTracerǁanalyze__mutmut_49, 
        'xǁRuntimeTracerǁanalyze__mutmut_50': xǁRuntimeTracerǁanalyze__mutmut_50, 
        'xǁRuntimeTracerǁanalyze__mutmut_51': xǁRuntimeTracerǁanalyze__mutmut_51, 
        'xǁRuntimeTracerǁanalyze__mutmut_52': xǁRuntimeTracerǁanalyze__mutmut_52, 
        'xǁRuntimeTracerǁanalyze__mutmut_53': xǁRuntimeTracerǁanalyze__mutmut_53, 
        'xǁRuntimeTracerǁanalyze__mutmut_54': xǁRuntimeTracerǁanalyze__mutmut_54, 
        'xǁRuntimeTracerǁanalyze__mutmut_55': xǁRuntimeTracerǁanalyze__mutmut_55, 
        'xǁRuntimeTracerǁanalyze__mutmut_56': xǁRuntimeTracerǁanalyze__mutmut_56, 
        'xǁRuntimeTracerǁanalyze__mutmut_57': xǁRuntimeTracerǁanalyze__mutmut_57, 
        'xǁRuntimeTracerǁanalyze__mutmut_58': xǁRuntimeTracerǁanalyze__mutmut_58, 
        'xǁRuntimeTracerǁanalyze__mutmut_59': xǁRuntimeTracerǁanalyze__mutmut_59, 
        'xǁRuntimeTracerǁanalyze__mutmut_60': xǁRuntimeTracerǁanalyze__mutmut_60, 
        'xǁRuntimeTracerǁanalyze__mutmut_61': xǁRuntimeTracerǁanalyze__mutmut_61, 
        'xǁRuntimeTracerǁanalyze__mutmut_62': xǁRuntimeTracerǁanalyze__mutmut_62, 
        'xǁRuntimeTracerǁanalyze__mutmut_63': xǁRuntimeTracerǁanalyze__mutmut_63, 
        'xǁRuntimeTracerǁanalyze__mutmut_64': xǁRuntimeTracerǁanalyze__mutmut_64, 
        'xǁRuntimeTracerǁanalyze__mutmut_65': xǁRuntimeTracerǁanalyze__mutmut_65, 
        'xǁRuntimeTracerǁanalyze__mutmut_66': xǁRuntimeTracerǁanalyze__mutmut_66, 
        'xǁRuntimeTracerǁanalyze__mutmut_67': xǁRuntimeTracerǁanalyze__mutmut_67, 
        'xǁRuntimeTracerǁanalyze__mutmut_68': xǁRuntimeTracerǁanalyze__mutmut_68, 
        'xǁRuntimeTracerǁanalyze__mutmut_69': xǁRuntimeTracerǁanalyze__mutmut_69, 
        'xǁRuntimeTracerǁanalyze__mutmut_70': xǁRuntimeTracerǁanalyze__mutmut_70, 
        'xǁRuntimeTracerǁanalyze__mutmut_71': xǁRuntimeTracerǁanalyze__mutmut_71, 
        'xǁRuntimeTracerǁanalyze__mutmut_72': xǁRuntimeTracerǁanalyze__mutmut_72, 
        'xǁRuntimeTracerǁanalyze__mutmut_73': xǁRuntimeTracerǁanalyze__mutmut_73, 
        'xǁRuntimeTracerǁanalyze__mutmut_74': xǁRuntimeTracerǁanalyze__mutmut_74, 
        'xǁRuntimeTracerǁanalyze__mutmut_75': xǁRuntimeTracerǁanalyze__mutmut_75, 
        'xǁRuntimeTracerǁanalyze__mutmut_76': xǁRuntimeTracerǁanalyze__mutmut_76, 
        'xǁRuntimeTracerǁanalyze__mutmut_77': xǁRuntimeTracerǁanalyze__mutmut_77, 
        'xǁRuntimeTracerǁanalyze__mutmut_78': xǁRuntimeTracerǁanalyze__mutmut_78, 
        'xǁRuntimeTracerǁanalyze__mutmut_79': xǁRuntimeTracerǁanalyze__mutmut_79, 
        'xǁRuntimeTracerǁanalyze__mutmut_80': xǁRuntimeTracerǁanalyze__mutmut_80, 
        'xǁRuntimeTracerǁanalyze__mutmut_81': xǁRuntimeTracerǁanalyze__mutmut_81, 
        'xǁRuntimeTracerǁanalyze__mutmut_82': xǁRuntimeTracerǁanalyze__mutmut_82, 
        'xǁRuntimeTracerǁanalyze__mutmut_83': xǁRuntimeTracerǁanalyze__mutmut_83, 
        'xǁRuntimeTracerǁanalyze__mutmut_84': xǁRuntimeTracerǁanalyze__mutmut_84, 
        'xǁRuntimeTracerǁanalyze__mutmut_85': xǁRuntimeTracerǁanalyze__mutmut_85, 
        'xǁRuntimeTracerǁanalyze__mutmut_86': xǁRuntimeTracerǁanalyze__mutmut_86, 
        'xǁRuntimeTracerǁanalyze__mutmut_87': xǁRuntimeTracerǁanalyze__mutmut_87, 
        'xǁRuntimeTracerǁanalyze__mutmut_88': xǁRuntimeTracerǁanalyze__mutmut_88, 
        'xǁRuntimeTracerǁanalyze__mutmut_89': xǁRuntimeTracerǁanalyze__mutmut_89, 
        'xǁRuntimeTracerǁanalyze__mutmut_90': xǁRuntimeTracerǁanalyze__mutmut_90, 
        'xǁRuntimeTracerǁanalyze__mutmut_91': xǁRuntimeTracerǁanalyze__mutmut_91, 
        'xǁRuntimeTracerǁanalyze__mutmut_92': xǁRuntimeTracerǁanalyze__mutmut_92, 
        'xǁRuntimeTracerǁanalyze__mutmut_93': xǁRuntimeTracerǁanalyze__mutmut_93, 
        'xǁRuntimeTracerǁanalyze__mutmut_94': xǁRuntimeTracerǁanalyze__mutmut_94, 
        'xǁRuntimeTracerǁanalyze__mutmut_95': xǁRuntimeTracerǁanalyze__mutmut_95, 
        'xǁRuntimeTracerǁanalyze__mutmut_96': xǁRuntimeTracerǁanalyze__mutmut_96, 
        'xǁRuntimeTracerǁanalyze__mutmut_97': xǁRuntimeTracerǁanalyze__mutmut_97, 
        'xǁRuntimeTracerǁanalyze__mutmut_98': xǁRuntimeTracerǁanalyze__mutmut_98, 
        'xǁRuntimeTracerǁanalyze__mutmut_99': xǁRuntimeTracerǁanalyze__mutmut_99, 
        'xǁRuntimeTracerǁanalyze__mutmut_100': xǁRuntimeTracerǁanalyze__mutmut_100, 
        'xǁRuntimeTracerǁanalyze__mutmut_101': xǁRuntimeTracerǁanalyze__mutmut_101, 
        'xǁRuntimeTracerǁanalyze__mutmut_102': xǁRuntimeTracerǁanalyze__mutmut_102, 
        'xǁRuntimeTracerǁanalyze__mutmut_103': xǁRuntimeTracerǁanalyze__mutmut_103, 
        'xǁRuntimeTracerǁanalyze__mutmut_104': xǁRuntimeTracerǁanalyze__mutmut_104, 
        'xǁRuntimeTracerǁanalyze__mutmut_105': xǁRuntimeTracerǁanalyze__mutmut_105, 
        'xǁRuntimeTracerǁanalyze__mutmut_106': xǁRuntimeTracerǁanalyze__mutmut_106, 
        'xǁRuntimeTracerǁanalyze__mutmut_107': xǁRuntimeTracerǁanalyze__mutmut_107, 
        'xǁRuntimeTracerǁanalyze__mutmut_108': xǁRuntimeTracerǁanalyze__mutmut_108, 
        'xǁRuntimeTracerǁanalyze__mutmut_109': xǁRuntimeTracerǁanalyze__mutmut_109, 
        'xǁRuntimeTracerǁanalyze__mutmut_110': xǁRuntimeTracerǁanalyze__mutmut_110, 
        'xǁRuntimeTracerǁanalyze__mutmut_111': xǁRuntimeTracerǁanalyze__mutmut_111, 
        'xǁRuntimeTracerǁanalyze__mutmut_112': xǁRuntimeTracerǁanalyze__mutmut_112, 
        'xǁRuntimeTracerǁanalyze__mutmut_113': xǁRuntimeTracerǁanalyze__mutmut_113, 
        'xǁRuntimeTracerǁanalyze__mutmut_114': xǁRuntimeTracerǁanalyze__mutmut_114, 
        'xǁRuntimeTracerǁanalyze__mutmut_115': xǁRuntimeTracerǁanalyze__mutmut_115, 
        'xǁRuntimeTracerǁanalyze__mutmut_116': xǁRuntimeTracerǁanalyze__mutmut_116, 
        'xǁRuntimeTracerǁanalyze__mutmut_117': xǁRuntimeTracerǁanalyze__mutmut_117, 
        'xǁRuntimeTracerǁanalyze__mutmut_118': xǁRuntimeTracerǁanalyze__mutmut_118, 
        'xǁRuntimeTracerǁanalyze__mutmut_119': xǁRuntimeTracerǁanalyze__mutmut_119, 
        'xǁRuntimeTracerǁanalyze__mutmut_120': xǁRuntimeTracerǁanalyze__mutmut_120, 
        'xǁRuntimeTracerǁanalyze__mutmut_121': xǁRuntimeTracerǁanalyze__mutmut_121, 
        'xǁRuntimeTracerǁanalyze__mutmut_122': xǁRuntimeTracerǁanalyze__mutmut_122, 
        'xǁRuntimeTracerǁanalyze__mutmut_123': xǁRuntimeTracerǁanalyze__mutmut_123, 
        'xǁRuntimeTracerǁanalyze__mutmut_124': xǁRuntimeTracerǁanalyze__mutmut_124, 
        'xǁRuntimeTracerǁanalyze__mutmut_125': xǁRuntimeTracerǁanalyze__mutmut_125, 
        'xǁRuntimeTracerǁanalyze__mutmut_126': xǁRuntimeTracerǁanalyze__mutmut_126, 
        'xǁRuntimeTracerǁanalyze__mutmut_127': xǁRuntimeTracerǁanalyze__mutmut_127
    }
    
    def analyze(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRuntimeTracerǁanalyze__mutmut_orig"), object.__getattribute__(self, "xǁRuntimeTracerǁanalyze__mutmut_mutants"), args, kwargs, self)
        return result 
    
    analyze.__signature__ = _mutmut_signature(xǁRuntimeTracerǁanalyze__mutmut_orig)
    xǁRuntimeTracerǁanalyze__mutmut_orig.__name__ = 'xǁRuntimeTracerǁanalyze'
    
    def xǁRuntimeTracerǁprobe_script__mutmut_orig(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_1(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = None
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_2(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(None)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_3(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = None
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_4(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "XXentry_pointXX": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_5(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "ENTRY_POINT": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_6(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "XXhas_helpXX": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_7(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "HAS_HELP": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_8(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": True,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_9(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "XXhelp_outputXX": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_10(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "HELP_OUTPUT": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_11(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "XXdetected_typeXX": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_12(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "DETECTED_TYPE": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_13(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "XXunknownXX",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_14(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "UNKNOWN",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_15(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_16(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = None
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_17(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(None, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_18(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, None)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_19(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_20(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, )
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_21(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = None
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_22(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["XXhas_helpXX"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_23(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["HAS_HELP"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_24(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = False
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_25(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = None
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_26(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["XXhelp_outputXX"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_27(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["HELP_OUTPUT"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_28(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2001]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_29(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = None
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_30(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["XXdetected_typeXX"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_31(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["DETECTED_TYPE"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_32(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "XXcliXX"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_33(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "CLI"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_34(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = None
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_35(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding=None)
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_36(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir * entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_37(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="XXutf-8XX")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_38(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="UTF-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_39(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() and "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_40(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "XXflaskXX" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_41(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "FLASK" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_42(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" not in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_43(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.upper() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_44(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "XXfastapiXX" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_45(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "FASTAPI" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_46(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" not in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_47(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.upper():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_48(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = None
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_49(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["XXdetected_typeXX"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_50(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["DETECTED_TYPE"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_51(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "XXweb_serviceXX"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_52(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "WEB_SERVICE"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_53(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() and "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_54(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "XXtkinterXX" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_55(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "TKINTER" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_56(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" not in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_57(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.upper() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_58(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "XXpyqtXX" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_59(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "PYQT" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_60(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" not in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_61(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.upper():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_62(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = None
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_63(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["XXdetected_typeXX"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_64(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["DETECTED_TYPE"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_65(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "XXguiXX"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_66(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "GUI"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_67(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source and "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_68(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "XXargparseXX" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_69(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "ARGPARSE" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_70(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" not in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_71(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "XXclickXX" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_72(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "CLICK" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_73(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" not in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_74(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = None
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_75(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["XXdetected_typeXX"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_76(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["DETECTED_TYPE"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_77(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "XXcliXX"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_78(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "CLI"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_79(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(None)
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_80(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug(None, entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_81(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", None, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_82(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, None)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_83(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug(entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_84(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_85(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, )
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_86(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("XXEntry point probe failed for %s: %sXX", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_87(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("entry point probe failed for %s: %s", entry_point, exc)
        
        return probe_result
    
    def xǁRuntimeTracerǁprobe_script__mutmut_88(self, source_dir: Path) -> dict[str, Any]:
        """Probe a script to understand its interface.
        
        Attempts to discover:
        - CLI arguments (via --help)
        - Entry points
        - Module attributes
        
        Args:
            source_dir: Source directory
            
        Returns:
            Dictionary with discovered information
        """
        entry_point = self._find_entry_point(source_dir)
        
        probe_result = {
            "entry_point": entry_point,
            "has_help": False,
            "help_output": None,
            "detected_type": "unknown",
        }
        
        if not entry_point:
            return probe_result
        
        # Try --help
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            probe_result["has_help"] = True
            probe_result["help_output"] = help_output[:2000]
            probe_result["detected_type"] = "cli"
        
        # Check source for patterns
        try:
            source = (source_dir / entry_point).read_text(encoding="utf-8")
            
            if "flask" in source.lower() or "fastapi" in source.lower():
                probe_result["detected_type"] = "web_service"
            elif "tkinter" in source.lower() or "pyqt" in source.lower():
                probe_result["detected_type"] = "gui"
            elif "argparse" in source or "click" in source:
                probe_result["detected_type"] = "cli"
                
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("ENTRY POINT PROBE FAILED FOR %S: %S", entry_point, exc)
        
        return probe_result
    
    xǁRuntimeTracerǁprobe_script__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRuntimeTracerǁprobe_script__mutmut_1': xǁRuntimeTracerǁprobe_script__mutmut_1, 
        'xǁRuntimeTracerǁprobe_script__mutmut_2': xǁRuntimeTracerǁprobe_script__mutmut_2, 
        'xǁRuntimeTracerǁprobe_script__mutmut_3': xǁRuntimeTracerǁprobe_script__mutmut_3, 
        'xǁRuntimeTracerǁprobe_script__mutmut_4': xǁRuntimeTracerǁprobe_script__mutmut_4, 
        'xǁRuntimeTracerǁprobe_script__mutmut_5': xǁRuntimeTracerǁprobe_script__mutmut_5, 
        'xǁRuntimeTracerǁprobe_script__mutmut_6': xǁRuntimeTracerǁprobe_script__mutmut_6, 
        'xǁRuntimeTracerǁprobe_script__mutmut_7': xǁRuntimeTracerǁprobe_script__mutmut_7, 
        'xǁRuntimeTracerǁprobe_script__mutmut_8': xǁRuntimeTracerǁprobe_script__mutmut_8, 
        'xǁRuntimeTracerǁprobe_script__mutmut_9': xǁRuntimeTracerǁprobe_script__mutmut_9, 
        'xǁRuntimeTracerǁprobe_script__mutmut_10': xǁRuntimeTracerǁprobe_script__mutmut_10, 
        'xǁRuntimeTracerǁprobe_script__mutmut_11': xǁRuntimeTracerǁprobe_script__mutmut_11, 
        'xǁRuntimeTracerǁprobe_script__mutmut_12': xǁRuntimeTracerǁprobe_script__mutmut_12, 
        'xǁRuntimeTracerǁprobe_script__mutmut_13': xǁRuntimeTracerǁprobe_script__mutmut_13, 
        'xǁRuntimeTracerǁprobe_script__mutmut_14': xǁRuntimeTracerǁprobe_script__mutmut_14, 
        'xǁRuntimeTracerǁprobe_script__mutmut_15': xǁRuntimeTracerǁprobe_script__mutmut_15, 
        'xǁRuntimeTracerǁprobe_script__mutmut_16': xǁRuntimeTracerǁprobe_script__mutmut_16, 
        'xǁRuntimeTracerǁprobe_script__mutmut_17': xǁRuntimeTracerǁprobe_script__mutmut_17, 
        'xǁRuntimeTracerǁprobe_script__mutmut_18': xǁRuntimeTracerǁprobe_script__mutmut_18, 
        'xǁRuntimeTracerǁprobe_script__mutmut_19': xǁRuntimeTracerǁprobe_script__mutmut_19, 
        'xǁRuntimeTracerǁprobe_script__mutmut_20': xǁRuntimeTracerǁprobe_script__mutmut_20, 
        'xǁRuntimeTracerǁprobe_script__mutmut_21': xǁRuntimeTracerǁprobe_script__mutmut_21, 
        'xǁRuntimeTracerǁprobe_script__mutmut_22': xǁRuntimeTracerǁprobe_script__mutmut_22, 
        'xǁRuntimeTracerǁprobe_script__mutmut_23': xǁRuntimeTracerǁprobe_script__mutmut_23, 
        'xǁRuntimeTracerǁprobe_script__mutmut_24': xǁRuntimeTracerǁprobe_script__mutmut_24, 
        'xǁRuntimeTracerǁprobe_script__mutmut_25': xǁRuntimeTracerǁprobe_script__mutmut_25, 
        'xǁRuntimeTracerǁprobe_script__mutmut_26': xǁRuntimeTracerǁprobe_script__mutmut_26, 
        'xǁRuntimeTracerǁprobe_script__mutmut_27': xǁRuntimeTracerǁprobe_script__mutmut_27, 
        'xǁRuntimeTracerǁprobe_script__mutmut_28': xǁRuntimeTracerǁprobe_script__mutmut_28, 
        'xǁRuntimeTracerǁprobe_script__mutmut_29': xǁRuntimeTracerǁprobe_script__mutmut_29, 
        'xǁRuntimeTracerǁprobe_script__mutmut_30': xǁRuntimeTracerǁprobe_script__mutmut_30, 
        'xǁRuntimeTracerǁprobe_script__mutmut_31': xǁRuntimeTracerǁprobe_script__mutmut_31, 
        'xǁRuntimeTracerǁprobe_script__mutmut_32': xǁRuntimeTracerǁprobe_script__mutmut_32, 
        'xǁRuntimeTracerǁprobe_script__mutmut_33': xǁRuntimeTracerǁprobe_script__mutmut_33, 
        'xǁRuntimeTracerǁprobe_script__mutmut_34': xǁRuntimeTracerǁprobe_script__mutmut_34, 
        'xǁRuntimeTracerǁprobe_script__mutmut_35': xǁRuntimeTracerǁprobe_script__mutmut_35, 
        'xǁRuntimeTracerǁprobe_script__mutmut_36': xǁRuntimeTracerǁprobe_script__mutmut_36, 
        'xǁRuntimeTracerǁprobe_script__mutmut_37': xǁRuntimeTracerǁprobe_script__mutmut_37, 
        'xǁRuntimeTracerǁprobe_script__mutmut_38': xǁRuntimeTracerǁprobe_script__mutmut_38, 
        'xǁRuntimeTracerǁprobe_script__mutmut_39': xǁRuntimeTracerǁprobe_script__mutmut_39, 
        'xǁRuntimeTracerǁprobe_script__mutmut_40': xǁRuntimeTracerǁprobe_script__mutmut_40, 
        'xǁRuntimeTracerǁprobe_script__mutmut_41': xǁRuntimeTracerǁprobe_script__mutmut_41, 
        'xǁRuntimeTracerǁprobe_script__mutmut_42': xǁRuntimeTracerǁprobe_script__mutmut_42, 
        'xǁRuntimeTracerǁprobe_script__mutmut_43': xǁRuntimeTracerǁprobe_script__mutmut_43, 
        'xǁRuntimeTracerǁprobe_script__mutmut_44': xǁRuntimeTracerǁprobe_script__mutmut_44, 
        'xǁRuntimeTracerǁprobe_script__mutmut_45': xǁRuntimeTracerǁprobe_script__mutmut_45, 
        'xǁRuntimeTracerǁprobe_script__mutmut_46': xǁRuntimeTracerǁprobe_script__mutmut_46, 
        'xǁRuntimeTracerǁprobe_script__mutmut_47': xǁRuntimeTracerǁprobe_script__mutmut_47, 
        'xǁRuntimeTracerǁprobe_script__mutmut_48': xǁRuntimeTracerǁprobe_script__mutmut_48, 
        'xǁRuntimeTracerǁprobe_script__mutmut_49': xǁRuntimeTracerǁprobe_script__mutmut_49, 
        'xǁRuntimeTracerǁprobe_script__mutmut_50': xǁRuntimeTracerǁprobe_script__mutmut_50, 
        'xǁRuntimeTracerǁprobe_script__mutmut_51': xǁRuntimeTracerǁprobe_script__mutmut_51, 
        'xǁRuntimeTracerǁprobe_script__mutmut_52': xǁRuntimeTracerǁprobe_script__mutmut_52, 
        'xǁRuntimeTracerǁprobe_script__mutmut_53': xǁRuntimeTracerǁprobe_script__mutmut_53, 
        'xǁRuntimeTracerǁprobe_script__mutmut_54': xǁRuntimeTracerǁprobe_script__mutmut_54, 
        'xǁRuntimeTracerǁprobe_script__mutmut_55': xǁRuntimeTracerǁprobe_script__mutmut_55, 
        'xǁRuntimeTracerǁprobe_script__mutmut_56': xǁRuntimeTracerǁprobe_script__mutmut_56, 
        'xǁRuntimeTracerǁprobe_script__mutmut_57': xǁRuntimeTracerǁprobe_script__mutmut_57, 
        'xǁRuntimeTracerǁprobe_script__mutmut_58': xǁRuntimeTracerǁprobe_script__mutmut_58, 
        'xǁRuntimeTracerǁprobe_script__mutmut_59': xǁRuntimeTracerǁprobe_script__mutmut_59, 
        'xǁRuntimeTracerǁprobe_script__mutmut_60': xǁRuntimeTracerǁprobe_script__mutmut_60, 
        'xǁRuntimeTracerǁprobe_script__mutmut_61': xǁRuntimeTracerǁprobe_script__mutmut_61, 
        'xǁRuntimeTracerǁprobe_script__mutmut_62': xǁRuntimeTracerǁprobe_script__mutmut_62, 
        'xǁRuntimeTracerǁprobe_script__mutmut_63': xǁRuntimeTracerǁprobe_script__mutmut_63, 
        'xǁRuntimeTracerǁprobe_script__mutmut_64': xǁRuntimeTracerǁprobe_script__mutmut_64, 
        'xǁRuntimeTracerǁprobe_script__mutmut_65': xǁRuntimeTracerǁprobe_script__mutmut_65, 
        'xǁRuntimeTracerǁprobe_script__mutmut_66': xǁRuntimeTracerǁprobe_script__mutmut_66, 
        'xǁRuntimeTracerǁprobe_script__mutmut_67': xǁRuntimeTracerǁprobe_script__mutmut_67, 
        'xǁRuntimeTracerǁprobe_script__mutmut_68': xǁRuntimeTracerǁprobe_script__mutmut_68, 
        'xǁRuntimeTracerǁprobe_script__mutmut_69': xǁRuntimeTracerǁprobe_script__mutmut_69, 
        'xǁRuntimeTracerǁprobe_script__mutmut_70': xǁRuntimeTracerǁprobe_script__mutmut_70, 
        'xǁRuntimeTracerǁprobe_script__mutmut_71': xǁRuntimeTracerǁprobe_script__mutmut_71, 
        'xǁRuntimeTracerǁprobe_script__mutmut_72': xǁRuntimeTracerǁprobe_script__mutmut_72, 
        'xǁRuntimeTracerǁprobe_script__mutmut_73': xǁRuntimeTracerǁprobe_script__mutmut_73, 
        'xǁRuntimeTracerǁprobe_script__mutmut_74': xǁRuntimeTracerǁprobe_script__mutmut_74, 
        'xǁRuntimeTracerǁprobe_script__mutmut_75': xǁRuntimeTracerǁprobe_script__mutmut_75, 
        'xǁRuntimeTracerǁprobe_script__mutmut_76': xǁRuntimeTracerǁprobe_script__mutmut_76, 
        'xǁRuntimeTracerǁprobe_script__mutmut_77': xǁRuntimeTracerǁprobe_script__mutmut_77, 
        'xǁRuntimeTracerǁprobe_script__mutmut_78': xǁRuntimeTracerǁprobe_script__mutmut_78, 
        'xǁRuntimeTracerǁprobe_script__mutmut_79': xǁRuntimeTracerǁprobe_script__mutmut_79, 
        'xǁRuntimeTracerǁprobe_script__mutmut_80': xǁRuntimeTracerǁprobe_script__mutmut_80, 
        'xǁRuntimeTracerǁprobe_script__mutmut_81': xǁRuntimeTracerǁprobe_script__mutmut_81, 
        'xǁRuntimeTracerǁprobe_script__mutmut_82': xǁRuntimeTracerǁprobe_script__mutmut_82, 
        'xǁRuntimeTracerǁprobe_script__mutmut_83': xǁRuntimeTracerǁprobe_script__mutmut_83, 
        'xǁRuntimeTracerǁprobe_script__mutmut_84': xǁRuntimeTracerǁprobe_script__mutmut_84, 
        'xǁRuntimeTracerǁprobe_script__mutmut_85': xǁRuntimeTracerǁprobe_script__mutmut_85, 
        'xǁRuntimeTracerǁprobe_script__mutmut_86': xǁRuntimeTracerǁprobe_script__mutmut_86, 
        'xǁRuntimeTracerǁprobe_script__mutmut_87': xǁRuntimeTracerǁprobe_script__mutmut_87, 
        'xǁRuntimeTracerǁprobe_script__mutmut_88': xǁRuntimeTracerǁprobe_script__mutmut_88
    }
    
    def probe_script(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRuntimeTracerǁprobe_script__mutmut_orig"), object.__getattribute__(self, "xǁRuntimeTracerǁprobe_script__mutmut_mutants"), args, kwargs, self)
        return result 
    
    probe_script.__signature__ = _mutmut_signature(xǁRuntimeTracerǁprobe_script__mutmut_orig)
    xǁRuntimeTracerǁprobe_script__mutmut_orig.__name__ = 'xǁRuntimeTracerǁprobe_script'
