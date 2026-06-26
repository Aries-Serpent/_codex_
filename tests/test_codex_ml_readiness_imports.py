"""
Test Codex Ml Readiness Imports

Test module for codex ml readiness imports.
"""

import importlib
import os
import sys
import types

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")


def _assert_import_contract(mod: object, module_name: str) -> None:
    """Assert stronger import guarantees than a simple non-None check."""
    assert mod.__name__ == module_name, "__name__ is not valid"
    assert hasattr(mod, "__spec__")
    # A real imported module should expose at least one public attribute.
    public_names = [name for name in dir(mod) if not name.startswith("_")]
    assert public_names, "public_names is not valid"


@pytest.fixture(autouse=True)
def stub_optional_dependencies(monkeypatch, tmp_path):
    """Stub heavy/optional deps so imports remain lightweight."""
    # NumPy stub
    numpy = types.ModuleType("numpy")
    numpy.__spec__ = importlib.machinery.ModuleSpec("numpy", loader=None)  # type: ignore[attr-defined]
    numpy.seed = lambda _s=None: None
    numpy.random = types.SimpleNamespace(seed=lambda _s=None: None)
    monkeypatch.setitem(sys.modules, "numpy", numpy)

    # Torch stub with minimal attributes used across helpers
    torch = types.SimpleNamespace(
        manual_seed=lambda _s=None: None,
        initial_seed=lambda: 42,
        cuda=types.SimpleNamespace(manual_seed_all=lambda _s=None: None),
        backends=types.SimpleNamespace(
            cudnn=types.SimpleNamespace(deterministic=False, benchmark=True),
            cuda=types.SimpleNamespace(matmul=types.SimpleNamespace(allow_tf32=True)),
        ),
        use_deterministic_algorithms=lambda _flag=False: None,
        float32="float32",
        float16="float16",
        bfloat16="bfloat16",
    )
    torch.__spec__ = importlib.machinery.ModuleSpec("torch", loader=None)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "torch.cuda", torch.cuda)

    # MLflow stub with a spec so util.find_spec succeeds
    mlflow = types.ModuleType("mlflow")
    mlflow.__spec__ = importlib.machinery.ModuleSpec("mlflow", loader=None)  # type: ignore[attr-defined]

    def _set_tracking_uri(uri):
        os.environ.setdefault("MLFLOW_TRACKING_URI", uri)

    def _set_experiment(name):
        os.environ.setdefault("MLFLOW_EXPERIMENT", name)

    def _start_run(**kwargs):
        return types.SimpleNamespace(**kwargs)

    mlflow.set_tracking_uri = _set_tracking_uri
    mlflow.set_experiment = _set_experiment
    mlflow.start_run = _start_run
    mlflow.end_run = lambda: None
    mlflow.log_params = lambda params: None
    mlflow.log_param = lambda k, v: None
    mlflow.log_metrics = lambda metrics, step=None: None
    mlflow.log_metric = lambda k, v, step=None: None
    mlflow.log_artifact = lambda path, artifact_path=None: None
    monkeypatch.setitem(sys.modules, "mlflow", mlflow)

    # W&B stub
    wandb = types.SimpleNamespace(init=lambda **kwargs: {"run": kwargs})
    monkeypatch.setitem(sys.modules, "wandb", wandb)

    # Hydra stub for CLI entrypoints
    hydra = types.SimpleNamespace(main=lambda **_kwargs: (lambda fn: fn))
    monkeypatch.setitem(sys.modules, "hydra", hydra)
    monkeypatch.setitem(sys.modules, "hydra.main", hydra)

    # Transformers / datasets / sentencepiece shims
    transformers = types.ModuleType("transformers")
    transformers.__spec__ = importlib.machinery.ModuleSpec("transformers", loader=None)  # type: ignore[attr-defined]

    class _AutoModel:
        def from_pretrained(self, *_args, **_kwargs):
            return self

    class _AutoTokenizer:
        def from_pretrained(self, *_args, **_kwargs):
            return self

        def encode(self, text, **_kwargs):
            return [0 for _ in text.split()]

        def decode(self, ids, **_kwargs):
            return " ".join(map(str, ids))

        def add_special_tokens(self, *_args, **_kwargs):
            return None

    transformers.AutoModelForCausalLM = _AutoModel()  # type: ignore[attr-defined]
    transformers.AutoModel = _AutoModel()  # type: ignore[attr-defined]
    transformers.AutoTokenizer = _AutoTokenizer()  # type: ignore[attr-defined]
    transformers.PreTrainedTokenizerBase = _AutoTokenizer  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "transformers", transformers)

    datasets = types.ModuleType("datasets")
    datasets.__spec__ = importlib.machinery.ModuleSpec("datasets", loader=None)  # type: ignore[attr-defined]
    datasets.Dataset = type("Dataset", (), {})
    monkeypatch.setitem(sys.modules, "datasets", datasets)
    monkeypatch.setitem(sys.modules, "sentencepiece", types.SimpleNamespace())

    # Ensure a writable MLflow directory
    os.environ.setdefault("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())
    os.environ.setdefault("HF_REVISION", "abcdef0")
    yield


@pytest.mark.parametrize(
    "module_name",
    [
        "codex_ml.utils.seeding",
        "codex_ml.utils.torch_det",
        "codex_ml.utils.experiment_tracking_mlflow",
        "codex_ml.utils.config_drift",
        "codex_ml.utils.env",
        "codex_ml.utils.optional",
        "codex_ml.utils.optional_dependencies",
        "codex_ml.utils.yaml_support",
        "codex_ml.utils.serialization",
        "codex_ml.utils.hf_revision",
        "codex_ml.utils.artifacts",
        "codex_ml.utils.logging_mlflow",
        "codex_ml.utils.logging_wandb",
        "codex_ml.utils.jsonio",
        "codex_ml.utils.opt_import",
        "codex_ml.utils.self_healing",
        "codex_ml.utils.stub_cleanup",
        "codex_ml.utils.checkpoint_event",
        "codex_ml.utils.runmeta",
    ],
)
def test_utils_modules_import(module_name):
    mod = importlib.import_module(module_name)
    _assert_import_contract(mod, module_name)


def test_seeding_and_worker_seed(monkeypatch):
    from codex_ml.utils import seeding, torch_det

    seeding.set_reproducible(123, deterministic=True)
    assert os.environ.get("PYTHONHASHSEED") == "123", "Condition must be true"

    # Ensure the worker seeding helper is tolerant to stubs
    torch_det.seed_worker(0)


@pytest.mark.parametrize(
    "module_name",
    [
        "codex_ml.analysis.parsers",
        "codex_ml.analysis.extractors",
    ],
)
def test_analysis_modules(module_name):
    mod = importlib.import_module(module_name)
    _assert_import_contract(mod, module_name)

    if hasattr(mod, "parse_tiered"):
        result = mod.parse_tiered("def f():\n    return 1")
        assert result.mode in {"ast", "cst", "parso", "degraded"}


def test_tracking_helpers(tmp_path):
    from codex_ml.tracking import init_offline, mlflow_wrapper

    uri = init_offline.init_mlflow_offline(local_dir=str(tmp_path / "mlruns"))
    assert uri.startswith("file:"), "Condition must be true"
    wandb_run = init_offline.init_wandb_offline(project="demo")
    assert isinstance(wandb_run, dict)
    assert "run" in wandb_run, "Condition must be true"

    tracker = mlflow_wrapper.MLflowTracker(enabled=True)
    with tracker.start_run():
        tracker.log_param("demo", "value")
        tracker.log_metric("score", 1.0)
        tracker.log_artifact(str(tmp_path / "artifact.txt"))


@pytest.mark.parametrize(
    "module_name",
    [
        "codex_ml.cli.hydra_main",
        "codex_ml.cli.hydra_entry",
        "codex_ml.cli.deploy",
        "codex_ml.cli.detectors",
        "codex_ml.cli.checkpoint_validate",
        "codex_ml.cli.tracking_decide",
        "codex_ml.cli.generate",
        "codex_ml.cli.list_plugins",
        "codex_ml.cli.entrypoints",
        "codex_ml.cli.simple_cli",
        "codex_ml.cli.eval_minimal",
        "codex_ml.cli.train_minimal",
        "codex_ml.cli.minimal_train",
        "codex_ml.cli.infer",
        "codex_ml.cli.migrate_data",
        "codex_ml.cli.codex_env",
    ],
)
def test_cli_entrypoints_import(module_name):
    mod = importlib.import_module(module_name)
    _assert_import_contract(mod, module_name)


@pytest.mark.parametrize(
    "module_name",
    [
        "codex_ml.metrics.generation",
        "codex_ml.metrics.reward",
        "codex_ml.metrics.streaming",
        "codex_ml.metrics.classification",
        "codex_ml.metrics.evaluator",
        "codex_ml.metrics._optional_bleu_rouge",
        "codex_ml.eval.evaluator",
        "codex_ml.eval.run_eval",
        "codex_ml.eval.runner",
    ],
)
def test_metrics_and_eval_imports(module_name):
    mod = importlib.import_module(module_name)
    _assert_import_contract(mod, module_name)


@pytest.mark.parametrize(
    "module_name",
    [
        "codex_ml.tokenization.hf_tokenizer",
        "codex_ml.tokenization.compat",
        "codex_ml.tokenization.sp_trainer",
        "codex_ml.tokenization.offline_vocab",
    ],
)
def test_tokenization_modules(module_name, monkeypatch):
    mod = importlib.import_module(module_name)
    _assert_import_contract(mod, module_name)

    adapter_cls = getattr(mod, "HFTokenizerAdapter", None)
    if adapter_cls is not None:
        # Mock load_from_pretrained to avoid actual HuggingFace downloads in CI
        # The stub_optional_dependencies fixture provides fake transformers, but
        # when real transformers is installed, this test would try to download.
        # We use the whitespace fallback by temporarily hiding transformers availability.
        monkeypatch.setattr(mod, "TRANSFORMERS_AVAILABLE", False)
        monkeypatch.setattr(mod, "AutoTokenizer", None)
        adapter = adapter_cls.load("demo", use_fast=False)
        tokens = adapter.encode("hello world", pad_to_max=True, max_length=4)
        assert isinstance(tokens, list)


def test_safety_and_deployment_imports():
    import codex_ml.deployment.package as package
    import codex_ml.detectors.capability_detectors as capability_detectors
    import codex_ml.detectors.experiment_summary as exp_summary
    import codex_ml.safety.moderation as moderation
    import codex_ml.safety.redaction as redaction
    import codex_ml.safety.sandbox as sandbox
    import codex_ml.safety.sanitizers as sanitizers
    import codex_ml.serving.deployment as serving

    settings = moderation.ModerationSettings(enabled=False)
    decision = moderation.ModerationDecision(approved=True, stage="test", provider="offline")
    assert decision.to_dict()["approved"], "Condition must be true"
    adapter = moderation.ModerationAdapter(settings)
    decision_checked = adapter.review("sample", stage="pre")
    assert decision_checked.approved is True, "approved is not valid"

    redactor = redaction.SecretRedactor()
    assert "TOKEN" in redactor.redact("bearer: token-1234"), "Condition must be true"
    sanitized = sanitizers.sanitize_output("clean")
    assert isinstance(sanitized, dict)
    assert sanitized.get("text") == "clean", "Condition must be true"
    result = sandbox.run_in_sandbox(["echo", "hi"], timeout=2)
    assert result.returncode == 0, "Result must not be empty"

    _assert_import_contract(package, "codex_ml.deployment.package")
    _assert_import_contract(serving, "codex_ml.serving.deployment")
    _assert_import_contract(exp_summary, "codex_ml.detectors.experiment_summary")
    _assert_import_contract(capability_detectors, "codex_ml.detectors.capability_detectors")
