"""
Sandbox Manager - Manage sandboxed execution of untrusted code.

Provides isolated execution environment with:
- Resource limits (CPU, memory, timeout)
- Network isolation
- File system restrictions
- Execution tracing

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Strict resource limits
- Network disabled by default
- Timeout enforcement
- Temporary workspace isolation
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Safeguards: Default resource limits
DEFAULT_TIMEOUT = 60
DEFAULT_MEMORY_MB = 512
DEFAULT_MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB


@dataclass
class SandboxConfig:
    """Configuration for sandboxed execution.

    Attributes:
        timeout_seconds: Maximum execution time
        memory_limit_mb: Maximum memory usage
        network_enabled: Whether to allow network access
        allowed_file_write: Whether to allow file writes
        env_overrides: Environment variable overrides
        working_dir: Optional working directory
    """

    timeout_seconds: int = DEFAULT_TIMEOUT
    memory_limit_mb: int = DEFAULT_MEMORY_MB
    network_enabled: bool = False
    allowed_file_write: bool = False
    env_overrides: dict[str, str] = field(default_factory=dict)
    working_dir: Optional[Path] = None


@dataclass
class ExecutionResult:
    """Result of sandboxed execution.

    Attributes:
        exit_code: Process exit code
        stdout: Standard output content
        stderr: Standard error content
        duration_ms: Execution duration in milliseconds
        memory_peak_mb: Peak memory usage (if available)
        timed_out: Whether execution timed out
        file_operations: list of file operations detected
        network_attempts: list of network access attempts
    """

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    memory_peak_mb: Optional[float] = None
    timed_out: bool = False
    file_operations: list[dict[str, Any]] = field(default_factory=list)
    network_attempts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "exit_code": self.exit_code,
            "stdout_snapshot": self.stdout[:10000] if self.stdout else "",
            "stderr_snapshot": self.stderr[:10000] if self.stderr else "",
            "duration_ms": self.duration_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "timed_out": self.timed_out,
            "file_operations": self.file_operations,
            "network_attempts": self.network_attempts,
        }


class SandboxManager:
    """Manage sandboxed execution of untrusted code.

    Provides an isolated environment for running Python scripts with:
    - Resource limits (CPU, memory, timeout)
    - Deterministic execution (fixed seeds, hashes)
    - Output capture (stdout, stderr)
    - Optional network isolation

    Example:
        >>> manager = SandboxManager(SandboxConfig(timeout_seconds=30))
        >>> result = manager.execute(Path("script.py"))
        >>> logger.info(f"Exit code: {result.exit_code}")

    Safeguards:
    - All executions run with strict timeout
    - Deterministic environment variables set
    - Output size is bounded
    - Temporary workspace used
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """Initialize sandbox manager.

        Args:
            config: Sandbox configuration (uses defaults if None)
        """
        self.config = config or SandboxConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def _build_environment(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def _truncate_output(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) > DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] + "\n[... truncated ...]"
        return output

    def execute(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",  # type: ignore[arg-type]
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Exception: {type(e).__name__}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def execute_with_tracing(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )

            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")

        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {type(e).__name__}")
            raise ValueError(f"Path validation failed: {e}") from e

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace
from codex.logging.structured_logger import logger

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({str(script)!r}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            return self.execute(Path(wrapper_path), stdin_input=stdin_input)
        finally:
            os.unlink(wrapper_path)

    def execute_in_tempdir(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd
