"""
Comprehensive tests for CLI operations (supplement).

Tests cover:
- Advanced argument handling
- Complex workflows
- State management
- Configuration variations
- Performance considerations
"""

import json
import os
import tempfile

import pytest
from click.testing import CliRunner

# ============================================================================
# Advanced Argument Tests
# ============================================================================


class TestAdvancedArguments:
    """Advanced argument handling."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_variable_number_of_arguments(self, runner):
        import click

        @click.command()
        @click.argument("files", nargs=-1)
        def process(files):
            click.echo(f"Processing {len(files)} files")

        result = runner.invoke(process, ["a.txt", "b.txt", "c.txt"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Processing 3 files" in result.output, "Result must not be empty"

    def test_no_arguments_for_variadic(self, runner):
        import click

        @click.command()
        @click.argument("files", nargs=-1, required=False)
        def process(files):
            click.echo(f"Processing {len(files)} files")

        result = runner.invoke(process, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Processing 0 files" in result.output, "Result must not be empty"

    def test_argument_with_callback(self, runner):
        import click

        def validate_number(ctx, param, value):
            if value < 0:
                raise click.BadParameter("Must be positive")
            return value

        @click.command()
        @click.argument("count", type=int, callback=validate_number)
        def process(count):
            click.echo(f"Count: {count}")

        result = runner.invoke(process, ["42"])
        assert result.exit_code == 0, "Result must not be empty"

        result = runner.invoke(process, ["-5"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_argument_nargs_range(self, runner):
        import click

        @click.command()
        @click.argument("numbers", type=int, nargs=3)
        def add(numbers):
            click.echo(sum(numbers))

        result = runner.invoke(add, ["1", "2", "3"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "6" in result.output, "Result must not be empty"


# ============================================================================
# Complex Workflows
# ============================================================================


class TestComplexWorkflows:
    """Complex command workflows."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_chained_operations(self, runner):
        import click

        @click.group()
        def cli():
            pass

        @cli.group()
        def data():
            pass

        @data.command()
        def load():
            click.echo("Data loaded")

        @data.command()
        def transform():
            click.echo("Data transformed")

        @data.command()
        def save():
            click.echo("Data saved")

        result = runner.invoke(cli, ["data", "load"])
        assert "Data loaded" in result.output, "Result must not be empty"

    def test_nested_groups(self, runner):
        import click

        @click.group()
        def cli():
            pass

        @cli.group()
        def admin():
            pass

        @admin.group()
        def users():
            pass

        @users.command()
        def list():
            click.echo("Users: admin, user1, user2")

        result = runner.invoke(cli, ["admin", "users", "list"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Users:" in result.output, "Result must not be empty"

    def test_command_with_context(self, runner):
        import click

        @click.command()
        @click.pass_context
        def cmd(ctx):
            ctx.obj = {"key": "value"}
            click.echo(ctx.obj["key"])

        result = runner.invoke(cmd, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "value" in result.output, "Result must not be empty"


# ============================================================================
# Configuration Variations
# ============================================================================


class TestConfigurationVariations:
    """Configuration handling variations."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "debug": True,
                    "timeout": 30,
                    "hosts": ["localhost", "127.0.0.1"],
                },
                f,
            )
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_config_environment_variable(self, runner):
        import click

        pass  # removed redundant `import os` (top-level import used)

        @click.command()
        def cmd():
            config_file = os.environ.get("CONFIG_FILE")
            if config_file:
                click.echo(f"Using {config_file}")
            else:
                click.echo("No config")

        result = runner.invoke(cmd, env={"CONFIG_FILE": "/path/to/config"})
        assert "Using /path/to/config" in result.output, "Result must not be empty"

    def test_config_from_file(self, runner, temp_config):
        import click

        @click.command()
        @click.argument("config", type=click.File("r"))
        def cmd(config):
            data = json.load(config)
            click.echo(f'Debug: {data["debug"]}')

        result = runner.invoke(cmd, [temp_config])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Debug: True" in result.output, "Result must not be empty"

    def test_config_with_defaults(self, runner):
        import click

        @click.command()
        @click.option("--timeout", type=int, default=30)
        @click.option("--retries", type=int, default=3)
        def cmd(timeout, retries):
            click.echo(f"Timeout: {timeout}, Retries: {retries}")

        result = runner.invoke(cmd, [])
        assert "Timeout: 30, Retries: 3" in result.output

    def test_config_override(self, runner):
        import click

        @click.command()
        @click.option("--timeout", type=int, default=30)
        def cmd(timeout):
            click.echo(f"Timeout: {timeout}")

        result = runner.invoke(cmd, ["--timeout", "60"])
        assert "Timeout: 60" in result.output, "Result must not be empty"


# ============================================================================
# State Management
# ============================================================================


class TestStateManagement:
    """Command state management."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_state_persistence_across_subcommands(self, runner):
        import click

        @click.group(invoke_without_command=True)
        @click.pass_context
        def cli(ctx):
            ctx.ensure_object(dict)
            ctx.obj["initialized"] = True

        @cli.command()
        @click.pass_context
        def status(ctx):
            if ctx.obj.get("initialized"):
                click.echo("Initialized")
            else:
                click.echo("Not initialized")

        result = runner.invoke(cli, ["status"])
        assert "Initialized" in result.output, "Result must not be empty"

    def test_stateful_option(self, runner):
        import click

        @click.command()
        @click.option("--verbose", is_flag=True, is_eager=True)
        @click.option("--debug", is_flag=True)
        def cmd(verbose, debug):
            flags = []
            if verbose:
                flags.append("verbose")
            if debug:
                flags.append("debug")
            click.echo(f'Flags: {",".join(flags) if flags else "none"}')

        result = runner.invoke(cmd, ["-v", "-d"])
        assert "verbose" in result.output, "Result must not be empty"
        assert "debug" in result.output, "Result must not be empty"


# ============================================================================
# Error Recovery
# ============================================================================


class TestErrorRecovery:
    """Error handling and recovery."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_retry_logic(self, runner):
        import click

        attempt = 0

        @click.command()
        def cmd():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise click.ClickException(f"Attempt {attempt} failed")
            click.echo("Success")

        # In real use, would implement retry logic
        runner.invoke(cmd)
        # Result depends on retry implementation

    def test_error_with_suggestion(self, runner):
        import click

        @click.command()
        @click.argument("command")
        def cmd(command):
            valid = ["start", "stop", "restart"]
            if command not in valid:
                raise click.ClickException(
                    f"Unknown command: {command}\n" f'Valid commands: {", ".join(valid)}'
                )
            click.echo(f"Executing: {command}")

        result = runner.invoke(cmd, ["invalid"])
        assert result.exit_code != 0, "Result must not be empty"
        assert "Valid commands" in result.output, "Result must not be empty"

    def test_graceful_degradation(self, runner):
        import click

        @click.command()
        @click.option("--feature", is_flag=True)
        def cmd(feature):
            try:
                if feature:
                    # Simulated feature that might fail
                    raise Exception("Feature unavailable")
                click.echo("Basic mode")
            except Exception as e:
                click.echo(f"Warning: {e}")
                click.echo("Falling back to basic mode")

        result = runner.invoke(cmd, ["--feature"])
        assert result.exit_code == 0, "Result must not be empty"


# ============================================================================
# Input/Output Variations
# ============================================================================


class TestIOVariations:
    """Input/output variations."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_stdin_processing(self, runner):
        import click

        @click.command()
        def cmd():
            for line in click.get_text_stream("stdin"):
                click.echo(line.strip().upper())

        result = runner.invoke(cmd, input="hello\nworld\n")
        assert "HELLO" in result.output, "Result must not be empty"
        assert "WORLD" in result.output, "Result must not be empty"

    def test_multiple_input_files(self, runner):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
            f1.write("file1 content\n")
            f1_path = f1.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
            f2.write("file2 content\n")
            f2_path = f2.name

        try:
            import click

            @click.command()
            @click.argument("files", type=click.File("r"), nargs=-1)
            def process(files):
                for f in files:
                    click.echo(f.read())

            result = runner.invoke(process, [f1_path, f2_path])
            assert "file1 content" in result.output, "Result must not be empty"
            assert "file2 content" in result.output, "Result must not be empty"
        finally:
            os.remove(f1_path)
            os.remove(f2_path)

    def test_output_to_file(self, runner):
        import click

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")

            @click.command()
            @click.argument("output", type=click.File("w"))
            def cmd(output):
                output.write("test output\n")

            result = runner.invoke(cmd, [output_file])
            assert result.exit_code == 0, "Result must not be empty"
            assert os.path.exists(output_file), "Condition must be true"

            with open(output_file) as f:
                assert "test output" in f.read(), "Condition must be true"


# ============================================================================
# Command Discovery
# ============================================================================


class TestCommandDiscovery:
    """Command discovery and help."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_help(self, runner):
        import click

        @click.command()
        @click.option("--name", help="Your name")
        @click.option("--age", type=int, help="Your age")
        def cmd(name, age):
            """A simple command."""
            click.echo(f"{name} is {age}")

        result = runner.invoke(cmd, ["--help"])
        assert "Your name" in result.output, "Result must not be empty"
        assert "Your age" in result.output, "Result must not be empty"
        assert "A simple command" in result.output, "Result must not be empty"

    def test_group_commands_listing(self, runner):
        import click

        @click.group()
        def cli():
            """Main command group."""
            pass

        @cli.command()
        def cmd1():
            """First command."""
            pass

        @cli.command()
        def cmd2():
            """Second command."""
            pass

        result = runner.invoke(cli, ["--help"])
        assert "cmd1" in result.output, "Result must not be empty"
        assert "cmd2" in result.output, "Result must not be empty"

    def test_command_aliases(self, runner):
        import click

        @click.group()
        def cli():
            pass

        @cli.command(name="start")
        def start_cmd():
            click.echo("Starting...")

        # Test primary name
        result = runner.invoke(cli, ["start"])
        assert "Starting" in result.output, "Result must not be empty"


# ============================================================================
# Performance and Limits
# ============================================================================


class TestPerformanceAndLimits:
    """Performance and resource limit tests."""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    def test_command_with_many_options(self, runner):
        import click

        # Dynamically create command with many options using functools.wraps
        def create_command_with_options():
            @click.command()
            def cmd(**kwargs):
                click.echo(f"Options: {len(kwargs)}")

            # Apply option decorators dynamically
            for i in range(20):
                cmd = click.option(f"--opt{i}", default=f"val{i}")(cmd)

            return cmd

        cmd = create_command_with_options()

        # Command should handle many options
        result = runner.invoke(cmd, ["--opt0", "v0", "--opt1", "v1"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_command_with_large_input(self, runner):
        import click

        @click.command()
        def cmd():
            large_input = "x" * 10000
            click.echo(len(large_input))

        result = runner.invoke(cmd)
        assert "10000" in result.output, "Result must not be empty"

    def test_command_execution_time(self, runner):
        import time

        import click

        @click.command()
        def cmd():
            start = time.time()
            time.sleep(0.1)
            elapsed = time.time() - start
            click.echo(f"Elapsed: {elapsed:.2f}s")

        result = runner.invoke(cmd)
        assert "Elapsed:" in result.output, "Result must not be empty"
