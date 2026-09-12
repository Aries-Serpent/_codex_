#!/usr/bin/env python3
"""Publishing assurance helpers for PyPI release automation."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tarfile
import tempfile
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


def collect_distribution_artifacts(dist_dir: Path, distribution: str) -> DistributionArtifacts:
    """Resolve and validate the wheel/sdist pair for one distribution."""

    root = dist_dir.resolve()
    if not root.exists():
        raise ValueError(f"distribution directory does not exist: {root}")

    wheel_paths = sorted(path for path in root.rglob("*.whl") if path.is_file())
    sdist_paths = sorted(
        path
        for suffix in _SDIST_SUFFIXES
        for path in root.rglob(f"*{suffix}")
        if path.is_file()
    )

    duplicate_wheels = [
        name
        for name, count in Counter(path.name for path in wheel_paths).items()
        if count > 1
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


def install_wheel_in_isolated_venv(
    distribution: str,
    dist_dir: Path,
    *,
    work_dir: Path | None = None,
    import_name: str | None = None,
) -> dict[str, Any]:
    """Install a built wheel into a clean virtualenv and verify its metadata."""

    artifacts = collect_distribution_artifacts(dist_dir, distribution)
    base_dir = work_dir or Path(tempfile.mkdtemp(prefix="publishing-assurance-"))
    venv_dir = base_dir / f"{distribution}-venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)
    python_path = _venv_python(venv_dir)

    _run([str(python_path), "-m", "pip", "install", "--no-deps", str(artifacts.wheel_path)])
    version_result = _run(
        [
            str(python_path),
            "-Ic",
            (
                "import importlib.metadata as metadata, sys; "
                "print(metadata.version(sys.argv[1]))"
            ),
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
        subjects = (
            entry.get("verificationResult", {})
            .get("statement", {})
            .get("subject", [])
        )
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
        )
    else:  # pragma: no cover
        raise AssertionError(f"unsupported command: {args.command}")

    _print_result(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
