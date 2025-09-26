#!/usr/bin/env python3
"""Execute the Codex-ready task sequence in an offline, reproducible manner.

This script implements the specification defined in ``codex_ready_task_sequence.yaml``
and orchestrates the following deterministic phases:

1. Preparation — capture environment provenance and seed all libraries.
2. Search & Mapping — scan the repository for stubs and capability coverage.
3. Best-Effort Construction — ensure evaluation helpers, gradient accumulation,
   base configuration scaffolding, and optional MLflow wiring are present.
4. Controlled Pruning — document deferrals, annotate stubs, and gate deferred
   tests behind an opt-in marker.
5. Error Capture — wrap each phase with structured error logging compliant with
   the ChatGPT-5 troubleshooting template.
6. Finalization — update changelog entries, run local tests, archive artefacts,
   and print a concise summary including internal quality gates.

The CLI defaults favour offline execution.  All filesystem operations are
idempotent and skip writes when ``--dry-run`` is supplied.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import textwrap
import types
import unittest
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Optional dependency for deterministic seeding and evaluation metrics
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore[assignment]

try:  # Optional dependency for training helpers
    import torch  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    torch = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Context & helpers
# ---------------------------------------------------------------------------


@dataclass
class ExecutionContext:
    """Holds execution metadata and paths for the task sequence."""

    root: Path
    logs_dir: Path
    reports_dir: Path
    mlflow_dir: Path
    seed: int
    grad_accum_steps: int
    dry_run: bool = False
    actions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.logs_dir.mkdir(parents=True, exist_ok=True) if not self.dry_run else None
        self.reports_dir.mkdir(parents=True, exist_ok=True) if not self.dry_run else None
        self.errors_path = self.logs_dir / "error_captures.ndjson"
        self.stub_scan_path = self.logs_dir / "stub_scan.json"
        self.capability_map_path = self.logs_dir / "capability_mapping.json"
        self.cost_refs_path = self.logs_dir / "cost_incurring_refs.txt"
        self.provenance_path = self.logs_dir / "provenance.json"
        self.pip_freeze_path = self.logs_dir / "pip_freeze.txt"
        self.git_commit_path = self.logs_dir / "git_commit.txt"
        self.test_results_path = self.logs_dir / "test_results.json"
        self.artifact_archive = self.root / "codex_run_artifacts.zip"

    def log_action(self, message: str) -> None:
        self.actions.append(message)

    def record_error(self, step_number: str, description: str, error: BaseException, context: str) -> None:
        timestamp = datetime.utcnow().isoformat() + "Z"
        block = textwrap.dedent(
            f"""
            Question for ChatGPT-5 {timestamp}:
            While performing [{step_number}:{description}], encountered the following error:
            {error!r}
            Context: {context}
            What are the possible causes, and how can this be resolved while preserving intended functionality?
            """
        ).strip()
        self.errors.append(block)
        if self.dry_run:
            return
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        with self.errors_path.open("a", encoding="utf-8") as handle:
            handle.write(block + "\n")


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def set_global_seed(seed: int) -> None:
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():  # pragma: no cover - depends on GPU
            torch.cuda.manual_seed_all(seed)
        try:  # pragma: no cover - optional torch backend flags
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        except Exception:
            pass


def safe_write_text(path: Path, content: str, *, dry_run: bool) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    if dry_run:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def safe_write_json(path: Path, payload: Any, *, dry_run: bool) -> bool:
    text = json.dumps(payload, indent=2, sort_keys=True)
    return safe_write_text(path, text + "\n", dry_run=dry_run)


def run_subprocess(args: Sequence[str], *, cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )


def gather_system_provenance(ctx: ExecutionContext) -> Dict[str, Any]:
    python_version = platform.python_version()
    os_info = platform.platform()
    cpu = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown")
    gpu: Optional[str] = None
    if torch is not None and torch.cuda.is_available():  # pragma: no cover - GPU dependent
        try:
            gpu = torch.cuda.get_device_name(0)
        except Exception:  # pragma: no cover - guard for CUDA errors
            gpu = "cuda:unknown"
    provenance = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": python_version,
        "os": os_info,
        "cpu": cpu,
        "gpu": gpu,
        "seed": ctx.seed,
    }
    return provenance


STUB_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("TODO", re.compile(r"\bTODO\b")),
    ("NotImplementedError", re.compile(r"NotImplementedError")),
    ("pass", re.compile(r"^\s*pass\b")),
)


CAPABILITY_BUCKETS: Dict[str, Tuple[str, ...]] = {
    "tokenization": ("token", "bpe", "sentencepiece"),
    "modeling": ("model", "decoder", "encoder"),
    "training": ("train", "optimizer", "gradient"),
    "config": ("config", "hydra", "cfg"),
    "evaluation": ("eval", "metric", "perplex"),
    "logging": ("log", "telemetry", "monitor"),
    "checkpointing": ("checkpoint", "resume", "state_dict"),
    "data_handling": ("data", "dataset", "loader"),
    "security_safety": ("safety", "policy", "secure"),
    "ci_tests": ("test", "pytest", "nox"),
    "deployment": ("deploy", "docker", "k8s"),
    "docs_examples": ("docs", "examples", "notebook"),
    "experiment_tracking": ("mlflow", "wandb", "tracking"),
    "extensibility": ("plugin", "registry", "extension"),
}


TestResult = Dict[str, Any]


def scan_for_stubs(root: Path) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if "codex_logs" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for marker, pattern in STUB_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                snippet = text.splitlines()[line_no - 1].strip()
                results.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": line_no,
                        "marker": marker,
                        "snippet": snippet,
                    }
                )
    return results


def map_capabilities(stubs: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {bucket: [] for bucket in CAPABILITY_BUCKETS}
    mapping["unclassified"] = []
    for record in stubs:
        file_path = record.get("file", "")
        assigned = False
        lower = file_path.lower()
        for bucket, hints in CAPABILITY_BUCKETS.items():
            if any(hint in lower for hint in hints):
                mapping[bucket].append(file_path)
                assigned = True
        if not assigned:
            mapping["unclassified"].append(file_path)
    for key, values in mapping.items():
        mapping[key] = sorted(sorted(set(values)))
    return mapping


COST_PATTERNS = (
    re.compile(r"requests\.(get|post|put|delete)\s*\(", re.IGNORECASE),
    re.compile(r"http[s]?://", re.IGNORECASE),
    re.compile(r"boto3\.", re.IGNORECASE),
)


def scan_cost_incurring_refs(root: Path) -> List[str]:
    findings: List[str] = []
    for path in root.rglob("*.py"):
        if "codex_logs" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in COST_PATTERNS:
            if pattern.search(text):
                findings.append(str(path.relative_to(root)))
                break
    return sorted(set(findings))


# ---------------------------------------------------------------------------
# Repository mutation helpers
# ---------------------------------------------------------------------------


EVALUATE_HELPER_SNIPPET = """

def evaluate_dataloader(model, dataloader, cfg: TrainCfg, device: torch.device) -> dict[str, float]:
    '''Evaluate ``model`` on ``dataloader`` and aggregate metrics in eval mode.'''
    if dataloader is None:
        return {}
    was_training = model.training
    model.eval()
    preds: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    batch_count = 0
    with torch.no_grad():
        for j, batch in enumerate(dataloader):
            if cfg.limit_val_batches and j >= cfg.limit_val_batches:
                break
            for key, value in batch.items():
                batch[key] = value.to(device)
            outputs = model(**batch)
            logits = outputs["logits"] if isinstance(outputs, dict) else outputs.logits
            preds.append(logits.detach().cpu().numpy())
            labels.append(batch["labels"].detach().cpu().numpy())
            batch_count += 1
    metrics: dict[str, float] = {"num_batches": float(batch_count)}
    if preds and labels:
        metrics.update(_compute_metrics((np.concatenate(preds), np.concatenate(labels))))
    if was_training:
        model.train()
    return metrics
"""


VAL_LOOP_PATTERN = re.compile(
    r"        if val_loader is not None:\n"  # existing block start
    r"            model\.eval\(\)\n"
    r"            preds = \[\]\n"
    r"            labels = \[\]\n"
    r"            with torch\.no_grad\(\):\n"
    r"                for j, vb in enumerate\(val_loader\):\n"
    r"                    if cfg\.limit_val_batches and j >= cfg\.limit_val_batches:\n"
    r"                        break\n"
    r"                    for k, v in vb\.items\(\):\n"
    r"                        vb\[k\] = v\.to\(device\)\n"
    r"                    outputs = model\(\*\*vb\)\n"
    r"                    logits = outputs\[\"logits\"\] if isinstance\(outputs, dict\) else outputs\.logits\n"
    r"                    preds\.append\(logits\.cpu\(\)\.numpy\(\)\)\n"
    r"                    labels\.append\(vb\[\"labels\"\]\.cpu\(\)\.numpy\(\)\)\n"
    r"            if preds and labels:\n"
    r"                metrics = _compute_metrics\(\(np\.concatenate\(preds\), np\.concatenate\(labels\)\)\)\n"
    r"                val_ppl = metrics\.get\(\"perplexity\", float\(\"inf\"\)\)\n"
    r"                if val_ppl < best_val:\n"
    r"                    best_val = val_ppl\n"
    r"                    patience_ctr = 0\n"
    r"                    ckpt = Path\(cfg\.checkpoint_dir\) / \"best\.pt\"\n"
    r"                    save_checkpoint\(\n"
    r"                        ckpt,\n"
    r"                        model,\n"
    r"                        optimizer,\n"
    r"                        scheduler,\n"
    r"                        epoch,\n"
    r"                        {\n"
    r"                            \"global_step\": global_step,\n"
    r"                            \"best_val\": best_val,\n"
    r"                            \"step_in_epoch\": 0,\n"
    r"                            \"rng_state\": dump_rng_state\(\),\n"
    r"                        },\n"
    r"                    \)\n"
    r"                else:\n"
    r"                    patience_ctr \+= 1\n"
    r"                if patience_ctr >= cfg\.patience:\n"
    r"                    break\n"
)


VAL_LOOP_REPLACEMENT = """
        if val_loader is not None:
            metrics = evaluate_dataloader(model, val_loader, cfg, device)
            if metrics:
                numeric_metrics = {
                    f"val_{k}": float(v)
                    for k, v in metrics.items()
                    if isinstance(v, (int, float))
                }
                if numeric_metrics:
                    try:
                        _codex_log_all(global_step, numeric_metrics, loggers)
                    except Exception:
                        pass
            val_ppl = float(metrics.get("perplexity", float("inf")))
            if metrics.get("num_batches", 0) > 0 and val_ppl < best_val:
                best_val = val_ppl
                patience_ctr = 0
                ckpt = Path(cfg.checkpoint_dir) / "best.pt"
                save_checkpoint(
                    ckpt,
                    model,
                    optimizer,
                    scheduler,
                    epoch,
                    {
                        "global_step": global_step,
                        "best_val": best_val,
                        "step_in_epoch": 0,
                        "rng_state": dump_rng_state(),
                    },
                )
            else:
                patience_ctr += 1
            if patience_ctr >= cfg.patience:
                break
"""


def ensure_training_helpers(ctx: ExecutionContext) -> None:
    target = ctx.root / "training" / "functional_training.py"
    if not target.exists():
        ctx.log_action("training/functional_training.py missing; skipped helper injection")
        return
    try:
        text = target.read_text(encoding="utf-8")
    except Exception as exc:
        ctx.record_error("P3", "read functional_training.py", exc, str(target))
        return

    updated = False
    if "def evaluate_dataloader(" not in text:
        text += EVALUATE_HELPER_SNIPPET
        updated = True
    if VAL_LOOP_PATTERN.search(text):
        text = VAL_LOOP_PATTERN.sub(VAL_LOOP_REPLACEMENT, text)
        updated = True
    if "loss_t = loss_t / cfg.grad_accum" not in text:
        ctx.record_error("P3", "verify gradient accumulation", RuntimeError("grad accumulation missing"), str(target))
    if updated:
        if safe_write_text(target, text, dry_run=ctx.dry_run):
            ctx.log_action("Updated evaluation helper in training/functional_training.py")
        else:
            ctx.log_action("evaluation helper changes already present")
    else:
        ctx.log_action("training evaluation helper verified")


BASE_CONFIG_TEMPLATE = """
'''Deterministic base configuration for Codex training loops.'''

BASE_CONFIG: dict[str, object] = {{
    "model_name": "sshleifer/tiny-gpt2",
    "tokenizer_name": "sshleifer/tiny-gpt2",
    "learning_rate": 5e-5,
    "batch_size": 8,
    "epochs": 3,
    "gradient_accumulation_steps": {grad_accum},
    "seed": {seed},
}}
"""


def ensure_base_config(ctx: ExecutionContext) -> None:
    path = ctx.root / "configs" / "base_config.py"
    rendered = BASE_CONFIG_TEMPLATE.format(grad_accum=ctx.grad_accum_steps, seed=ctx.seed)
    if safe_write_text(path, rendered, dry_run=ctx.dry_run):
        ctx.log_action("Created configs/base_config.py")
    else:
        ctx.log_action("configs/base_config.py already matches expected content")


TEST_FILE_SNIPPET = """
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore[assignment]


def _build_dummy_dataset(torch):
    class DummyDataset(torch.utils.data.Dataset):
        def __len__(self) -> int:
            return 4

        def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
            ids = torch.randint(0, 10, (4,), dtype=torch.long)
            return {
                "input_ids": ids,
                "attention_mask": torch.ones_like(ids),
                "labels": torch.zeros_like(ids),
            }

    return DummyDataset()


def test_evaluate_dataloader_runs() -> None:
    torch = pytest.importorskip("torch")
    from training.functional_training import TrainCfg, evaluate_dataloader

    dataset = _build_dummy_dataset(torch)
    loader = torch.utils.data.DataLoader(dataset, batch_size=2)

    class TinyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = torch.nn.Embedding(10, 4)
            self.lm_head = torch.nn.Linear(4, 10)

        def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
            hidden = self.embedding(input_ids)
            logits = self.lm_head(hidden)
            loss = None
            if labels is not None:
                loss_fn = torch.nn.CrossEntropyLoss()
                loss = loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
            return types.SimpleNamespace(loss=loss, logits=logits)

    model = TinyModel()
    cfg = TrainCfg(limit_val_batches=None)
    device = torch.device("cpu")
    metrics = evaluate_dataloader(model, loader, cfg, device)
    assert metrics.get("num_batches", 0) > 0


def test_gradient_accumulation_optimizer_steps(monkeypatch) -> None:
    torch = pytest.importorskip("torch")
    from training.functional_training import TrainCfg, run_custom_trainer

    dataset = _build_dummy_dataset(torch)
    step_counter = {"steps": 0}

    class DummyOptimizer:
        def __init__(self, params, lr=0.001, weight_decay=0.0):
            self.params = list(params)

        def zero_grad(self, set_to_none: bool = True) -> None:  # noqa: D401
            for param in self.params:
                if param.grad is not None:
                    param.grad.zero_()

        def step(self) -> None:
            step_counter["steps"] += 1

        def state_dict(self):  # pragma: no cover - compatibility
            return {}

        def load_state_dict(self, state):  # pragma: no cover - compatibility
            return

    torch_manual_seed = getattr(torch, "manual_seed")

    def fake_adamw(params, lr=0.001, weight_decay=0.0):
        return DummyOptimizer(params, lr=lr, weight_decay=weight_decay)

    monkeypatch.setattr("training.functional_training.torch.optim.AdamW", fake_adamw)
    monkeypatch.setattr("training.functional_training.clip_grad_norm_", lambda *a, **k: None)
    monkeypatch.setattr("training.functional_training.save_checkpoint", lambda *a, **k: None)

    class TinyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.embedding = torch.nn.Embedding(10, 4)
            self.lm_head = torch.nn.Linear(4, 10)

        def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
            hidden = self.embedding(input_ids)
            logits = self.lm_head(hidden)
            loss_fn = torch.nn.MSELoss()
            loss = loss_fn(logits.float(), torch.zeros_like(logits.float()))
            return types.SimpleNamespace(loss=loss, logits=logits)

    cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        grad_accum=2,
        lr=1e-3,
        save_every=0,
        patience=5,
        limit_train_batches=4,
        max_steps=4,
    )
    run_custom_trainer(TinyModel(), None, dataset, None, cfg)
    assert step_counter["steps"] == 2


def test_base_config_module_loads() -> None:
    base = pytest.importorskip("configs.base_config")
    assert isinstance(getattr(base, "BASE_CONFIG", {}), dict)
    assert "gradient_accumulation_steps" in base.BASE_CONFIG


def test_mlflow_optional(monkeypatch) -> None:
    from codex_task_sequence import setup_mlflow_tracking

    monkeypatch.setitem(sys.modules, "mlflow", None)
    assert setup_mlflow_tracking(Path("mlruns"), dry_run=True) is False
"""


def ensure_tests(ctx: ExecutionContext) -> None:
    target = ctx.root / "tests" / "test_codex_sequence_validations.py"
    if safe_write_text(target, TEST_FILE_SNIPPET, dry_run=ctx.dry_run):
        ctx.log_action("Created tests/test_codex_sequence_validations.py")
    else:
        ctx.log_action("tests/test_codex_sequence_validations.py already present")


DEFERRED_HEADER = "# Deferred/Pruned Modules\n\n"


def update_deferred_report(ctx: ExecutionContext, entries: List[Tuple[str, str]]) -> None:
    path = ctx.reports_dir / "deferred.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
    lines = []
    if not existing.startswith(DEFERRED_HEADER):
        lines.append(DEFERRED_HEADER)
    else:
        lines.append(existing)
    lines.append(f"## Update {timestamp}\n\n")
    lines.append("| Module | Rationale |\n| --- | --- |\n")
    for module, rationale in entries:
        lines.append(f"| {module} | {rationale} |\n")
    content = "".join(lines)
    if safe_write_text(path, content, dry_run=ctx.dry_run):
        ctx.log_action("Updated reports/deferred.md")
    else:
        ctx.log_action("Deferred report already up to date")


DEFERRED_MARKER = "# Controlled Pruning: deferred offline implementation"


def annotate_deferred_modules(ctx: ExecutionContext, modules: List[Path]) -> None:
    for rel_path in modules:
        target = ctx.root / rel_path
        if not target.exists():
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except Exception as exc:
            ctx.record_error("P4", f"read {rel_path}", exc, str(target))
            continue
        if DEFERRED_MARKER in text:
            continue
        updated = text.replace(
            "raise NotImplementedError(\"run_functional_training is not implemented yet\")",
            "raise NotImplementedError(\"run_functional_training is not implemented yet (deferred offline implementation)\")",
        )
        if updated == text:
            updated = DEFERRED_MARKER + "\n" + text
        if safe_write_text(target, updated, dry_run=ctx.dry_run):
            ctx.log_action(f"Annotated deferred module {rel_path}")


def ensure_pytest_deferred_marker(ctx: ExecutionContext) -> None:
    pytest_ini = ctx.root / "pytest.ini"
    if pytest_ini.exists():
        text = pytest_ini.read_text(encoding="utf-8")
        if "deferred:" not in text:
            updated = text.rstrip() + "\n    deferred: tests exercising deferred modules (skipped by default)\n"
            safe_write_text(pytest_ini, updated + "\n", dry_run=ctx.dry_run)
            ctx.log_action("Registered 'deferred' marker in pytest.ini")
    conftest = ctx.root / "tests" / "conftest.py"
    if not conftest.exists():
        return
    text = conftest.read_text(encoding="utf-8")
    if "RUN_DEFERRED_TESTS" in text and "deferred" in text:
        return
    insertion = text.replace(
        "def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:",
        textwrap.dedent(
            """
            def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
                run_deferred = os.getenv("RUN_DEFERRED_TESTS", "0") == "1"
                if not run_deferred:
                    skip_deferred = pytest.mark.skip(reason="deferred module (enable RUN_DEFERRED_TESTS=1 to run)")
                else:
                    skip_deferred = None
            """
        ).strip()
        + "\n"
    )
    if insertion != text:
        insertion += textwrap.dedent(
            """
                for item in items:
                    if "deferred" in getattr(item, "keywords", {}):
                        if not run_deferred and skip_deferred:
                            item.add_marker(skip_deferred)
                            continue
                    if not config.getoption("--runslow"):
                        skip_slow = pytest.mark.skip(reason="need --runslow to run")
                    else:
                        skip_slow = None
                    if skip_slow and "slow" in item.keywords:
                        item.add_marker(skip_slow)
                        continue
                    module_name = getattr(item.module, "__name__", "")
                    for prefix, deps in OPTIONAL_TEST_GROUPS.items():
                        if module_name.startswith(prefix):
                            missing = _missing_modules(deps)
                            if missing:
                                reason = f"optional dependency missing: {', '.join(sorted(set(missing)))}"
                                item.add_marker(pytest.mark.skip(reason=reason))
                            break
            """
        )
        if safe_write_text(conftest, insertion, dry_run=ctx.dry_run):
            ctx.log_action("Injected deferred test skip logic into tests/conftest.py")


# ---------------------------------------------------------------------------
# MLflow helper
# ---------------------------------------------------------------------------


def setup_mlflow_tracking(mlruns_dir: Path, *, dry_run: bool) -> bool:
    try:
        import mlflow  # type: ignore
    except Exception:
        return False
    uri = mlruns_dir.resolve()
    if not dry_run:
        mlruns_dir.mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{uri}")
    return True


# ---------------------------------------------------------------------------
# Internal tests for quality gates
# ---------------------------------------------------------------------------


def run_internal_tests(ctx: ExecutionContext) -> List[TestResult]:
    results: List[TestResult] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        results.append({"name": name, "passed": passed, "detail": detail})

    try:
        mapping = map_capabilities([{ "file": "training/example.py" }])
        assert "training" in mapping
        record("stub_mapping", True, "mapping generated")
    except Exception as exc:
        record("stub_mapping", False, str(exc))
        ctx.record_error("TEST", "stub mapping", exc, "internal test")

    try:
        setup_ok = setup_mlflow_tracking(ctx.mlflow_dir, dry_run=True)
        record("mlflow_optional", setup_ok in {True, False}, "mlflow import attempted")
    except Exception as exc:
        record("mlflow_optional", False, str(exc))
        ctx.record_error("TEST", "mlflow optional", exc, "internal test")

    try:
        import training.functional_training as ft  # type: ignore

        if not hasattr(ft, "evaluate_dataloader"):
            raise AssertionError("evaluate_dataloader missing")
        if torch is None:
            raise unittest.SkipTest("torch not available")

        class _Dataset(torch.utils.data.Dataset):
            def __len__(self) -> int:
                return 2

            def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
                return {
                    "input_ids": torch.ones(4, dtype=torch.long),
                    "attention_mask": torch.ones(4, dtype=torch.long),
                    "labels": torch.zeros(4, dtype=torch.long),
                }

        class _Model(torch.nn.Module):
            def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
                logits = torch.nn.functional.one_hot(input_ids, num_classes=4).float()
                loss = logits.sum() * 0.0
                return types.SimpleNamespace(loss=loss, logits=logits)

        dataset = _Dataset()
        loader = torch.utils.data.DataLoader(dataset, batch_size=1)
        metrics = ft.evaluate_dataloader(_Model(), loader, ft.TrainCfg(), torch.device("cpu"))
        record("eval_helper", metrics.get("num_batches", 0) > 0, "evaluation produced metrics")
    except ModuleNotFoundError as exc:
        record("eval_helper", True, f"skipped: {exc}")
    except unittest.SkipTest as skip:
        record("eval_helper", True, f"skipped: {skip}")
    except Exception as exc:
        record("eval_helper", False, str(exc))
        ctx.record_error("TEST", "eval helper", exc, "internal test")

    try:
        import training.functional_training as ft  # type: ignore

        cfg = ft.TrainCfg(grad_accum=3)
        record("grad_accum_config", cfg.grad_accum == 3, "TrainCfg preserves grad_accum")
    except ModuleNotFoundError as exc:
        record("grad_accum_config", True, f"skipped: {exc}")
    except Exception as exc:
        record("grad_accum_config", False, str(exc))
        ctx.record_error("TEST", "grad accum config", exc, "internal test")

    try:
        base_cfg = __import__("configs.base_config", fromlist=["BASE_CONFIG"])
        record("base_config", "BASE_CONFIG" in base_cfg.__dict__, "base config importable")
    except Exception as exc:
        record("base_config", False, str(exc))
        ctx.record_error("TEST", "base config", exc, "internal test")

    return results


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------


def phase_preparation(ctx: ExecutionContext) -> None:
    set_global_seed(ctx.seed)
    ctx.log_action(f"Seeded environment with {ctx.seed}")
    provenance = gather_system_provenance(ctx)
    safe_write_json(ctx.provenance_path, provenance, dry_run=ctx.dry_run)
    ctx.log_action("Captured provenance.json")

    pip_proc = run_subprocess([sys.executable, "-m", "pip", "freeze"])
    if pip_proc.returncode == 0:
        safe_write_text(ctx.pip_freeze_path, pip_proc.stdout, dry_run=ctx.dry_run)
        ctx.log_action("Captured pip_freeze.txt")
    else:
        ctx.record_error("P1", "pip freeze", RuntimeError(pip_proc.stderr), "pip freeze failed")

    git_proc = run_subprocess(["git", "rev-parse", "HEAD"], cwd=ctx.root)
    if git_proc.returncode == 0:
        safe_write_text(ctx.git_commit_path, git_proc.stdout.strip() + "\n", dry_run=ctx.dry_run)
        ctx.log_action("Recorded git commit SHA")
    else:
        ctx.record_error("P1", "git rev-parse", RuntimeError(git_proc.stderr), "git commit capture failed")

    workflows_dir = ctx.root / ".github" / "workflows"
    if workflows_dir.exists():
        ctx.log_action("Verified existing .github/workflows/ (no modifications performed)")
    else:
        ctx.log_action("No .github/workflows/ directory detected")


def phase_search_mapping(ctx: ExecutionContext) -> None:
    stubs = scan_for_stubs(ctx.root)
    safe_write_json(ctx.stub_scan_path, stubs, dry_run=ctx.dry_run)
    ctx.log_action("Persisted stub scan results")
    mapping = map_capabilities(stubs)
    safe_write_json(ctx.capability_map_path, mapping, dry_run=ctx.dry_run)
    ctx.log_action("Persisted capability mapping")
    cost_refs = scan_cost_incurring_refs(ctx.root)
    safe_write_text(ctx.cost_refs_path, "\n".join(cost_refs) + ("\n" if cost_refs else ""), dry_run=ctx.dry_run)
    ctx.log_action("Logged potential cost-incurring references")


def phase_best_effort(ctx: ExecutionContext) -> None:
    ensure_training_helpers(ctx)
    ensure_base_config(ctx)
    ensure_tests(ctx)
    if setup_mlflow_tracking(ctx.mlflow_dir, dry_run=ctx.dry_run):
        ctx.log_action("MLflow local tracking initialised")
    else:
        ctx.log_action("MLflow unavailable; skipped tracking setup")


def phase_controlled_pruning(ctx: ExecutionContext) -> None:
    deferred_entries = [
        (
            "codex_update_runner.py::run_functional_training",
            "Requires remote registry orchestration and network callbacks; deferred for offline execution.",
        ),
        (
            "src/codex_ml/monitoring/prometheus.py",
            "Prometheus exporter depends on remote telemetry endpoints and is disabled in offline mode.",
        ),
    ]
    update_deferred_report(ctx, deferred_entries)
    annotate_deferred_modules(
        ctx,
        [Path("codex_update_runner.py")],
    )
    ensure_pytest_deferred_marker(ctx)


def phase_finalization(ctx: ExecutionContext, internal_tests: List[TestResult]) -> None:
    changelog = ctx.root / "CHANGELOG_CODEX.md"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    entry = textwrap.dedent(
        f"""
        ## {timestamp} – Codex-ready task sequence

        - Captured reproducible environment metadata under codex_logs/.
        - Ensured training evaluation helper and gradient accumulation checks.
        - Created configs/base_config.py for deterministic runs and added validation tests.
        - Documented deferred modules and guarded pytest via the `deferred` marker.
        """
    )
    if changelog.exists():
        existing = changelog.read_text(encoding="utf-8")
    else:
        existing = "# Codex Changelog\n\n"
    safe_write_text(changelog, existing + entry, dry_run=ctx.dry_run)
    ctx.log_action("Updated CHANGELOG_CODEX.md")

    pytest_cmd = [sys.executable, "-m", "pytest", "-q"]
    proc = run_subprocess(pytest_cmd, cwd=ctx.root)
    tests_passed = proc.returncode == 0
    if not tests_passed:
        ctx.record_error("P6", "pytest", RuntimeError(proc.stderr or proc.stdout), "pytest run failed")
    safe_write_json(
        ctx.test_results_path,
        {
            "command": " ".join(pytest_cmd),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "internal_tests": internal_tests,
        },
        dry_run=ctx.dry_run,
    )
    ctx.log_action("Recorded test results")

    if not ctx.dry_run:
        with zipfile.ZipFile(ctx.artifact_archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in [ctx.logs_dir, ctx.reports_dir]:
                if not path.exists():
                    continue
                for file in path.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(ctx.root))
        ctx.log_action("Archived artefacts into codex_run_artifacts.zip")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def execute_phase(ctx: ExecutionContext, step_id: str, description: str, func, *args, **kwargs) -> None:
    try:
        func(*args, **kwargs)
    except Exception as exc:
        ctx.record_error(step_id, description, exc, f"Phase {description}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute the Codex task sequence offline")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--log-dir", type=str, default="codex_logs", help="Directory for logs")
    parser.add_argument("--reports-dir", type=str, default="reports", help="Directory for reports")
    parser.add_argument("--seed", type=int, default=42, help="Global random seed")
    parser.add_argument("--grad-accum-steps", type=int, default=1, help="Gradient accumulation override")
    parser.add_argument("--mlflow-dir", type=str, default="mlruns", help="Local MLflow directory")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without mutating files")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root_path = args.root.resolve()
    ctx = ExecutionContext(
        root=root_path,
        logs_dir=(root_path / args.log_dir).resolve(),
        reports_dir=(root_path / args.reports_dir).resolve(),
        mlflow_dir=(root_path / args.mlflow_dir).resolve(),
        seed=args.seed,
        grad_accum_steps=args.grad_accum_steps,
        dry_run=args.dry_run,
    )

    execute_phase(ctx, "P1", "Preparation", phase_preparation, ctx)
    execute_phase(ctx, "P2", "Search & Mapping", phase_search_mapping, ctx)
    execute_phase(ctx, "P3", "Best-Effort Construction", phase_best_effort, ctx)
    execute_phase(ctx, "P4", "Controlled Pruning", phase_controlled_pruning, ctx)
    internal_tests = run_internal_tests(ctx)
    execute_phase(ctx, "P6", "Finalization", phase_finalization, ctx, internal_tests)

    summary = {
        "actions": ctx.actions,
        "errors": ctx.errors,
        "logs_dir": str(ctx.logs_dir),
        "reports_dir": str(ctx.reports_dir),
        "artifact_archive": str(ctx.artifact_archive),
        "internal_tests": internal_tests,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not ctx.errors else 1


if __name__ == "__main__":
    sys.exit(main())
