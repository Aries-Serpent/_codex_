"""Tests for the archive PR checklist helper."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

from src.tools.archive_pr_checklist import evaluate_archive_pr


@pytest.fixture
def compliant_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "arch").mkdir(parents=True)
    (repo / ".codex" / "evidence").mkdir(parents=True)
    (repo / "artifacts" / "provenance").mkdir(parents=True)

    (repo / "docs" / "arch" / "adr-999.md").write_text("# ADR 999", encoding="utf-8")
    (repo / "docs/CHANGELOG.md").write_text("- Added archive entry", encoding="utf-8")
    (repo / ".codex" / "evidence" / "archive_ops.jsonl").write_text(
        '{"change": "archive"}\n', encoding="utf-8"
    )
    (repo / "artifacts" / "provenance" / "attestation.json").write_text(
        '{"attested": true}\n', encoding="utf-8"
    )

    return repo


@pytest.fixture
def non_compliant_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "artifacts").mkdir()

    # Intentional omissions: ADR, evidence, provenance.
    (repo / "docs/CHANGELOG.md").write_text("- Partial entry", encoding="utf-8")

    return repo


@pytest.fixture
def noxfile_module(monkeypatch: pytest.MonkeyPatch):
    dummy_options = types.SimpleNamespace(
        reuse_existing_virtualenvs=True,
        stop_on_first_error=False,
        error_on_missing_interpreters=False,
    )

    def _session(*args, **_kwargs):
        def decorator(func):
            return func

        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

    dummy_nox = types.SimpleNamespace(session=_session, options=dummy_options, Session=object)
    monkeypatch.setitem(sys.modules, "nox", dummy_nox)
    sys.modules.pop("noxfile", None)
    return importlib.import_module("noxfile")


def test_evaluate_archive_pr_all_requirements_present(compliant_repo: Path) -> None:
    changed_files = [
        "docs/arch/adr-999.md",
        "docs/CHANGELOG.md",
        ".codex/evidence/archive_ops.jsonl",
        "artifacts/provenance/attestation.json",
    ]
    result = evaluate_archive_pr(
        compliant_repo,
        changed_files=changed_files,
    )

    assert result.ok is True, "Result must not be empty"
    assert result.missing == [], "Result must not be empty"
    assert result.has_adr, "Result must not be empty"
    assert result.has_changelog, "Result must not be empty"
    assert result.has_evidence, "Result must not be empty"
    assert result.has_provenance, "Result must not be empty"
    assert result.changed_files == sorted(changed_files), "Result must not be empty"


@pytest.mark.parametrize(
    "missing_path,expected_missing",
    [
        ("docs/arch/adr-999.md", "ADR in docs/arch/"),
        ("docs/CHANGELOG.md", "docs/CHANGELOG.md update"),
        (
            ".codex/evidence/archive_ops.jsonl",
            "Evidence log delta (.codex/evidence/archive_ops.jsonl)",
        ),
        ("artifacts/provenance/attestation.json", "Provenance artifact"),
    ],
)
def test_evaluate_archive_pr_flags_missing_requirements(
    compliant_repo: Path, missing_path: str, expected_missing: str
) -> None:
    changed = [
        "docs/arch/adr-999.md",
        "docs/CHANGELOG.md",
        ".codex/evidence/archive_ops.jsonl",
        "artifacts/provenance/attestation.json",
    ]
    changed.remove(missing_path)

    result = evaluate_archive_pr(compliant_repo, changed_files=changed)

    assert result.ok is False, "Result must not be empty"
    assert expected_missing in result.missing, "Result must not be empty"


def test_evaluate_archive_pr_reports_all_missing(non_compliant_repo: Path) -> None:
    result = evaluate_archive_pr(
        non_compliant_repo,
        changed_files=["docs/CHANGELOG.md"],
    )

    assert result.ok is False, "Result must not be empty"
    assert result.has_changelog is True, "Result must not be empty"
    assert result.has_adr is False, "Result must not be empty"
    assert result.has_evidence is False, "Result must not be empty"
    assert result.has_provenance is False, "Result must not be empty"
    assert "ADR in docs/arch/" in result.missing, "Result must not be empty"
    assert "Evidence log delta (.codex/evidence/archive_ops.jsonl)" in result.missing, "Result must not be empty"
    assert "Provenance artifact" in result.missing, "Result must not be empty"


@pytest.mark.parametrize(
    "relative_path",
    [
        "artifacts/provenance/report.json",
        "artifacts/attest/build.attestation.json",
        "artifacts/intoto/archive.intoto.jsonl",
        "artifacts/in-toto/statement.json",
        "artifacts/slsa/provenance.json",
        "artifacts/SLSA/provenance.json",  # Case-insensitive check.
    ],
)
def test_provenance_hints_detect_common_patterns(compliant_repo: Path, relative_path: str) -> None:
    target = compliant_repo / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}", encoding="utf-8")

    result = evaluate_archive_pr(
        compliant_repo,
        changed_files=[relative_path],
    )

    assert result.has_provenance is True, "Result must not be empty"


@pytest.mark.parametrize(
    "relative_path",
    [
        "artifacts/logs/archive.txt",
        "docs/archived/readme.md",
        "artifacts/intro/statement.json",  # substring should not match ``intoto``.
    ],
)
def test_provenance_hints_ignore_unrelated_paths(compliant_repo: Path, relative_path: str) -> None:
    target = compliant_repo / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}", encoding="utf-8")

    result = evaluate_archive_pr(
        compliant_repo,
        changed_files=[relative_path],
    )

    assert result.has_provenance is False, "Result must not be empty"
