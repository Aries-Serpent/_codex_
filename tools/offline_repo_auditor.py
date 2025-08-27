#!/usr/bin/env python3
# [Tool]: Offline Repository Auditor
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
"""
Offline static analyzer for codebases.

- Walks a repository tree without any network access
- Detects stubs (TODO/FIXME/TBD, NotImplementedError, pass placeholders)
- Summarizes structure (dirs/files), languages, and pattern counts
- Heuristically audits capabilities and emits a Markdown report

Usage:
  python tools/offline_repo_auditor.py --root . --out CODEBASE_AUDIT_LOCAL.md [--debug]

No external dependencies; stdlib only.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import fnmatch
import io
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

# -------------------------
# Utilities
# -------------------------

TEXT_EXTS = {
    ".py",
    ".md",
    ".rst",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".sh",
    ".bash",
    ".zsh",
    ".json",
    ".ipynb",
}
CODE_EXTS = {".py", ".sh"}
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".nox",
    ".idea",
    ".vscode",
    "site-packages",
    "build",
    "dist",
    ".eggs",
    ".ruff_cache",
}

STUB_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bTBD\b",
    r"NotImplementedError",
    r"\braise\s+NotImplementedError\b",
    r"^\s*pass\s*(#.*)?$",
]


@dataclass
class FileFinding:
    path: str
    line_no: int
    kind: str
    line: str


@dataclass
class PyStructure:
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    docstrings: int = 0
    loc: int = 0
    comments: int = 0


@dataclass
class RepoSummary:
    top_dirs: List[str] = field(default_factory=list)
    top_files: List[str] = field(default_factory=list)
    stubs: List[FileFinding] = field(default_factory=list)
    py_structs: Dict[str, PyStructure] = field(default_factory=dict)
    notebooks: List[str] = field(default_factory=list)
    configs: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)


# -------------------------
# Core Analyzer
# -------------------------


class IntuitiveAptitude:
    """Code ingestion, analysis & pattern replication system (simplified)"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.summary = RepoSummary()

    def log(self, msg: str) -> None:
        if self.debug:
            print(f"[audit] {msg}", file=sys.stderr)

    def walk_repo(self, root: str) -> Iterable[str]:
        for dirpath, dirnames, filenames in os.walk(root):
            # prune ignored dirs
            dirnames[:] = [
                d
                for d in dirnames
                if d not in IGNORE_DIRS and not d.startswith(".mamba")
            ]
            for name in filenames:
                yield os.path.join(dirpath, name)

    def is_text(self, path: str) -> bool:
        ext = os.path.splitext(path)[1].lower()
        return ext in TEXT_EXTS

    def scan_stubs(self, path: str, content: str) -> List[FileFinding]:
        findings: List[FileFinding] = []
        lines = content.splitlines()
        for i, line in enumerate(lines, start=1):
            for pat in STUB_PATTERNS:
                if re.search(pat, line):
                    findings.append(
                        FileFinding(path=path, line_no=i, kind=pat, line=line.strip())
                    )
                    break
        return findings

    def parse_py(self, path: str, content: str) -> Optional[PyStructure]:
        try:
            tree = ast.parse(content)
        except Exception:
            return None
        imports, functions, classes = [], [], []
        docstrings = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    mod = getattr(node, "module", None)
                    if isinstance(node, ast.Import):
                        mods = [alias.name for alias in node.names]
                        imports.extend(mods)
                    else:
                        base = mod or ""
                        names = [alias.name for alias in node.names]
                        imports.extend([f"{base}.{n}" if base else n for n in names])
                except Exception:
                    pass
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                if ast.get_docstring(node):
                    docstrings += 1
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                if ast.get_docstring(node):
                    docstrings += 1
        # LOC and comments
        loc = content.count("\n") + 1
        comments = sum(
            1 for line in content.splitlines() if line.strip().startswith("#")
        )
        return PyStructure(
            imports=imports,
            functions=functions,
            classes=classes,
            docstrings=docstrings,
            loc=loc,
            comments=comments,
        )

    def collect(self, root: str) -> RepoSummary:
        root = os.path.abspath(root)
        self.log(f"Scanning root: {root}")
        # Top-level
        try:
            entries = os.listdir(root)
        except Exception as e:
            raise RuntimeError(f"Failed to listdir({root}): {e}") from e
        self.summary.top_dirs = sorted(
            [e for e in entries if os.path.isdir(os.path.join(root, e))]
        )
        self.summary.top_files = sorted(
            [e for e in entries if os.path.isfile(os.path.join(root, e))]
        )

        for path in self.walk_repo(root):
            rel = os.path.relpath(path, root)
            ext = os.path.splitext(path)[1].lower()
            if ext == ".ipynb":
                self.summary.notebooks.append(rel)
            if ext in {".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}:
                self.summary.configs.append(rel)
            if fnmatch.fnmatch(rel, "tests/test_*.py") or fnmatch.fnmatch(
                rel, "test/*.py"
            ):
                self.summary.tests.append(rel)

            if not self.is_text(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            # Stubs
            self.summary.stubs.extend(self.scan_stubs(rel, content))

            # Python structures
            if ext == ".py":
                ps = self.parse_py(rel, content)
                if ps:
                    self.summary.py_structs[rel] = ps

        return self.summary

    # Heuristic checks for capabilities (based on filenames, imports, symbols)
    def guess_capabilities(self, summary: RepoSummary) -> Dict[str, str]:
        caps: Dict[str, str] = {}

        def seen_import(prefix: str) -> bool:
            for st in summary.py_structs.values():
                if any(im.startswith(prefix) for im in st.imports):
                    return True
            return False

        def seen_file(pattern: str) -> bool:
            return any(
                fnmatch.fnmatch(p, pattern)
                for p in list(summary.py_structs.keys())
                + summary.configs
                + summary.top_files
            )

        # Tokenization
        caps["tokenization"] = (
            "Implemented"
            if any("tokenizer" in p.lower() for p in summary.py_structs.keys())
            else "Missing"
        )

        # Modeling
        if seen_import("torch") or any(
            "model" in p.lower() for p in summary.py_structs.keys()
        ):
            caps["modeling"] = "Partially Implemented"
        else:
            caps["modeling"] = "Missing"

        # Training
        if seen_import("transformers") or any(
            "train" in p.lower() for p in summary.py_structs.keys()
        ):
            caps["training"] = "Partially Implemented"
        else:
            caps["training"] = "Missing"

        # Config
        if summary.configs:
            caps["config"] = "Implemented"
        else:
            caps["config"] = "Missing"

        # Evaluation
        caps["evaluation"] = (
            "Partially Implemented"
            if any("eval" in p.lower() for p in summary.py_structs.keys())
            else "Missing"
        )

        # Logging/Monitoring
        if (
            seen_import("torch.utils.tensorboard")
            or seen_import("mlflow")
            or seen_import("wandb")
        ):
            caps["logging"] = "Partially Implemented"
        else:
            caps["logging"] = "Missing"

        # Checkpointing
        if any(
            "checkpoint" in p.lower() or "ckpt" in p.lower()
            for p in summary.py_structs.keys()
        ):
            caps["checkpointing"] = "Partially Implemented"
        else:
            caps["checkpointing"] = "Missing"

        # Data Handling
        if any(
            "data" in p.split(os.sep)[0].lower() or "dataset" in p.lower()
            for p in summary.py_structs.keys()
        ):
            caps["data"] = "Partially Implemented"
        else:
            caps["data"] = "Missing"

        # Security
        if (
            any(f in summary.top_files for f in ["requirements.txt", "pyproject.toml"])
            or seen_file("poetry.lock")
            or seen_file("uv.lock")
            or seen_file("requirements-lock.txt")
        ):
            caps["security"] = "Partially Implemented"
        else:
            caps["security"] = "Missing"

        # Internal CI/Test
        if summary.tests or any(
            f in summary.top_files
            for f in ["tox.ini", "noxfile.py", ".pre-commit-config.yaml"]
        ):
            caps["ci"] = "Implemented"
        else:
            caps["ci"] = "Missing"

        # Deployment
        if any(
            f in summary.top_files for f in ["pyproject.toml", "setup.py", "Dockerfile"]
        ):
            caps["deploy"] = "Partially Implemented"
        else:
            caps["deploy"] = "Missing"

        # Docs
        if (
            any(f.lower().startswith("readme") for f in summary.top_files)
            or summary.notebooks
        ):
            caps["docs"] = "Partially Implemented"
        else:
            caps["docs"] = "Missing"

        # Experiment Tracking
        if seen_import("mlflow") or seen_import("wandb"):
            caps["tracking"] = "Partially Implemented"
        else:
            caps["tracking"] = "Missing"

        # Extensibility
        if any("registry" in p.lower() for p in summary.py_structs.keys()):
            caps["extensibility"] = "Partially Implemented"
        else:
            caps["extensibility"] = "Missing"

        return caps

    def render_markdown(
        self, out_path: str, repo: str = "Aries-Serpent/_codex_"
    ) -> None:
        now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        buf = io.StringIO()
        w = buf.write

        # Header
        w(f"# [Audit]: Implementation Status for {repo}\n")
        w(f"> Generated: {now} | Author: offline-auditor\n\n")

        # Repo map
        w("## 1) Repo Map\n\n")
        w("- Top-level directories:\n")
        for d in self.summary.top_dirs:
            w(f"  - {d}\n")
        w("- Top-level files:\n")
        for f in self.summary.top_files:
            w(f"  - {f}\n")
        w("\n- Stub findings (top 50):\n")
        for s in self.summary.stubs[:50]:
            w(f"  - {s.path}:{s.line_no} [{s.kind}] {s.line}\n")
        if len(self.summary.stubs) > 50:
            w(f"  - ...(and {len(self.summary.stubs) - 50} more)\n")
        w("\n")

        # Capability audit
        caps = self.guess_capabilities(self.summary)
        w("## 2) Capability Audit Table\n\n")
        w("| Capability | Status |\n|---|---|\n")
        ordered = [
            ("Tokenization", "tokenization"),
            ("ChatGPT Codex Modeling", "modeling"),
            ("Training Engine", "training"),
            ("Configuration Management", "config"),
            ("Evaluation & Metrics", "evaluation"),
            ("Logging & Monitoring", "logging"),
            ("Checkpointing & Resume", "checkpointing"),
            ("Data Handling", "data"),
            ("Security & Safety", "security"),
            ("Internal CI/Test", "ci"),
            ("Deployment", "deploy"),
            ("Documentation & Examples", "docs"),
            ("Experiment Tracking", "tracking"),
            ("Extensibility", "extensibility"),
        ]
        for title, key in ordered:
            w(f"| {title} | {caps.get(key, 'Missing')} |\n")
        w("\n")

        # Findings
        w("## 3) High-Signal Findings\n\n")
        w(
            "- Automated heuristic assessment; validate against your code’s ground truth.\n"
        )
        w("- Add deterministic seeding and RNG capture if absent.\n")
        w("- Provide offline-safe logging (TB/NDJSON) and MLflow local tracking.\n")
        w("- Ensure configs exist for seed/device/dtype/precision.\n")
        w("- Add tests and tox gate to enforce offline correctness.\n\n")

        # Save
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(buf.getvalue())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=".", help="Repository root")
    ap.add_argument("--out", type=str, required=True, help="Output Markdown path")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    auditor = IntuitiveAptitude(debug=args.debug)
    try:
        auditor.collect(args.root)
    except Exception as e:
        # Emit a minimal report with error capture
        now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(f"# [Audit]: Collection Error\n> Generated: {now}\n\n")
            f.write("```\n")
            f.write(f"Question for ChatGPT-5 {now}:\n")
            f.write(
                "While performing STEP_1:REPO_TRAVERSAL, encountered the following error:\n"
            )
            f.write(f"{e}\n")
            f.write("Context: offline auditor execution.\n")
            f.write(
                "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
            )
            f.write("```\n")
        return

    auditor.render_markdown(args.out)


if __name__ == "__main__":
    main()
