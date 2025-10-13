"""Validate Codex checkpoint directories and metadata."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Annotated, Any

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = (ArgparseJSONParser, run_cmd)

try:  # Optional dependency for CLI ergonomics.
    import typer
except ModuleNotFoundError:  # pragma: no cover - Typer not installed
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - namespace stub without Typer attributes
    if not hasattr(typer, "Typer"):
        typer = None  # type: ignore[assignment]


class CheckpointValidationError(RuntimeError):
    """Raised when a checkpoint fails validation."""


def _load_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - surfaced via CLI
        raise CheckpointValidationError(f"missing metadata: {path}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - surfaced via CLI
        raise CheckpointValidationError(f"metadata is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckpointValidationError(f"metadata must be a JSON object: {path}")
    return data


def _detect_state_file(directory: Path) -> Path:
    for candidate in ("state.pt", "weights.pt"):
        state_path = directory / candidate
        if state_path.exists():
            return state_path
    raise CheckpointValidationError(f"missing checkpoint payload in {directory}")


def validate_checkpoint(
    path: Path,
    *,
    expect_schema: str | None = None,
    require_digest: bool = True,
) -> Mapping[str, Any]:
    """Validate ``path`` as a checkpoint directory or metadata file."""

    target = Path(path)
    if target.is_dir():
        state_file = _detect_state_file(target)
        meta_path = target / "metadata.json"
        meta = _load_metadata(meta_path)
        digest = meta.get("digest_sha256")
        sha_path = target / "state.sha256"
        if require_digest and digest:
            try:
                recorded = sha_path.read_text(encoding="utf-8").strip()
            except FileNotFoundError as exc:
                raise CheckpointValidationError(f"missing digest file: {sha_path}") from exc
            if recorded != digest:
                raise CheckpointValidationError(
                    f"state.sha256 mismatch: expected {digest!r} but found {recorded!r}"
                )
        if expect_schema is not None:
            schema = str(meta.get("schema_version", ""))
            if schema != expect_schema:
                raise CheckpointValidationError(
                    f"schema mismatch: expected {expect_schema!r} but found {schema!r}"
                )
        return meta | {"checkpoint": str(state_file)}

    if target.is_file():
        if target.name.endswith(".json"):
            meta = _load_metadata(target)
            if expect_schema is not None:
                schema = str(meta.get("schema_version", ""))
                if schema != expect_schema:
                    raise CheckpointValidationError(
                        f"schema mismatch: expected {expect_schema!r} but found {schema!r}"
                    )
            return meta
        raise CheckpointValidationError(f"unsupported file type: {target}")

    raise CheckpointValidationError(f"path does not exist: {target}")


if typer is not None:  # pragma: no cover - exercised via CLI tests
    app = typer.Typer(help="Validate Codex checkpoint directories and manifests.")

    @app.command("validate")
    def validate_cmd(
        path: Annotated[
            Path,
            typer.Option(
                ...,
                "--path",
                "-p",
                exists=True,
                help="Checkpoint path to validate.",
            ),
        ],
        schema: Annotated[
            str | None,
            typer.Option(
                None,
                "--schema",
                help="Expected schema version (e.g. '2').",
            ),
        ] = None,
        show: Annotated[
            bool,
            typer.Option(
                False,
                "--show",
                help="Print metadata JSON on success.",
            ),
        ] = False,
    ) -> None:
        try:
            info = validate_checkpoint(path, expect_schema=schema)
        except CheckpointValidationError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=2) from exc
        if show:
            typer.echo(json.dumps(dict(info), indent=2, sort_keys=True))
        else:
            typer.echo(f"OK: {path}")

else:  # pragma: no cover - Typer missing
    app = None  # type: ignore[assignment]


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``python -m codex_ml.cli.checkpoint_validate``."""

    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else []
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog="checkpoint-validate", args=arg_list)
        if typer is None:
            log_event(
                logger,
                "cli.finish",
                prog="checkpoint-validate",
                status="error",
                exit_code=1,
            )
            raise SystemExit(
                "Typer is required to use codex_ml.cli.checkpoint_validate; install it with "
                "`pip install typer`."
            )
        try:
            app(prog_name="codex-checkpoint", args=arg_list, standalone_mode=False)
        except typer.Exit as exc:  # type: ignore[attr-defined]
            exit_code = int(exc.exit_code or 0)
        else:
            exit_code = 0
        status = "ok" if exit_code == 0 else "error"
        log_event(
            logger, "cli.finish", prog="checkpoint-validate", status=status, exit_code=exit_code
        )
        return exit_code


__all__ = ["CheckpointValidationError", "app", "main", "validate_checkpoint"]
