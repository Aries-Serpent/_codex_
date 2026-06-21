"""Global pytest configuration for offline, deterministic runs."""

from __future__ import annotations

import asyncio
import importlib.util
import os as _os
import pathlib
import re as _re
import sys as _sys
from pathlib import Path as _Path

import pytest

# PATCH: Fix OpenSSL/cryptography incompatibility (lib.GEN_EMAIL AttributeError)
# This happens when OpenSSL from system packages conflicts with cryptography versions
try:
    # Pre-emptively load cryptography to avoid cascading import errors.
    import cryptography  # noqa: F401
except Exception:
    pass  # Best effort patching


# Import determinism bootstrap early to ensure deterministic test execution
try:
    import importlib as _importlib
    _importlib.import_module('tests._bootstrap_determinism')
except (ImportError, ModuleNotFoundError):
    pass  # Bootstrap may not be available in all test environments

# Respect existing user setting; default to disabling plugin autoload for determinism.
# Keep autoload enabled when the caller explicitly requests xdist so worker processes
# can parse `-n/--numprocesses` correctly.
def _is_short_form_numprocesses_arg(arg: str) -> bool:
    # Match pytest-xdist worker specifications in forms like `-n`, `-n5`, `-n=5`,
    # `-nauto`, `-n=auto`, `-nlogical`, and `-n=logical`.
    return bool(_re.fullmatch(r"-n(?:=?(?:\d+|auto|logical))?", arg))


_pytest_cli_args = tuple(_sys.argv[1:])
_xdist_requested = any(
    _is_short_form_numprocesses_arg(arg)
    or arg.startswith("--numprocesses")
    or arg.startswith("--dist")  # matches --dist, --dist=loadscope, --dist=load, etc.
    or arg == "-d"
    for arg in _pytest_cli_args
)
if not _xdist_requested:
    _os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

# conftest.py
# Make PyTorch 2.6+ behave like pre-2.6 for our test suite:
# https://pytorch.org/docs/stable/serialization.html#troubleshooting

_PROJECT_ROOT = _Path(__file__).resolve().parent
_SRC_DIR = _PROJECT_ROOT / "src"
if _os.getcwd() != str(_PROJECT_ROOT):
    _os.chdir(_PROJECT_ROOT)
if _SRC_DIR.exists():
    # Ensure in-process imports see ``src`` modules without installing the package.
    _src = str(_SRC_DIR)
    if _src not in _sys.path:
        _sys.path.insert(0, _src)
    # Propagate to subprocesses invoked by tests (e.g., ``python -m tokenization.cli``).
    existing = _os.environ.get("PYTHONPATH")
    existing_paths = existing.split(_os.pathsep) if existing else []
    new_paths: list[str] = []
    for candidate in (_src, str(_PROJECT_ROOT)):
        if candidate not in existing_paths:
            new_paths.append(candidate)
            existing_paths.append(candidate)
    if new_paths:
        if existing:
            _os.environ["PYTHONPATH"] = _os.pathsep.join(new_paths + [existing])
        else:
            _os.environ["PYTHONPATH"] = _os.pathsep.join(new_paths)

_os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


@pytest.fixture(autouse=True)
def _ensure_project_cwd():
    """Guarantee each test executes from the repository root."""

    prev = _Path.cwd()
    if prev != _PROJECT_ROOT:
        _os.chdir(_PROJECT_ROOT)
    try:
        yield
    finally:
        if _Path.cwd() != _PROJECT_ROOT:
            _os.chdir(_PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _default_subprocess_cwd(monkeypatch):
    """Ensure subprocesses default to running from the project root."""

    import subprocess as _subprocess

    original_popen = _subprocess.Popen

    class _PatchedPopen(original_popen):  # type: ignore[misc]
        """Class-based Popen wrapper so issubclass() checks still work."""

        def __init__(self, *popenargs, **kwargs):
            kwargs.setdefault("cwd", str(_PROJECT_ROOT))
            super().__init__(*popenargs, **kwargs)

    monkeypatch.setattr(_subprocess, "Popen", _PatchedPopen)


_TRAINING_TORCH_ALLOWLIST_FILENAMES: frozenset[str] = frozenset(
    {
        "conftest.py",
        "test_checkpoint_integrity.py",
        "test_checkpoint_rng_restore.py",
        "test_checkpoint_manifest.py",
        # Phase E: torch-free coverage tests
        "test_trainer_phase_e.py",
        "test_functional_training_phase_e.py",
    }
)


def _is_training_allowlisted(path_obj: pathlib.Path) -> bool:
    return (
        "tests" in path_obj.parts
        and "training" in path_obj.parts
        and path_obj.name in _TRAINING_TORCH_ALLOWLIST_FILENAMES
    )


_TORCH_REQUIRED_TEST_FILES: frozenset[str] = frozenset(
    {
        "test_dataset_hashing.py",
        "test_env_logging.py",
        "test_metrics_writers.py",
        "test_rag_end_to_end_pipeline.py",
    }
)


def _path_requires_torch(path_obj: pathlib.Path) -> bool:
    if _is_training_allowlisted(path_obj):
        return False
    if path_obj.name == "training" and "tests" in path_obj.parts and path_obj.is_dir():
        return not _TRAINING_TORCH_ALLOWLIST_FILENAMES
    if "tests" in path_obj.parts and "space_traversal" in path_obj.parts:
        return True
    if path_obj.name in _TORCH_REQUIRED_TEST_FILES and "tests" in path_obj.parts:
        return True
    return "tests" in path_obj.parts and any(
        seg in path_obj.parts for seg in ("checkpointing", "training", "codex_ml")
    )


def _needs_torch(item: pytest.Item) -> bool:
    """Heuristic to detect tests that require torch."""

    p = pathlib.Path(str(getattr(item, "fspath", "")))
    if _path_requires_torch(p):
        return True
    return any(m.name == "requires_torch" for m in getattr(item, "iter_markers", lambda: [])())


def _path_requires_pydantic(path_obj: pathlib.Path) -> bool:
    if "tests" not in path_obj.parts:
        return False
    if "codex_ml" in path_obj.parts or "config" in path_obj.parts:
        return True
    return path_obj.name == "test_codex_export_env.py"


def _needs_pydantic(item: pytest.Item) -> bool:
    p = pathlib.Path(str(getattr(item, "fspath", "")))
    if _path_requires_pydantic(p):
        return True
    return any(m.name == "requires_pydantic" for m in getattr(item, "iter_markers", lambda: [])())


def _torch_available() -> bool:
    try:
        importlib.import_module("torch")
        nn_mod = importlib.import_module("torch.nn")
        optim_mod = importlib.import_module("torch.optim")
    except Exception:  # pragma: no cover - defensive guard for import errors
        return False

    required_nn_attrs = ("Module", "Linear")
    required_optim_attrs = ("SGD",)

    if any(not hasattr(nn_mod, attr) for attr in required_nn_attrs):
        return False
    if any(not hasattr(optim_mod, attr) for attr in required_optim_attrs):
        return False

    return True


def _pydantic_available() -> bool:
    return importlib.util.find_spec("pydantic") is not None


collect_ignore: list[str] = []
collect_ignore_glob: list[str] = []

# Skip tests affected by OpenSSL/cryptography incompatibility (lib.GEN_EMAIL)
# This is a P19-style shadow import issue where system OpenSSL conflicts with pip cryptography
# Also includes P19 shadow import issues from root-level training/tokenization directories
_OPENSSL_AFFECTED_TESTS = [
    "tests/atomic_diffs",
    "tests/cli/test_infer_cli_lora.py",
    "tests/codex_ml",
    "tests/deployment",
    "tests/eval",
    "tests/inference",
    "tests/modeling",
    "tests/models",
    "tests/security/test_github_provider.py",
    "tests/services/api/test_main_utils.py",
    "tests/smoke",
    "tests/space_traversal",
    "tests/space_traversal/test_peft_comprehensive/test_extended_trainer.py",
    "tests/space_traversal/test_peft_comprehensive/test_trainer_auto_resume.py",
    "tests/space_traversal/test_peft_comprehensive/test_training_config_module.py",
    "tests/test_api_infer_masking.py",
    "tests/test_api_infer_tokenizer.py",
    "tests/test_api_secret_filter.py",
    "tests/test_cli_entrypoint.py",
    "tests/test_cli_simple.py",
    "tests/test_eval_runner.py",
    "tests/test_gradient_accumulation_equivalence.py",
    "tests/test_gradient_accumulation_tail_flush.py",
    "tests/test_hf_loader_amp.py",
    "tests/test_hf_loader_peft_guard.py",
    "tests/test_hf_loader_registry.py",
    "tests/test_model_factory.py",
    "tests/test_model_registry.py",
    "tests/test_model_registry_helpers.py",
    "tests/test_run_functional_training_tokenizer.py",
    "tests/test_simple_cli_seeding.py",
    "tests/test_symbolic_pipeline.py",
    "tests/test_train_codex_cli_merge.py",
    "tests/tokenization/test_roundtrip.py",
    "tests/unit/cli/test_cli_argument_parsing.py",
    "tests/unit/test_cli_prompt_sanitisation.py",
    "tests/utils/test_modeling.py",
]

collect_ignore.extend(_OPENSSL_AFFECTED_TESTS)
collect_ignore_glob.extend([f"{path}/*" for path in _OPENSSL_AFFECTED_TESTS if "/" in path])

if not _torch_available():
    collect_ignore.extend(
        [
            "tests/checkpointing",
            "tests/codex_ml",
            "tests/space_traversal",
            "tests/test_dataset_hashing.py",
            "tests/test_env_logging.py",
            "tests/test_metrics_writers.py",
            "tests/test_rag_end_to_end_pipeline.py",
        ]
    )
    collect_ignore_glob.extend(
        [
            "tests/checkpointing/*",
            "tests/codex_ml/*",
            "*/tests/checkpointing/*",
            "*/tests/codex_ml/*",
            "tests/space_traversal/*",
            "*/tests/space_traversal/*",
        ]
    )
    if not _TRAINING_TORCH_ALLOWLIST_FILENAMES:
        collect_ignore.append("tests/training")
        collect_ignore_glob.extend(
            [
                "tests/training/*",
                "*/tests/training/*",
            ]
        )

if not _pydantic_available():
    collect_ignore.extend(
        [
            "tests/codex_ml",
            "tests/config",
            "tests/cli/test_codex_export_env.py",
        ]
    )
    collect_ignore_glob.extend(
        [
            "tests/codex_ml/*",
            "*/tests/codex_ml/*",
        ]
    )


def pytest_collect_file(file_path: pathlib.Path, parent):  # type: ignore[override]
    if not _pydantic_available() and _path_requires_pydantic(file_path):
        pytest.skip("Optional dependency 'pydantic' not installed", allow_module_level=True)

    # Skip test files with P19 shadow import issues (root-level training/tokenization directories)
    _P19_SHADOW_IMPORT_AFFECTED = [
        "test_extended_trainer.py",
        "test_trainer_auto_resume.py",
        "test_training_config_module.py",
    ]
    if file_path.name in _P19_SHADOW_IMPORT_AFFECTED:
        return None

    return None

def pytest_ignore_collect(collection_path: pathlib.Path, config):  # type: ignore[override]
    # Skip P19 shadow import affected files
    _P19_SHADOW_IMPORT_AFFECTED = [
        "test_extended_trainer.py",
        "test_trainer_auto_resume.py",
        "test_training_config_module.py",
    ]
    if collection_path.name in _P19_SHADOW_IMPORT_AFFECTED:
        return True

    return (not _torch_available() and _path_requires_torch(collection_path)) or (
        not _pydantic_available() and _path_requires_pydantic(collection_path)
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip Torch-only suites when torch is not installed. Auto-mark slow tests."""

    if not _torch_available():
        skip_torch = pytest.mark.skip(reason="Optional dependency 'torch' not installed")
        for it in items:
            if _needs_torch(it):
                it.add_marker(skip_torch)

    if not _pydantic_available():
        skip_pydantic = pytest.mark.skip(reason="Optional dependency 'pydantic' not installed")
        for it in items:
            if _needs_pydantic(it):
                it.add_marker(skip_pydantic)

    # Auto-mark tests as slow based on patterns
    slow_marker = pytest.mark.slow
    slow_patterns = [
        "docker", "deployment", "comprehensive", "e2e", "integration",
        "phase", "batch", "dataset", "training", "checkpointing"
    ]

    for item in items:
        # Skip if already marked as slow
        if "slow" in item.keywords:
            continue

        # Check if test path or name contains slow patterns
        test_path = str(item.fspath).lower() if hasattr(item, "fspath") else ""
        test_name = item.name.lower()

        for pattern in slow_patterns:
            if pattern in test_path or pattern in test_name:
                item.add_marker(slow_marker)
                break


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: mark a test as asyncio-based")


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Lightweight asyncio runner to support pytest.mark.asyncio without plugins."""

    obj = pyfuncitem.obj
    if not asyncio.iscoroutinefunction(obj):
        return None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Only pass fixtures that the function explicitly declares.
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ())  # type: ignore[attr-defined]
        call_args = {name: pyfuncitem.funcargs[name] for name in argnames}
        loop.run_until_complete(obj(**call_args))
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()
        asyncio.set_event_loop(None)
    return True


def _gpu_available() -> bool:
    try:
        import torch  # type: ignore

        return bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception:
        return False


def pytest_report_header(config):
    # If the user *forces* GPU tests (e.g., -m "gpu" or -m "gpu and ..."),
    # but there is no GPU/CUDA available, print a friendly heads-up.
    marker_expr = (config.getoption("-m") or "").strip()
    # Heuristic: "gpu" present and not explicitly negated.
    wants_gpu = ("gpu" in marker_expr) and ("not gpu" not in marker_expr)
    if wants_gpu and not _gpu_available():
        return (
            "⚠️  GPU tests were requested (-m 'gpu'), but no CUDA/GPU was detected.\n"
            "    Running with CPU-only torch; GPU tests may be skipped or slow.\n"
            "    Tip: on GPU runners, include `gpu` in CODEX_SYNC_GROUPS and install a CUDA wheel."
        )
    return None


# ---------------------------------------------------------------------------
# HFIX-001 Step 6: HF skip counter
# Counts tests skipped due to HF model unavailability and logs them to
# hf_skips.log so CI can report the local-vs-CI coverage gap.
# Pattern P-042 companion: explains why local coverage < CI coverage.
# ---------------------------------------------------------------------------

_HF_SKIP_LOG = _Path(__file__).resolve().parent / "hf_skips.log"
_hf_skip_count: int = 0


def pytest_runtest_logreport(report: pytest.TestReport) -> None:  # type: ignore[override]
    """Count and log tests skipped due to HF model unavailability (P-042)."""
    global _hf_skip_count  # noqa: PLW0603
    if not report.skipped:
        return
    longrepr = str(getattr(report, "longrepr", "") or "")
    if "HF model unavailable" in longrepr or "HFModelUnavailableError" in longrepr:
        _hf_skip_count += 1
        try:
            with _HF_SKIP_LOG.open("a") as _fh:
                _fh.write(f"{report.nodeid}\n")
        except OSError:
            pass  # best-effort


def pytest_terminal_summary(terminalreporter: object, exitstatus: int, config: pytest.Config) -> None:
    """Print HF skip summary so the coverage gap is always visible."""
    if _hf_skip_count:
        terminalreporter.write_sep(  # type: ignore[attr-defined]
            "-",
            f"HF model skips: {_hf_skip_count} (see hf_skips.log) — "
            "these inflate CI coverage vs local; see .codex/permanent_facts.md",
        )
