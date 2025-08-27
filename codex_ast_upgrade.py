#!/usr/bin/env python3
"""
codex_ast_upgrade.py — Offline, no-removal, best-effort upgrade path.

What this does:
- Unzips repo, detects root.
- READMEs: remove placeholder badges/links (best-effort), inject "Fallback Modes & Flags".
- Adds tiered parsing adapters (ast -> libcst -> parso -> degraded).
- Adds extractors (imports/functions/classes/patterns) with CST support & fallbacks.
- Adds simple metrics (radon if present, else safe fallback).
- Adds plugin registries + internal/external search providers (external disabled by default).
- Writes small tests, docs, and NDJSON metrics.
- Emits unified patches under patches/.
- Appends Error-Capture blocks on any failure.

Design anchors:
- Python ast visitors (NodeVisitor)                                     # docs.python.org AST
- LibCST round-trippable CST for codemods & formatting preservation     # LibCST docs
- Parso tolerant parsing for partial/invalid code                        # parso docs
- Radon metrics taxonomy (cyclomatic, MI, Halstead)                      # radon docs
- GitHub advanced/code search patterns for design-time references        # GitHub docs

STRICTLY LOCAL: Do NOT activate any online CI/CD or remote services.
"""
import argparse, os, sys, zipfile, shutil, json, re, textwrap, datetime
from pathlib import Path

TS = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------- utils ----------
def w(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def a(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(s)

def r(p: Path) -> str:
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        try:
            from charset_normalizer import from_bytes
            data = p.read_bytes()
            best = from_bytes(data).best()
            enc = best.encoding if best else "utf-8"
            return data.decode(enc, errors="replace")
        except Exception:
            return p.read_text(errors="ignore")

def udiff(before: str, after: str, a_label: str, b_label: str) -> str:
    import difflib
    return "".join(
        difflib.unified_diff(
            before.splitlines(True),
            after.splitlines(True),
            fromfile=a_label,
            tofile=b_label,
            lineterm="",
        )
    )

def err_block(step_no: str, desc: str, msg: str, ctx: str) -> str:
    return f"""
Question for ChatGPT-5 {TS()}:
While performing [{step_no}:{desc}], encountered the following error:
{msg}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?

"""

# --------- repo handling ----------
def unzip_repo(zip_path: Path, out_dir: Path):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)

def detect_root(base: Path) -> Path:
    cands = [d for d in base.iterdir() if d.is_dir()]
    for d in cands:
        if (d / "src").exists() or (d / "functional_training.py").exists() or (d / "training").exists():
            return d
    return base

# --------- additions (code blocks) ----------
PARSERS_PY = """\
# src/codex_ml/analysis/parsers.py
# Tiered parsing: ast -> libcst -> parso -> degraded metrics-only
from __future__ import annotations
from dataclasses import dataclass
import ast

try:
    import libcst as cst  # optional
except Exception:
    cst = None
try:
    import parso  # optional
except Exception:
    parso = None

@dataclass
class ParseResult:
    mode: str
    ast_tree: object | None = None
    cst_tree: object | None = None
    parso_tree: object | None = None
    degraded: bool = False

def parse_tiered(code: str) -> ParseResult:
    # Primary: stdlib AST
    try:
        return ParseResult(mode="ast", ast_tree=ast.parse(code))
    except SyntaxError:
        pass
    # Secondary: LibCST (formatting-preserving)
    if cst is not None:
        try:
            return ParseResult(mode="cst", cst_tree=cst.parse_module(code))
        except Exception:
            pass
    # Tertiary: Parso (tolerant/partial)
    if parso is not None:
        try:
            return ParseResult(mode="parso", parso_tree=parso.parse(code))
        except Exception:
            pass
    # Last resort: degraded
    return ParseResult(mode="degraded", degraded=True)
"""

EXTRACTORS_PY = """\
# src/codex_ml/analysis/extractors.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import ast

try:
    import libcst as cst
except Exception:
    cst = None

@dataclass
class Extraction:
    imports: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)

class _ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.items = []
    def visit_Import(self, node: ast.Import):
        for n in node.names:
            self.items.append({"type":"import", "name": n.name, "asname": n.asname})
    def visit_ImportFrom(self, node: ast.ImportFrom):
        for n in node.names:
            self.items.append({"type":"from", "module": node.module, "name": n.name, "asname": n.asname, "level": node.level})

class _FuncVisitor(ast.NodeVisitor):
    def __init__(self): self.items=[]
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.items.append({"name": node.name, "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else "" for d in node.decorator_list],
                           "args": [a.arg for a in node.args.args], "returns": getattr(getattr(node, "returns", None), "id", None)})
        self.generic_visit(node)

class _ClassVisitor(ast.NodeVisitor):
    def __init__(self): self.items=[]
    def visit_ClassDef(self, node: ast.ClassDef):
        bases = [ast.unparse(b) if hasattr(ast, "unparse") else getattr(getattr(b, "id", None), "id", None) for b in node.bases]
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        self.items.append({"name": node.name, "bases": bases, "methods": methods})
        self.generic_visit(node)

def extract_ast(tree: ast.AST) -> Extraction:
    out = Extraction()
    iv = _ImportVisitor(); iv.visit(tree); out.imports = iv.items
    fv = _FuncVisitor(); fv.visit(tree); out.functions = fv.items
    cv = _ClassVisitor(); cv.visit(tree); out.classes = cv.items
    # Patterns: small examples
    out.patterns.append({"context_managers": any(isinstance(n, ast.With) for n in ast.walk(tree))})
    out.patterns.append({"comprehensions": any(isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for n in ast.walk(tree))})
    return out

def extract_cst(module) -> Extraction:
    # Minimal CST extraction; preserves formatting in follow-up codemods
    out = Extraction()
    try:
        # Imports via CST
        for n in module.body:
            if cst and isinstance(n, cst.SimpleStatementLine):
                code = n.code
                if "import " in code:
                    out.imports.append({"raw": code})
    except Exception:
        pass
    return out

def extract_parso(tree) -> Extraction:
    # Minimal tolerant extraction
    return Extraction()

def extract_degraded(code: str) -> Extraction:
    # Regex/line-based approximations
    import re
    out = Extraction()
    for m in re.finditer(r"^\s*def\s+(\w+)\(", code, re.M): out.functions.append({"name": m.group(1), "approx": True})
    for m in re.finditer(r"^\s*class\s+(\w+)\(", code, re.M): out.classes.append({"name": m.group(1), "approx": True})
    for m in re.finditer(r"^\s*import\s+([\w\.]+)", code, re.M): out.imports.append({"type":"import","name":m.group(1),"approx":True})
    return out
"""

REGISTRY_PY = """\
# src/codex_ml/analysis/registry.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class Registry:
    parsers: Dict[str, Callable] | None = None
    extractors: Dict[str, Callable] | None = None

REG = Registry(parsers={}, extractors={})
def register_parser(name: str, fn): REG.parsers[name]=fn
def register_extractor(name: str, fn): REG.extractors[name]=fn
"""

PROVIDERS_PY = """\
# src/codex_ml/analysis/providers.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SearchResult:
    where: str
    snippet: str
    meta: dict

class SearchProvider:
    def search(self, query: str) -> List[dict]:
        raise NotImplementedError

class InternalRepoSearch(SearchProvider):
    def __init__(self, root): self.root=root
    def search(self, query: str) -> List[dict]:
        out=[]
        import re, glob, os
        pat = re.compile(re.escape(query), re.I)
        for path in glob.glob(str(self.root / "**/*.py"), recursive=True):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if pat.search(line):
                            out.append({"where": path, "line": i, "snippet": line.strip()})
            except Exception:
                pass
        return out

class ExternalWebSearch(SearchProvider):
    def __init__(self): pass
    def search(self, query: str) -> List[dict]:
        # Disabled by default in offline policy. Placeholder only.
        return [{"disabled": True, "query": query}]
"""

METRICS_PY = """\
# src/codex_ml/analysis/metrics.py
from __future__ import annotations
import math

def mccabe_minimal(ast_tree) -> int:
    # very rough: count of branches + 1
    import ast
    branches = (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Try, ast.With, ast.BoolOp)
    return 1 + sum(1 for n in ast.walk(ast_tree) if isinstance(n, branches))

def perplexity_from_mean_nll(mean_nll: float | None):
    try:
        return math.exp(float(mean_nll))
    except Exception:
        return None
"""

CLI_PY = """\
# src/codex_ml/cli/audit_pipeline.py
from __future__ import annotations
import json, os, ast
from pathlib import Path
from typing import Dict, Any, Iterable
from codex_ml.analysis.parsers import parse_tiered
from codex_ml.analysis.extractors import (
    extract_ast, extract_cst, extract_parso, extract_degraded
)
from codex_ml.analysis.metrics import mccabe_minimal, perplexity_from_mean_nll
from codex_ml.analysis.providers import InternalRepoSearch, ExternalWebSearch

DEGRADED_BANNER = "# NOTE: Degraded mode; structures approximated.\n"

def _to_serializable(obj):
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)

def audit_file(path: Path) -> Dict[str, Any]:
    code = path.read_text(encoding="utf-8", errors="ignore")
    pr = parse_tiered(code)
    res = {"file": str(path), "mode": pr.mode, "degraded": pr.degraded}

    if pr.mode == "ast":
        out = extract_ast(pr.ast_tree)
        complexity = mccabe_minimal(pr.ast_tree)
    elif pr.mode == "cst":
        out = extract_cst(pr.cst_tree)
        # Complexity requires AST; mark as None when not available
        complexity = None
    elif pr.mode == "parso":
        out = extract_parso(pr.parso_tree)
        complexity = None
    else:  # degraded
        out = extract_degraded(code)
        complexity = None

    res["extraction"] = {
        "imports": [_to_serializable(x) for x in getattr(out, "imports", [])],
        "functions": [_to_serializable(x) for x in getattr(out, "functions", [])],
        "classes": [_to_serializable(x) for x in getattr(out, "classes", [])],
        "patterns": [_to_serializable(x) for x in getattr(out, "patterns", [])],
    }
    res["metrics"] = {
        "mccabe_minimal": complexity,
        # placeholder: example of safe best-effort metric shape
        "fallback_perplexity": perplexity_from_mean_nll(None),
    }
    if pr.mode == "degraded":
        res["banner"] = DEGRADED_BANNER.strip()
    return res

def _iter_py_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        # skip venvs, build, dist, hidden vendor dirs
        if any(s in p.parts for s in (".venv", "venv", "build", "dist", ".eggs", ".git", ".mypy_cache", ".pytest_cache")):
            continue
        yield p

def audit_repo(root: Path, *, use_external_search: bool = False) -> Dict[str, Any]:
    results = []
    for path in _iter_py_files(root):
        try:
            results.append(audit_file(path))
        except Exception as e:
            results.append({
                "file": str(path),
                "error": repr(e),
                "error_capture": {
                    "template": "Question for ChatGPT-5 {ts}:\nWhile performing [AUDIT_FILE:parse/extract], encountered the following error:\n{err}\nContext: file={file}\nWhat are the possible causes, and how can this be resolved while preserving intended functionality?"
                }
            })

    # Research → Integrate → Validate → Measure → Iterate (RIVMI)
    providers = [InternalRepoSearch(root)]
    if use_external_search:
        providers.append(ExternalWebSearch())

    evidence = []
    for q in (
        "AST parsing utilities", "decorators and type hints",
        "import graph / aliases", "complexity metrics"
    ):
        for prov in providers:
            try:
                evidence.extend(prov.search(q))
            except Exception:
                pass

    return {"root": str(root), "files": results, "evidence": evidence}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=".")
    ap.add_argument("--external-search", action="store_true", help="disabled by default; offline policy preferred")
    ap.add_argument("--out", type=str, default="analysis_report.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    report = audit_repo(root, use_external_search=bool(args.external_search))

    # ensure deterministic-ish ordering
    report["files"] = sorted(report["files"], key=lambda x: x.get("file", ""))
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "summary": {
            "root": str(root),
            "files_analyzed": len(report["files"]),
            "evidence_items": len(report["evidence"]),
            "out": args.out
        }
    }, indent=2))

if __name__ == "__main__":
    main()
"""

