#!/usr/bin/env python3
"""
codex_audit_orchestrator.py

Offline orchestrator for the _codex_ repository audit and gap-closure workflow.
- Targets branches: main, 0D_base_
- Includes archived paths but clearly marks them as cold paths
- Produces artifacts under audit_artifacts/
- Never touches .github/workflows or enables CI

Intended to be run inside the Codex runtime / local clone:

    python codex_audit_orchestrator.py --steps 1.1 1.2 2.1
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import subprocess
import sys
import traceback
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- Configuration ---------------------------------------------------------------------------

REPO_ROOT_SENTINEL = ".git"

TARGET_BRANCHES = ["main", "0D_base_"]

ARCHIVED_PATH_PATTERNS = [
    "archive/",
    "archive/ removed",
    "temp/",
]

ACTIVE_ROOTS = [
    "_codex_",
    "codex_ml",
    "training",
    "tokenization",
    "configs",
    "hydra",
    "requirements",
    "tests",
    "tools",
    "nox_sessions",
    "monitoring",
    "docs",
]

AUDIT_ROOT = Path("audit_artifacts")
CONTEXT_DIR = AUDIT_ROOT / "context"
GAP_PLANS_DIR = AUDIT_ROOT / "gap_plans"
ERROR_CAPTURES_DIR = AUDIT_ROOT / "error_captures"
LOGS_DIR = AUDIT_ROOT / "logs"
REPORTS_DIR = AUDIT_ROOT / "reports"

ERROR_CAPTURE_TEMPLATE = (
    "Question for ChatGPT @codex {timestamp}:\n"
    "While performing [{step_number}:{step_description}], "
    "encountered the following error:\n"
    "{error_message}\n"
    "Context: {brief_context}\n"
    "What are the possible causes, and how can this be resolved while "
    "preserving intended functionality?\n\n"
)


@dataclasses.dataclass
class StepContext:
    phase_id: int
    step_id: str
    description: str


class StepFailure(RuntimeError):
    """Raised when a phase step fails and has already been captured."""

    def __init__(self, ctx: StepContext, original: BaseException):
        super().__init__(f"Step {ctx.phase_id}.{ctx.step_id} failed: {original}")
        self.ctx = ctx
        self.original = original


# ---- Utility helpers -------------------------------------------------------------------------


def log(msg: str) -> None:
    """Log to stdout and file."""

    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    line = f"[{timestamp}] {msg}"
    print(line)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logfile = LOGS_DIR / "audit_orchestrator.log"
    with logfile.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upward until we find a .git directory."""

    if start is None:
        start = Path.cwd().resolve()
    current = start
    while True:
        if (current / REPO_ROOT_SENTINEL).exists():
            return current
        if current.parent == current:
            raise RuntimeError("Could not locate repo root (.git not found)")
        current = current.parent


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a command and capture exit code, stdout, stderr."""

    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def safe_git(cmd: List[str], repo_root: Path) -> Optional[str]:
    code, out, err = run_cmd(["git"] + cmd, cwd=repo_root)
    if code != 0:
        log(f"git {' '.join(cmd)} failed: {err.strip()}")
        return None
    return out.strip() or None


def serialize_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def error_capture(exc: BaseException, ctx: StepContext, brief_context: str) -> None:
    """Record error in the standardized ChatGPT @codex format."""

    ERROR_CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    error_message = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    block = ERROR_CAPTURE_TEMPLATE.format(
        timestamp=timestamp,
        step_number=f"{ctx.phase_id}.{ctx.step_id}",
        step_description=ctx.description,
        error_message=error_message.strip(),
        brief_context=brief_context,
    )
    path = ERROR_CAPTURES_DIR / "error_captures_codex_questions.md"
    with path.open("a", encoding="utf-8") as f:
        f.write(block)
    log(f"Recorded error capture for step {ctx.phase_id}.{ctx.step_id}")


def phase_step(phase_id: int, step_id: str, description: str):
    """
    Decorator for phase steps.
    Handles error capture and logging in a consistent way.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ctx = StepContext(phase_id=phase_id, step_id=step_id, description=description)
            log(f"START {ctx.phase_id}.{ctx.step_id} - {ctx.description}")
            try:
                result = fn(ctx, *args, **kwargs)
                log(f"END   {ctx.phase_id}.{ctx.step_id} - OK")
                return result
            except Exception as exc:  # noqa: BLE001
                log(f"ERROR {ctx.phase_id}.{ctx.step_id} - {exc}")
                error_capture(exc, ctx, brief_context=f"args={args}, kwargs={kwargs}")
                raise StepFailure(ctx, exc) from exc

        wrapper.phase_id = phase_id
        wrapper.step_label = step_id
        wrapper.step_description = description
        return wrapper

    return decorator


# ---- Phase 1: Preparation --------------------------------------------------------------------


@phase_step(1, "1.1", "Resolve repo root and detect branches")
def step_1_1_resolve_repo_root_and_branches(ctx: StepContext) -> Dict[str, Any]:  # noqa: ARG001
    repo_root = find_repo_root()
    branch = safe_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root) or "UNKNOWN"
    branches_raw = safe_git(["branch", "--all", "--format", "%(refname:short)"], repo_root)
    branches = sorted(set((branches_raw or "").splitlines()))
    data = {
        "repo_root": str(repo_root),
        "current_branch": branch,
        "branches": branches,
        "target_branches": TARGET_BRANCHES,
    }
    serialize_json(CONTEXT_DIR / "repo_context.json", data)
    return data


@phase_step(1, "1.2", "Create local audit_artifacts directories")
def step_1_2_create_output_dirs(ctx: StepContext) -> None:  # noqa: ARG001
    for d in (AUDIT_ROOT, CONTEXT_DIR, GAP_PLANS_DIR, ERROR_CAPTURES_DIR, LOGS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


@phase_step(1, "1.3", "Snapshot environment and git SHAs")
def step_1_3_environment_snapshot(ctx: StepContext) -> None:  # noqa: ARG001
    repo_root = find_repo_root()
    python_version = sys.version.replace("\n", " ")
    uname_code, uname_out, _ = run_cmd(["uname", "-a"])
    uname = uname_out.strip() if uname_code == 0 else "UNKNOWN"
    branch_shas = {}
    for br in TARGET_BRANCHES:
        sha = safe_git(["rev-parse", br], repo_root)
        branch_shas[br] = sha or "UNKNOWN"
    snapshot = {
        "timestamp_utc": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "python_version": python_version,
        "uname": uname,
        "branch_shas": branch_shas,
    }
    serialize_json(CONTEXT_DIR / "environment_snapshot.json", snapshot)


# ---- Phase 2: Search & Mapping --------------------------------------------------------------


@phase_step(2, "2.1", "Enumerate top-level directories and classify archived vs active")
def step_2_1_list_top_level(ctx: StepContext) -> Dict[str, Any]:  # noqa: ARG001
    repo_root = find_repo_root()
    top_entries = []
    for entry in sorted(repo_root.iterdir(), key=lambda p: p.name):
        if not entry.is_dir():
            continue
        rel = entry.name
        classification = "archived" if any(p in rel for p in ARCHIVED_PATH_PATTERNS) else "active"
        top_entries.append({"name": rel, "classification": classification})
    serialize_json(CONTEXT_DIR / "repo_tree_overview.json", {"top_level": top_entries})
    return {"top_level": top_entries}


@phase_step(2, "2.2", "Scan code for stubs and TODOs")
def step_2_2_stub_scan(ctx: StepContext) -> None:  # noqa: ARG001
    repo_root = find_repo_root()
    patterns = ("TODO", "FIXME", "NotImplementedError", "pass  # stub", "pass  # TODO")
    stub_records: List[Dict[str, Any]] = []

    def should_scan(path: Path) -> bool:
        if any(part.startswith(".git") for part in path.parts):
            return False
        if "audit_artifacts" in path.parts:
            return False
        return path.suffix in {".py", ".md", ".sh", ".ipynb", ".yml", ".yaml"}

    for root, _, files in os.walk(repo_root):
        root_path = Path(root)
        for fname in files:
            path = root_path / fname
            if not should_scan(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                for pat in patterns:
                    if pat in line:
                        stub_records.append(
                            {
                                "file": str(path.relative_to(repo_root)),
                                "line": lineno,
                                "pattern": pat,
                                "snippet": line.strip(),
                            }
                        )
    serialize_json(CONTEXT_DIR / "stub_index.json", {"stubs": stub_records})


@phase_step(2, "2.3", "Map artifacts to capabilities (high-level)")
def step_2_3_capability_mapping(ctx: StepContext) -> None:  # noqa: ARG001
    """
    This is intentionally coarse: it uses directory names and simple heuristics
    to map modules to the capability categories from the audit prompt.
    """

    repo_root = find_repo_root()
    capability_map: Dict[str, Dict[str, Any]] = {}

    def record(cap: str, artifact: str) -> None:
        capability_map.setdefault(
            cap,
            {"artifacts": [], "inferred_gaps": [], "status": "Unknown"},
        )
        capability_map[cap]["artifacts"].append(artifact)

    dir_to_caps = {
        "tokenization": ["Tokenization"],
        "codex_ml": ["ChatGPT Codex Modeling", "Training Engine"],
        "training": ["Training Engine"],
        "hydra": ["Configuration Management"],
        "configs": ["Configuration Management"],
        "monitoring": ["Logging & Monitoring"],
        "tests": ["Internal CI/Test"],
        "nox_sessions": ["Internal CI/Test"],
        "deploy": ["Deployment"],
        "docs": ["Documentation & Examples"],
        "experiments": ["Experiment Tracking"],
        "models": ["Checkpointing & Resume"],
        "data": ["Data Handling"],
        "great_expectations": ["Data Handling"],
        "requirements": ["Security & Safety"],
        "semgrep_rules": ["Security & Safety"],
        "yaml": ["Configuration Management"],
    }

    for root, _, files in os.walk(repo_root):
        root_path = Path(root)
        rel_root = root_path.relative_to(repo_root)
        top_level = rel_root.parts[0] if rel_root.parts else ""
        caps = dir_to_caps.get(top_level)
        if not caps:
            continue
        for cap in caps:
            for f in files:
                record(cap, str(rel_root / f))

    for cap, info in capability_map.items():
        files = info["artifacts"]
        if not files:
            info["status"] = "Missing"
        elif any(f.startswith("tests/") or "/tests/" in f for f in files):
            info["status"] = "Partially Implemented"
        else:
            info["status"] = "Implemented"

    serialize_json(REPORTS_DIR / "capability_audit_table.json", capability_map)


# ---- Phase 3: Best-Effort Construction ------------------------------------------------------


@phase_step(3, "3.1", "Propose atomic diffs for high-signal gaps")
def step_3_1_propose_atomic_diffs(ctx: StepContext) -> None:  # noqa: ARG001
    GAP_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    patch_paths = {
        "mlflow_guard": GAP_PLANS_DIR / "0001_add_guarded_mlflow_init.diff",
        "hydra_defaults": GAP_PLANS_DIR / "0002_hydra_defaults_sanity.diff",
        "lora_wiring": GAP_PLANS_DIR / "0003_lora_peft_wiring.diff",
    }
    for key, path in patch_paths.items():
        if path.exists():
            continue
        path.write_text(
            f"# Placeholder unified diff for {key}\n"
            "# To be filled by ChatGPT @codex or human based on repo context.\n",
            encoding="utf-8",
        )
    serialize_json(
        GAP_PLANS_DIR / "atomic_diffs_index.json",
        {"patches": {k: str(p) for k, p in patch_paths.items()}},
    )


@phase_step(3, "3.2", "Suggest local test/gate definitions")
def step_3_2_test_gate_suggestions(ctx: StepContext) -> None:  # noqa: ARG001
    patch_path = GAP_PLANS_DIR / "test_gate_suggestions.diff"
    if patch_path.exists():
        return
    patch_path.write_text(
        "# Placeholder diff for nox/pytest gate improvements.\n"
        "# Safe to apply locally; does not touch .github/workflows.\n",
        encoding="utf-8",
    )


@phase_step(3, "3.3", "Draft reproducibility checklist proposal")
def step_3_3_repro_checklist(ctx: StepContext) -> None:  # noqa: ARG001
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = REPORTS_DIR / "_codex_reproducibility_checklist_proposed.md"
    if target.exists():
        return
    target.write_text(
        "# _codex_ Reproducibility Checklist (Proposed)\n\n"
        "- [ ] Random seeds set for Python, NumPy, and torch.\n"
        "- [ ] Training configs captured via Hydra/OmegaConf.\n"
        "- [ ] Dataset versions pinned and documented.\n"
        "- [ ] Environment snapshot stored (Python, OS, deps).\n"
        "- [ ] Checkpoints versioned with git SHA and config hash.\n",
        encoding="utf-8",
    )


# ---- Phase 4: Controlled Pruning ------------------------------------------------------------


@phase_step(4, "4.1", "Record deferred items")
def step_4_1_deferred_items(ctx: StepContext) -> None:  # noqa: ARG001
    serialize_json(REPORTS_DIR / "deferred_items.json", {"items": []})


@phase_step(4, "4.2", "Record archive-only pruning notes")
def step_4_2_archived_pruning_notes(ctx: StepContext) -> None:  # noqa: ARG001
    target = REPORTS_DIR / "archived_pruning_notes.md"
    if target.exists():
        return
    target.write_text(
        "# Archived Codepath Pruning Notes (Skeleton)\n\n"
        "- Use this file to justify why certain archive-only modules remain untouched.\n",
        encoding="utf-8",
    )


# ---- Phase 5: Error Capture Finalization ----------------------------------------------------


@phase_step(5, "5.1", "Ensure error capture file exists")
def step_5_1_error_capture_file(ctx: StepContext) -> None:  # noqa: ARG001
    path = ERROR_CAPTURES_DIR / "error_captures_codex_questions.md"
    if not path.exists():
        path.write_text("", encoding="utf-8")


# ---- Phase 6: Finalization ------------------------------------------------------------------


@phase_step(6, "6.1", "Write status update skeleton")
def step_6_1_status_update(ctx: StepContext) -> None:  # noqa: ARG001
    today = dt.date.today().isoformat()
    target = Path(f"_codex_status_update-{today}.md")
    if target.exists():
        return
    target.write_text(
        f"# 📍 _codex_: Status Update ({today})\n\n"
        "This file is a skeleton generated by `codex_audit_orchestrator.py`.\n"
        "Fill in Repo Map, Capability Audit Table, High-Signal Findings, Atomic Diffs,\n"
        "Local Tests & Gates, Reproducibility Checklist, and Deferred Items\n"
        "based on artifacts under `audit_artifacts/`.\n",
        encoding="utf-8",
    )


@phase_step(6, "6.2", "Emit follow-up Codex prompts skeleton")
def step_6_2_followup_prompts(ctx: StepContext) -> None:  # noqa: ARG001
    target = REPORTS_DIR / "codex_followup_prompts.md"
    if target.exists():
        return
    target.write_text(
        "# Codex Follow-up Prompts (Skeleton)\n\n"
        "1. Example Suggested Task Prompt for Codex (pass 1).\n"
        "2. Example Suggested Task Prompt for Codex (pass 2).\n"
        "3. Example Suggested Task Prompt for Codex (pass 3).\n",
        encoding="utf-8",
    )


# ---- Main orchestration ---------------------------------------------------------------------


PHASE_FUNCTIONS = [
    step_1_1_resolve_repo_root_and_branches,
    step_1_2_create_output_dirs,
    step_1_3_environment_snapshot,
    step_2_1_list_top_level,
    step_2_2_stub_scan,
    step_2_3_capability_mapping,
    step_3_1_propose_atomic_diffs,
    step_3_2_test_gate_suggestions,
    step_3_3_repro_checklist,
    step_4_1_deferred_items,
    step_4_2_archived_pruning_notes,
    step_5_1_error_capture_file,
    step_6_1_status_update,
    step_6_2_followup_prompts,
]


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline audit orchestrator for Aries-Serpent/_codex_.",
    )
    parser.add_argument(
        "--list-steps",
        action="store_true",
        help="List available steps and exit.",
    )
    parser.add_argument(
        "--steps",
        nargs="*",
        metavar="PHASE.STEP",
        help="Optional subset of steps to run, e.g. 1.1 2.2 6.1. "
        "If omitted, all known steps are executed.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.list_steps:
        print("Available steps:")
        for fn in PHASE_FUNCTIONS:
            label = getattr(fn, "step_label", fn.__name__)
            description = getattr(fn, "step_description", "")
            print(f" - {label} ({fn.__name__}): {description}")
        return 0

    log("Starting codex_audit_orchestrator run")

    requested_labels = set(args.steps or [])
    available_labels = {getattr(fn, "step_label", fn.__name__) for fn in PHASE_FUNCTIONS}

    if requested_labels:
        unknown_labels = requested_labels - available_labels
        if unknown_labels:
            log(f"Unknown --steps labels requested; ignoring: {sorted(unknown_labels)}")
        requested_labels = requested_labels & available_labels
        log(f"Executing only requested steps: {sorted(requested_labels)}")

    for fn in PHASE_FUNCTIONS:
        label = getattr(fn, "step_label", fn.__name__)

        if requested_labels and label not in requested_labels:
            log(f"Skipping {label} ({fn.__name__}) because it was not requested")
            continue

        log(f"Running {label} ({fn.__name__})")
        try:
            fn()
        except StepFailure as exc:
            log(f"Aborting after failure in {label}: {exc}")
            return 1

    log("Finished codex_audit_orchestrator run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

