"""Dependency-direction checks for independently published packages."""

from __future__ import annotations

import ast
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
STANDALONE_SOURCES = REPOSITORY_ROOT / "packages"
MONOLITH_PACKAGES = {"aries_serpent_core", "codex", "codex_ml", "cognitive_brain"}
DOMAIN_ALIASES = {
    "checkpointing": "checkpointing",
    "config": "configuration",
    "config_schema": "configuration",
    "configs": "configuration",
    "codex_structured_logging": "logging",
    "eval": "evaluation",
    "evaluation": "evaluation",
    "logging": "logging",
    "metrics": "metrics",
    "monitoring": "monitoring",
    "peft": "lora",
    "telemetry": "telemetry",
    "training": "training",
    "train_loop": "training",
}
ALLOWED_DOMAIN_EDGES = {
    ("evaluation", "configuration"),
    ("evaluation", "logging"),
    ("evaluation", "metrics"),
    ("evaluation", "training"),
    ("training", "configuration"),
    ("training", "logging"),
    ("training", "metrics"),
    ("training", "monitoring"),
    ("training", "telemetry"),
}


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.partition(".")[0])
    return imported


def _codex_ml_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = (node.module,)
        else:
            continue
        for name in names:
            if name.startswith("codex_ml."):
                imported.add(name.split(".", 2)[1])
    return imported


def _source_domain(path: Path) -> str | None:
    relative = path.relative_to(REPOSITORY_ROOT / "src" / "codex_ml")
    component = relative.parts[0]
    if component.endswith(".py"):
        component = component.removesuffix(".py")
    return DOMAIN_ALIASES.get(component)


def _domain_edges() -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    source_root = REPOSITORY_ROOT / "src" / "codex_ml"
    for path in sorted(source_root.rglob("*.py")):
        source = _source_domain(path)
        if source is None:
            continue
        for imported in _codex_ml_imports(path):
            target = DOMAIN_ALIASES.get(imported)
            if target is not None and target != source:
                edges.add((source, target))
    return edges


def test_standalone_packages_do_not_import_monolith_packages() -> None:
    violations: list[str] = []
    for path in sorted(STANDALONE_SOURCES.glob("*/src/**/*.py")):
        forbidden = sorted(_top_level_imports(path) & MONOLITH_PACKAGES)
        if forbidden:
            relative = path.relative_to(REPOSITORY_ROOT)
            violations.append(f"{relative}: {', '.join(forbidden)}")

    assert not violations, "standalone package boundary violations:\n" + "\n".join(violations)


def test_domain_dependencies_follow_the_allowed_dag() -> None:
    unexpected = sorted(_domain_edges() - ALLOWED_DOMAIN_EDGES)
    assert not unexpected, "unexpected codex_ml domain dependencies:\n" + "\n".join(
        f"{source} -> {target}" for source, target in unexpected
    )


def test_domain_dependency_graph_is_acyclic() -> None:
    graph: dict[str, set[str]] = {domain: set() for domain in set(DOMAIN_ALIASES.values())}
    for source, target in _domain_edges():
        graph[source].add(target)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(domain: str, path: tuple[str, ...]) -> None:
        if domain in visiting:
            cycle = " -> ".join((*path, domain))
            raise AssertionError(f"codex_ml domain dependency cycle: {cycle}")
        if domain in visited:
            return
        visiting.add(domain)
        for target in sorted(graph[domain]):
            visit(target, (*path, domain))
        visiting.remove(domain)
        visited.add(domain)

    for domain in sorted(graph):
        visit(domain, ())
