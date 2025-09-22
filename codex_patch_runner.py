#!/usr/bin/env python3
"""Offline helper to apply pending patches and capture local test metrics."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
STATUS_DIR = ROOT / ".codex" / "status"
PATCHES_DIR = ROOT / "patches" / "pending"
LOGS_DIR = ROOT / "logs"
DOCS_DIR = ROOT / "docs"


def ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def run(
    cmd: Sequence[str], *, check: bool = False, env: Optional[dict] = None
) -> Tuple[int, str, str]:
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
    )
    out, err = process.communicate()
    if check and process.returncode != 0:
        raise RuntimeError(f"Command failed ({process.returncode}): {' '.join(cmd)}\n{out}\n{err}")
    return process.returncode, out, err


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hard_disable_github_actions() -> None:
    workflows = ROOT / ".github" / "workflows"
    if not workflows.exists():
        return
    notice = "# DISABLED for offline-only execution\n"
    for file in workflows.glob("*.yml"):
        disabled = file.with_suffix(file.suffix + ".disabled")
        file.rename(disabled)
        text = disabled.read_text(encoding="utf-8")
        if not text.startswith(notice):
            disabled.write_text(notice + text, encoding="utf-8")
    for file in workflows.glob("*.yaml"):
        disabled = file.with_suffix(file.suffix + ".disabled")
        file.rename(disabled)
        text = disabled.read_text(encoding="utf-8")
        if not text.startswith(notice):
            disabled.write_text(notice + text, encoding="utf-8")


def error_capture(step: str, error: Exception | str, context: str) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    block = (
        f"Question for ChatGPT-5 {ts()}:\n"
        f"While performing [{step}], encountered the following error:\n{error}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    with (LOGS_DIR / "error_captures.log").open("a", encoding="utf-8") as handle:
        handle.write(block)


def apply_patch_file(patch: Path) -> bool:
    strategies = [
        ["git", "apply", "--index", "--reject", str(patch)],
        ["git", "apply", "-3", "--reject", str(patch)],
    ]
    for cmd in strategies:
        code, _, _ = run(cmd)
        if code == 0:
            return True
    patch_cmd = ["patch", "-p0", "-i", str(patch)]
    code, _, _ = run(patch_cmd)
    if code == 0:
        return True
    error_capture("apply_patch", f"failed to apply {patch.name}", f"cwd={ROOT}")
    return False


def run_nox(session: str) -> Tuple[int, str, str]:
    env = os.environ.copy()
    env.setdefault("NOX_OFFLINE", "1")
    return run(["nox", "-s", session], env=env)


def summarise_pytest(output: str) -> Dict[str, float]:
    total = passed = skipped = failed = 0
    match = re.search(r"collected\s+(\d+)\s+items", output)
    if match:
        total = int(match.group(1))
    match = re.search(r"(\d+)\s+passed", output)
    if match:
        passed = int(match.group(1))
    match = re.search(r"(\d+)\s+skipped", output)
    if match:
        skipped = int(match.group(1))
    match = re.search(r"(\d+)\s+failed", output)
    if match:
        failed = int(match.group(1))
    denominator = max(1, total - skipped)
    rate = passed / denominator
    return {"total": total, "passed": passed, "skipped": skipped, "failed": failed, "rate": rate}


def emit_status(metrics: Dict[str, float], applied: Sequence[str]) -> None:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    status_path = STATUS_DIR / "_codex_status_update-2025-09-21.md"
    lines = ["\n## Automation Summary (codex_patch_runner)\n"]
    if applied:
        lines.append("- Applied patches:\n")
        lines.extend(f"  - {name}\n" for name in applied)
    else:
        lines.append("- No patches applied (directory empty).\n")
    lines.append(
        "- Pytest metrics: total={total}, passed={passed}, skipped={skipped}, failed={failed}, rate={rate:.2%}\n".format(
            **metrics
        )
    )
    with status_path.open("a", encoding="utf-8") as handle:
        handle.writelines(lines)


def write_manifest(paths: Iterable[Path]) -> None:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        entries.append(
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    manifest_path = STATUS_DIR / f"manifest-{ts().replace(':', '-')}.json"
    write(manifest_path, json.dumps(entries, indent=2))


def gather_targets() -> List[Path]:
    targets = [
        ROOT / "codex_patch_runner.py",
        ROOT / "codex_task_sequence.py",
        STATUS_DIR / "_codex_status_update-2025-09-21.md",
    ]
    targets.append(DOCS_DIR / "gaps_report.md")
    targets.append(DOCS_DIR / "pruning_log.md")
    targets.extend(sorted(PATCHES_DIR.glob("*.patch")))
    return targets


def run_sequence(dry_run: bool = False) -> Dict[str, object]:
    hard_disable_github_actions()
    applied: List[str] = []
    if PATCHES_DIR.exists():
        for patch in sorted(PATCHES_DIR.glob("*.patch")):
            if dry_run:
                applied.append(f"(dry-run) {patch.name}")
                continue
            if apply_patch_file(patch):
                applied.append(patch.name)
    code, out, err = run(
        [
            "python",
            "-c",
            "import compileall,sys; sys.exit(0 if compileall.compile_dir('.', quiet=1) else 1)",
        ]
    )
    if code != 0:
        error_capture("py_compile", err or out, "compileall")
    code, out, err = run_nox("tests")
    metrics = summarise_pytest(out + "\n" + err)
    if code != 0:
        error_capture("nox -s tests", err or out, "nox")
    emit_status(metrics, applied)
    write_manifest(gather_targets())
    return {"applied": applied, "metrics": metrics, "nox_returncode": code}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply pending patches and run offline gates.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Inspect pending patches without applying them."
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        result = run_sequence(dry_run=args.dry_run)
    except Exception as exc:  # pragma: no cover - defensive
        error_capture("run", exc, "codex_patch_runner")
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get("nox_returncode") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
