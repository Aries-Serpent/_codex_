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
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import typer

app = typer.Typer(help="Evaluation loop commands (reference).")


def _load_config(path: Path) -> Dict[str, Any]:
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
        except ImportError:
            import tomli as tomllib  # type: ignore
        return tomllib.loads(text)
    typer.echo("Unsupported config format (use .json or .toml)", err=True)
    raise typer.Exit(code=2)


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
):
    """
    Run evaluation with provided config. Produces NDJSON logs + optional JSON summary.
    """
    cfg = _load_config(config)
    # Lazy import evaluation loop
    from codex_ml.evaluation.loop import evaluate_epoch
    from codex_ml.logging.registry import build_loggers  # type: ignore

    # Minimal synthetic components derived from config (placeholder)
    model = cfg.get("_model_obj")
    dataloader = cfg.get("_eval_dataloader")
    criterion = cfg.get("_criterion")

    if model is None or dataloader is None or criterion is None:
        typer.echo("Config must inject _model_obj, _eval_dataloader, _criterion for reference CLI.", err=True)
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

    summary = evaluate_epoch(
        model=model,
        dataloader=dataloader,
        criterion=criterion,
        device=device,
        metrics=cfg.get("evaluation", {}).get("metrics"),
        logger=loggers,
        max_batches=max_batches,
        seed=cfg.get("seed"),
        deterministic=deterministic,
    )

    if json_output:
        typer.echo(json.dumps(summary, indent=2))
    else:
        typer.echo(
            f"Eval complete | loss={summary['loss']:.4f} | count={summary['count']} | metrics={summary['metrics']}"
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
    lines = [json.loads(l) for l in input.read_text().splitlines() if l.strip()]
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
        cmp_lines = [json.loads(l) for l in compare.read_text().splitlines() if l.strip()]
        cmp_epochs = [r for r in cmp_lines if r.get("type") == "epoch"]
        if not cmp_epochs:
            typer.echo("Compare file has no epoch records.", err=True)
            raise typer.Exit(code=3)
        other = cmp_epochs[-1]
        deterministic = json.dumps(out, sort_keys=True) == json.dumps(
            {
                "loss": other.get("loss"),
                "count": other.get("count"),
                "metrics": other.get("metrics", {}),
                "batches": other.get("batches"),
                "duration_sec": other.get("duration_sec"),
            },
            sort_keys=True,
        )
        out["determinism_match"] = deterministic
        if not deterministic:
            typer.echo("Determinism mismatch detected.", err=True)
            raise typer.Exit(code=4)

    if json_output:
        typer.echo(json.dumps(out, indent=2))
    else:
        typer.echo(f"Report: loss={out['loss']:.4f} count={out['count']} metrics={out['metrics']}")


if __name__ == "__main__":  # pragma: no cover
    app()