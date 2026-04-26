"""
tests/api/test_rag_api_validation.py
──────────────────────────────────────
Parameterized validation tests for RAG API request models.

Covers:
- MergeIndicesRequest.source_indices: min_length=2 constraint (Pydantic v2)
- MergeIndicesRequest field presence and type validation
- _ensure_subpath path-traversal guard
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("slowapi")
from fastapi import HTTPException  # noqa: E402
from pydantic import ValidationError

from codex.api.rag_api import MergeIndicesRequest, _ensure_subpath

# ---------------------------------------------------------------------------
# MergeIndicesRequest.source_indices — min_length=2 (Pydantic v2)
# ---------------------------------------------------------------------------


class TestMergeIndicesRequestValidation:
    """Parameterized tests for MergeIndicesRequest field validation."""

    # ── source_indices: invalid cases (must raise ValidationError) ──────────

    @pytest.mark.parametrize(
        "source_indices, description",
        [
            ([], "empty list — 0 items < minimum 2"),
            (["only_one"], "single item — 1 item < minimum 2"),
        ],
    )
    def test_source_indices_below_minimum_raises(
        self, source_indices: list, description: str
    ) -> None:
        """Fewer than 2 source_indices must be rejected (Pydantic v2 min_length=2)."""
        with pytest.raises(ValidationError) as exc_info:
            MergeIndicesRequest(
                source_indices=source_indices,
                target_index="merged",
                tenant_id="default",
            )
        errors = exc_info.value.errors()
        assert any(
            "source_indices" in str(e.get("loc", "")) for e in errors
        ), f"Expected source_indices validation error for: {description}"

    # ── source_indices: valid cases (must NOT raise) ─────────────────────────

    @pytest.mark.parametrize(
        "source_indices, description",
        [
            (["a", "b"], "exactly 2 items — boundary minimum"),
            (["a", "b", "c"], "3 items — above minimum"),
            (["x"] * 10, "10 items — well above minimum"),
        ],
    )
    def test_source_indices_at_or_above_minimum_accepted(
        self, source_indices: list, description: str
    ) -> None:
        """2 or more source_indices must be accepted."""
        req = MergeIndicesRequest(
            source_indices=source_indices,
            target_index="merged",
            tenant_id="default",
        )
        assert req.source_indices == source_indices, description

    # ── other required fields ────────────────────────────────────────────────

    def test_target_index_required(self) -> None:
        """target_index is required; omitting it raises ValidationError."""
        with pytest.raises(ValidationError):
            MergeIndicesRequest(source_indices=["a", "b"])  # type: ignore[call-arg]

    def test_tenant_id_defaults_to_default(self) -> None:
        """tenant_id has a default of 'default'."""
        req = MergeIndicesRequest(source_indices=["a", "b"], target_index="merged")
        assert req.tenant_id == "default"

    @pytest.mark.parametrize("tenant_id", ["acme", "tenant-42", "org_123"])
    def test_custom_tenant_id_accepted(self, tenant_id: str) -> None:
        """Any non-empty string is accepted as tenant_id."""
        req = MergeIndicesRequest(
            source_indices=["a", "b"],
            target_index="merged",
            tenant_id=tenant_id,
        )
        assert req.tenant_id == tenant_id


# ---------------------------------------------------------------------------
# _ensure_subpath — path traversal guard
# ---------------------------------------------------------------------------


class TestEnsureSubpath:
    """Unit tests for the path-traversal guard in rag_api."""

    def test_exact_base_is_allowed(self, tmp_path: Path) -> None:
        result = _ensure_subpath(tmp_path, tmp_path)
        assert result == tmp_path.resolve()

    def test_child_path_is_allowed(self, tmp_path: Path) -> None:
        child = tmp_path / "subdir" / "file.txt"
        result = _ensure_subpath(tmp_path, child)
        assert result == child.resolve()

    def test_parent_escape_raises_400(self, tmp_path: Path) -> None:
        """Paths that escape the base directory must raise HTTP 400."""
        escape = tmp_path / ".." / "etc" / "passwd"
        with pytest.raises(HTTPException) as exc_info:
            _ensure_subpath(tmp_path, escape)
        assert exc_info.value.status_code == 400

    def test_absolute_escape_raises_400(self, tmp_path: Path) -> None:
        """An absolute path outside base must raise HTTP 400."""
        outside = Path("/etc/passwd")
        with pytest.raises(HTTPException) as exc_info:
            _ensure_subpath(tmp_path, outside)
        assert exc_info.value.status_code == 400
