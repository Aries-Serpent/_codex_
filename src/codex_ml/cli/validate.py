from __future__ import annotations

import difflib
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

try:  # Optional dependency: prefer full validation when pydantic is available
    from pydantic import ValidationError
except ModuleNotFoundError:  # pragma: no cover - pydantic missing
    ValidationError = None  # type: ignore[assignment]

try:
    from codex_ml.config_schema import TrainConfig, validate_config_file
except Exception:  # pragma: no cover - schema validation optional
    TrainConfig = None  # type: ignore[assignment]
    validate_config_file = None  # type: ignore[assignment]

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load

_ = (ArgparseJSONParser, run_cmd)

try:  # Optional dependency: prefer Typer when available
    import typer  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Typer not installed
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - namespace stub without Typer attributes
    if not hasattr(typer, "Typer"):
        typer = None  # type: ignore[assignment]


def _format_validation_error(exc: ValidationError) -> str:
    """Return a human-friendly message for schema validation errors."""

    extra_keys: list[str] = []
    messages: list[str] = []
    if ValidationError is None or exc is None:  # pragma: no cover - defensive fallback
        return str(exc)

    messages = []
    extra_keys = []
    for err in exc.errors():
        err_type = err.get("type")
        loc = err.get("loc", ())
        location = ".".join(str(part) for part in loc) if loc else "<root>"
        if err_type == "extra_forbidden":
            extra_keys.append(location)
        else:
            messages.append(f"{location}: {err.get('msg', 'invalid value')}")
    if extra_keys:
        base = f"Unrecognized config keys: {set(extra_keys)}"
        if TrainConfig is not None:
            try:
                known = set(getattr(TrainConfig, "model_fields", {}).keys())
            except Exception:  # pragma: no cover - defensive
                known = set()
            hints: list[str] = []
            for key in extra_keys:
                suggestion = difflib.get_close_matches(key, list(known), n=1)
                if suggestion:
                    hints.append(f"{key}->{suggestion[0]}")
            if hints:
                base += f"\nHint: Did you mean {', '.join(hints)}?"
        messages.insert(0, base)
    return "\n".join(messages) or str(exc)


def _fallback_validate_config(config_path: Path) -> tuple[str, int]:
    """Lightweight validation when pydantic is unavailable."""
    try:
        data = safe_load(config_path.read_text(encoding="utf-8")) or {}
    except MissingPyYAMLError as exc:  # pragma: no cover - PyYAML missing
        raise RuntimeError(
            "PyYAML is required to parse configuration files. "
            'Install it via ``pip install "PyYAML>=6.0"`` '
            f"before loading {config_path}."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("Configuration must be a mapping of keys to values")
    training = data.get("training") if isinstance(data.get("training"), dict) else data
    lr = training.get("learning_rate") or training.get("lr")
    if lr is None:
        raise ValueError("learning_rate is required")
    if float(lr) <= 0:
        raise ValueError("learning_rate must be positive")
    epochs = training.get("epochs")
    if epochs is None:
        raise ValueError("epochs is required")
    if int(epochs) <= 0:
        raise ValueError("epochs must be positive")
    model_name = training.get("model") or training.get("model_name") or data.get("model_name")
    model_name = str(model_name or "unknown")
    return model_name, int(epochs)


def _run_validation(config_path: Path, *, echo, exit_cls) -> None:
    """Shared validation routine that supports both Typer and Click frontends."""
    if ValidationError is None or validate_config_file is None:
        try:
            model_name, epochs = _fallback_validate_config(config_path)
            echo(f"OK: {config_path} is valid. model_name={model_name} epochs={epochs}")
            raise exit_cls(code=0)
        except exit_cls:  # type: ignore[misc]
            raise
        except Exception as exc:  # pragma: no cover - simple fallback
            echo(f"Invalid configuration:\n{exc}", err=True)
            raise exit_cls(code=2) from exc

    try:
        cfg = validate_config_file(config_path)
        echo(f"OK: {config_path} is valid. model_name={cfg.model_name} epochs={cfg.epochs}")
        raise exit_cls(code=0)
    except exit_cls:  # type: ignore[misc]
        raise
    except ValidationError as exc:
        echo("Invalid configuration:\n" + _format_validation_error(exc), err=True)
        raise exit_cls(code=2) from exc
    except Exception as exc:  # pragma: no cover - defensive fallback
        echo(f"Validation error: {exc}", err=True)
        raise exit_cls(code=2) from exc


if typer is not None:  # pragma: no cover - exercised via Typer CLI tests
    app = typer.Typer(help="Validate Codex training/eval configuration and exit.")

    @app.command("file")
    def validate_file(
        config_path: Annotated[
            Path,
            typer.Argument(..., exists=True, readable=True, help="YAML config to validate"),
        ],
    ) -> None:
        """Validate a YAML config file against the schema."""
        _run_validation(config_path, echo=typer.echo, exit_cls=typer.Exit)

else:
    import click

    @click.group(help="Validate Codex training/eval configuration and exit.")
    def app() -> None:
        """Entry point for the fallback Click-based validator."""

    @app.command("file")
    @click.argument(
        "config_path",
        type=click.Path(exists=True, readable=True, dir_okay=False, path_type=Path),
    )
    def validate_file_cli(config_path: Path) -> None:
        """Validate a YAML config file against the schema."""
        _run_validation(config_path, echo=click.echo, exit_cls=click.exceptions.Exit)


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover - thin wrapper
    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=sys.argv[0], args=arg_list)
        exit_code = 0
        if typer is not None:
            try:
                app(prog_name=sys.argv[0], args=arg_list, standalone_mode=False)
            except typer.Exit as exc:
                exit_code = exc.exit_code
        else:
            try:
                app.main(args=arg_list, prog_name=sys.argv[0], standalone_mode=False)
            except click.exceptions.Exit as exc:
                exit_code = exc.exit_code
        status = "ok" if exit_code == 0 else "error"
        log_event(logger, "cli.finish", prog=sys.argv[0], status=status, exit_code=exit_code)
        return exit_code


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())
