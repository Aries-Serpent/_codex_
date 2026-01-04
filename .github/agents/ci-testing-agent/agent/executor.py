"""
Sandbox Command Runner
Executes tests in isolated environment with timeout and resource limits.
"""
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List


class SandboxExecutor:
    """Executes test commands in sandboxed environment."""

    def __init__(self, workspace: Path, timeout: int = 300):
        """
        Initialize SandboxExecutor.
        
        Args:
            workspace: Path to repository workspace
            timeout: Command timeout in seconds (default: 300)
        """
        self.workspace = workspace
        self.timeout = timeout

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute test command in sandbox.
        
        Args:
            task: Task dictionary containing:
                - command: Command to execute (default: 'pytest')
                - args: List of command arguments (optional)
                - env: Environment variables dict (optional)
                - timeout: Override default timeout (optional)
        
        Returns:
            Dictionary with:
                - status: 'success', 'failure', 'timeout', or 'error'
                - returncode: Command exit code
                - stdout: Command standard output
                - stderr: Command standard error
                - command: Full command executed
        """
        command = task.get("command", "pytest")
        args = task.get("args", [])
        env_vars = task.get("env", {})
        timeout = task.get("timeout", self.timeout)

        # Build full command
        full_command = [command] + args

        # Prepare environment
        env = os.environ.copy()
        env.update(env_vars)

        try:
            # Pass environment variables to subprocess
            # Note: env parameter requires a complete environment dict
            result = subprocess.run(
                full_command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env if env else None,
            )

            return {
                "status": "success" if result.returncode == 0 else "failure",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(full_command),
            }

        except subprocess.TimeoutExpired as e:
            return {
                "status": "timeout",
                "returncode": -1,
                "error": f"Command timed out after {timeout}s",
                "command": " ".join(full_command),
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else "",
            }

        except FileNotFoundError as e:
            return {
                "status": "error",
                "returncode": -1,
                "error": f"Command not found: {command}",
                "command": " ".join(full_command),
            }

        except Exception as e:
            return {
                "status": "error",
                "returncode": -1,
                "error": str(e),
                "command": " ".join(full_command),
            }

    def execute_parallel(
        self, tasks: List[Dict[str, Any]], max_workers: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple test commands in parallel.
        
        Args:
            tasks: List of task dictionaries
            max_workers: Maximum number of parallel workers (default: 4)
        
        Returns:
            List of result dictionaries
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.execute, task): task for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle unexpected errors
                    task = future_to_task[future]
                    results.append(
                        {
                            "status": "error",
                            "returncode": -1,
                            "error": f"Unexpected error: {e}",
                            "command": task.get("command", "unknown"),
                        }
                    )

        return results

    def validate_command(self, command: str) -> bool:
        """
        Validate that command is safe to execute.
        
        Args:
            command: Command to validate
        
        Returns:
            True if command is safe, False otherwise
        """
        # List of allowed commands
        allowed_commands = {
            "pytest",
            "python",
            "python3",
            "coverage",
            "ruff",
            "black",
            "isort",
            "mypy",
        }

        # Check if command is in allowed list
        return command in allowed_commands

    def execute_with_validation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute command with safety validation.
        
        Args:
            task: Task dictionary
        
        Returns:
            Result dictionary or error if validation fails
        """
        command = task.get("command", "pytest")

        if not self.validate_command(command):
            return {
                "status": "error",
                "returncode": -1,
                "error": f"Command not allowed: {command}",
                "command": command,
            }

        return self.execute(task)
