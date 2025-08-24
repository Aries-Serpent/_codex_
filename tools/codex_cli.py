#!/usr/bin/env python3
"""Utility CLI for linting, testing, and training pipelines."""

import json
import os
import pathlib
import shutil
import subprocess  # nosec B404
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import click  # noqa: E402

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
    """Append an event record to the log file."""

    rec = {"ts": time.time(), "event": event, "status": status, "detail": detail}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def run(cmd: list[str]) -> int:
    """Run a command and return its exit code."""

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
    """Run pre-commit hooks."""

    if SKIP_PRECOMMIT:
        rc = 0
    else:
        rc = run(["pre-commit", "run", "--all-files"])
    log("lint", "ok" if rc == 0 else "fail")
    return rc


def cmd_test() -> int:
    """Run tests."""

    if SKIP_TESTS:
        rc = 0
    else:
        rc = run(["pytest", "-q"])
    log("test", "ok" if rc == 0 else "fail")
    return rc


def cmd_audit() -> int:
    """Run lint and tests."""

    rc = 0
    if not SKIP_PRECOMMIT:
        rc |= run(["pre-commit", "run", "--all-files"])
    if not SKIP_TESTS:
        rc |= run(["pytest", "-q"])
    log("audit", "ok" if rc == 0 else "fail", "pre-commit+pytest")
    return rc


@click.group()
def codex() -> None:
    """Codex utility CLI."""


@codex.command("lint")
def lint_cmd() -> None:
    """Run pre-commit hooks."""

    raise SystemExit(cmd_lint())


@codex.command("test")
def test_cmd() -> None:
    """Run tests."""

    raise SystemExit(cmd_test())


@codex.command("audit")
def audit_cmd() -> None:
    """Run lint and tests."""

    raise SystemExit(cmd_audit())


@click.command("train-all")
@click.option(
    "--fallback/--no-fallback",
    default=True,
    help="Enable fallback logic via CODEX_FALLBACK (default: enabled).",
)
@click.option(
    "--print-summary",
    is_flag=True,
    default=True,
    help="Print JSON summary for dashboards/CI.",
)
def train_all(fallback: bool, print_summary: bool) -> None:
    """Run the full training pipeline with optional fallbacks."""

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

    if print_summary:
        click.echo(json.dumps(summary, indent=2))


codex.add_command(train_all)


if __name__ == "__main__":
    codex()
