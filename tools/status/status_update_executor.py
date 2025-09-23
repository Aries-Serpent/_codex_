#!/usr/bin/env python3
"""Automate status-update hygiene tasks for the `_codex_` repository."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / ".codex"
STATUS_DIR = CODEX_DIR / "status"
DEFAULT_CHANGELOG = STATUS_DIR / "status_update_change_log.md"
DEFAULT_JSON = STATUS_DIR / "status_update_scan.json"
DEFAULT_ERROR_LOG = STATUS_DIR / "status_update_errors.ndjson"


@dataclass
class ChangeLogEntry:
    """Structured entry for the status-update change log."""

    title: str
    details: Sequence[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [f"- **{self.title}**"]
        for note in self.details:
            lines.append(f"  - {note}")
        return "\n".join(lines)


class ErrorCaptureRecorder:
    """Emit error-capture prompts in the mandated format."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, step: str, error: str, context: Optional[Dict[str, str]] = None) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        prompt = textwrap.dedent(
            f""":::
Question for ChatGPT @codex {timestamp}:
While performing {step}, encountered the following error:
{error}
Context: {json.dumps(context or {}, sort_keys=True)}
What are the possible causes, and how can this be resolved while preserving intended functionality?
:::
"""
        ).strip()
        payload = {
            "timestamp": timestamp,
            "step": step,
            "error": error,
            "context": context or {},
            "prompt": prompt,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def normalise_readme_links(*, write: bool) -> Dict[str, Sequence[str]]:
    """Normalise README doc links and report adjustments."""

    readme_path = REPO_ROOT / "README.md"
    original_text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\]\((\.\/?docs\/[^)]+)\)")
    replacements: List[str] = []

    def _replace(match: re.Match[str]) -> str:
        target = match.group(1)
        normalised = re.sub(r"/+/", "/", target)
        normalised = normalised.lstrip("./")
        if normalised.startswith("docs/"):
            if normalised != target:
                replacements.append(f"{target} -> {normalised}")
            return f"]({normalised})"
        return match.group(0)

    new_text = pattern.sub(_replace, original_text)
    missing: List[str] = []
    for link in re.findall(r"\]\((docs/[^)]+)\)", new_text):
        link_path = REPO_ROOT / link
        if not link_path.exists():
            missing.append(link)

    if write and new_text != original_text:
        readme_path.write_text(new_text, encoding="utf-8")

    return {"updated": replacements, "missing": missing}


def build_repo_map() -> Dict[str, Sequence[str]]:
    """Summarise the repository layout for downstream embedding."""

    directories: Dict[str, List[str]] = {}
    for child in sorted(REPO_ROOT.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            directories[child.name] = sorted(p.name for p in child.iterdir() if p.is_file())[:10]
    key_files = [
        "pyproject.toml",
        "requirements-dev.txt",
        "Makefile",
        "noxfile.py",
        "codex_workflow.py",
    ]
    present_files = [item for item in key_files if (REPO_ROOT / item).exists()]
    return {"directories": directories, "key_files": present_files}


def scan_placeholders() -> List[Dict[str, object]]:
    """Locate sentinel placeholders that should feed the change log."""

    targets = [REPO_ROOT / "src", REPO_ROOT / "tools", REPO_ROOT / "scripts"]
    keywords = ("NotImplementedError", "TODO", "FIXME", "pass  # stub")
    findings: List[Dict[str, object]] = []
    for base in targets:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for idx, line in enumerate(text.splitlines(), start=1):
                if any(keyword in line for keyword in keywords):
                    findings.append(
                        {
                            "path": str(path.relative_to(REPO_ROOT)),
                            "line": idx,
                            "snippet": line.strip(),
                        }
                    )
    return findings


def synthesise_change_log(
    entries: Sequence[ChangeLogEntry], *, write: bool, path: Path = DEFAULT_CHANGELOG
) -> None:
    """Write the aggregated change log to disk when requested."""

    header = ["# Status Update Change Log", ""]
    body = [entry.render() for entry in entries]
    content = "\n".join(header + list(body)) + "\n"
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def write_json_snapshot(
    payload: Dict[str, object], *, write: bool, path: Path = DEFAULT_JSON
) -> None:
    """Persist the automation snapshot to JSON for reproducibility."""

    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(
    work_dir: Optional[Path] = None,
    *,
    write: bool = False,
    error_recorder: Optional[ErrorCaptureRecorder] = None,
) -> Dict[str, object]:
    """Execute the automation workflow and return collected artefacts."""

    del work_dir  # Present for parity with other runners.

    results: Dict[str, object] = {}

    try:
        readme_info = normalise_readme_links(write=write)
        results["readme_links"] = readme_info
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_1:README_LINK_NORMALISATION", repr(exc))
        results["readme_links_error"] = repr(exc)

    try:
        repo_map = build_repo_map()
        results["repo_map"] = repo_map
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_2:REPO_MAP", repr(exc))
        results["repo_map_error"] = repr(exc)

    try:
        placeholders = scan_placeholders()
        results["placeholders"] = placeholders
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_3:PLACEHOLDER_SCAN", repr(exc))
        results["placeholders_error"] = repr(exc)

    changelog_entries: List[ChangeLogEntry] = []

    readme_updates = results.get("readme_links", {})
    if isinstance(readme_updates, dict):
        updated = readme_updates.get("updated") or []
        missing = readme_updates.get("missing") or []
        if updated:
            changelog_entries.append(ChangeLogEntry("README link normalisation", list(updated)))
        if missing:
            details = [f"Missing documentation link: {item}" for item in missing]
            changelog_entries.append(ChangeLogEntry("Broken documentation links", details))

    placeholder_list = results.get("placeholders", [])
    if isinstance(placeholder_list, list) and placeholder_list:
        details = [
            f"{item['path']}:{item['line']} — {item['snippet']}"  # type: ignore[index]
            for item in placeholder_list
        ][:25]
        changelog_entries.append(ChangeLogEntry("Sentinel placeholders detected", details))

    synthesise_change_log(changelog_entries, write=write)
    write_json_snapshot(results, write=write)

    return results


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="Persist generated artefacts instead of dry-run output"
    )
    parser.add_argument(
        "--error-log", default=str(DEFAULT_ERROR_LOG), help="Path to the NDJSON error-capture log"
    )
    parser.add_argument("--json", default=str(DEFAULT_JSON), help="Override JSON snapshot path")
    parser.add_argument(
        "--changelog", default=str(DEFAULT_CHANGELOG), help="Override change log path"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    recorder = ErrorCaptureRecorder(Path(args.error_log))

    results = run(write=args.write, error_recorder=recorder)
    if args.json != str(DEFAULT_JSON):
        write_json_snapshot(results, write=args.write, path=Path(args.json))
    if args.changelog != str(DEFAULT_CHANGELOG):
        entries = []
        if args.write:
            try:
                entries = [ChangeLogEntry("See default change log", [str(DEFAULT_CHANGELOG)])]
            except Exception as exc:  # pragma: no cover - defensive
                recorder.record("STEP_4:ALT_CHANGELOG", repr(exc))
        synthesise_change_log(entries, write=args.write, path=Path(args.changelog))

    if not args.write:
        print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
