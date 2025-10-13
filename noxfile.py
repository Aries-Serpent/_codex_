from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import nox  # type: ignore

from codex_ml.utils.optional import optional_import

REPO_ROOT = Path(__file__).resolve().parent
PYTHON_VERSIONS = ("3.12", "3.11", "3.10")
PYTHON = [*PYTHON_VERSIONS]


def _select_python() -> str:
    override = os.getenv("CODEX_NOX_PYTHON")
    if override:
        return override
    for candidate in PYTHON_VERSIONS:
        if shutil.which(f"python{candidate}"):
            return candidate
    return f"{sys.version_info.major}.{sys.version_info.minor}"


DEFAULT_PYTHON = _select_python()
DEFAULT_COVERAGE_FLOOR = int(os.getenv("CODEX_COV_FLOOR", "85"))
UV = os.getenv("UV_BIN", "uv")
OFFLINE_TEST_TARGETS = (
    "tests/unit/test_zendesk_models.py",
    "tests/e2e_offline/test_diff_and_apply.py",
)

_torch, _HAS_TORCH = optional_import("torch")

nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = False
nox.options.error_on_missing_interpreters = False


def _export_env(session: nox.Session) -> None:
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.env.setdefault("PYTHONUTF8", "1")


@nox.session(name="tests_offline", python=DEFAULT_PYTHON)
def tests_offline(session: nox.Session) -> None:
    """Run unit and offline e2e tests with minimal dependencies."""
    session.install("pytest", "pydantic")
    _export_env(session)
    session.run("pytest", "-q", *OFFLINE_TEST_TARGETS)


@nox.session(name="tests", python=PYTHON)
def tests(session: nox.Session) -> None:
    """Offline pytest session for Zendesk modules."""

    session.run("python", "-m", "pip", "install", "--upgrade", "pip", silent=True)
    session.install("pytest", "pydantic")
    _export_env(session)
    session.run("pytest", "-q", *OFFLINE_TEST_TARGETS)


@nox.session(name="tests_gpu", python=DEFAULT_PYTHON)
def tests_gpu(session: nox.Session) -> None:
    """Run GPU-marked tests when CUDA devices are available."""

    if not (
        _HAS_TORCH and _torch is not None and getattr(_torch.cuda, "is_available", lambda: False)()
    ):
        session.log("CUDA is unavailable; skipping GPU test session.")
        return

    session.install("pytest", "pytest-randomly")
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
    """Create/refresh lock then sync env locally (uv)."""
    _export_env(session)
    session.install("uv")
    # Compile universal lock from pyproject or requirements.in
    # --universal produces a platform-independent lock
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
    # Sync current venv to lockfile (offline after warm cache)
    session.run(UV, "pip", "sync", "requirements.txt")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Ruff format + lint (single tool), import-linter contracts, dead-code sweep."""
    session.install("ruff", "import-linter", "vulture")
    _export_env(session)
    session.run("ruff", "format", ".")
    session.run("ruff", "check", "--fix", "src", "tests", "scripts")
    # Architectural contracts (optional)
    if (REPO_ROOT / ".importlinter").exists():
        session.run("lint-imports")
    # Dead code sweep (non-fatal)
    if (REPO_ROOT / "src").exists():
        session.run("vulture", "src", "--min-confidence", "80", success_codes=[0, 1])


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """mypy on curated modules (fast)."""
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
    """Incremental mypy via daemon."""
    session.install("mypy")
    _export_env(session)
    # Start or reuse daemon; run fine-grained cache
    session.run("dmypy", "run", "--", "--cache-fine-grained", "src")


@nox.session(python=DEFAULT_PYTHON)
def test(session: nox.Session) -> None:
    """Fast pytest run (deterministic + randomized order)."""
    session.install("pytest", "pytest-randomly")
    _export_env(session)
    # Make hash randomization explicit and reproducible
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
    """Coverage run with branch coverage, floor, and HTML report."""
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
    """Generate offline API documentation with pdoc (artifacts/docs)."""
    session.install("pdoc")
    _export_env(session)
    out = REPO_ROOT / "artifacts" / "docs"
    out.mkdir(parents=True, exist_ok=True)
    # Use the package name to allow pdoc to resolve imports properly
    session.run("pdoc", "codex_ml", "-o", str(out))


@nox.session(python=DEFAULT_PYTHON)
def sec(session: nox.Session) -> None:
    """Local security checks (no network by default; pip-audit gated)."""
    session.install("bandit", "semgrep", "detect-secrets", "pip-audit")
    _export_env(session)
    # Bandit (Python SAST)
    if (REPO_ROOT / "src").exists():
        session.run("bandit", "-q", "-r", "src", "-c", "bandit.yaml")
    # Semgrep (local rules)
    if (REPO_ROOT / "semgrep_rules").exists():
        session.run("semgrep", "scan", "--config", "semgrep_rules/", "--error", "src/")
    # detect-secrets (scan, do not baseline update)
    session.run("detect-secrets", "scan")
    # pip-audit (optional; may use network)
    if session.env.get("CODEX_AUDIT", "0") == "1":
        req = REPO_ROOT / "requirements.txt"
        if req.exists():
            session.run("pip-audit", "-r", str(req))
        else:
            session.run("pip-audit")


@nox.session
def docker_lint(session: nox.Session) -> None:
    """Run hadolint against available Dockerfiles (requires hadolint in PATH)."""
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
    """Alias to docker_lint for compatibility with older docs."""

    session.notify("docker_lint")


@nox.session
def imagescan(session: nox.Session) -> None:
    """Trivy image scan (optional; gate by CODEX_AUDIT=1)."""

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
    """Run Codex CRM focused tests."""

    session.install("-r", "requirements.txt")
    _export_env(session)
    session.run("pytest", "-q", "tests/crm")
