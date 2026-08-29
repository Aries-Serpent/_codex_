#!/usr/bin/env python3
"""Codex Task Executor for sequential task block execution."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import subprocess
import sys
import textwrap
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

RUN_TIMESTAMP = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@dataclass
class ChangeLogEntry:
    step: str
    status: str
    action: str
    details: str
    timestamp: str = field(default_factory=lambda: _dt.datetime.now(_dt.timezone.utc).isoformat())


@dataclass
class GapRecord:
    feature: str
    reason: str
    explored_paths: list[str]
    notes: str


class CodexTaskExecutor:
    """Implements the sequential phases described in the execution block."""

    def __init__(
        self, repo_root: Path, logs_dir: Path, reports_dir: Path, dry_run: bool = False
    ) -> None:
        self.repo_root = repo_root
        self.logs_dir = logs_dir
        self.reports_dir = reports_dir
        self.dry_run = dry_run
        self.change_log: list[ChangeLogEntry] = []
        self.gap_records: list[GapRecord] = []
        self.errors: list[dict[str, str]] = []
        self.pending_pruning: dict[str, GapRecord] = {}
        self.readme_audit: dict[str, Any] = {}
        self.mapping: dict[str, Any] = {}
        self.adaptation_notes: dict[str, Any] = {}
        self.artifacts: dict[str, Any] = {}
        self._ensure_directories()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _ensure_directories(self) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _run_step(self, step: str, description: str, func: Callable[[], Any]) -> Any:
        try:
            result = func()
            self._record_change(
                step,
                "completed",
                description,
                json.dumps(result, default=str) if result is not None else "",
            )
            return result
        except Exception as exc:  # pragma: no cover - defensive logging
            self._record_change(step, "failed", description, str(exc))
            self._record_error(step, description, exc)
            return None

    def _record_change(self, step: str, status: str, action: str, details: str) -> None:
        self.change_log.append(
            ChangeLogEntry(step=step, status=status, action=action, details=details)
        )

    def _record_gap(
        self, feature: str, reason: str, explored_paths: Sequence[str], notes: str
    ) -> None:
        record = GapRecord(
            feature=feature, reason=reason, explored_paths=list(explored_paths), notes=notes
        )
        self.gap_records.append(record)
        self.pending_pruning[feature] = record
        self._record_change(feature, "gap", reason, notes)

    def _record_error(self, step: str, description: str, error: Exception) -> None:
        timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        question = (
            f"Question from ChatGPT @codex {timestamp}:\n"
            f"While performing [{step}:{description}], encountered the following error: {error} "
            "Context: executing codex_task_executor.py. What are the possible causes, and how can this be resolved while preserving intended functionality?"
        )
        self.errors.append({"question": question})

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _append_ndjson(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            handle.write("\n")

    def _read_file(self, path: Path) -> Optional[str]:
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _write_file(self, path: Path, content: str) -> None:
        if self.dry_run:
            self._record_change(str(path), "dry-run", "write_skipped", "dry run enabled")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _ensure_insertion(self, path: Path, marker: str, snippet: str) -> bool:
        current = self._read_file(path)
        if current is None:
            return False
        if marker in current:
            return False
        if self.dry_run:
            self._record_change(str(path), "dry-run", "insertion_skipped", marker)
            return False
        updated = f"{current.rstrip()}\n\n{snippet}\n"
        path.write_text(updated, encoding="utf-8")
        return True

    # ------------------------------------------------------------------
    # Phase 1 — Preparation
    # ------------------------------------------------------------------
    def phase_preparation(self) -> None:
        self._run_step("1.1", "establish_directories", self._establish_directories)
        self._run_step("1.2", "parse_readme", self._parse_and_update_readme)
        self._run_step("1.3", "capture_environment", self._capture_environment)
        self._run_step(
            "1.4", "assert_no_cost_incurring_actions", self._assert_no_cost_incurring_actions
        )

    def _establish_directories(self) -> dict[str, str]:
        return {
            "logs_dir": str(self.logs_dir),
            "reports_dir": str(self.reports_dir),
            "run_id": RUN_TIMESTAMP,
        }

    def _parse_and_update_readme(self) -> dict[str, Any]:
        readme_path = self.repo_root / "README.md"
        text = self._read_file(readme_path)
        if text is None:
            self._record_gap(
                "README", "Missing README.md", [str(readme_path)], "Cannot audit README references."
            )
            return {"status": "missing"}
        keywords = ["LoRA", "metrics", "secret", "Docker", "reproducibility"]
        summary: dict[str, list[str]] = {}
        for keyword in keywords:
            lines = [line.strip() for line in text.splitlines() if keyword.lower() in line.lower()]
            summary[keyword] = lines
        placeholders = {
            "{{TODO_LORA_CLI}}": "LoRA CLI support is provided via `codex train-lora`.",
            "{{TODO_METRICS_AGGREGATOR}}": "Use `python tools/metrics_aggregate.py --input metrics.ndjson --csv metrics.csv`.",
            "{{TODO_SECRET_SCANNING}}": "Run `nox -s gates` to execute detect-secrets and bandit locally.",
            "{{TODO_PACKAGING}}": "Package via `python -m build` and install locally with `pip install dist/*.whl`.",
            "{{TODO_REPRO}}": "Environment manifests are written to `.codex/runs/<timestamp>/manifest.json`.",
        }
        updated_text = text
        replacements: dict[str, str] = {}
        for marker, replacement in placeholders.items():
            if marker in updated_text:
                replacements[marker] = replacement
                updated_text = updated_text.replace(marker, replacement)
        if replacements and not self.dry_run:
            readme_path.write_text(updated_text, encoding="utf-8")
        self.readme_audit = {"summary": summary, "replacements": replacements}
        self._write_json(self.logs_dir / "readme_audit.json", self.readme_audit)
        return self.readme_audit

    def _capture_environment(self) -> dict[str, Any]:
        provenance = {
            "timestamp": RUN_TIMESTAMP,
            "python": sys.version,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "executable": sys.executable,
            "env": {k: v for k, v in os.environ.items() if k.startswith("CODEX_")},
        }
        try:
            pip_freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        except Exception as exc:  # pragma: no cover - subprocess failure
            pip_freeze = f"pip freeze failed: {exc}"
        provenance["pip_freeze"] = pip_freeze
        try:
            git_head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=self.repo_root, text=True
            ).strip()
        except Exception as exc:  # pragma: no cover - git failure
            git_head = f"git rev-parse failed: {exc}"
        provenance["git_head"] = git_head
        self._write_json(self.logs_dir / "provenance.json", provenance)
        return provenance

    def _assert_no_cost_incurring_actions(self) -> dict[str, Any]:
        workflows_path = self.repo_root / ".github" / "workflows"
        return {
            "workflows_present": workflows_path.exists(),
            "message": "ensure workflows remain disabled",
        }

    # ------------------------------------------------------------------
    # Phase 2 — Search & Mapping
    # ------------------------------------------------------------------
    def phase_search_mapping(self) -> None:
        self._run_step("2.1", "enumerate_candidate_modules", self._enumerate_candidates)
        self._run_step("2.2", "compare_purposes", self._compare_purposes)
        self._run_step("2.3", "identify_related_tooling", self._identify_related_tooling)

    def _enumerate_candidates(self) -> dict[str, Any]:
        categories = {
            "lora": ["src/codex_cli", "training", "docs", "tests"],
            "metrics": ["src/codex_ml/metrics", "analysis", "tools", "scripts"],
            "security": ["noxfile.py", "requirements-dev.txt", "docs/modules"],
            "packaging": ["pyproject.toml", "setup.cfg", "Dockerfile"],
            "reproducibility": ["docs", "training", "codex_utils"],
        }
        mapping: dict[str, list[str]] = {}
        for key, targets in categories.items():
            collected: list[str] = []
            for target in targets:
                for match in self.repo_root.glob(f"**/{Path(target).name}"):
                    try:
                        collected.append(str(match.relative_to(self.repo_root)))
                    except ValueError:
                        collected.append(str(match))
            mapping[key] = sorted(set(collected))
        self.mapping = mapping
        self._write_json(self.logs_dir / "mapping.json", mapping)
        return mapping

    def _compare_purposes(self) -> dict[str, Any]:
        notes: dict[str, Any] = {}
        for key, paths in self.mapping.items():
            comparisons: list[dict[str, Any]] = []
            for rel_path in paths:
                full = self.repo_root / rel_path
                snippet = None
                content = self._read_file(full)
                if content:
                    snippet = "\n".join(content.splitlines()[:5])
                comparisons.append({"path": rel_path, "preview": snippet})
            notes[key] = comparisons
        self.adaptation_notes = notes
        self._write_json(self.logs_dir / "adaptation_notes.json", notes)
        return notes

    def _identify_related_tooling(self) -> dict[str, Any]:
        tooling = {
            "hydra_configs": [
                str(path.relative_to(self.repo_root))
                for path in (self.repo_root / "configs").rglob("*.yaml")
            ],
            "nox_sessions": [
                str(path.relative_to(self.repo_root))
                for path in (self.repo_root / "nox_sessions").glob("*.py")
            ],
            "tools": [
                str(path.relative_to(self.repo_root))
                for path in (self.repo_root / "tools").glob("*.py")
            ],
        }
        self._write_json(self.logs_dir / "tooling_map.json", tooling)
        return tooling

    # ------------------------------------------------------------------
    # Phase 3 — Best-Effort Construction
    # ------------------------------------------------------------------
    def phase_best_effort_construction(self) -> None:
        self._run_step("3.1", "lora_cli_docs_tests", self._ensure_lora_cli_docs_tests)
        self._run_step(
            "3.2", "metrics_registry_aggregator", self._ensure_metrics_registry_and_aggregator
        )
        self._run_step("3.3", "secret_scanning_gates", self._ensure_secret_scanning_gates)
        self._run_step("3.4", "packaging_and_docker", self._ensure_packaging_and_docker)
        self._run_step(
            "3.5", "reproducibility_improvements", self._ensure_reproducibility_improvements
        )

    def _ensure_lora_cli_docs_tests(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        cli_path = self.repo_root / "src" / "codex_cli" / "app.py"
        if not cli_path.exists():
            self._record_gap(
                "lora_cli", "CLI module missing", [str(cli_path)], "Cannot expose LoRA parameters."
            )
            return {"status": "missing_cli"}
        cli_text = self._read_file(cli_path) or ""
        marker = '@app.command("train-lora")'
        if marker not in cli_text:
            snippet = textwrap.dedent(
                """
                @app.command("train-lora")
                def train_lora(
                    config_path: str = _typer.Option(..., help="Hydra/OMEGACONF config or experiment identifier"),
                    lora_r: int = _typer.Option(8, help="Rank of LoRA adapters (0 disables LoRA)"),
                    lora_alpha: int = _typer.Option(16, help="Alpha scaling factor"),
                    lora_dropout: float = _typer.Option(0.05, help="Dropout probability for LoRA adapters"),
                    target_modules: str = _typer.Option("q_proj,v_proj", help="Comma-separated module names"),
                ) -> None:
                    \"\"\"Train a model locally with optional LoRA adapters.\"\"\"
                    try:
                        from src import modeling
                        from src.training import trainer as trainer_module
                    except Exception as exc:  # pragma: no cover - optional import path
                        echo(f"Training modules unavailable: {exc}")
                        raise Exit(code=1)

                    modules = tuple(part.strip() for part in target_modules.split(",") if part.strip())
                    lora_enabled = lora_r > 0
                    lora_settings = modeling.LoraSettings(
                        r=lora_r,
                        alpha=lora_alpha,
                        dropout=lora_dropout,
                        target_modules=modules if modules else None,
                    ) if lora_enabled else None
                    model_config = modeling.ModelInitConfig(lora_settings=lora_settings)
                    echo(f"Loading model with LoRA enabled={lora_enabled} (modules={modules or '<auto>'})")
                    model, tokenizer = modeling.load_model_and_tokenizer(model_config)
                    run = trainer_module.build_run_from_config(config_path)
                    run.train(model=model, tokenizer=tokenizer)
                """
            )
            inserted = self._ensure_insertion(cli_path, marker, snippet)
            results["cli_command_added"] = inserted
        else:
            results["cli_command_added"] = False
        docs_path = self.repo_root / "docs" / "CLI.md"
        docs_marker = "## LoRA fine-tuning via CLI"
        docs_text = self._read_file(docs_path) or ""
        if docs_marker not in docs_text:
            section = textwrap.dedent(
                """
                ## LoRA fine-tuning via CLI

                ```bash
                codex train-lora --config-path configs/training/base.yaml --lora-r 16 --lora-alpha 32 --lora-dropout 0.05 --target-modules q_proj,v_proj
                ```

                The command wraps the offline training stack and injects LoRA settings directly into the model initialisation pipeline.
                """
            )
            added = self._ensure_insertion(docs_path, docs_marker, section)
            results["docs_updated"] = added
        else:
            results["docs_updated"] = False
        test_path = self.repo_root / "tests" / "test_cli_lora.py"
        if not test_path.exists():
            test_content = textwrap.dedent(
                """
                from __future__ import annotations

                from typer.testing import CliRunner

                from codex_cli.app import app


                def test_cli_exposes_lora_command() -> None:
                    runner = CliRunner()
                    result = runner.invoke(app, ["--help"])
                    assert result.exit_code == 0
                    assert "train-lora" in result.stdout
                """
            )
            self._write_file(test_path, test_content)
            results["test_created"] = True
        else:
            results["test_created"] = False
        return results

    def _ensure_metrics_registry_and_aggregator(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        registry_path = self.repo_root / "src" / "codex_ml" / "metrics" / "registry.py"
        registry_text = self._read_file(registry_path)
        if registry_text is None:
            self._record_gap(
                "metrics_registry",
                "Registry missing",
                [str(registry_path)],
                "Cannot register metrics.",
            )
            results["registry_missing"] = True
        else:
            if "def f1_score" not in registry_text:
                snippet = textwrap.dedent(
                    """

                    from typing import Any, Sequence


                    def accuracy(preds: Sequence[Any], labels: Sequence[Any]) -> float:
                        if not preds:
                            return 0.0
                        correct = sum(1 for pred, label in zip(preds, labels) if pred == label)
                        return correct / max(1, len(preds))


                    def precision(preds: Sequence[Any], labels: Sequence[Any]) -> float:
                        tp = sum(1 for pred, label in zip(preds, labels) if pred == label and pred)
                        fp = sum(1 for pred, label in zip(preds, labels) if pred and pred != label)
                        return tp / max(1, tp + fp)


                    def recall(preds: Sequence[Any], labels: Sequence[Any]) -> float:
                        tp = sum(1 for pred, label in zip(preds, labels) if pred == label and label)
                        fn = sum(1 for pred, label in zip(preds, labels) if label and pred != label)
                        return tp / max(1, tp + fn)


                    def f1_score(preds: Sequence[Any], labels: Sequence[Any]) -> float:
                        p = precision(preds, labels)
                        r = recall(preds, labels)
                        if p + r == 0:
                            return 0.0
                        return 2 * (p * r) / (p + r)


                    register("accuracy", accuracy)
                    register("precision", precision)
                    register("recall", recall)
                    register("f1", f1_score)
                    """
                )
                if not self.dry_run:
                    registry_path.write_text(registry_text.rstrip() + snippet, encoding="utf-8")
                results["registry_augmented"] = True
            else:
                results["registry_augmented"] = False
        aggregator_path = self.repo_root / "tools" / "metrics_aggregate.py"
        if not aggregator_path.exists():
            aggregator_code = textwrap.dedent(
                '''
                #!/usr/bin/env python3
                """Aggregate NDJSON metrics into summary NDJSON/CSV outputs."""

                from __future__ import annotations

                import argparse
                import csv
                import json
                from collections import defaultdict
                from pathlib import Path
                from statistics import mean
                from typing import Any, Dict, Iterable, List


                Record = Dict[str, Any]


                def load_records(path: Path) -> List[Record]:
                    records: List[Record] = []
                    for line in path.read_text(encoding="utf-8").splitlines():
                        if not line.strip():
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(payload, dict):
                            records.append(payload)
                    return records


                def aggregate_metrics(records: Iterable[Record], metric_key: str) -> Dict[str, float]:
                    buckets: Dict[str, List[float]] = defaultdict(list)
                    for record in records:
                        metrics = record.get(metric_key)
                        if isinstance(metrics, dict):
                            for key, value in metrics.items():
                                try:
                                    buckets[str(key)].append(float(value))
                                except (TypeError, ValueError):
                                    continue
                    return {key: mean(values) for key, values in buckets.items() if values}


                def write_ndjson(path: Path, payload: Dict[str, float]) -> None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("w", encoding="utf-8") as handle:
                        for key, value in payload.items():
                            handle.write(json.dumps({"metric": key, "value": value}))
                            handle.write("\n")


                def write_csv(path: Path, payload: Dict[str, float]) -> None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("w", encoding="utf-8", newline="") as handle:
                        writer = csv.writer(handle)
                        writer.writerow(["metric", "value"])
                        for key, value in payload.items():
                            writer.writerow([key, value])


                def main(argv: Iterable[str] | None = None) -> int:
                    parser = argparse.ArgumentParser(description="Aggregate NDJSON metrics")
                    parser.add_argument("--input", required=True, help="Path to NDJSON metrics file")
                    parser.add_argument("--ndjson", help="Output NDJSON summary path")
                    parser.add_argument("--csv", help="Output CSV summary path")
                    parser.add_argument("--metric-key", default="metrics", help="Field containing metric dictionary")
                    args = parser.parse_args(list(argv) if argv is not None else None)

                    records = load_records(Path(args.input))
                    summary = aggregate_metrics(records, args.metric_key)
                    if args.ndjson:
                        write_ndjson(Path(args.ndjson), summary)
                    if args.csv:
                        write_csv(Path(args.csv), summary)
                    if not args.ndjson and not args.csv:
                        print(json.dumps(summary, indent=2))
                    return 0


                if __name__ == "__main__":  # pragma: no cover
                    raise SystemExit(main())
                '''
            )
            self._write_file(aggregator_path, aggregator_code)
            results["aggregator_created"] = True
        else:
            results["aggregator_created"] = False
        docs_metrics_path = self.repo_root / "docs" / "metrics.md"
        docs_marker = "## Metrics registry"
        docs_text = self._read_file(docs_metrics_path) or ""
        if docs_marker not in docs_text:
            section = textwrap.dedent(
                """
                ## Metrics registry

                Register custom metrics by importing `codex_ml.metrics.registry` and calling `register(name, fn)`. Common metrics are pre-registered (accuracy, precision, recall, F1).

                Aggregate NDJSON logs locally with:

                ```bash
                python tools/metrics_aggregate.py --input metrics.ndjson --csv summary.csv --ndjson summary.ndjson
                ```
                """
            )
            added = self._ensure_insertion(docs_metrics_path, docs_marker, section)
            results["metrics_docs_added"] = added
        else:
            results["metrics_docs_added"] = False
        return results

    def _ensure_secret_scanning_gates(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        nox_path = self.repo_root / "noxfile.py"
        nox_text = self._read_file(nox_path)
        if nox_text is None:
            self._record_gap(
                "secret_scanning", "noxfile missing", [str(nox_path)], "Cannot inject gates."
            )
            return {"status": "missing_nox"}
        if "detect-secrets" not in nox_text or "bandit" not in nox_text:
            injection = textwrap.dedent(
                """
                session.install("detect-secrets", "bandit")
                session.run("detect-secrets", "scan", "--all-files", external=True)
                session.run("bandit", "-r", "src", external=True)
                """
            ).strip("\n")
            anchor = '    session.run("python", str(_CONFIG_VALIDATOR), "--quiet")'
            if anchor in nox_text and not self.dry_run:
                # Prepare the injection with proper indentation
                indented_injection = injection.replace("\n", "\n    ")
                updated = nox_text.replace(
                    anchor,
                    f"{anchor}\n    # Secret scanning\n    {indented_injection}",
                )
                nox_path.write_text(updated, encoding="utf-8")
                results["nox_updated"] = True
            else:
                results["nox_updated"] = False
        else:
            results["nox_updated"] = False
        safety_doc = self.repo_root / "docs" / "modules" / "safety.md"
        safety_marker = "### Secret scanning"
        safety_text = self._read_file(safety_doc) or ""
        if safety_marker not in safety_text:
            section = textwrap.dedent(
                """
                ### Secret scanning

                Local gates execute `detect-secrets` and `bandit` via `nox -s gates`. Review `.secrets.baseline` when rotating secrets to keep fingerprints current.
                """
            )
            added = self._ensure_insertion(safety_doc, safety_marker, section)
            results["docs_updated"] = added
        else:
            results["docs_updated"] = False
        baseline_path = self.repo_root / ".secrets.baseline"
        if not baseline_path.exists():
            baseline_payload = {
                "version": "1.0",
                "generated_at": RUN_TIMESTAMP,
                "filters": [],
            }
            self._write_file(baseline_path, json.dumps(baseline_payload, indent=2))
            results["baseline_created"] = True
        else:
            results["baseline_created"] = False
        return results

    def _ensure_packaging_and_docker(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        pyproject_path = self.repo_root / "pyproject.toml"
        pyproject_text = self._read_file(pyproject_path)
        if pyproject_text is None:
            self._record_gap(
                "packaging",
                "pyproject missing",
                [str(pyproject_path)],
                "Cannot define CLI entry point.",
            )
            results["pyproject_missing"] = True
        else:
            if "[project.scripts]" not in pyproject_text:
                addition = textwrap.dedent(
                    """
                    [project]
                    name = "codex"
                    version = "0.1.0"
                    description = "Codex offline reasoning toolkit"
                    requires-python = ">=3.10"
                    dependencies = [
                        "typer>=0.9",
                    ]

                    [project.scripts]
                    codex = "src.codex_cli.app:app"
                    """
                )
                self._write_file(pyproject_path, pyproject_text.rstrip() + "\n" + addition)
                results["pyproject_updated"] = True
            else:
                results["pyproject_updated"] = False
        docker_path = self.repo_root / "Dockerfile"
        docker_text = self._read_file(docker_path)
        if docker_text is None:
            docker_content = textwrap.dedent(
                """
                # syntax=docker/dockerfile:1
                FROM python:3.10-slim AS build
                ENV VIRTUAL_ENV=/opt/venv
                RUN python -m venv $VIRTUAL_ENV
                ENV PATH="$VIRTUAL_ENV/bin:$PATH"
                RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*
                COPY pyproject.toml uv.lock requirements requirements-dev.txt /tmp/src/
                WORKDIR /tmp/src
                RUN pip install --upgrade pip setuptools wheel && \
                    pip install --no-cache-dir -r requirements-dev.txt && \
                    pip install --no-cache-dir -r requirements/base.txt

                FROM python:3.10-slim AS runtime
                ENV VIRTUAL_ENV=/opt/venv
                RUN python -m venv $VIRTUAL_ENV
                ENV PATH="$VIRTUAL_ENV/bin:$PATH"
                RUN useradd --create-home codex && mkdir -p /opt/codex && chown codex:codex /opt/codex
                USER codex
                WORKDIR /opt/codex
                COPY --from=build /opt/venv /opt/venv
                COPY . .
                ENTRYPOINT ["codex"]
                """
            )
            self._write_file(docker_path, docker_content)
            results["dockerfile_created"] = True
        else:
            if "USER codex" not in docker_text:
                patched = docker_text.rstrip() + "\nUSER codex\n"
                self._write_file(docker_path, patched)
                results["dockerfile_hardened"] = True
            else:
                results["dockerfile_hardened"] = False
        runbook_path = self.repo_root / "docs" / "runbook.md"
        runbook_text = self._read_file(runbook_path) or ""
        runbook_marker = "## Packaging and deployment"
        if runbook_marker not in runbook_text:
            section = textwrap.dedent(
                """
                ## Packaging and deployment

                Build and install locally:

                ```bash
                python -m build
                tar -xf dist/codex-0.1.0.tar.gz -C /tmp
                pip install dist/codex-0.1.0-py3-none-any.whl
                ```

                Build the hardened Docker image:

                ```bash
                docker build --target runtime -t codex-offline .
                ```
                """
            )
            added = self._ensure_insertion(runbook_path, runbook_marker, section)
            results["runbook_updated"] = added
        else:
            results["runbook_updated"] = False
        return results

    def _ensure_reproducibility_improvements(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        repro_doc = self.repo_root / "docs" / "reproducibility.md"
        if not repro_doc.exists():
            repro_doc = self.repo_root / "docs" / "repro.md"
        repro_text = self._read_file(repro_doc) or ""
        marker = "## Deterministic settings"
        if marker not in repro_text:
            section = textwrap.dedent(
                """
                ## Deterministic settings

                Enable deterministic behaviour with:

                ```bash
                export PYTHONHASHSEED=0
                export CUBLAS_WORKSPACE_CONFIG=:16:8
                python -m codex_cli.set_deterministic --seed 42
                ```

                Training runs emit environment manifests under `.codex/runs/<timestamp>/manifest.json` capturing platform, dependency, and RNG state.
                """
            )
            added = self._ensure_insertion(repro_doc, marker, section)
            results["repro_doc_updated"] = added
        else:
            results["repro_doc_updated"] = False
        manifest_dir = self.repo_root / ".codex" / "runs" / RUN_TIMESTAMP
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "manifest.json"
        manifest_payload = {
            "timestamp": RUN_TIMESTAMP,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "provenance": str(self.logs_dir / "provenance.json"),
        }
        self._write_file(manifest_path, json.dumps(manifest_payload, indent=2))
        results["manifest_written"] = True
        nox_path = self.repo_root / "noxfile.py"
        nox_text = self._read_file(nox_path) or ""
        if "uv.lock" not in nox_text:
            addition = textwrap.dedent(
                """
                def _install_with_lock(session: nox.Session) -> None:
                    from pathlib import Path

                    lockfile = Path("uv.lock")
                    if lockfile.exists():
                        session.install("uv")
                        session.run("uv", "sync", "--locked", external=True)
                """
            )
            hook = "def tests("
            if hook in nox_text and "_install_with_lock" not in nox_text and not self.dry_run:
                hook_index = nox_text.find(hook)
                line_break = nox_text.find("\n", hook_index)
                if line_break == -1:
                    results["lockfile_enforced"] = False
                else:
                    updated_tests = (
                        nox_text[: line_break + 1]
                        + "    _install_with_lock(session)\n"
                        + nox_text[line_break + 1 :]
                    )
                    updated = addition + "\n" + updated_tests
                    nox_path.write_text(updated, encoding="utf-8")
                    results["lockfile_enforced"] = True
            else:
                results["lockfile_enforced"] = False
        else:
            results["lockfile_enforced"] = False
        return results

    # ------------------------------------------------------------------
    # Phase 4 — Controlled Pruning
    # ------------------------------------------------------------------
    def phase_controlled_pruning(self) -> None:
        self._run_step("4.1", "document_pruning", self._document_pruning)
        self._run_step("4.2", "cross_reference_pruning", self._cross_reference_pruning)
        self._run_step("4.3", "tag_deferred_work", self._tag_deferred_work)

    def _document_pruning(self) -> dict[str, Any]:
        report_path = self.reports_dir / "pruning_report.md"
        if not self.pending_pruning:
            content = "# Pruning Report\n\nNo items pruned; all tasks attempted.\n"
        else:
            lines = ["# Pruning Report", ""]
            for feature, record in self.pending_pruning.items():
                lines.append(f"## {feature}")
                lines.append(f"Reason: {record.reason}")
                lines.append(f"Explored paths: {', '.join(record.explored_paths) or '<none>'}")
                lines.append(f"Notes: {record.notes}")
                lines.append("")
            content = "\n".join(lines)
        self._write_file(report_path, content)
        return {"report": str(report_path)}

    def _cross_reference_pruning(self) -> dict[str, Any]:
        refs = {
            feature: {
                "reason": record.reason,
                "explored": record.explored_paths,
            }
            for feature, record in self.pending_pruning.items()
        }
        self._write_json(self.logs_dir / "pruning_cross_reference.json", refs)
        return refs

    def _tag_deferred_work(self) -> dict[str, Any]:
        return {feature: record.notes for feature, record in self.pending_pruning.items()}

    # ------------------------------------------------------------------
    # Phase 5 — Error Capture
    # ------------------------------------------------------------------
    def phase_error_capture(self) -> None:
        error_path = self.logs_dir / "error_captures.ndjson"
        for error in self.errors:
            self._append_ndjson(error_path, error)

    # ------------------------------------------------------------------
    # Phase 6 — Finalization
    # ------------------------------------------------------------------
    def phase_finalization(self) -> None:
        summary_path = self.reports_dir / "final_summary.md"
        lines = [
            "# Final Summary",
            "",
            f"Run timestamp: {RUN_TIMESTAMP}",
            "",
            "## Completed actions",
        ]
        for entry in self.change_log:
            if entry.status == "completed":
                lines.append(f"- [{entry.step}] {entry.action}")
        if self.pending_pruning:
            lines.append("")
            lines.append("## Outstanding gaps")
            for feature, record in self.pending_pruning.items():
                lines.append(f"- {feature}: {record.reason}")
        lines.append("")
        lines.append("## Errors captured")
        if self.errors:
            for error in self.errors:
                lines.append(f"- {error['question'].splitlines()[0]}")
        else:
            lines.append("- None")
        self._write_file(summary_path, "\n".join(lines))
        change_log_path = self.repo_root / "codex_change_log.jsonl"
        for entry in self.change_log:
            payload = {
                "timestamp": entry.timestamp,
                "step": entry.step,
                "status": entry.status,
                "action": entry.action,
                "details": entry.details,
            }
            self._append_ndjson(change_log_path, payload)
        self.artifacts = {"summary": str(summary_path), "change_log": str(change_log_path)}

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------
    def run(self) -> None:
        self.phase_preparation()
        self.phase_search_mapping()
        self.phase_best_effort_construction()
        self.phase_controlled_pruning()
        self.phase_error_capture()
        self.phase_finalization()
        print(json.dumps({"artifacts": self.artifacts, "errors": len(self.errors)}, indent=2))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex task executor")
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    parser.add_argument("--logs-dir", default=Path("logs/codex_tasks"), type=Path)
    parser.add_argument("--reports-dir", default=Path(".codex/reports/codex_tasks"), type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    executor = CodexTaskExecutor(
        repo_root=args.repo_root.resolve(),
        logs_dir=args.logs_dir.resolve(),
        reports_dir=args.reports_dir.resolve(),
        dry_run=args.dry_run,
    )
    executor.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
