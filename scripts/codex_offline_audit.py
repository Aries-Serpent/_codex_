#!/usr/bin/env python3
"""Offline Codex repository audit orchestrator.

This script executes a deterministic, offline audit pipeline composed of eight
phases.  It stitches together existing helper modules inside the repository to
generate structured artifacts that capture repository structure, capability
signals, reproducibility metadata, and smoke-test results.

The implementation follows the plan provided in the task prompt.  Every phase
attempts to emit its expected artifacts even when intermediate steps fail.
Errors are captured in a canonical "Error Capture Block" format and persisted
to both ``errors_log.md`` and ``errors.json``.

Usage
-----

```
python scripts/codex_offline_audit.py --repo-root . --output-dir _codex_reports/$(date +%F)
```

The script is intentionally offline: it does not perform any network calls and
avoids touching CI workflows.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List


# Ensure repository modules are importable when script is invoked directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from scripts import repo_audit  # type: ignore  # noqa: E402
from src.utils.logging_factory import init_logging  # noqa: E402
from src.utils.checkpoint import load_checkpoint, save_checkpoint  # noqa: E402
from src.training.simple_trainer import SimpleTrainer  # noqa: E402
from src.tokenizer.fast_tokenizer import FastTokenizerWrapper  # noqa: E402
from src.experiments import manager as experiment_manager  # noqa: E402


@dataclass
class PhaseResult:
    """Outcome metadata for a single phase."""

    name: str
    success: bool
    message: str


@dataclass
class AuditContext:
    """Shared execution context for the audit run."""

    repo_root: Path
    output_dir: Path
    logger: Any
    errors: List[Dict[str, Any]] = field(default_factory=list)
    phase_results: List[PhaseResult] = field(default_factory=list)
    audit_data: Dict[str, Any] = field(default_factory=dict)
    env_info: Dict[str, Any] = field(default_factory=dict)
    capability_matrix: Dict[str, Any] = field(default_factory=dict)
    reproducibility: Dict[str, Any] = field(default_factory=dict)


def timestamp() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def record_error(
    ctx: AuditContext,
    phase_number: int,
    phase_description: str,
    exc: Exception,
    context: str,
) -> None:
    message = str(exc)
    block = (
        f"Question from ChatGPT @codex {timestamp()}:\n"
        f"While performing [{phase_number}:{phase_description}], encountered the following error: {message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )
    ctx.logger.error(block)
    ctx.errors.append(
        {
            "timestamp": timestamp(),
            "phase": phase_number,
            "step": phase_description,
            "error_message": message,
            "context": context,
            "formatted_block": block,
        }
    )


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(text)


def gather_python_env() -> Dict[str, Any]:
    import platform

    return {
        "python_version": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "python_build": platform.python_build(),
    }


def parse_requirements(req_path: Path) -> List[str]:
    entries: List[str] = []
    try:
        for line in req_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)
    except Exception:
        pass
    return entries


def detect_seed_calls(repo_root: Path) -> Dict[str, Any]:
    patterns = {
        "torch.manual_seed": 0,
        "random.seed": 0,
        "np.random.seed": 0,
        "numpy.random.seed": 0,
    }
    locations: Dict[str, List[str]] = {k: [] for k in patterns}
    for path in repo_root.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in patterns:
            if pattern in text:
                patterns[pattern] += text.count(pattern)
                locations[pattern].append(str(path.relative_to(repo_root)))
    return {"counts": patterns, "locations": locations}


def run_phase(
    ctx: AuditContext,
    phase_number: int,
    name: str,
    func,
) -> None:
    ctx.logger.info("Starting phase %s: %s", phase_number, name)
    try:
        func()
        ctx.phase_results.append(PhaseResult(name=name, success=True, message="completed"))
        ctx.logger.info("Completed phase %s: %s", phase_number, name)
    except Exception as exc:  # noqa: BLE001
        record_error(ctx, phase_number, name, exc, context=name)
        ctx.phase_results.append(PhaseResult(name=name, success=False, message=str(exc)))
        ctx.logger.warning("Phase %s degraded: %s", phase_number, name)


def run_preparation(ctx: AuditContext) -> None:
    env_info = gather_python_env()
    requirements = {}
    for candidate in ["requirements.txt", "requirements-dev.txt", "pyproject.toml"]:
        path = ctx.repo_root / candidate
        if path.exists():
            requirements[candidate] = (
                parse_requirements(path) if path.suffix == ".txt" else "present"
            )
    env_info["requirements"] = requirements
    env_info["environment_variables"] = {
        k: os.environ.get(k)
        for k in sorted(os.environ)
        if k.startswith("CODEX") or k in {"PYTHONPATH", "VIRTUAL_ENV"}
    }
    ctx.env_info = env_info
    write_json(ctx.output_dir / "env_report.json", env_info)

    git_meta: Dict[str, Any] = {}
    try:
        git_meta["commit"] = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ctx.repo_root)
            .decode()
            .strip()
        )
    except Exception as exc:  # noqa: BLE001
        record_error(ctx, 1, "git metadata", exc, "git rev-parse")
    for cmd_name, args in {
        "status": ["git", "status", "--porcelain"],
        "diff_names": ["git", "diff", "--name-only"],
    }.items():
        try:
            git_meta[cmd_name] = (
                subprocess.check_output(args, cwd=ctx.repo_root)
                .decode("utf-8", errors="ignore")
                .strip()
                .splitlines()
            )
        except Exception as exc:  # noqa: BLE001
            record_error(ctx, 1, f"git {cmd_name}", exc, " ".join(args))
    write_json(ctx.output_dir / "git_meta.json", git_meta)
    if git_meta.get("commit"):
        ctx.env_info["git_commit"] = git_meta["commit"]

    seed_info = detect_seed_calls(ctx.repo_root)
    write_json(ctx.output_dir / "seed_scan.json", seed_info)


def run_repo_mapping(ctx: AuditContext) -> None:
    audit_md = ctx.output_dir / "audit_raw.md"
    # Run the repo audit script in-process to avoid spawning external interpreters unnecessarily.
    sys_argv_backup = list(sys.argv)
    cwd_backup = Path.cwd()
    try:
        sys.argv = ["repo_audit", "--format", "markdown", "--output", str(audit_md)]
        os.chdir(ctx.repo_root)
        repo_audit.main()  # type: ignore[attr-defined]
    finally:
        sys.argv = sys_argv_backup
        os.chdir(cwd_backup)
    generated_audit = ctx.repo_root / "audit.json"
    if generated_audit.exists():
        shutil.move(str(generated_audit), ctx.output_dir / "audit.json")
        with (ctx.output_dir / "audit.json").open("r", encoding="utf-8") as fh:
            ctx.audit_data = json.load(fh)
    else:
        raise FileNotFoundError("audit.json was not generated by repo_audit script")

    # Derive stub density metrics
    total_stub_count = ctx.audit_data.get("stubs_total")
    if total_stub_count is None:
        total_stub_count = len(ctx.audit_data.get("stubs", []))
    total_py_lines = 0
    for path in ctx.repo_root.rglob("*.py"):
        try:
            total_py_lines += sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))
        except Exception:
            continue
    kloc = total_py_lines / 1000 if total_py_lines else 0
    ctx.audit_data["stub_density"] = {
        "total_python_lines": total_py_lines,
        "total_stub_count": total_stub_count,
        "stubs_per_kloc": total_stub_count / kloc if kloc else None,
    }
    write_json(ctx.output_dir / "audit_enriched.json", ctx.audit_data)


def infer_status(present: bool, partial: bool = False) -> str:
    if present and not partial:
        return "Implemented"
    if present and partial:
        return "Partially"
    if not present and partial:
        return "Stubbed"
    return "Missing"


def run_capability_extraction(ctx: AuditContext) -> None:
    repo_root = ctx.repo_root

    def find_files(patterns: List[str]) -> List[str]:
        matches: List[str] = []
        for pattern in patterns:
            for path in repo_root.rglob(pattern):
                matches.append(str(path.relative_to(repo_root)))
        return sorted(set(matches))

    def search_text(keywords: List[str]) -> List[str]:
        hits: List[str] = []
        for path in repo_root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if any(keyword in text for keyword in keywords):
                hits.append(str(path.relative_to(repo_root)))
        return sorted(set(hits))

    capability_matrix: Dict[str, Dict[str, Any]] = {}

    def add_capability(
        name: str, present_files: List[str], evidence: List[str], notes: str
    ) -> None:
        capability_matrix[name] = {
            "status": "Implemented" if present_files else "Missing",
            "evidence": present_files,
            "gaps": notes,
            "risk_summary": "" if present_files else "Capability not detected",
        }
        if present_files and notes:
            capability_matrix[name]["status"] = "Partially"

    capability_matrix["tokenization"] = {
        "status": (
            "Implemented"
            if (ctx.repo_root / "src/tokenizer/fast_tokenizer.py").exists()
            else "Missing"
        ),
        "evidence": find_files(["tokenizer.json", "tokenization/**", "src/tokenizer/*.py"]),
        "gaps": (
            "Validate encode/decode roundtrips and batching"
            if (ctx.repo_root / "src/tokenizer").exists()
            else "Tokenizer utilities absent"
        ),
        "risk_summary": (
            "Performance degradation"
            if (ctx.repo_root / "src/tokenizer").exists()
            else "No tokenizer implementation located"
        ),
    }

    capability_matrix["training_engine"] = {
        "status": (
            "Partially"
            if (ctx.repo_root / "src/training/simple_trainer.py").exists()
            else "Missing"
        ),
        "evidence": find_files(["src/training/*.py", "training/*.py"]),
        "gaps": "Add gradient accumulation, metrics hooks, and evaluation gates",
        "risk_summary": "Scaling and convergence risks without richer trainer",
    }

    capability_matrix["checkpointing_resume"] = {
        "status": (
            "Partially" if (ctx.repo_root / "src/utils/checkpoint.py").exists() else "Missing"
        ),
        "evidence": (
            ["src/utils/checkpoint.py"]
            if (ctx.repo_root / "src/utils/checkpoint.py").exists()
            else []
        ),
        "gaps": "Need retention policy and CUDA RNG restoration",
        "risk_summary": "Resuming training may be non-deterministic",
    }

    capability_matrix["logging_monitoring"] = {
        "status": (
            "Partially" if (ctx.repo_root / "src/utils/logging_factory.py").exists() else "Missing"
        ),
        "evidence": (
            ["src/utils/logging_factory.py"]
            if (ctx.repo_root / "src/utils/logging_factory.py").exists()
            else []
        ),
        "gaps": "Extend to capture system metrics and ensure offline-first integrations",
        "risk_summary": "Resource usage blind spots",
    }

    capability_matrix["experiment_tracking"] = {
        "status": "Partially" if search_text(["mlflow", "wandb"]) else "Missing",
        "evidence": search_text(["mlflow", "wandb"]),
        "gaps": "Ensure offline defaults and metadata capture",
        "risk_summary": "Experiments may be hard to reproduce",
    }

    capability_matrix["config_mgmt"] = {
        "status": (
            "Partially" if find_files(["configs/**/*.yaml", "hydra/**/*.yaml"]) else "Missing"
        ),
        "evidence": find_files(["configs/**/*.yaml", "hydra/**/*.yaml"]),
        "gaps": "Document overrides and versioning of configs",
        "risk_summary": "Config drift between runs",
    }

    capability_matrix["evaluation_metrics"] = {
        "status": "Partially" if search_text(["accuracy", "bleu", "metrics"]) else "Missing",
        "evidence": search_text(["accuracy", "bleu", "metric"]),
        "gaps": "Add offline evaluation harness",
        "risk_summary": "Model quality may be unverified",
    }

    capability_matrix["data_handling"] = {
        "status": (
            "Partially" if find_files(["data/**", "datasets/**", "src/data/*.py"]) else "Missing"
        ),
        "evidence": find_files(["data/**", "datasets/**", "src/data/*.py"]),
        "gaps": "Need deterministic splits and manifests",
        "risk_summary": "Dataset drift",
    }

    capability_matrix["security_safety"] = {
        "status": "Partially" if find_files(["bandit.yaml", "semgrep_rules/**"]) else "Missing",
        "evidence": find_files(["bandit.yaml", "semgrep_rules/**"]),
        "gaps": "Add dependency locking and secrets scanning",
        "risk_summary": "Exposure to vulnerabilities",
    }

    capability_matrix["internal_ci_test"] = {
        "status": "Implemented" if (ctx.repo_root / "noxfile.py").exists() else "Missing",
        "evidence": ["noxfile.py"] if (ctx.repo_root / "noxfile.py").exists() else [],
        "gaps": "Ensure sessions enforce pytest and lint",
        "risk_summary": "Changes may bypass test gates",
    }

    capability_matrix["deployment"] = {
        "status": "Partially" if find_files(["Dockerfile", "docker-compose.yml"]) else "Missing",
        "evidence": find_files(["Dockerfile", "docker-compose.yml"]),
        "gaps": "Review image hardening and runtime configs",
        "risk_summary": "Operational readiness risk",
    }

    capability_matrix["docs_examples"] = {
        "status": (
            "Partially" if find_files(["docs/**/*.md", "notebooks/**/*.ipynb"]) else "Missing"
        ),
        "evidence": find_files(["docs/**/*.md", "notebooks/**/*.ipynb"]),
        "gaps": "Ensure quickstarts contain reproducibility metadata",
        "risk_summary": "Onboarding friction",
    }

    capability_matrix["extensibility"] = {
        "status": "Partially" if search_text(["registry", "plugin"]) else "Missing",
        "evidence": search_text(["registry", "plugin"]),
        "gaps": "Add pluggable component registry",
        "risk_summary": "Difficult to add new backends",
    }

    ctx.capability_matrix = capability_matrix
    write_json(ctx.output_dir / "capability_matrix.json", capability_matrix)


def run_reproducibility(ctx: AuditContext) -> None:
    repo_root = ctx.repo_root

    seeds_info = ctx.output_dir / "seed_scan.json"
    seed_data = json.loads(seeds_info.read_text()) if seeds_info.exists() else {}
    lockfiles = [
        str(path.relative_to(repo_root))
        for path in repo_root.glob("**/requirements*.txt")
        if path.is_file()
    ]
    lockfiles += [
        str(path.relative_to(repo_root))
        for path in repo_root.glob("**/pyproject.toml")
        if path.is_file()
    ]

    reproducibility = {
        "seeds_present": any(count > 0 for count in seed_data.get("counts", {}).values()),
        "seed_details": seed_data,
        "rng_checkpoint_capture": (repo_root / "src/utils/checkpoint.py").exists(),
        "environment_lock": lockfiles,
        "data_split_determinism": "needs_review",
        "model_init_determinism": "needs_review",
        "recommendations": [
            "Ensure CUDA RNG restoration for multi-GPU training",
            "Capture git SHA and environment manifest alongside checkpoints",
            "Add deterministic dataset split utilities with checksum manifests",
        ],
    }
    ctx.reproducibility = reproducibility
    write_json(ctx.output_dir / "reproducibility.json", reproducibility)


def run_training_and_tokenizer(ctx: AuditContext) -> None:
    import traceback

    phase_number = 5
    trainer_result: Dict[str, Any] = {
        "status": "not_run",
    }
    trainer_log_lines: List[str] = []
    trainer_path = ctx.output_dir / "trainer_smoke.json"
    trainer_log_path = ctx.output_dir / "trainer_smoke.log"

    try:
        import torch
        from torch import nn, optim

        torch.manual_seed(1234)
        model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 4))
        optimizer = optim.SGD(model.parameters(), lr=0.01)
        trainer = SimpleTrainer(model=model, optimizer=optimizer, device="cpu")
        inputs = torch.randn(8, 16)
        labels = torch.randint(0, 4, (8,))
        loss_value = trainer.step((inputs, labels))
        trainer_log_lines.append(f"Initial training loss: {loss_value:.6f}")

        ckpt_path = ctx.output_dir / "tmp_trainer_checkpoint.pt"
        save_checkpoint(
            {
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
            },
            str(ckpt_path),
        )
        restored_state = load_checkpoint(str(ckpt_path))
        new_model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 4))
        new_model.load_state_dict(restored_state["model_state"])
        deviation = 0.0
        for p1, p2 in zip(model.parameters(), new_model.parameters()):
            deviation = max(deviation, float((p1 - p2).abs().max().item()))
        trainer_log_lines.append(f"Checkpoint parameter max deviation: {deviation:.6e}")
        trainer_result.update(
            {
                "status": "success",
                "loss": loss_value,
                "checkpoint_path": str(ckpt_path),
                "parameter_max_deviation": deviation,
            }
        )
    except Exception as exc:  # noqa: BLE001
        trainer_result.update(
            {
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
        record_error(ctx, phase_number, "trainer_smoke_test", exc, "SimpleTrainer synthetic step")

    write_json(trainer_path, trainer_result)
    write_text(trainer_log_path, "\n".join(trainer_log_lines))

    tokenizer_result: Dict[str, Any] = {"status": "not_run"}
    tokenizer_path = ctx.output_dir / "tokenizer_check.json"

    tokenizer_files = []
    for candidate in ["tokenizer.json", "tokenizer.model"]:
        tokenizer_files.extend(list(ctx.repo_root.rglob(candidate)))

    if tokenizer_files:
        tokenizer_file = tokenizer_files[0]
        try:
            tokenizer = FastTokenizerWrapper(str(tokenizer_file))
            encoded = tokenizer.encode_batch(
                ["hello world", "codex offline audit"], pad_to_length=8
            )
            decoded = tokenizer.decode(encoded[0])
            tokenizer_result.update(
                {
                    "status": "success",
                    "tokenizer_file": str(tokenizer_file.relative_to(ctx.repo_root)),
                    "encoded_batch": encoded,
                    "decoded_first": decoded,
                }
            )
        except Exception as exc:  # noqa: BLE001
            tokenizer_result.update(
                {
                    "status": "failed",
                    "tokenizer_file": str(tokenizer_file.relative_to(ctx.repo_root)),
                    "error": str(exc),
                }
            )
            record_error(ctx, phase_number, "tokenizer_check", exc, str(tokenizer_file))
    else:
        tokenizer_result.update(
            {
                "status": "skipped",
                "reason": "No tokenizer.json or tokenizer.model found",
            }
        )

    write_json(tokenizer_path, tokenizer_result)

    # Attempt to initialize experiment tracking in offline mode if mlflow is available.
    try:
        experiment_manager.init_experiment("codex_offline_audit")
    except Exception as exc:  # noqa: BLE001
        record_error(ctx, phase_number, "experiment_tracking_init", exc, "mlflow init")


def build_consolidated_report(ctx: AuditContext) -> None:
    today = _dt.date.today().isoformat()
    report_path = ctx.output_dir / f"_codex_status_update-{today}.md"

    audit_summary = ctx.audit_data or {}
    capability_matrix = ctx.capability_matrix or {}
    reproducibility = ctx.reproducibility or {}

    repo_map_summary = [
        "## Repo Map Summary",
        "",
        f"- Root directory: `{ctx.repo_root}`",
        f"- Total files scanned: {audit_summary.get('files_count', 'n/a')}",
        f"- Python LOC (approx): {audit_summary.get('stub_density', {}).get('total_python_lines', 'n/a')}",
        f"- Stub density (per KLOC): {audit_summary.get('stub_density', {}).get('stubs_per_kloc', 'n/a')}",
    ]

    capability_lines = [
        "## Capability Matrix",
        "",
        "| Capability | Status | Evidence | Gaps |",
        "|---|---|---|---|",
    ]
    for name, payload in sorted(capability_matrix.items()):
        evidence = "<br>".join(payload.get("evidence", [])[:5]) or "—"
        gaps = payload.get("gaps", "—")
        capability_lines.append(
            f"| {name} | {payload.get('status', 'n/a')} | {evidence} | {gaps} |"
        )

    reproducibility_lines = [
        "## Reproducibility Checklist",
        "",
        f"- Seeds detected: {reproducibility.get('seeds_present', False)}",
        f"- RNG checkpoint capture available: {reproducibility.get('rng_checkpoint_capture', False)}",
        f"- Environment lock files: {', '.join(reproducibility.get('environment_lock', [])) or 'None'}",
        "- Recommendations:",
    ]
    for rec in reproducibility.get("recommendations", []):
        reproducibility_lines.append(f"  - {rec}")

    errors_section = ["## Error Capture Summary", ""]
    if ctx.errors:
        errors_section.append(f"Total captured errors: {len(ctx.errors)}")
        for entry in ctx.errors:
            errors_section.append("")
            errors_section.append(entry["formatted_block"])
    else:
        errors_section.append("No errors captured during audit run.")

    quick_wins = [
        "## Key Gaps & Quick Wins",
        "",
    ]
    quick_win_items = [
        "Harden checkpoint RNG restoration across CPU/GPU devices.",
        "Add deterministic dataset split utilities with manifest outputs.",
        "Expand tokenizer coverage with roundtrip unit tests.",
        "Augment SimpleTrainer with evaluation hooks and metrics logging.",
        "Guard experiment tracking integrations for offline defaults.",
        "Capture git SHA and env manifest in saved artifacts.",
        "Add psutil-based resource logging to logging_factory.",
        "Create reproducible nox sessions for lint/type/test gates.",
        "Document quickstart for CPU-only smoke run.",
        "Add security scans (bandit/semgrep) to local gating instructions.",
    ]
    for item in quick_win_items[:10]:
        quick_wins.append(f"- {item}")

    phase_summary_lines = ["## Phase Results", "", "| Phase | Status | Notes |", "|---|---|---|"]
    for idx, phase in enumerate(ctx.phase_results, start=1):
        status = "PASS" if phase.success else "DEGRADED"
        phase_summary_lines.append(f"| {idx} - {phase.name} | {status} | {phase.message} |")

    report_sections = [
        "# _codex Offline Audit Status",
        "",
        *repo_map_summary,
        "",
        *capability_lines,
        "",
        *reproducibility_lines,
        "",
        *quick_wins,
        "",
        *errors_section,
        "",
        *phase_summary_lines,
    ]
    write_text(report_path, "\n".join(report_sections))


def finalize_errors(ctx: AuditContext) -> None:
    errors_json = ctx.output_dir / "errors.json"
    errors_md = ctx.output_dir / "errors_log.md"
    write_json(errors_json, ctx.errors)
    if ctx.errors:
        write_text(
            errors_md,
            "\n\n".join(entry["formatted_block"] for entry in ctx.errors),
        )
    else:
        write_text(errors_md, "No errors captured.")


def package_artifacts(ctx: AuditContext) -> None:
    artifacts: List[Dict[str, Any]] = []
    for path in sorted(ctx.output_dir.glob("**/*")):
        if path.is_file():
            digest = sha256(path.read_bytes()).hexdigest()
            segments = [digest[i : i + 4] for i in range(0, len(digest), 4)]
            artifacts.append(
                {
                    "name": str(path.relative_to(ctx.output_dir)),
                    "sha256_segments": segments,
                }
            )
    manifest = {
        "git_commit": ctx.env_info.get("git_commit") or "",
        "created_at": timestamp(),
        "artifacts": artifacts,
    }
    write_json(ctx.output_dir / "artifacts_manifest.json", manifest)


def summarize_console(ctx: AuditContext) -> None:
    print("\nAudit Phase Summary:")
    for idx, phase in enumerate(ctx.phase_results, start=1):
        status = "PASS" if phase.success else "DEGRADED"
        print(f"  Phase {idx}: {phase.name} -> {status}")
    print(f"\nArtifacts directory: {ctx.output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Codex repository audit")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to place generated artifacts (default: _codex_reports/<date>)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"Repository root not found: {repo_root}")

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = repo_root / "_codex_reports" / _dt.date.today().isoformat()

    output_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("CODEX_LOG_MODE", "offline")
    logger = init_logging(mode="offline", project="codex_offline_audit")

    ctx = AuditContext(repo_root=repo_root, output_dir=output_dir, logger=logger)

    phases = [
        (1, "Preparation", lambda: run_preparation(ctx)),
        (2, "Repository Mapping", lambda: run_repo_mapping(ctx)),
        (3, "Capability Signal Extraction", lambda: run_capability_extraction(ctx)),
        (4, "Reproducibility & Seeds", lambda: run_reproducibility(ctx)),
        (5, "Training & Tokenizer Smoke", lambda: run_training_and_tokenizer(ctx)),
        (6, "Consolidated Report", lambda: build_consolidated_report(ctx)),
        (7, "Error Capture", lambda: finalize_errors(ctx)),
        (8, "Final Packaging", lambda: package_artifacts(ctx)),
    ]

    for number, name, func in phases:
        run_phase(ctx, number, name, func)

    summarize_console(ctx)


if __name__ == "__main__":
    main()
