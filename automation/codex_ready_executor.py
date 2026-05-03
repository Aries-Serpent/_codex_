"""Codex-ready executor implementing the sequential workflow end-to-end.

This script operationalizes the YAML block in
`automation/codex_ready_task_sequence_v2.yaml`. It is offline-first, avoids
GitHub Actions, and captures artifacts for every phase.

Features:
- Preparation: environment snapshot and metadata harvest.
- Search & Mapping: stub scan + capability mapping + config alignment.
- README parsing: generate sanitized README copy removing dead references.
- Best-effort construction: log targeted fixes and run optional verifications.
- Error capture: render research questions for ChatGPT @codex.
- Finalization: consolidated status and residual risk report.

Usage:
  python automation/codex_ready_executor.py --root . --artifacts artifacts/codex_ready
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

ROOT_DEFAULT = Path(__file__).resolve().parent.parent


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class Finding:
    path: str
    line: int
    category: str
    snippet: str
    capability: str
    applied_fix: Optional[str] = None
    residual_risk: Optional[str] = None


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def run_command(cmd: list[str], cwd: Path) -> CommandResult:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return CommandResult(cmd, completed.returncode, completed.stdout, completed.stderr)


def snapshot_environment(root: Path, artifacts: Path) -> None:
    git_head = run_command(["git", "rev-parse", "HEAD"], cwd=root)
    env_snapshot = {
        "timestamp": now_iso(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "cwd": str(root),
        "git_head": git_head.stdout.strip(),
        "git_head_status": git_head.returncode,
    }
    write_json(artifacts / "env_snapshot.json", env_snapshot)


def load_metadata(root: Path, artifacts: Path) -> None:
    interesting = ["AUDIT_PROMPT.md", "pytest.ini", "noxfile.py", "policies/denylist.yaml"]
    lines: list[str] = [f"# Project metadata captured {now_iso()}\n"]
    for rel in interesting:
        path = root / rel
        if not path.exists():
            lines.append(f"- {rel}: missing")
            continue
        snippet = path.read_text(encoding="utf-8").splitlines()[:40]
        lines.append(f"- {rel}: present ({len(snippet)} lines captured)")
        lines.extend([f"  {line}" for line in snippet])
    write_text(artifacts / "project_metadata.md", "\n".join(lines))


def build_workspace_index(root: Path, artifacts: Path) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {
        "code": [],
        "configs": [],
        "tests": [],
        "docs": [],
        "scripts": [],
        "notebooks": [],
        "other": [],
    }
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel.startswith("artifacts/"):
            continue
        suffix = path.suffix
        if suffix == ".py":
            (
                buckets["tests"]
                if "tests/" in rel
                else buckets["scripts"] if "scripts/" in rel or "tools/" in rel else buckets["code"]
            ).append(rel)
        elif suffix in {".yaml", ".yml", ".json", ".ini", ".toml"}:
            buckets["configs"].append(rel)
        elif suffix in {".md", ".rst"}:
            buckets["docs"].append(rel)
        elif suffix == ".ipynb":
            buckets["notebooks"].append(rel)
        else:
            buckets["other"].append(rel)
    write_json(artifacts / "workspace_index.json", buckets)
    return buckets


CAPABILITY_KEYWORDS = {
    "token": "tokenization",
    "train": "training",
    "config": "configuration",
    "hydra": "configuration",
    "eval": "evaluation",
    "metric": "evaluation",
    "api": "deployment",
    "server": "deployment",
    "connector": "extensibility",
    "mlflow": "tracking",
    "tracking": "tracking",
    "dataset": "data",
    "security": "security",
}


def infer_capability(path: str) -> str:
    lowered = path.lower()
    for key, cap in CAPABILITY_KEYWORDS.items():
        if key in lowered:
            return cap
    return "general"


STUB_PATTERNS = [
    re.compile(r"TODO"),
    re.compile(r"NotImplementedError"),
    re.compile(r"pass\s+#\s*stub"),
]


def scan_stubs(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for file in root.rglob("*"):
        if file.is_dir() or file.suffix not in {".py", ".md", ".yaml", ".yml"}:
            continue
        rel = file.relative_to(root).as_posix()
        if rel.startswith(".git/") or rel.startswith("artifacts/"):
            continue
        for idx, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern in STUB_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=rel,
                            line=idx,
                            category=pattern.pattern,
                            snippet=line.strip(),
                            capability=infer_capability(rel),
                        )
                    )
    return findings


def map_capabilities(findings: list[Finding]) -> dict[str, list[dict[str, Any]]]:
    mapping: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        mapping.setdefault(finding.capability, []).append(
            {
                "path": finding.path,
                "line": finding.line,
                "category": finding.category,
                "snippet": finding.snippet,
            }
        )
    return mapping


def parse_readme(root: Path, artifacts: Path, apply: bool) -> dict[str, Any]:
    readme = root / "README.md"
    if not readme.exists():
        return {"status": "missing"}
    text = readme.read_text(encoding="utf-8")
    pattern = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)")
    dead_links: list[dict[str, str]] = []
    sanitized = text
    for match in pattern.finditer(text):
        target = match.group("target")
        if target.startswith("http"):
            continue
        target_path = (root / target).resolve()
        if not target_path.exists():
            dead_links.append({"label": match.group("label"), "target": target})
            sanitized = sanitized.replace(match.group(0), match.group("label"))
    write_json(artifacts / "readme_links.json", {"dead_links": dead_links})
    if apply and dead_links:
        backup = readme.with_suffix(".bak_codex_ready")
        backup.write_text(text, encoding="utf-8")
        write_text(readme, sanitized)
    else:
        write_text(artifacts / "README.sanitized.md", sanitized)
    return {"status": "processed", "dead_links": dead_links, "applied": apply}


def record_patch_log(artifacts: Path, findings: Iterable[Finding]) -> None:
    lines: list[str] = ["# Patch Log", f"Generated: {now_iso()}", ""]
    for finding in findings:
        applied = finding.applied_fix or "documented"
        residual = finding.residual_risk or "Review required"
        lines.append(f"- [{finding.capability}] {finding.path}:{finding.line} :: {finding.snippet}")
        lines.append(f"  - action: {applied}")
        lines.append(f"  - residual_risk: {residual}")
    write_text(artifacts / "patch_log.md", "\n".join(lines))


def verify_commands(root: Path, artifacts: Path) -> list[CommandResult]:
    commands = [
        ["python", "-m", "compileall", "automation/codex_ready_executor.py"],
        ["PYTEST_DISABLE_PLUGIN_AUTOLOAD=1", "pytest", "-q", "--disable-warnings", "--maxfail=1"],
    ]
    results: list[CommandResult] = []
    for raw in commands:
        if raw[0].startswith("PYTEST_DISABLE_PLUGIN_AUTOLOAD"):
            env = os.environ.copy()
            env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            cmd = raw[1:]
        else:
            env = None
            cmd = raw
        completed = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True, env=env, check=False
        )
        results.append(CommandResult(cmd, completed.returncode, completed.stdout, completed.stderr))
    payload = [asdict(r) for r in results]
    write_json(artifacts / "verification_results.json", payload)
    return results


def emit_error_question(
    artifacts: Path, step_number: str, step_description: str, error_message: str, context: str
) -> None:
    block = (
        f"> Question from ChatGPT @codex {now_iso()}:\n"
        f"> While performing [{step_number}:{step_description}], encountered the following error: {error_message} Context: {context}. "
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    path = artifacts / "error_questions.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    write_text(path, existing + block)


def status_report(
    artifacts: Path, findings: list[Finding], verification: list[CommandResult]
) -> None:
    lines = ["# Codex-ready Status", f"Generated: {now_iso()}", ""]
    lines.append("## Findings")
    if not findings:
        lines.append("- No stubs detected in scanned files.")
    else:
        for finding in findings:
            lines.append(
                f"- [{finding.capability}] {finding.path}:{finding.line} :: {finding.snippet}"
            )
    lines.append("\n## Verification")
    for result in verification:
        status = "pass" if result.returncode == 0 else "fail"
        lines.append(
            f"- {'✅' if status == 'pass' else '❌'} {' '.join(result.command)} (rc={result.returncode})"
        )
    lines.append("\n## Residual Risks")
    residuals = [f.residual_risk for f in findings if f.residual_risk]
    if residuals:
        for item in residuals:
            lines.append(f"- {item}")
    else:
        lines.append("- Residual risks documented per finding; review patch_log.md.")
    write_text(artifacts / "status_report.md", "\n".join(lines))


def run_sequence(
    root: Path, artifacts: Path, apply_readme: bool, max_errors: int, dry_run: bool
) -> int:
    ensure_dir(artifacts)
    errors = 0
    try:
        snapshot_environment(root, artifacts)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(
            artifacts, "1.1", "Environment snapshot", str(exc), "Preparing environment"
        )
        if errors >= max_errors:
            return 1
    try:
        load_metadata(root, artifacts)
        build_workspace_index(root, artifacts)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(artifacts, "1.2", "Metadata/indexing", str(exc), "Preparation phase")
    try:
        findings = scan_stubs(root)
        mapping = map_capabilities(findings)
        write_json(artifacts / "stub_report.json", [asdict(f) for f in findings])
        write_json(artifacts / "capability_mapping.json", mapping)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(artifacts, "2.1", "Stub scan", str(exc), "Scanning repository")
        findings = []
    try:
        parse_readme(root, artifacts, apply=apply_readme and not dry_run)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(artifacts, "3.0", "README parsing", str(exc), "Processing README")
    try:
        record_patch_log(artifacts, findings)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(artifacts, "3.1", "Patch log", str(exc), "Recording fixes")
    verification: list[CommandResult] = []
    try:
        if dry_run:
            verification = []
        else:
            verification = verify_commands(root, artifacts)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(
            artifacts, "3.2", "Verification", str(exc), "Running verification commands"
        )
    try:
        status_report(artifacts, findings, verification)
    except Exception as exc:  # noqa: BLE001
        errors += 1
        emit_error_question(artifacts, "6.1", "Status report", str(exc), "Finalization phase")
    return 0 if errors == 0 else 1


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Codex-ready sequential workflow.")
    parser.add_argument("--root", default=str(ROOT_DEFAULT), help="Repository root")
    parser.add_argument("--artifacts", default="artifacts/codex_ready", help="Artifact directory")
    parser.add_argument(
        "--apply-readme",
        action="store_true",
        help="Apply sanitized README edits in place (backs up first)",
    )
    parser.add_argument(
        "--max-errors", type=int, default=25, help="Maximum tolerated errors before abort"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Record actions without mutating tracked files"
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    artifacts = Path(args.artifacts).resolve()
    return run_sequence(root, artifacts, args.apply_readme, args.max_errors, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
