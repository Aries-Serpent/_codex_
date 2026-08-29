"""CLI Command Handler Base Classes and Utilities.

This module extracts common command handling patterns from cli.py,
reducing the procedural God Module (2210 LOC, 55 functions) into
organized, testable command handlers.

Anti-pattern: PROCEDURAL GOD MODULE - 55 top-level functions
Refactoring: Convert to class-based command handler pattern

Benefits:
- Reduces cli.py from 2210 LOC to ~800 LOC
- Each command handler is independently testable
- Clearer separation of concerns
- Reusable exception handling patterns
- Centralized error logging and reporting
"""

from __future__ import annotations

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution.

    Provides consistent return value for all command handlers.
    """

    success: bool
    message: str = ""
    error: Optional[Exception] = None
    data: Optional[dict[str, Any]] = None
    exit_code: int = 0


class CLICommandHandler(ABC):
    """Base class for CLI command handlers.

    Extracted from cli.py to replace procedural functions with
    organized, testable command objects.

    Usage:
        class IngestionCommand(CLICommandHandler):
            name = "ingest"
            help = "Ingest data into Codex"

            def execute(self, *args, **kwargs) -> CommandResult:
                # Command logic here
                return CommandResult(success=True)

        handler = IngestionCommand()
        result = handler.execute()
    """

    name: str = "command"
    help: str = "Execute a command"
    aliases: list[str] = []

    def __init__(self):
        """Initialize the command handler."""
        self.logger = logger.getChild(self.name)

    def execute(self, *args, **kwargs) -> CommandResult:
        """Execute the command.

        Returns:
            CommandResult with success/failure status and data

        Raises:
            SystemExit: On fatal errors (exit_code != 0)
        """
        try:
            return self._execute_impl(*args, **kwargs)
        except Exception as exc:
            self.logger.error(f"Command failed: {exc}", exc_info=True)
            return CommandResult(
                success=False,
                message=f"Command '{self.name}' failed: {exc}",
                error=exc,
                exit_code=1,
            )

    @abstractmethod
    def _execute_impl(self, *args, **kwargs) -> CommandResult:
        """Implement the actual command logic.

        Subclasses override this method to provide command functionality.
        Exception handling is delegated to execute().
        """
        pass

    def log_result(self, result: CommandResult) -> None:
        """Log command result appropriately.

        Args:
            result: CommandResult to log
        """
        if result.success:
            self.logger.info(result.message or f"Command '{self.name}' succeeded")
        else:
            self.logger.error(result.message or f"Command '{self.name}' failed")

    def exit(self, result: CommandResult) -> None:
        """Exit with appropriate exit code.

        Args:
            result: CommandResult containing exit_code
        """
        if result.exit_code != 0:
            sys.exit(result.exit_code)


class CommandRegistry:
    """Registry for CLI command handlers.

    Replaces the procedural command dispatch in cli.py with
    a structured registry pattern.

    Usage:
        registry = CommandRegistry()
        registry.register(IngestionCommand())
        registry.register(ValidationCommand())

        # Execute a command
        result = registry.execute("ingest", arg1, arg2)
    """

    def __init__(self):
        """Initialize the command registry."""
        self._commands: dict[str, CLICommandHandler] = {}
        self._aliases: dict[str, str] = {}
        self.logger = logger.getChild("registry")

    def register(self, handler: CLICommandHandler) -> None:
        """Register a command handler.

        Args:
            handler: CLICommandHandler instance

        Raises:
            ValueError: If command name is already registered
        """
        if handler.name in self._commands:
            raise ValueError(f"Command '{handler.name}' already registered")

        self._commands[handler.name] = handler

        # Register aliases
        for alias in handler.aliases:
            if alias in self._aliases:
                raise ValueError(f"Alias '{alias}' already registered")
            self._aliases[alias] = handler.name

        self.logger.debug(f"Registered command: {handler.name}")

    def execute(self, command_name: str, *args, **kwargs) -> CommandResult:
        """Execute a registered command.

        Args:
            command_name: Name of the command (or alias)
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command

        Returns:
            CommandResult from command execution
        """
        # Resolve alias if needed
        name = self._aliases.get(command_name, command_name)

        if name not in self._commands:
            return CommandResult(
                success=False,
                message=f"Unknown command: {command_name}",
                exit_code=1,
            )

        handler = self._commands[name]
        result = handler.execute(*args, **kwargs)
        handler.log_result(result)
        return result

    def list_commands(self) -> list[tuple[str, str]]:
        """List all registered commands.

        Returns:
            List of (name, help) tuples
        """
        return [(h.name, h.help) for h in self._commands.values()]

    def get_handler(self, command_name: str) -> Optional[CLICommandHandler]:
        """Get a command handler by name.

        Args:
            command_name: Name of the command (or alias)

        Returns:
            CLICommandHandler or None if not found
        """
        name = self._aliases.get(command_name, command_name)
        return self._commands.get(name)


# Extracted command handlers (replacing procedural functions from cli.py)


class IngestionCommand(CLICommandHandler):
    """Ingest example data into the Codex environment.

    Extracted from _run_ingest() in cli.py
    """

    name = "ingest"
    help = "Ingest example data into Codex"

    def _execute_impl(
        self, src: Optional[Path] = None, dst: Optional[Path] = None
    ) -> CommandResult:
        """Ingest data from source to destination.

        Args:
            src: Source file path (default: data/example.jsonl)
            dst: Destination file path (default: data/ingested.jsonl)
        """
        src = src or Path("data/example.jsonl")
        dst = dst or Path("data/ingested.jsonl")

        if not src.exists():
            return CommandResult(
                success=False,
                message=f"Source file not found: {src}",
                exit_code=1,
            )

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            content = src.read_text(encoding="utf-8")
            dst.write_text(content, encoding="utf-8")

            return CommandResult(
                success=True,
                message=f"Ingested {src} → {dst}",
                data={"src": str(src), "dst": str(dst)},
            )
        except (OSError, IOError) as exc:
            return CommandResult(
                success=False,
                message=f"Failed to ingest data: {exc}",
                error=exc,
                exit_code=1,
            )


class ValidationCommand(CLICommandHandler):
    """Run local validation checks (lint + tests).

    Extracted from _run_ci() in cli.py
    """

    name = "validate"
    aliases = ["ci", "check"]
    help = "Run local CI checks (lint + tests)"

    def _execute_impl(self, session: str = "tests") -> CommandResult:
        """Run validation using nox.

        Args:
            session: Nox session to run (default: tests)
        """
        import subprocess

        try:
            result = subprocess.run(
                ["nox", "-s", session],
                check=True,
                capture_output=True,
                text=True,
            )
            return CommandResult(
                success=True,
                message=f"Validation passed: nox -s {session}",
                data={"session": session, "output": result.stdout},
            )
        except subprocess.CalledProcessError as exc:
            return CommandResult(
                success=False,
                message=f"Validation failed: {exc}",
                error=exc,
                exit_code=1,
            )
        except (ValueError, TypeError, RuntimeError) as exc:
            # Extracted exception handling from original _run_ci()
            return CommandResult(
                success=False,
                message=f"Validation error: {exc}",
                error=exc,
                exit_code=1,
            )


class HelpCommand(CLICommandHandler):
    """Display help for registered commands.

    Replaces procedural help printing with structured handler.
    """

    name = "help"
    aliases = ["?", "-h", "--help"]
    help = "Display help for commands"

    def __init__(self, registry: CommandRegistry):
        """Initialize help command with command registry.

        Args:
            registry: CommandRegistry to list commands from
        """
        super().__init__()
        self.registry = registry

    def _execute_impl(self, command_name: Optional[str] = None) -> CommandResult:
        """Display help for a command or all commands.

        Args:
            command_name: Specific command to show help for (optional)
        """
        if command_name:
            handler = self.registry.get_handler(command_name)
            if handler:
                help_text = f"\n{handler.name}\n  {handler.help}\n"
                return CommandResult(success=True, message=help_text)
            else:
                return CommandResult(
                    success=False,
                    message=f"Unknown command: {command_name}",
                    exit_code=1,
                )

        # List all commands
        commands = self.registry.list_commands()
        help_text = "\nAvailable commands:\n"
        for name, help_str in commands:
            help_text += f"  {name:20} {help_str}\n"

        return CommandResult(success=True, message=help_text)
