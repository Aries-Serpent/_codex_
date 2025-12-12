"""Inspect import graphs to estimate coupling energy.

The script gathers import statements from Python files and reports simple
in/out degree metrics that approximate coupling energy (in_degree * out_degree)
per module. Lower scores generally indicate healthier boundaries.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

TARGET_ROOT = Path(__file__).resolve().parent.parent / "src"


@dataclass
class ModuleCoupling:
    module: str
    in_degree: int
    out_degree: int

    @property
    def coupling_energy(self) -> int:
        return self.in_degree * self.out_degree


def discover_python_files(base_dir: Path) -> Iterable[Path]:
    for path in base_dir.rglob("*.py"):
        if path.is_file():
            yield path


def module_name_from_path(path: Path, base_dir: Path) -> str:
    relative = path.relative_to(base_dir)
    return ".".join(relative.with_suffix("").parts)


def parse_imports(path: Path) -> List[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []

    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return imports


def analyze_coupling(base_dir: Path) -> List[ModuleCoupling]:
    inbound: Dict[str, set[str]] = defaultdict(set)
    outbound: Dict[str, set[str]] = defaultdict(set)

    for path in discover_python_files(base_dir):
        module_name = module_name_from_path(path, base_dir)
        imports = parse_imports(path)
        outbound[module_name].update(imports)
        for dependency in imports:
            inbound[dependency].add(module_name)

    modules = set(outbound) | set(inbound)
    results: List[ModuleCoupling] = []
    for module in sorted(modules):
        results.append(
            ModuleCoupling(
                module=module,
                in_degree=len(inbound.get(module, set())),
                out_degree=len(outbound.get(module, set())),
            )
        )
    return sorted(results, key=lambda item: item.coupling_energy, reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze import coupling")
    parser.add_argument(
        "base_dir",
        nargs="?",
        type=Path,
        default=TARGET_ROOT,
        help="Base source directory to analyze",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of modules to display",
    )
    args = parser.parse_args()

    results = analyze_coupling(args.base_dir)
    print(f"Analyzed {len(results)} modules under {args.base_dir}.")
    print(f"Top {args.limit} modules by coupling energy:")
    for item in results[: args.limit]:
        print(
            f"{item.module}: in={item.in_degree}, out={item.out_degree}, "
            f"energy={item.coupling_energy}"
        )


if __name__ == "__main__":
    main()
