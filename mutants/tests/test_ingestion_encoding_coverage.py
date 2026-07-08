"""Verify ingestion text readers expose an ``encoding`` parameter."""

import ast
from pathlib import Path

READ_ATTRS = {("Path", "read_text"), ("", "read_text")}
PANDAS_FUNCS = {"read_csv", "read_table", "read_json"}


def _calls_text_readers(fn_node: ast.FunctionDef) -> bool:
    class Finder(ast.NodeVisitor):
        def __init__(self):
            self.uses_text_reader = False

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "read_text":
                self.uses_text_reader = True
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if (
                    len(node.args) >= 2
                    and isinstance(node.args[1], ast.Constant)
                    and isinstance(node.args[1].value, str)
                ):
                    if "b" not in node.args[1].value:
                        self.uses_text_reader = True
                else:
                    self.uses_text_reader = True
            if isinstance(node.func, ast.Attribute) and node.func.attr in PANDAS_FUNCS:
                self.uses_text_reader = True
            return self.generic_visit(node)

    f = Finder()
    f.visit(fn_node)
    return f.uses_text_reader


def _has_encoding_param(fn_node: ast.FunctionDef) -> bool:
    for arg in list(fn_node.args.args) + list(fn_node.args.kwonlyargs):
        if arg.arg == "encoding":
            return True
    return bool(fn_node.args.kwarg and fn_node.args.kwarg.arg)


def test_all_text_readers_accept_encoding():
    root = Path(__file__).resolve().parents[1] / "src" / "ingestion"
    if not root.exists():
        return
    offenders = []
    for py in root.rglob("*.py"):
        mod = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
        for n in mod.body:
            if isinstance(n, ast.FunctionDef):
                if _calls_text_readers(n) and not _has_encoding_param(n):
                    offenders.append(f"{py}:{n.name}")
    assert not offenders, "Functions missing `encoding` param:\n" + "\n".join(offenders)
