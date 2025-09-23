from __future__ import annotations

import difflib
from pathlib import Path

import typer
from pydantic import ValidationError

from codex_ml.config_schema import TrainConfig, validate_config_file


def _format_validation_error(exc: ValidationError) -> str:
    """Return a human-friendly message for schema validation errors."""

    extra_keys: list[str] = []
    messages: list[str] = []
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
        known = set(TrainConfig.model_fields.keys())
        hints: list[str] = []
        for key in extra_keys:
            suggestion = difflib.get_close_matches(key, known, n=1)
            if suggestion:
                hints.append(f"{key}->{suggestion[0]}")
        if hints:
            base += f"\nHint: Did you mean {', '.join(hints)}?"
        messages.insert(0, base)
    return "\n".join(messages) or str(exc)


app = typer.Typer(help="Validate Codex training/eval configuration and exit.")


@app.command("file")
def validate_file(
    config_path: Path = typer.Argument(
        ..., exists=True, readable=True, help="YAML config to validate"
    ),
) -> None:
    """
    Validate a YAML config file against the schema. Exit with code 0 on success, 2 on failure.
    """

    try:
        cfg = validate_config_file(config_path)
        typer.echo(f"OK: {config_path} is valid. model_name={cfg.model_name} epochs={cfg.epochs}")
        raise typer.Exit(code=0)
    except ValidationError as e:
        typer.echo("Invalid configuration:\n" + _format_validation_error(e), err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(f"Validation error: {e}", err=True)
        raise typer.Exit(code=2)


def main():
    app()


if __name__ == "__main__":
    main()
