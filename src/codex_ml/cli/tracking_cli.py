"""Tracking bootstrap CLI (offline-friendly).

Initializes local MLflow and/or W&B in offline/disabled modes without network I/O.
All optional deps are import-guarded.

Usage:
  python -m codex_ml.cli tracking bootstrap --mlflow --wandb \
    --mlflow-uri file:./mlruns --project codex-demo --mode offline
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any


def _enable_mlflow(uri: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"enabled": False, "tracking_uri": uri or "mlruns"}
    try:
        import mlflow

        if uri:
            os.environ["MLFLOW_TRACKING_URI"] = uri
            try:
                mlflow.set_tracking_uri(uri)  # type: ignore[attr-defined]
            except Exception:
                pass
        result["enabled"] = True
        result["tracking_uri"] = os.environ.get("MLFLOW_TRACKING_URI") or result["tracking_uri"]
    except Exception as exc:  # pragma: no cover - depends on optional dep
        result["warning"] = f"mlflow not available: {exc!r}"
    return result


def _enable_wandb(project: str | None, mode: str) -> dict[str, Any]:
    result: dict[str, Any] = {"enabled": False}
    if mode:
        os.environ["WANDB_MODE"] = mode
    try:
        import wandb

        run = wandb.init(
            project=project or "codex",
            mode=os.environ.get("WANDB_MODE", "online"),
        )
        result["enabled"] = True
        result["mode"] = getattr(
            run.settings,
            "mode",
            os.environ.get("WANDB_MODE", "online"),
        )
        result["offline"] = getattr(run.settings, "_offline", False)
        run.finish()
    except Exception as exc:  # pragma: no cover - depends on optional dep
        result["warning"] = f"wandb not available: {exc!r}"
    return result


def _mk_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex tracking",
        description="Tracking bootstrap (offline)",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)
    bootstrap = sub.add_parser(
        "bootstrap",
        help="Initialize offline-friendly tracking",
    )
    bootstrap.add_argument(
        "--mlflow",
        action="store_true",
        help="Enable MLflow with local file store",
    )
    bootstrap.add_argument(
        "--mlflow-uri",
        default="file:./mlruns",
        help="Tracking URI (e.g., file:./mlruns)",
    )
    bootstrap.add_argument("--wandb", action="store_true", help="Enable Weights & Biases")
    bootstrap.add_argument("--project", help="W&B project name (default: codex)")
    bootstrap.add_argument(
        "--mode",
        default="offline",
        choices=["online", "offline", "disabled"],
        help="W&B mode",
    )
    bootstrap.set_defaults(func=_cmd_bootstrap)
    return parser


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {"ok": True}
    if args.mlflow:
        payload["mlflow"] = _enable_mlflow(args.mlflow_uri)
    if args.wandb:
        payload["wandb"] = _enable_wandb(args.project, args.mode)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _mk_parser()
    namespace = parser.parse_args(argv)
    return int(namespace.func(namespace))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
