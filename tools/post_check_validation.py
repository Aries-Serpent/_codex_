"""Post-check validation utilities for verifying Iterations 1-4 hardening."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
import types
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


@contextmanager
def _sys_path() -> Sequence[str]:
    added: list[str] = []
    for candidate in (str(REPO_ROOT), str(SRC_ROOT)):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
            added.append(candidate)
    try:
        yield added
    finally:
        for candidate in added:
            try:
                sys.path.remove(candidate)
            except ValueError:  # pragma: no cover - defensive cleanup
                pass


@dataclass
class CheckReport:
    """Result of an individual validation check."""

    name: str
    passed: bool
    details: list[str]

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "passed": self.passed, "details": list(self.details)}


@dataclass
class ValidationReport:
    """Aggregate report covering all validation checks."""

    checks: list[CheckReport]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        return {"passed": self.passed, "checks": [check.to_dict() for check in self.checks]}


_DEF_STUB_MARKER = "raise NotImplementedError"


def _no_notimplemented(name: str, paths: Sequence[Path]) -> CheckReport:
    issues: list[str] = []
    for path in paths:
        if not path.exists():
            issues.append(f"missing file: {path}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append(f"unable to read {path}: {exc}")
            continue
        if _DEF_STUB_MARKER in text:
            issues.append(f"{path} still contains '{_DEF_STUB_MARKER}'")
    return CheckReport(name=name, passed=not issues, details=issues)


def _check_codex_setup_bootstrap() -> CheckReport:
    name = "Iteration 1 – codex_setup bootstrap"
    try:
        with _sys_path():
            module = import_module("codex_setup")
    except Exception as exc:  # pragma: no cover - import failure reported as failure
        return CheckReport(name=name, passed=False, details=[f"import failed: {exc!r}"])

    issues: list[str] = []
    original_env = {"CODEX_SESSION_ID": os.environ.get("CODEX_SESSION_ID")}
    original_attrs = {
        attr: getattr(module, attr)
        for attr in (
            "REPO_ROOT",
            "CODEX_DIR",
            "CHANGE_LOG",
            "ERRORS_NDJSON",
            "RESULTS_MD",
            "README_MD",
        )
    }

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex_dir = tmp_path / ".codex"
            readme = tmp_path / "README.md"
            readme.write_text("# Codex\n", encoding="utf-8")

            module.REPO_ROOT = tmp_path
            module.CODEX_DIR = codex_dir
            module.CHANGE_LOG = codex_dir / "change_log.md"
            module.ERRORS_NDJSON = codex_dir / "errors.ndjson"
            module.RESULTS_MD = codex_dir / "results.md"
            module.README_MD = readme

            module.init_codex_dir()
            if not codex_dir.exists():
                issues.append(".codex directory was not created")
            expected_files = [
                codex_dir / "change_log.md",
                codex_dir / "errors.ndjson",
                codex_dir / "results.md",
            ]
            for file_path in expected_files:
                if not file_path.exists():
                    issues.append(f"expected bootstrap file missing: {file_path}")

            meta = module.check_cli_version(sys.executable, "--version")
            if meta.get("tool") != sys.executable:
                issues.append("check_cli_version did not record tool name")
            if meta.get("available") is False:
                issues.append("python interpreter was reported unavailable")

            module.update_readme_best_effort()
            readme_content = readme.read_text(encoding="utf-8")
            if "## Codex Logs" not in readme_content:
                issues.append("README was not augmented with Codex Logs section")
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        for attr, value in original_attrs.items():
            setattr(module, attr, value)

    return CheckReport(name=name, passed=not issues, details=issues)


def _check_task_sequence_seed_and_mlflow() -> CheckReport:
    name = "Iteration 2 – task sequence seed & MLflow"
    try:
        with _sys_path():
            module = import_module("codex_task_sequence")
    except Exception as exc:  # pragma: no cover - import failure reported as failure
        return CheckReport(name=name, passed=False, details=[f"import failed: {exc!r}"])

    issues: list[str] = []
    saved_env = {
        key: os.environ.get(key)
        for key in ("MLFLOW_TRACKING_URI", "CODEX_MLFLOW_URI", "CODEX_MLFLOW_LOCAL_DIR")
    }
    try:
        module._set_global_seed(1234)
        first = random.randint(0, 10_000)
        second = random.randint(0, 10_000)
        module._set_global_seed(1234)
        repeat = random.randint(0, 10_000)
        if repeat != first:
            issues.append("random seed was not deterministic across resets")
        if os.environ.get("PYTHONHASHSEED") != "1234":
            issues.append("PYTHONHASHSEED was not enforced by _set_global_seed")
        if second == first:
            issues.append("random generator did not advance after initial seed set")

        for key in saved_env:
            os.environ.pop(key, None)
        with tempfile.TemporaryDirectory() as tmp:
            mlruns_dir = Path(tmp) / "mlruns"
            recorded_uri: list[str] = []

            dummy_mlflow = types.SimpleNamespace(
                set_tracking_uri=lambda uri: recorded_uri.append(uri),
                get_tracking_uri=lambda: recorded_uri[-1] if recorded_uri else "",
            )
            previous_mlflow = sys.modules.get("mlflow")
            sys.modules["mlflow"] = dummy_mlflow  # type: ignore[assignment]
            try:
                success = module.setup_mlflow_tracking(mlruns_dir, dry_run=False)
            finally:
                if previous_mlflow is None:
                    sys.modules.pop("mlflow", None)
                else:
                    sys.modules["mlflow"] = previous_mlflow

            if not success:
                issues.append("setup_mlflow_tracking returned False unexpectedly")

            tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "")
            codex_uri = os.environ.get("CODEX_MLFLOW_URI", "")
            if not tracking_uri.startswith("file:"):
                issues.append("MLFLOW_TRACKING_URI was not coerced to file scheme")
            if tracking_uri != codex_uri:
                issues.append("MLFLOW_TRACKING_URI and CODEX_MLFLOW_URI diverged")
            local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")
            if not local_dir:
                issues.append("CODEX_MLFLOW_LOCAL_DIR was not exported")
            else:
                expected_dir = mlruns_dir.resolve()
                if Path(local_dir).resolve() != expected_dir:
                    issues.append("CODEX_MLFLOW_LOCAL_DIR does not point to requested directory")

            if not recorded_uri or not recorded_uri[-1].startswith("file:"):
                issues.append("mlflow.set_tracking_uri was not invoked with file URI")
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    return CheckReport(name=name, passed=not issues, details=issues)


def _check_mlflow_guard_offline() -> CheckReport:
    name = "Iteration 3 – MLflow offline guard"
    try:
        with _sys_path():
            guard = import_module("codex_ml.tracking.mlflow_guard")
    except Exception as exc:  # pragma: no cover - import failure reported as failure
        return CheckReport(name=name, passed=False, details=[f"import failed: {exc!r}"])

    issues: list[str] = []
    saved_env = {
        key: os.environ.get(key)
        for key in ("MLFLOW_TRACKING_URI", "CODEX_MLFLOW_URI", "MLFLOW_ALLOW_REMOTE")
    }
    try:
        os.environ["MLFLOW_TRACKING_URI"] = "http://example.com"
        os.environ.pop("CODEX_MLFLOW_URI", None)
        os.environ.pop("MLFLOW_ALLOW_REMOTE", None)
        uri = guard.bootstrap_offline_tracking()
        if not uri.startswith("file:"):
            issues.append("bootstrap_offline_tracking did not return file URI")
        decision = guard.bootstrap_offline_tracking_decision()
        if decision.allow_remote:
            issues.append(
                "bootstrap_offline_tracking_decision unexpectedly allowed remote tracking"
            )
        if decision.fallback_reason not in {"non_file_scheme", None}:
            issues.append("unexpected fallback reason returned by guard")
        if guard.last_decision() is None:
            issues.append("last_decision did not record guard output")
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    return CheckReport(name=name, passed=not issues, details=issues)


def _check_training_defaults() -> CheckReport:
    name = "Iteration 3 – training defaults"
    try:
        with _sys_path():
            training = import_module("codex_ml.training")
    except Exception as exc:  # pragma: no cover - import failure reported as failure
        return CheckReport(name=name, passed=False, details=[f"import failed: {exc!r}"])

    issues: list[str] = []
    cfg = training.TrainingRunConfig()
    if not getattr(cfg, "deterministic", False):
        issues.append("TrainingRunConfig.deterministic default is not enabled")
    if getattr(cfg, "mlflow_enable", True):
        issues.append("TrainingRunConfig.mlflow_enable default should be False for offline guard")
    if not hasattr(training, "run_functional_training"):
        issues.append("run_functional_training entrypoint is missing")
    if not hasattr(training, "build_dataloader"):
        issues.append("build_dataloader helper is missing")

    return CheckReport(name=name, passed=not issues, details=issues)


def _check_regression_tests_present() -> CheckReport:
    name = "Iteration 4 – regression tests present"
    required_tests = [
        "tests/test_determinism.py",
        "tests/test_codex_sequence_validations.py",
        "tests/test_logging_bootstrap.py",
        "tests/test_mlflow_adapter.py",
        "tests/test_nox_tests_delegation.py",
    ]
    issues: list[str] = []
    for rel in required_tests:
        path = REPO_ROOT / rel
        if not path.exists():
            issues.append(f"regression test missing: {rel}")
    return CheckReport(name=name, passed=not issues, details=issues)


def run_post_check_validation() -> ValidationReport:
    checks = [
        _no_notimplemented(
            "Iteration 1 – automation stubs cleared",
            [
                REPO_ROOT / "codex_setup.py",
                REPO_ROOT / "noxfile.py",
                REPO_ROOT / "codex_update_runner.py",
            ],
        ),
        _check_codex_setup_bootstrap(),
        _no_notimplemented(
            "Iteration 2 – orchestration stubs cleared",
            [
                REPO_ROOT / "codex_task_sequence.py",
                REPO_ROOT / "codex_ast_upgrade.py",
            ],
        ),
        _check_task_sequence_seed_and_mlflow(),
        _check_mlflow_guard_offline(),
        _check_training_defaults(),
        _check_regression_tests_present(),
    ]
    return ValidationReport(checks=checks)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Iterations 1-4 hardening work")
    parser.add_argument(
        "--format", choices=("human", "json"), default="human", help="Output format"
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_post_check_validation()
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        for check in report.checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"[{status}] {check.name}")
            for detail in check.details:
                print(f"  - {detail}")
        print(f"Overall: {'PASS' if report.passed else 'FAIL'}")
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
