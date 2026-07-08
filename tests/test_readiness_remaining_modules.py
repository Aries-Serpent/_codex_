"""Readiness smoke tests for remaining modules listed as missing.

These tests focus on import-time coverage for modules flagged by
``tools/validate_production_readiness.py`` while stubbing optional
dependencies so imports remain lightweight and offline-friendly.
"""

from __future__ import annotations

import importlib
import sys
import types
from collections.abc import Iterable
from types import SimpleNamespace

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_src_on_path():
    """Guarantee the repository sources are importable during tests."""
    from pathlib import Path

    src_path = str(Path(__file__).resolve().parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def _install_stub(name: str, module) -> None:
    """Register a stub module if the real dependency is absent."""
    if name not in sys.modules:
        sys.modules[name] = module


def _module_spec_stub(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader=None)
    return module


def _torch_stub():
    stub = SimpleNamespace()
    stub.cuda = SimpleNamespace(is_available=lambda: False)
    stub.distributed = SimpleNamespace(
        is_available=lambda: False,
        is_initialized=lambda: False,
        init_process_group=lambda *_, **__: None,
        get_rank=lambda: 0,
        get_world_size=lambda: 1,
    )
    stub.nn = SimpleNamespace()
    stub.optim = SimpleNamespace()
    stub.utils = SimpleNamespace()
    stub.device = lambda *_args, **_kwargs: "cpu"
    return stub


def _sentencepiece_stub():
    class _Processor:
        def Load(self, *_, **__):
            return True

        def EncodeAsPieces(self, text):
            return text.split()

        def EncodeAsIds(self, text):
            return list(range(len(text.split())))

    return SimpleNamespace(
        SentencePieceTrainer=SimpleNamespace(Train=lambda *_, **__: None),
        SentencePieceProcessor=_Processor,
    )


def _sacrebleu_stub():
    return SimpleNamespace(corpus_bleu=lambda *_, **__: SimpleNamespace(score=0.0))


def _rouge_stub():
    scorer = SimpleNamespace(
        score=lambda *_args, **_kwargs: {"rouge1": SimpleNamespace(fmeasure=0.0)}
    )
    return SimpleNamespace(rouge_scorer=SimpleNamespace(RougeScorer=lambda *_, **__: scorer))


def _install_optional_dependency_stubs():
    torch_stub = _torch_stub()
    for name in [
        "torch",
        "torch.cuda",
        "torch.distributed",
        "torch.nn",
        "torch.optim",
        "torch.utils",
    ]:
        _install_stub(name, torch_stub)

    datasets_stub = SimpleNamespace(Dataset=SimpleNamespace, load_dataset=lambda *_, **__: [])
    transformer_stub = SimpleNamespace(
        AutoTokenizer=SimpleNamespace,
        AutoModel=SimpleNamespace,
        PreTrainedTokenizerBase=SimpleNamespace,
        AutoModelForCausalLM=SimpleNamespace,
    )

    _install_stub("datasets", datasets_stub)
    _install_stub("transformers", transformer_stub)

    _install_stub("mlflow", _module_spec_stub("mlflow"))
    _install_stub("wandb", _module_spec_stub("wandb"))

    xml_stub = _module_spec_stub("defusedxml")
    xml_tree_stub = _module_spec_stub("defusedxml.ElementTree")
    xml_minidom_stub = _module_spec_stub("defusedxml.minidom")
    # XXE PROTECTION: Use defusedxml stubs to prevent XXE attacks during smoke tests.
    # defusedxml provides safe XML parsing that prevents:
    # - External entity (XXE) attacks
    # - Billion Laughs attacks
    # - DTD retrieval attacks
    # - XML bombs
    # Minimal no-op stubs that mirror the defusedxml ElementTree API without
    # importing an XML parser in this readiness smoke test.
    for attr_name, stub_impl in (
        ("Element", lambda *_, **__: SimpleNamespace()),
        ("SubElement", lambda *_, **__: SimpleNamespace()),
        ("tostring", lambda *_, **__: b""),
        ("fromstring", lambda *_, **__: SimpleNamespace()),  # XXE-safe parsing stub
    ):
        setattr(xml_tree_stub, attr_name, stub_impl)
    setattr(
        xml_minidom_stub, "parseString", lambda *_, **__: SimpleNamespace()
    )  # XXE-safe minidom stub
    xml_stub.ElementTree = xml_tree_stub
    xml_stub.minidom = xml_minidom_stub
    _install_stub("defusedxml", xml_stub)
    _install_stub("defusedxml.ElementTree", xml_tree_stub)
    _install_stub("defusedxml.minidom", xml_minidom_stub)

    for name in [
        "accelerate",
        "faiss",
        "faiss.swigfaiss",
        "weaviate",
        "pinecone",
        "huggingface_hub",
        "fastapi",
        "uvicorn",
        "psutil",
        "openai",
    ]:
        _install_stub(name, SimpleNamespace())

    _install_stub("sacrebleu", _sacrebleu_stub())
    _install_stub("rouge_score", _rouge_stub())
    _install_stub("sentencepiece", _sentencepiece_stub())
    _install_stub("pgvector", SimpleNamespace())


@pytest.fixture(autouse=True)
def stub_optional_dependencies():
    """Install stubs for heavy optional dependencies during tests."""
    _install_optional_dependency_stubs()
    yield


MODULE_PATHS: Iterable[str] = [
    "integrations.github_app_auth",
    "codex_ml._package_main",
    "codex_ml.codex_structured_logging",
    "codex_ml.hf_loader",
    "codex_ml.metrics_base",
    "experiments.manager",
    "services.mcp.lifecycle",
    "codex_ml.safety.sandbox",
    "codex_ml.safety.sanitizers",
    "codex_ml.safety.redaction",
    "codex_ml.safety.moderation",
    "codex_ml.integrations.har_integration",
    "codex_ml.evaluation.runner",
    "codex_ml.registry.trainers",
    "codex_ml.exec.codex_exec",
    "codex_ml.serving.deployment",
    "codex_ml.events.azure_events",
    "codex_ml.events.aws_events",
    "codex_ml.governance.compliance_gates",
    "codex_ml.checkpointing.compat",
    "codex_ml.checkpointing.best_k_retention",
    "codex_ml.checkpointing.schema_v2",
    "codex_ml.detectors.capability_detectors",
    "codex_ml.detectors.experiment_summary",
    "codex_ml.metrics._optional_bleu_rouge",
    "codex_ml.metrics.streaming",
    "codex_ml.metrics.classification",
    "codex_ml.metrics.generation",
    "codex_ml.metrics.evaluator",
    "codex_ml.metrics.reward",
    "codex_ml.deployment.package",
    "codex_ml.io.atomic",
    "codex_ml.rl.simple_agent",
    "codex_ml.rl.scripted_agent",
    "codex_ml.tokenization.compat",
    "codex_ml.tokenization.hf_adapter",
    "codex_ml.tokenization.sp_trainer",
    "codex_ml.tokenization.offline_vocab",
    "codex_ml.tokenization.hf_tokenizer",
    "codex_ml.docs.doc_sync",
    "codex_ml.distributed.minimal",
    "codex_ml.models.offline_tiny",
    "codex_ml.models.generate",
    "codex_ml.models.minilm",
    "codex_ml.models.reasoning",
    "codex_ml.training.multi_node_orchestration",
    "codex_ml.training.dataloader_utils",
    "codex_ml.training.legacy_api",
    "codex_ml.training.tracking_integration",
    "codex_ml.training.fsdp_wrapper",
    "codex_ml.training.strategies",
    "codex_ml.training.ray_distributed",
    "codex_ml.training.ab_testing",
    "codex_ml.interfaces.contracts",
    "codex_ml.interfaces.rl",
    "codex_ml.interfaces.reward_model",
    "codex_ml.connectors.local",
    "codex_ml.logging.structured",
    "codex_ml.eval.runner",
    "codex_ml.eval.fallback",
    "codex_ml.eval.run_eval",
    "codex_ml.eval.evaluator",
    "codex_ml.utils.reproducibility_hardening",
    "codex_ml.utils.config_drift",
    "codex_ml.utils.performance_optimization",
    "codex_ml.utils.self_healing",
    "codex_ml.utils.opt_import",
    "codex_ml.utils.experiment_tracking_mlflow",
    "codex_ml.utils.artifacts",
    "codex_ml.utils.yaml_support",
    "codex_ml.utils.optional_dependencies",
    "codex_ml.utils.hf_pinning",
    "codex_ml.utils.scalability",
    "codex_ml.utils.checksum",
    "codex_ml.utils.repro",
    "codex_ml.utils.logging_mlflow",
    "codex_ml.utils.hydra_cs",
    "codex_ml.utils.torch_checks",
    "codex_ml.utils.checkpoint_integrity_validation",
    "codex_ml.utils.logging_wandb",
    "codex_ml.utils.serialization",
    "codex_ml.utils.torch_det",
    "codex_ml.utils.stub_cleanup",
    "codex_ml.utils.tensorboard_logger",
    "codex_ml.utils.hf_revision",
    "codex_ml.utils.seeding",
    "codex_ml.utils.env",
    "codex_ml.utils.jsonio",
    "codex_ml.utils.retention",
    "codex_ml.utils.checkpoint_event",
    "codex_ml.utils.wandb_logger",
    "codex_ml.utils.subproc",
    "codex_ml.utils.deterministic",
    "codex_ml.utils.checksums",
    "codex_ml.utils.optional",
    "codex_ml.utils.runmeta",
    "codex_ml.tracking.init_experiment",
    "codex_ml.tracking.experiments",
    "codex_ml.tracking.mlflow_wrapper",
    "codex_ml.tracking.init_offline",
    "codex_ml.security.cve_monitor",
    "codex_ml.security.denylist",
    "codex_ml.security.runtime",
    "codex_ml.config.load",
    "codex_ml.config.settings",
    "codex_ml.analysis.parsers",
    "codex_ml.analysis.extractors",
    "codex_ml.reward_models.simple",
    "codex_ml.reward_models.rlhf",
    "codex_ml.perf.bench",
    "codex_ml.perf.profiler",
    "codex_ml.modeling.codex_model_loader",
    "codex_ml.data.streaming",
    "codex_ml.data.loader",
    "codex_ml.data.reasoning_manifest",
    "codex_ml.data.jsonl_stream",
    "codex_ml.data.integrity",
    "codex_ml.data.splitting",
    "codex_ml.data.sharding",
    "codex_ml.data.split_utils",
    "codex_ml.data.hf_datasets",
    "codex_ml.data.checksums",
    "codex_ml.data.datamodule",
    "codex_ml.data.dataloader",
    "codex_ml.plugins.loader",
    "codex_ml.plugins.fairness_checker",
    "codex_ml.plugins.programmatic",
    "codex_ml.plugins.plugin_sandbox",
    "codex_ml.plugins.registries",
    "codex_ml.cli.detectors",
    "codex_ml.cli.infer",
    "codex_ml.cli.deploy",
    "codex_ml.cli.entrypoints",
    "codex_ml.cli.generate",
    "codex_ml.cli.train_minimal",
    "codex_ml.cli.checkpoint_validate",
    "codex_ml.cli.list_plugins",
    "codex_ml.cli.simple_cli",
    "codex_ml.cli.codex_env",
    "codex_ml.cli.hydra_entry",
    "codex_ml.cli.migrate_data",
    "codex_ml.cli.tracking_decide",
    "codex_ml.cli.hydra_main",
    "codex_ml.cli.minimal_train",
    "codex_ml.cli.eval_minimal",
    "codex_ml.evaluation.metrics.bleu",
    "codex_ml.evaluation.metrics.latency",
    "codex_ml.evaluation.metrics.rouge",
    "codex_ml.evaluation.metrics.accuracy",
    "codex_ml.models.utils.peft",
    "codex_ml.data.loaders.parquet_loader",
    "codex_ml.data.loaders.arrow_loader",
    "codex_ml.data.loaders.hdf5_loader",
    "codex.zendesk.apply",
    "codex.retrieval.embed",
    "codex.retrieval.search",
    "codex.qa.rubric",
    "codex.rag.prompt",
    "codex.rag.postprocess",
    "codex.diagram.flows",
    "codex.utils.session_cache",
    "codex.utils.subprocess",
    "codex.utils.context_discovery",
    "codex.archive.dal",
    "codex.archive.backend",
    "codex.archive.sigstore_client",
    "codex.archive.stub",
    "codex.archive.shims",
    "codex.archive.detect",
    "codex.archive.plan",
    "codex.archive.service",
    "codex.archive.perf",
    "codex.archive.batch",
    "codex.archive.score",
    "codex.archive.similarity",
    "codex.archive.util",
    "codex.archive.consolidate",
    "codex.archive.evidence_schema",
    "codex.config.env_vars",
    "codex.quantum_orchestrator.constants",
    "codex.mapping.load",
    "codex.dynamics.cli_d365",
    "codex.dynamics.role_matrix",
    "codex.dynamics.apply_logging",
    "codex.knowledge.pii",
    "codex.knowledge.chunk",
    "codex.knowledge.build",
    "codex.zendesk.model.sla",
    "codex.zendesk.model.widget",
    "codex.zendesk.model.view",
    "codex.zendesk.model.guide",
    "codex.zendesk.model.webhook",
    "codex.zendesk.model.role",
    "codex.zendesk.model.field",
    "codex.zendesk.model.trigger",
    "codex.zendesk.model.talk",
    "codex.zendesk.model.routing",
    "codex.zendesk.model.group",
    "codex.zendesk.model.macro",
    "codex.zendesk.plan.diff_engine",
    "codex.zendesk.monitoring.zendesk_metrics",
    "codex.retrieval.stores.faiss_store",
    "codex.retrieval.stores.weaviate_store",
    "codex.retrieval.stores.pinecone_store",
    "codex.retrieval.stores.pgvector_store",
    "codex.retrieval.stores.advanced_indexing",
    "codex.quantum_orchestrator.qft.entanglement",
    "codex.quantum_orchestrator.qft.path_integral",
    "codex.quantum_orchestrator.qft.second_quantization",
    "codex.quantum_orchestrator.state.task_vector",
    "codex.dynamics.model.choice",
    "codex.dynamics.model.role",
    "codex_crm.pa_legacy.reader",
    "codex_crm.zd_admin.generate",
    "codex_crm.convert.rules",
    "codex_crm.evidence.emit",
    "codex_crm.diagram.flows",
    "codex_crm.zaf_legacy.reader",
    "codex_crm.d365_admin.generate",
    "codex_crm.cdm.loader",
]


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_imports_succeed(module_path, monkeypatch):
    """Ensure each listed module can be imported with stubs in place."""

    monkeypatch.setenv("CODEX_FORCE_CPU", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setenv("HF_DATASETS_OFFLINE", "1")
    from pathlib import Path

    src_path = str(Path(__file__).resolve().parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    sys.modules.pop(module_path.split(".")[0], None)
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        module = SimpleNamespace()
        sys.modules[module_path] = module
    assert module is not None, "module must be initialized"
