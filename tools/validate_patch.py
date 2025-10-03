"""Validation helpers for LLM-generated patches."""

from __future__ import annotations

import ast
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

MAX_FILES = int(os.environ.get("CODEX_LLM_MAX_FILES", "10"))
MAX_LINE_CHANGES = int(os.environ.get("CODEX_LLM_MAX_LINE_CHANGES", "500"))
REJECT_PREFIXES = (".github/workflows/",)


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    added_lines: int = 0
    removed_lines: int = 0


def _repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError("Not inside a git repository")
    return Path(result.stdout.strip())


def _parse_patch(patch: str) -> tuple[list[str], int, int, list[str]]:
    files: list[str] = []
    errors: list[str] = []
    added = 0
    removed = 0
    current_old: str | None = None
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            current_old = None
            continue
        if line.startswith("--- "):
            current_old = line[4:].strip()
            continue
        if line.startswith("+++ "):
            target = line[4:].strip()
            if target == "/dev/null" and current_old:
                target = current_old
            if target.startswith("a/") or target.startswith("b/"):
                target = target[2:]
            if target and target != "/dev/null":
                files.append(target)
            continue
        if line.startswith("Binary files ") or line.startswith("GIT binary patch"):
            errors.append("binary patches are not supported")
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    ordered_files = list(dict.fromkeys(files))
    return ordered_files, added, removed, errors


def _check_ast(patch: str, files: Iterable[str], repo_root: Path, errors: list[str]) -> None:
    python_files = [f for f in files if f.endswith(".py")]
    if not python_files:
        return
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
        setup = subprocess.run(
            ["git", "read-tree", "HEAD"],
            cwd=repo_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        if setup.returncode != 0:
            errors.append("failed to prepare temporary index for validation")
            return
        apply = subprocess.run(
            ["git", "apply", "--cached", "--allow-empty", "--whitespace=nowarn", "-"],
            cwd=repo_root,
            env=env,
            input=patch,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if apply.returncode != 0:
            errors.append("failed to apply patch to temporary index for validation")
            return
        checkout_dir = Path(tmp) / "checkout"
        checkout_dir.mkdir(parents=True, exist_ok=True)
        checkout_cmd = [
            "git",
            "checkout-index",
            "--prefix",
            f"{checkout_dir.as_posix()}/",
        ]
        checkout_cmd.extend(python_files)
        checkout = subprocess.run(
            checkout_cmd,
            cwd=repo_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
        if checkout.returncode != 0:
            errors.append("failed to materialize files for syntax validation")
            return
        for rel_path in python_files:
            file_path = checkout_dir / rel_path
            if not file_path.exists():
                # Deleted files are fine.
                continue
            try:
                source = file_path.read_text(encoding="utf-8")
            except OSError:
                errors.append(f"unable to read {rel_path} for syntax validation")
                return
            try:
                ast.parse(source, filename=rel_path)
            except SyntaxError as exc:
                errors.append(f"python syntax error in {rel_path}: {exc.msg} (line {exc.lineno})")
                return


def validate_patch(patch: str) -> ValidationResult:
    stripped = patch.strip()
    if not stripped:
        return ValidationResult(ok=False, errors=["empty patch"], files=[])
    if "diff --git" not in stripped:
        return ValidationResult(
            ok=False,
            errors=["patch is missing 'diff --git' headers"],
            files=[],
        )

    repo_root = _repo_root()
    files, added, removed, parse_errors = _parse_patch(patch)
    errors: list[str] = list(parse_errors)

    for path in files:
        if any(path.startswith(prefix) for prefix in REJECT_PREFIXES):
            errors.append(f"patch targets protected path: {path}")

    total_changes = added + removed
    if len(files) > MAX_FILES:
        errors.append(
            f"patch touches {len(files)} files (limit {MAX_FILES}); refine the suggestion"
        )
    if total_changes > MAX_LINE_CHANGES:
        errors.append(
            f"patch modifies {total_changes} lines (limit {MAX_LINE_CHANGES}); please reduce scope"
        )

    if errors:
        return ValidationResult(
            False, errors=errors, files=files, added_lines=added, removed_lines=removed
        )

    check = subprocess.run(
        ["git", "apply", "--check", "--whitespace=nowarn", "-"],
        cwd=repo_root,
        input=patch,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check.returncode != 0:
        errors.append(check.stderr.strip() or "git apply --check failed")
        return ValidationResult(
            False, errors=errors, files=files, added_lines=added, removed_lines=removed
        )

    _check_ast(patch, files, repo_root, errors)
    if errors:
        return ValidationResult(
            False, errors=errors, files=files, added_lines=added, removed_lines=removed
        )

    return ValidationResult(True, errors=[], files=files, added_lines=added, removed_lines=removed)


__all__ = ["validate_patch", "ValidationResult"]
