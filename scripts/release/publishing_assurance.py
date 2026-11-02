#!/usr/bin/env python3
"""Publishing assurance helpers for PyPI release automation."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.machinery
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import venv
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from email.parser import Parser
from pathlib import Path, PurePosixPath
from typing import Any

_DIST_NAME_RE = re.compile(r"[-_.]+")
_SDIST_SUFFIXES = (".tar.gz", ".zip")
_BYTECODE_SUFFIXES = (".pyc", ".pyo", ".pyd")
_ORIGINS = {"pypi": "https://pypi.org", "testpypi": "https://test.pypi.org"}
_IMPORT_NAMES = {
    "codex-ml": "codex_ml",
    "codex-cognitive-sdk": "codex_cognitive_sdk",
    "codex-contracts": "codex_contracts",
    "codex-ml-evaluation": "codex_evaluation",
    "codex-ml-lora": "codex_lora",
    "codex-ml-telemetry": "codex_ml_telemetry",
}
_HTTP_TIMEOUT = 30
_MAX_INDEX_BYTES = 2 * 1024 * 1024
_PUBLIC_CHECKS = {
    "codex-ml": (
        "from codex_ml.api import RagAPI; "
        "api = RagAPI(); api.index([{'id': 'release', 'content': 'artifact assurance'}]); "
        "assert api.query('artifact')[0]['id'] == 'release'"
    ),
    "codex-cognitive-sdk": (
        "from codex_cognitive_sdk import SignalEvidence, SignalSource, make_event_id; "
        "signal = SignalEvidence(SignalSource.MANUAL, 'release', '2026-01-01T00:00:00Z'); "
        "key = make_event_id('release/repo', 'abc', signal, None, None); "
        "assert len(key) == 16 and key == make_event_id('release/repo', 'abc', signal, None, None)"
    ),
    "codex-contracts": (
        "from codex_contracts import EventEnvelope; "
        "event = EventEnvelope(kind='release', source='assurance', payload={'checked': True}); "
        "assert EventEnvelope.from_json(event.to_json()).to_dict() == event.to_dict()"
    ),
    "codex-ml-evaluation": (
        "from codex_evaluation import DriftBatch, PopulationStabilityIndex; "
        "report = PopulationStabilityIndex().evaluate(DriftBatch([1, 2], [1, 2])); "
        "assert report.score == 0 and not report.drifted"
    ),
    "codex-ml-lora": (
        "from codex_lora import LoraConfig; "
        "assert LoraConfig(rank=4, alpha=8).as_backend_kwargs()['r'] == 4"
    ),
    "codex-ml-telemetry": (
        "from codex_ml_telemetry import HealthReport, HealthStatus; "
        "assert HealthReport(HealthStatus.HEALTHY).to_dict()['status'] == 'healthy'"
    ),
}


@dataclass(frozen=True)
class DistributionArtifacts:
    """Resolved distribution artifacts for a single build output."""

    distribution: str
    version: str
    wheel_path: Path
    sdist_path: Path
    metadata_name: str


def normalize_distribution_name(name: str) -> str:
    """Normalize a package name using PEP 503-compatible rules."""

    return _DIST_NAME_RE.sub("-", name).lower()


def _strip_tag_ref(tag: str) -> str:
    return tag.removeprefix("refs/tags/")


def _find_single_file(paths: list[Path], *, kind: str, root: Path) -> Path:
    if not paths:
        raise ValueError(f"expected exactly one {kind} under {root}, found none")
    if len(paths) != 1:
        rel_paths = [path.relative_to(root).as_posix() for path in paths]
        raise ValueError(
            f"expected exactly one {kind} under {root}, found {len(paths)}: {rel_paths}"
        )
    return paths[0]


def _parse_wheel_metadata(wheel_path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(wheel_path) as wheel_zip:
        metadata_candidates = [
            name for name in wheel_zip.namelist() if name.endswith(".dist-info/METADATA")
        ]
        metadata_path = _find_single_string(
            metadata_candidates,
            kind="wheel metadata",
            root=wheel_path,
        )
        metadata = Parser().parsestr(wheel_zip.read(metadata_path).decode("utf-8"))
    name = metadata.get("Name")
    version = metadata.get("Version")
    if not name or not version:
        raise ValueError(f"{wheel_path} is missing Name/Version metadata")
    return name, version


def _find_single_string(values: list[str], *, kind: str, root: Path) -> str:
    if not values:
        raise ValueError(f"expected exactly one {kind} entry in {root}, found none")
    if len(values) != 1:
        raise ValueError(f"expected exactly one {kind} entry in {root}, found {values}")
    return values[0]


def _parse_sdist_name(path: Path, version: str) -> str:
    file_name = path.name
    for suffix in _SDIST_SUFFIXES:
        if file_name.endswith(suffix):
            stem = file_name[: -len(suffix)]
            break
    else:
        raise ValueError(f"unsupported source distribution suffix for {path}")

    version_suffix = f"-{version}"
    if not stem.endswith(version_suffix):
        raise ValueError(f"{path.name} does not end with expected version suffix {version_suffix}")
    return stem[: -len(version_suffix)]


def _validate_archive_hygiene(path: Path) -> None:
    if path.suffix == ".whl" or path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            member_names = archive.namelist()
    else:
        with tarfile.open(path, "r:*") as archive:
            member_names = archive.getnames()

    forbidden = sorted(
        name
        for name in member_names
        if "__pycache__" in PurePosixPath(name).parts
        or PurePosixPath(name).name.endswith(_BYTECODE_SUFFIXES)
    )
    if forbidden:
        raise ValueError(f"forbidden Python cache entries in {path.name}: {forbidden}")


def _parse_sdist_metadata(path: Path) -> tuple[str, str]:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            names = [
                name
                for name in archive.namelist()
                if len(PurePosixPath(name).parts) == 2 and name.endswith("/PKG-INFO")
            ]
            member = _find_single_string(names, kind="sdist metadata", root=path)
            raw = archive.read(member)
    else:
        with tarfile.open(path, "r:*") as archive:
            names = [
                member.name
                for member in archive.getmembers()
                if member.isfile()
                and len(PurePosixPath(member.name).parts) == 2
                and member.name.endswith("/PKG-INFO")
            ]
            member = _find_single_string(names, kind="sdist metadata", root=path)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("sdist metadata is not a regular file")
            raw = stream.read()
    metadata = Parser().parsestr(raw.decode("utf-8"))
    name, version = metadata.get("Name"), metadata.get("Version")
    if not name or not version:
        raise ValueError("sdist metadata is missing Name/Version")
    return name, version


def collect_distribution_artifacts(dist_dir: Path, distribution: str) -> DistributionArtifacts:
    """Resolve and validate the wheel/sdist pair for one distribution."""

    root = dist_dir.resolve()
    if not root.exists():
        raise ValueError(f"distribution directory does not exist: {root}")

    wheel_paths = sorted(path for path in root.rglob("*.whl") if path.is_file())
    sdist_paths = sorted(
        path for suffix in _SDIST_SUFFIXES for path in root.rglob(f"*{suffix}") if path.is_file()
    )

    duplicate_wheels = [
        name for name, count in Counter(path.name for path in wheel_paths).items() if count > 1
    ]
    if duplicate_wheels:
        raise ValueError(f"duplicate wheel path(s) detected for {distribution}: {duplicate_wheels}")

    wheel_path = _find_single_file(wheel_paths, kind="wheel", root=root)
    sdist_path = _find_single_file(sdist_paths, kind="source distribution", root=root)

    metadata_name, version = _parse_wheel_metadata(wheel_path)
    if normalize_distribution_name(metadata_name) != normalize_distribution_name(distribution):
        raise ValueError(
            f"wheel metadata name mismatch: expected {distribution}, found {metadata_name}"
        )

    sdist_name = _parse_sdist_name(sdist_path, version)
    if normalize_distribution_name(sdist_name) != normalize_distribution_name(distribution):
        raise ValueError(
            f"source distribution name mismatch: expected {distribution}, found {sdist_name}"
        )
    sdist_metadata_name, sdist_version = _parse_sdist_metadata(sdist_path)
    if (
        normalize_distribution_name(sdist_metadata_name)
        != normalize_distribution_name(distribution)
        or sdist_version != version
    ):
        raise ValueError("wheel/sdist metadata name or version mismatch")

    _validate_archive_hygiene(wheel_path)
    _validate_archive_hygiene(sdist_path)

    return DistributionArtifacts(
        distribution=distribution,
        version=version,
        wheel_path=wheel_path,
        sdist_path=sdist_path,
        metadata_name=metadata_name,
    )


def expected_release_tag(distribution: str, version: str) -> str:
    """Return the expected release tag for a distribution/version pair."""

    return f"v{version}" if distribution == "codex-ml" else f"{distribution}-v{version}"


def validate_release_tag(distribution: str, dist_dir: Path, tag: str) -> dict[str, Any]:
    """Validate that a release tag matches the built artifact version exactly."""

    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    normalized_tag = _strip_tag_ref(tag)
    expected_tag = expected_release_tag(distribution, artifacts.version)
    if normalized_tag != expected_tag:
        raise ValueError(
            f"release tag mismatch for {distribution}: "
            f"expected {expected_tag}, found {normalized_tag}"
        )
    return {
        "distribution": distribution,
        "version": artifacts.version,
        "tag": normalized_tag,
        "expected_tag": expected_tag,
    }


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _run(cmd: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def artifact_sha256(path: Path) -> str:
    """Hash the exact retained artifact bytes, not their filename."""

    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def record_build_identity(
    distribution: str, dist_dir: Path, *, source_sha: str, origin: str
) -> dict[str, Any]:
    """Record local build identity; this is not a provenance attestation."""

    if not re.fullmatch(r"[0-9a-f]{40}", source_sha) or origin not in _ORIGINS:
        raise ValueError("invalid source identity or target origin")
    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    payload = {
        "distribution": distribution,
        "version": artifacts.version,
        "source_sha": source_sha,
        "origin": origin,
        "artifacts": {
            path.name: artifact_sha256(path)
            for path in (artifacts.wheel_path, artifacts.sdist_path)
        },
    }
    (dist_dir / "BUILD_IDENTITY.json").write_text(json.dumps(payload, sort_keys=True))
    return payload


def validate_build_identity(
    distribution: str, dist_dir: Path, *, source_sha: str, origin: str
) -> tuple[DistributionArtifacts, dict[str, Any]]:
    """Bind retained bytes and metadata to the expected source and target."""

    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    identity = json.loads((dist_dir / "BUILD_IDENTITY.json").read_text())
    expected = {
        "distribution": distribution,
        "version": artifacts.version,
        "source_sha": source_sha,
        "origin": origin,
        "artifacts": {
            path.name: artifact_sha256(path)
            for path in (artifacts.wheel_path, artifacts.sdist_path)
        },
    }
    if (
        origin not in _ORIGINS
        or not re.fullmatch(r"[0-9a-f]{40}", source_sha)
        or identity != expected
    ):
        raise ValueError("build identity version/digest/source/origin mismatch")
    return artifacts, identity


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    """Reject redirects before urllib can send a redirected request."""

    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        raise ValueError("public URL redirect mismatch")


def _read_public_url(url: str, *, max_bytes: int) -> bytes:
    """Read bounded public bytes without ambient proxies or redirects."""

    deadline = time.monotonic() + _HTTP_TIMEOUT
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _RejectRedirects())
    with opener.open(url, timeout=_HTTP_TIMEOUT) as response:
        if response.geturl() != url:
            raise ValueError("public URL origin redirect mismatch")
        chunks: list[bytes] = []
        size = 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("public response deadline exceeded")
            chunk = response.read1(min(65536, max_bytes - size + 1))
            if time.monotonic() >= deadline:
                raise TimeoutError("public response deadline exceeded")
            if not chunk:
                return b"".join(chunks)
            size += len(chunk)
            if size > max_bytes:
                raise ValueError("public response exceeds size limit")
            chunks.append(chunk)


def _validate_wheel_url(url: str, *, origin: str, filename: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    expected_host = (
        "test-files.pythonhosted.org" if origin == "testpypi" else "files.pythonhosted.org"
    )
    path = urllib.parse.unquote(parsed.path, errors="strict")
    if (
        parsed.scheme != "https"
        or parsed.netloc != expected_host
        or "?" in url
        or "#" in url
        or any(ord(character) <= 32 for character in url)
        or not path.startswith("/packages/")
        or any(part in ("", ".", "..") for part in path.split("/")[1:])
        or "\\" in path
        or "%" in path
        or PurePosixPath(path).name != filename
    ):
        raise ValueError("published wheel origin/path mismatch")


def verify_installed_artifact(
    distribution: str,
    dist_dir: Path,
    *,
    source_sha: str,
    origin: str,
    import_name: str,
    artifact_kind: str = "wheel",
) -> dict[str, Any]:
    """Check exact local installation identity and execute a public API call.

    Run with the verification interpreter in isolated mode, outside checkout.
    An origin in the build record is intent, not proof of index publication.
    """

    artifacts, identity = validate_build_identity(
        distribution, dist_dir, source_sha=source_sha, origin=origin
    )
    if artifact_kind not in ("wheel", "sdist"):
        raise ValueError("unsupported installed artifact kind")
    artifact = artifacts.wheel_path if artifact_kind == "wheel" else artifacts.sdist_path
    installed = importlib.metadata.distribution(distribution)
    if (
        normalize_distribution_name(installed.metadata["Name"])
        != normalize_distribution_name(distribution)
        or installed.version != artifacts.version
    ):
        raise ValueError("installed version/name mismatch")
    direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
    if (
        direct_url.get("url") != artifact.as_uri()
        or direct_url.get("archive_info", {}).get("hashes", {}).get("sha256")
        != identity["artifacts"][artifact.name]
    ):
        raise ValueError("installed artifact digest/source mismatch")
    if _IMPORT_NAMES.get(distribution) != import_name:
        raise ValueError("installed import name mismatch")
    spec = importlib.machinery.PathFinder.find_spec(import_name)
    if spec is None or spec.origin is None:
        raise ValueError("installed module has no source file")
    module_path = Path(spec.origin).resolve()
    installed_root = Path(str(installed.locate_file(""))).resolve()
    expected_module_path = Path(str(installed.locate_file(f"{import_name}/__init__.py"))).resolve()
    if not module_path.is_relative_to(installed_root) or module_path != expected_module_path:
        raise ValueError("installed module source mismatch")
    cached_module = sys.modules.get(import_name)
    cached_source = getattr(cached_module, "__file__", None)
    if cached_module is not None and (
        cached_source is None or Path(cached_source).resolve() != module_path
    ):
        raise ValueError("installed cached module source mismatch")
    with zipfile.ZipFile(artifacts.wheel_path) as archive:
        if module_path.relative_to(installed_root).as_posix() not in archive.namelist():
            raise ValueError("installed module absent from validated wheel")
        for name in archive.namelist():
            if not name.endswith(".py"):
                continue
            parts = PurePosixPath(name).parts
            if ".." in parts or PurePosixPath(name).is_absolute():
                raise ValueError("unsafe wheel source path")
            source_path = Path(str(installed.locate_file(name))).resolve()
            if not source_path.is_relative_to(installed_root):
                raise ValueError("installed source path mismatch")
            if (
                not source_path.is_file()
                or hashlib.sha256(source_path.read_bytes()).digest()
                != hashlib.sha256(archive.read(name)).digest()
            ):
                raise ValueError("installed source content mismatch")
    check = _PUBLIC_CHECKS.get(distribution)
    if check is None:
        raise ValueError(f"no public functional check for {distribution}")
    module = importlib.import_module(import_name)
    if module.__file__ is None or Path(module.__file__).resolve() != module_path:
        raise ValueError("installed module source mismatch")
    exec(check, {"__builtins__": __builtins__})
    return {**identity, "artifact_kind": artifact_kind, "functional_check": "passed"}


def verify_published_wheel(
    distribution: str,
    dist_dir: Path,
    *,
    source_sha: str,
    origin: str,
    python_path: Path,
) -> dict[str, Any]:
    """Compare target-index bytes with the retained wheel, then install locally.

    No package-name resolution, dependency resolution, or alternate index is used.
    This does not establish hosted provenance or TestPyPI-to-PyPI promotion.
    """

    artifacts, identity = validate_build_identity(
        distribution, dist_dir, source_sha=source_sha, origin=origin
    )
    url = (
        f"{_ORIGINS[origin]}/pypi/"
        f"{urllib.parse.quote(distribution, safe='')}/"
        f"{urllib.parse.quote(artifacts.version, safe='')}/json"
    )
    payload = json.loads(_read_public_url(url, max_bytes=_MAX_INDEX_BYTES))
    if (
        normalize_distribution_name(payload["info"]["name"])
        != normalize_distribution_name(distribution)
        or payload["info"]["version"] != artifacts.version
    ):
        raise ValueError("published version/name mismatch")
    files = [entry for entry in payload["urls"] if entry["filename"] == artifacts.wheel_path.name]
    if len(files) != 1 or files[0]["digests"]["sha256"] != artifact_sha256(artifacts.wheel_path):
        raise ValueError("published wheel digest mismatch")
    wheel_url = files[0]["url"]
    _validate_wheel_url(wheel_url, origin=origin, filename=artifacts.wheel_path.name)
    digest = hashlib.sha256(
        _read_public_url(wheel_url, max_bytes=artifacts.wheel_path.stat().st_size)
    ).hexdigest()
    if digest != artifact_sha256(artifacts.wheel_path):
        raise ValueError("downloaded wheel digest mismatch")
    _run(
        [
            str(python_path),
            "-I",
            "-m",
            "pip",
            "--isolated",
            "install",
            "--no-deps",
            "--no-index",
            "--force-reinstall",
            str(artifacts.wheel_path),
        ]
    )
    return {**identity, "target_index_wheel_digest_checked": digest}


def install_artifacts_in_isolated_venvs(
    distribution: str,
    dist_dir: Path,
    *,
    source_sha: str,
    origin: str,
    work_dir: Path,
    import_name: str,
    build_requirements: Path,
) -> dict[str, Any]:
    """Functionally test both retained artifacts, with separately pinned build tools."""

    artifacts, identity = validate_build_identity(
        distribution, dist_dir, source_sha=source_sha, origin=origin
    )
    results = {}
    for kind, artifact in (("wheel", artifacts.wheel_path), ("sdist", artifacts.sdist_path)):
        base_dir = (work_dir / kind).resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        python_path = _venv_python(base_dir / "venv")
        venv.EnvBuilder(with_pip=True, clear=True).create(base_dir / "venv")
        if kind == "sdist":
            _run(
                [
                    str(python_path),
                    "-I",
                    "-m",
                    "pip",
                    "--isolated",
                    "install",
                    "--require-hashes",
                    "-r",
                    str(build_requirements.resolve()),
                ]
            )
        _run(
            [
                str(python_path),
                "-I",
                "-m",
                "pip",
                "--isolated",
                "install",
                "--no-deps",
                "--no-index",
                "--no-build-isolation",
                str(artifact),
            ]
        )
        result = subprocess.run(
            [
                str(python_path),
                "-I",
                str(Path(__file__).resolve()),
                "verify-installed",
                "--distribution",
                distribution,
                "--dist-dir",
                str(dist_dir.resolve()),
                "--source-sha",
                source_sha,
                "--origin",
                origin,
                "--import-name",
                import_name,
                "--artifact-kind",
                kind,
            ],
            cwd=base_dir,
            check=True,
            text=True,
            capture_output=True,
        )
        results[kind] = json.loads(result.stdout)
    return {**identity, "functional_results": results}


def install_wheel_in_isolated_venv(
    distribution: str,
    dist_dir: Path,
    *,
    work_dir: Path | None = None,
    import_name: str | None = None,
) -> dict[str, Any]:
    """Install a built wheel into a clean virtualenv and verify its metadata."""

    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    base_dir = work_dir or Path(
        tempfile.mkdtemp(prefix="publishing-assurance-", dir=dist_dir.resolve().parent)
    )
    venv_dir = base_dir / f"{distribution}-venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
    python_path = _venv_python(venv_dir)

    _run([str(python_path), "-m", "pip", "install", "--no-deps", str(artifacts.wheel_path)])
    version_result = _run(
        [
            str(python_path),
            "-Ic",
            ("import importlib.metadata as metadata, sys; " "print(metadata.version(sys.argv[1]))"),
            distribution,
        ],
        capture_output=True,
    )
    installed_version = version_result.stdout.strip()
    if installed_version != artifacts.version:
        raise ValueError(
            f"installed version mismatch for {distribution}: "
            f"expected {artifacts.version}, found {installed_version}"
        )

    if import_name:
        _run(
            [
                str(python_path),
                "-Ic",
                "import importlib, sys; importlib.import_module(sys.argv[1])",
                import_name,
            ]
        )

    return {
        "distribution": distribution,
        "version": installed_version,
        "venv_dir": str(venv_dir),
        "wheel_path": str(artifacts.wheel_path),
    }


def _extract_subject_names(attestation_payload: list[dict[str, Any]]) -> set[str]:
    subject_names: set[str] = set()
    for entry in attestation_payload:
        subjects = entry.get("verificationResult", {}).get("statement", {}).get("subject", [])
        for subject in subjects:
            name = subject.get("name")
            if isinstance(name, str) and name:
                subject_names.add(Path(name).name)
    return subject_names


def verify_attestations(
    distribution: str,
    dist_dir: Path,
    *,
    repo: str,
    signer_workflow: str,
    source_ref: str | None = None,
    source_digest: str | None = None,
) -> dict[str, Any]:
    """Verify GitHub artifact attestations for the built wheel and sdist."""

    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    verified_paths: list[str] = []

    for artifact_path in (artifacts.wheel_path, artifacts.sdist_path):
        cmd = [
            "gh",
            "attestation",
            "verify",
            str(artifact_path),
            "--repo",
            repo,
            "--signer-workflow",
            signer_workflow,
            "--format",
            "json",
        ]
        if source_ref:
            cmd.extend(["--source-ref", source_ref])
        if source_digest:
            cmd.extend(["--source-digest", source_digest])

        result = _run(cmd, capture_output=True)
        payload = json.loads(result.stdout)
        if not isinstance(payload, list) or not payload:
            raise ValueError(f"no attestation records returned for {artifact_path}")
        subject_names = _extract_subject_names(payload)
        if artifact_path.name not in subject_names:
            raise ValueError(
                f"attestation subject mismatch for {artifact_path.name}: "
                f"found {sorted(subject_names)}"
            )
        if not any(
            Path(subject.get("name", "")).name == artifact_path.name
            and subject.get("digest", {}).get("sha256") == artifact_sha256(artifact_path)
            for entry in payload
            for subject in entry.get("verificationResult", {})
            .get("statement", {})
            .get("subject", [])
        ):
            raise ValueError(f"attestation subject digest mismatch for {artifact_path.name}")
        verified_paths.append(str(artifact_path))

    return {
        "distribution": distribution,
        "version": artifacts.version,
        "verified_paths": verified_paths,
        "repo": repo,
        "signer_workflow": signer_workflow,
    }


def _print_result(payload: dict[str, Any]) -> None:
    def convert(value: Any) -> Any:
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, dict):
            return {key: convert(inner) for key, inner in value.items()}
        if isinstance(value, list):
            return [convert(inner) for inner in value]
        return value

    print(json.dumps(convert(payload), indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-dist", help="Validate wheel/sdist outputs")
    validate_parser.add_argument("--distribution", required=True)
    validate_parser.add_argument("--dist-dir", required=True, type=Path)

    tag_parser = subparsers.add_parser("validate-tag", help="Validate tag/version matching")
    tag_parser.add_argument("--distribution", required=True)
    tag_parser.add_argument("--dist-dir", required=True, type=Path)
    tag_parser.add_argument("--tag", required=True)

    install_parser = subparsers.add_parser(
        "install-wheel",
        help="Install a built wheel inside an isolated virtualenv",
    )
    install_parser.add_argument("--distribution", required=True)
    install_parser.add_argument("--dist-dir", required=True, type=Path)
    install_parser.add_argument("--work-dir", type=Path)
    install_parser.add_argument("--import-name")

    verify_parser = subparsers.add_parser(
        "verify-attestation",
        help="Verify GitHub artifact attestations for built artifacts",
    )
    verify_parser.add_argument("--distribution", required=True)
    verify_parser.add_argument("--dist-dir", required=True, type=Path)
    verify_parser.add_argument("--repo", required=True)
    verify_parser.add_argument("--signer-workflow", required=True)
    verify_parser.add_argument("--source-ref")
    verify_parser.add_argument("--source-digest")

    for command in ("record-build", "verify-published", "verify-installed", "install-artifacts"):
        identity_parser = subparsers.add_parser(command)
        identity_parser.add_argument("--distribution", required=True)
        identity_parser.add_argument("--dist-dir", required=True, type=Path)
        identity_parser.add_argument("--source-sha", required=True)
        identity_parser.add_argument("--origin", required=True, choices=sorted(_ORIGINS))
        if command == "verify-published":
            identity_parser.add_argument("--python-path", required=True, type=Path)
        if command in ("verify-installed", "install-artifacts"):
            identity_parser.add_argument("--import-name", required=True)
        if command == "verify-installed":
            identity_parser.add_argument(
                "--artifact-kind", choices=("wheel", "sdist"), default="wheel"
            )
        if command == "install-artifacts":
            identity_parser.add_argument("--work-dir", required=True, type=Path)
            identity_parser.add_argument("--build-requirements", required=True, type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""

    args = build_parser().parse_args(argv)

    if args.command == "validate-dist":
        payload = asdict(collect_distribution_artifacts(args.dist_dir, args.distribution))
    elif args.command == "validate-tag":
        payload = validate_release_tag(args.distribution, args.dist_dir, args.tag)
    elif args.command == "install-wheel":
        payload = install_wheel_in_isolated_venv(
            args.distribution,
            args.dist_dir,
            work_dir=args.work_dir,
            import_name=args.import_name,
        )
    elif args.command == "verify-attestation":
        payload = verify_attestations(
            args.distribution,
            args.dist_dir,
            repo=args.repo,
            signer_workflow=args.signer_workflow,
            source_ref=args.source_ref,
            source_digest=args.source_digest,
        )
    elif args.command == "record-build":
        payload = record_build_identity(
            args.distribution, args.dist_dir, source_sha=args.source_sha, origin=args.origin
        )
    elif args.command == "verify-published":
        payload = verify_published_wheel(
            args.distribution,
            args.dist_dir,
            source_sha=args.source_sha,
            origin=args.origin,
            python_path=args.python_path,
        )
    elif args.command == "verify-installed":
        payload = verify_installed_artifact(
            args.distribution,
            args.dist_dir,
            source_sha=args.source_sha,
            origin=args.origin,
            import_name=args.import_name,
            artifact_kind=args.artifact_kind,
        )
    elif args.command == "install-artifacts":
        payload = install_artifacts_in_isolated_venvs(
            args.distribution,
            args.dist_dir,
            source_sha=args.source_sha,
            origin=args.origin,
            import_name=args.import_name,
            work_dir=args.work_dir,
            build_requirements=args.build_requirements,
        )
    else:  # pragma: no cover
        raise AssertionError(f"unsupported command: {args.command}")

    _print_result(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
