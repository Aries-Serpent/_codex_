import ast
import sys
from pathlib import Path

def is_empty_func(node):
    # A function is considered empty if its body only contains 'pass', '...', or docstrings.
    for stmt in node.body:
        if isinstance(stmt, ast.Pass):
            continue
        elif isinstance(stmt, ast.Expr) and (
            isinstance(stmt.value, ast.Constant) and (
                stmt.value.value is Ellipsis or isinstance(stmt.value.value, str)
            )
        ):
            continue
        else:
            return False
    return True

for p in Path("src").rglob("*.py"):
    try:
        content = p.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                if is_empty_func(node):
                    # check if it has @abstractmethod
                    is_abstract = False
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "abstractmethod":
                            is_abstract = True
                        elif isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod":
                            is_abstract = True
                    if not is_abstract:
                        print(f"{p}:{node.lineno} {node.name}")
    except Exception as e:
        print(f"Warning: failed to scan {p}: {e}", file=sys.stderr)
