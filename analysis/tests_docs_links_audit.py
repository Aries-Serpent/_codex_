"""Utility to audit documentation navigation, markdown links, and referenced tests.

The 2025-09-10 status update noted that the original script crashed because it
attempted to reference a ``root`` variable that was never defined.  This module
reimplements the audit so it can be imported in unit tests or executed as a
stand-alone CLI.  The audit collects three high-signal checks that routinely
regressed in Codex automation sessions:

* Whether ``pytest.ini`` still contains the deprecated ``--cov=src/codex_ml``
  option.
* The concrete set of Markdown files referenced from ``mkdocs.yml``.
* Missing Markdown targets or ``tests/`` references that no longer point to
  real files.

Run the audit via ``python -m analysis.tests_docs_links_audit``.  The CLI prints
a JSON payload and, when ``--out`` is supplied, also writes it to disk for
archival in ``artifacts/docs_link_audit/``.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

# Repository root default used for CLI invocations.
ROOT = Path(__file__).resolve().parents[1]

try:  # Optional dependency: PyYAML makes nav parsing precise.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - PyYAML is optional.
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BrokenLink:
    """Represents a documentation link that targets a missing file."""

    source: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target}


# ---------------------------------------------------------------------------
# ``pytest.ini`` helpers
# ---------------------------------------------------------------------------


def _audit_pytest_ini(pytest_ini: Path) -> Optional[str]:
    """Return a remediation hint when deprecated coverage flags are present."""

    if not pytest_ini.exists():
        return None

    parser = configparser.ConfigParser()
    parser.read(pytest_ini, encoding="utf-8")
    addopts = parser.get("pytest", "addopts", fallback="")
    tokens = set(shlex.split(addopts))
    if "--cov=src/codex_ml" in tokens and "--cov=src/codex" not in tokens:
        return "replace --cov=src/codex_ml with --cov=src/codex in pytest.ini"
    return None


# ---------------------------------------------------------------------------
# MkDocs navigation parsing
# ---------------------------------------------------------------------------

_NAV_ITEM_PATTERN = re.compile(r"[A-Za-z0-9_./-]+\.md")


def _flatten_nav_items(nav: Iterable) -> List[str]:
    """Recursively flatten MkDocs ``nav`` entries into a list of strings."""

    items: List[str] = []

    def _walk(node: Iterable | dict | str) -> None:
        if isinstance(node, list):
            for child in node:
                _walk(child)
        elif isinstance(node, dict):
            for child in node.values():
                _walk(child)
        elif isinstance(node, str):
            if node.endswith(".md"):
                items.append(node)

    _walk(list(nav))
    return items


def _parse_nav_from_yaml(text: str) -> List[str]:
    """Parse the MkDocs nav structure using PyYAML when available."""

    if yaml is None:  # pragma: no cover - exercised when PyYAML missing.
        return []
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return []
    nav = data.get("nav")
    if not isinstance(nav, list):
        return []
    return _flatten_nav_items(nav)


def _parse_nav_fallback(text: str) -> List[str]:
    """Best-effort nav parser when PyYAML is unavailable."""

    return _NAV_ITEM_PATTERN.findall(text)


# ---------------------------------------------------------------------------
# Markdown link + test reference analysis
# ---------------------------------------------------------------------------

_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_TEST_REFERENCE_PATTERN = re.compile(r"(tests/[A-Za-z0-9_./-]+\.py)")

_RELATIVE_IGNORES = ("http://", "https://", "mailto:", "tel:", "#", "{{", "{%")


def _normalise_nav_paths(items: Iterable[str], *, docs_root: Path, repo_root: Path) -> List[str]:
    """Convert nav entries to ``docs/...`` repository-relative paths."""

    docs_prefix = docs_root.relative_to(repo_root)
    normalised: List[str] = []
    seen: set[str] = set()
    for item in items:
        value = item.strip()
        if not value:
            continue
        path = Path(value)
        if path.is_absolute():
            candidate = path.as_posix()
        else:
            candidate = (docs_prefix / path).as_posix()
        if candidate not in seen:
            seen.add(candidate)
            normalised.append(candidate)
    return normalised


def _iter_markdown_files(docs_root: Path) -> Iterable[Path]:
    for path in sorted(docs_root.rglob("*.md")):
        if path.is_file():
            yield path


def _extract_relative_links(text: str) -> List[str]:
    links: List[str] = []
    for match in _LINK_PATTERN.finditer(text):
        target = match.group(1).strip()
        if not target:
            continue
        if target.startswith(_RELATIVE_IGNORES):
            continue
        links.append(target)
    return links


def _resolve_link_candidates(doc_path: Path, target: str, repo_root: Path) -> List[Path]:
    pure_target = target.split("#", 1)[0].split("?", 1)[0]
    if not pure_target:
        return []
    rel_candidate = (doc_path.parent / pure_target).resolve()
    alt_candidate = repo_root / pure_target.lstrip("/")
    return [rel_candidate, alt_candidate]


def _find_broken_links(docs_root: Path, repo_root: Path) -> List[BrokenLink]:
    broken: List[BrokenLink] = []
    seen: set[tuple[str, str]] = set()
    for doc in _iter_markdown_files(docs_root):
        try:
            text = doc.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for target in _extract_relative_links(text):
            candidates = _resolve_link_candidates(doc, target, repo_root)
            if any(candidate.exists() for candidate in candidates):
                continue
            record = (doc.relative_to(repo_root).as_posix(), target)
            if record not in seen:
                seen.add(record)
                broken.append(BrokenLink(*record))
    return broken


def _find_missing_tests(docs_root: Path, repo_root: Path) -> List[str]:
    missing: set[str] = set()
    for doc in _iter_markdown_files(docs_root):
        try:
            text = doc.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in _TEST_REFERENCE_PATTERN.finditer(text):
            candidate = match.group(1)
            path = (repo_root / candidate).resolve()
            if not path.exists():
                missing.add(candidate)
    return sorted(missing)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_audit(repo_root: Path, *, docs_dir: str = "docs") -> dict:
    """Execute the documentation/test audit for ``repo_root``."""

    repo_root = repo_root.resolve()
    docs_root = (repo_root / docs_dir).resolve()

    pytest_hint = _audit_pytest_ini(repo_root / "pytest.ini")
    mkdocs_path = repo_root / "mkdocs.yml"
    nav_items: List[str] = []
    if mkdocs_path.exists():
        text = mkdocs_path.read_text(encoding="utf-8")
        nav_items = _parse_nav_from_yaml(text)
        if not nav_items:  # fallback when PyYAML unavailable
            nav_items = _parse_nav_fallback(text)
    nav_paths = _normalise_nav_paths(nav_items, docs_root=docs_root, repo_root=repo_root)

    broken_links = _find_broken_links(docs_root, repo_root)
    broken_pairs = {(item.source, item.target) for item in broken_links}
    # Include navigation entries that point at missing files.
    for nav_path in nav_paths:
        candidate = repo_root / nav_path
        record = ("mkdocs.yml", nav_path)
        if not candidate.exists() and record not in broken_pairs:
            broken_links.append(BrokenLink(*record))
            broken_pairs.add(record)

    missing_tests = _find_missing_tests(docs_root, repo_root)

    payload = {
        "pytest_ini": pytest_hint,
        "pytest_cov": None,  # Reserved for future expansion.
        "mkdocs_nav": nav_paths,
        "broken_links": [item.to_dict() for item in broken_links],
        "missing_tests": missing_tests,
    }
    return payload


def _write_output(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit docs navigation and references")
    parser.add_argument("--repo", default=str(ROOT), help="Repository root to audit")
    parser.add_argument(
        "--docs-dir", default="docs", help="Documentation directory relative to repo root"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional path (relative to repo root) where the JSON payload will be written",
    )
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit with status 1 when broken links or missing tests are discovered",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(args.repo or ROOT)
    payload = run_audit(repo_root, docs_dir=args.docs_dir)
    print(json.dumps(payload, indent=2))

    if args.out:
        out_path = repo_root / args.out
        _write_output(out_path, payload)

    if args.fail_on_issues and (payload["broken_links"] or payload["missing_tests"]):
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via CLI
    raise SystemExit(main())
