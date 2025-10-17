from __future__ import annotations

from pathlib import Path

import pytest

from src.tools.archive_pr_checklist import evaluate_archive_pr


def _prepare_compliant_tree(base: Path) -> list[str]:
    adr = base / "docs" / "arch"
    adr.mkdir(parents=True, exist_ok=True)
    adr_path = adr / "adr-20250101-demo.md"
    adr_path.write_text("# ADR\n", encoding="utf-8")

    changelog = base / "CHANGELOG.md"
    changelog.write_text("## [Unreleased]\n- Archive stub\n", encoding="utf-8")

    evidence_dir = base / ".codex" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "archive_ops.jsonl"
    evidence_path.write_text('{"action":"APPEND"}\n', encoding="utf-8")

    attest_dir = base / "attestations"
    attest_dir.mkdir(parents=True, exist_ok=True)
    provenance_path = attest_dir / "arch-20250101-demo.intoto.jsonl"
    provenance_path.write_text("{}\n", encoding="utf-8")

    return [
        adr_path.relative_to(base).as_posix(),
        changelog.relative_to(base).as_posix(),
        evidence_path.relative_to(base).as_posix(),
        provenance_path.relative_to(base).as_posix(),
    ]


def test_archive_pr_checklist_happy_path(tmp_path: Path) -> None:
    changed_files = _prepare_compliant_tree(tmp_path)

    result = evaluate_archive_pr(tmp_path, changed_files=changed_files)

    assert result.ok is True
    assert result.missing == []
    assert result.has_adr and result.has_changelog and result.has_evidence and result.has_provenance
    assert sorted(changed_files) == result.changed_files


@pytest.mark.parametrize(
    "changed_files",
    [
        pytest.param([], id="no-files"),
        pytest.param(["docs/README.md"], id="non-adr-doc"),
    ],
)
def test_archive_pr_checklist_flags_missing_requirements(
    tmp_path: Path, changed_files: list[str]
) -> None:
    # Only create the paths we explicitly expect to change; nothing satisfies the checklist.
    for rel in changed_files:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")

    result = evaluate_archive_pr(tmp_path, changed_files=changed_files)

    assert result.ok is False
    assert "ADR in docs/arch/" in result.missing
    assert "CHANGELOG.md update" in result.missing
    assert "Evidence log delta (.codex/evidence/archive_ops.jsonl)" in result.missing
    assert "Provenance artifact" in result.missing
