"""Tests for the archive PR checklist helper."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from typing import ClassVar

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
    (repo / "CHANGELOG.md").write_text("- Partial entry", encoding="utf-8")

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


def test_evaluate_archive_pr_no_changed_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = evaluate_archive_pr(repo, changed_files=[])

    assert result.ok is True
    assert result.missing == []
    assert result.changed_files == []


def test_archive_pr_gate_skips_when_no_staged_changes(
    monkeypatch: pytest.MonkeyPatch, noxfile_module
) -> None:
    logged: list[str] = []

    class DummySession:
        posargs: ClassVar[list[str]] = []
        env: ClassVar[dict[str, str]] = {}

        def log(self, message: str) -> None:
            logged.append(message)

        def install(self, *args: str, **kwargs: str) -> None:  # pragma: no cover - defensive
            raise AssertionError("install should not be called when gate is skipped")

        def run(self, *args: str, **kwargs: str) -> None:  # pragma: no cover - defensive
            raise AssertionError("run should not be called when gate is skipped")

    monkeypatch.setattr(noxfile_module, "_archive_gate_staged_files", lambda _: [])

    noxfile_module.archive_pr_gate(DummySession())

    assert logged == ["No staged changes detected; skipping archive PR checklist gate."]
