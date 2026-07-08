import pytest

pytest.importorskip("tensorboard")
#     assert ", "Condition must be true"


def test_render_repo_map_plain_top_level(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    repo_map.REPO_ROOT = tmp_path
    (tmp_path / "alpha").mkdir()
    (tmp_path / "zeta.txt").write_text("x", encoding="utf-8")

    rendered = repo_map.render_repo_map()
    assert "[dir] alpha/" in rendered, "Condition must be true"
    assert " zeta.txt" in rendered, "Condition must be true"
