"""
Typer-based CLI for evaluation operations.

Console script entry point suggestion: codex-eval
Commands:
    codex-eval run --config path [--json]
    codex-eval report --input metrics.ndjson [--json]

Exit codes:
    0 success
    2 invalid arguments/config
    3 runtime error
    4 determinism mismatch (report comparison)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import importlib  # noqa: E402
import json  # noqa: E402
from collections.abc import Callable, Iterable, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

import typer  # noqa: E402

app = typer.Typer(help="Evaluation loop commands (reference).")


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        typer.echo(f"Config not found: {path}", err=True)
        raise typer.Exit(code=2)
    text = path.read_text()
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix == ".toml":
        # Proper fallback for tomllib (Python 3.11+) vs tomli (Python <3.11)
        try:
            import tomllib
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            import tomli as tomllib  # type: ignore
        return tomllib.loads(text)
    typer.echo("Unsupported config format (use .json or .toml)", err=True)
    raise typer.Exit(code=2)


def _import_string(spec: str) -> Callable[..., Iterable[object]]:
    if ":" in spec:
        module_name, attr = spec.split(":", 1)
    else:
        module_name, attr = spec.rsplit(".", 1)
    module = importlib.import_module(module_name)
    target = getattr(module, attr)
    if not callable(target):
        raise TypeError(f"Resolved object '{spec}' is not callable")
    return target


def _resolve_metrics(cfg: dict[str, Any], names: Sequence[str] | None) -> dict[str, Callable]:
    from codex_ml.metrics.registry import get as get_metric

    evaluation_cfg = cfg.get("evaluation", {})
    configured = evaluation_cfg.get("metrics")

    candidates: Iterable[str] | dict[str, Any]
    candidates = list(names) if names else configured or []

    resolved: dict[str, Callable] = {}
    if isinstance(candidates, dict):
        for alias, value in candidates.items():
            if callable(value):
                resolved[alias] = value
            elif isinstance(value, str):
                resolved[alias] = get_metric(value)
            else:
                resolved[alias] = get_metric(alias)
    else:
        for name in candidates:
            resolved[str(name)] = get_metric(str(name))
    return resolved


def _resolve_transform(
    cfg: dict[str, Any], override: Optional[str], key: str
) -> Optional[Callable]:
    evaluation_cfg = cfg.get("evaluation", {})
    spec = override or evaluation_cfg.get(key)
    if spec is None:
        return None
    if callable(spec):
        return spec
    if isinstance(spec, str):
        return _import_string(spec)
    raise TypeError(f"Unsupported transform specification for {key}: {spec!r}")


@app.command("run")
def run_command(
    config: Path = typer.Option(..., "--config", help="Experiment config (.json/.toml)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON summary to stdout"),
    device: str = typer.Option("cpu", "--device", help="Device (cpu|cuda)"),
    max_batches: Optional[int] = typer.Option(
        None, "--max-batches", help="Limit number of batches for quick tests"
    ),
    deterministic: bool = typer.Option(
        False, "--deterministic", help="Enable deterministic mode for reproducibility"
    ),
    sys_metrics: bool = typer.Option(
        False, "--sys-metrics", help="Enable system metrics collection (future)"
    ),
    metric: Optional[list[str]] = typer.Option(
        None,
        "--metric",
        help="Metric name (repeat for multiple). Defaults to config-defined metrics.",
    ),
    prediction_transform: Optional[str] = typer.Option(
        None,
        "--prediction-transform",
        help="Optional dotted path for prediction post-processing callable.",
    ),
    target_transform: Optional[str] = typer.Option(
        None,
        "--target-transform",
        help="Optional dotted path for target post-processing callable.",
    ),
):
    """
    Run evaluation with provided config. Produces NDJSON logs + optional JSON summary.
    """
    cfg = _load_config(config)
    # Lazy import evaluation loop
    from codex_ml.evaluation.loop import evaluate_epoch
    from codex_ml.logging.registry import build_loggers

    # Minimal synthetic components derived from config (placeholder)
    model = cfg.get("_model_obj")
    dataloader = cfg.get("_eval_dataloader")
    criterion = cfg.get("_criterion")

    if model is None or dataloader is None or criterion is None:
        typer.echo(
            "Config must inject _model_obj, _eval_dataloader, _criterion for reference CLI.",
            err=True,
        )
        raise typer.Exit(code=2)

    log_dir = Path("runs/eval")
    log_dir.mkdir(parents=True, exist_ok=True)

    loggers = build_loggers(
        {
            "output_dir": str(log_dir),
            "use_mlflow": cfg.get("logging", {}).get("mlflow", False),
            "sys_metrics": sys_metrics,
        }
    )

    metrics_mapping = _resolve_metrics(cfg, metric)
    prediction_transform_fn = _resolve_transform(cfg, prediction_transform, "prediction_transform")
    target_transform_fn = _resolve_transform(cfg, target_transform, "target_transform")

    summary = evaluate_epoch(
        model=model,
        dataloader=dataloader,
        criterion=criterion,
        device=device,
        metrics=metrics_mapping or None,
        logger=loggers,
        max_batches=max_batches,
        seed=cfg.get("seed"),
        deterministic=deterministic,
        prediction_transform=prediction_transform_fn,
        target_transform=target_transform_fn,
    )

    if json_output:
        typer.echo(json.dumps(summary, indent=2))
    else:
        typer.echo(
            f"Eval complete | loss={summary['loss']:.4f} | count={summary['count']} | metrics={summary['metrics']}"  # noqa: E501
        )


@app.command("report")
def report_command(
    input: Path = typer.Option(..., "--input", help="Path to metrics.ndjson"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON aggregated summary"),
    compare: Optional[Path] = typer.Option(
        None, "--compare", help="Optional second metrics.ndjson to compare determinism"
    ),
):
    """
    Aggregate NDJSON evaluation metrics; optional determinism comparison against second run.
    """
    if not input.exists():
        typer.echo(f"Input log not found: {input}", err=True)
        raise typer.Exit(code=2)
    lines = [json.loads(line) for line in input.read_text().splitlines() if line.strip()]
    epoch_records = [r for r in lines if r.get("type") == "epoch"]
    if not epoch_records:
        typer.echo("No epoch records found.", err=True)
        raise typer.Exit(code=3)
    # Use last epoch record for summary
    summary = epoch_records[-1]
    out = {
        "loss": summary.get("loss"),
        "count": summary.get("count"),
        "metrics": summary.get("metrics", {}),
        "batches": summary.get("batches"),
        "duration_sec": summary.get("duration_sec"),
    }
    if compare:
        if not compare.exists():
            typer.echo(f"Compare file not found: {compare}", err=True)
            raise typer.Exit(code=2)
        cmp_lines = [json.loads(line) for line in compare.read_text().splitlines() if line.strip()]
        cmp_epochs = [r for r in cmp_lines if r.get("type") == "epoch"]
        if not cmp_epochs:
            typer.echo("Compare file has no epoch records.", err=True)
            raise typer.Exit(code=3)
        other = cmp_epochs[-1]
        # Compare only deterministic fields (exclude duration_sec which varies by runtime)
        current_deterministic = {
            "loss": out.get("loss"),
            "count": out.get("count"),
            "metrics": out.get("metrics", {}),
            "batches": out.get("batches"),
        }
        other_deterministic = {
            "loss": other.get("loss"),
            "count": other.get("count"),
            "metrics": other.get("metrics", {}),
            "batches": other.get("batches"),
        }
        deterministic = json.dumps(current_deterministic, sort_keys=True) == json.dumps(
            other_deterministic,
            sort_keys=True,
        )
        out["determinism_match"] = deterministic

    if json_output:
        typer.echo(json.dumps(out, indent=2))
    else:
        typer.echo(f"Report: loss={out['loss']:.4f} count={out['count']} metrics={out['metrics']}")

    # Check determinism after output so JSON is still returned
    if compare and not out["determinism_match"]:
        typer.echo("Determinism mismatch detected.", err=True)
        raise typer.Exit(code=4)


if __name__ == "__main__":  # pragma: no cover
    app()
