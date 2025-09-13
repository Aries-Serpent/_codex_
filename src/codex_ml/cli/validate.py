from __future__ import annotations

from pathlib import Path

import typer

from codex_ml.config_schema import ValidationError, validate_config_file  # type: ignore

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
        typer.echo("Invalid configuration:\n" + str(e), err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(f"Validation error: {e}", err=True)
        raise typer.Exit(code=2)


def main():
    app()


if __name__ == "__main__":
    main()
