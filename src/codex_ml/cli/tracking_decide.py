"""Inspect the MLflow tracking guard decision from the command line."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import asdict
from typing import Dict, Iterable, Iterator, Mapping, Sequence

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)
from codex_ml.tracking.mlflow_guard import GuardDecision, bootstrap_offline_tracking_decision

_ = (ArgparseJSONParser, run_cmd)

try:  # Optional dependency used for the public CLI.
    import typer
except ModuleNotFoundError:  # pragma: no cover - Typer not installed
    typer = None  # type: ignore[assignment]
else:  # pragma: no cover - namespace stub without Typer attributes
    if not hasattr(typer, "Typer"):
        typer = None  # type: ignore[assignment]


def _parse_env_overrides(values: Sequence[str]) -> Dict[str, str | None]:
    overrides: Dict[str, str | None] = {}
    for raw in values:
        if "=" not in raw:
            overrides[raw] = None
            continue
        key, value = raw.split("=", 1)
        overrides[key.strip()] = value if value != "" else None
    return overrides


@contextmanager
def _patched_environ(updates: Mapping[str, str | None]) -> Iterator[None]:
    original: Dict[str, str] = {}
    removed: set[str] = set()
    try:
        for key, value in updates.items():
            if key in os.environ:
                original[key] = os.environ[key]
            else:
                removed.add(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key in updates:
            if key in original:
                os.environ[key] = original[key]
            elif key in removed and key in os.environ:
                os.environ.pop(key)
            elif key not in original and key not in removed and key in os.environ:
                os.environ.pop(key)


def decide(
    uri: str | None = None,
    *,
    force: bool = False,
    env_overrides: Mapping[str, str | None] | None = None,
) -> GuardDecision:
    """Return the guard decision after applying ``env_overrides`` and ``uri``."""

    overrides: Dict[str, str | None] = dict(env_overrides or {})
    if uri is not None:
        overrides["MLFLOW_TRACKING_URI"] = uri
    with _patched_environ(overrides):
        decision = bootstrap_offline_tracking_decision(force=force, requested_uri=uri)
    return decision


if typer is not None:  # pragma: no cover - exercised via CLI tests
    app = typer.Typer(help="Evaluate MLflow tracking guard decisions.")

    @app.command("decide")
    def decide_cmd(
        uri: str | None = typer.Option(
            None,
            "--uri",
            help="Requested tracking URI (defaults to environment value).",
        ),
        env: Iterable[str] = typer.Option(
            None,
            "--env",
            help="Additional environment overrides as KEY=VALUE pairs.",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            help="Force guard evaluation even if environment already configured.",
        ),
        pretty: bool = typer.Option(
            True,
            "--pretty/--no-pretty",
            help="Pretty-print the decision JSON.",
        ),
    ) -> None:
        """Print the guard decision as JSON."""

        env_overrides = _parse_env_overrides(list(env or ()))
        try:
            decision = decide(uri, force=force, env_overrides=env_overrides)
        except Exception as exc:  # pragma: no cover - defensive fallback
            typer.echo(f"error: {exc}", err=True)
            raise typer.Exit(code=1) from exc
        payload = asdict(decision)
        text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
        typer.echo(text)

else:  # pragma: no cover - Typer missing
    app = None  # type: ignore[assignment]


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``python -m codex_ml.cli.tracking_decide``."""

    logger = init_json_logging()
    arg_list = list(argv) if argv is not None else []
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog="tracking-decide", args=arg_list)
        if typer is None:
            log_event(logger, "cli.finish", prog="tracking-decide", status="error", exit_code=1)
            raise SystemExit(
                "Typer is required to use codex_ml.cli.tracking_decide; install it with `pip install typer`."
            )
        try:
            app(prog_name="codex-tracking", args=arg_list, standalone_mode=False)
        except typer.Exit as exc:  # type: ignore[attr-defined]
            exit_code = int(exc.exit_code or 0)
        else:
            exit_code = 0
        status = "ok" if exit_code == 0 else "error"
        log_event(logger, "cli.finish", prog="tracking-decide", status=status, exit_code=exit_code)
        return exit_code


__all__ = ["app", "decide", "main"]
