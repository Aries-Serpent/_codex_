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

If ``--write`` is omitted the report is printed to stdout and no files are
created.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / ".codex"
STATUS_DIR = CODEX_DIR / "status"
ERROR_LOG_PATH = CODEX_DIR / "errors.ndjson"
UTC = dt.timezone.utc

SRC_DIRS: Tuple[Path, ...] = (
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


def utc_timestamp() -> str:
    return dt.datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class PythonFile:
    """Container for parsed Python file metadata."""

    path: Path
    text: str
    parsed: bool
    tree: Optional[ast.AST]
    imports: Set[str] = field(default_factory=set)


def log_error(step: str, error_message: str, context: Optional[Dict[str, str]] = None) -> None:
    """Append a JSON error record to `.codex/errors.ndjson`."""

    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": utc_timestamp() + "Z",
        "step": step,
        "error": error_message,
        "context": context or {},
    }
    try:
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    except Exception:
        # Last resort: swallow logging failures to avoid cascading issues.
        pass


def safe_read_text(path: Path) -> Tuple[str, bool]:
    """Read text from a file, logging and returning ``False`` on failure."""

    try:
        return path.read_text(encoding="utf-8"), True
    except Exception as exc:  # pragma: no cover - defensive
        log_error("read_text", str(exc), {"path": str(path)})
        return "", False


def collect_imports(tree: ast.AST) -> Set[str]:
    modules: Set[str] = set()

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> None:  # noqa: D401
            for alias in node.names:
                modules.add(alias.name.split(".")[0])

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: D401
            if node.module:
                modules.add(node.module.split(".")[0])

    ImportVisitor().visit(tree)
    return modules


def existing_src_dirs() -> List[Path]:
    dirs = [d for d in SRC_DIRS if d.exists()]
    return sorted(dirs)


def iter_python_files(paths: Iterable[Path]) -> Iterator[Path]:
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


def load_python_files(paths: Iterable[Path]) -> List[PythonFile]:
    python_files: List[PythonFile] = []
    for py_path in iter_python_files(paths):
        text, ok = safe_read_text(py_path)
        tree: Optional[ast.AST] = None
        imports: Set[str] = set()
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


def strip_docstring(body: Sequence[ast.stmt]) -> List[ast.stmt]:
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


def get_attr_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = get_attr_name(node.value)
        return f"{value}.{node.attr}" if value else node.attr
    if isinstance(node, ast.Call):
        return get_attr_name(node.func)
    return ""


def extract_raise_message(exc: ast.AST) -> Optional[str]:
    if isinstance(exc, ast.Call):
        for arg in exc.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
    if isinstance(exc, ast.Constant) and isinstance(exc.value, str):
        return exc.value
    return None


def classify_placeholder(message: Optional[str]) -> bool:
    if not message:
        return False
    lowered = message.lower()
    return any(keyword in lowered for keyword in PLACEHOLDER_KEYWORDS)


def scan_stubs(python_files: Sequence[PythonFile]) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []

    for py_file in python_files:
        if not py_file.parsed or not py_file.tree:
            continue

        rel_path = py_file.path.relative_to(REPO_ROOT)

        class StubVisitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.context: List[str] = []

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


def count_todos(python_files: Sequence[PythonFile]) -> List[Dict[str, object]]:
    todo_rows: List[Dict[str, object]] = []
    patterns = {kw: re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in TODO_KEYWORDS}

    for py_file in python_files:
        text = py_file.text
        counts = {kw: len(pattern.findall(text)) for kw, pattern in patterns.items()}
        total = sum(counts.values())
        if total:
            row = {"file": str(py_file.path.relative_to(REPO_ROOT)), "total": total}
            row.update({kw.lower(): counts[kw] for kw in TODO_KEYWORDS})
            todo_rows.append(row)

    todo_rows.sort(key=lambda item: item["file"])
    return todo_rows


def is_trivial_init(init_path: Path) -> bool:
    text, ok = safe_read_text(init_path)
    if not ok:
        return False
    stripped_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not stripped_lines:
        return True
    allowed_prefixes = ("#", "__all__", "import ", "from ")
    return all(line.startswith(allowed_prefixes) for line in stripped_lines)


def find_empty_packages() -> List[Dict[str, str]]:
    empty: List[Dict[str, str]] = []
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


def load_docs_texts() -> Dict[Path, str]:
    docs: Dict[Path, str] = {}
    if not DOCS_DIR.exists():
        return docs
    for extension in ("*.md", "*.rst"):
        for doc_path in sorted(DOCS_DIR.rglob(extension)):
            text, ok = safe_read_text(doc_path)
            if ok:
                docs[doc_path] = text
    return docs


def find_docs_mentions(doc_texts: Dict[Path, str], term: str) -> List[str]:
    mentions: List[str] = []
    lowered = term.lower()
    for doc_path, text in doc_texts.items():
        if lowered in text.lower():
            mentions.append(str(doc_path.relative_to(REPO_ROOT)))
    return sorted(set(mentions))


def classify_cli_status(body: Sequence[ast.stmt]) -> str:
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


def extract_cli_names(decorator: ast.AST) -> List[str]:
    names: List[str] = []
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


def discover_cli(
    python_files: Sequence[PythonFile], doc_texts: Dict[Path, str]
) -> List[Dict[str, object]]:
    cli_entries: List[Dict[str, object]] = []

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
            cli_names: List[str] = []
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
            docs_mentions: List[str] = []
            for candidate in {node.name, *cli_names}:
                docs_mentions.extend(find_docs_mentions(doc_texts, candidate))
            entry = {
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
    try:
        snippet = ast.get_source_segment(py_file.text, node)
        if snippet:
            return snippet.strip()
    except Exception:
        pass
    return type(node).__name__


def inspect_registries(python_files: Sequence[PythonFile]) -> List[Dict[str, object]]:
    registries: List[Dict[str, object]] = []

    for py_file in python_files:
        if "registry" not in py_file.path.name.lower():
            continue
        if not py_file.parsed or not py_file.tree:
            continue

        rel_path = str(py_file.path.relative_to(REPO_ROOT))
        entries: Dict[str, Dict[str, object]] = {}

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
                        elif isinstance(key_node, ast.Index) and isinstance(key_node.value, ast.Constant):  # type: ignore[attr-defined]
                            if isinstance(key_node.value.value, str):
                                key_value = key_node.value.value
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
                        for key_node, value_node in zip(node.value.keys, node.value.values):
                            if isinstance(key_node, ast.Constant) and isinstance(
                                key_node.value, str
                            ):
                                value_repr = registry_value_repr(py_file, value_node)
                                status = "ok"
                                lowered = value_repr.lower()
                                if lowered in {"none", "...", "ellipsis"} or any(
                                    token in lowered for token in ("todo", "tbd")
                                ):
                                    status = "unresolved"
                                entries[key_node.value] = {
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


def map_tests(python_files: Sequence[PythonFile]) -> Dict[str, object]:
    src_files = [pf for pf in python_files if pf.path.suffix == ".py"]
    module_entries: List[Dict[str, str]] = []
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

    modules_without_tests: List[str] = []
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


def docs_crossreferences(doc_texts: Dict[Path, str]) -> List[Dict[str, object]]:
    topic_patterns = {topic: re.compile(re.escape(topic), re.IGNORECASE) for topic in DOC_TOPICS}
    crossrefs: List[Dict[str, object]] = []

    for doc_path, text in doc_texts.items():
        lines = text.splitlines()
        topics: List[Dict[str, object]] = []
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


def packaging_summary() -> Dict[str, object]:
    summary: Dict[str, object] = {}

    pyproject = REPO_ROOT / "pyproject.toml"
    summary["pyproject"] = pyproject.exists()

    requirement_files: List[str] = []
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
    for candidate in ["requirements.lock", "uv.lock", "poetry.lock", "Pipfile.lock"]:
        path = REPO_ROOT / candidate
        if path.exists():
            lock_files.append(str(path.relative_to(REPO_ROOT)))
    summary["lock_files"] = sorted(lock_files)

    package_map: Dict[str, List[Dict[str, str]]] = {}
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

    duplicates: List[Dict[str, object]] = []
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


def compliance_summary() -> Dict[str, object]:
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


def reproducibility_summary(python_files: Sequence[PythonFile]) -> Dict[str, object]:
    manifest_files = [
        str(path.relative_to(REPO_ROOT))
        for path in sorted(REPO_ROOT.rglob("manifest.json"))
        if path.is_file()
    ]

    seed_modules: List[str] = []
    seed_calls: List[Dict[str, object]] = []
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
    checkpoint_files: Set[str] = set()
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


def build_summary_counts(data: Dict[str, object]) -> Dict[str, object]:
    stubs = data.get("stubs", [])
    todo_counts = data.get("todo_counts", [])
    empty_packages = data.get("empty_packages", [])
    cli_entries = data.get("cli", [])
    registries = data.get("registries", [])
    tests = data.get("tests", {})

    kind_counts: Dict[str, int] = {}
    for item in stubs:
        kind_counts[item["kind"]] = kind_counts.get(item["kind"], 0) + 1

    cli_status_counts: Dict[str, int] = {}
    for entry in cli_entries:
        status = entry["status"]
        cli_status_counts[status] = cli_status_counts.get(status, 0) + 1

    registry_status_counts: Dict[str, int] = {}
    for entry in registries:
        status = entry["status"]
        registry_status_counts[status] = registry_status_counts.get(status, 0) + 1

    summary = {
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
    return summary


def render_table_rows(rows: List[str]) -> List[str]:
    return rows if rows else ["| (none) |"]


def write_report(author: str, date: str, data: Dict[str, object], write: bool) -> Path:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STATUS_DIR / f"_codex_status_update-{date}.md"
    generated_ts = dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    summary_counts = build_summary_counts(data)

    lines: List[str] = []
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
    registry_rows: List[str] = []
    for registry in data.get("registries", []):
        entries = registry.get("entries", [])
        if entries:
            for entry in entries:
                registry_rows.append(
                    f"| {registry['registry_file']} | {entry['key']} | {entry['implementation']} | {entry['status']} |"
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
    doc_rows: List[str] = []
    for entry in data.get("docs", []):
        doc = entry["doc"]
        topics = entry.get("topics", [])
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
    lines.append(
        f"| .secrets.baseline present | {compliance.get('detect_secrets_baseline', False)} |"
    )
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
        for record in seed_calls:
            lines.append(f"- {record['file']}: {record['keywords']}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("## Notes")
    lines.append("- Generated offline; review CLI statuses and registry entries for accuracy.")

    markdown = "\n".join(lines) + "\n"

    if write:
        out_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return out_path


def write_status_snapshot(data: Dict[str, object]) -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = CODEX_DIR / "status_scan.json"
    snapshot_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def generate(author: str, date: str, write: bool) -> Path:
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

    data: Dict[str, object] = {
        "generated_at": utc_timestamp() + "Z",
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
    report_path = write_report(author=author, date=date, data=data, write=write)
    return report_path


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate exhaustive status update")
    parser.add_argument("--author", required=True, help="Report author name or handle")
    parser.add_argument(
        "--date", default=dt.date.today().isoformat(), help="Report date (YYYY-MM-DD)"
    )
    parser.add_argument("--write", action="store_true", help="Persist outputs instead of printing")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    generate(author=args.author, date=args.date, write=args.write)


if __name__ == "__main__":  # pragma: no cover
    main()
