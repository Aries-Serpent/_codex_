# src/codex_ml/cli/audit_pipeline.py
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from codex_ml.analysis.extractors import (
    extract_ast,
    extract_cst,
    extract_degraded,
    extract_parso,
)
from codex_ml.analysis.metrics import mccabe_minimal, perplexity_from_mean_nll
from codex_ml.analysis.parsers import parse_tiered
from codex_ml.analysis.providers import ExternalWebSearch, InternalRepoSearch
from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = run_cmd

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
            for s in (
                ".venv",
                "venv",
                "build",
                "dist",
                ".eggs",
                ".git",
                ".mypy_cache",
                ".pytest_cache",
            )
        ):
            continue
        yield p


def audit_repo(
    root: Path,
    *,
    use_external_search: bool | None = None,
    external_search_endpoint: str | None = None,
    external_search_timeout: float | None = None,
) -> Dict[str, Any]:
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

    external_kwargs: Dict[str, Any] = {}
    if external_search_endpoint is not None:
        external_kwargs["endpoint"] = external_search_endpoint
    if external_search_timeout is not None:
        external_kwargs["timeout"] = external_search_timeout
    if use_external_search is not None:
        external_kwargs["enabled"] = use_external_search

    external_provider = ExternalWebSearch(**external_kwargs)
    if external_provider.enabled:
        providers.append(external_provider)

    evidence = []
    for q in (
        "AST parsing utilities",
        "decorators and type hints",
        "import graph / aliases",
        "complexity metrics",
    ):
        for prov in providers:
            try:
                outcome = prov.search(q)
            except Exception as exc:
                evidence.append(
                    {
                        "provider": prov.__class__.__name__.lower(),
                        "query": q,
                        "status": "error",
                        "error": repr(exc),
                    }
                )
                continue

            if isinstance(outcome, dict):
                provider_name = outcome.get("provider") or prov.__class__.__name__.lower()
                status = outcome.get("status", "unknown")
                provider_results = outcome.get("results", [])
                for item in provider_results:
                    if isinstance(item, dict):
                        item.setdefault("provider", provider_name)
                        item.setdefault("query", q)
                        evidence.append(item)
                if status != "ok":
                    details = {
                        "provider": provider_name,
                        "query": q,
                        "status": status,
                    }
                    for key in ("reason", "error", "status_code"):
                        if key in outcome:
                            details[key] = outcome[key]
                    evidence.append(details)
            elif isinstance(outcome, list):
                for item in outcome:
                    if isinstance(item, dict):
                        item.setdefault("provider", prov.__class__.__name__.lower())
                        item.setdefault("query", q)
                        evidence.append(item)

    return {"root": str(root), "files": results, "evidence": evidence}


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    ap = ArgparseJSONParser()
    ap.add_argument("--root", type=str, default=".")
    ap.add_argument(
        "--external-search",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Enable or disable the external web search provider. Defaults to"
            " the environment configuration (disabled when unset)."
        ),
    )
    ap.add_argument(
        "--external-search-endpoint",
        type=str,
        default=None,
        help=(
            "Override the external search endpoint. Accepts HTTP URLs or"
            " file paths (prefix with file:// for absolute paths)."
        ),
    )
    ap.add_argument(
        "--external-search-timeout",
        type=float,
        default=None,
        help="Override the HTTP timeout in seconds for the external provider.",
    )
    ap.add_argument("--out", type=str, default="analysis_report.json")
    arg_list: List[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = ap.parse_args(arg_list)
        log_event(logger, "cli.start", prog=ap.prog, args=arg_list)

        root = Path(args.root).resolve()
        report = audit_repo(
            root,
            use_external_search=args.external_search,
            external_search_endpoint=args.external_search_endpoint,
            external_search_timeout=args.external_search_timeout,
        )
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
        log_event(
            logger,
            "cli.finish",
            prog=ap.prog,
            status="ok",
            root=str(root),
            output_path=str(args.out),
            files_analyzed=len(report["files"]),
            evidence_items=len(report["evidence"]),
        )
        return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
