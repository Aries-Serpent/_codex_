from __future__ import annotations

import importlib.util
from pathlib import Path


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Repository root not found from test path"
    raise RuntimeError(msg)


def _load_repo_map_module():
    module_path = _repo_root() / "src" / "codex_ml" / "cli" / "repo_map.py"
    spec = importlib.util.spec_from_file_location("codex_ml_cli_repo_map_under_test", module_path)
    assert spec is not None and spec.loader is not None, "spec must be initialized"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_list_top_level_ignores_hidden(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")

    items = repo_map._list_top_level(tmp_path)
    assert "[dir] docs/" in items, "Item must not be empty"
    assert " README.md" in items, "Item must not be empty"
    assert all(".hidden" not in item for item in items), "Item must not be empty"


def test_extract_scalars_from_text_parses_key_values(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    yaml_file = tmp_path / "sample.yaml"
    yaml_file.write_text("trace_mode: mirror\nrollout_ring: canary\n", encoding="utf-8")

    values = repo_map._extract_scalars_from_text(yaml_file, ["trace_mode", "rollout_ring"])
    assert values == {"trace_mode": "mirror", "rollout_ring": "canary"}


def test_collect_reasoning_sections_from_text_fallback(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    repo_map.yaml = None

    baseline = tmp_path / "configs" / "training" / "reasoning" / "baseline.yaml"
    baseline.parent.mkdir(parents=True)
    baseline.write_text(
        "trace_mode: mirror\npreset: phase31\nrollout_ring: ring-b\n",
        encoding="utf-8",
    )
    deploy = tmp_path / "configs" / "deploy" / "reasoning_pod.yaml"
    deploy.parent.mkdir(parents=True)
    deploy.write_text(
        "rollout_ring: canary\nCODEX_TRACE_MODE: explore\nCODEX_CURRICULUM_PHASE: phase31\n",
        encoding="utf-8",
    )

    summary, sections = repo_map._collect_reasoning_sections(tmp_path)
    assert "trace_mode" in summary, "Condition must be true"
    assert "curriculum.preset" in summary, "Condition must be true"
    assert "deployment.rollout_ring" in summary, "Condition must be true"
    assert sections["curriculum"], "Condition must be true"
    assert sections["rollout_ring"], "Condition must be true"


def test_render_repo_map_reasoning_status_include(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    repo_map.yaml = None
    repo_map.REPO_ROOT = tmp_path

    (tmp_path / "README.md").write_text("root", encoding="utf-8")
    baseline = tmp_path / "configs" / "training" / "reasoning" / "baseline.yaml"
    baseline.parent.mkdir(parents=True)
    baseline.write_text("trace_mode: mirror\npreset: phase31\n", encoding="utf-8")

    rendered = repo_map.render_repo_map(reasoning=True, include=["reasoning_status", "key_files"])
    assert "reasoning_status:" in rendered, "Condition must be true"
    assert "trace_mode" in rendered, "Condition must be true"
    assert ", "Condition must be true"


def test_render_repo_map_plain_top_level(tmp_path: Path) -> None:
    repo_map = _load_repo_map_module()
    repo_map.REPO_ROOT = tmp_path
    (tmp_path / "alpha").mkdir()
    (tmp_path / "zeta.txt").write_text("x", encoding="utf-8")

    rendered = repo_map.render_repo_map()
    assert "[dir] alpha/" in rendered, "Condition must be true"
    assert " zeta.txt" in rendered, "Condition must be true"
