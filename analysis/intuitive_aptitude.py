"""Utility module providing rich code analysis helpers.

This module exposes the :class:`intuitive_aptitude` analyzer alongside the
``analyze_and_suggest`` helper that powers lightweight static analysis
workflows in test fixtures.  The implementation mirrors a full featured
ingestion pipeline used in production, but is intentionally self contained so
that tests depending on it do not require optional third party packages.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

__all__ = [
    "intuitive_aptitude",
    "analyze_and_suggest",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
]


@dataclass
class ImportInfo:
    module: Optional[str]
    name: Optional[str]
    alias: Optional[str]
    level: int = 0


@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    defaults: int
    kwonlyargs: List[str]
    decorators: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    lineno: int
    end_lineno: Optional[int]
    complexity: int = 1
    calls: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    decorators: List[str]
    docstring: Optional[str]
    methods: Dict[str, FunctionInfo]
    lineno: int
    end_lineno: Optional[int]


def _unparse(node: ast.AST) -> str:
    """Return the source representation for ``node``.

    Python 3.9+ ships :func:`ast.unparse` which is preferred.  When running on
    older interpreters we fall back to ``astor`` if available to preserve the
    behaviour used in the original implementation.
    """

    if hasattr(ast, "unparse"):
        return ast.unparse(node)  # type: ignore[attr-defined]

    try:  # pragma: no cover - fallback path used on <3.9 only
        import astor  # type: ignore

        return astor.to_source(node).rstrip()
    except Exception as exc:  # pragma: no cover - fallback path
        raise RuntimeError(
            "Unable to unparse AST. Install Python 3.9+ or 'astor' package."
        ) from exc


class _NameRenamer(ast.NodeTransformer):
    """AST transformer that renames identifiers according to *mapping*."""

    def __init__(self, mapping: Dict[str, str]):
        super().__init__()
        self.mapping = mapping or {}

    def visit_Name(self, node: ast.Name) -> ast.AST:  # noqa: N802 (ast API)
        if node.id in self.mapping:
            return ast.copy_location(
                ast.Name(id=self.mapping[node.id], ctx=node.ctx),
                node,
            )
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:  # noqa: N802 (ast API)
        self.generic_visit(node)
        if isinstance(node.attr, str) and node.attr in self.mapping:
            node.attr = self.mapping[node.attr]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:  # noqa: N802 (ast API)
        if node.name in self.mapping:
            node.name = self.mapping[node.name]
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg in self.mapping:
                arg.arg = self.mapping[arg.arg]
        if node.args.vararg and node.args.vararg.arg in self.mapping:
            node.args.vararg.arg = self.mapping[node.args.vararg.arg]
        if node.args.kwarg and node.args.kwarg.arg in self.mapping:
            node.args.kwarg.arg = self.mapping[node.args.kwarg.arg]
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:  # noqa: N802
        if node.name in self.mapping:
            node.name = self.mapping[node.name]
        return self.generic_visit(node)

    def visit_alias(self, node: ast.alias) -> ast.AST:  # noqa: N802
        if node.name in self.mapping:
            node.name = self.mapping[node.name]
        if node.asname and node.asname in self.mapping:
            node.asname = self.mapping[node.asname]
        return node


class intuitive_aptitude:
    """Code ingestion, analysis & pattern replication system."""

    def __init__(self) -> None:
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.imports: List[ImportInfo] = []
        self.variables: Dict[str, Any] = {}
        self.patterns: Dict[str, List[Dict[str, Any]]] = {
            "error_handling": [],
            "iteration": [],
            "conditional": [],
            "function_calls": [],
        }
        self.metrics: Dict[str, float] = {
            "loc": 0,
            "comment_ratio": 0.0,
            "complexity": 0.0,
        }
        self._source: str = ""
        self.ast_tree: Optional[ast.AST] = None
        self.last_error: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(self, code: str) -> bool:
        """Parse *code* and populate analysis artefacts."""

        self.reset()
        self._source = code or ""
        try:
            self.metrics["loc"] = float(len(self._source.splitlines()))
            self.ast_tree = ast.parse(self._source)
            self._extract_imports()
            self._extract_globals()
            self._extract_functions()
            self._extract_classes()
            self._analyze_patterns()
            self._compute_metrics()
            return True
        except Exception as exc:  # pragma: no cover - defensive guard
            self.last_error = f"{type(exc).__name__}: {exc}"
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Return a high level summary of discovered artefacts."""

        return {
            "functions_count": len(self.functions),
            "classes_count": len(self.classes),
            "imports_count": len(self.imports),
            "variables_count": len(self.variables),
            "metrics": dict(self.metrics),
        }

    def get_detailed_structure(self) -> Dict[str, Any]:
        """Return the detailed structure extracted from the AST."""

        return {
            "imports": [import_info.__dict__ for import_info in self.imports],
            "functions": {k: v.__dict__ for k, v in self.functions.items()},
            "classes": {
                k: {
                    **{kk: vv for kk, vv in v.__dict__.items() if kk != "methods"},
                    "methods": {mk: mv.__dict__ for mk, mv in v.methods.items()},
                }
                for k, v in self.classes.items()
            },
            "variables": dict(self.variables),
        }

    def clone_structure(self, mappings: Dict[str, str]) -> str:
        """Replicate code using the provided *mappings* for identifiers."""

        if not self.ast_tree:
            raise ValueError("No AST available. Call ingest(code) first.")

        try:
            tree_copy = ast.parse(self._source)
            new_tree = _NameRenamer(mappings).visit(tree_copy)
            ast.fix_missing_locations(new_tree)
            return _unparse(new_tree)
        except Exception:
            code = self._source
            for old, new in mappings.items():
                code = re.sub(rf"(?<!\.)\b{re.escape(old)}\b", new, code)
                code = re.sub(rf"(\.){re.escape(old)}\b", rf"\1{new}", code)
            return code

    def extract_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.patterns

    def analyze_code_style(self) -> Dict[str, Any]:
        return {
            "naming": self._analyze_naming_conventions(),
            "indentation": self._analyze_indentation(),
            "docstrings": self._analyze_docstring_style(),
            "paradigm": self._analyze_functional_style(),
        }

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_imports(self) -> None:
        self.imports.clear()
        assert self.ast_tree is not None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(
                        ImportInfo(
                            module=None,
                            name=alias.name,
                            alias=alias.asname,
                            level=0,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.imports.append(
                        ImportInfo(
                            module=node.module,
                            name=alias.name,
                            alias=alias.asname,
                            level=getattr(node, "level", 0) or 0,
                        )
                    )

    def _extract_globals(self) -> None:
        self.variables.clear()
        assert self.ast_tree is not None
        for node in getattr(self.ast_tree, "body", []):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        self.variables[tgt.id] = "assigned"
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    self.variables[node.target.id] = "annotated"

    def _extract_functions(self) -> None:
        self.functions.clear()
        assert self.ast_tree is not None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                kwonly = [a.arg for a in node.args.kwonlyargs]
                decorators = [self._expr_to_str(d) for d in node.decorator_list]
                returns = self._expr_to_str(node.returns)
                doc = ast.get_docstring(node)
                calls = self._find_calls(node)
                complexity = self._cyclomatic_complexity(node)
                self.functions[node.name] = FunctionInfo(
                    name=node.name,
                    args=args,
                    defaults=len(node.args.defaults or []),
                    kwonlyargs=kwonly,
                    decorators=decorators,
                    returns=returns,
                    docstring=doc,
                    lineno=getattr(node, "lineno", 0),
                    end_lineno=getattr(node, "end_lineno", None),
                    complexity=complexity,
                    calls=calls,
                )

    def _extract_classes(self) -> None:
        self.classes.clear()
        assert self.ast_tree is not None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                bases = [self._expr_to_str(b) for b in node.bases]
                decorators = [self._expr_to_str(d) for d in node.decorator_list]
                doc = ast.get_docstring(node)
                methods: Dict[str, FunctionInfo] = {}
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef):
                        args = [a.arg for a in body_node.args.args]
                        kwonly = [a.arg for a in body_node.args.kwonlyargs]
                        decorators_m = [self._expr_to_str(d) for d in body_node.decorator_list]
                        returns = self._expr_to_str(body_node.returns)
                        doc_m = ast.get_docstring(body_node)
                        calls = self._find_calls(body_node)
                        complexity = self._cyclomatic_complexity(body_node)
                        methods[body_node.name] = FunctionInfo(
                            name=body_node.name,
                            args=args,
                            defaults=len(body_node.args.defaults or []),
                            kwonlyargs=kwonly,
                            decorators=decorators_m,
                            returns=returns,
                            docstring=doc_m,
                            lineno=getattr(body_node, "lineno", 0),
                            end_lineno=getattr(body_node, "end_lineno", None),
                            complexity=complexity,
                            calls=calls,
                        )
                self.classes[node.name] = ClassInfo(
                    name=node.name,
                    bases=bases,
                    decorators=decorators,
                    docstring=doc,
                    methods=methods,
                    lineno=getattr(node, "lineno", 0),
                    end_lineno=getattr(node, "end_lineno", None),
                )

    def _analyze_patterns(self) -> None:
        self.patterns = {k: [] for k in self.patterns.keys()}
        assert self.ast_tree is not None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Try):
                self.patterns["error_handling"].append(
                    {
                        "lineno": getattr(node, "lineno", 0),
                        "handlers": [self._expr_to_str(h.type) for h in node.handlers if h.type],
                        "has_finally": bool(node.finalbody),
                        "has_else": bool(node.orelse),
                    }
                )
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                kind = "for" if isinstance(node, (ast.For, ast.AsyncFor)) else "while"
                self.patterns["iteration"].append(
                    {
                        "lineno": getattr(node, "lineno", 0),
                        "kind": kind,
                        "target": self._expr_to_str(getattr(node, "target", None)),
                        "iter": self._expr_to_str(getattr(node, "iter", None)),
                        "has_else": bool(node.orelse),
                    }
                )
            elif isinstance(node, ast.If):
                self.patterns["conditional"].append(
                    {
                        "lineno": getattr(node, "lineno", 0),
                        "test": self._expr_to_str(node.test),
                        "branches": 1 + self._count_elifs(node),
                        "has_else": bool(node.orelse),
                    }
                )
            elif isinstance(node, ast.Call):
                self.patterns["function_calls"].append(
                    {
                        "lineno": getattr(node, "lineno", 0),
                        "call": self._expr_to_str(node.func),
                        "args": len(getattr(node, "args", []) or []),
                        "keywords": [kw.arg for kw in getattr(node, "keywords", []) if kw.arg],
                    }
                )

    def _compute_metrics(self) -> None:
        lines = self._source.splitlines()
        if not lines:
            self.metrics["comment_ratio"] = 0.0
        else:
            comments = sum(1 for ln in lines if re.match(r"^\s*#", ln))
            self.metrics["comment_ratio"] = round(comments / len(lines), 4)

        complexities: List[int] = [fi.complexity for fi in self.functions.values()]
        for cls in self.classes.values():
            complexities.extend(m.complexity for m in cls.methods.values())
        if complexities:
            avg = sum(complexities) / len(complexities)
            self.metrics["complexity"] = float(round(avg, 3))
        else:
            self.metrics["complexity"] = 0.0

    # ------------------------------------------------------------------
    # Style analysis helpers
    # ------------------------------------------------------------------

    def _analyze_naming_conventions(self) -> Dict[str, Any]:
        snake = camel = pascal = other = 0

        def classify(name: str) -> str:
            if re.fullmatch(r"[a-z_][a-z0-9_]*", name):
                return "snake"
            if re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)+", name):
                return "camel"
            if re.fullmatch(r"[A-Z][A-Za-z0-9]*", name):
                return "pascal"
            return "other"

        names: List[str] = []
        names.extend(self.functions.keys())
        names.extend(self.classes.keys())
        names.extend(self.variables.keys())
        for cls in self.classes.values():
            names.extend(cls.methods.keys())

        for name in names:
            kind = classify(name)
            if kind == "snake":
                snake += 1
            elif kind == "camel":
                camel += 1
            elif kind == "pascal":
                pascal += 1
            else:
                other += 1

        return {
            "snake_case": snake,
            "camelCase": camel,
            "PascalCase": pascal,
            "other": other,
        }

    def _analyze_indentation(self) -> Dict[str, Any]:
        spaces2 = spaces4 = tabs = 0
        lines = self._source.splitlines()
        for ln in lines:
            if not ln.strip():
                continue
            match = re.match(r"^([ \t]+)", ln)
            if not match:
                continue
            indent = match.group(1)
            if indent.startswith("\t"):
                tabs += 1
            else:
                clean = indent.replace("\t", "")
                if len(clean) % 4 == 0:
                    spaces4 += 1
                elif len(clean) % 2 == 0:
                    spaces2 += 1
        return {"2space": spaces2, "4space": spaces4, "tabs": tabs}

    def _analyze_docstring_style(self) -> Dict[str, Any]:
        styles = {"Google": 0, "NumPy": 0, "Sphinx": 0, "Simple": 0, "None": 0}

        def classify(doc: Optional[str]) -> None:
            if not doc:
                styles["None"] += 1
                return
            text = doc.strip()
            if re.search(r"^Args:\s", text, re.M) or re.search(r"^Returns?:\s", text, re.M):
                styles["Google"] += 1
            elif re.search(r"^-{3,}\nParameters\n-{3,}", text) or re.search(
                r"^-{3,}\nReturns?\n-{3,}", text
            ):
                styles["NumPy"] += 1
            elif re.search(r":param\s+\w+\s*:", text) or re.search(
                r":return[s]?:",
                text,
            ):
                styles["Sphinx"] += 1
            else:
                styles["Simple"] += 1

        try:
            module_doc = ast.get_docstring(self.ast_tree) if self.ast_tree else None
        except Exception:
            module_doc = None
        classify(module_doc)
        for fn in self.functions.values():
            classify(fn.docstring)
        for cls in self.classes.values():
            classify(cls.docstring)
            for method in cls.methods.values():
                classify(method.docstring)
        return styles

    def _analyze_functional_style(self) -> Dict[str, Any]:
        func_indicators = 0
        oop_indicators = 0
        comp_count = 0
        lambda_count = 0
        hof_calls = 0

        assert self.ast_tree is not None
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                comp_count += 1
                func_indicators += 1
            elif isinstance(node, ast.Lambda):
                lambda_count += 1
                func_indicators += 1
            elif isinstance(node, ast.Call):
                callee = self._expr_to_str(node.func)
                if callee in {"map", "filter", "reduce"} or (
                    isinstance(callee, str)
                    and (callee.endswith(".map") or callee.endswith(".filter"))
                ):
                    hof_calls += 1
                    func_indicators += 1
            elif isinstance(node, ast.ClassDef):
                oop_indicators += 1

        return {
            "functional_signals": func_indicators,
            "oop_signals": oop_indicators,
            "comprehensions": comp_count,
            "lambdas": lambda_count,
            "higher_order_calls": hof_calls,
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _expr_to_str(node: Optional[ast.AST]) -> Optional[str]:
        if node is None:
            return None
        try:
            return _unparse(node)
        except Exception:
            try:
                if isinstance(node, ast.Name):
                    return node.id
                if isinstance(node, ast.Attribute):
                    left = intuitive_aptitude._expr_to_str(node.value)
                    return f"{left}.{node.attr}" if left else node.attr
                if isinstance(node, ast.Constant):
                    return repr(node.value)
            except Exception:
                return None
            return None

    @staticmethod
    def _count_elifs(node_if: ast.If) -> int:
        count = 0
        orelse = node_if.orelse
        while orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If):
            count += 1
            orelse = orelse[0].orelse
        return count

    @staticmethod
    def _find_calls(fn_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> List[str]:
        calls: List[str] = []
        for node in ast.walk(fn_node):
            if isinstance(node, ast.Call):
                callee = intuitive_aptitude._expr_to_str(node.func)
                if callee:
                    calls.append(callee)
        return calls

    @staticmethod
    def _cyclomatic_complexity(fn_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        cc = 1
        for node in ast.walk(fn_node):
            if isinstance(
                node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)
            ):
                cc += 1
            elif isinstance(node, ast.BoolOp):
                cc += max(1, len(getattr(node, "values", [])) - 1)
            elif isinstance(node, ast.ExceptHandler):
                cc += 1
            elif isinstance(node, ast.comprehension):
                cc += 1
        return cc

    def reset(self) -> None:
        self.functions.clear()
        self.classes.clear()
        self.imports.clear()
        self.variables.clear()
        self.patterns = {k: [] for k in self.patterns.keys()}
        self.metrics = {"loc": 0, "comment_ratio": 0.0, "complexity": 0.0}
        self._source = ""
        self.ast_tree = None
        self.last_error = None

    # ------------------------------------------------------------------
    # Code generation helpers
    # ------------------------------------------------------------------

    def _generate_imports(self) -> str:
        lines: List[str] = []
        for imp in self.imports:
            if imp.module is None and imp.name:
                if imp.alias:
                    lines.append(f"import {imp.name} as {imp.alias}")
                else:
                    lines.append(f"import {imp.name}")
            else:
                level = "." * (imp.level or 0)
                target = f"{level}{imp.module or ''}"
                if imp.name:
                    if imp.alias:
                        lines.append(f"from {target} import {imp.name} as {imp.alias}")
                    else:
                        lines.append(f"from {target} import {imp.name}")
                else:
                    lines.append(f"import {target}")
        return "\n".join(lines)

    def _generate_functions(self) -> str:
        parts: List[str] = []
        for fn in self.functions.values():
            decos = "".join(f"@{decorator}\n" for decorator in fn.decorators if decorator)
            args = ", ".join(fn.args)
            if fn.kwonlyargs:
                args = args + (", *" if args else "*") + ", " + ", ".join(fn.kwonlyargs)
            ret = f" -> {fn.returns}" if fn.returns else ""
            doc = f'    """{fn.docstring}"""\n' if fn.docstring else "    pass\n"
            parts.append(f"{decos}def {fn.name}({args}){ret}:\n{doc}")
        return "\n\n".join(parts)

    def _generate_classes(self) -> str:
        parts: List[str] = []
        for cls in self.classes.values():
            decos = "".join(f"@{decorator}\n" for decorator in cls.decorators if decorator)
            bases = f"({', '.join(base for base in cls.bases if base)})" if cls.bases else ""
            doc = f'    """{cls.docstring}"""\n' if cls.docstring else "    pass\n"
            body: List[str] = [doc]
            for method in cls.methods.values():
                m_decos = "".join(f"@{decorator}\n" for decorator in method.decorators if decorator)
                args = ", ".join(method.args)
                if method.kwonlyargs:
                    args = args + (", *" if args else "*") + ", " + ", ".join(method.kwonlyargs)
                ret = f" -> {method.returns}" if method.returns else ""
                m_doc = (
                    f'        """{method.docstring}"""\n' if method.docstring else "        pass\n"
                )
                body.append(f"{m_decos}    def {method.name}({args}){ret}:\n{m_doc}")
            parts.append(f"{decos}class {cls.name}{bases}:\n" + "\n".join(body))
        return "\n\n".join(parts)

    def _generate_error_handling_pattern(self) -> str:
        return "\n".join(
            [
                "try:",
                "    # TODO: place guarded logic here",
                "    pass",
                "except Exception as e:",
                "    # TODO: refine exception types and remediation",
                "    raise",
                "finally:",
                "    # Optional: cleanup or finalization",
                "    pass",
            ]
        )


def analyze_and_suggest(user_code: str) -> Dict[str, Any]:
    """High level helper used in integration tests.

    The function orchestrates ingesting ``user_code`` with
    :class:`intuitive_aptitude` and returns a dictionary containing metrics,
    structural information, and a handful of heuristic suggestions.
    """

    analyzer = intuitive_aptitude()
    ok = analyzer.ingest(user_code)
    result: Dict[str, Any] = {
        "success": ok,
        "error": analyzer.last_error,
        "summary": analyzer.get_summary() if ok else {},
        "patterns": analyzer.extract_patterns() if ok else {},
        "style": analyzer.analyze_code_style() if ok else {},
        "structure": analyzer.get_detailed_structure() if ok else {},
        "suggestions": {},
    }
    if not ok:
        return result

    suggestions: Dict[str, Any] = {}
    naming = result["style"].get("naming", {})
    if naming.get("other", 0) > 0:
        suggestions["naming_conventions"] = (
            "Consider standardizing to snake_case for functions/variables and PascalCase for classes."
        )

    docstyles = result["style"].get("docstrings", {})
    if docstyles.get("None", 0) > 0:
        suggestions["docstrings"] = (
            "Add docstrings to undocumented objects. Prefer Google or NumPy style for consistency."
        )

    indent = result["style"].get("indentation", {})
    if indent.get("tabs", 0) > 0 and indent.get("4space", 0) > 0:
        suggestions["indentation"] = (
            "Mixed tabs and 4-space indentation detected. Standardize indentation to 4 spaces."
        )

    complexity = result["summary"]["metrics"]["complexity"]
    if complexity and complexity > 10:
        suggestions["complexity"] = (
            f"Average cyclomatic complexity is high ({complexity}). "
            "Consider refactoring large functions or splitting logic."
        )

    result["suggestions"] = suggestions
    return result
