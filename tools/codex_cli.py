#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import shutil
import subprocess  # nosec B404
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from codex_ml.config import (  # noqa: E402
    PretrainingConfig,
    RLHFConfig,
    SFTConfig,
    TrainingWeights,
    ValidationThresholds,
)
from codex_ml.pipeline import run_codex_pipeline  # noqa: E402

LOG_PATH = pathlib.Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/action_log.ndjson"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

SKIP_PRECOMMIT = os.getenv("CODEX_CLI_SKIP_PRECOMMIT") == "1"
SKIP_TESTS = os.getenv("CODEX_CLI_SKIP_TESTS") == "1"


def log(event: str, status: str, detail: str = "") -> None:
    rec = {"ts": time.time(), "event": event, "status": status, "detail": detail}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def run(cmd: list[str]) -> int:
    try:
        exe = shutil.which(cmd[0])
        if exe is None:
            raise FileNotFoundError(cmd[0])
        result = subprocess.run([exe, *cmd[1:]], check=True)  # nosec B603
        return result.returncode
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def cmd_lint() -> int:
    if SKIP_PRECOMMIT:
        rc = 0
    else:
        rc = run(["pre-commit", "run", "--all-files"])
    log("lint", "ok" if rc == 0 else "fail")
    return rc


def cmd_test() -> int:
    if SKIP_TESTS:
        rc = 0
    else:
        rc = run(["pytest", "-q"])
    log("test", "ok" if rc == 0 else "fail")
    return rc


def cmd_audit() -> int:
    rc = 0
    if not SKIP_PRECOMMIT:
        rc |= run(["pre-commit", "run", "--all-files"])
    if not SKIP_TESTS:
        rc |= run(["pytest", "-q"])
    log("audit", "ok" if rc == 0 else "fail", "pre-commit+pytest")
    return rc


def cmd_train_all(fallback: bool, print_summary: bool) -> int:
    if fallback:
        os.environ["CODEX_FALLBACK"] = "1"
    else:
        os.environ["CODEX_FALLBACK"] = "0"

    corpus = ["def add(a,b): return a+b", "SELECT * FROM t;"]
    demos = [
        {"prompt": "Write a CLI", "completion": "argparse ..."},
        {"prompt": "Gzip a folder", "completion": "tar -czf ..."},
    ]
    pairwise_prefs = [
        ("sum", "def add(a,b): return a+b", "def add(a,b): return a-b", 1),
        ("sql", "SELECT * FROM users;", "DROP TABLE users;", 1),
    ]

    try:
        summary = run_codex_pipeline(
            corpus=corpus,
            demos=demos,
            pairwise_prefs=pairwise_prefs,
            weights=TrainingWeights(alpha=1.0, beta=1.2, gamma=0.05),
            pre_cfg=PretrainingConfig(model_size="placeholder", context_length=4096),
            sft_cfg=SFTConfig(batch_size=32, learning_rate=5e-6, epochs=3),
            rlhf_cfg=RLHFConfig(algorithm="PPO", kl_penalty=0.1, ppo_epochs=4),
            val_t=ValidationThresholds(
                syntax_ok=0.98, logic_ok=0.92, security_ok=1.0, perf_ok=0.85
            ),
            synth_prompts=None,
        )
    except Exception as exc:  # pragma: no cover - defensive
        log("train-all", "fail", str(exc))
        return 1

    if print_summary:
        print(json.dumps(summary, indent=2))

    log("train-all", "ok")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser("codex-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lint")
    sub.add_parser("test")
    sub.add_parser("audit")
    p_train = sub.add_parser("train-all")
    p_train.add_argument(
        "--fallback",
        dest="fallback",
        action="store_true",
        default=True,
        help="Enable fallback logic via CODEX_FALLBACK (default: enabled).",
    )
    p_train.add_argument(
        "--no-fallback",
        dest="fallback",
        action="store_false",
        help="Disable fallback logic via CODEX_FALLBACK.",
    )
    p_train.add_argument(
        "--print-summary",
        dest="print_summary",
        action="store_true",
        default=True,
        help="Print JSON summary for dashboards/CI.",
    )
    p_train.add_argument(
        "--no-print-summary",
        dest="print_summary",
        action="store_false",
        help="Suppress JSON summary output.",
    )
    args = parser.parse_args()
    if args.cmd == "lint":
        sys.exit(cmd_lint())
    if args.cmd == "test":
        sys.exit(cmd_test())
    if args.cmd == "audit":
        sys.exit(cmd_audit())
    if args.cmd == "train-all":
        sys.exit(cmd_train_all(args.fallback, args.print_summary))


if __name__ == "__main__":
    main()
