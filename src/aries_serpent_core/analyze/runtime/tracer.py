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

__all__ = [
    "MAX_CALL_DEPTH",
    "MAX_TRACE_ENTRIES",
    "RuntimeReport",
    "RuntimeTracer",
    "TraceEntry",
]


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
        >>> logger.info(f"Executed {len(report.execution_results)} samples")

    Safeguards:
    - Sandboxed execution with resource limits
    - Deterministic environment
    - Bounded trace collection
    """

    def __init__(
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

    def _find_entry_point(self, source_dir: Path) -> Optional[str]:
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

    def _detect_argparse_help(self, source_dir: Path, entry_point: str) -> Optional[str]:
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
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.debug(f"Exception: {type(exc).__name__}")
            # Ignore errors from --help execution - it's optional metadata collection.
            # Failures here don't prevent the main analysis.
            logger.debug("Help detection failed for %s: %s", entry_point, exc)

        return None

    def analyze(
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
                execution_results=[
                    {
                        "input_ref": "(no entry point)",
                        "exit_code": -1,
                        "error": "No entry point found",
                    }
                ],
            )

        logger.info("Found entry point: %s", entry_point)

        execution_results: list[dict[str, Any]] = []

        # Try to get help output first
        help_output = self._detect_argparse_help(source_dir, entry_point)
        if help_output:
            execution_results.append(
                {
                    "input_ref": "(--help probe)",
                    "exit_code": 0,
                    "stdout_snapshot": help_output[:5000],
                    "duration_ms": 0,
                }
            )

        # Execute with sample inputs
        if sample_inputs:
            for input_file in sample_inputs:
                input_ref = str(input_file)
                stdin_input = None

                if input_file.exists():
                    try:
                        stdin_input = input_file.read_text(encoding="utf-8")
                    except (IOError, OSError) as e:
                        logger.debug("Exception: <ERROR_TYPE>")
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

                execution_results.append(
                    {
                        "input_ref": input_ref,
                        **result.to_dict(),
                    }
                )
        else:
            # Execute without input
            if enable_tracing:
                result = self.sandbox.execute_with_tracing(source_dir / entry_point)
            else:
                result = self.sandbox.execute_in_tempdir(source_dir, entry_point)

            execution_results.append(
                {
                    "input_ref": "(no input)",
                    **result.to_dict(),
                }
            )

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

    def probe_script(self, source_dir: Path) -> dict[str, Any]:
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

        except (ValueError, TypeError) as exc:
            logger.debug("Exception: <ERROR_TYPE>")
            # Ignore errors during source code inspection - this is best-effort detection.
            # Missing type information doesn't prevent the rest of the analysis.
            logger.debug("Entry point probe failed for %s: %s", entry_point, exc)

        return probe_result
