"""Unit tests for codex_ml.utils.retention (prune_checkpoints)."""

from __future__ import annotations

import json
from pathlib import Path

from codex_ml.utils.retention import EPOCH_DIR_RE, prune_checkpoints


def _make_epoch_dirs(root: Path, epochs: list[int]) -> None:
    """Create epoch-XXXX dirs under root."""
    for e in epochs:
        (root / f"epoch-{e:04d}").mkdir(parents=True, exist_ok=True)


def _write_latest_json(root: Path, epoch: int) -> None:
    (root / "latest.json").write_text(json.dumps({"epoch": epoch}))


# ---------------------------------------------------------------------------
# EPOCH_DIR_RE
# ---------------------------------------------------------------------------


def test_epoch_dir_re_matches_four_digit():
    assert EPOCH_DIR_RE.match("epoch-0001"), "Condition must be true"
    assert EPOCH_DIR_RE.match("epoch-9999"), "Condition must be true"


def test_epoch_dir_re_matches_more_digits():
    assert EPOCH_DIR_RE.match("epoch-00100"), "Condition must be true"
    assert EPOCH_DIR_RE.match("epoch-12345"), "Condition must be true"


def test_epoch_dir_re_no_match_short():
    assert not EPOCH_DIR_RE.match("epoch-001"), "Condition must be true"
    assert not EPOCH_DIR_RE.match("epoch-12"), "Condition must be true"


def test_epoch_dir_re_no_match_non_epoch():
    assert not EPOCH_DIR_RE.match("best"), "Condition must be true"
    assert not EPOCH_DIR_RE.match("latest"), "Condition must be true"
    assert not EPOCH_DIR_RE.match("epoch_0001"), "Condition must be true"


# ---------------------------------------------------------------------------
# prune_checkpoints — empty / missing directory
# ---------------------------------------------------------------------------


def test_prune_checkpoints_nonexistent_dir():
    result = prune_checkpoints("/nonexistent/path/xyz")
    assert result["total"] == 0, "Result must not be empty"
    assert result["kept"] == [], "Result must not be empty"
    assert result["pruned"] == [], "Result must not be empty"


def test_prune_checkpoints_empty_dir(tmp_path: Path):
    result = prune_checkpoints(tmp_path)
    assert result["total"] == 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — keep_last
# ---------------------------------------------------------------------------


def test_prune_checkpoints_keep_last_basic(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4, 5])
    result = prune_checkpoints(tmp_path, keep_last=2)
    assert sorted(result["kept"]) == [4, 5]
    assert sorted(result["pruned"]) == [1, 2, 3]


def test_prune_checkpoints_keep_last_deletes_dirs(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3])
    prune_checkpoints(tmp_path, keep_last=1)
    remaining_names = {p.name for p in tmp_path.iterdir()}
    assert "epoch-0003" in remaining_names, "Condition must be true"
    assert "epoch-0001" not in remaining_names, "Condition must be true"
    assert "epoch-0002" not in remaining_names, "Condition must be true"


def test_prune_checkpoints_keep_last_greater_than_total(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2])
    result = prune_checkpoints(tmp_path, keep_last=10)
    assert sorted(result["kept"]) == [1, 2]
    assert result["pruned"] == [], "Result must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — keep_every
# ---------------------------------------------------------------------------


def test_prune_checkpoints_keep_every(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    result = prune_checkpoints(tmp_path, keep_every=5)
    assert 5 in result["kept"], "Result must not be empty"
    assert 10 in result["kept"], "Result must not be empty"
    assert 1 in result["pruned"] or 2 in result["pruned"], "Result must not be empty"


def test_prune_checkpoints_keep_every_zero_ignored(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3])
    result = prune_checkpoints(tmp_path, keep_every=0)
    # No keep policy → all pruned
    assert sorted(result["pruned"]) == [1, 2, 3]


# ---------------------------------------------------------------------------
# prune_checkpoints — keep_last + keep_every combined
# ---------------------------------------------------------------------------


def test_prune_checkpoints_combined_keep(tmp_path: Path):
    _make_epoch_dirs(tmp_path, list(range(1, 11)))
    result = prune_checkpoints(tmp_path, keep_last=2, keep_every=5)
    # Epochs 5 and 10 kept (keep_every=5), 9 and 10 kept (keep_last=2)
    assert 5 in result["kept"], "Result must not be empty"
    assert 10 in result["kept"], "Result must not be empty"
    assert 9 in result["kept"], "Result must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — latest.json protection
# ---------------------------------------------------------------------------


def test_prune_checkpoints_protects_latest(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4, 5])
    _write_latest_json(tmp_path, 2)
    result = prune_checkpoints(tmp_path, keep_last=1)
    # Epoch 2 is protected even though keep_last=1 would normally exclude it
    assert 2 in result["kept"], "Result must not be empty"
    assert result["protected_latest"] == 2, "Result must not be empty"


def test_prune_checkpoints_protected_latest_none_when_no_latest_json(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2])
    result = prune_checkpoints(tmp_path, keep_last=1)
    assert result["protected_latest"] is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — max_epochs
# ---------------------------------------------------------------------------


def test_prune_checkpoints_max_epochs_limits_kept(tmp_path: Path):
    _make_epoch_dirs(tmp_path, list(range(1, 11)))
    result = prune_checkpoints(tmp_path, max_epochs=3)
    assert len(result["kept"]) <= 3, "Collection must not be empty"


def test_prune_checkpoints_max_epochs_keeps_newest(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4, 5])
    result = prune_checkpoints(tmp_path, max_epochs=2)
    assert 5 in result["kept"], "Result must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — dry_run
# ---------------------------------------------------------------------------


def test_prune_checkpoints_dry_run_does_not_delete(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3])
    result = prune_checkpoints(tmp_path, keep_last=1, dry_run=True)
    assert result["dry_run"] is True, "Result must not be empty"
    # All directories still exist
    for epoch in [1, 2, 3]:
        assert (tmp_path / f"epoch-{epoch:04d}").exists(), "Condition must be true"


def test_prune_checkpoints_dry_run_returns_plan(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4, 5])
    result = prune_checkpoints(tmp_path, keep_last=2, dry_run=True)
    assert sorted(result["pruned"]) == [1, 2, 3]
    assert sorted(result["kept"]) == [4, 5]


# ---------------------------------------------------------------------------
# prune_checkpoints — result structure
# ---------------------------------------------------------------------------


def test_prune_checkpoints_result_has_expected_keys(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3])
    result = prune_checkpoints(tmp_path, keep_last=1)
    assert "total" in result, "Result must not be empty"
    assert "kept" in result, "Result must not be empty"
    assert "pruned" in result, "Result must not be empty"
    assert "protected_latest" in result, "Result must not be empty"
    assert "dry_run" in result, "Result must not be empty"


def test_prune_checkpoints_total_matches_epoch_count(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3, 4])
    result = prune_checkpoints(tmp_path, keep_last=2)
    assert result["total"] == 4, "Result must not be empty"


def test_prune_checkpoints_kept_plus_pruned_equals_total(tmp_path: Path):
    _make_epoch_dirs(tmp_path, list(range(1, 8)))
    result = prune_checkpoints(tmp_path, keep_last=3, keep_every=3)
    assert len(result["kept"]) + len(result["pruned"]) == result["total"], "Collection must not be empty"


# ---------------------------------------------------------------------------
# prune_checkpoints — non-epoch directories are ignored
# ---------------------------------------------------------------------------


def test_prune_checkpoints_ignores_non_epoch_dirs(tmp_path: Path):
    _make_epoch_dirs(tmp_path, [1, 2, 3])
    (tmp_path / "best").mkdir()
    (tmp_path / "logs").mkdir()
    result = prune_checkpoints(tmp_path, keep_last=1)
    # Only 3 epoch dirs counted
    assert result["total"] == 3, "Result must not be empty"
    # Non-epoch dirs still exist
    assert (tmp_path / "best").exists(), "Condition must be true"
    assert (tmp_path / "logs").exists(), "Condition must be true"
