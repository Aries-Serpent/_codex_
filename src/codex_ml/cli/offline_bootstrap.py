from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from codex_ml.tracking.offline import decide_offline, export_env_lines

_ORIGINAL_MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI_REQUESTED") or os.environ.get(
    "MLFLOW_TRACKING_URI"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap local/offline tracking safely.")
    parser.add_argument(
        "--mlruns-dir",
        type=Path,
        default=None,
        help="Directory for local MLflow store (default: ./mlruns)",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Permit remote tracking URIs if already set",
    )
    parser.add_argument(
        "--write",
        type=Path,
        default=None,
        help="Write export lines to this file",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write the decision as JSON",
    )
    parser.add_argument(
        "--print",
        dest="print_",
        action="store_true",
        help="Print export lines to stdout",
    )
    parser.add_argument(
        "--no-print",
        dest="print_",
        action="store_false",
        help="Do not print export lines to stdout",
    )
    parser.set_defaults(print_=True)
    parser.add_argument(
        "command",
        choices=["env"],
        nargs="?",
        default="env",
        help="Command to run (default: env)",
    )
    return parser


def cmd_env(
    *,
    mlruns_dir: Optional[Path],
    allow_remote: bool,
    write: Optional[Path],
    print_: bool,
    json_out: Optional[Path],
) -> None:
    prefer_offline = not allow_remote
    if allow_remote and _ORIGINAL_MLFLOW_TRACKING_URI:
        os.environ["MLFLOW_TRACKING_URI"] = _ORIGINAL_MLFLOW_TRACKING_URI
    decision = decide_offline(
        prefer_offline=prefer_offline, allow_remote=allow_remote, mlruns_dir=mlruns_dir
    )
    exports = export_env_lines(decision)

    if print_:
        print(exports, end="")

    if write:
        write.parent.mkdir(parents=True, exist_ok=True)
        write.write_text(exports, encoding="utf-8")

    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(asdict(decision), indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "env":
        cmd_env(
            mlruns_dir=args.mlruns_dir,
            allow_remote=args.allow_remote,
            write=args.write,
            print_=args.print_,
            json_out=args.json_out,
        )


if __name__ == "__main__":  # pragma: no cover
    main()
