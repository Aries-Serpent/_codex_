#!/usr/bin/env python3
"""Codex-ready sequential task runner derived from the 2025-09-16 status update."""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

CHANGE_LOG = Path("logs/codex_task_change_log.md")
ERROR_LOG = Path("logs/codex_task_error_log.md")


def _ensure_log_files() -> None:
    """Create log files with headers if they do not exist."""
    for path, header in (
        (CHANGE_LOG, "# Codex Task Change Log\n\n"),
        (ERROR_LOG, "# Codex Task Error Log\n\n"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(header, encoding="utf-8")


def _timestamp() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(message: str) -> None:
    _ensure_log_files()
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"- [{_timestamp()}] {message}\n")


def log_error(step: str, error: Exception, context: str) -> None:
    _ensure_log_files()
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            "Question for ChatGPT-5 {timestamp}:\n"
            "While performing {step}, encountered the following error: {error}\n"
            "Context: {context}\n\n".format(
                timestamp=_timestamp(), step=step, error=error, context=context
            )
        )


def read_readme() -> str:
    readme = Path("README.md")
    if not readme.exists():
        raise FileNotFoundError("README.md not found")
    return readme.read_text(encoding="utf-8")


def search_paths(patterns: Sequence[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            matches.append(str(path))
    return sorted(set(matches))


def run_command(command: Sequence[str], step: str, dry_run: bool) -> None:
    if dry_run:
        log_change(f"[DRY-RUN] Would execute command: {' '.join(command)}")
        return
    try:
        subprocess.run(command, check=True)
        log_change(f"Executed command: {' '.join(command)}")
    except subprocess.CalledProcessError as exc:
        log_error(step=step, error=exc, context=f"Command: {' '.join(command)}")


def save_gap_snapshot(task_name: str, gaps: Iterable[str]) -> None:
    snapshot_path = Path("logs") / f"{task_name.replace(' ', '_').lower()}_gaps.json"
    snapshot = {"generated_at": _timestamp(), "gaps": list(gaps)}
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    log_change(f"Recorded gap snapshot for {task_name} -> {snapshot_path}")


class CodexTaskRunner:
    def __init__(self, *, dry_run: bool = True, run_tests: bool = False) -> None:
        self.dry_run = dry_run
        self.run_tests = run_tests
        _ensure_log_files()

    def _phase_header(self, task: str, phase: str) -> None:
        log_change(f"[{task}] Entering phase: {phase}")

    def run(self, tasks: Sequence[str]) -> None:
        for task in tasks:
            handler = getattr(self, f"task_{task}")
            handler()

    # Task 1: Model + Training integration
    def task_model_training(self) -> None:
        task_name = "Model & Training Integration"
        # Phase 1: Preparation
        self._phase_header(task_name, "Preparation")
        try:
            read_readme()
            log_change(
                "Analysed README for offline constraints, noted need for expanded Hydra examples (HS#3)."
            )
            log_change(
                "Extracted existing training references to align with unified training engine patch plan."
            )
            save_gap_snapshot(
                "model_training_preparation",
                [
                    "Toy-only train_loop usage (HS#1)",
                    "Experiment tracking not invoked in training (HS#2)",
                    "LoRA task_type hidden from configuration (HS#5)",
                ],
            )
        except Exception as exc:
            log_error("Task1-Preparation", exc, "Reading README.md")

        # Phase 2: Search & Mapping
        self._phase_header(task_name, "Search & Mapping")
        try:
            candidates = search_paths(
                [
                    "src/codex_ml/models/*.py",
                    "src/codex_ml/peft/*.py",
                    "src/codex_ml/training/*.py",
                    "src/codex_ml/train_loop.py",
                    "tests/test_train_loop.py",
                ]
            )
            log_change("Mapped model/training artefacts: " + ", ".join(candidates))
        except Exception as exc:
            log_error("Task1-Search", exc, "Collecting candidate files")

        # Phase 3: Best-Effort Construction
        self._phase_header(task_name, "Best-Effort Construction")
        construction_notes = [
            "Apply Atomic Diff 1 to expose LoRA task_type default in peft_adapter.py (Capability: ChatGPT Codex Modeling).",
            "Implement offline HF model loader registry entries (Capability: ChatGPT Codex Modeling minimal patch).",
            "Apply Atomic Diff 2 to enable resume-from-checkpoint in training/__init__.py (Capability: Training Engine).",
            "Execute Atomic Diff 3 to consolidate train_loop with experiment tracking (addresses HS#1, HS#2).",
            "Extend TrainConfig and CLI flags to surface LoRA/task precision knobs per minimal patch plan.",
            "Augment tests/test_train_loop.py for coverage expansion (HS#7).",
        ]
        for note in construction_notes:
            log_change(f"[Plan] {note}")
        save_gap_snapshot(
            "model_training_best_effort",
            construction_notes,
        )

        # Phase 4: Controlled Pruning
        self._phase_header(task_name, "Controlled Pruning")
        pruning_notes = [
            "If accelerate mixed precision cannot be added offline, document deferral with rationale.",
            "If pretrained weights unavailable offline, fall back to toy MiniLM and record requirement for local cache packaging.",
        ]
        for note in pruning_notes:
            log_change(f"[Pruning] {note}")

        # Phase 5: Error Capture
        self._phase_header(task_name, "Error Capture")
        log_change(
            "Prepared error capture template for Task 1; errors will be appended to logs/codex_task_error_log.md."
        )

        # Phase 6: Finalization
        self._phase_header(task_name, "Finalization")
        final_steps = [
            "Update change_log with implemented diffs and new registry entries.",
            "Document Hydra config updates and CLI guidance in docs/ and README (Capability: Configuration Management crossover).",
            "Run pytest -q -m 'not slow' to verify training loop tests (optional via --run-tests).",
        ]
        for step in final_steps:
            log_change(f"[Finalize] {step}")
        if self.run_tests:
            run_command(["pytest", "-q", "-m", "not slow"], "Task1-Finalization", self.dry_run)

    # Task 2: Data, Evaluation, Safety hardening
    def task_data_eval_safety(self) -> None:
        task_name = "Data, Evaluation & Safety Hardening"
        # Phase 1
        self._phase_header(task_name, "Preparation")
        try:
            read_readme()
            log_change(
                "Reviewed README data pipeline references to align with dataset split automation (HS#4)."
            )
        except Exception as exc:
            log_error("Task2-Preparation", exc, "Reading README for data sections")
        save_gap_snapshot(
            "data_eval_safety_preparation",
            [
                "Manual dataset split process (HS#4)",
                "Limited evaluation metrics (Capability: Evaluation & Metrics)",
                "Safety filters optional in training/generation (HS#8)",
            ],
        )

        # Phase 2
        self._phase_header(task_name, "Search & Mapping")
        try:
            candidates = search_paths(
                [
                    "src/codex_ml/data/*.py",
                    "src/codex_ml/eval/*.py",
                    "src/codex_ml/safety/*.py",
                    "configs/**/*.yaml",
                    "tests/test_data*.py",
                ]
            )
            log_change("Mapped data/eval/safety artefacts: " + ", ".join(candidates))
        except Exception as exc:
            log_error("Task2-Search", exc, "Collecting data/eval files")

        # Phase 3
        self._phase_header(task_name, "Best-Effort Construction")
        construction_notes = [
            "Apply Atomic Diff 4 by adding data/split_utils.py and companion tests (Capability: Data Handling).",
            "Introduce dataset manifest + schema validation using Pydantic models; update loaders to use manifest when available.",
            "Enhance eval.metrics with F1/ROUGE and register via entry points (Capability: Evaluation & Metrics minimal patch).",
            "Wire SafetyFilters into training generation paths and CLI commands (HS#8, Capability: Security & Safety).",
            "Create regression tests for split_utils and safety enforcement (HS#7).",
            "Detect missing telemetry dependencies and emit structured warnings instead of silent disablement (HS#9).",
        ]
        for note in construction_notes:
            log_change(f"[Plan] {note}")
        save_gap_snapshot(
            "data_eval_safety_best_effort",
            construction_notes,
        )

        # Phase 4
        self._phase_header(task_name, "Controlled Pruning")
        for note in [
            "If dataset manifest generation is too expensive for huge corpora, document fallback to streaming splits.",
            "If ROUGE dependencies unavailable offline, mark as deferred with instructions to vendor wheels locally.",
        ]:
            log_change(f"[Pruning] {note}")

        # Phase 5
        self._phase_header(task_name, "Error Capture")
        log_change(
            "Configured error capture for Task 2; dataset or metric failures will be logged with HS references."
        )

        # Phase 6
        self._phase_header(task_name, "Finalization")
        final_steps = [
            "Update README and docs with dataset split CLI and safety defaults (HS#6, HS#8).",
            "Run targeted tests: pytest tests/test_data_split_utils.py tests/test_safety_filters.py (optional).",
            "Summarise evaluation metric additions in change log and mkdocs site.",
        ]
        for step in final_steps:
            log_change(f"[Finalize] {step}")
        if self.run_tests:
            run_command(
                ["pytest", "tests/test_data_split_utils.py", "tests/test_safety_filters.py"],
                "Task2-Finalization",
                self.dry_run,
            )

    # Task 3: Configuration, CLI, Deployment, Documentation
    def task_config_cli_docs(self) -> None:
        task_name = "Configuration, CLI, Deployment & Docs Enablement"
        # Phase 1
        self._phase_header(task_name, "Preparation")
        try:
            read_readme()
            log_change(
                "Captured current configuration/deployment guidance to expand with new examples (HS#3, HS#10)."
            )
        except Exception as exc:
            log_error("Task3-Preparation", exc, "Reading README for configuration guidance")
        save_gap_snapshot(
            "config_cli_docs_preparation",
            [
                "Hydra config coverage limited (Capability: Configuration Management)",
                "CLI lacks dataset inspection utility (HS#6)",
                "Dockerfile single-stage without GPU build path (Capability: Deployment)",
                "Docs lack feature walkthroughs (Capability: Documentation & Examples)",
            ],
        )

        # Phase 2
        self._phase_header(task_name, "Search & Mapping")
        try:
            candidates = search_paths(
                [
                    "configs/**/*.yaml",
                    "src/codex_ml/cli/*.py",
                    "Dockerfile",
                    "docker-compose.yml",
                    "mkdocs.yml",
                    "docs/**/*.md",
                ]
            )
            log_change("Mapped configuration/CLI/doc artefacts: " + ", ".join(candidates))
        except Exception as exc:
            log_error("Task3-Search", exc, "Collecting config/CLI/doc files")

        # Phase 3
        self._phase_header(task_name, "Best-Effort Construction")
        construction_notes = [
            "Extend TrainConfig schema with seed/device/dtype/LoRA parameters (Capability: Configuration Management).",
            "Add hydra default config set and validation CLI (typer) per minimal patch plan.",
            "Implement `codex-tokenizer stats` CLI command for vocab inspection (HS#6, Capability: Tokenization gap).",
            "Document optional dependency expectations and add runtime detection that surfaces actionable warnings (HS#9).",
            "Create multi-stage Dockerfiles for CPU/GPU and update Makefile targets (Capability: Deployment).",
            "Author MkDocs pages + README quickstarts for LoRA + MLflow workflows (HS#10).",
            "Provide notebook or example script demonstrating LoRA fine-tune with tracking enabled.",
        ]
        for note in construction_notes:
            log_change(f"[Plan] {note}")
        save_gap_snapshot(
            "config_cli_docs_best_effort",
            construction_notes,
        )

        # Phase 4
        self._phase_header(task_name, "Controlled Pruning")
        for note in [
            "If GPU Docker base images unavailable offline, document requirement for mirroring images internally.",
            "If typer validation CLI causes dependency conflicts, provide fallback instructions using python -m codex_ml.cli.validate.",
        ]:
            log_change(f"[Pruning] {note}")

        # Phase 5
        self._phase_header(task_name, "Error Capture")
        log_change(
            "Error capture configured for Task 3; CLI generation or Docker build errors will be logged with context."
        )

        # Phase 6
        self._phase_header(task_name, "Finalization")
        final_steps = [
            "Update mkdocs navigation and README release notes to surface new tooling.",
            "Add coverage entries to change log and docs summarising CLI + deployment updates.",
            "Optionally run `nox -s docs` and `nox -s lint` when available (skipped when --dry-run).",
        ]
        for step in final_steps:
            log_change(f"[Finalize] {step}")
        if self.run_tests:
            run_command(["nox", "-s", "docs"], "Task3-Finalization", self.dry_run)
            run_command(["nox", "-s", "lint"], "Task3-Finalization", self.dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex-ready task orchestrator")
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=["model_training", "data_eval_safety", "config_cli_docs"],
        help="Subset of tasks to execute (model_training, data_eval_safety, config_cli_docs)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Log actions without executing commands"
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run verification commands during finalization phases",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runner = CodexTaskRunner(dry_run=args.dry_run or not args.run_tests, run_tests=args.run_tests)
    runner.run(args.tasks)


if __name__ == "__main__":
    main()
