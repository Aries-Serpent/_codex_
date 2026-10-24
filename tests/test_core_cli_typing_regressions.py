"""Focused offline regressions for the core CLI typing implementation lane."""

from __future__ import annotations

import builtins
import importlib.util
import json
import socket
import sys
from pathlib import Path
from unittest.mock import Mock, create_autospec

import pytest
from typer.testing import CliRunner

from aries_serpent_core import cli_rag, cli_zendesk, rag
from aries_serpent_core.ast_adapters.python_adapter import PythonASTAdapter
from aries_serpent_core.governance import approval_service
from aries_serpent_core.rag.benchmarks import BenchmarkResult, BenchmarkRunner
from aries_serpent_core.rag.retriever import Retriever
from aries_serpent_core.utils import config_loader


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail instead of contacting any remote boundary from these regressions."""

    def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("A focused core CLI regression attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@pytest.mark.parametrize("resource", sorted(cli_zendesk._RESOURCE_CONFIG))
def test_zendesk_registered_diffs_accept_empty_model_inputs(resource: str) -> None:
    """Every registry entry uses the shared diff API without an adapter shim."""
    _, diff = cli_zendesk._RESOURCE_CONFIG[resource]
    assert diff([], []) == []


def test_zendesk_trigger_diff_accepts_models_and_mappings(
    tmp_path: Path,
) -> None:
    """The public diff command still serializes changes from validated models."""
    model, diff = cli_zendesk._RESOURCE_CONFIG["triggers"]
    desired = model.model_validate({"name": "Notify", "category": "notifications"})
    actual = {"name": "Notify", "category": "old"}
    patches = diff([desired], [actual])
    assert patches
    desired_file = tmp_path / "desired.json"
    current_file = tmp_path / "current.json"
    output = tmp_path / "diff.json"
    desired_file.write_text(json.dumps([desired.model_dump(mode="json")]))
    current_file.write_text(json.dumps([actual]))
    cli_zendesk.diff("triggers", desired_file, current_file, output)
    assert json.loads(output.read_text()) == {"triggers": patches}


@pytest.mark.parametrize("approvers", [[], ["reviewer"], ["one", "two", "owner"]])
def test_approval_submission_cancellation_and_audit_copy(
    approvers: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Actor-less operations retain cancellation and shallow-copy semantics."""
    service = approval_service.ApprovalService()
    service.register_sla_policy(approval_service.SLAPolicy(policy_code="TEST"))
    engine = Mock()
    monkeypatch.setattr(approval_service, "get_default_engine", engine, raising=False)
    request = service.submit_request("TEST", "requester", approvers)
    assert request.escalation_chain == [1, 2, 3]
    assert request.current_approver_id == (approvers[0] if approvers else "")
    assert request.status == approval_service.ApprovalState.PENDING
    cancelled = service.cancel_request(request.request_id, "No longer needed")
    assert cancelled.status == approval_service.ApprovalState.CANCELLED
    events = service.get_audit_log(request.request_id)
    assert events[-1]["audit_code"] == approval_service.AuditCode.WORKFLOW_CANCELLED.value
    assert events[-1]["message"] == "No longer needed"
    assert events is not request.audit_log
    assert events[0] is request.audit_log[0]
    events.clear()
    assert len(request.audit_log) == 2
    engine.assert_not_called()


def test_approval_unknown_actorless_requests_still_raise() -> None:
    """Missing request IDs do not create cancellation or audit placeholders."""
    service = approval_service.ApprovalService()
    with pytest.raises(KeyError, match="missing"):
        service.cancel_request("missing")
    with pytest.raises(KeyError, match="missing"):
        service.get_audit_log("missing")


def test_python_adapter_wildcard_aliases_and_heterogeneous_metadata() -> None:
    """Valid wildcard imports and mixed metadata survive concrete CST parsing."""
    adapter = PythonASTAdapter()
    adapter.parse(
        "import package.module as local\n"
        "from package.module import value as alias\n"
        "from package.module import *\n"
        "@decorate\n"
        "class Child(Parent):\n"
        '    """Class docs."""\n'
        "    @decorate\n"
        '    def method(self, value: str = "x") -> str:\n'
        '        """Method docs."""\n'
        "        return value\n"
    )
    imported = adapter.find_nodes_by_type("import")
    from_imports = adapter.find_nodes_by_type("import_from")
    assert imported[0].metadata["alias"] == "local"
    assert [(node.name, node.metadata["alias"]) for node in from_imports] == [
        ("package.module.value", "alias"),
        ("package.module.*", None),
    ]
    cls = adapter.find_nodes_by_type("class")[0]
    method = adapter.find_nodes_by_type("function")[0]
    assert cls.metadata["decorators"] == ["decorate"]
    assert cls.metadata["bases"] == ["Parent"]
    assert cls.metadata["docstring"] == "Class docs."
    assert method.metadata["docstring"] == "Method docs."
    assert method.metadata["parameters"][1]["name"] == "value"
    assert "return_type" in method.metadata


def test_python_adapter_requires_unavailable_libcst(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable libcst still raises the documented installation error."""
    original_import = builtins.__import__

    def without_libcst(name: str, globals=None, locals=None, fromlist=(), level: int = 0):
        if name == "libcst":
            raise ImportError("libcst deliberately unavailable for regression")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", without_libcst)
    spec = importlib.util.spec_from_file_location(
        "aries_serpent_core.ast_adapters._without_libcst",
        sys.modules[PythonASTAdapter.__module__].__file__,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    with pytest.raises(ImportError, match="libcst is required for PythonASTAdapter"):
        module.PythonASTAdapter()


def test_rag_query_uses_retriever_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI query text reaches the real retriever's q parameter."""
    retriever = create_autospec(Retriever, instance=True)
    retriever.query.return_value = []
    factory = Mock(return_value=retriever)
    monkeypatch.setattr(cli_rag, "RAGRetriever", factory)
    result = CliRunner().invoke(
        cli_rag.app, ["query", "needle", "--top-k", "3", "--min-score", "0.4"]
    )
    assert result.exit_code == 0, result.output
    retriever.query.assert_called_once_with(q="needle", top_k=3, min_score=0.4)
    factory.assert_called_once_with(index_name="default", tenant_id="default")


def test_rag_build_uses_existing_package_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Build retains the package-export patch boundary and existing parameters."""
    document = tmp_path / "document.txt"
    document.write_text("offline indexing fixture")
    build = Mock(return_value=tmp_path / "index")
    monkeypatch.setattr(rag, "build_index_from_files", build)
    result = CliRunner().invoke(
        cli_rag.app, ["build", "--files", str(document), "--index-name", "docs"]
    )
    assert result.exit_code == 0, result.output
    build.assert_called_once_with(
        files=[document], index_name="docs", tenant_id="default", chunk_size=1000, overlap=128
    )


def test_rag_merge_and_metrics_use_existing_package_exports(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tenant merging and metrics reuse their real exported APIs, without I/O."""
    merge = Mock(
        return_value=rag.TenantOperationResult(
            success=True,
            operation=rag.IndexOperation.MERGE,
            tenant_id="default",
            index_names=["one", "two"],
            message="Merged",
        )
    )
    metrics = Mock()
    metrics.get_statistics.return_value = {"queries": 7}
    get_metrics = Mock(return_value=metrics)
    monkeypatch.setattr(rag, "manage_tenant_indices", merge)
    monkeypatch.setattr(rag, "get_metrics", get_metrics)
    merged = CliRunner().invoke(
        cli_rag.app, ["merge", "--source", "one", "--source", "two", "--target", "all"]
    )
    assert merged.exit_code == 0, merged.output
    merge.assert_called_once_with(
        tenant_id="default",
        operation=rag.IndexOperation.MERGE,
        index_names=["one", "two"],
        merge_name="all",
    )
    exported = CliRunner().invoke(cli_rag.app, ["metrics", "--format", "json"])
    assert exported.exit_code == 0, exported.output
    assert '"queries": 7' in exported.output
    get_metrics.assert_called_once_with()


def test_benchmark_result_round_trips_real_schema() -> None:
    """Baseline comparisons receive dataclass instances, including optional fields."""
    row = BenchmarkResult(
        name="example",
        duration_ms=10,
        memory_mb=2,
        success=False,
        error="offline failure",
        metadata={"runs": 1},
    )
    rebuilt = cli_rag._benchmark_result(row.to_dict())
    assert isinstance(rebuilt, BenchmarkResult)
    assert rebuilt.to_dict() == row.to_dict()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", 1),
        ("duration_ms", "10"),
        ("duration_ms", True),
        ("memory_mb", None),
        ("success", "false"),
        ("error", []),
        ("metadata", []),
        ("metadata", {1: "not a string key"}),
    ],
)
def test_benchmark_result_rejects_malformed_fields(field: str, value: object) -> None:
    """Malformed serialized rows fail explicitly rather than becoming fake classes."""
    data: dict[str, object] = {
        "name": "example",
        "duration_ms": 10,
        "memory_mb": 2,
        "success": True,
    }
    data[field] = value
    with pytest.raises(TypeError):
        cli_rag._benchmark_result(data)


@pytest.mark.parametrize(("duration", "expected_exit"), [(10.0, 0), (20.0, 1)])
def test_benchmark_cli_compares_real_results(
    duration: float, expected_exit: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Actual baseline comparison preserves success and regression exit codes."""
    from aries_serpent_core.rag import benchmarks

    row = BenchmarkResult(name="example", duration_ms=duration, memory_mb=2, success=True)
    monkeypatch.setattr(
        benchmarks,
        "benchmark_embedding_providers",
        Mock(return_value={"results": [row.to_dict()]}),
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "name": "example",
                        "duration_ms": 10,
                        "memory_mb": 2,
                    }
                ]
            }
        )
    )
    original_compare = BenchmarkRunner.compare_with_baseline
    compared: list[BenchmarkResult] = []

    def compare(
        self: BenchmarkRunner, baseline_file: str, threshold_percent: float = 10.0
    ) -> dict[str, object]:
        assert all(isinstance(item, BenchmarkResult) for item in self.results)
        compared.extend(self.results)
        return original_compare(self, baseline_file, threshold_percent)

    monkeypatch.setattr(BenchmarkRunner, "compare_with_baseline", compare)
    result = CliRunner().invoke(
        cli_rag.app, ["benchmark", "--type", "embedding", "--baseline", str(baseline)]
    )
    assert result.exit_code == expected_exit, result.output
    assert compared == [row]


def test_config_loader_hydra_compose_and_overrides(tmp_path: Path) -> None:
    """Available Hydra still composes configuration with the public override syntax."""
    conf = tmp_path / "conf"
    conf.mkdir()
    (conf / "app.yaml").write_text("app:\n  name: original\n")
    result = config_loader.ConfigLoader(tmp_path).load_config(
        "app", overrides=["app.name=changed"], allow_fallback=False
    )
    assert result["app"]["name"] == "changed"


def test_config_loader_without_hydra_preserves_yaml_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A genuinely unavailable optional Hydra import keeps YAML and missing-file behavior."""
    original_import = builtins.__import__

    def without_hydra(name: str, globals=None, locals=None, fromlist=(), level: int = 0):
        if name == "hydra" or name.startswith(("hydra.", "config_legacy")):
            raise ImportError("Hydra deliberately unavailable for regression")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", without_hydra)
    spec = importlib.util.spec_from_file_location(
        "_core_cli_config_without_hydra", config_loader.__file__
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    assert module.compose is None
    assert module.initialize_config_dir is None
    assert module.HydraMissingConfigException is FileNotFoundError
    conf = tmp_path / "conf"
    conf.mkdir()
    (conf / "app.yaml").write_text("app:\n  name: original\n")
    loader = module.ConfigLoader(tmp_path)
    result = loader.load_config("app", overrides=["app.name=changed"], allow_fallback=False)
    assert result["app"]["name"] == "changed"
    with pytest.raises(module.MissingConfigException) as missing:
        loader.load_config("absent", allow_fallback=False)
    assert missing.value.missing_cfg_file == str(conf / "absent.yaml")
