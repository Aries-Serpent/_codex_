# Access environment defaults for coverage thresholds and lock refresh commands.
import configparser
import datetime as dt
import hashlib
import os
import shutil
import uuid
from contextlib import suppress
from importlib import metadata
from pathlib import Path
from typing import Mapping, Sequence

import nox
from nox import command

REPO_ROOT = Path(__file__).resolve().parent
PYTHON = "3.10"
UV = os.getenv("UV_BIN", "uv")
DEFAULT_COVERAGE_FLOOR_FALLBACK = 60


def _coerce_default_coverage_floor(
    raw: str | None, fallback: int = DEFAULT_COVERAGE_FLOOR_FALLBACK
) -> int:
    """Return a non-negative integer coverage floor or a safe fallback."""

    if raw is None:
        return fallback
    raw = raw.strip()
    if not raw:
        return fallback
    try:
        value = int(raw)
    except ValueError:
        return fallback
    if value < 0:
        return fallback
    return value


DEFAULT_COVERAGE_FLOOR = _coerce_default_coverage_floor(os.getenv("CODEX_COV_FLOOR"))

nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = False
nox.options.error_on_missing_interpreters = False

os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONHASHSEED", os.environ.get("PYTHONHASHSEED", "0"))
os.environ.setdefault("PYTEST_RANDOMLY_SEED", os.environ.get("PYTEST_RANDOMLY_SEED", "123"))

COVERAGE_XML = Path("artifacts/coverage.xml")
COVERAGE_HTML = Path("artifacts/coverage_html")
COVERAGE_JSON_ROOT = Path("artifacts/coverage")


def _default_fail_under() -> str:
    """Resolve the coverage floor, preferring COVERAGE_MIN when provided."""

    codex_floor = os.environ.get("CODEX_COV_FLOOR")
    if codex_floor is not None:
        try:
            value = int(codex_floor)
        except ValueError:
            pass
        else:
            if value >= 0:
                return str(value)
    for var in ("COVERAGE_MIN", "COV_FAIL_UNDER"):
        raw = os.environ.get(var)
        if raw is None:
            continue
        try:
            value = int(raw)
        except ValueError:
            continue
        if value < 0:
            continue
        return str(value)
    config_path = Path(".coveragerc")
    if config_path.is_file():
        parser = configparser.ConfigParser()
        try:
            parser.read(config_path)
            if parser.has_option("report", "fail_under"):
                value = parser.getint("report", "fail_under")
                if value >= 0:
                    return str(value)
        except (configparser.Error, ValueError):
            pass
    return str(DEFAULT_COVERAGE_FLOOR)


DEFAULT_FAIL_UNDER = _default_fail_under()
LOCKFILE = Path("requirements.lock")
UV_LOCK_FILE = Path("uv.lock")
LOCK_EXTRAS: tuple[str, ...] = ("dev", "test", "cpu", "cli", "tracking")
DEFAULT_LOCK_PYTHON = os.environ.get("NOX_LOCK_PYTHON", "3.12")
LOCK_REGEN_CMD = os.environ.get(
    "NOX_LOCK_REGEN_CMD", "NOX_ALLOW_LOCK_REFRESH=1 nox -s lock_refresh"
)
PYTEST_COV_REQUIREMENT = os.environ.get("PYTEST_COV_REQUIREMENT", "pytest-cov==7.0.0")
TORCH_REQUIREMENT = os.environ.get("NOX_TORCH_REQUIREMENT", "torch==2.8.0+cpu")
TORCH_DEFAULT_INDEX_URL = "https://download.pytorch.org/whl/cpu"

try:  # pragma: no cover - packaging is an optional runtime dependency
    from packaging.requirements import Requirement
except Exception:  # pragma: no cover - gracefully degrade if packaging missing
    Requirement = None  # type: ignore[assignment, misc]


def _torch_index_url(env: Mapping[str, str] | None = None) -> str | None:
    """Return the index URL to use when installing PyTorch."""

    source = env or os.environ
    override = source.get("NOX_TORCH_INDEX_URL")
    if override is None:
        return TORCH_DEFAULT_INDEX_URL
    override = override.strip()
    return override or None


def _parse_requirement(spec: str) -> "Requirement | None":
    if not spec:
        return None
    if Requirement is None:
        return None
    try:
        return Requirement(spec)
    except Exception:
        return None


def _torch_package_name(req: "Requirement | None", requirement: str | None = None) -> str:
    if req is not None and req.name:
        name = req.name.strip()
        if name:
            return name
    if requirement:
        head = requirement.split(";", 1)[0]
        head = head.split("==", 1)[0]
        head = head.split("[", 1)[0]
        head = head.strip()
        if head:
            return head
    return "torch"


def _version_matches(installed: str, expected: str) -> bool:
    if installed == expected:
        return True
    if expected and installed.startswith(f"{expected}+"):
        return True
    return False


def _torch_installed_version(req: "Requirement | None", requirement: str) -> str | None:
    package = _torch_package_name(req, requirement)
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        try:
            module = __import__(package)
        except Exception:
            return None
        version = getattr(module, "__version__", None)
        if isinstance(version, str) and version.strip().lower().endswith("offline"):
            return None
        return version


def _torch_requirement_satisfied(requirement: str, req: "Requirement | None" = None) -> bool:
    parsed = req or _parse_requirement(requirement)
    version = _torch_installed_version(parsed, requirement)
    if version is None:
        return False
    if parsed is None:
        if "==" in requirement:
            expected = requirement.split("==", 1)[1].strip()
            return _version_matches(version, expected)
        return True
    if parsed.marker is not None:
        try:
            if not parsed.marker.evaluate():
                return True
        except Exception:
            pass
    if parsed.specifier and version not in parsed.specifier:
        if "==" in requirement:
            expected = requirement.split("==", 1)[1].strip()
            if _version_matches(version, expected):
                return True
        return False
    return True


def _torch_offline_stub_present(session: nox.Session, module: str = "torch") -> bool:
    """Return True when the bundled offline stub for torch is installed."""

    check_script = (
        "import importlib, sys; "
        f"module = importlib.import_module({module!r}); "
        "version = getattr(module, '__version__', None); "
        "sys.exit(0 if isinstance(version, str) and version.strip().lower().endswith('offline') else 1)"
    )
    try:
        session.run("python", "-c", check_script, silent=True)
    except command.CommandFailed:
        return False
    return True


try:  # pragma: no cover - logging availability is optional
    from codex.logging.session_logger import get_session_id, log_message
except Exception:  # pragma: no cover - keep sessions usable when logging missing
    get_session_id = None  # type: ignore[assignment]
    log_message = None  # type: ignore[assignment]


def _session_id() -> str:
    if get_session_id is not None:  # type: ignore[truthy-function]
        try:
            return get_session_id()
        except Exception:  # pragma: no cover - fall back to local identifier
            pass
    sid = os.getenv("CODEX_SESSION_ID")
    if sid:
        return sid
    generated = f"nox-gate-{uuid.uuid4()}"
    os.environ.setdefault("CODEX_SESSION_ID", generated)
    return generated


def _log_gate(message: str, *, meta: dict | None = None, role: str = "system") -> None:
    if log_message is None:
        return
    try:
        log_message(_session_id(), role, message, meta=meta)
    except Exception:  # pragma: no cover - best-effort logging
        pass


def _coverage_json_destination(label: str | None = None) -> Path:
    timestamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    folder = COVERAGE_JSON_ROOT / timestamp
    if label:
        safe_label = label.replace("/", "-")
        folder = folder / safe_label
    path = folder / "coverage.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _record_coverage_artifact(path: Path) -> None:
    if not path.exists():
        _log_gate(
            "coverage artifact missing",
            meta={"artifact": str(path), "source": "noxfile.py", "available": False},
            role="WARN",
        )
        return
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        size = path.stat().st_size
    except Exception as exc:  # pragma: no cover - hashing failures shouldn't halt gate
        _log_gate(
            "coverage artifact hashing failed",
            meta={"artifact": str(path), "error": repr(exc), "source": "noxfile.py"},
            role="WARN",
        )
        return
    _log_gate(
        "coverage artifact generated",
        meta={
            "artifact": str(path),
            "sha256": digest,
            "bytes": size,
            "source": "noxfile.py",
        },
    )


@nox.session
def ci_local(session):
    # Install core extras and then ensure torch is available via the CPU wheel index so
    # training-related tests execute locally instead of skipping or failing early.
    session.install("-e", ".[dev,test,cli,tracking]")
    _ensure_torch(session)
    json_path = _coverage_json_destination("ci_local")
    cmd = ["pytest", "-q"]
    cmd += _coverage_args(
        session,
        fail_under=DEFAULT_FAIL_UNDER,
        json_report=json_path,
    )
    session.run(*cmd)
    session.run("coverage", "report", f"--fail-under={DEFAULT_FAIL_UNDER}")
    _record_coverage_artifact(json_path)


# Optional: prefer `uv`, with automatic fallback to `virtualenv` if uv is unavailable.
# Enable by exporting NOX_PREFER_UV=1 on runners where uv is ubiquitous.
if os.environ.get("NOX_PREFER_UV") == "1":
    # Allows "uv|virtualenv" fallback selection (first available is used).
    nox.options.default_venv_backend = (
        "uv|virtualenv"  # also settable via CLI/env. :contentReference[oaicite:15]{index=15}
    )


def _has_uv(session: nox.Session) -> bool:
    """Detect if `uv` is available on PATH."""
    with suppress(Exception):
        session.run("uv", "--version", external=True, silent=True)
        return True
    return False


def _install(session: nox.Session, *pkgs: str) -> None:
    """
    Fast path: use `uv pip install` when available (very fast resolver/installer).
    Fallback: use session.install(...) which uses pip inside the venv.
    For sessions running without a virtual environment (venv_backend="none"),
    install directly into the interpreter via `python -m pip install`.
    """
    if (
        getattr(session, "venv_backend", None) == "none"
        or getattr(session, "virtualenv", None) is None
    ):
        session.run("python", "-m", "pip", "install", *pkgs, external=True)
        return
    if _has_uv(session):
        session.run("uv", "pip", "install", *pkgs, external=True)
    else:
        session.install(*pkgs)


def _ensure_torch(session: nox.Session) -> None:
    """Install PyTorch from the configured CPU wheel index when missing."""

    requirement = TORCH_REQUIREMENT
    parsed_requirement = _parse_requirement(requirement)
    if parsed_requirement is not None and parsed_requirement.marker is not None:
        try:
            if not parsed_requirement.marker.evaluate():
                return
        except Exception:
            pass
    torch_available = _module_available(session, "torch")
    if torch_available and _torch_requirement_satisfied(requirement, parsed_requirement):
        return
    if torch_available and _torch_offline_stub_present(session, "torch"):
        session.log(
            "torch stub detected (0.0.0-offline); continuing without strict version enforcement"
        )
        return
    _ensure_pip_cache(session)
    index_url = _torch_index_url(session.env)
    if _has_uv(session):
        cmd = ["uv", "pip", "install"]
        if index_url:
            cmd.extend(["--index-url", index_url])
        cmd.append(requirement)
        session.run(*cmd, external=True)
    else:
        cmd = ["python", "-m", "pip", "install"]
        if index_url:
            cmd.extend(["--index-url", index_url])
        cmd.append(requirement)
        session.run(*cmd)
    if not _module_available(session, "torch"):
        session.error(
            "PyTorch is required for ci_local but could not be installed. "
            "Set NOX_TORCH_INDEX_URL to a reachable index or install torch manually."
        )
    if not _torch_requirement_satisfied(requirement, parsed_requirement):
        installed = _torch_installed_version(parsed_requirement, requirement)
        expected = ""
        if "==" in requirement:
            expected = requirement.split("==", 1)[1].strip()
        if expected and installed and _version_matches(installed, expected):
            return
        try:
            module = __import__(_torch_package_name(parsed_requirement, requirement))
        except Exception:
            module_version = None
        else:
            module_version = getattr(module, "__version__", None)
        if isinstance(module_version, str) and module_version.strip().lower().endswith("offline"):
            session.log(
                "torch stub detected (0.0.0-offline); continuing without strict version enforcement"
            )
            return
        installed_display = installed or module_version or "unknown"
        session.error(
            "PyTorch installation does not satisfy the pinned requirement. "
            f"Expected `{requirement}`, found `{installed_display}`."
        )


def _selected_lock_extras() -> tuple[str, ...]:
    extras_env = os.environ.get("NOX_LOCK_EXTRAS")
    if extras_env:
        extras = tuple(e.strip() for e in extras_env.split(",") if e.strip())
        if extras:
            return extras
    return LOCK_EXTRAS


def _sync_lockfile(session: nox.Session, lockfile: Path = LOCKFILE) -> None:
    """Install dependencies exactly as pinned in the requirements lock file."""

    if not lockfile.exists():
        session.error(
            f"{lockfile} is missing; regenerate it with `{LOCK_REGEN_CMD}` before syncing."
        )
    _ensure_pip_cache(session)
    if _has_uv(session):
        session.run("uv", "pip", "sync", str(lockfile), external=True)
    else:
        session.install("-r", str(lockfile))


def _annotate_lockfile(lockfile: Path, *, python_version: str) -> None:
    """Ensure the lockfile header documents the Python target and refresh command."""

    try:
        lines = lockfile.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return

    header_end = 0
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("#"):
            header_end = idx + 1
            continue
        header_end = idx
        break
    else:
        header_end = len(lines)

    metadata = [
        f"# Python lock target: CPython {python_version}",
        f"# Regenerate with: {LOCK_REGEN_CMD}",
    ]

    header = [
        line
        for line in lines[:header_end]
        if not line.lower().startswith("# python lock target")
        and not line.lower().startswith("# regenerate with:")
    ]

    updated_lines = header + metadata + lines[header_end:]

    if updated_lines != lines:
        lockfile.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _compile_lockfile(session: nox.Session, *, python_version: str) -> None:
    """Regenerate requirements.lock from pyproject metadata."""

    extras = _selected_lock_extras()

    if _has_uv(session):
        cmd = [
            "uv",
            "pip",
            "compile",
            "pyproject.toml",
            "--output-file",
            str(LOCKFILE),
        ]
        for extra in extras:
            cmd.extend(["--extra", extra])
        if python_version:
            cmd.extend(["--python-version", python_version])
        session.run(*cmd, external=True)
    else:
        _ensure_pip_cache(session)
        _install(session, "pip-tools>=7.4")
        cmd = [
            "pip-compile",
            "pyproject.toml",
            "--output-file",
            str(LOCKFILE),
        ]
        for extra in extras:
            cmd.extend(["--extra", extra])
        if python_version:
            cmd.extend(["--python-version", python_version])
        session.run(*cmd)

    _annotate_lockfile(LOCKFILE, python_version=python_version)


@nox.session(name="bootstrap", python=PYTHON)
def bootstrap(session: nox.Session) -> None:
    """Create or refresh a universal requirements lock using uv, then sync the environment."""

    _ensure_pip_cache(session)
    session.install("uv")
    requirements_in = REPO_ROOT / "requirements.in"
    source = requirements_in if requirements_in.exists() else REPO_ROOT / "pyproject.toml"
    session.run(
        UV,
        "pip",
        "compile",
        str(source),
        "--universal",
        "-o",
        "requirements.txt",
        external=True,
    )
    session.run(UV, "pip", "sync", "requirements.txt", external=True)


def _ensure_pip_cache(session: nox.Session) -> None:
    """Default PIP_CACHE_DIR for faster, repeatable installs."""
    session.env.setdefault("PIP_CACHE_DIR", str(Path(".cache/pip").resolve()))
    session.env.setdefault(
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
        os.environ.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1"),
    )
    session.env.setdefault("PYTHONUTF8", os.environ.get("PYTHONUTF8", "1"))
    session.env.setdefault("PYTHONHASHSEED", os.environ.get("PYTHONHASHSEED", "0"))
    session.env.setdefault("PYTEST_RANDOMLY_SEED", os.environ.get("PYTEST_RANDOMLY_SEED", "42"))


def _module_available(session: nox.Session, name: str, *, external: bool = False) -> bool:
    """Return True if `import name` succeeds in the target interpreter."""
    try:
        session.run("python", "-c", f"import {name}", external=external, silent=True)
        return True
    except Exception:
        return False


def _coverage_args(
    session: nox.Session,
    *,
    fail_under: str | None = None,
    branch: bool = False,
    external: bool = False,
    paths: Sequence[str] | None = ("src",),
    json_report: Path | None = None,
) -> list[str]:
    """Return pytest coverage flags, erroring if pytest-cov is unavailable."""
    if not _module_available(session, "pytest_cov", external=external):
        session.error(
            f"pytest-cov is required; install {PYTEST_COV_REQUIREMENT} before running gates."
        )
    args = [f"--cov={p}" for p in (paths or [])] or ["--cov"]
    if branch:
        args.append("--cov-branch")
    args.append("--cov-report=term-missing")
    if json_report is not None:
        args.append(f"--cov-report=json:{json_report}")
    args.append(f"--cov-report=xml:{COVERAGE_XML}")
    if fail_under is not None:
        args.append(f"--cov-fail-under={fail_under}")
    return args


@nox.session
def lock_sanity(session):
    """Install from requirements.lock and validate the environment."""

    _sync_lockfile(session)
    session.run("python", "-m", "pip", "check")
    session.run(
        "python",
        "-c",
        "import accelerate, transformers, pytest; print('lockfile import check ok')",
    )


@nox.session
def lock_refresh(session):
    """Regenerate requirements.lock (requires explicit opt-in for network access)."""

    if os.environ.get("NOX_ALLOW_LOCK_REFRESH") != "1":
        session.error("Set NOX_ALLOW_LOCK_REFRESH=1 to regenerate the lockfile (network required).")

    python_version = session.posargs[0] if session.posargs else DEFAULT_LOCK_PYTHON
    extras_display = ", ".join(_selected_lock_extras())
    session.log(
        f"Refreshing requirements.lock for Python {python_version} with extras: {extras_display}"
    )
    _compile_lockfile(session, python_version=python_version)


@nox.session
def lint(session):
    _ensure_pip_cache(session)
    packages = ["ruff", "vulture"]
    config_path = REPO_ROOT / ".importlinter"
    if config_path.exists():
        packages.append("import-linter")
    _install(session, *packages)
    session.run("ruff", "format", ".")
    session.run("ruff", "check", "--fix", "src", "tests", "scripts")
    if config_path.exists():
        session.run("lint-imports", external=True)
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        session.run(
            "vulture",
            str(src_dir),
            "--min-confidence",
            "80",
            success_codes=[0, 1],
        )


@nox.session
def typecheck(session):
    _ensure_pip_cache(session)
    _install(session, "mypy")
    try:
        session.run("mypy", "src")
    except Exception:
        session.log("mypy not configured — skipping")


@nox.session(name="typecheckd", python=PYTHON)
def typecheckd(session: nox.Session) -> None:
    """Incremental mypy via daemon when available."""

    _ensure_pip_cache(session)
    _install(session, "mypy")
    try:
        session.run("dmypy", "run", "--", "--cache-fine-grained", "src")
    except Exception:
        session.log("dmypy unavailable — skipping incremental type checking")


@nox.session
def ci(session):
    """Run linting, type checks, and test coverage."""
    session.notify("lock_sanity")
    session.notify("lint")
    session.notify("typecheck")
    session.notify("coverage")


@nox.session
def quality(session):
    """Run formatting hooks and tests locally."""
    _install(
        session,
        "pre-commit",
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "pytest-asyncio",
        "hypothesis",
    )
    session.run("pre-commit", "run", "--all-files")
    json_path = _coverage_json_destination("quality")
    cmd = ["pytest", "-q"]
    cmd += _coverage_args(
        session,
        fail_under=DEFAULT_FAIL_UNDER,
        json_report=json_path,
    )
    session.run(*cmd)
    session.run("coverage", "report", f"--fail-under={DEFAULT_FAIL_UNDER}")
    session.run("coverage", "xml", f"-o={COVERAGE_XML}")
    session.run("coverage", "html", f"-d={COVERAGE_HTML}")
    _record_coverage_artifact(json_path)


@nox.session(python=PYTHON)
def test(session: nox.Session) -> None:
    """Fast pytest run with deterministic ordering."""

    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-randomly")
    cmd = ["pytest", "--disable-plugin-autoload", "-q"]
    if session.posargs:
        cmd.extend(session.posargs)
    session.run(*cmd)


@nox.session(python=PYTHON)
def cov(session: nox.Session) -> None:
    """Coverage run with branch data and HTML artifacts."""

    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-cov")
    COVERAGE_HTML.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pytest",
        "--disable-plugin-autoload",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-report=html:{COVERAGE_HTML.as_posix()}",
        f"--cov-fail-under={DEFAULT_FAIL_UNDER}",
        "-q",
    ]
    if session.posargs:
        cmd.extend(session.posargs)
    session.run(*cmd)


@nox.session
def coverage(session):
    _ensure_pip_cache(session)
    # Default to CPU-only wheels for coverage unless explicitly overridden.
    # _ensure_torch() will respect NOX_TORCH_INDEX_URL when present.
    session.env.setdefault("NOX_TORCH_INDEX_URL", "https://download.pytorch.org/whl/cpu")
    _ensure_torch(session)
    _install(
        session,
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "pytest-asyncio",
        "hypothesis",
    )
    # Hard fail if pytest-cov failed to install even though pip returned success.
    session.run(
        "python",
        "-c",
        "import pytest, pytest_cov; print(pytest.__version__)",
        silent=True,
    )
    _install(session, "-e", ".[test,cli]")
    _install(session, "numpy")
    try:
        session.run(
            "python",
            "-c",
            "import hydra; hydra._ensure_hydra_extra()",
            silent=True,
        )
    except command.CommandFailed:
        session.error(
            "hydra.extra plugin unavailable — install Codex test extras before running coverage gates"
        )
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_HTML.mkdir(parents=True, exist_ok=True)
    json_path = _coverage_json_destination("coverage")
    cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
    cmd += _coverage_args(
        session,
        fail_under=DEFAULT_FAIL_UNDER,
        branch=True,
        json_report=json_path,
    )
    if session.posargs:
        cmd.extend(session.posargs)
    session.run(*cmd)
    session.run("coverage", "report", f"--fail-under={DEFAULT_FAIL_UNDER}")
    session.run("coverage", "xml", f"-o={COVERAGE_XML}")
    session.run("coverage", "html", f"-d={COVERAGE_HTML}")
    _record_coverage_artifact(json_path)


@nox.session
def tests(session):
    """
    Thin wrapper to keep one source of truth:
    `nox -s tests` simply delegates to the 'coverage' gate.
    """
    session.notify("coverage")


@nox.session
def fence_tests(session):
    """Run the lightweight fence validator test suite offline."""
    _install(session, "pytest", "pytest-randomly", "pytest-asyncio")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if session.posargs:
        cmd = ["pytest", "-q", *session.posargs]
    else:
        cmd = [
            "pytest",
            "-q",
            "tests/tools/test_validate_fences.py",
            "tests/test_fences_tool.py",
        ]
    session.run(*cmd)


@nox.session(venv_backend="none")  # run directly in the current interpreter; no venv
def tests_sys(session):
    """
    Run tests in the *Codex initial* environment for minimal overhead.
    Preferred order for determinism:
      1) If pyproject.toml + uv.lock exist and uv is available AND NOX_PREFER_UV=1:
         use `uv sync --frozen` (strict lockfile).
      2) Else, if UV_SYNC_FILE (or requirements.txt) exists and uv is available AND NOX_PREFER_UV=1:
         use `uv pip sync <file>` (idempotent).
      3) Else: minimally ensure pytest deps with pip/uv and run tests.
    """
    _ensure_pip_cache(session)
    prefer_uv = os.environ.get("NOX_PREFER_UV") == "1" and _has_uv(session)
    has_pyproject = Path("pyproject.toml").is_file()
    has_uv_lock = UV_LOCK_FILE.is_file()
    # 1) Strongest determinism: project lock
    if prefer_uv and has_pyproject and has_uv_lock:
        # Strictly use the lockfile as the source of truth and do not update it
        session.run("uv", "sync", "--frozen", external=True)
    else:
        # 2) Next best: requirements sync (idempotent)
        sync_target = os.environ.get("UV_SYNC_FILE") or (
            "requirements.txt" if Path("requirements.txt").is_file() else None
        )
        if prefer_uv and sync_target and Path(sync_target).is_file():
            session.run("uv", "pip", "sync", sync_target, external=True)
        else:
            # Fall back to installing minimal deps if pytest isn't available.
            try:
                session.run("pytest", "--version", external=True)
            except Exception:
                # Install basics quickly via pip so the system interpreter can import them.
                session.run(
                    "python",
                    "-m",
                    "pip",
                    "install",
                    "pytest",
                    "pytest-randomly",
                    "pytest-asyncio",
                    "hypothesis",
                    PYTEST_COV_REQUIREMENT,
                    external=True,
                )
            else:
                # pytest is present but pytest-cov might not be; install it on demand.
                if not _module_available(session, "pytest_cov", external=True):
                    session.run(
                        "python",
                        "-m",
                        "pip",
                        "install",
                        PYTEST_COV_REQUIREMENT,
                        external=True,
                    )
                if not _module_available(session, "pytest_randomly", external=True):
                    session.run(
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "pytest-randomly",
                        external=True,
                    )
                if not _module_available(session, "pytest_asyncio", external=True):
                    session.run(
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "pytest-asyncio",
                        external=True,
                    )
                if not _module_available(session, "hypothesis", external=True):
                    session.run(
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "hypothesis",
                        external=True,
                    )
    # Now run tests from the system env (no venv).
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    json_path = _coverage_json_destination("tests_sys")
    cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
    cmd += _coverage_args(
        session,
        fail_under=DEFAULT_FAIL_UNDER,
        branch=True,
        external=True,
        json_report=json_path,
    )
    if session.posargs:
        cmd.extend(session.posargs)
    session.run(*cmd, external=True)
    _record_coverage_artifact(json_path)


@nox.session
def build(session):
    """Produce reproducible wheel and sdist artifacts."""

    _ensure_pip_cache(session)
    session.install("build", "setuptools-reproducible")
    session.env.setdefault("SOURCE_DATE_EPOCH", "1700000000")
    session.run("python", "-m", "build", "--wheel", "--sdist", external=True)


@nox.session(reuse_venv=False)
def package(session):
    """Build wheel/sdist artifacts and validate an installation."""

    _ensure_pip_cache(session)
    build_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    _install(session, "build")
    session.run("python", "-m", "build", "--wheel", "--sdist")
    artifacts = sorted(build_dir.iterdir())
    if not artifacts:
        session.error("No distribution artifacts were produced")

    wheels = [p for p in artifacts if p.suffix == ".whl"]
    sdists = [p for p in artifacts if p.name.endswith(".tar.gz") or p.suffix == ".zip"]
    if not wheels:
        session.error("Wheel artifact was not produced")
    if not sdists:
        session.error("Source distribution artifact was not produced")

    install_queue = wheels + sdists
    for index, artifact in enumerate(install_queue):
        session.run("python", "-m", "pip", "install", "--no-deps", str(artifact))
        session.run(
            "python",
            "-c",
            (
                "import codex, codex_ml; "
                "print(f'codex={codex.__version__}, codex_ml={codex_ml.__version__}')"
            ),
        )
        session.run("codex-ml-cli", "--version")
        if index < len(install_queue) - 1:
            session.run("python", "-m", "pip", "uninstall", "codex", "-y")


@nox.session
def tests_ssp(session):
    session.install(
        "-e",
        ".",
        "sentencepiece>=0.1.99",
        "pytest",
        "pytest-cov",
        "pytest-randomly",
        "pytest-asyncio",
        "hypothesis",
    )
    session.env["PYTEST_ADDOPTS"] = ""
    session.run("pytest", "-q", "tests/tokenization", "-k", "sentencepiece")


@nox.session
def tests_min(session):
    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-randomly", "pytest-asyncio")
    session.run("pytest", "-q", "-m", "not slow")


@nox.session
def coverage_html(session):
    """Emit local coverage reports (HTML + XML) without hitting CI or remote services."""

    _ensure_pip_cache(session)
    session.install("-r", "requirements-dev.txt")
    COVERAGE_XML.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_HTML.mkdir(parents=True, exist_ok=True)
    session.run(
        "pytest",
        "--disable-plugin-autoload",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        f"--cov-report=xml:{COVERAGE_XML.as_posix()}",
        f"--cov-report=html:{COVERAGE_HTML.as_posix()}",
        f"--cov-fail-under={DEFAULT_FAIL_UNDER}",
        "-q",
    )


@nox.session
def perf_smoke(session):
    _ensure_pip_cache(session)
    _install(session, "pytest", "pytest-cov", "pytest-randomly", "pytest-asyncio")
    session.run("pytest", "-q", "tests/perf/test_perf_smoke.py", "--no-cov")


@nox.session
def codex_gate(session):
    session.install(
        "pytest",
        "pytest-randomly",
        "charset-normalizer>=3.0.0",
        "chardet>=5.0.0",
    )
    session.run(
        "pytest",
        "-q",
        "tests/test_ingestion_encodings_matrix.py",
        "tests/test_ingestion_auto_encoding.py",
        "tests/test_ingestion_encoding_coverage.py",
        "tests/test_sqlite_pool_close.py",
        "tests/test_chat_session_exit.py",
    )


@nox.session
def codex_ext(session):
    session.install(
        "pytest",
        "pytest-randomly",
        "charset-normalizer>=3.0.0",
        "chardet>=5.0.0",
    )
    session.install("-r", "requirements.txt")
    session.run(
        "pytest",
        "-q",
        "--no-cov",
        "tests/test_checkpoint_manager.py",
        "tests/test_eval_runner.py",
    )


@nox.session(python=PYTHON)
def sec(session: nox.Session) -> None:
    """Local security checks (no network by default; pip-audit gated)."""

    _ensure_pip_cache(session)
    _install(session, "bandit", "semgrep", "detect-secrets", "pip-audit")
    src_path = REPO_ROOT / "src"
    if src_path.exists():
        session.run("bandit", "-q", "-r", "src", "-c", "bandit.yaml", external=True)
    rules_path = REPO_ROOT / "semgrep_rules"
    if rules_path.exists():
        session.run(
            "semgrep", "scan", "--config", "semgrep_rules/", "--error", "src/", external=True
        )
    session.run("detect-secrets", "scan", external=True)
    if session.env.get("CODEX_AUDIT", "0") == "1":
        requirements = REPO_ROOT / "requirements.txt"
        if requirements.exists():
            session.run("pip-audit", "-r", str(requirements), external=True)
        else:
            session.run("pip-audit", external=True)


@nox.session(name="sec_scan")
def sec_scan(session):
    """Compatibility alias for the legacy sec_scan session."""

    session.notify("sec")


@nox.session(python=PYTHON)
def docs(session: nox.Session) -> None:
    """Generate offline API documentation with pdoc (artifacts/docs)."""

    _ensure_pip_cache(session)
    _install(session, "pdoc")
    output = REPO_ROOT / "artifacts" / "docs"
    output.mkdir(parents=True, exist_ok=True)
    # Use the package name to allow pdoc to resolve imports properly
    session.run("pdoc", "codex_ml", "-o", str(output), external=True)


@nox.session
def deadcode(session):
    """Scan for unused code with vulture."""

    _ensure_pip_cache(session)
    session.install("vulture")
    session.run("vulture", "src", "scripts", "--min-confidence", "80", external=True)


@nox.session
def spellcheck(session):
    """Run codespell against source and documentation."""

    _ensure_pip_cache(session)
    session.install("codespell")
    session.run("codespell", "src", "docs", "scripts", external=True)


@nox.session
def docs_smoke(session):
    _ensure_pip_cache(session)
    _install(session, "nbformat")
    session.run(
        "python",
        "-c",
        "import nbformat; nbformat.read('notebooks/quick_start.ipynb', as_version=4)",
    )
    session.run(
        "python",
        "-c",
        (
            "from pathlib import Path,sys,re;"
            "arch=Path('docs/architecture.md').read_text(encoding='utf-8');"
            "assert '```mermaid' in arch;"
            "readme=Path('README.md').read_text(encoding='utf-8');"
            "missing=[p for p in re.findall(r'\\[(?:[^\\]]+)\\]\\((docs/[^)]+)\\)', readme) if not Path(p).exists()];"
            "sys.exit('Missing docs: '+', '.join(missing)) if missing else None"
        ),
    )


@nox.session
def metrics(session):
    _ensure_pip_cache(session)
    session.install("-r", "requirements-dev.txt")
    session.install("nbformat")
    session.run("python", "tools/metrics/generate_repo_metrics.py")


@nox.session(python=PYTHON)
def licenses(session: nox.Session) -> None:
    """Generate THIRD_PARTY_NOTICES.md using pip-licenses."""

    _ensure_pip_cache(session)
    (REPO_ROOT / "artifacts" / "licenses").mkdir(parents=True, exist_ok=True)
    session.run("bash", "scripts/security/licenses.sh")


@nox.session
def docs_audit(session):
    _ensure_pip_cache(session)
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/docs/scan_links.py")


@nox.session
def nb_check(session):
    _ensure_pip_cache(session)
    session.install("nbformat")
    session.run("python", "tools/notebooks/check_load.py")


@nox.session(name="ops_smoke")
def ops_smoke(session):
    """Run ops dry-run tests without network. Skips heavy deps by default."""

    session.install("-e", ".[test]")
    session.run("pytest", "-q", "tests/ops/test_codex_mint_tokens_contract.py")


@nox.session(name="ops_contract")
def ops_contract(session):
    """Offline contract tests for token scoping/revoke using monkeypatch mocks."""

    session.install("-e", ".[test,ops]")
    session.run("pytest", "-q", "tests/ops/test_codex_mint_tokens_contract.py")


@nox.session
def conventional(session):
    """Check recent commits for Conventional Commit compliance."""

    _ensure_pip_cache(session)
    session.install("commitizen")
    session.run("cz", "check", "--rev-range", "HEAD~10..HEAD", external=True)


@nox.session
def docker_lint(session):
    """Run hadolint against available Dockerfiles (requires hadolint on PATH)."""

    if shutil.which("hadolint") is None:
        session.log("hadolint not found on PATH; skipping docker_lint.")
        return
    dockerfiles = [REPO_ROOT / "Dockerfile", REPO_ROOT / "Dockerfile.gpu"]
    found = False
    for dockerfile in dockerfiles:
        if dockerfile.exists():
            found = True
            session.run("hadolint", str(dockerfile), external=True)
    if not found:
        session.log("No Dockerfile found; skipping hadolint.")


@nox.session(name="dockerlint")
def dockerlint(session):
    """Compatibility alias for docker_lint."""

    session.notify("docker_lint")


@nox.session
def imagescan(session):
    """Trivy image scan (optional; gate by CODEX_AUDIT=1)."""

    if os.getenv("CODEX_AUDIT", "0") != "1":
        session.log("CODEX_AUDIT!=1; skipping image scan.")
        return
    if shutil.which("trivy") is None:
        session.log("trivy not found on PATH; skipping imagescan.")
        return
    image = os.getenv("CODEX_IMAGE", "codex:local")
    session.run("trivy", "image", image, external=True)


@nox.session(name="docker_scan")
def docker_scan(session):
    """Compatibility alias for the legacy docker_scan session."""

    session.notify("imagescan")
