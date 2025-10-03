"""Orchestrate local LLM-powered auto-fixes for staged changes."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List

from tools import ledger
from tools.llm_bridge import BridgeResponse, request_patch
from tools.validate_patch import ValidationResult, validate_patch

ERROR_LOG = Path(".codex/errors.ndjson")


def _staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    return result.stdout


def _tail_errors(limit: int = 20) -> str:
    if not ERROR_LOG.exists():
        return ""
    try:
        lines = ERROR_LOG.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-limit:])


def _run_checks(files: List[str]) -> tuple[int, str]:
    override = os.environ.get("CODEX_AUTO_FIX_CHECK_CMD")
    if override:
        if "{files}" in override:
            file_arg = " ".join(shlex.quote(path) for path in files)
            override_cmd = override.replace("{files}", file_arg)
        else:
            override_cmd = override
        cmd = shlex.split(override_cmd)
    else:
        cmd = ["pre-commit", "run", "--hook-stage", "pre-commit"]
        if files:
            cmd.extend(["--files", *files])
        else:
            cmd.append("--all-files")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output


def _append_ledger(event: str, status: str, data: dict | None = None) -> None:
    payload = {"event": event, "status": status, "data": data or {}}
    ledger.append_event(payload)


def _apply_patch(patch: str) -> bool:
    proc = subprocess.run(
        ["git", "apply", "--index", "--allow-empty", "--whitespace=nowarn", "-"],
        input=patch,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return False
    return True


def _rollback_patch(patch: str) -> None:
    subprocess.run(
        ["git", "apply", "--reverse", "--index", "--allow-empty", "--whitespace=nowarn", "-"],
        input=patch,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main(argv: list[str]) -> int:
    if os.environ.get("CODEX_AUTO_FIX_ENABLED", "0") != "1":
        print("[llm-auto-fix] CODEX_AUTO_FIX_ENABLED!=1 -> skipping")
        return 0

    files = _staged_files()
    if not files:
        print("[llm-auto-fix] no staged files detected; nothing to fix")
        return 0

    rc, check_output = _run_checks(files)
    if rc == 0:
        print("[llm-auto-fix] checks already passing; nothing to do")
        return 0

    diff = _staged_diff()
    if not diff.strip():
        print("[llm-auto-fix] staged diff empty; aborting")
        return rc

    error_tail = _tail_errors()
    combined_errors = check_output.strip()
    if error_tail:
        combined_errors = (
            f"{combined_errors}\n\nRecent errors (tail):\n{error_tail}"
            if combined_errors
            else error_tail
        )

    metadata = {"staged_files": len(files)}
    response: BridgeResponse | None = request_patch(diff, combined_errors, metadata)
    if not response:
        _append_ledger(
            "llm_patch_generated",
            "skipped",
            {"reason": "no-response", "files": len(files)},
        )
        return rc

    validation: ValidationResult = validate_patch(response.patch)
    if not validation.ok:
        _append_ledger(
            "llm_patch_apply",
            "rejected",
            {
                "errors": validation.errors,
                "files": validation.files,
                "artifact": str(response.artifact_path) if response.artifact_path else None,
            },
        )
        print("[llm-auto-fix] validation failed:")
        for err in validation.errors:
            print(f"  - {err}")
        return rc

    _append_ledger(
        "llm_patch_generated",
        "ok",
        {
            "files": validation.files,
            "added": validation.added_lines,
            "removed": validation.removed_lines,
            "artifact": str(response.artifact_path) if response.artifact_path else None,
        },
    )

    if not _apply_patch(response.patch):
        _append_ledger(
            "llm_patch_apply",
            "failed",
            {
                "reason": "apply-error",
                "artifact": str(response.artifact_path) if response.artifact_path else None,
            },
        )
        return rc

    rerun_rc, rerun_output = _run_checks(files)
    if rerun_rc != 0:
        print("[llm-auto-fix] checks still failing after patch; rolling back")
        _rollback_patch(response.patch)
        _append_ledger(
            "llm_patch_apply",
            "failed",
            {
                "reason": "post-check-failure",
                "output": rerun_output,
                "artifact": str(response.artifact_path) if response.artifact_path else None,
            },
        )
        return rerun_rc

    _append_ledger(
        "llm_patch_apply",
        "applied",
        {
            "files": validation.files,
            "artifact": str(response.artifact_path) if response.artifact_path else None,
        },
    )
    print("[llm-auto-fix] patch applied and checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
