"""Offline tracking bootstrap CLI.

Initialises a local tracking workspace and emits environment exports for
MLflow and Weights & Biases so runs can remain fully offline.

Exit codes
==========

``0``
    Success
``2``
    Invalid arguments or unreachable paths
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


def _mlflow_env(root: Path) -> Dict[str, str]:
    mlruns = root.joinpath("mlruns")
    mlruns.mkdir(parents=True, exist_ok=True)
    uri = f"file:{mlruns.resolve().as_posix()}"
    return {
        "MLFLOW_TRACKING_URI": uri,
        "MLFLOW_EXPERIMENT_NAME": "codex-local",
    }


def _wandb_env(root: Path, mode: str) -> Dict[str, str]:
    wandb_root = root.joinpath("wandb")
    wandb_root.mkdir(parents=True, exist_ok=True)
    env: Dict[str, str] = {"WANDB_DIR": wandb_root.resolve().as_posix()}
    if mode == "offline":
        env["WANDB_MODE"] = "offline"
    else:
        env["WANDB_DISABLED"] = "true"
    return env


def _write_env_file(path: Path, env: Mapping[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for key, value in env.items():
            handle.write(f"{key}={value}\n")


def _print_exports(env: Mapping[str, str]) -> None:
    for key, value in env.items():
        print(f'export {key}="{value}"')


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    if args.backend not in {"mlflow", "wandb", "both"}:
        print(f"[track-bootstrap] invalid backend: {args.backend}")
        return 2
    if args.mode not in {"offline", "disabled"}:
        print(f"[track-bootstrap] invalid mode: {args.mode}")
        return 2

    payload: Dict[str, Any] = {
        "ok": True,
        "root": root.as_posix(),
        "mlflow": {"enabled": False, "uri": None, "env": None},
        "wandb": {"enabled": False, "mode": None, "offline": None, "env": None},
        "env": {},
    }

    exports: Dict[str, str] = {}
    if args.backend in {"mlflow", "both"}:
        mlflow_env = _mlflow_env(root)
        payload["mlflow"].update(
            {
                "enabled": True,
                "uri": mlflow_env.get("MLFLOW_TRACKING_URI"),
                "env": mlflow_env,
            }
        )
        exports.update(mlflow_env)
    if args.backend in {"wandb", "both"}:
        wandb_env = _wandb_env(root, args.mode)
        payload["wandb"].update(
            {
                "enabled": True,
                "mode": args.mode,
                "offline": args.mode == "offline",
                "env": wandb_env,
            }
        )
        exports.update(wandb_env)

    payload["env"] = exports

    if args.write_env:
        env_path = Path(args.write_env).expanduser().resolve()
        _write_env_file(env_path, exports)

    if args.print_exports:
        _print_exports(exports)

    print(json.dumps(payload))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex track", description="Experiment tracking utilities"
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)
    bootstrap = sub.add_parser(
        "bootstrap",
        help="Initialise local MLflow/W&B tracking roots and exports",
    )
    bootstrap.add_argument("--root", required=True, help="Tracking root directory")
    bootstrap.add_argument(
        "--backend",
        choices=["mlflow", "wandb", "both"],
        default="both",
        help="Which backends to configure",
    )
    bootstrap.add_argument(
        "--mode",
        choices=["offline", "disabled"],
        default="offline",
        help="W&B posture (offline or disabled)",
    )
    bootstrap.add_argument("--write-env", help="Optional path to emit KEY=VALUE lines")
    bootstrap.add_argument(
        "--print-exports",
        action="store_true",
        help="Echo export statements to stdout",
    )
    bootstrap.set_defaults(func=cmd_bootstrap)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
