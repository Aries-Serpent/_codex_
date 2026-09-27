"""Dependency-direction checks for independently published packages."""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
STANDALONE_SOURCES = REPOSITORY_ROOT / "packages"
MONOLITH_PACKAGES = {"aries_serpent_core", "codex", "codex_ml", "cognitive_brain"}
PUBLIC_API_SNAPSHOTS = {
    "cognitive_sdk": (
        "codex_cognitive_sdk",
        {
            "ActionResult",
            "Decision",
            "GovernanceDecision",
            "GovernanceProtocol",
            "GovernanceRequest",
            "MemoryProtocol",
            "MemoryQuery",
            "MemoryRecord",
            "Observation",
            "OODACycle",
            "OODAProtocol",
            "Orientation",
            "__version__",
        },
    ),
    "contracts": (
        "codex_contracts",
        {
            "ArtifactReference",
            "CodexPlugin",
            "ContractValidationError",
            "ErrorEnvelope",
            "EventEnvelope",
            "__version__",
        },
    ),
    "evaluation": (
        "codex_evaluation",
        {
            "CodexMetricAdapter",
            "DatasetLoader",
            "DistributionValue",
            "DriftBatch",
            "DriftEvaluator",
            "DriftReport",
            "EvaluateMetricAdapter",
            "EvaluationBatch",
            "EvaluationError",
            "EvaluationReport",
            "EvaluationRunner",
            "Evaluator",
            "FrameworkMetricLoader",
            "HuggingFaceDatasetAdapter",
            "KullbackLeiblerDivergence",
            "Metric",
            "MetricInput",
            "MetricLoader",
            "MetricRegistrationError",
            "MetricRegistry",
            "OptionalDependencyError",
            "PopulationStabilityIndex",
            "__version__",
        },
    ),
    "lora": (
        "codex_lora",
        {
            "CodexMlLoraAdapter",
            "LoraArtifact",
            "LoraArtifactMetadata",
            "LoraBackend",
            "LoraConfig",
            "LoraLifecycleBackend",
            "LoraTrainingBackend",
            "OptionalDependencyError",
            "PeftBackend",
            "__version__",
            "activate_lora",
            "apply_lora",
            "delete_lora",
            "disable_lora",
            "load_lora",
            "prepare_lora_training",
            "read_lora_artifact",
            "save_lora",
        },
    ),
    "telemetry": (
        "codex_ml_telemetry",
        {
            "EXAMPLES_PROCESSED",
            "REQUEST_LATENCY",
            "TRAIN_STEP_DURATION",
            "HealthReport",
            "HealthStatus",
            "MetricsRegistry",
            "__version__",
            "render_prometheus",
            "start_metrics_server",
            "track_time",
        },
    ),
}
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
NESTED_DOMAIN_ALIASES = {
    "models.utils.peft": "lora",
    "utils.checkpoint": "checkpointing",
    "utils.checkpoint_core": "checkpointing",
    "utils.checkpointing": "checkpointing",
}
ALLOWED_DOMAIN_EDGES = {
    ("evaluation", "configuration"),
    ("evaluation", "logging"),
    ("evaluation", "metrics"),
    ("evaluation", "training"),
    ("training", "configuration"),
    ("training", "checkpointing"),
    ("training", "logging"),
    ("training", "lora"),
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


def _importing_package(path: Path, source_root: Path) -> str:
    relative = path.relative_to(source_root)
    package_parts = list(relative.parent.parts)
    return ".".join(("codex_ml", *package_parts))


def _codex_ml_imports(path: Path, source_root: Path | None = None) -> set[str]:
    source_root = source_root or REPOSITORY_ROOT / "src" / "codex_ml"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                relative_name = "." * node.level + (node.module or "")
                base = importlib.util.resolve_name(
                    relative_name, _importing_package(path, source_root)
                )
            else:
                base = node.module or ""
            names = (base, *(f"{base}.{alias.name}" for alias in node.names))
        else:
            continue
        for name in names:
            if name.startswith("codex_ml."):
                suffix = name.removeprefix("codex_ml.")
                if any(
                    suffix == prefix or suffix.startswith(f"{prefix}.")
                    for prefix in NESTED_DOMAIN_ALIASES
                ):
                    imported.add(suffix)
                else:
                    imported.add(suffix.partition(".")[0])
    return imported


def _domain_alias(module: str) -> str | None:
    for prefix, domain in NESTED_DOMAIN_ALIASES.items():
        if module == prefix or module.startswith(f"{prefix}."):
            return domain
    return DOMAIN_ALIASES.get(module.partition(".")[0])


def _source_domain(path: Path) -> str | None:
    relative = path.relative_to(REPOSITORY_ROOT / "src" / "codex_ml")
    module = relative.with_suffix("").as_posix().replace("/", ".")
    if module.endswith(".__init__"):
        module = module.removesuffix(".__init__")
    return _domain_alias(module)


def _domain_edges() -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    source_root = REPOSITORY_ROOT / "src" / "codex_ml"
    for path in sorted(source_root.rglob("*.py")):
        source = _source_domain(path)
        if source is None:
            continue
        for imported in _codex_ml_imports(path):
            target = _domain_alias(imported)
            if target is not None and target != source:
                edges.add((source, target))
    return edges


def _standalone_package_roots() -> dict[str, str]:
    roots: dict[str, str] = {}
    for init_path in sorted(STANDALONE_SOURCES.glob("*/src/*/__init__.py")):
        package_dir = init_path.parents[2].name
        roots[package_dir] = init_path.parent.name
    return roots


def _standalone_edges() -> set[tuple[str, str]]:
    roots = _standalone_package_roots()
    owners = {import_name: package_dir for package_dir, import_name in roots.items()}
    edges: set[tuple[str, str]] = set()
    for package_dir in sorted(roots):
        source = STANDALONE_SOURCES / package_dir / "src"
        for path in sorted(source.rglob("*.py")):
            for imported in _top_level_imports(path):
                target = owners.get(imported)
                if target is not None and target != package_dir:
                    edges.add((package_dir, target))
    return edges


def _find_cycle(graph: dict[str, set[str]]) -> tuple[str, ...] | None:
    visited: set[str] = set()
    active: list[str] = []
    active_indexes: dict[str, int] = {}

    def visit(node: str) -> tuple[str, ...] | None:
        if node in active_indexes:
            start = active_indexes[node]
            return (*active[start:], node)
        if node in visited:
            return None
        active_indexes[node] = len(active)
        active.append(node)
        for target in sorted(graph.get(node, ())):
            cycle = visit(target)
            if cycle is not None:
                return cycle
        active.pop()
        active_indexes.pop(node)
        visited.add(node)
        return None

    for node in sorted(graph):
        cycle = visit(node)
        if cycle is not None:
            return cycle
    return None


def _dependency_graph(
    nodes: set[str], edges: set[tuple[str, str]]
) -> dict[str, set[str]]:
    graph = {node: set() for node in nodes}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set())
    return graph


def test_standalone_packages_do_not_import_monolith_packages() -> None:
    violations: list[str] = []
    for path in sorted(STANDALONE_SOURCES.glob("*/src/**/*.py")):
        forbidden = sorted(_top_level_imports(path) & MONOLITH_PACKAGES)
        if forbidden:
            relative = path.relative_to(REPOSITORY_ROOT)
            violations.append(f"{relative}: {', '.join(forbidden)}")

    assert not violations, "standalone package boundary violations:\n" + "\n".join(violations)


def test_all_standalone_packages_have_public_api_snapshots() -> None:
    assert _standalone_package_roots() == {
        package_dir: import_name
        for package_dir, (import_name, _) in PUBLIC_API_SNAPSHOTS.items()
    }


@pytest.mark.parametrize(
    ("package_dir", "import_name", "expected"),
    [
        (package_dir, import_name, expected)
        for package_dir, (import_name, expected) in PUBLIC_API_SNAPSHOTS.items()
    ],
)
def test_standalone_package_root_public_api_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    package_dir: str,
    import_name: str,
    expected: set[str],
) -> None:
    monkeypatch.syspath_prepend(str(STANDALONE_SOURCES / package_dir / "src"))
    module = importlib.import_module(import_name)

    assert set(module.__all__) == expected
    assert all(hasattr(module, name) for name in expected)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("from codex_ml import metrics\n", {"metrics"}),
        ("from .. import metrics\n", {"metrics"}),
        ("from ..metrics import accuracy\n", {"metrics"}),
        (
            "from codex_ml.models.utils.peft import apply_lora_if_available\n",
            {
                "models.utils.peft",
                "models.utils.peft.apply_lora_if_available",
            },
        ),
        (
            "from codex_ml.utils.checkpointing import save_checkpoint\n",
            {"utils.checkpointing", "utils.checkpointing.save_checkpoint"},
        ),
    ],
)
def test_codex_ml_import_detection_covers_supported_import_forms(
    tmp_path: Path, source: str, expected: set[str]
) -> None:
    source_root = tmp_path / "codex_ml"
    path = source_root / "training" / "module.py"
    path.parent.mkdir(parents=True)
    path.write_text(source, encoding="utf-8")

    assert _codex_ml_imports(path, source_root) == expected


def test_nested_compatibility_namespaces_have_domain_aliases() -> None:
    expected = {
        "models.utils.peft": "lora",
        "models.utils.peft.backend": "lora",
        "utils.checkpoint": "checkpointing",
        "utils.checkpoint_core": "checkpointing",
        "utils.checkpointing": "checkpointing",
    }
    assert {module: _domain_alias(module) for module in expected} == expected


def test_domain_dependencies_follow_the_allowed_dag() -> None:
    unexpected = sorted(_domain_edges() - ALLOWED_DOMAIN_EDGES)
    assert not unexpected, "unexpected codex_ml domain dependencies:\n" + "\n".join(
        f"{source} -> {target}" for source, target in unexpected
    )


def test_domain_dependency_graph_is_acyclic() -> None:
    graph = _dependency_graph(set(DOMAIN_ALIASES.values()), _domain_edges())
    cycle = _find_cycle(graph)
    assert cycle is None, "codex_ml domain dependency cycle: " + " -> ".join(cycle or ())


def test_standalone_package_dependency_graph_is_acyclic() -> None:
    edges = _standalone_edges()
    graph = _dependency_graph(set(_standalone_package_roots()), edges)
    cycle = _find_cycle(graph)
    assert cycle is None, "standalone package dependency cycle: " + " -> ".join(cycle or ())


def test_cycle_detection_reports_closed_deterministic_path() -> None:
    graph = {
        "consumer": {"evaluation"},
        "contracts": {"evaluation"},
        "evaluation": {"contracts"},
    }

    assert _find_cycle(graph) == ("evaluation", "contracts", "evaluation")
