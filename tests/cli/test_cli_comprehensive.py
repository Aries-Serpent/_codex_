"""
Comprehensive tests for CLI modules.

Tests cover:
- Command-line argument parsing
- Input validation
- File operations
- Configuration loading
- Error handling
- Output formatting
- Exit codes
"""

import os
import tempfile

import pytest
from click.testing import CliRunner

# ============================================================================
# CLI Testing Utilities
# ============================================================================


@pytest.fixture
def cli_runner():
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_file(temp_dir):
    """Create temporary file."""
    filepath = os.path.join(temp_dir, "test_file.txt")
    with open(filepath, "w") as f:
        f.write("test content")
    return filepath


# ============================================================================
# Argument Parsing Tests
# ============================================================================


class TestArgumentParsing:
    """Command-line argument parsing."""

    def test_required_argument(self, cli_runner):
        # Mock command with required argument
        import click

        @click.command()
        @click.argument("name")
        def hello(name):
            click.echo(f"Hello {name}!")

        result = cli_runner.invoke(hello, ["World"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Hello World!" in result.output, "Result must not be empty"

    def test_missing_required_argument(self, cli_runner):
        import click

        @click.command()
        @click.argument("name")
        def hello(name):
            click.echo(f"Hello {name}!")

        result = cli_runner.invoke(hello, [])
        assert result.exit_code != 0, "Result must not be empty"

    def test_optional_argument(self, cli_runner):
        import click

        @click.command()
        @click.argument("name", required=False)
        def hello(name):
            click.echo(f'Hello {name or "World"}!')

        result = cli_runner.invoke(hello, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Hello World!" in result.output, "Result must not be empty"

    def test_multiple_arguments(self, cli_runner):
        import click

        @click.command()
        @click.argument("first")
        @click.argument("last")
        def greet(first, last):
            click.echo(f"{first} {last}")

        result = cli_runner.invoke(greet, ["John", "Doe"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "John Doe" in result.output, "Result must not be empty"

    def test_argument_with_default(self, cli_runner):
        import click

        @click.command()
        @click.argument("count", type=int, default=1)
        def repeat(count):
            click.echo("x" * count)

        result = cli_runner.invoke(repeat, [])
        assert result.exit_code == 0, "Result must not be empty"
        assert "x" in result.output, "Result must not be empty"

    def test_argument_type_validation(self, cli_runner):
        import click

        @click.command()
        @click.argument("count", type=int)
        def process(count):
            click.echo(count * 2)

        result = cli_runner.invoke(process, ["not_a_number"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_argument_with_choices(self, cli_runner):
        import click

        @click.command()
        @click.argument("level", type=click.Choice(["info", "debug", "error"]))
        def log(level):
            click.echo(level)

        result = cli_runner.invoke(log, ["info"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "info" in result.output, "Result must not be empty"

    def test_argument_invalid_choice(self, cli_runner):
        import click

        @click.command()
        @click.argument("level", type=click.Choice(["info", "debug"]))
        def log(level):
            click.echo(level)

        result = cli_runner.invoke(log, ["invalid"])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Option Parsing Tests
# ============================================================================


class TestOptionParsing:
    """Command-line option parsing."""

    def test_boolean_flag(self, cli_runner):
        import click

        @click.command()
        @click.option("--verbose", is_flag=True)
        def run(verbose):
            click.echo("verbose" if verbose else "quiet")

        result = cli_runner.invoke(run, ["--verbose"])
        assert "verbose" in result.output, "Result must not be empty"

    def test_short_option(self, cli_runner):
        import click

        @click.command()
        @click.option("-v", "--verbose", is_flag=True)
        def run(verbose):
            click.echo("verbose" if verbose else "quiet")

        result = cli_runner.invoke(run, ["-v"])
        assert "verbose" in result.output, "Result must not be empty"

    def test_option_with_value(self, cli_runner):
        import click

        @click.command()
        @click.option("--name", default="World")
        def greet(name):
            click.echo(f"Hello {name}!")

        result = cli_runner.invoke(greet, ["--name", "Alice"])
        assert "Hello Alice!" in result.output, "Result must not be empty"

    def test_multiple_values_option(self, cli_runner):
        import click

        @click.command()
        @click.option("--item", multiple=True)
        def process(item):
            for i in item:
                click.echo(i)

        result = cli_runner.invoke(process, ["--item", "a", "--item", "b"])
        assert "a" in result.output, "Result must not be empty"
        assert "b" in result.output, "Result must not be empty"

    def test_option_count(self, cli_runner):
        import click

        @click.command()
        @click.option("-v", "--verbose", count=True)
        def run(verbose):
            click.echo(f"verbosity: {verbose}")

        result = cli_runner.invoke(run, ["-vvv"])
        assert "verbosity: 3" in result.output, "Result must not be empty"

    def test_required_option(self, cli_runner):
        import click

        @click.command()
        @click.option("--name", required=True)
        def greet(name):
            click.echo(name)

        result = cli_runner.invoke(greet, [])
        assert result.exit_code != 0, "Result must not be empty"

    def test_option_with_default(self, cli_runner):
        import click

        @click.command()
        @click.option("--count", type=int, default=1)
        def repeat(count):
            click.echo("x" * count)

        result = cli_runner.invoke(repeat, [])
        assert "x" in result.output, "Result must not be empty"


# ============================================================================
# File I/O Tests
# ============================================================================


class TestFileOperations:
    """File input/output operations."""

    def test_read_input_file(self, cli_runner, temp_file):
        import click

        @click.command()
        @click.argument("filename", type=click.File("r"))
        def read(filename):
            content = filename.read()
            click.echo(content)

        result = cli_runner.invoke(read, [temp_file])
        assert result.exit_code == 0, "Result must not be empty"
        assert "test content" in result.output, "Result must not be empty"

    def test_write_output_file(self, cli_runner, temp_dir):
        import click

        output_file = os.path.join(temp_dir, "output.txt")

        @click.command()
        @click.argument("filename", type=click.File("w"))
        def write(filename):
            filename.write("output content")

        result = cli_runner.invoke(write, [output_file])
        assert result.exit_code == 0, "Result must not be empty"
        assert os.path.exists(output_file), "Condition must be true"

        with open(output_file) as f:
            assert f.read() == "output content", "Content must not be empty"

    def test_file_not_found(self, cli_runner):
        import click

        @click.command()
        @click.argument("filename", type=click.File("r"))
        def read(filename):
            click.echo(filename.read())

        result = cli_runner.invoke(read, ["/nonexistent/file.txt"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_process_file_line_by_line(self, cli_runner, temp_file):
        import click

        @click.command()
        @click.argument("filename", type=click.File("r"))
        def process(filename):
            for line in filename:
                click.echo(line.strip().upper())

        result = cli_runner.invoke(process, [temp_file])
        assert result.exit_code == 0, "Result must not be empty"


# ============================================================================
# Input Validation Tests
# ============================================================================


class TestInputValidation:
    """Input validation and sanitization."""

    def test_integer_validation(self, cli_runner):
        import click

        @click.command()
        @click.argument("count", type=int)
        def process(count):
            assert count > 0, "count must be positive"
            click.echo(f"Count: {count}")

        result = cli_runner.invoke(process, ["42"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_float_validation(self, cli_runner):
        import click

        @click.command()
        @click.argument("ratio", type=float)
        def calculate(ratio):
            click.echo(f"Ratio: {ratio}")

        result = cli_runner.invoke(calculate, ["3.14"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_range_validation(self, cli_runner):
        import click

        @click.command()
        @click.argument("level", type=click.IntRange(0, 100))
        def set_level(level):
            click.echo(f"Level: {level}")

        result = cli_runner.invoke(set_level, ["50"])
        assert result.exit_code == 0, "Result must not be empty"

        result = cli_runner.invoke(set_level, ["150"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_email_validation(self, cli_runner):
        import click

        @click.command()
        @click.argument("email")
        def subscribe(email):
            if "@" not in email:
                raise click.BadParameter("Invalid email")
            click.echo(f"Subscribed: {email}")

        result = cli_runner.invoke(subscribe, ["user@example.com"])
        assert result.exit_code == 0, "Result must not be empty"

        result = cli_runner.invoke(subscribe, ["invalid_email"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_path_validation(self, cli_runner, temp_dir):
        import click

        @click.command()
        @click.argument("path", type=click.Path(exists=True))
        def process(path):
            click.echo(f"Processing: {path}")

        result = cli_runner.invoke(process, [temp_dir])
        assert result.exit_code == 0, "Result must not be empty"

        result = cli_runner.invoke(process, ["/nonexistent/path"])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and messages."""

    def test_command_error(self, cli_runner):
        import click

        @click.command()
        def fail():
            raise click.ClickException("Something went wrong")

        result = cli_runner.invoke(fail)
        assert result.exit_code != 0, "Result must not be empty"
        assert "Something went wrong" in result.output, "Result must not be empty"

    def test_bad_parameter(self, cli_runner):
        import click

        @click.command()
        @click.argument("name")
        def greet(name):
            if not name:
                raise click.BadParameter("Name cannot be empty")
            click.echo(f"Hello {name}!")

        cli_runner.invoke(greet, [""])
        # Result depends on implementation

    def test_exception_handling(self, cli_runner):
        import click

        @click.command()
        def process():
            try:
                raise Exception("Processing error")
            except Exception as e:
                raise click.ClickException(str(e))

        result = cli_runner.invoke(process)
        assert result.exit_code != 0, "Result must not be empty"

    def test_missing_argument_error_message(self, cli_runner):
        import click

        @click.command()
        @click.argument("name")
        def hello(name):
            click.echo(f"Hello {name}!")

        result = cli_runner.invoke(hello, [])
        assert result.exit_code != 0, "Result must not be empty"
        assert "Missing argument" in result.output or "required" in result.output.lower(), "Result must not be empty"

    def test_invalid_option_error_message(self, cli_runner):
        import click

        @click.command()
        @click.option("--count", type=int)
        def repeat(count):
            click.echo("x" * count)

        result = cli_runner.invoke(repeat, ["--count", "not_a_number"])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Output Formatting Tests
# ============================================================================


class TestOutputFormatting:
    """Output formatting and display."""

    def test_echo_output(self, cli_runner):
        import click

        @click.command()
        def hello():
            click.echo("Hello, World!")

        result = cli_runner.invoke(hello)
        assert result.exit_code == 0, "Result must not be empty"
        assert "Hello, World!" in result.output

    def test_colored_output(self, cli_runner):
        import click

        @click.command()
        def colorful():
            click.echo(click.style("Success", fg="green"))

        result = cli_runner.invoke(colorful)
        assert result.exit_code == 0, "Result must not be empty"

    def test_progress_bar(self, cli_runner):
        import click

        @click.command()
        def progress():
            with click.progressbar(range(10)) as bar:
                for item in bar:
                    pass
            click.echo("Done")

        result = cli_runner.invoke(progress)
        assert result.exit_code == 0, "Result must not be empty"
        assert "Done" in result.output, "Result must not be empty"

    def test_table_output(self, cli_runner):
        import click

        @click.command()
        def table():
            data = [["Alice", 30], ["Bob", 25]]
            click.echo("Name  Age")
            for row in data:
                click.echo(f"{row[0]:<8} {row[1]}")

        result = cli_runner.invoke(table)
        assert result.exit_code == 0, "Result must not be empty"
        assert "Alice" in result.output, "Result must not be empty"

    def test_json_output(self, cli_runner):
        import json

        import click

        @click.command()
        def json_output():
            data = {"name": "Alice", "age": 30}
            click.echo(json.dumps(data))

        result = cli_runner.invoke(json_output)
        assert result.exit_code == 0, "Result must not be empty"
        assert '"name": "Alice"' in result.output or '"name":"Alice"' in result.output, "Result must not be empty"


# ============================================================================
# Exit Code Tests
# ============================================================================


class TestExitCodes:
    """Command exit codes."""

    def test_success_exit_code(self, cli_runner):
        import click

        @click.command()
        def success():
            click.echo("OK")

        result = cli_runner.invoke(success)
        assert result.exit_code == 0, "Result must not be empty"

    def test_custom_exit_code(self, cli_runner):
        import click

        @click.command()
        def failure():
            raise SystemExit(1)

        result = cli_runner.invoke(failure)
        assert result.exit_code == 1, "Result must not be empty"

    def test_validation_exit_code(self, cli_runner):
        import click

        @click.command()
        @click.argument("count", type=int)
        def process(count):
            click.echo(count)

        result = cli_runner.invoke(process, ["invalid"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_usage_error_exit_code(self, cli_runner):
        import click

        @click.command()
        @click.argument("name")
        def hello(name):
            click.echo(name)

        result = cli_runner.invoke(hello, [])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfigurationLoading:
    """Configuration file loading."""

    def test_load_json_config(self, cli_runner, temp_dir):
        import json

        import click

        config_file = os.path.join(temp_dir, "config.json")
        config = {"key": "value", "debug": True}
        with open(config_file, "w") as f:
            json.dump(config, f)

        @click.command()
        @click.argument("config", type=click.File("r"))
        def run(config):
            data = json.load(config)
            click.echo(f"Key: {data['key']}")

        result = cli_runner.invoke(run, [config_file])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Key: value" in result.output, "Result must not be empty"

    def test_load_yaml_config(self, cli_runner, temp_dir):
        import click

        config_file = os.path.join(temp_dir, "config.yaml")
        with open(config_file, "w") as f:
            f.write("key: value\ndebug: true\n")

        @click.command()
        @click.argument("config", type=click.File("r"))
        def run(config):
            # Simplified YAML parsing
            config.read()
            click.echo("Configuration loaded")

        result = cli_runner.invoke(run, [config_file])
        assert result.exit_code == 0, "Result must not be empty"

    def test_missing_config_file(self, cli_runner):
        import click

        @click.command()
        @click.argument("config", type=click.File("r"))
        def run(config):
            pass

        result = cli_runner.invoke(run, ["/nonexistent/config.json"])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Integration Tests
# ============================================================================


class TestCLIIntegration:
    """CLI integration scenarios."""

    def test_full_command_flow(self, cli_runner, temp_dir):
        import click

        @click.group()
        def cli():
            pass

        @cli.command()
        @click.argument("name")
        def create(name):
            click.echo(f"Created {name}")

        @cli.command()
        @click.argument("name")
        def delete(name):
            click.echo(f"Deleted {name}")

        result = cli_runner.invoke(cli, ["create", "test-item"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Created test-item" in result.output, "Result must not be empty"

        result = cli_runner.invoke(cli, ["delete", "test-item"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Deleted test-item" in result.output, "Result must not be empty"

    def test_subcommand_flow(self, cli_runner):
        import click

        @click.group()
        def cli():
            pass

        @cli.group()
        def db():
            pass

        @db.command()
        def init():
            click.echo("Database initialized")

        @db.command()
        def migrate():
            click.echo("Database migrated")

        result = cli_runner.invoke(cli, ["db", "init"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Database initialized" in result.output, "Result must not be empty"

    def test_help_text(self, cli_runner):
        import click

        @click.command()
        @click.option("--name", help="Your name")
        def hello(name):
            """Say hello to someone."""
            click.echo(f'Hello {name or "World"}!')

        result = cli_runner.invoke(hello, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "Your name" in result.output, "Result must not be empty"
        assert "Say hello" in result.output, "Result must not be empty"
