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
import argparse
import ast
import datetime
import json
import re
import shutil
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def TS() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------- utils ----------
def w(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def a(p: Path, s: str) -> None:
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
def unzip_repo(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)


def detect_root(base: Path) -> Path:
    cands = [d for d in base.iterdir() if d.is_dir()]
    for d in cands:
        if (
            (d / "src").exists()
            or (d / "functional_training.py").exists()
            or (d / "training").exists()
        ):
            return d
    return base


# --------- templates ----------
def _template(text: str) -> str:
    return textwrap.dedent(text).strip("\n") + "\n"


ANALYSIS_INIT = _template(
    '''
    """Analysis utilities with tiered parsing and extraction."""

    __all__ = [
        "parsers",
        "extractors",
        "registry",
        "providers",
        "metrics",
    ]
    '''
)


ANALYSIS_PARSERS = _template(
    '''
    # src/codex_ml/analysis/parsers.py
    # Tiered parsing: ast -> libcst -> parso -> degraded metrics-only
    from __future__ import annotations

    import ast
    from dataclasses import dataclass

    try:
        import libcst as cst  # optional
    except Exception:  # pragma: no cover - optional dependency
        cst = None
    try:
        import parso  # optional
    except Exception:  # pragma: no cover - optional dependency
        parso = None


    @dataclass
    class ParseResult:
        mode: str
        ast_tree: object | None = None
        cst_tree: object | None = None
        parso_tree: object | None = None
        degraded: bool = False


    def parse_tiered(code: str) -> ParseResult:
        """Parse *code* using tiered fallbacks.

        Order: stdlib ``ast`` -> ``libcst`` -> ``parso`` -> degraded.
        The first successful parser determines the mode.
        """
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
    '''
)


ANALYSIS_EXTRACTORS = _template(
    '''
    # src/codex_ml/analysis/extractors.py
    from __future__ import annotations

    import ast
    from dataclasses import dataclass, field
    from typing import Any, Dict, List

    try:
        import libcst as cst  # optional
    except Exception:  # pragma: no cover - optional dependency
        cst = None


    @dataclass
    class Extraction:
        imports: List[Dict[str, Any]] = field(default_factory=list)
        functions: List[Dict[str, Any]] = field(default_factory=list)
        classes: List[Dict[str, Any]] = field(default_factory=list)
        patterns: List[Dict[str, Any]] = field(default_factory=list)


    class _ImportVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.items: List[Dict[str, Any]] = []

        def visit_Import(self, node: ast.Import) -> None:  # pragma: no cover - simple
            for n in node.names:
                self.items.append({"type": "import", "name": n.name, "asname": n.asname})

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # pragma: no cover - simple
            for n in node.names:
                self.items.append(
                    {
                        "type": "from",
                        "module": node.module,
                        "name": n.name,
                        "asname": n.asname,
                        "level": node.level,
                    }
                )


    class _FuncVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.items: List[Dict[str, Any]] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pragma: no cover - simple
            self.items.append(
                {
                    "name": node.name,
                    "decorators": [
                        ast.unparse(d) if hasattr(ast, "unparse") else "" for d in node.decorator_list
                    ],
                    "args": [a.arg for a in node.args.args],
                    "returns": getattr(getattr(node, "returns", None), "id", None),
                }
            )
            self.generic_visit(node)


    class _ClassVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.items: List[Dict[str, Any]] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:  # pragma: no cover - simple
            bases = [
                ast.unparse(b) if hasattr(ast, "unparse") else getattr(getattr(b, "id", None), "id", None)
                for b in node.bases
            ]
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            self.items.append({"name": node.name, "bases": bases, "methods": methods})
            self.generic_visit(node)


    def extract_ast(tree: ast.AST) -> Extraction:
        """AST-based extraction."""

        out = Extraction()
        iv = _ImportVisitor()
        iv.visit(tree)
        out.imports = iv.items
        fv = _FuncVisitor()
        fv.visit(tree)
        out.functions = fv.items
        cv = _ClassVisitor()
        cv.visit(tree)
        out.classes = cv.items
        # Patterns: simple boolean indicators
        out.patterns.append({"context_managers": any(isinstance(n, ast.With) for n in ast.walk(tree))})
        out.patterns.append(
            {
                "comprehensions": any(
                    isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for n in ast.walk(tree)
                )
            }
        )
        return out


    def extract_cst(module: Any) -> Extraction:  # pragma: no cover - simple
        """Minimal CST extraction preserving formatting."""

        out = Extraction()
        try:
            for n in module.body:  # type: ignore[attr-defined]
                if cst and isinstance(n, cst.SimpleStatementLine):
                    code = n.code
                    if "import " in code:
                        out.imports.append({"raw": code})
        except Exception:
            pass
        return out


    def extract_parso(tree: Any) -> Extraction:  # pragma: no cover - simple
        """Minimal tolerant extraction for Parso parse trees."""

        return Extraction()


    def extract_degraded(code: str) -> Extraction:
        """Regex/line-based approximations when parsing fails."""

        import re

        out = Extraction()
        for m in re.finditer(r"^\s*def\s+(\w+)\(", code, re.M):
            out.functions.append({"name": m.group(1), "approx": True})
        for m in re.finditer(r"^\s*class\s+(\w+)\(", code, re.M):
            out.classes.append({"name": m.group(1), "approx": True})
        for m in re.finditer(r"^\s*import\s+([\w\.]+)", code, re.M):
            out.imports.append({"type": "import", "name": m.group(1), "approx": True})
        return out
    '''
)


ANALYSIS_REGISTRY = _template(
    """
    # src/codex_ml/analysis/registry.py
    from dataclasses import dataclass
    from typing import Callable, Dict


    @dataclass
    class Registry:
        parsers: Dict[str, Callable] | None = None
        extractors: Dict[str, Callable] | None = None


    REG = Registry(parsers={}, extractors={})


    def register_parser(name: str, fn: Callable) -> None:
        REG.parsers[name] = fn


    def register_extractor(name: str, fn: Callable) -> None:
        REG.extractors[name] = fn


    # Default registrations bind to core implementations
    try:  # pragma: no cover - import side effects only
        from .parsers import parse_tiered
        from .extractors import extract_ast, extract_cst, extract_parso, extract_degraded

        register_parser("tiered", parse_tiered)
        register_extractor("ast", extract_ast)
        register_extractor("cst", extract_cst)
        register_extractor("parso", extract_parso)
        register_extractor("degraded", extract_degraded)
    except Exception:
        # Registration is best-effort; failures fall back to manual wiring.
        pass
    """
)

ANALYSIS_PROVIDERS = _template(
    '''
    # src/codex_ml/analysis/providers.py
    from __future__ import annotations

    import json
    import os
    from pathlib import Path
    from typing import Any, Callable, Dict, Iterable, List, Optional
    from urllib.parse import urlparse

    try:  # pragma: no cover - optional dependency
        import requests
    except Exception:  # pragma: no cover - requests missing or broken
        requests = None  # type: ignore[assignment]


    class SearchProvider:
        def search(self, query: str) -> Dict[str, Any]:  # pragma: no cover - interface
            raise NotImplementedError


    class InternalRepoSearch(SearchProvider):
        def __init__(self, root: Path) -> None:
            self.root = root

        def search(self, query: str) -> Dict[str, Any]:
            import glob
            import re

            results: List[Dict[str, Any]] = []
            pattern = re.compile(re.escape(query), re.I)
            for path in glob.glob(str(self.root / "**/*.py"), recursive=True):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                        for lineno, line in enumerate(handle, 1):
                            if pattern.search(line):
                                results.append(
                                    {
                                        "provider": "internal",
                                        "where": path,
                                        "line": lineno,
                                        "snippet": line.strip(),
                                    }
                                )
                except Exception:
                    continue
            return {"status": "ok", "query": query, "results": results}


    def _coerce_bool(value: Optional[str], default: bool = False) -> bool:
        if value is None:
            return default
        value = value.strip().lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
        try:
            return bool(int(value))
        except (TypeError, ValueError):
            return default


    def _normalise_timeout(value: Optional[str], default: float) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default


    class ExternalWebSearch(SearchProvider):
        """Configurable external search provider with offline-safe defaults."""

        DEFAULT_ENDPOINT = "https://api.duckduckgo.com/"
        _DEFAULT_PARAMS: Dict[str, Any] = {
            "format": "json",
            "no_html": 1,
            "no_redirect": 1,
        }

        def __init__(
            self,
            endpoint: str | None = None,
            *,
            timeout: float | None = None,
            enabled: bool | None = None,
            http_get: Optional[Callable[..., Any]] = None,
        ) -> None:
            env_enabled = os.getenv("CODEX_ANALYSIS_SEARCH_ENABLED")
            self.enabled = enabled if enabled is not None else _coerce_bool(env_enabled, False)

            env_endpoint = os.getenv("CODEX_ANALYSIS_SEARCH_ENDPOINT")
            if endpoint is not None:
                resolved_endpoint = endpoint.strip()
            elif env_endpoint is not None:
                resolved_endpoint = env_endpoint.strip()
            else:
                resolved_endpoint = self.DEFAULT_ENDPOINT
            self.endpoint = resolved_endpoint

            env_timeout = os.getenv("CODEX_ANALYSIS_SEARCH_TIMEOUT")
            base_timeout = timeout if timeout is not None else _normalise_timeout(env_timeout, 5.0)
            self.timeout = base_timeout if base_timeout > 0 else 5.0
            self._http_get = http_get

        def search(self, query: str) -> Dict[str, Any]:
            result: Dict[str, Any] = {
                "provider": "external_web",
                "query": query,
                "results": [],
            }

            if not self.enabled:
                result["status"] = "disabled"
                return result

            if not self.endpoint:
                result["status"] = "unavailable"
                result["reason"] = "no-endpoint"
                return result

            kind, path = self._classify_endpoint()
            if kind == "none":
                result["status"] = "unavailable"
                result["reason"] = "no-endpoint"
                return result
            if kind == "unknown":
                result["status"] = "unavailable"
                result["reason"] = "invalid-endpoint"
                return result

            if kind == "file" and path is not None:
                return self._load_offline_index(path, query, result)

            return self._perform_http(query, result)

        def _classify_endpoint(self) -> tuple[str, Optional[Path]]:
            if not self.endpoint:
                return "none", None

            parsed = urlparse(self.endpoint)
            scheme = parsed.scheme.lower()
            if scheme in {"http", "https"}:
                return "http", None
            if scheme == "file":
                netloc = parsed.netloc or ""
                path_part = parsed.path or ""

                if netloc and path_part:
                    path_part = f"/{path_part.lstrip('/')}"
                    if netloc.endswith(":"):
                        location = f"{netloc}{path_part}"
                    else:
                        location = f"//{netloc}{path_part}"
                elif netloc:
                    location = netloc
                else:
                    location = path_part

                if location.startswith("//") and len(location) > 3 and location[3] == ":":
                    location = location.lstrip("/")
                if location.startswith("/") and len(location) > 2 and location[2] == ":":
                    location = location.lstrip("/")
                path = Path(location)
                return "file", path
            if scheme and len(scheme) == 1 and self.endpoint[1:3] in (":/", ":\\"):
                return "file", Path(self.endpoint)
            if scheme:
                return "unknown", None

            candidate = Path(self.endpoint)
            return "file", candidate

        def _perform_http(self, query: str, result: Dict[str, Any]) -> Dict[str, Any]:
            http_get = self._http_get
            if http_get is None and requests is not None:
                http_get = requests.get  # type: ignore[assignment]

            if http_get is None:
                result["status"] = "unavailable"
                result["reason"] = "requests-missing"
                return result

            params = dict(self._DEFAULT_PARAMS)
            params["q"] = query

            try:
                response = http_get(self.endpoint, params=params, timeout=self.timeout)
            except Exception as exc:  # pragma: no cover - network failures via mocks
                result["status"] = "error"
                result["error"] = str(exc)
                return result

            try:
                status_code = getattr(response, "status_code", None)
                response.raise_for_status()
            except Exception as exc:
                result["status"] = "error"
                if status_code is not None:
                    result["status_code"] = status_code
                result["error"] = str(exc)
                return result

            payload: Dict[str, Any]
            try:
                if hasattr(response, "json"):
                    payload = response.json()  # type: ignore[assignment]
                else:  # pragma: no cover - fallback path for mocks
                    payload = json.loads(response.text)
            except Exception as exc:
                result["status"] = "error"
                result["error"] = f"invalid-json: {exc}"  # pragma: no cover - defensive
                return result

            result["results"] = self._normalise_payload(payload, query)
            result["status"] = "ok"
            return result

        def _normalise_payload(self, payload: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
            entries: List[Dict[str, Any]] = []

            def _append(item: Dict[str, Any]) -> None:
                if not item:
                    return
                title = item.get("Text") or item.get("text")
                url = item.get("FirstURL") or item.get("first_url")
                if not title or not url:
                    return
                entries.append(
                    {
                        "provider": "external_web",
                        "query": query,
                        "title": title,
                        "url": url,
                        "snippet": item.get("Result") or item.get("snippet", ""),
                    }
                )

            related = payload.get("RelatedTopics")
            if isinstance(related, list):
                for topic in related:
                    if isinstance(topic, dict):
                        if "Topics" in topic and isinstance(topic["Topics"], list):
                            for nested in topic["Topics"]:
                                if isinstance(nested, dict):
                                    _append(nested)
                        else:
                            _append(topic)

            results = payload.get("Results")
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        _append(item)

            return entries

        def _load_offline_index(self, path: Path, query: str, result: Dict[str, Any]) -> Dict[str, Any]:
            if not path.exists():
                result["status"] = "error"
                result["reason"] = "offline-missing"
                return result

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                result["status"] = "error"
                result["reason"] = "offline-invalid"
                result["error"] = str(exc)
                return result

            matches = data.get(query) if isinstance(data, dict) else None
            if not isinstance(matches, list):
                matches = []
            entries: List[Dict[str, Any]] = []
            for item in matches:
                if isinstance(item, dict):
                    entry = {
                        "provider": "external_web",
                        "query": query,
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    entries.append(entry)
            result["results"] = entries
            result["status"] = "ok"
            return result
    '''
)


ANALYSIS_METRICS = _template(
    '''
    # src/codex_ml/analysis/metrics.py
    from __future__ import annotations

    import ast
    import math


    def mccabe_minimal(ast_tree: ast.AST) -> int:
        """Return a rough McCabe complexity: branch nodes + 1."""

        branches = (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Try, ast.With, ast.BoolOp)
        return 1 + sum(1 for n in ast.walk(ast_tree) if isinstance(n, branches))


    def perplexity_from_mean_nll(mean_nll: float | None):
        """Convert mean negative log-likelihood to perplexity."""

        try:
            return math.exp(float(mean_nll))
        except Exception:  # pragma: no cover - defensive
            return None
    '''
)


AUDIT_PIPELINE = _template(
    """
    # src/codex_ml/cli/audit_pipeline.py
    from __future__ import annotations

    import argparse
    import json
    from pathlib import Path
    from typing import Any, Dict, Iterable

    from codex_ml.analysis.extractors import (
        extract_ast,
        extract_cst,
        extract_degraded,
        extract_parso,
    )
    from codex_ml.analysis.metrics import mccabe_minimal, perplexity_from_mean_nll
    from codex_ml.analysis.parsers import parse_tiered
    from codex_ml.analysis.providers import ExternalWebSearch, InternalRepoSearch

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
                                "Question for ChatGPT-5 {ts}:\\nWhile performing [AUDIT_FILE:parse/extract], "
                                "encountered the following error:\\n{err}\\nContext: file={file}\\n"
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
                except Exception:
                    pass
                else:
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


    def main() -> None:
        ap = argparse.ArgumentParser()
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
        args = ap.parse_args()

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


    if __name__ == "__main__":  # pragma: no cover - CLI entry
        main()
    """
)

TEST_AUDIT_PIPELINE = _template(
    '''
    # tests/analysis/test_audit_pipeline.py
    from pathlib import Path

    from codex_ml.analysis.parsers import parse_tiered
    from codex_ml.cli.audit_pipeline import audit_file


    def test_parse_tiered_ast_mode() -> None:
        code = """\nimport os\n\nclass A:\n    def f(self):\n        return os.getcwd()\n"""
        result = parse_tiered(code)
        assert result.mode == "ast"
        assert result.ast_tree is not None


    def test_audit_file_roundtrip(tmp_path: Path) -> None:
        sample = tmp_path / "sample.py"
        sample.write_text("def foo(x):\n    return x * 2\n", encoding="utf-8")
        report = audit_file(sample)
        assert report["mode"] == "ast"
        assert report["metrics"]["mccabe_minimal"] == 1
        assert report["extraction"]["functions"][0]["name"] == "foo"
    '''
)


TEST_PROVIDERS = _template(
    """
    # tests/analysis/test_providers.py
    from pathlib import Path

    from codex_ml.analysis.providers import ExternalWebSearch, InternalRepoSearch


    def test_internal_repo_search(tmp_path: Path) -> None:
        sample = tmp_path / "sample.py"
        sample.write_text("import os\n", encoding="utf-8")
        search = InternalRepoSearch(tmp_path)
        outcome = search.search("import os")
        assert outcome["status"] == "ok"
        assert outcome["query"] == "import os"
        assert any("sample.py" in r["where"] for r in outcome["results"])


    def test_external_web_search_disabled(monkeypatch) -> None:
        monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENABLED", raising=False)

        called = False

        def fail_if_called(*_args, **_kwargs):
            nonlocal called
            called = True
            raise AssertionError("HTTP layer should not be invoked when disabled")

        provider = ExternalWebSearch(http_get=fail_if_called)
        outcome = provider.search("anything")
        assert outcome["status"] == "disabled"
        assert outcome["results"] == []
        assert not called
    """
)


TEST_EXTERNAL_WEB_SEARCH = _template(
    """
    # tests/analysis/test_external_web_search.py
    import json
    from pathlib import Path
    from typing import Any, Dict

    import pytest

    from codex_ml.analysis.providers import ExternalWebSearch


    class _DummyResponse:
        def __init__(
            self,
            payload: Dict[str, Any],
            *,
            content_type: str = "application/json",
            status_code: int = 200,
            raise_error: Exception | None = None,
        ) -> None:
            self._payload = payload
            self.headers = {"Content-Type": content_type}
            self.status_code = status_code
            self._raise_error = raise_error

        def json(self) -> Dict[str, Any]:
            return self._payload

        def raise_for_status(self) -> None:
            if self._raise_error:
                raise self._raise_error

        @property
        def text(self) -> str:  # pragma: no cover - fallback path
            return json.dumps(self._payload)


    def test_external_search_uses_default_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENABLED", raising=False)
        monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENDPOINT", raising=False)
        monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_TIMEOUT", raising=False)

        payload = {
            "RelatedTopics": [
                {"Text": "Python", "FirstURL": "https://example.com/python"},
            ]
        }
        response = _DummyResponse(payload)
        captured: Dict[str, Any] = {}

        def fake_get(endpoint: str, params: Dict[str, Any], timeout: float) -> _DummyResponse:
            captured["endpoint"] = endpoint
            captured["params"] = params
            captured["timeout"] = timeout
            return response

        provider = ExternalWebSearch(enabled=True, http_get=fake_get, timeout=3.5)
        outcome = provider.search("python")

        assert outcome["status"] == "ok"
        assert captured["endpoint"] == ExternalWebSearch.DEFAULT_ENDPOINT
        assert captured["params"] == {
            "format": "json",
            "no_html": 1,
            "no_redirect": 1,
            "q": "python",
        }
        assert captured["timeout"] == pytest.approx(3.5)
        assert outcome["results"]


    def test_external_search_reports_unavailable_without_endpoint() -> None:
        provider = ExternalWebSearch(endpoint="", enabled=True)
        outcome = provider.search("python")
        assert outcome["status"] == "unavailable"
        assert outcome["reason"] == "no-endpoint"


    def test_external_search_captures_http_errors() -> None:
        def failing_get(*_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("boom")

        provider = ExternalWebSearch(
            endpoint="https://search.example/api",
            enabled=True,
            http_get=failing_get,
        )

        outcome = provider.search("python")
        assert outcome["status"] == "error"
        assert "boom" in outcome["error"]


    def test_external_search_handles_http_status_errors() -> None:
        payload: Dict[str, Any] = {}
        response = _DummyResponse(payload, raise_error=RuntimeError("bad response"), status_code=503)

        def fake_get(*_args: Any, **_kwargs: Any) -> _DummyResponse:
            return response

        provider = ExternalWebSearch(
            endpoint="https://search.example/api",
            enabled=True,
            http_get=fake_get,
        )
        outcome = provider.search("python")
        assert outcome["status"] == "error"
        assert outcome["status_code"] == 503
        assert "bad response" in outcome["error"]


    def test_external_search_success_normalises_payload(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_ANALYSIS_SEARCH_ENABLED", "1")

        payload = {
            "RelatedTopics": [
                {"Text": "Python", "FirstURL": "https://example.com/python"},
                {
                    "Topics": [
                        {"Text": "PyPI", "FirstURL": "https://pypi.org"},
                    ]
                },
            ]
        }

        response = _DummyResponse(payload)

        def fake_get(endpoint: str, params: Dict[str, Any], timeout: float) -> _DummyResponse:
            assert endpoint == "https://search.example/api"
            assert params["q"] == "python"
            assert params["format"] == "json"
            assert timeout == pytest.approx(2.5)
            return response

        provider = ExternalWebSearch(
            endpoint="https://search.example/api",
            timeout=2.5,
            enabled=True,
            http_get=fake_get,
        )
        outcome = provider.search("python")

        assert outcome["status"] == "ok"
        titles = [item["title"] for item in outcome["results"]]
        assert "Python" in titles
        assert "PyPI" in titles
        assert all(item["provider"] == "external_web" for item in outcome["results"])


    def test_external_search_supports_offline_index(tmp_path: Path) -> None:
        index = tmp_path / "index.json"
        index.write_text(
            json.dumps(
                {
                    "python": [
                        {"title": "Python", "url": "https://example.com/python", "snippet": "Lang"}
                    ],
                    "other": [],
                }
            ),
            encoding="utf-8",
        )

        provider = ExternalWebSearch(endpoint=str(index), enabled=True)
        outcome = provider.search("python")

        assert outcome["status"] == "ok"
        assert outcome["results"][0]["title"] == "Python"


    def test_external_search_missing_offline_index(tmp_path: Path) -> None:
        provider = ExternalWebSearch(endpoint=str(tmp_path / "missing.json"), enabled=True)
        outcome = provider.search("python")
        assert outcome["status"] == "error"
        assert outcome["reason"] == "offline-missing"


    def test_external_search_invalid_endpoint() -> None:
        provider = ExternalWebSearch(endpoint="ftp://example.com/index", enabled=True)
        outcome = provider.search("python")
        assert outcome["status"] == "unavailable"
        assert outcome["reason"] == "invalid-endpoint"
    """
)


DOC_ANALYSIS_OVERVIEW = _template(
    """
    # docs/analysis/audit_pipeline.md
    # Analysis audit pipeline overview

    ## Tiered parsing and fallbacks

    The analysis pipeline inspects Python sources with a multi-layer parsing
    strategy:

    - **AST (stdlib)** for fast structural inspection.
    - **LibCST** when formatting preservation is required and `libcst` is
      installed.
    - **Parso** as a tolerant parser for partially-valid sources.
    - **Degraded** regex extraction when no parser succeeds.

    ## CLI usage

    Run the audit locally:

    ```bash
    python -m codex_ml.cli.audit_pipeline --root . --out analysis_report.json
    ```

    Optional external search is disabled by default. Enable it explicitly
    (offline indexes supported via `file://` paths):

    ```bash
    python -m codex_ml.cli.audit_pipeline --root . --external-search --external-search-endpoint file://index.json
    ```

    ## Outputs

    - JSON report containing per-file extraction + metrics.
    - NDJSON metrics stream saved under `.codex/` for offline review.
    - Evidence snippets from internal (and optional external) search providers.
    """
)


FALLBACK_SECTION = _template(
    """
    ## Fallback Modes & Feature Flags

    The analysis utilities provide tiered parsing with safe fallbacks and optional features:

    - Tiered parsing: [`parsers.py`](src/codex_ml/analysis/parsers.py)
    - Metrics helpers: [`metrics.py`](src/codex_ml/analysis/metrics.py)
    - Optional external search via `--external-search` (disabled by default).
    """
)


CHANGELOG_ENTRY = _template(
    """
    ## 2025-11-23 – Tiered parsing and offline audit pipeline

    - Added analysis modules with tiered parsing fallbacks and search providers.
    - Added CLI `codex_ml.cli.audit_pipeline` and tests for AST extraction.
    - Documented "Fallback Modes & Feature Flags" in README.
    - Deferred advanced codemods and online external search; kept AST-only analyzers as fallback.
    """
)


FILE_TEMPLATES: Dict[Path, str] = {
    Path("src/codex_ml/analysis/__init__.py"): ANALYSIS_INIT,
    Path("src/codex_ml/analysis/parsers.py"): ANALYSIS_PARSERS,
    Path("src/codex_ml/analysis/extractors.py"): ANALYSIS_EXTRACTORS,
    Path("src/codex_ml/analysis/registry.py"): ANALYSIS_REGISTRY,
    Path("src/codex_ml/analysis/providers.py"): ANALYSIS_PROVIDERS,
    Path("src/codex_ml/analysis/metrics.py"): ANALYSIS_METRICS,
    Path("src/codex_ml/cli/audit_pipeline.py"): AUDIT_PIPELINE,
}

TEST_TEMPLATES: Dict[Path, str] = {
    Path("tests/analysis/test_audit_pipeline.py"): TEST_AUDIT_PIPELINE,
    Path("tests/analysis/test_providers.py"): TEST_PROVIDERS,
    Path("tests/analysis/test_external_web_search.py"): TEST_EXTERNAL_WEB_SEARCH,
}

DOC_TEMPLATES: Dict[Path, str] = {
    Path("docs/analysis/audit_pipeline.md"): DOC_ANALYSIS_OVERVIEW,
}

METRIC_TARGETS: List[Path] = [
    Path("src/codex_ml/analysis/registry.py"),
    Path("src/codex_ml/analysis/extractors.py"),
    Path("src/codex_ml/analysis/parsers.py"),
    Path("src/codex_ml/analysis/providers.py"),
    Path("src/codex_ml/analysis/metrics.py"),
    Path("src/codex_ml/cli/audit_pipeline.py"),
]


@dataclass
class UpgradeContext:
    root: Path
    errors: List[str] = field(default_factory=list)
    patches: Dict[str, str] = field(default_factory=dict)
    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)


# --------- helpers ----------
def _record_diff(ctx: UpgradeContext, rel_path: Path, before: str, after: str) -> None:
    if before == after:
        return
    rel = rel_path.as_posix()
    diff = udiff(before, after, f"a/{rel}", f"b/{rel}")
    if diff.strip():
        ctx.patches[rel] = diff


def _write_with_patch(ctx: UpgradeContext, rel_path: Path, content: str) -> None:
    abs_path = ctx.root / rel_path
    before = r(abs_path)
    if before == content:
        return
    w(abs_path, content)
    _record_diff(ctx, rel_path, before, content)
    if before:
        ctx.updated.append(rel_path.as_posix())
    else:
        ctx.created.append(rel_path.as_posix())


def _run_step(ctx: UpgradeContext, step: str, desc: str, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive path
        block = err_block(step, desc, repr(exc), f"root={ctx.root}")
        ctx.errors.append(block)
        return None


# --------- upgrade operations ----------
def update_readmes(ctx: UpgradeContext) -> None:
    fallback_title = "## Fallback Modes & Feature Flags"
    pattern = re.compile(r"<!-- BEGIN: CODEX_BADGES -->.*?<!-- END: CODEX_BADGES -->\s*", re.S)

    for readme in ctx.root.glob("README*.md"):
        original = r(readme)
        if not original:
            continue
        updated = re.sub(pattern, "", original)
        updated = re.sub(r"^\s+", "", updated, count=1)
        if fallback_title not in updated:
            marker = re.search(r"^##\s+Continuous Integration", updated, re.M)
            if marker:
                idx = marker.start()
                updated = (
                    updated[:idx].rstrip("\n")
                    + "\n\n"
                    + FALLBACK_SECTION
                    + "\n"
                    + updated[idx:].lstrip("\n")
                )
            else:
                updated = updated.rstrip("\n") + "\n\n" + FALLBACK_SECTION + "\n"
        updated = re.sub(r"\n{3,}", "\n\n", updated)
        if updated != original:
            _write_with_patch(ctx, readme.relative_to(ctx.root), updated)


def update_changelog(ctx: UpgradeContext) -> None:
    path = ctx.root / "CHANGELOG_CODEX.md"
    original = r(path)
    if not original:
        return
    if CHANGELOG_ENTRY.strip() in original:
        return
    updated = CHANGELOG_ENTRY + "\n" + original.lstrip("\n")
    _write_with_patch(ctx, path.relative_to(ctx.root), updated)


def write_core_files(ctx: UpgradeContext) -> None:
    for rel_path, content in FILE_TEMPLATES.items():
        _write_with_patch(ctx, rel_path, content)


def write_tests(ctx: UpgradeContext) -> None:
    for rel_path, content in TEST_TEMPLATES.items():
        _write_with_patch(ctx, rel_path, content)


def write_docs(ctx: UpgradeContext) -> None:
    for rel_path, content in DOC_TEMPLATES.items():
        _write_with_patch(ctx, rel_path, content)


def write_metrics(ctx: UpgradeContext) -> None:
    records: List[Dict[str, Any]] = []
    branches = (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.Try, ast.With, ast.BoolOp)
    for rel_path in METRIC_TARGETS:
        abs_path = ctx.root / rel_path
        content = r(abs_path)
        if not content:
            continue
        try:
            tree = ast.parse(content)
        except SyntaxError:
            complexity: Optional[int] = None
        else:
            complexity = 1 + sum(1 for n in ast.walk(tree) if isinstance(n, branches))
        records.append(
            {
                "file": rel_path.as_posix(),
                "mccabe_minimal": complexity,
                "fallback_perplexity": None,
            }
        )

    records.append(
        {
            "ts": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "name": "analysis.upgrade",
            "value": len(records),
            "repo": str(ctx.root),
        }
    )

    payload = "".join(json.dumps(item) + "\n" for item in records)
    metrics_path = Path(".codex/analysis_metrics.jsonl")
    _write_with_patch(ctx, metrics_path, payload)


def emit_patch_bundle(ctx: UpgradeContext) -> None:
    if not ctx.patches:
        return
    bundle = "\n".join(ctx.patches[path] for path in sorted(ctx.patches))
    patches_dir = ctx.root / "patches"
    patches_dir.mkdir(parents=True, exist_ok=True)
    patch_path = patches_dir / "codex_ast_upgrade.patch"
    w(patch_path, bundle + "\n")


def append_errors(ctx: UpgradeContext) -> None:
    if not ctx.errors:
        return
    log_path = ctx.root / ".codex" / "errors_codex.log"
    for block in ctx.errors:
        a(log_path, block)


def summarise(ctx: UpgradeContext) -> Dict[str, Any]:
    return {
        "root": str(ctx.root),
        "created": sorted(ctx.created),
        "updated": sorted(ctx.updated),
        "patches": sorted(ctx.patches.keys()),
        "errors": len(ctx.errors),
    }


def resolve_root(args) -> Path:
    if args.archive:
        archive = Path(args.archive).expanduser().resolve()
        if not archive.exists():
            raise FileNotFoundError(f"archive not found: {archive}")
        workdir = Path(args.workdir).expanduser().resolve()
        if workdir.exists():
            if args.force:
                shutil.rmtree(workdir)
            else:
                raise FileExistsError(f"workspace already exists: {workdir}")
        unzip_repo(archive, workdir)
        return detect_root(workdir)
    root = Path(args.root or ".").expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"root not found: {root}")
    return detect_root(root)


def run_upgrade(args) -> Dict[str, Any]:
    root = resolve_root(args)
    ctx = UpgradeContext(root=root)

    _run_step(ctx, "README", "sanitize README badges and fallback block", update_readmes, ctx)
    _run_step(ctx, "CHANGELOG", "document upgrade in changelog", update_changelog, ctx)
    _run_step(ctx, "MODULES", "write analysis modules", write_core_files, ctx)
    _run_step(ctx, "TESTS", "write regression tests", write_tests, ctx)
    _run_step(ctx, "DOCS", "write analysis overview docs", write_docs, ctx)
    _run_step(ctx, "METRICS", "emit NDJSON metrics", write_metrics, ctx)
    if args.emit_patches:
        _run_step(ctx, "PATCH", "emit unified patch bundle", emit_patch_bundle, ctx)

    append_errors(ctx)
    summary = summarise(ctx)
    print(json.dumps({"summary": summary}, indent=2))
    return summary


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=str, help="Path to a .zip archive containing the repository")
    ap.add_argument("--root", type=str, help="Operate on an existing repository root")
    ap.add_argument(
        "--workdir", type=str, default="upgrade_workspace", help="Workspace for extracted archive"
    )
    ap.add_argument(
        "--force", action="store_true", help="Overwrite existing workspace when extracting archives"
    )
    ap.add_argument(
        "--no-patches", dest="emit_patches", action="store_false", help="Skip writing patch bundle"
    )
    ap.set_defaults(emit_patches=True)
    return ap


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not args.archive and not args.root:
        parser.error("provide either --archive or --root")
    run_upgrade(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
