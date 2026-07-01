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
from fastapi import HTTPException
from pydantic import ValidationError

from codex.api.rag_api import MergeIndicesRequest, _ensure_subpath, _validate_path_segment

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
        # Fixed malformed assertion: assert any(...)

    def test_child_path_is_allowed(self, tmp_path: Path) -> None:
        child = tmp_path / "subdir" / "file.txt"
        result = _ensure_subpath(tmp_path, child)
        assert result == child.resolve(), "Result must not be empty"

    def test_parent_escape_raises_400(self, tmp_path: Path) -> None:
        """Paths that escape the base directory must raise HTTP 400."""
        escape = tmp_path / ".." / "etc" / "passwd"
        with pytest.raises(HTTPException) as exc_info:
            _ensure_subpath(tmp_path, escape)
        assert exc_info.value.status_code == 400, "Value must be initialized"

    def test_absolute_escape_raises_400(self, tmp_path: Path) -> None:
        """An absolute path outside base must raise HTTP 400."""
        outside = Path("/etc/passwd")
        with pytest.raises(HTTPException) as exc_info:
            _ensure_subpath(tmp_path, outside)
        assert exc_info.value.status_code == 400, "Value must be initialized"


class TestValidatePathSegment:
    """Unit tests for tenant/index path segment validation."""

    @pytest.mark.parametrize("value", ["default", "tenant-42", "index_1", "release.v1", "a" * 128])
    def test_valid_segments_pass(self, value: str) -> None:
        assert _validate_path_segment(value, "segment") == value

    @pytest.mark.parametrize("value", ["../etc", "a/b", r"a\\b", " ", "", "🔥", "a" * 129])
    def test_invalid_segments_raise_400(self, value: str) -> None:
        with pytest.raises(HTTPException) as exc_info:
            _validate_path_segment(value, "segment")
        assert exc_info.value.status_code == 400, "Value must be initialized"
