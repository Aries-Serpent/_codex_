"""Tests for the archive PR checklist helper."""

from __future__ import annotations

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
    (repo / "CHANGELOG.md").write_text("- Added archive entry", encoding="utf-8")
    (repo / ".codex" / "evidence" / "archive_ops.jsonl").write_text(
        "{\"change\": \"archive\"}\n", encoding="utf-8"
    )
    (repo / "artifacts" / "provenance" / "attestation.json").write_text(
        "{\"attested\": true}\n", encoding="utf-8"
    )

    return repo


@pytest.fixture
def non_compliant_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "artifacts").mkdir()

    # Intentional omissions: ADR, evidence, provenance.
    (repo / "CHANGELOG.md").write_text("- Partial entry", encoding="utf-8")

    return repo


def test_evaluate_archive_pr_all_requirements_present(compliant_repo: Path) -> None:
    changed_files = [
        "docs/arch/adr-999.md",
        "CHANGELOG.md",
        ".codex/evidence/archive_ops.jsonl",
        "artifacts/provenance/attestation.json",
    ]
    result = evaluate_archive_pr(
        compliant_repo,
        changed_files=changed_files,
    )

    assert result.ok is True
    assert result.missing == []
    assert result.has_adr
    assert result.has_changelog
    assert result.has_evidence
    assert result.has_provenance
    assert result.changed_files == sorted(changed_files)


@pytest.mark.parametrize(
    "missing_path,expected_missing",
    [
        ("docs/arch/adr-999.md", "ADR in docs/arch/"),
        ("CHANGELOG.md", "CHANGELOG.md update"),
        (".codex/evidence/archive_ops.jsonl", "Evidence log delta (.codex/evidence/archive_ops.jsonl)"),
        ("artifacts/provenance/attestation.json", "Provenance artifact"),
    ],
)
def test_evaluate_archive_pr_flags_missing_requirements(
    compliant_repo: Path, missing_path: str, expected_missing: str
) -> None:
    changed = [
        "docs/arch/adr-999.md",
        "CHANGELOG.md",
        ".codex/evidence/archive_ops.jsonl",
        "artifacts/provenance/attestation.json",
    ]
    changed.remove(missing_path)

    result = evaluate_archive_pr(compliant_repo, changed_files=changed)

    assert result.ok is False
    assert expected_missing in result.missing


def test_evaluate_archive_pr_reports_all_missing(non_compliant_repo: Path) -> None:
    result = evaluate_archive_pr(
        non_compliant_repo,
        changed_files=["CHANGELOG.md"],
    )

    assert result.ok is False
    assert result.has_changelog is True
    assert result.has_adr is False
    assert result.has_evidence is False
    assert result.has_provenance is False
    assert "ADR in docs/arch/" in result.missing
    assert "Evidence log delta (.codex/evidence/archive_ops.jsonl)" in result.missing
    assert "Provenance artifact" in result.missing
