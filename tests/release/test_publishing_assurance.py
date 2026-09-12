"""Tests for release publishing assurance helpers."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from io import StringIO
from pathlib import Path

import pytest

from scripts.release.publishing_assurance import (
    collect_distribution_artifacts,
    expected_release_tag,
    install_wheel_in_isolated_venv,
    validate_release_tag,
    verify_attestations,
)


def _record_bytes(rows: list[tuple[str, str, str]]) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def _create_minimal_wheel(
    dist_dir: Path,
    *,
    distribution: str,
    version: str,
    import_name: str,
    extra_files: dict[str, bytes] | None = None,
) -> Path:
    normalized_distribution = distribution.replace("-", "_")
    wheel_path = dist_dir / f"{normalized_distribution}-{version}-py3-none-any.whl"
    dist_info = f"{normalized_distribution}-{version}.dist-info"

    files: dict[str, bytes] = {
        f"{import_name}/__init__.py": f"__version__ = {version!r}\n".encode("utf-8"),
        f"{dist_info}/METADATA": (
            "Metadata-Version: 2.1\n"
            f"Name: {distribution}\n"
            f"Version: {version}\n"
        ).encode("utf-8"),
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\n"
            "Generator: pytest\n"
            "Root-Is-Purelib: true\n"
            "Tag: py3-none-any\n"
        ).encode("utf-8"),
    }
    files.update(extra_files or {})

    records: list[tuple[str, str, str]] = []
    for file_name, payload in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode(
            "utf-8"
        )
        records.append((file_name, f"sha256={digest}", str(len(payload))))
    records.append((f"{dist_info}/RECORD", "", ""))
    files[f"{dist_info}/RECORD"] = _record_bytes(records)

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name, payload in files.items():
            archive.writestr(file_name, payload)

    return wheel_path


def _create_minimal_sdist(
    dist_dir: Path,
    *,
    distribution: str,
    version: str,
    extra_files: dict[str, bytes] | None = None,
) -> Path:
    sdist_path = dist_dir / f"{distribution}-{version}.tar.gz"
    files = {f"{distribution}-{version}/pyproject.toml": b"[build-system]\n"}
    files.update(extra_files or {})
    with tarfile.open(sdist_path, "w:gz") as archive:
        for file_name, payload in files.items():
            info = tarfile.TarInfo(file_name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return sdist_path


def _create_distribution_pair(
    dist_dir: Path,
    *,
    distribution: str,
    version: str,
    import_name: str,
) -> tuple[Path, Path]:
    dist_dir.mkdir(parents=True, exist_ok=True)
    wheel_path = _create_minimal_wheel(
        dist_dir,
        distribution=distribution,
        version=version,
        import_name=import_name,
    )
    sdist_path = _create_minimal_sdist(dist_dir, distribution=distribution, version=version)
    return wheel_path, sdist_path


def test_collect_distribution_artifacts_returns_validated_metadata(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    wheel_path, sdist_path = _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )

    artifacts = collect_distribution_artifacts(dist_dir, "codex-cognitive-sdk")

    assert artifacts.version == "0.1.0a1"
    assert artifacts.wheel_path == wheel_path
    assert artifacts.sdist_path == sdist_path
    assert artifacts.metadata_name == "codex-cognitive-sdk"


def test_collect_distribution_artifacts_rejects_duplicate_wheels(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    wheel_path, _ = _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )
    duplicate_dir = dist_dir / "nested"
    duplicate_dir.mkdir()
    (duplicate_dir / wheel_path.name).write_bytes(wheel_path.read_bytes())

    with pytest.raises(ValueError, match="duplicate wheel path"):
        collect_distribution_artifacts(dist_dir, "codex-cognitive-sdk")


@pytest.mark.parametrize(
    ("archive_kind", "forbidden_name"),
    [
        ("wheel", "codex_ml/__pycache__/marker.txt"),
        ("wheel", "codex_ml/module.pyc"),
        ("sdist", "codex-ml-0.3.0/codex_ml/module.pyo"),
        ("sdist", "codex-ml-0.3.0/codex_ml/native.pyd"),
    ],
)
def test_collect_distribution_artifacts_rejects_python_cache_entries(
    tmp_path: Path,
    archive_kind: str,
    forbidden_name: str,
) -> None:
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    wheel_extra = {forbidden_name: b"cache"} if archive_kind == "wheel" else None
    sdist_extra = {forbidden_name: b"cache"} if archive_kind == "sdist" else None
    _create_minimal_wheel(
        dist_dir,
        distribution="codex-ml",
        version="0.3.0",
        import_name="codex_ml",
        extra_files=wheel_extra,
    )
    _create_minimal_sdist(
        dist_dir,
        distribution="codex-ml",
        version="0.3.0",
        extra_files=sdist_extra,
    )

    with pytest.raises(ValueError, match="forbidden Python cache entries"):
        collect_distribution_artifacts(dist_dir, "codex-ml")


@pytest.mark.parametrize(
    ("distribution", "version", "tag"),
    [
        ("codex-ml", "0.3.0", "refs/tags/v0.3.0"),
        ("codex-cognitive-sdk", "0.1.0a1", "codex-cognitive-sdk-v0.1.0a1"),
    ],
)
def test_validate_release_tag_accepts_expected_formats(
    tmp_path: Path,
    distribution: str,
    version: str,
    tag: str,
) -> None:
    import_name = distribution.replace("-", "_")
    dist_dir = tmp_path / distribution
    _create_distribution_pair(
        dist_dir,
        distribution=distribution,
        version=version,
        import_name=import_name,
    )

    payload = validate_release_tag(distribution, dist_dir, tag)

    assert payload["expected_tag"] == expected_release_tag(distribution, version)
    assert payload["version"] == version


def test_validate_release_tag_rejects_version_mismatch(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )

    with pytest.raises(
        ValueError,
        match=(
            r"expected codex-cognitive-sdk-v0\.1\.0a1, "
            r"found codex-cognitive-sdk-v0\.1\.0a2"
        ),
    ):
        validate_release_tag(
            "codex-cognitive-sdk",
            dist_dir,
            "codex-cognitive-sdk-v0.1.0a2",
        )


def test_install_wheel_in_isolated_venv_installs_built_wheel(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )

    payload = install_wheel_in_isolated_venv(
        "codex-cognitive-sdk",
        dist_dir,
        work_dir=tmp_path / "work",
        import_name="codex_cognitive_sdk",
    )

    assert payload["version"] == "0.1.0a1"
    assert Path(payload["venv_dir"]).exists()
    installed_version = subprocess.run(
        [
            str(Path(payload["venv_dir"]) / "bin" / "python"),
            "-Ic",
            "import importlib.metadata as metadata; print(metadata.version('codex-cognitive-sdk'))",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert installed_version.stdout.strip() == "0.1.0a1"


def test_verify_attestations_uses_gh_for_wheel_and_sdist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dist_dir = tmp_path / "dist"
    wheel_path, sdist_path = _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )
    observed_commands: list[list[str]] = []

    def fake_run(
        cmd: list[str],
        *,
        check: bool,
        text: bool,
        capture_output: bool,
    ) -> subprocess.CompletedProcess[str]:
        observed_commands.append(cmd)
        artifact_name = Path(cmd[3]).name
        payload = [
            {
                "verificationResult": {
                    "statement": {
                        "subject": [
                            {
                                "name": artifact_name,
                                "digest": {"sha256": "abc123"},
                            }
                        ]
                    }
                }
            }
        ]
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps(payload),
            stderr="",
        )

    monkeypatch.setattr("scripts.release.publishing_assurance.subprocess.run", fake_run)

    payload = verify_attestations(
        "codex-cognitive-sdk",
        dist_dir,
        repo="Aries-Serpent/_codex_",
        signer_workflow="Aries-Serpent/_codex_/.github/workflows/pypi-publish.yml",
        source_ref="refs/tags/codex-cognitive-sdk-v0.1.0a1",
    )

    assert payload["verified_paths"] == [str(wheel_path), str(sdist_path)]
    assert len(observed_commands) == 2
    assert observed_commands[0][:4] == ["gh", "attestation", "verify", str(wheel_path)]
    assert "--signer-workflow" in observed_commands[0]


def test_verify_attestations_rejects_wrong_subject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dist_dir = tmp_path / "dist"
    _create_distribution_pair(
        dist_dir,
        distribution="codex-cognitive-sdk",
        version="0.1.0a1",
        import_name="codex_cognitive_sdk",
    )

    def fake_run(
        cmd: list[str],
        *,
        check: bool,
        text: bool,
        capture_output: bool,
    ) -> subprocess.CompletedProcess[str]:
        payload = [
            {
                "verificationResult": {
                    "statement": {
                        "subject": [{"name": "different-artifact.whl"}],
                    }
                }
            }
        ]
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=json.dumps(payload),
            stderr="",
        )

    monkeypatch.setattr("scripts.release.publishing_assurance.subprocess.run", fake_run)

    with pytest.raises(ValueError, match="attestation subject mismatch"):
        verify_attestations(
            "codex-cognitive-sdk",
            dist_dir,
            repo="Aries-Serpent/_codex_",
            signer_workflow="Aries-Serpent/_codex_/.github/workflows/pypi-publish.yml",
        )
