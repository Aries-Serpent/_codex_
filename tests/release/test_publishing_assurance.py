"""Tests for release publishing assurance helpers."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import zipfile
from email.message import Message
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.response import addinfourl

import pytest

from scripts.release import publishing_assurance as assurance
from scripts.release.publishing_assurance import (
    DistributionArtifacts,
    collect_distribution_artifacts,
    expected_release_tag,
    install_artifacts_in_isolated_venvs,
    install_wheel_in_isolated_venv,
    record_build_identity,
    validate_build_identity,
    validate_release_tag,
    verify_attestations,
    verify_installed_artifact,
    verify_published_wheel,
)


@pytest.mark.parametrize(
    ("distribution", "source_path"),
    [
        ("codex-ml", "src"),
        ("codex-cognitive-sdk", "packages/cognitive_sdk/src"),
        ("codex-contracts", "packages/contracts/src"),
        ("codex-ml-evaluation", "packages/evaluation/src"),
        ("codex-ml-lora", "packages/lora/src"),
        ("codex-ml-telemetry", "packages/telemetry/src"),
    ],
)
def test_public_smoke_matches_actual_exported_source_api(
    distribution: str, source_path: str
) -> None:
    """Validate smoke signatures; this is not installed-artifact verification."""

    root = Path(__file__).resolve().parents[2]
    subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            "import sys; sys.path.insert(0, sys.argv[1]); exec(sys.argv[2], {})",
            str(root / source_path),
            assurance._PUBLIC_CHECKS[distribution],
        ],
        cwd=root.parent,
        check=True,
        capture_output=True,
        text=True,
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
            "Metadata-Version: 2.1\n" f"Name: {distribution}\n" f"Version: {version}\n"
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
        digest = (
            base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("utf-8")
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
    files = {
        f"{distribution}-{version}/pyproject.toml": b"[build-system]\n",
        f"{distribution}-{version}/PKG-INFO": (
            f"Metadata-Version: 2.1\nName: {distribution}\nVersion: {version}\n"
        ).encode(),
    }
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

    assert artifacts.version == "0.1.0a1", "version is not valid"
    assert artifacts.wheel_path == wheel_path, "wheel_path is not valid"
    assert artifacts.sdist_path == sdist_path, "sdist_path is not valid"
    assert artifacts.metadata_name == "codex-cognitive-sdk", "Data must not be empty"


def test_sdist_metadata_must_match_wheel(tmp_path: Path) -> None:
    _create_minimal_wheel(
        tmp_path, distribution="codex-contracts", version="0.1.0", import_name="codex_contracts"
    )
    _create_minimal_sdist(
        tmp_path,
        distribution="codex-contracts",
        version="0.1.0",
        extra_files={
            "codex-contracts-0.1.0/PKG-INFO": b"Name: different\nVersion: 0.1.0\n",
        },
    )
    with pytest.raises(ValueError, match="metadata name or version mismatch"):
        collect_distribution_artifacts(tmp_path, "codex-contracts")


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
    assert payload["version"] == version, "Condition must be true"


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
            r"expected codex-cognitive-sdk-v0\.1\.0a1, " r"found codex-cognitive-sdk-v0\.1\.0a2"
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

    assert payload["version"] == "0.1.0a1", "Condition must be true"
    assert Path(payload["venv_dir"]).exists(), "Condition must be true"
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
    assert installed_version.stdout.strip() == "0.1.0a1", "Condition must be true"


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
                                "digest": {
                                    "sha256": hashlib.sha256(Path(cmd[3]).read_bytes()).hexdigest()
                                },
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
        source_digest="a" * 40,
    )

    assert payload["verified_paths"] == [str(wheel_path), str(sdist_path)]
    assert len(observed_commands) == 2, "Observed_commands must not be empty"
    assert observed_commands[0][:4] == ["gh", "attestation", "verify", str(wheel_path)]
    assert "--signer-workflow" in observed_commands[0], "Condition must be true"
    assert observed_commands[0][-2:] == ["--source-digest", "a" * 40]


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


def _mock_retained_bundle(monkeypatch: pytest.MonkeyPatch) -> tuple[Path, dict]:
    """Keep new substitution tests independent of filesystem/build availability."""

    root = Path(__file__).resolve().parent
    wheel = root / "codex_contracts-0.1.0-py3-none-any.whl"
    sdist = root / "codex_contracts-0.1.0.tar.gz"
    digest = hashlib.sha256(b"validated wheel").hexdigest()
    artifacts = DistributionArtifacts("codex-contracts", "0.1.0", wheel, sdist, "codex-contracts")
    identity = {
        "distribution": "codex-contracts",
        "version": "0.1.0",
        "source_sha": "a" * 40,
        "origin": "testpypi",
        "artifacts": {wheel.name: digest, sdist.name: digest},
    }
    monkeypatch.setattr(
        "scripts.release.publishing_assurance.collect_distribution_artifacts",
        lambda *a: artifacts,
    )
    monkeypatch.setattr("scripts.release.publishing_assurance.artifact_sha256", lambda _: digest)
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: json.dumps(identity))
    original_stat = Path.stat
    monkeypatch.setattr(
        Path,
        "stat",
        lambda path, *a, **k: (
            SimpleNamespace(st_size=len(b"validated wheel"))
            if path == wheel
            else original_stat(path, *a, **k)
        ),
    )
    monkeypatch.setattr(
        assurance.importlib.machinery.PathFinder,
        "find_spec",
        lambda _: SimpleNamespace(origin=str(root / "site-packages/codex_contracts/__init__.py")),
    )
    return wheel, identity


def test_record_build_identity_binds_both_artifacts_without_claiming_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    writes = []
    monkeypatch.setattr(Path, "write_text", lambda path, data: writes.append((path, data)))
    result = record_build_identity(
        "codex-contracts", wheel.parent, source_sha="a" * 40, origin="testpypi"
    )
    assert result == identity
    assert json.loads(writes[0][1]) == identity
    assert writes[0][0].name == "BUILD_IDENTITY.json"
    assert "provenance_verified" not in result


def test_target_index_verification_installs_only_the_retained_exact_wheel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    wheel_url = "https://test-files.pythonhosted.org/packages/" + wheel.name
    payload = {
        "info": {"name": "codex-contracts", "version": "0.1.0"},
        "urls": [
            {
                "filename": wheel.name,
                "url": wheel_url,
                "digests": {"sha256": identity["artifacts"][wheel.name]},
            }
        ],
    }

    class Response(io.BytesIO):
        def __init__(self, url: str, data: bytes) -> None:
            super().__init__(data)
            self.url = url

        def geturl(self) -> str:
            return self.url

    def open_url(url: str, *, timeout: int) -> Response:
        return Response(
            url, json.dumps(payload).encode() if url.endswith("/json") else b"validated wheel"
        )

    monkeypatch.setattr(
        assurance.urllib.request, "build_opener", lambda *handlers: Mock(open=open_url)
    )
    install = Mock()
    monkeypatch.setattr("scripts.release.publishing_assurance._run", install)
    python = wheel.parent / "python"
    result = verify_published_wheel(
        "codex-contracts",
        wheel.parent,
        source_sha="a" * 40,
        origin="testpypi",
        python_path=python,
    )
    assert result["target_index_wheel_digest_checked"] == identity["artifacts"][wheel.name]
    install.assert_called_once_with(
        [
            str(python),
            "-I",
            "-m",
            "pip",
            "--isolated",
            "install",
            "--no-deps",
            "--no-index",
            "--force-reinstall",
            str(wheel),
        ]
    )


def test_both_artifact_types_get_clean_functional_checks_and_separate_build_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheel, _ = _mock_retained_bundle(monkeypatch)
    monkeypatch.setattr(Path, "mkdir", lambda *a, **k: None)
    builder = Mock()
    monkeypatch.setattr("scripts.release.publishing_assurance.venv.EnvBuilder", builder)
    install = Mock()
    monkeypatch.setattr("scripts.release.publishing_assurance._run", install)
    verify = Mock(return_value=Mock(stdout='{"functional_check": "passed"}'))
    monkeypatch.setattr("scripts.release.publishing_assurance.subprocess.run", verify)
    requirements = wheel.parent / "lock-release.txt"
    result = install_artifacts_in_isolated_venvs(
        "codex-contracts",
        wheel.parent,
        source_sha="a" * 40,
        origin="testpypi",
        work_dir=wheel.parent / "work",
        import_name="codex_contracts",
        build_requirements=requirements,
    )
    assert set(result["functional_results"]) == {"wheel", "sdist"}
    assert builder.call_args_list == [
        ((), {"with_pip": True, "clear": True}),
        ((), {"with_pip": True, "clear": True}),
    ]
    assert verify.call_count == 2
    for call, kind in zip(verify.call_args_list, ("wheel", "sdist")):
        command = call.args[0]
        assert "-I" in command and "verify-installed" in command
        assert command[-2:] == ["--artifact-kind", kind]
        assert call.kwargs["cwd"] == wheel.parent / "work" / kind
    commands = [call.args[0] for call in install.call_args_list]
    assert len(commands) == 3
    assert "--require-hashes" in commands[1]
    assert str(requirements) in commands[1]
    for command in (commands[0], commands[2]):
        assert "--no-deps" in command and "--no-index" in command
        assert "--no-build-isolation" in command


@pytest.mark.parametrize("mutation", ["function-fails", "modified-source"])
def test_import_only_or_modified_source_cannot_pass_functional_assurance(
    monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    root = wheel.parent / "site-packages"
    installed = Mock()
    installed.version = "0.1.0"
    installed.metadata = {"Name": "codex-contracts"}
    installed.read_text.return_value = json.dumps(
        {
            "url": wheel.as_uri(),
            "archive_info": {"hashes": {"sha256": identity["artifacts"][wheel.name]}},
        }
    )
    installed.locate_file.side_effect = lambda name: root / name
    monkeypatch.setattr("importlib.metadata.distribution", lambda _: installed)
    import_module = Mock(return_value=Mock(__file__=str(root / "codex_contracts" / "__init__.py")))
    monkeypatch.setattr(assurance.importlib, "import_module", import_module)
    archive = Mock()
    archive.namelist.return_value = ["codex_contracts/__init__.py"]
    archive.read.return_value = b"validated source"
    archive.__enter__ = Mock(return_value=archive)
    archive.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(assurance.zipfile, "ZipFile", lambda _: archive)
    monkeypatch.setattr(Path, "is_file", lambda _: True)
    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda _: b"modified" if mutation == "modified-source" else b"validated source",
    )
    monkeypatch.setitem(
        assurance._PUBLIC_CHECKS,
        "codex-contracts",
        "raise RuntimeError('public function failed')",
    )
    error = ValueError if mutation == "modified-source" else RuntimeError
    match = "source content mismatch" if mutation == "modified-source" else "public function failed"
    with pytest.raises(error, match=match):
        verify_installed_artifact(
            "codex-contracts",
            wheel.parent,
            source_sha="a" * 40,
            origin="testpypi",
            import_name="codex_contracts",
        )
    if mutation == "modified-source":
        import_module.assert_not_called()
    else:
        import_module.assert_called_once_with("codex_contracts")


@pytest.mark.parametrize("mutation", ["tampered", "shadow"])
def test_real_untrusted_installed_module_is_rejected_without_execution(
    tmp_path: Path, mutation: str
) -> None:
    dist_dir = tmp_path / "dist"
    _create_distribution_pair(
        dist_dir,
        distribution="codex-contracts",
        version="0.1.0",
        import_name="codex_contracts",
    )
    record_build_identity("codex-contracts", dist_dir, source_sha="a" * 40, origin="testpypi")
    installed = install_wheel_in_isolated_venv(
        "codex-contracts",
        dist_dir,
        work_dir=tmp_path / "work",
    )
    python = Path(installed["venv_dir"]) / "bin" / "python"
    marker = tmp_path / "unexpected-execution"
    shadow = tmp_path / "shadow"
    if mutation == "tampered":
        result = subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "import importlib.metadata as m; print(m.distribution('codex-contracts').locate_file(''))",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        module_path = Path(result.stdout.strip()) / "codex_contracts" / "__init__.py"
    else:
        module_path = shadow / "codex_contracts" / "__init__.py"
        module_path.parent.mkdir(parents=True)
    module_path.write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
    )
    helper = Path(assurance.__file__).resolve()
    result = subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "".join(
                [
                    "import sys, runpy; from pathlib import Path; ",
                    "sys.path.insert(0, sys.argv[1]); ",
                    "helper=runpy.run_path(sys.argv[2]); ",
                    "helper['verify_installed_artifact']('codex-contracts', Path(sys.argv[3]), ",
                    "source_sha='a'*40, origin='testpypi', import_name='codex_contracts')",
                ]
            ),
            str(shadow),
            str(helper),
            str(dist_dir),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert (
        "installed source content mismatch" in result.stderr
        if mutation == "tampered"
        else ("installed module source mismatch" in result.stderr)
    )
    assert not marker.exists(), "untrusted module must not execute before rejection"


def test_public_reader_real_301_handler_rejects_before_redirect_or_proxy_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []
    url = "https://test.pypi.org/pypi/codex-contracts/0.1.0/json"

    class OfflineHTTPSHandler(assurance.urllib.request.BaseHandler):
        def https_open(self, request):
            calls.append(request.full_url)
            headers = Message()
            headers["Location"] = "https://redirected.example/must-not-open"
            response = addinfourl(io.BytesIO(b""), headers, request.full_url, 301)
            response.msg = "Moved Permanently"
            return response

    monkeypatch.setattr(assurance.urllib.request, "HTTPSHandler", OfflineHTTPSHandler)
    proxies = Mock(side_effect=AssertionError("ambient proxies must not be consulted"))
    monkeypatch.setattr(assurance.urllib.request, "getproxies", proxies)
    with pytest.raises(ValueError, match="redirect mismatch"):
        assurance._read_public_url(url, max_bytes=1024)
    assert calls == [url]
    proxies.assert_not_called()


@pytest.mark.parametrize("failure", ["size", "deadline"])
def test_public_reader_bounds_response_size_and_success_deadline(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    response = Mock()
    response.geturl.return_value = "https://pypi.org/example"
    response.read1.return_value = b"oversized"
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(
        assurance.urllib.request,
        "build_opener",
        lambda *handlers: Mock(open=Mock(return_value=response)),
    )
    if failure == "deadline":
        ticks = iter([0, 31])
        monkeypatch.setattr(assurance.time, "monotonic", lambda: next(ticks))
        error, match = TimeoutError, "deadline exceeded"
    else:
        error, match = ValueError, "size limit"
    with pytest.raises(error, match=match):
        assurance._read_public_url("https://pypi.org/example", max_bytes=3)
    if failure == "deadline":
        response.read1.assert_not_called()


@pytest.mark.parametrize("field", ["version", "source_sha", "origin", "artifacts"])
def test_build_identity_rejects_stale_or_substituted_bundle(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    identity[field] = {"wrong.whl": "0" * 64} if field == "artifacts" else "wrong"
    with pytest.raises(ValueError, match="version/digest/source/origin mismatch"):
        validate_build_identity(
            "codex-contracts", wheel.parent, source_sha="a" * 40, origin="testpypi"
        )


@pytest.mark.parametrize("mutation", ["older", "digest", "source", "module-source"])
def test_installed_package_cannot_satisfy_exact_artifact_check(
    monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    direct = {
        "url": wheel.as_uri(),
        "archive_info": {"hashes": {"sha256": identity["artifacts"][wheel.name]}},
    }
    if mutation == "digest":
        direct["archive_info"]["hashes"]["sha256"] = "0" * 64
    if mutation == "source":
        direct["url"] = "https://pypi.org/older.whl"
    installed = Mock()
    installed.version = "0.0.9" if mutation == "older" else "0.1.0"
    installed.metadata = {"Name": "codex-contracts"}
    installed.read_text.return_value = json.dumps(direct)
    installed.locate_file.return_value = wheel.parent / "site-packages"
    monkeypatch.setattr("importlib.metadata.distribution", lambda _: installed)
    import_module = Mock(return_value=Mock(__file__=str(wheel.parent / "checkout" / "__init__.py")))
    monkeypatch.setattr(assurance.importlib, "import_module", import_module)
    if mutation == "module-source":
        monkeypatch.setattr(
            assurance.importlib.machinery.PathFinder,
            "find_spec",
            lambda _: SimpleNamespace(origin=str(wheel.parent / "checkout" / "__init__.py")),
        )
    with pytest.raises(ValueError, match="installed .* mismatch"):
        verify_installed_artifact(
            "codex-contracts",
            wheel.parent,
            source_sha="a" * 40,
            origin="testpypi",
            import_name="codex_contracts",
        )
    import_module.assert_not_called()


@pytest.mark.parametrize(
    "mutation",
    [
        "older",
        "digest",
        "origin",
        "download",
        "redirect",
        "path",
        "filename",
        "query",
        "fragment",
        "userinfo",
        "port",
        "encoded-traversal",
    ],
)
def test_target_index_verification_rejects_substitution_without_install(
    monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    wheel, identity = _mock_retained_bundle(monkeypatch)
    digest = identity["artifacts"][wheel.name]
    wheel_url = "https://test-files.pythonhosted.org/packages/" + wheel.name
    if mutation == "origin":
        wheel_url = "https://files.pythonhosted.org/packages/" + wheel.name
    elif mutation == "path":
        wheel_url = "https://test-files.pythonhosted.org/other/" + wheel.name
    elif mutation == "filename":
        wheel_url = "https://test-files.pythonhosted.org/packages/older.whl"
    elif mutation == "query":
        wheel_url += "?redirect=https://other.example"
    elif mutation == "fragment":
        wheel_url += "#fragment"
    elif mutation == "userinfo":
        wheel_url = wheel_url.replace("https://", "https://user@")
    elif mutation == "port":
        wheel_url = wheel_url.replace(".org/", ".org:443/")
    elif mutation == "encoded-traversal":
        wheel_url = wheel_url.replace("/packages/", "/packages/%2e%2e/")
    payload = {
        "info": {"name": "codex-contracts", "version": "0.0.9" if mutation == "older" else "0.1.0"},
        "urls": [
            {
                "filename": wheel.name,
                "digests": {"sha256": "0" * 64 if mutation == "digest" else digest},
                "url": wheel_url,
            }
        ],
    }
    calls = []

    class Response(io.BytesIO):
        def __init__(self, url: str, data: bytes) -> None:
            super().__init__(data)
            self.url = url

        def geturl(self) -> str:
            return "https://pypi.org/substitute" if mutation == "redirect" else self.url

    def open_url(url: str, *, timeout: int) -> Response:
        calls.append(url)
        assert timeout == 30
        return Response(
            url,
            (
                json.dumps(payload).encode()
                if url.endswith("/json")
                else b"substitute" if mutation == "download" else b"validated wheel"
            ),
        )

    monkeypatch.setattr(
        assurance.urllib.request, "build_opener", lambda *handlers: Mock(open=open_url)
    )
    install = Mock()
    monkeypatch.setattr("scripts.release.publishing_assurance._run", install)
    with pytest.raises(ValueError, match="mismatch"):
        verify_published_wheel(
            "codex-contracts",
            wheel.parent,
            source_sha="a" * 40,
            origin="testpypi",
            python_path=wheel.parent / "python",
        )
    install.assert_not_called()
    assert calls[0] == "https://test.pypi.org/pypi/codex-contracts/0.1.0/json"
    if mutation in (
        "origin",
        "path",
        "filename",
        "query",
        "fragment",
        "userinfo",
        "port",
        "encoded-traversal",
    ):
        assert len(calls) == 1, "invalid wheel URLs must be rejected before opening"


def test_attestation_rejects_correct_name_with_wrong_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wheel, _ = _mock_retained_bundle(monkeypatch)
    monkeypatch.setattr(
        "scripts.release.publishing_assurance._run",
        lambda *a, **k: Mock(
            stdout=json.dumps(
                [
                    {
                        "verificationResult": {
                            "statement": {
                                "subject": [
                                    {
                                        "name": wheel.name,
                                        "digest": {"sha256": "0" * 64},
                                    }
                                ]
                            }
                        }
                    }
                ]
            )
        ),
    )
    with pytest.raises(ValueError, match="subject digest mismatch"):
        verify_attestations(
            "codex-contracts",
            wheel.parent,
            repo="release/repo",
            signer_workflow="release/repo/.github/workflows/pypi-publish.yml",
        )
