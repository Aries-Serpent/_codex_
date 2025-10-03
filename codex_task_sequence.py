#!/usr/bin/env python3
"""Codex offline task sequence executor.

This script orchestrates the Codex-ready task sequence described in the
companion YAML specification.  It operates entirely in offline mode and is
idempotent so repeated executions do not introduce duplicate artefacts.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import subprocess
import sys
import textwrap
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking

try:  # Optional dependency for deterministic helpers
    import numpy as np
except Exception:  # pragma: no cover - numpy might be unavailable
    np = None  # type: ignore

try:  # Optional dependency for seeding and evaluation tests
    import torch
    from torch.utils.data import DataLoader
except Exception:  # pragma: no cover - torch might be unavailable
    torch = None  # type: ignore
    DataLoader = None  # type: ignore


CAPABILITY_BUCKETS: Dict[str, Sequence[str]] = {
    "tokenization": ("token", "bpe", "spm", "sentencepiece"),
    "modeling": ("model", "encoder", "decoder", "transformer"),
    "training": ("train", "optimizer", "scheduler"),
    "config": ("config", "cfg", "hydra"),
    "evaluation": ("eval", "metric", "score"),
    "logging": ("log", "monitor", "telemetry"),
    "checkpointing": ("checkpoint", "resume", "snapshot"),
    "data_handling": ("data", "dataset", "loader"),
    "security": ("safety", "security", "policy"),
    "internal_ci": ("nox", "pytest", "ci"),
    "deployment": ("deploy", "cloud", "infra"),
    "docs": ("docs", "readme", "tutorial"),
    "experiment_tracking": ("mlflow", "tracking", "wandb"),
    "extensibility": ("plugin", "registry", "adapter"),
}

ERROR_TEMPLATE = textwrap.dedent(
    """
    Question for ChatGPT-5 {timestamp}:
    While performing [{step_number}:{step_description}], encountered the following error:
    {error_message}
    Context: {context}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
).strip()


@dataclass
class TaskContext:
    root: Path
    log_dir: Path
    reports_dir: Path
    mlflow_dir: Path
    seed: int
    grad_accum_steps: int
    dry_run: bool

    @property
    def error_log(self) -> Path:
        return self.log_dir / "error_captures.ndjson"

    @property
    def capability_mapping(self) -> Path:
        return self.log_dir / "capability_mapping.json"

    @property
    def provenance_path(self) -> Path:
        return self.log_dir / "provenance.json"

    @property
    def changelog_path(self) -> Path:
        return self.root / "CHANGELOG_CODEX.md"

    @property
    def deferred_report(self) -> Path:
        return self.reports_dir / "deferred.md"

    @property
    def archive_path(self) -> Path:
        return self.log_dir / "codex_run_artifacts.zip"


def _timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, content: str) -> None:
    _ensure_dir(path.parent)
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing != content:
        path.write_text(content, encoding="utf-8")


def _append_error(
    ctx: TaskContext, step_number: int, description: str, error: Exception, context: str
) -> None:
    block = ERROR_TEMPLATE.format(
        timestamp=_timestamp(),
        step_number=step_number,
        step_description=description,
        error_message=repr(error),
        context=context,
    )
    with ctx.error_log.open("a", encoding="utf-8") as handle:
        handle.write(block + "\n")


def _set_global_seed(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    if np is not None:
        np.random.seed(seed)  # type: ignore[arg-type]
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():  # pragma: no cover - cuda unavailable in tests
            torch.cuda.manual_seed_all(seed)
        if hasattr(torch.backends, "cudnn"):
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False


def _capture_environment(ctx: TaskContext) -> None:
    pip_freeze_path = ctx.log_dir / "pip_freeze.txt"
    try:
        freeze = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            check=True,
            capture_output=True,
            text=True,
        )
        _write_text(pip_freeze_path, freeze.stdout)
    except Exception as exc:  # pragma: no cover - subprocess failure
        _append_error(ctx, 101, "pip_freeze", exc, "Collecting dependency versions")

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ctx.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except Exception:
        commit = "(no git repository)"

    gpu_info: List[str] = []
    if torch is not None and torch.cuda.is_available():  # pragma: no cover - GPU optional
        for idx in range(torch.cuda.device_count()):
            gpu_info.append(torch.cuda.get_device_name(idx))

    provenance = {
        "timestamp": _timestamp(),
        "seed": ctx.seed,
        "grad_accumulation_steps": ctx.grad_accum_steps,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "gpu": gpu_info,
        "git_commit": commit,
        "dry_run": ctx.dry_run,
    }
    _write_text(ctx.provenance_path, json.dumps(provenance, indent=2, sort_keys=True))


def phase_preparation(ctx: TaskContext) -> None:
    _ensure_dir(ctx.log_dir)
    _ensure_dir(ctx.reports_dir)
    _set_global_seed(ctx.seed)
    _capture_environment(ctx)


def _iter_python_files(root: Path) -> Iterable[Path]:
    excluded = {".git", "__pycache__", "codex_logs", "mlruns", ".venv", "venv"}
    for path in root.rglob("*.py"):
        if any(part in excluded for part in path.parts):
            continue
        yield path


def _scan_stubs(ctx: TaskContext) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    patterns = ["TODO", "NotImplementedError"]
    for file_path in _iter_python_files(ctx.root):
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - permission errors rare
            _append_error(ctx, 201, "read_file", exc, f"Scanning {file_path}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            match = None
            if stripped == "pass":
                match = "pass"
            else:
                for pattern in patterns:
                    if pattern in line:
                        match = pattern
                        break
            if match:
                entries.append(
                    {
                        "file": str(file_path.relative_to(ctx.root)),
                        "line": line_number,
                        "text": stripped,
                    }
                )
    return entries


def _capabilities_for_entry(entry: Dict[str, Any]) -> List[str]:
    path_lower = entry["file"].lower()
    text_lower = entry["text"].lower()
    matched: List[str] = []
    for capability, hints in CAPABILITY_BUCKETS.items():
        if any(hint in path_lower or hint in text_lower for hint in hints):
            matched.append(capability)
    if not matched:
        matched.append("misc")
    return sorted(set(matched))


def phase_search_and_mapping(ctx: TaskContext) -> List[Dict[str, Any]]:
    entries = _scan_stubs(ctx)
    for entry in entries:
        entry["capabilities"] = _capabilities_for_entry(entry)
    _write_text(ctx.capability_mapping, json.dumps(entries, indent=2))
    return entries


def _ensure_base_config(ctx: TaskContext) -> bool:
    target = ctx.root / "configs" / "base_config.py"
    desired = (
        textwrap.dedent(
            '''
        """Base offline training configuration for Codex workflows."""

        from __future__ import annotations

        BASE_TRAINING_CONFIG: dict[str, object] = {
            "model_name": "sshleifer/tiny-gpt2",
            "tokenizer_name": "sshleifer/tiny-gpt2",
            "learning_rate": 5e-4,
            "batch_size": 8,
            "epochs": 3,
            "gradient_accumulation_steps": 1,
            "seed": 42,
        }


        def get_base_training_config() -> dict[str, object]:
            """Return a shallow copy of the base training configuration."""

            return dict(BASE_TRAINING_CONFIG)
        '''
        ).strip()
        + "\n"
    )
    if target.exists():
        return False
    if ctx.dry_run:
        return False
    _write_text(target, desired)
    return True


def _ensure_evaluation_loop(ctx: TaskContext) -> bool:
    target = ctx.root / "training" / "functional_training.py"
    if not target.exists():
        return False
    text = target.read_text(encoding="utf-8")
    if "def evaluate_batches" in text:
        return False
    if ctx.dry_run:
        return False
    addition = textwrap.dedent(
        '''
        def evaluate_batches(model, dataloader, metrics_fn, *, device, limit_batches=None):
            """Evaluate ``model`` on ``dataloader`` and aggregate metrics."""
            import numpy as _np
            import torch as _torch

            model.eval()
            loss_total = 0.0
            loss_steps = 0
            preds = []
            labels = []
            with _torch.no_grad():
                for batch_index, batch in enumerate(dataloader):
                    if limit_batches is not None and batch_index >= int(limit_batches):
                        break
                    for key, value in batch.items():
                        batch[key] = value.to(device)
                    outputs = model(**batch)
                    if isinstance(outputs, dict):
                        logits = outputs.get("logits")
                        loss = outputs.get("loss")
                    else:
                        logits = getattr(outputs, "logits", None)
                        loss = getattr(outputs, "loss", None)
                    if loss is not None:
                        loss_steps += 1
                        loss_total += float(loss.detach().cpu().item())
                    if logits is not None and metrics_fn is not None:
                        preds.append(logits.detach().cpu().numpy())
                        labels.append(batch["labels"].detach().cpu().numpy())
            metrics = {}
            if metrics_fn is not None and preds and labels:
                stacked = (_np.concatenate(preds), _np.concatenate(labels))
                metrics.update(metrics_fn(stacked))
            if loss_steps:
                metrics["loss"] = loss_total / float(loss_steps)
            metrics.setdefault("batches_evaluated", float(len(preds) or loss_steps))
            return metrics
        '''
    )
    _write_text(target, text + addition)
    return True


def _ensure_gradient_accumulation(ctx: TaskContext) -> bool:
    target = ctx.root / "training" / "functional_training.py"
    if not target.exists():
        return False
    text = target.read_text(encoding="utf-8")
    if "loss_t = loss_t / cfg.grad_accum" in text:
        return False
    if ctx.dry_run:
        return False
    replacement = text.replace(
        'loss_t = out["loss"] if isinstance(out, dict) else out.loss',
        'loss_t = out["loss"] if isinstance(out, dict) else out.loss\n                    loss_t = loss_t / cfg.grad_accum',
    )
    if replacement == text:
        return False
    _write_text(target, replacement)
    return True


def setup_mlflow_tracking(mlruns_dir: Path, *, dry_run: bool) -> bool:
    """Configure a local MLflow tracking URI when mlflow is available."""

    if dry_run:
        return False
    try:
        import mlflow  # type: ignore
    except Exception:
        return False

    mlruns_dir = mlruns_dir.resolve()
    _ensure_dir(mlruns_dir)
    os.environ.setdefault("CODEX_MLFLOW_LOCAL_DIR", str(mlruns_dir))
    uri = bootstrap_offline_tracking(force=True)
    if not uri.startswith("file:"):
        uri = f"file://{mlruns_dir}"
    mlflow.set_tracking_uri(uri)
    return True


def _configure_mlflow(ctx: TaskContext) -> Optional[str]:
    try:
        import mlflow  # type: ignore
    except Exception:
        return None

    mlruns_path = (ctx.root / ctx.mlflow_dir).resolve()
    if setup_mlflow_tracking(mlruns_path, dry_run=ctx.dry_run):
        return mlflow.get_tracking_uri()
    return None


def phase_best_effort(ctx: TaskContext) -> Dict[str, Any]:
    created = {
        "base_config": _ensure_base_config(ctx),
        "evaluation_loop": _ensure_evaluation_loop(ctx),
        "gradient_accum": _ensure_gradient_accumulation(ctx),
    }
    mlflow_uri = _configure_mlflow(ctx)
    return {"created": created, "mlflow_uri": mlflow_uri}


def _ensure_deferred_docs(ctx: TaskContext) -> bool:
    content = (
        textwrap.dedent(
            """
        # Deferred or Pruned Modules

        All orchestrated modules currently ship with offline-friendly fallbacks. Record
        new deferrals in this report if future work re-introduces external service
        dependencies so that downstream automation can make an informed decision.
        """
        ).strip()
        + "\n"
    )
    existing = (
        ctx.deferred_report.read_text(encoding="utf-8") if ctx.deferred_report.exists() else None
    )
    if existing == content:
        return False
    if ctx.dry_run:
        return False
    _write_text(ctx.deferred_report, content)
    return True


def _ensure_deferred_modules(ctx: TaskContext) -> List[str]:
    updated: List[str] = []
    remote_connector = ctx.root / "src" / "codex_ml" / "connectors" / "remote.py"
    if not remote_connector.exists() and not ctx.dry_run:
        _write_text(
            remote_connector,
            textwrap.dedent(
                '''
                """Offline-friendly remote connector implementations."""

                from __future__ import annotations

                import json
                from datetime import datetime
                from pathlib import Path
                from typing import Iterable, List

                from .base import Connector, ConnectorError, LocalConnector

                __all__ = ["RemoteConnector"]

                DEFAULT_CACHE_ROOT = Path.home() / ".codex" / "remote_cache"


                class RemoteConnector(Connector):
                    """Local emulation of remote storage with manifest tracking."""

                    def __init__(
                        self,
                        endpoint: str | None = None,
                        *,
                        cache_root: str | Path | None = None,
                        readonly: bool = False,
                    ) -> None:
                        self.endpoint = endpoint or "offline://remote"
                        root = Path(cache_root or DEFAULT_CACHE_ROOT).expanduser()
                        self._local = LocalConnector(root)
                        self.readonly = readonly
                        self._manifest_name = ".remote_manifest.json"
                        self._manifest_path = self._local.root / self._manifest_name
                        if not self._manifest_path.exists():
                            self._write_manifest(files=[], created=True)

                    @property
                    def cache_root(self) -> Path:
                        """Return the backing cache directory."""

                        return self._local.root

                    async def list_files(self, path: str) -> List[str]:  # type: ignore[override]
                        entries = await self._local.list_files(path)
                        return sorted(entry for entry in entries if entry != self._manifest_name)

                    async def read_file(self, path: str) -> bytes:  # type: ignore[override]
                        return await self._local.read_file(path)

                    async def write_file(self, path: str, data: bytes) -> None:  # type: ignore[override]
                        if self.readonly:
                            raise ConnectorError(
                                f"remote connector is read-only for endpoint {self.endpoint}"
                            )
                        await self._local.write_file(path, data)
                        files = [
                            item
                            for item in await self._local.list_files(".")
                            if item != self._manifest_name
                        ]
                        self._write_manifest(files=files)

                    def _write_manifest(self, *, files: Iterable[str], created: bool = False) -> None:
                        payload = {
                            "endpoint": self.endpoint,
                            "readonly": self.readonly,
                            "files": sorted(str(item) for item in files),
                        }
                        timestamp_key = "created_at" if created else "updated_at"
                        payload[timestamp_key] = datetime.utcnow().isoformat() + "Z"
                        self._manifest_path.write_text(
                            json.dumps(payload, indent=2, sort_keys=True),
                            encoding="utf-8",
                        )
                '''
            ).strip()
            + "\n",
        )
        updated.append(str(remote_connector.relative_to(ctx.root)))

    deployment_pkg = ctx.root / "src" / "codex_ml" / "deployment"
    cloud_path = deployment_pkg / "cloud.py"
    if not cloud_path.exists() and not ctx.dry_run:
        _ensure_dir(deployment_pkg)
        _write_text(
            cloud_path,
            textwrap.dedent(
                '''
                """Offline-friendly cloud deployment utilities."""

                from __future__ import annotations

                import json
                from datetime import datetime
                from pathlib import Path
                from typing import Any, Dict, Optional

                __all__ = ["provision_stack"]

                _STATUS_DEFERRED = "deferred"
                _DEFAULT_PROJECT = "codex-offline"


                def _timestamp() -> str:
                    return datetime.utcnow().isoformat() + "Z"


                def _resolve_output_dir(output_dir: str | Path | None) -> Path | None:
                    if output_dir is None:
                        return None
                    return Path(output_dir).expanduser().resolve()


                def provision_stack(
                    *,
                    project: str | None = None,
                    output_dir: str | Path | None = None,
                    dry_run: bool = True,
                    metadata: Optional[Dict[str, Any]] = None,
                ) -> Dict[str, Any]:
                    """Return a structured status block describing offline provisioning results."""

                    details: Dict[str, Any] = {
                        "status": _STATUS_DEFERRED,
                        "reason": "Cloud deployment is disabled for offline Codex runs.",
                        "project": project or _DEFAULT_PROJECT,
                        "dry_run": dry_run,
                        "timestamp": _timestamp(),
                    }
                    resolved_dir = _resolve_output_dir(output_dir)
                    if resolved_dir is not None:
                        details["output_dir"] = str(resolved_dir)
                    if metadata:
                        details["metadata"] = metadata

                    if dry_run:
                        return details

                    target_dir = resolved_dir or (Path.cwd() / "deployments" / details["project"])
                    sandbox_dir = target_dir / "sandbox"
                    manifest_path = target_dir / "manifest.json"

                    target_dir.mkdir(parents=True, exist_ok=True)
                    sandbox_dir.mkdir(parents=True, exist_ok=True)

                    manifest_payload = {
                        "project": details["project"],
                        "created_at": details["timestamp"],
                        "sandbox": str(sandbox_dir),
                        "metadata": metadata or {},
                    }
                    manifest_path.write_text(
                        json.dumps(manifest_payload, indent=2, sort_keys=True),
                        encoding="utf-8",
                    )

                    readme_path = sandbox_dir / "README.txt"
                    if not readme_path.exists():
                        readme_path.write_text(
                            "Offline sandbox created for Codex deployment. Add packaging artefacts here.",
                            encoding="utf-8",
                        )

                    details.update(
                        {
                            "output_dir": str(target_dir),
                            "manifest": str(manifest_path),
                            "sandbox_root": str(sandbox_dir),
                        }
                    )
                    return details
                '''
            ).strip()
            + "\n",
        )
        _write_text(
            deployment_pkg / "__init__.py",
            textwrap.dedent(
                '''
                """Deployment helpers for Codex ML."""

                from __future__ import annotations

                from .cloud import provision_stack

                __all__ = ["provision_stack"]
                '''
            ).strip()
            + "\n",
        )
        updated.append(str(cloud_path.relative_to(ctx.root)))
    return updated


def phase_controlled_pruning(ctx: TaskContext) -> Dict[str, Any]:
    docs_updated = _ensure_deferred_docs(ctx)
    modules = _ensure_deferred_modules(ctx)
    return {"deferred_docs_updated": docs_updated, "modules": modules}


def _update_changelog(ctx: TaskContext, summary_lines: Iterable[str]) -> bool:
    if not ctx.changelog_path.exists():
        _write_text(ctx.changelog_path, "# Codex Changelog\n\n")
    existing = ctx.changelog_path.read_text(encoding="utf-8")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    header = f"## {today} – Codex task sequence automation\n"
    entry = "\n".join([header, *summary_lines, ""]) + "\n"
    if header in existing:
        return False
    if ctx.dry_run:
        return False
    with ctx.changelog_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return True


def _run_pytest(ctx: TaskContext) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=ctx.root,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - subprocess failure
        _append_error(ctx, 601, "pytest", exc, "Invoking pytest")
        return {"status": "error", "code": None, "output": str(exc)}

    payload = {
        "status": "passed" if result.returncode == 0 else "failed",
        "code": result.returncode,
        "output": result.stdout + result.stderr,
    }
    _write_text(ctx.log_dir / "pytest_results.json", json.dumps(payload, indent=2))
    if result.returncode != 0:
        _append_error(
            ctx,
            602,
            "pytest",
            RuntimeError(f"pytest exited with {result.returncode}"),
            "See pytest_results.json for details",
        )
    return payload


def _archive_artifacts(ctx: TaskContext) -> None:
    with zipfile.ZipFile(ctx.archive_path, "w") as archive:
        for folder in (ctx.log_dir, ctx.reports_dir):
            if not folder.exists():
                continue
            for file in folder.rglob("*"):
                if file.is_file():
                    archive.write(file, arcname=str(file.relative_to(ctx.root)))


def _quality_test_stub_mapping(ctx: TaskContext) -> tuple[str, str]:
    try:
        data = json.loads(ctx.capability_mapping.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        return ("stub_mapping", "PASS" if data else "WARN")
    except Exception as exc:
        _append_error(ctx, 701, "quality_stub_mapping", exc, "Validating capability mapping")
        return ("stub_mapping", "FAIL")


def _quality_test_evaluation_loop(ctx: TaskContext) -> tuple[str, str]:
    if torch is None or DataLoader is None:
        return ("evaluation_loop", "SKIP")
    from training.functional_training import evaluate_batches  # local import

    class _ToyDataset(torch.utils.data.Dataset):
        def __len__(self) -> int:
            return 2

        def __getitem__(self, index: int):
            tensor = torch.ones(2, dtype=torch.float32) * (index + 1)
            return {"input_ids": tensor.clone(), "labels": tensor.clone()}

    class _ToyModel(torch.nn.Module):
        def forward(self, input_ids, labels):  # type: ignore[override]
            loss = torch.nn.functional.mse_loss(input_ids, labels)
            return {"logits": input_ids, "loss": loss}

    loader = DataLoader(_ToyDataset(), batch_size=1)
    metrics = evaluate_batches(
        _ToyModel(),
        loader,
        lambda data: {"perplexity": float(data[0].mean())},
        device=torch.device("cpu"),
    )
    return ("evaluation_loop", "PASS" if "perplexity" in metrics else "FAIL")


def _quality_test_gradient_accumulation(ctx: TaskContext) -> tuple[str, str]:
    target = ctx.root / "training" / "functional_training.py"
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    if "loss_t = loss_t / cfg.grad_accum" in text and "(step + 1) % cfg.grad_accum" in text:
        return ("gradient_accumulation", "PASS")
    return ("gradient_accumulation", "FAIL")


def _quality_test_config_load(ctx: TaskContext) -> tuple[str, str]:
    try:
        from configs.base_config import BASE_TRAINING_CONFIG, get_base_training_config

        cfg = get_base_training_config()
        cfg["model_name"] = "x"
        if BASE_TRAINING_CONFIG["model_name"] == "x":
            return ("config_load", "FAIL")
        return ("config_load", "PASS")
    except Exception as exc:
        _append_error(ctx, 704, "quality_config", exc, "Loading base config")
        return ("config_load", "FAIL")


def _quality_test_mlflow(ctx: TaskContext) -> tuple[str, str]:
    try:
        import mlflow  # type: ignore

        uri = mlflow.get_tracking_uri()
        if uri and uri.startswith("file://"):
            return ("mlflow_local", "PASS")
        return ("mlflow_local", "WARN")
    except Exception:
        return ("mlflow_local", "SKIP")


def run_quality_tests(ctx: TaskContext) -> List[tuple[str, str]]:
    return [
        _quality_test_stub_mapping(ctx),
        _quality_test_evaluation_loop(ctx),
        _quality_test_gradient_accumulation(ctx),
        _quality_test_config_load(ctx),
        _quality_test_mlflow(ctx),
    ]


def phase_finalization(ctx: TaskContext, mapping_count: int) -> Dict[str, Any]:
    summary_lines = [
        "- Added offline automation helpers and reproducibility artefacts.",
        "- Ensured evaluation loop and gradient accumulation helpers exist.",
        "- Documented deferred remote connectors and offline deployment gaps.",
        f"- Stub capability entries recorded: {mapping_count}.",
    ]
    changelog_updated = _update_changelog(ctx, summary_lines)
    pytest_result = _run_pytest(ctx)
    _archive_artifacts(ctx)
    quality = run_quality_tests(ctx)
    return {
        "changelog_updated": changelog_updated,
        "pytest": pytest_result,
        "quality_tests": quality,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute the Codex task sequence offline.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root directory.")
    parser.add_argument(
        "--log-dir", type=Path, default=Path("codex_logs"), help="Directory for logs and artefacts."
    )
    parser.add_argument(
        "--reports-dir", type=Path, default=Path("reports"), help="Directory for generated reports."
    )
    parser.add_argument("--seed", type=int, default=42, help="Global random seed.")
    parser.add_argument(
        "--grad-accum-steps",
        type=int,
        default=1,
        help="Gradient accumulation steps for validation.",
    )
    parser.add_argument(
        "--mlflow-dir", type=Path, default=Path("mlruns"), help="Local MLflow directory."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Plan actions without modifying tracked files."
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    ctx = TaskContext(
        root=args.root.resolve(),
        log_dir=(args.root / args.log_dir).resolve(),
        reports_dir=(args.root / args.reports_dir).resolve(),
        mlflow_dir=args.mlflow_dir,
        seed=args.seed,
        grad_accum_steps=args.grad_accum_steps,
        dry_run=bool(args.dry_run),
    )

    phase_preparation(ctx)
    entries = phase_search_and_mapping(ctx)
    best_effort_info = phase_best_effort(ctx)
    pruning_info = phase_controlled_pruning(ctx)
    finalization = phase_finalization(ctx, len(entries))

    summary = {
        "log_dir": str(ctx.log_dir),
        "reports_dir": str(ctx.reports_dir),
        "capability_entries": len(entries),
        "best_effort": best_effort_info,
        "pruning": pruning_info,
        "finalization": finalization,
        "archive": str(ctx.archive_path),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
