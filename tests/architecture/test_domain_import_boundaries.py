"""Enforce the production import policy for ML lifecycle domains.

The checks in this module deliberately use the standard-library AST rather
than importing production modules.  This keeps the architecture gate
deterministic and independent of optional runtime dependencies.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_CONFIG_ROOT_NAMES = ("conf", "config", "configs")

# Ordered from the most specific names to compatibility/legacy namespaces.
DOMAIN_PREFIXES: tuple[tuple[str, str], ...] = (
    ("codex_ml.models.utils.peft", "lora"),
    ("codex_ml_telemetry", "telemetry"),
    ("codex_evaluation", "evaluation"),
    ("codex_lora", "lora"),
    ("aries_serpent_core.monitoring", "monitoring"),
    ("aries_serpent_core.logging", "logging"),
    ("codex_ml.checkpointing", "checkpointing"),
    ("codex_ml.utils.checkpointing", "checkpointing"),
    ("codex_ml.utils.checkpoint_core", "checkpointing"),
    ("codex_ml.utils.checkpoint", "checkpointing"),
    ("utils.checkpointing", "checkpointing"),
    ("utils.checkpoint", "checkpointing"),
    ("codex_ml.evaluation", "evaluation"),
    ("codex_ml.eval", "evaluation"),
    ("codex_ml.metrics", "metrics"),
    ("codex_ml.peft", "lora"),
    ("codex_ml.telemetry", "telemetry"),
    ("codex_ml.monitoring", "monitoring"),
    ("codex_ml.logging", "logging"),
    ("codex_ml.codex_structured_logging", "logging"),
    ("codex.logging", "logging"),
    ("codex_ml.config_schema", "configuration"),
    ("codex_ml.config", "configuration"),
    ("codex_ml.training", "training"),
    ("codex_ml.train_loop", "training"),
    ("configs", "configuration"),
    ("config", "configuration"),
    ("conf", "configuration"),
    ("monitoring", "monitoring"),
    ("training", "training"),
)

# This is an acyclic dependency policy: orchestration points down toward
# contracts/configuration, never back up toward training.
ALLOWED_DOMAIN_EDGES: dict[str, frozenset[str]] = {
    "configuration": frozenset(),
    "logging": frozenset({"configuration"}),
    "metrics": frozenset({"configuration"}),
    "telemetry": frozenset({"metrics", "logging", "configuration"}),
    "monitoring": frozenset({"telemetry", "metrics", "logging", "configuration"}),
    "checkpointing": frozenset({"logging", "configuration"}),
    "lora": frozenset({"checkpointing", "configuration"}),
    "evaluation": frozenset(
        {"metrics", "telemetry", "logging", "configuration", "checkpointing"}
    ),
    "training": frozenset(
        {
            "evaluation",
            "lora",
            "checkpointing",
            "monitoring",
            "telemetry",
            "metrics",
            "logging",
            "configuration",
        }
    ),
}

# Compatibility debt is recorded by exact importer and imported module.  New
# importers, targets, or directions still fail the gate.
DOMAIN_EDGE_BASELINE: frozenset[tuple[str, str]] = frozenset(
    {
        ("codex_ml.evaluation.loop", "codex_ml.training.engine"),
        ("codex_ml.peft.peft_adapter", "codex.logging.adapter"),
        ("utils.checkpoint", "training.checkpoint_manager"),
    }
)

STATIC_SCC_BASELINE: frozenset[frozenset[str]] = frozenset(
    {
        frozenset(
            {
                "aries_serpent_core.archive",
                "aries_serpent_core.archive.archive_database",
                "aries_serpent_core.archive.backend",
                "aries_serpent_core.archive.config",
                "aries_serpent_core.archive.logging_config",
                "aries_serpent_core.archive.service",
            }
        ),
        frozenset(
            {"codex_ml.utils", "codex_ml.utils.checkpointing", "codex_ml.utils.repro"}
        ),
        frozenset({"codex_ml.features", "codex_ml.features.monitoring"}),
        frozenset(
            {
                "codex_ml.interfaces.tokenizer",
                "codex_ml.interfaces.tokenizer_hf",
                "codex_ml.tokenization.hf_adapter",
            }
        ),
        frozenset({"codex_ml.tracking", "codex_ml.tracking.mlflow_utils"}),
        frozenset({"codex_ml.training", "codex_ml.training.unified_training"}),
        frozenset({"codex_ml.callbacks", "codex_ml.callbacks.system_metrics"}),
    }
)

FACADE_REVERSE_BASELINE: frozenset[tuple[str, str]] = frozenset(
    {
        (
            "aries_serpent_core.logging.conversation_logger",
            "aries_serpent_core.logging",
        ),
        ("aries_serpent_core.monitoring.otel_metrics", "aries_serpent_core.monitoring"),
        ("codex_ml.callbacks.system_metrics", "codex_ml.callbacks"),
        ("codex_ml.training.unified_training", "codex_ml.training"),
        ("codex_ml.utils.checkpointing", "codex_ml.utils"),
        ("codex_ml.utils.repro", "codex_ml.utils"),
    }
)

SYS_PATH_MUTATION_BASELINE: frozenset[tuple[str, str]] = frozenset(
    {
        ("src/aries_serpent_core/governance/approval_service.py", "insert"),
        ("src/cli.py", "append"),
        ("src/cli.py", "insert"),
        ("src/cli.py", "remove"),
        ("src/codex/__init__.py", "insert"),
        ("src/codex_ml/evaluation/metrics/accuracy.py", "insert"),
        ("src/codex_ml/evaluation/metrics/bleu.py", "insert"),
        ("src/codex_ml/evaluation/metrics/latency.py", "insert"),
        ("src/codex_ml/evaluation/metrics/perplexity.py", "insert"),
        ("src/codex_ml/evaluation/metrics/rouge.py", "insert"),
        ("src/codex_ml/plugins/plugin_registry.py", "insert"),
        ("src/codex_ml/plugins/registry.py", "insert"),
        ("src/codex_ml/training.py", "insert"),
        ("src/codex_ml/training.py", "remove"),
        ("src/common/validate.py", "insert"),
        ("src/common/validate.py", "remove"),
        ("src/services/crawler/zendesk_sync.py", "insert"),
        ("configs/sitecustomize.py", "insert"),
    }
)

PACKAGE_MODULE_COLLISION_BASELINE = frozenset(
    {
        "src/aries_serpent_core/cli",
        "src/aries_serpent_core/evidence",
        "src/cli",
        "src/codex/cli",
        "src/codex/ingest",
        "src/codex/transform",
        "src/codex_ml/data/loaders",
        "src/codex_ml/metrics",
        "src/codex_ml/registry",
        "src/codex_ml/training",
        "src/mcp/observability",
    }
)


@dataclass(frozen=True, order=True)
class ImportEdge:
    source: str
    target: str
    line: int
    phase: str


def _production_source_roots() -> tuple[Path, ...]:
    roots = [ROOT / "src", ROOT / "training", ROOT / "monitoring"]
    roots.extend(ROOT / name for name in EXECUTABLE_CONFIG_ROOT_NAMES)
    roots.extend(sorted((ROOT / "packages").glob("*/src")))
    return tuple(path for path in roots if path.is_dir())


def _module_name(path: Path, source_root: Path) -> str:
    relative = path.relative_to(source_root)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    if source_root.parent == ROOT and source_root.name in EXECUTABLE_CONFIG_ROOT_NAMES:
        parts.insert(0, source_root.name)
    return ".".join(parts)


def _production_modules() -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for source_root in _production_source_roots():
        for path in sorted(source_root.rglob("*.py")):
            module = _module_name(path, source_root)
            if module:
                modules.setdefault(module, path)
    return modules


def _is_type_checking_test(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Name)
        and node.id == "TYPE_CHECKING"
        or isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "typing"
        and node.attr == "TYPE_CHECKING"
    )


class _ImportVisitor(ast.NodeVisitor):
    def __init__(self, module: str, is_package: bool) -> None:
        self.module = module
        self.package = module if is_package else module.rpartition(".")[0]
        self.function_depth = 0
        self.type_checking_depth = 0
        self.edges: list[ImportEdge] = []

    @property
    def phase(self) -> str:
        if self.type_checking_depth:
            return "type_checking"
        return "deferred" if self.function_depth else "static"

    def _record(self, target: str, line: int) -> None:
        if target:
            self.edges.append(ImportEdge(self.module, target, line, self.phase))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record(alias.name, node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            package_parts = self.package.split(".") if self.package else []
            keep = len(package_parts) - (node.level - 1)
            prefix = package_parts[: max(keep, 0)]
            module_parts = node.module.split(".") if node.module else []
            base = ".".join((*prefix, *module_parts))
        else:
            base = node.module or ""
        self._record(base, node.lineno)
        for alias in node.names:
            if alias.name != "*":
                self._record(".".join(part for part in (base, alias.name) if part), node.lineno)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        guarded = _is_type_checking_test(node.test)
        if guarded:
            self.type_checking_depth += 1
        for child in node.body:
            self.visit(child)
        if guarded:
            self.type_checking_depth -= 1
        for child in node.orelse:
            self.visit(child)


def _all_imports(modules: dict[str, Path]) -> list[ImportEdge]:
    edges: list[ImportEdge] = []
    for module, path in sorted(modules.items()):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        visitor = _ImportVisitor(module, path.name == "__init__.py")
        visitor.visit(tree)
        edges.extend(visitor.edges)
    return edges


def _local_targets(target: str, modules: dict[str, Path]) -> set[str]:
    resolved: set[str] = set()
    candidate = target
    while candidate:
        if candidate in modules:
            resolved.add(candidate)
            break
        candidate = candidate.rpartition(".")[0]
    if target in modules:
        resolved.add(target)
    return resolved


def _domain(module: str) -> str | None:
    for prefix, domain in DOMAIN_PREFIXES:
        if module == prefix or module.startswith(f"{prefix}."):
            return domain
    return None


def _static_graph(modules: dict[str, Path], imports: list[ImportEdge]) -> dict[str, set[str]]:
    graph = {module: set() for module in modules}
    for edge in imports:
        if edge.phase != "static" or edge.source not in graph:
            continue
        graph[edge.source].update(
            target
            for target in _local_targets(edge.target, modules)
            if target != edge.source
        )
    return graph


def _strongly_connected_components(graph: dict[str, set[str]]) -> set[frozenset[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: set[frozenset[str]] = set()

    def visit(node: str) -> None:
        nonlocal index
        indexes[node] = lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph.get(node, ()):
            if target not in indexes:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[target])
        if lowlinks[node] == indexes[node]:
            component: set[str] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            if len(component) > 1 or node in graph.get(node, set()):
                components.add(frozenset(component))

    for node in sorted(graph):
        if node not in indexes:
            visit(node)
    return components


def _format_items(items: object) -> str:
    if isinstance(items, (set, frozenset)):
        ordered = sorted(items, key=repr)
    else:
        ordered = items
    return "\n".join(f"  - {item!r}" for item in ordered)


def test_no_new_or_expanded_static_import_cycles() -> None:
    """Existing static SCC debt may shrink, but cannot grow or expand."""
    modules = _production_modules()
    actual = _strongly_connected_components(_static_graph(modules, _all_imports(modules)))
    assert actual <= STATIC_SCC_BASELINE, (
        "New or expanded static import SCCs detected:\n"
        f"{_format_items(actual - STATIC_SCC_BASELINE)}"
    )


def test_imports_follow_domain_direction() -> None:
    """Cross-domain runtime imports must follow the acyclic policy."""
    modules = _production_modules()
    violations: set[tuple[str, str]] = set()
    details: dict[tuple[str, str], list[str]] = defaultdict(list)
    for edge in _all_imports(modules):
        if edge.phase == "type_checking":
            continue
        source_domain = _domain(edge.source)
        for target in _local_targets(edge.target, modules):
            target_domain = _domain(target)
            if (
                source_domain
                and target_domain
                and source_domain != target_domain
                and target_domain not in ALLOWED_DOMAIN_EDGES[source_domain]
            ):
                key = (edge.source, target)
                violations.add(key)
                details[key].append(f"{modules[edge.source].relative_to(ROOT)}:{edge.line}")
    unexpected = violations - DOMAIN_EDGE_BASELINE
    assert not unexpected, "Forbidden production domain imports:\n" + "\n".join(
        f"  - {source} -> {target} at {', '.join(details[(source, target)])}"
        for source, target in sorted(unexpected)
    )


def test_compatibility_namespaces_are_classified() -> None:
    """Nested PEFT and checkpoint compatibility modules retain their domains."""
    expected = {
        "codex_ml.models.utils.peft": "lora",
        "codex_ml.models.utils.peft.backend": "lora",
        "codex_ml.utils.checkpoint": "checkpointing",
        "codex_ml.utils.checkpoint_core": "checkpointing",
        "codex_ml.utils.checkpointing": "checkpointing",
        "utils.checkpoint": "checkpointing",
        "utils.checkpointing": "checkpointing",
    }
    assert {module: _domain(module) for module in expected} == expected


def test_executable_configuration_roots_are_scanned() -> None:
    """Python files in repository configuration roots are production inputs."""
    modules = _production_modules()
    expected = {
        path.relative_to(ROOT).as_posix()
        for root_name in EXECUTABLE_CONFIG_ROOT_NAMES
        for path in (ROOT / root_name).rglob("*.py")
        if (ROOT / root_name).is_dir()
    }
    actual = {
        path.relative_to(ROOT).as_posix()
        for module, path in modules.items()
        if _domain(module) == "configuration"
    }
    assert expected <= actual


def test_evaluation_does_not_gain_concrete_training_imports() -> None:
    """Evaluation must depend on protocols, not training implementations."""
    modules = _production_modules()
    violations = set()
    for edge in _all_imports(modules):
        if edge.phase == "type_checking" or _domain(edge.source) != "evaluation":
            continue
        violations.update(
            (edge.source, target)
            for target in _local_targets(edge.target, modules)
            if _domain(target) == "training"
        )
    baseline = {
        edge for edge in DOMAIN_EDGE_BASELINE if _domain(edge[0]) == "evaluation"
    }
    assert violations <= baseline, (
        "Evaluation imports concrete training code:\n"
        f"{_format_items(violations - baseline)}"
    )


def test_leaf_modules_do_not_gain_facade_reverse_imports() -> None:
    """A package implementation must not import its own ``__init__`` facade."""
    modules = _production_modules()
    violations: set[tuple[str, str]] = set()
    for edge in _all_imports(modules):
        if (
            edge.phase == "type_checking"
            or "." not in edge.source
            or (
                _domain(edge.source) is None
                and not edge.source.startswith(("codex_ml.callbacks", "codex_ml.utils"))
            )
        ):
            continue
        parent = edge.source.rpartition(".")[0]
        if edge.target == parent and modules.get(parent, Path()).name == "__init__.py":
            violations.add((edge.source, edge.target))
    assert violations <= FACADE_REVERSE_BASELINE, (
        "New facade reverse imports detected:\n"
        f"{_format_items(violations - FACADE_REVERSE_BASELINE)}"
    )


def _sys_path_mutations(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    operations: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if (
                isinstance(owner, ast.Attribute)
                and isinstance(owner.value, ast.Name)
                and owner.value.id == "sys"
                and owner.attr == "path"
                and node.func.attr in {"append", "extend", "insert", "remove"}
            ):
                operations.add(node.func.attr)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "sys"
                    and target.attr == "path"
                ):
                    operations.add("assign")
    return operations


def test_production_code_does_not_gain_sys_path_mutation() -> None:
    """Production import resolution must not be altered at runtime."""
    actual: set[tuple[str, str]] = set()
    for source_root in _production_source_roots():
        for path in sorted(source_root.rglob("*.py")):
            relative = path.relative_to(ROOT).as_posix()
            actual.update((relative, operation) for operation in _sys_path_mutations(path))
    assert actual <= SYS_PATH_MUTATION_BASELINE, (
        "New production sys.path mutations detected:\n"
        f"{_format_items(actual - SYS_PATH_MUTATION_BASELINE)}"
    )


def test_no_new_package_module_name_collisions() -> None:
    """A source root cannot define both ``name.py`` and ``name/__init__.py``."""
    actual: set[str] = set()
    for source_root in _production_source_roots():
        for module_file in sorted(source_root.rglob("*.py")):
            if module_file.name == "__init__.py":
                continue
            package_init = module_file.with_suffix("") / "__init__.py"
            if package_init.is_file():
                actual.add(module_file.with_suffix("").relative_to(ROOT).as_posix())
    assert actual <= PACKAGE_MODULE_COLLISION_BASELINE, (
        "New package/module name collisions detected:\n"
        f"{_format_items(actual - PACKAGE_MODULE_COLLISION_BASELINE)}"
    )
