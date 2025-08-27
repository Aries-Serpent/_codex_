# src/codex_ml/cli/audit_pipeline.py
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from codex_ml.analysis.parsers import parse_tiered
from codex_ml.analysis.extractors import (
    extract_ast,
    extract_cst,
    extract_parso,
    extract_degraded,
)
from codex_ml.analysis.metrics import mccabe_minimal, perplexity_from_mean_nll
from codex_ml.analysis.providers import InternalRepoSearch, ExternalWebSearch

DEGRADED_BANNER = "# NOTE: Degraded mode; structures approximated.\n"


def _to_serializable(obj: Any) -> Any:
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def audit_file(path: Path) -> Dict[str, Any]:
    code = path.read_text(encoding="utf-8", errors="ignore")
    pr = parse_tiered(code)
    res: Dict[str, Any] = {"file": str(path), "mode": pr.mode, "degraded": pr.degraded}

    if pr.mode == "ast" and pr.ast_tree is not None:
        out = extract_ast(pr.ast_tree)
        complexity = mccabe_minimal(pr.ast_tree)
    elif pr.mode == "cst" and pr.cst_tree is not None:
        out = extract_cst(pr.cst_tree)
        complexity = None
    elif pr.mode == "parso" and pr.parso_tree is not None:
        out = extract_parso(pr.parso_tree)
        complexity = None
    else:
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
        "fallback_perplexity": perplexity_from_mean_nll(None),
    }
    if pr.mode == "degraded":
        res["banner"] = DEGRADED_BANNER.strip()
    return res


def _iter_py_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        if any(
            s in p.parts
            for s in (".venv", "venv", "build", "dist", ".eggs", ".git", ".mypy_cache", ".pytest_cache")
        ):
            continue
        yield p


def audit_repo(root: Path, *, use_external_search: bool = False) -> Dict[str, Any]:
    results = []
    for path in _iter_py_files(root):
        try:
            results.append(audit_file(path))
        except Exception as e:  # pragma: no cover - defensive
            results.append(
                {
                    "file": str(path),
                    "error": repr(e),
                    "error_capture": {
                        "template": (
                            "Question for ChatGPT-5 {ts}:\nWhile performing [AUDIT_FILE:parse/extract], "
                            "encountered the following error:\n{err}\nContext: file={file}\n" 
                            "What are the possible causes, and how can this be resolved while preserving intended functionality?"
                        )
                    },
                }
            )

    providers = [InternalRepoSearch(root)]
    if use_external_search:
        providers.append(ExternalWebSearch())

    evidence = []
    for q in (
        "AST parsing utilities",
        "decorators and type hints",
        "import graph / aliases",
        "complexity metrics",
    ):
        for prov in providers:
            try:
                evidence.extend(prov.search(q))
            except Exception:
                pass

    return {"root": str(root), "files": results, "evidence": evidence}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=".")
    ap.add_argument(
        "--external-search", action="store_true", help="disabled by default; offline policy preferred"
    )
    ap.add_argument("--out", type=str, default="analysis_report.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    report = audit_repo(root, use_external_search=bool(args.external_search))
    report["files"] = sorted(report["files"], key=lambda x: x.get("file", ""))
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "summary": {
                    "root": str(root),
                    "files_analyzed": len(report["files"]),
                    "evidence_items": len(report["evidence"]),
                    "out": args.out,
                }
            },
            indent=2,
        )
    )


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
