#!/usr/bin/env python3
"""Offline, deterministic status update generator.

This script scans the repository for incomplete or missing components and
produces both a Markdown report and a machine-readable JSON snapshot. It is
designed to run without network access and to emit deterministic output by
sorting all discovered artefacts.

Generated artefacts:
* `.codex/status/_codex_status_update-YYYY-MM-DD.md`
* `.codex/status_scan.json`

Usage::

    python tools/status/generate_status_update.py --author "<name>" \
        --date YYYY-MM-DD --write

If ``--write`` is omitted, a redacted preview is printed to stdout and no files
are created.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, TypedDict


class _StubFinding(TypedDict):
    file: str
    symbol: str
    kind: str
    line: int
    detail: str


class _TodoRow(TypedDict):
    file: str
    total: int
    todo: int
    fixme: int
    xxx: int


class _EmptyPackage(TypedDict):
    path: str
    reason: str


class _CLIEntry(TypedDict):
    path: str
    function: str
    cli_names: list[str]
    status: str
    doc_references: list[str]
    decorators: list[str]


class _RegistryImplementation(TypedDict):
    implementation: str
    kind: str
    status: str


class _RegistryEntry(TypedDict):
    key: str
    implementation: str
    registration_kind: str
    status: str


class _Registry(TypedDict):
    registry_file: str
    entries: list[_RegistryEntry]
    status: str


class _TestMapping(TypedDict, total=False):
    total_modules: int
    modules_without_tests: list[str]
    modules_without_tests_count: int
    modules_with_tests_count: int


class _DocTopic(TypedDict):
    topic: str
    lines: list[int]
    count: int


class _DocCrossreference(TypedDict):
    doc: str
    topics: list[_DocTopic]


class _DuplicatePackage(TypedDict):
    package: str
    files: list[str]
    specs: list[str]


class _PackagingSummary(TypedDict, total=False):
    pyproject: bool
    requirement_files: list[str]
    lock_files: list[str]
    duplicate_packages: list[_DuplicatePackage]
    lock_file_present: bool


class _ComplianceSummary(TypedDict, total=False):
    license_files: list[str]
    duplicate_license_candidates: list[str]
    detect_secrets_baseline: bool
    pre_commit_config: bool


class _SeedCall(TypedDict):
    file: str
    keywords: list[str]


class _ReproducibilitySummary(TypedDict, total=False):
    data_manifests: list[str]
    seed_modules: list[str]
    seed_calls: list[_SeedCall]
    checkpoint_artifacts: list[str]


class _SummaryCounts(TypedDict):
    stubs_total: int
    stubs_by_kind: dict[str, int]
    todo_files: int
    todo_total: int
    empty_packages: int
    cli_total: int
    cli_status_counts: dict[str, int]
    registry_total: int
    registry_status_counts: dict[str, int]
    modules_scanned: int
    modules_without_tests: int


class _StatusData(TypedDict, total=False):
    generated_at: str
    author: str
    date: str
    stubs: list[_StubFinding]
    todo_counts: list[_TodoRow]
    empty_packages: list[_EmptyPackage]
    cli: list[_CLIEntry]
    registries: list[_Registry]
    tests: _TestMapping
    docs: list[_DocCrossreference]
    packaging: _PackagingSummary
    compliance: _ComplianceSummary
    repro: _ReproducibilitySummary
    summary: _SummaryCounts


REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / ".codex"
STATUS_DIR = CODEX_DIR / "status"
ERROR_LOG_PATH = CODEX_DIR / "errors.ndjson"
UTC = dt.timezone.utc

SRC_DIRS: tuple[Path, ...] = (
    REPO_ROOT / "src",
    REPO_ROOT / "codex_ml",
)
DOCS_DIR = REPO_ROOT / "docs"
TESTS_DIR = REPO_ROOT / "tests"


PLACEHOLDER_KEYWORDS = (
    "todo",
    "fixme",
    "nyi",
    "not implemented",
    "not-implemented",
    "placeholder",
    "stub",
    "disabled",
    "coming soon",
)

TODO_KEYWORDS = ("TODO", "FIXME", "XXX")

DOC_TOPICS = (
    "tokenizer CLI",
    "ExternalWebSearch",
    "Hydra sweeps",
    "SentencePiece",
    "LoRA",
    "MLflow",
    "W&B",
    "Weights & Biases",
    "Typer",
)

COMPLIANCE_LICENSE_PATTERN = re.compile(r"^LICENSE", re.IGNORECASE)
SENSITIVE_OUTPUT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(token|secret|password|api[-_]?key)\s*[:=]\s*[^\s|]+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
)


def utc_timestamp() -> str:
    """Return the current UTC time as an ISO 8601 string, to whole seconds."""
    return dt.datetime.now(UTC).isoformat(timespec="seconds")


def sanitize_for_logging(text: str) -> str:
    """Redact sensitive-looking key/value fragments before console output."""
    sanitized = text
    for pattern in SENSITIVE_OUTPUT_PATTERNS:
        sanitized = pattern.sub("[redacted]", sanitized)
    return sanitized


@dataclass
class PythonFile:
    """Container for parsed Python file metadata."""

    path: Path
    text: str
    parsed: bool
    tree: Optional[ast.AST]
    imports: set[str] = field(default_factory=set)


def log_error(step: str, error_message: str, context: Optional[dict[str, str]] = None) -> None:
    """Append a JSON error record to `.codex/errors.ndjson`."""

    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": utc_timestamp(),
        "step": step,
        "error": error_message,
        "context": context or {},
    }
    try:
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except Exception:
        # Last resort: swallow logging failures to avoid cascading issues.
        _ = None  # suppressed: no action needed


def safe_read_text(path: Path) -> tuple[str, bool]:
    """Read text from a file, logging and returning ``False`` on failure."""

    try:
        return path.read_text(encoding="utf-8"), True
    except Exception as exc:  # pragma: no cover - defensive
        log_error("read_text", str(exc), {"path": str(path)})
        return "", False


def collect_imports(tree: ast.AST) -> set[str]:
    """Collect top-level import names, e.g. ``import a.b`` contributes ``a``."""
    modules: set[str] = set()

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> None:  # noqa: D401
            for alias in node.names:
                modules.add(alias.name.split(".")[0])

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: D401
            if node.module:
                modules.add(node.module.split(".")[0])

    ImportVisitor().visit(tree)
    return modules


def existing_src_dirs() -> list[Path]:
    """Return existing configured source directories in sorted path order."""
    dirs = [d for d in SRC_DIRS if d.exists()]
    return sorted(dirs)


def iter_python_files(paths: Iterable[Path]) -> Iterator[Path]:
    """Yield sorted Python paths, excluding common build and environment folders."""
    exclude_names = {
        ".git",
        ".hg",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "build",
        "dist",
        "site-packages",
        "node_modules",
        "venv",
        ".venv",
        ".tox",
        ".nox",
        "egg-info",
    }
    for base in sorted(set(paths)):
        if not base.exists():
            continue
        for candidate in sorted(base.rglob("*.py")):
            if any(part in exclude_names for part in candidate.parts):
                continue
            yield candidate


def load_python_files(paths: Iterable[Path]) -> list[PythonFile]:
    """Read Python files and parse ASTs; retain unreadable or invalid files as metadata."""
    python_files: list[PythonFile] = []
    for py_path in iter_python_files(paths):
        text, ok = safe_read_text(py_path)
        tree: Optional[ast.AST] = None
        imports: set[str] = set()
        parsed = False
        if ok:
            try:
                tree = ast.parse(text)
                imports = collect_imports(tree)
                parsed = True
            except SyntaxError as exc:
                log_error("parse_ast", str(exc), {"path": str(py_path)})
        python_files.append(
            PythonFile(path=py_path, text=text, parsed=parsed, tree=tree, imports=imports)
        )
    return python_files


def strip_docstring(body: Sequence[ast.stmt]) -> list[ast.stmt]:
    """Copy a statement body without its leading string-literal docstring."""
    if not body:
        return []
    body_list = list(body)
    first = body_list[0]
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return body_list[1:]
    return body_list


def get_attr_name(node: ast.AST | None) -> str:
    """Resolve dotted names and call targets; return ``""`` for unnamed nodes."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = get_attr_name(node.value)
        return f"{value}.{node.attr}" if value else node.attr
    if isinstance(node, ast.Call):
        return get_attr_name(node.func)
    return ""


def extract_raise_message(exc: ast.AST | None) -> Optional[str]:
    """Find the first literal string argument of a raise expression, if any."""
    if isinstance(exc, ast.Call):
        for arg in exc.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
    if isinstance(exc, ast.Constant) and isinstance(exc.value, str):
        return exc.value
    return None


def classify_placeholder(message: Optional[str]) -> bool:
    """Check whether a message contains a configured incompleteness keyword."""
    if not message:
        return False
    lowered = message.lower()
    return any(keyword in lowered for keyword in PLACEHOLDER_KEYWORDS)


def scan_stubs(python_files: Sequence[PythonFile]) -> list[_StubFinding]:
    """Find trivial bodies and placeholder raises, sorted by source location.

    Files must be beneath ``REPO_ROOT``; results use repository-relative paths
    and dotted enclosing symbols. Unparsed files are skipped.
    """
    findings: list[_StubFinding] = []

    for py_file in python_files:
        if not py_file.parsed or not py_file.tree:
            continue

        rel_path = py_file.path.relative_to(REPO_ROOT)

        class StubVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.context: list[str] = []

            def push(self, name: str) -> None:
                self.context.append(name)

            def pop(self) -> None:
                if self.context:
                    self.context.pop()

            def current_symbol(self) -> str:
                return ".".join(self.context) if self.context else "<module>"

            def record(self, kind: str, node: ast.AST, detail: Optional[str] = None) -> None:
                findings.append(
                    {
                        "file": str(rel_path),
                        "symbol": self.current_symbol(),
                        "kind": kind,
                        "line": getattr(node, "lineno", 0),
                        "detail": detail or "",
                    }
                )

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: D401
                self.push(node.name)
                self._check_trivial(node, node.body)
                self.generic_visit(node)
                self.pop()

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: D401
                self.push(node.name)
                self._check_trivial(node, node.body)
                self.generic_visit(node)
                self.pop()

            def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: D401
                self.push(node.name)
                self._check_trivial(node, node.body)
                self.generic_visit(node)
                self.pop()

            def visit_Raise(self, node: ast.Raise) -> None:  # noqa: D401
                exc = node.exc
                if exc is None:
                    return
                name = get_attr_name(exc)
                message = extract_raise_message(exc)
                lowered_name = name.lower()
                if name.endswith("NotImplementedError") or lowered_name == "notimplementederror":
                    self.record("NotImplementedError", node, detail=message)
                    return
                if classify_placeholder(message) or "notimplemented" in lowered_name:
                    self.record("PlaceholderRaise", node, detail=message or name)

            def _check_trivial(self, node: ast.AST, body: Sequence[ast.stmt]) -> None:
                body_wo_doc = strip_docstring(body)
                if not body_wo_doc:
                    self.record("TrivialBody", node, detail="empty body")
                    return
                if len(body_wo_doc) == 1:
                    stmt = body_wo_doc[0]
                    if isinstance(stmt, ast.Pass):
                        self.record("TrivialBody", node, detail="pass")
                        return
                    if (
                        isinstance(stmt, ast.Expr)
                        and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is Ellipsis
                    ):
                        self.record("TrivialBody", node, detail="ellipsis")
                        return

        StubVisitor().visit(py_file.tree)

    findings.sort(key=lambda item: (item["file"], item["line"], item["kind"], item["symbol"]))
    return findings


def count_todos(python_files: Sequence[PythonFile]) -> list[_TodoRow]:
    """Count TODO/FIXME/XXX words in all text, including strings and comments."""
    todo_rows: list[_TodoRow] = []
    patterns = {kw: re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in TODO_KEYWORDS}

    for py_file in python_files:
        text = py_file.text
        counts = {kw: len(pattern.findall(text)) for kw, pattern in patterns.items()}
        total = sum(counts.values())
        if total:
            row: _TodoRow = {
                "file": str(py_file.path.relative_to(REPO_ROOT)),
                "total": total,
                "todo": counts["TODO"],
                "fixme": counts["FIXME"],
                "xxx": counts["XXX"],
            }
            todo_rows.append(row)

    todo_rows.sort(key=lambda item: item["file"])
    return todo_rows


def is_trivial_init(init_path: Path) -> bool:
    """Recognize empty initializers or ones containing only comments/imports/exports."""
    text, ok = safe_read_text(init_path)
    if not ok:
        return False
    stripped_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not stripped_lines:
        return True
    allowed_prefixes = ("#", "__all__", "import ", "from ")
    return all(line.startswith(allowed_prefixes) for line in stripped_lines)


def find_empty_packages() -> list[_EmptyPackage]:
    """Locate leaf packages containing only .gitkeep or a trivial initializer."""
    empty: list[_EmptyPackage] = []
    for src_root in existing_src_dirs():
        for directory in sorted(src_root.rglob("*")):
            if not directory.is_dir():
                continue
            entries = sorted(directory.iterdir())
            files = [entry for entry in entries if entry.is_file()]
            subdirs = [entry for entry in entries if entry.is_dir() and entry.name != "__pycache__"]
            gitkeep_only = files and all(file.name == ".gitkeep" for file in files)
            init_files = [file for file in files if file.name == "__init__.py"]
            non_trivial_files = [
                file
                for file in files
                if file.name != ".gitkeep"
                and not (file.name == "__init__.py" and is_trivial_init(file))
            ]

            if gitkeep_only and not subdirs:
                empty.append(
                    {
                        "path": str(directory.relative_to(REPO_ROOT)),
                        "reason": ".gitkeep-only",
                    }
                )
            elif init_files and not non_trivial_files and not subdirs:
                empty.append(
                    {
                        "path": str(directory.relative_to(REPO_ROOT)),
                        "reason": "trivial __init__.py",
                    }
                )

    empty.sort(key=lambda item: item["path"])
    return empty


def load_docs_texts() -> dict[Path, str]:
    """Load readable Markdown and reStructuredText files beneath ``DOCS_DIR``."""
    docs: dict[Path, str] = {}
    if not DOCS_DIR.exists():
        return docs
    for extension in ("*.md", "*.rst"):
        for doc_path in sorted(DOCS_DIR.rglob(extension)):
            text, ok = safe_read_text(doc_path)
            if ok:
                docs[doc_path] = text
    return docs


def find_docs_mentions(doc_texts: dict[Path, str], term: str) -> list[str]:
    """Return relative document paths containing a case-insensitive substring."""
    mentions: list[str] = []
    lowered = term.lower()
    for doc_path, text in doc_texts.items():
        if lowered in text.lower():
            mentions.append(str(doc_path.relative_to(REPO_ROOT)))
    return sorted(set(mentions))


def classify_cli_status(body: Sequence[ast.stmt]) -> str:
    """Classify a CLI body by trivial statements and placeholder raise messages."""
    body_wo_doc = strip_docstring(body)
    if not body_wo_doc:
        return "stub-empty"
    first_stmt = body_wo_doc[0]
    if isinstance(first_stmt, ast.Pass):
        return "stub-pass"
    if (
        isinstance(first_stmt, ast.Expr)
        and isinstance(first_stmt.value, ast.Constant)
        and first_stmt.value.value is Ellipsis
    ):
        return "stub-pass"
    if isinstance(first_stmt, ast.Raise):
        message = extract_raise_message(first_stmt.exc)
        name = get_attr_name(first_stmt.exc)
        lowered_name = name.lower() if name else ""
        if message and "disabled" in message.lower():
            return "disabled"
        if classify_placeholder(message) or "notimplemented" in lowered_name:
            return "stub-todo"
    for node in ast.walk(ast.Module(body=list(body_wo_doc), type_ignores=[])):
        if isinstance(node, ast.Raise):
            message = extract_raise_message(node.exc)
            name = get_attr_name(node.exc)
            lowered_name = name.lower() if name else ""
            if (
                name.endswith("NotImplementedError")
                or "notimplemented" in lowered_name
                or classify_placeholder(message)
            ):
                return "stub-todo"
    return "implemented"


def extract_cli_names(decorator: ast.AST) -> list[str]:
    """Extract literal positional names and name/command/value decorator keywords."""
    names: list[str] = []
    if isinstance(decorator, ast.Call):
        for arg in decorator.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                names.append(arg.value)
        for kw in decorator.keywords:
            if (
                kw.arg in {"name", "command", "value"}
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                names.append(kw.value.value)
    return names


def discover_cli(python_files: Sequence[PythonFile], doc_texts: dict[Path, str]) -> list[_CLIEntry]:
    """Discover Click/Typer-decorated functions and matching document references."""
    cli_entries: list[_CLIEntry] = []

    for py_file in python_files:
        if not py_file.parsed or not py_file.tree:
            continue
        rel_path = str(py_file.path.relative_to(REPO_ROOT))
        imports = py_file.imports

        for node in ast.walk(py_file.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorators = node.decorator_list
            decorator_names = [get_attr_name(dec) for dec in decorators]
            cli_related = False
            cli_names: list[str] = []
            for decorator in decorators:
                name = get_attr_name(decorator)
                base = name.lower()
                if any(token in base for token in ("click.", "typer.")):
                    cli_related = True
                if base.endswith(".command") or base.endswith(".group"):
                    if {"click", "typer"} & imports:
                        cli_related = True
                cli_names.extend(extract_cli_names(decorator))
            if not cli_related:
                continue

            cli_names = sorted(set(cli_names)) or [node.name]
            status = classify_cli_status(node.body)
            docs_mentions: list[str] = []
            for candidate in {node.name, *cli_names}:
                docs_mentions.extend(find_docs_mentions(doc_texts, candidate))
            entry: _CLIEntry = {
                "path": rel_path,
                "function": node.name,
                "cli_names": sorted(set(cli_names)),
                "status": status,
                "doc_references": sorted(set(docs_mentions)),
                "decorators": sorted(set(filter(None, decorator_names))),
            }
            cli_entries.append(entry)

    cli_entries.sort(key=lambda item: (item["path"], item["function"]))
    return cli_entries


def registry_value_repr(py_file: PythonFile, node: ast.AST) -> str:
    """Return a stripped source segment, falling back to the AST node type name."""
    try:
        snippet = ast.get_source_segment(py_file.text, node)
        if snippet:
            return snippet.strip()
    except Exception:
        _ = None  # suppressed: no action needed
    return type(node).__name__


def inspect_registries(python_files: Sequence[PythonFile]) -> list[_Registry]:
    """Inspect registry-named files for register decorators and mapping assignments."""
    registries: list[_Registry] = []

    for py_file in python_files:
        if "registry" not in py_file.path.name.lower():
            continue
        if not py_file.parsed or not py_file.tree:
            continue

        rel_path = str(py_file.path.relative_to(REPO_ROOT))
        entries: dict[str, _RegistryImplementation] = {}

        for node in ast.walk(py_file.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    name = get_attr_name(decorator)
                    if not name.lower().endswith(".register"):
                        continue
                    keys = extract_cli_names(decorator)
                    for key in keys:
                        entries[key] = {
                            "implementation": node.name,
                            "kind": node.__class__.__name__.replace("Def", ""),
                            "status": "ok",
                        }
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Subscript):
                        base_name = get_attr_name(target.value)
                        if "registry" not in base_name.lower():
                            continue
                        key_node = target.slice
                        key_value = None
                        if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                            key_value = key_node.value
                        if key_value:
                            value_repr = registry_value_repr(py_file, node.value)
                            status = "ok"
                            lowered = value_repr.lower()
                            if lowered in {"none", "...", "ellipsis"} or any(
                                token in lowered for token in ("todo", "tbd")
                            ):
                                status = "unresolved"
                            entries[key_value] = {
                                "implementation": value_repr,
                                "kind": "assignment",
                                "status": status,
                            }
                    if (
                        isinstance(target, ast.Name)
                        and "registry" in target.id.lower()
                        and isinstance(node.value, ast.Dict)
                    ):
                        for mapping_key, value_node in zip(node.value.keys, node.value.values):
                            if isinstance(mapping_key, ast.Constant) and isinstance(
                                mapping_key.value, str
                            ):
                                value_repr = registry_value_repr(py_file, value_node)
                                status = "ok"
                                lowered = value_repr.lower()
                                if lowered in {"none", "...", "ellipsis"} or any(
                                    token in lowered for token in ("todo", "tbd")
                                ):
                                    status = "unresolved"
                                entries[mapping_key.value] = {
                                    "implementation": value_repr,
                                    "kind": "mapping",
                                    "status": status,
                                }

        registry_status = "empty" if not entries else "ok"
        if entries and any(entry["status"] != "ok" for entry in entries.values()):
            registry_status = "has-unresolved"
        registries.append(
            {
                "registry_file": rel_path,
                "entries": [
                    {
                        "key": key,
                        "implementation": value["implementation"],
                        "registration_kind": value["kind"],
                        "status": value["status"],
                    }
                    for key, value in sorted(entries.items())
                ],
                "status": registry_status,
            }
        )

    registries.sort(key=lambda item: item["registry_file"])
    return registries


def module_name_from_path(path: Path) -> str:
    """Derive an import name, removing a source root and package __init__ suffix."""
    for src_root in existing_src_dirs():
        try:
            relative = path.relative_to(src_root)
        except ValueError:
            continue
        if relative.name == "__init__.py":
            parts = relative.parent.parts
        else:
            parts = relative.with_suffix("").parts
        if not parts:
            return ""
        return ".".join(parts)
    relative = path.relative_to(REPO_ROOT)
    return ".".join(relative.with_suffix("").parts)


def map_tests(python_files: Sequence[PythonFile]) -> _TestMapping:
    """Estimate test references by module names, paths, and sufficiently long basenames."""
    src_files = [pf for pf in python_files if pf.path.suffix == ".py"]
    module_entries: list[dict[str, str]] = []
    for pf in src_files:
        module_name = module_name_from_path(pf.path)
        if not module_name:
            continue
        module_entries.append(
            {
                "file": str(pf.path.relative_to(REPO_ROOT)),
                "module": module_name,
            }
        )

    test_files = load_python_files([TESTS_DIR]) if TESTS_DIR.exists() else []
    test_texts = [(str(pf.path.relative_to(REPO_ROOT)), pf.text) for pf in test_files]

    modules_without_tests: list[str] = []
    for entry in module_entries:
        module_name = entry["module"]
        module_file = entry["file"].replace(os.sep, "/")
        module_basename = module_name.split(".")[-1]
        has_tests = False
        for _, test_text in test_texts:
            if module_name in test_text or module_file in test_text:
                has_tests = True
                break
            token = f"import {module_name}"
            if token in test_text:
                has_tests = True
                break
            if len(module_basename) >= 5 and re.search(
                rf"\b{re.escape(module_basename)}\b", test_text
            ):
                has_tests = True
                break
        if not has_tests:
            modules_without_tests.append(entry["file"])

    modules_without_tests = sorted(set(modules_without_tests))
    total_modules = len(module_entries)
    return {
        "total_modules": total_modules,
        "modules_without_tests": modules_without_tests,
        "modules_without_tests_count": len(modules_without_tests),
        "modules_with_tests_count": total_modules - len(modules_without_tests),
    }


def docs_crossreferences(doc_texts: dict[Path, str]) -> list[_DocCrossreference]:
    """Find configured documentation topics with one-based matching line numbers."""
    topic_patterns = {topic: re.compile(re.escape(topic), re.IGNORECASE) for topic in DOC_TOPICS}
    crossrefs: list[_DocCrossreference] = []

    for doc_path, text in doc_texts.items():
        lines = text.splitlines()
        topics: list[_DocTopic] = []
        for topic, pattern in topic_patterns.items():
            matches = [idx + 1 for idx, line in enumerate(lines) if pattern.search(line)]
            if matches:
                topics.append(
                    {
                        "topic": topic,
                        "lines": matches,
                        "count": len(matches),
                    }
                )
        if topics:
            crossrefs.append(
                {
                    "doc": str(doc_path.relative_to(REPO_ROOT)),
                    "topics": sorted(topics, key=lambda item: item["topic"].lower()),
                }
            )

    crossrefs.sort(key=lambda item: item["doc"])
    return crossrefs


def parse_requirements_line(line: str) -> Optional[str]:
    """Normalize the name before a version operator; skip blank/comment/option lines.

    For example, ``"Some_Package>=1"`` returns ``"some-package"``. This is a
    lightweight text heuristic, not a full requirements-file parser.
    """
    cleaned = line.strip()
    if not cleaned or cleaned.startswith("#"):
        return None
    if cleaned.startswith("-"):
        return None
    match = re.split(r"[<>=!~]", cleaned, maxsplit=1)
    package = match[0].strip()
    if not package:
        return None
    return package.lower().replace("_", "-")


def packaging_summary() -> _PackagingSummary:
    """Summarize requirement files, known locks, and repeated package specifications."""
    summary: _PackagingSummary = {}

    pyproject = REPO_ROOT / "pyproject.toml"
    summary["pyproject"] = pyproject.exists()

    requirement_files: list[str] = []
    for pattern in ("requirements*.txt", "requirements*.in"):
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.is_file():
                requirement_files.append(str(path.relative_to(REPO_ROOT)))
    requirements_dir = REPO_ROOT / "requirements"
    if requirements_dir.exists():
        for path in sorted(requirements_dir.rglob("requirements*.txt")):
            if path.is_file():
                requirement_files.append(str(path.relative_to(REPO_ROOT)))
    summary["requirement_files"] = sorted(set(requirement_files))

    lock_files = []
    for candidate in ["requirements/lock.txt", "uv.lock", "poetry.lock", "Pipfile.lock"]:
        path = REPO_ROOT / candidate
        if path.exists():
            lock_files.append(str(path.relative_to(REPO_ROOT)))
    summary["lock_files"] = sorted(lock_files)

    package_map: dict[str, list[dict[str, str]]] = {}
    for rel_path in summary["requirement_files"]:
        path = REPO_ROOT / rel_path
        text, ok = safe_read_text(path)
        if not ok:
            continue
        for line in text.splitlines():
            package = parse_requirements_line(line)
            if not package:
                continue
            package_map.setdefault(package, []).append({"file": rel_path, "spec": line.strip()})

    duplicates: list[_DuplicatePackage] = []
    for package, records in sorted(package_map.items()):
        files = {record["file"] for record in records}
        specs = {record["spec"] for record in records}
        if len(files) > 1 or len(specs) > 1:
            duplicates.append(
                {
                    "package": package,
                    "files": sorted(files),
                    "specs": sorted(specs),
                }
            )
    summary["duplicate_packages"] = duplicates

    summary["lock_file_present"] = bool(summary["lock_files"])
    return summary


def compliance_summary() -> _ComplianceSummary:
    """List license candidates and the presence of secret/pre-commit configuration."""
    license_files = [
        str(path.relative_to(REPO_ROOT))
        for path in sorted(REPO_ROOT.glob("**/LICENSE*"))
        if path.is_file() and COMPLIANCE_LICENSE_PATTERN.match(path.name)
    ]
    duplicate_licenses = [path for path in license_files if path.lower() != "license"]

    detect_secrets = (REPO_ROOT / ".secrets.baseline").exists()
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").exists()

    return {
        "license_files": license_files,
        "duplicate_license_candidates": duplicate_licenses,
        "detect_secrets_baseline": detect_secrets,
        "pre_commit_config": pre_commit,
    }


def reproducibility_summary(python_files: Sequence[PythonFile]) -> _ReproducibilitySummary:
    """Find manifest/checkpoint artifacts and textual matches for common seed calls."""
    manifest_files = [
        str(path.relative_to(REPO_ROOT))
        for path in sorted(REPO_ROOT.rglob("manifest.json"))
        if path.is_file()
    ]

    seed_modules: list[str] = []
    seed_calls: list[_SeedCall] = []
    seed_patterns = [
        "random.seed",
        "np.random.seed",
        "torch.manual_seed",
        "seed_everything",
        "set_seed",
    ]
    for py_file in python_files:
        lowered_name = py_file.path.name.lower()
        if "seed" in lowered_name:
            seed_modules.append(str(py_file.path.relative_to(REPO_ROOT)))
        matches = [pattern for pattern in seed_patterns if pattern in py_file.text]
        if matches:
            seed_calls.append(
                {
                    "file": str(py_file.path.relative_to(REPO_ROOT)),
                    "keywords": matches,
                }
            )

    checkpoint_patterns = ("*.ckpt", "*.pt", "*.pth", "*.bin")
    checkpoint_files: set[str] = set()
    for pattern in checkpoint_patterns:
        for path in sorted(REPO_ROOT.rglob(pattern)):
            if path.is_file():
                checkpoint_files.add(str(path.relative_to(REPO_ROOT)))
    for path in sorted(REPO_ROOT.rglob("*checkpoint*")):
        if path.is_file():
            checkpoint_files.add(str(path.relative_to(REPO_ROOT)))

    return {
        "data_manifests": manifest_files,
        "seed_modules": sorted(set(seed_modules)),
        "seed_calls": sorted(seed_calls, key=lambda item: item["file"]),
        "checkpoint_artifacts": sorted(checkpoint_files),
    }


def build_summary_counts(data: _StatusData) -> _SummaryCounts:
    """Aggregate scan sections, treating omitted sections as empty.

    ``build_summary_counts({})["stubs_total"]`` is ``0``; callers can supply
    only the scan sections they have collected.
    """
    stubs = data.get("stubs", [])
    todo_counts = data.get("todo_counts", [])
    empty_packages = data.get("empty_packages", [])
    cli_entries = data.get("cli", [])
    registries = data.get("registries", [])
    tests = data.get("tests", {})

    kind_counts: dict[str, int] = {}
    for item in stubs:
        kind_counts[item["kind"]] = kind_counts.get(item["kind"], 0) + 1

    cli_status_counts: dict[str, int] = {}
    for entry in cli_entries:
        status = entry["status"]
        cli_status_counts[status] = cli_status_counts.get(status, 0) + 1

    registry_status_counts: dict[str, int] = {}
    for registry in registries:
        status = registry["status"]
        registry_status_counts[status] = registry_status_counts.get(status, 0) + 1

    return {
        "stubs_total": len(stubs),
        "stubs_by_kind": kind_counts,
        "todo_files": len(todo_counts),
        "todo_total": sum(item["total"] for item in todo_counts),
        "empty_packages": len(empty_packages),
        "cli_total": len(cli_entries),
        "cli_status_counts": cli_status_counts,
        "registry_total": len(registries),
        "registry_status_counts": registry_status_counts,
        "modules_scanned": tests.get("total_modules", 0),
        "modules_without_tests": tests.get("modules_without_tests_count", 0),
    }


def render_table_rows(rows: list[str]) -> list[str]:
    """Return table rows or a single ``| (none) |`` placeholder when empty."""
    return rows if rows else ["| (none) |"]


def write_report(author: str, date: str, data: _StatusData, write: bool) -> Path:
    """Render collected sections and return the dated Markdown output path.

    With ``write=False``, emit only a size notice to stderr, not repository
    content. The status directory is created in either mode.
    """
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STATUS_DIR / f"_codex_status_update-{date}.md"
    generated_ts = dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    summary_counts = build_summary_counts(data)

    lines: list[str] = []
    lines.append("# Status Update: Exhaustive Audit")
    lines.append(f"> Generated: {generated_ts} | Author: {author}")
    lines.append("")

    lines.append("## Summary")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(
        f"| Stub findings | {summary_counts['stubs_total']} total ({summary_counts['stubs_by_kind']}) |"
    )
    lines.append(
        f"| TODO/FIXME/XXX occurrences | {summary_counts['todo_total']} across {summary_counts['todo_files']} files |"
    )
    lines.append(f"| Empty packages/modules | {summary_counts['empty_packages']} |")
    lines.append(
        f"| CLI commands discovered | {summary_counts['cli_total']} ({summary_counts['cli_status_counts']}) |"
    )
    lines.append(
        f"| Registries inspected | {summary_counts['registry_total']} ({summary_counts['registry_status_counts']}) |"
    )
    lines.append(
        f"| Modules without direct test references | {summary_counts['modules_without_tests']} of {summary_counts['modules_scanned']} scanned |"
    )
    lines.append("")

    lines.append("## Stub and Incompleteness Inventory")
    lines.append("| File | Symbol | Kind | Line | Detail |")
    lines.append("| --- | --- | --- | --- | --- |")
    stub_rows = [
        f"| {item['file']} | {item['symbol']} | {item['kind']} | {item['line']} | {item['detail']} |"
        for item in data.get("stubs", [])
    ]
    lines.extend(render_table_rows(stub_rows))
    lines.append("")

    lines.append("### TODO/FIXME/XXX Counts")
    lines.append("| File | TODO | FIXME | XXX | Total |")
    lines.append("| --- | --- | --- | --- | --- |")
    todo_rows = [
        f"| {item['file']} | {item.get('todo', 0)} | {item.get('fixme', 0)} | {item.get('xxx', 0)} | {item['total']} |"
        for item in data.get("todo_counts", [])
    ]
    lines.extend(render_table_rows(todo_rows))
    lines.append("")

    lines.append("## Empty Packages/Modules")
    lines.append("| Path | Reason |")
    lines.append("| --- | --- |")
    empty_rows = [
        f"| {item['path']} | {item['reason']} |" for item in data.get("empty_packages", [])
    ]
    lines.extend(render_table_rows(empty_rows))
    lines.append("")

    lines.append("## CLI Discovery and Status")
    lines.append("| Path | Function | CLI Names | Status | Docs | Decorators |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    cli_rows = []
    for entry in data.get("cli", []):
        docs_value = "<br/>".join(entry.get("doc_references", [])) or ""
        cli_rows.append(
            "| {path} | {function} | {names} | {status} | {docs} | {decorators} |".format(
                path=entry["path"],
                function=entry["function"],
                names=", ".join(entry.get("cli_names", [])),
                status=entry["status"],
                docs=docs_value or "",
                decorators=", ".join(entry.get("decorators", [])),
            )
        )
    lines.extend(render_table_rows(cli_rows))
    lines.append("")

    lines.append("## Registries and Plugins")
    lines.append("| Registry File | Key | Implementation | Status |")
    lines.append("| --- | --- | --- | --- |")
    registry_rows: list[str] = []
    for registry in data.get("registries", []):
        entries = registry.get("entries", [])
        if entries:
            for registry_entry in entries:
                registry_rows.append(
                    f"| {registry['registry_file']} | {registry_entry['key']} | {registry_entry['implementation']} | {registry_entry['status']} |"
                )
        else:
            registry_rows.append(
                f"| {registry['registry_file']} | (empty) |  | {registry['status']} |"
            )
    lines.extend(render_table_rows(registry_rows))
    lines.append("")

    lines.append("## Tests Mapping")
    tests = data.get("tests", {})
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Modules scanned | {tests.get('total_modules', 0)} |")
    lines.append(f"| Modules with detected tests | {tests.get('modules_with_tests_count', 0)} |")
    lines.append(
        f"| Modules without detected tests | {tests.get('modules_without_tests_count', 0)} |"
    )
    lines.append("")
    modules_without_tests = tests.get("modules_without_tests", [])
    if modules_without_tests:
        lines.append("<details><summary>Modules lacking explicit test references</summary>")
        lines.append("")
        for module in modules_without_tests:
            lines.append(f"- {module}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("## Docs Cross-References")
    lines.append("| Doc | Topic | Line(s) | Count |")
    lines.append("| --- | --- | --- | --- |")
    doc_rows: list[str] = []
    for doc_entry in data.get("docs", []):
        doc = doc_entry["doc"]
        topics = doc_entry.get("topics", [])
        for topic in topics:
            lines_repr = ", ".join(str(num) for num in topic.get("lines", []))
            doc_rows.append(f"| {doc} | {topic['topic']} | {lines_repr} | {topic['count']} |")
    lines.extend(render_table_rows(doc_rows))
    lines.append("")

    lines.append("## Packaging and Environment")
    packaging = data.get("packaging", {})
    lines.append("| Item | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| pyproject.toml present | {packaging.get('pyproject', False)} |")
    lines.append(f"| Requirement files | {packaging.get('requirement_files', [])} |")
    lines.append(f"| Lock files | {packaging.get('lock_files', [])} |")
    lines.append(f"| Lock file present | {packaging.get('lock_file_present', False)} |")
    duplicates = packaging.get("duplicate_packages", [])
    lines.append(f"| Duplicate/overlapping packages | {len(duplicates)} |")
    lines.append("")
    if duplicates:
        lines.append("<details><summary>Duplicate package specifications</summary>")
        lines.append("")
        for record in duplicates:
            lines.append(f"- {record['package']}: files={record['files']} specs={record['specs']}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("## Compliance")
    compliance = data.get("compliance", {})
    lines.append("| Item | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| License files | {compliance.get('license_files', [])} |")
    lines.append(
        f"| Duplicate license candidates | {compliance.get('duplicate_license_candidates', [])} |"
    )
    lines.append("| .secrets.baseline present | [redacted] |")
    lines.append(
        f"| .pre-commit-config.yaml present | {compliance.get('pre_commit_config', False)} |"
    )
    lines.append("")

    lines.append("## Reproducibility")
    reproducibility = data.get("repro", {})
    lines.append("| Item | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Data manifests | {reproducibility.get('data_manifests', [])} |")
    lines.append(f"| Seed-related modules | {reproducibility.get('seed_modules', [])} |")
    lines.append(f"| Seed invocation matches | {len(reproducibility.get('seed_calls', []))} |")
    lines.append(f"| Checkpoint artefacts | {reproducibility.get('checkpoint_artifacts', [])} |")
    lines.append("")
    seed_calls = reproducibility.get("seed_calls", [])
    if seed_calls:
        lines.append("<details><summary>Seed invocation sources</summary>")
        lines.append("")
        for seed_call in seed_calls:
            lines.append(f"- {seed_call['file']}: {seed_call['keywords']}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("## Notes")
    lines.append("- Generated offline; review CLI statuses and registry entries for accuracy.")

    markdown = "\n".join(lines) + "\n"

    if write:
        out_path.write_text(markdown, encoding="utf-8")
    else:
        # Preview mode: report size only so that no repository content reaches
        # the output stream.  Use --write to persist the full report.
        sys.stderr.write(
            f"[preview] Status update ready ({len(markdown)} chars). "
            "Pass --write to save to disk.\n"
        )
    return out_path


def write_status_snapshot(data: _StatusData) -> None:
    """Persist the scan as sorted, indented JSON in ``CODEX_DIR/status_scan.json``."""
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = CODEX_DIR / "status_scan.json"
    snapshot_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def generate(author: str, date: str, write: bool) -> Path:
    """Scan configured repository paths and render a report, optionally persisting it.

    ``generate("reviewer", "2026-10-22", write=False)`` previews report size
    without writing Markdown or the JSON snapshot. Scanning failures may still
    append to the error log.
    """
    src_python_files = load_python_files(existing_src_dirs())
    doc_texts = load_docs_texts()

    stubs = scan_stubs(src_python_files)
    todo_counts = count_todos(src_python_files)
    empty_packages = find_empty_packages()
    cli_entries = discover_cli(src_python_files, doc_texts)
    registries = inspect_registries(src_python_files)
    tests = map_tests(src_python_files)
    docs_refs = docs_crossreferences(doc_texts)
    packaging = packaging_summary()
    compliance = compliance_summary()
    reproducibility = reproducibility_summary(src_python_files)

    data: _StatusData = {
        "generated_at": utc_timestamp(),
        "author": author,
        "date": date,
        "stubs": stubs,
        "todo_counts": todo_counts,
        "empty_packages": empty_packages,
        "cli": cli_entries,
        "registries": registries,
        "tests": tests,
        "docs": docs_refs,
        "packaging": packaging,
        "compliance": compliance,
        "repro": reproducibility,
        "summary": build_summary_counts(
            {
                "stubs": stubs,
                "todo_counts": todo_counts,
                "empty_packages": empty_packages,
                "cli": cli_entries,
                "registries": registries,
                "tests": tests,
            }
        ),
    }

    if write:
        write_status_snapshot(data)
    return write_report(author=author, date=date, data=data, write=write)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse --author, an optional ISO date string, and the --write switch."""
    parser = argparse.ArgumentParser(description="Generate exhaustive status update")
    parser.add_argument("--author", required=True, help="Report author name or handle")
    parser.add_argument(
        "--date", default=dt.date.today().isoformat(), help="Report date (YYYY-MM-DD)"
    )
    parser.add_argument("--write", action="store_true", help="Persist outputs instead of printing")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Run the offline scan from CLI arguments; preview unless --write is given."""
    args = parse_args(argv)
    generate(author=args.author, date=args.date, write=args.write)


if __name__ == "__main__":  # pragma: no cover
    main()
