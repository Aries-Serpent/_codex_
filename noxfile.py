from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import nox

REPO_ROOT = Path(__file__).resolve().parent
_CANDIDATE_PYTHONS = ("3.12", "3.11", "3.10")
_available = [v for v in _CANDIDATE_PYTHONS if shutil.which(f"python{v}")]
if _available:
    PY_VERSIONS = tuple(_available)
else:
    PY_VERSIONS = (f"{sys.version_info.major}.{sys.version_info.minor}",)

DEFAULT_PYTHON = os.getenv("CODEX_NOX_PYTHON") or PY_VERSIONS[0]
if DEFAULT_PYTHON not in PY_VERSIONS:
    PY_VERSIONS = (DEFAULT_PYTHON, *PY_VERSIONS)

TEST_BOOTSTRAP_PKGS = ("pip", "setuptools", "wheel")
DEFAULT_COVERAGE_FLOOR = int(os.getenv("CODEX_COV_FLOOR", "85"))
UV = os.getenv("UV_BIN", "uv")
OFFLINE_TEST_TARGETS = (
    "tests/unit/test_zendesk_models.py",
    "tests/e2e_offline/test_diff_and_apply.py",
)

nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = False
nox.options.error_on_missing_interpreters = False


def _export_env(session: nox.Session) -> None:
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.env.setdefault("PYTHONUTF8", "1")


@nox.session(python=list(PY_VERSIONS))
def tests(session: nox.Session) -> None:
    """Run the full unit test suite against all discovered interpreters."""

    session.install(*TEST_BOOTSTRAP_PKGS)
    session.install("-e", ".[test]")
    _export_env(session)
    session.run("pytest", "-q")


@nox.session(name="tests_offline", python=DEFAULT_PYTHON)
def tests_offline(session: nox.Session) -> None:
    """Run the curated offline test targets used in release checklists."""

    session.install("pytest", "pydantic")
    _export_env(session)
    session.run("pytest", "-q", *OFFLINE_TEST_TARGETS)


@nox.session(name="tests_gpu", python=DEFAULT_PYTHON)
def tests_gpu(session: nox.Session) -> None:
    """Run GPU-marked tests when CUDA devices are available."""

    session.install("pytest", "pytest-randomly", "torch")

    try:
        import torch  # type: ignore
    except ImportError:  # pragma: no cover - defensive guard
        session.log("PyTorch is unavailable after installation; skipping GPU test session.")
        return

    is_available = getattr(getattr(torch, "cuda", None), "is_available", None)
    if not callable(is_available) or not is_available():
        session.log("CUDA is unavailable; skipping GPU test session.")
        return

    _export_env(session)
    session.env.setdefault("PYTHONHASHSEED", "0")
    session.run(
        "pytest",
        "--disable-plugin-autoload",
        "-p",
        "pytest_randomly",
        "-q",
        "-m",
        "gpu",
    )


@nox.session(name="bootstrap", python=DEFAULT_PYTHON)
def bootstrap(session: nox.Session) -> None:
    """Create or refresh dependency locks using uv."""

    _export_env(session)
    session.install("uv")
    if (REPO_ROOT / "requirements.in").exists():
        session.run(
            UV,
            "pip",
            "compile",
            "requirements.in",
            "--universal",
            "-o",
            "requirements.txt",
        )
    else:
        session.run(
            UV,
            "pip",
            "compile",
            "pyproject.toml",
            "--universal",
            "-o",
            "requirements.txt",
        )
    session.run(UV, "pip", "sync", "requirements.txt")


@nox.session(python=list(PY_VERSIONS))
def lint(session: nox.Session) -> None:
    """Run formatters and linters that are safe offline."""

    session.install("ruff", "black", "isort")
    session.run("ruff", "check", ".")
    session.run("isort", "--check-only", ".")
    session.run("black", "--check", ".")


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run mypy against curated modules."""

    session.install("mypy", "types-PyYAML")
    _export_env(session)
    targets = ["src/security", "scripts/space_traversal", "src/codex_ml"]
    existing = [t for t in targets if (REPO_ROOT / t).exists()]
    if not existing:
        session.log("No targets found for mypy; skipping.")
        return
    session.run("mypy", *existing)


@nox.session(name="typecheckd", python=DEFAULT_PYTHON)
def typecheckd(session: nox.Session) -> None:
    """Incremental mypy daemon run."""

    session.install("mypy")
    _export_env(session)
    session.run("dmypy", "run", "--", "--cache-fine-grained", "src")


@nox.session(python=DEFAULT_PYTHON)
def test(session: nox.Session) -> None:
    """Fast pytest run with deterministic randomness."""

    session.install("pytest", "pytest-randomly")
    _export_env(session)
    session.env.setdefault("PYTHONHASHSEED", "0")
    session.run(
        "pytest",
        "--disable-plugin-autoload",
        "-p",
        "pytest_randomly",
        "-q",
    )


@nox.session(python=DEFAULT_PYTHON)
def cov(session: nox.Session) -> None:
    """Run coverage with HTML output and an enforced floor."""

    session.install("pytest", "pytest-cov", "pytest-randomly")
    _export_env(session)
    session.env.setdefault("PYTHONHASHSEED", "0")
    out_html = REPO_ROOT / "artifacts" / "coverage_html"
    out_html.mkdir(parents=True, exist_ok=True)
    session.run(
        "pytest",
        "--disable-plugin-autoload",
        "-p",
        "pytest_randomly",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-report=html:{out_html.as_posix()}",
        f"--cov-fail-under={DEFAULT_COVERAGE_FLOOR}",
        "-q",
    )


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """Generate API documentation with pdoc into artifacts/docs."""

    session.install("pdoc")
    _export_env(session)
    out = REPO_ROOT / "artifacts" / "docs"
    out.mkdir(parents=True, exist_ok=True)
    session.run("pdoc", "codex_ml", "-o", str(out))


@nox.session(python=DEFAULT_PYTHON)
def sec(session: nox.Session) -> None:
    """Run local security scanners."""

    session.install("bandit", "semgrep", "detect-secrets", "pip-audit")
    _export_env(session)
    if (REPO_ROOT / "src").exists():
        session.run("bandit", "-q", "-r", "src", "-c", "bandit.yaml")
    if (REPO_ROOT / "semgrep_rules").exists():
        session.run("semgrep", "scan", "--config", "semgrep_rules/", "--error", "src/")
    session.run("detect-secrets", "scan")
    if session.env.get("CODEX_AUDIT", "0") == "1":
        req = REPO_ROOT / "requirements.txt"
        if req.exists():
            session.run("pip-audit", "-r", str(req))
        else:
            session.run("pip-audit")


@nox.session
def docker_lint(session: nox.Session) -> None:
    """Run hadolint against repository Dockerfiles."""

    _export_env(session)
    from shutil import which

    if which("hadolint") is None:
        session.log("hadolint not found on PATH; skipping docker_lint.")
        return

    dockerfiles = [REPO_ROOT / "Dockerfile", REPO_ROOT / "Dockerfile.gpu"]
    found = False
    for df in dockerfiles:
        if df.exists():
            found = True
            session.run("hadolint", str(df), external=True)
    if not found:
        session.log("No Dockerfile found; skipping hadolint.")


@nox.session(name="dockerlint")
def dockerlint(session: nox.Session) -> None:
    """Compatibility alias for docker_lint."""

    session.notify("docker_lint")


@nox.session
def imagescan(session: nox.Session) -> None:
    """Run a container image scan with trivy when CODEX_AUDIT=1."""

    from shutil import which

    if os.getenv("CODEX_AUDIT", "0") != "1":
        session.log("CODEX_AUDIT!=1; skipping image scan.")
        return
    if which("trivy") is None:
        session.log("trivy not found on PATH; skipping imagescan.")
        return
    image = os.getenv("CODEX_IMAGE", "codex:local")
    session.run("trivy", "image", image, external=True)


@nox.session(name="crm_gates", python=DEFAULT_PYTHON)
def crm_gates(session: nox.Session) -> None:
    """Run CRM-focused regression suites."""

    session.install("-r", "requirements.txt")
    _export_env(session)
    session.run(
        "pytest",
        "-q",
        "tests/crm",
        "-k",
        "conversion_truths or cli or pa_reader or zaf_reader",
    )
    session.run("pytest", "-q", "tests/d365")
    session.run("pytest", "-q", "tests/archive", "-k", "not sql_identifier_safety")
    session.run("pytest", "-q", "tests/archive/test_sql_identifier_safety.py")
    session.run("pytest", "-q", "tests/release")
    session.run("pytest", "-q", "tests/diagram")
    session.run("pytest", "-q", "tests/knowledge")
    session.run("pytest", "-q", "tests/zd")


@nox.session(name="diagram_check", python=DEFAULT_PYTHON)
def diagram_check(session: nox.Session) -> None:
    """Ensure diagram helpers import and render simple flows."""

    session.install("-r", "requirements.txt")
    _export_env(session)
    session.run(
        "python",
        "-c",
        (
            "from codex.diagram import flow_to_mermaid; "
            "print(flow_to_mermaid('intake', ['Create','Triage']))"
        ),
    )
