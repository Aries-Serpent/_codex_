"""Smoke test for codex.cli_knowledge Typer app."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Skip if typer is not properly installed
try:
    import typer
    if not hasattr(typer, 'Typer'):
        pytest.skip("typer package not properly installed", allow_module_level=True)
    from typer.testing import CliRunner

    from codex import cli_knowledge
    TYPER_AVAILABLE = True
except (ImportError, AttributeError):
    TYPER_AVAILABLE = False
    pytest.skip("typer package not available", allow_module_level=True)


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="typer not available")
def test_cli_knowledge_help():
    runner = CliRunner()
    result = runner.invoke(cli_knowledge.app, ["--help"])
    assert result.exit_code == 0
    assert result.output


@pytest.mark.skipif(not TYPER_AVAILABLE, reason="typer not available")
def test_sync_mermaid_map_generates_searchable_datablobs(tmp_path: Path):
    mermaid = tmp_path / "map.mmd"
    mermaid.write_text(
        "\n".join(
            [
                "flowchart TD",
                'A["Start"] --> B["Middle"]',
                'B --> C["End"]',
            ]
        ),
        encoding="utf-8",
    )
    mapping_doc = tmp_path / "map.md"
    mapping_doc.write_text(
        "\n".join(
            [
                "# Runtime Map",
                "",
                "Quantum mapping variables: N E V T.",
                "",
                "## Notes",
                "Mermaid source of truth.",
            ]
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    runner = CliRunner()
    result = runner.invoke(
        cli_knowledge.app,
        [
            "sync-mermaid-map",
            "--mermaid",
            str(mermaid),
            "--mapping-doc",
            str(mapping_doc),
            "--out-dir",
            str(out_dir),
            "--compress",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["node_count"] == 3
    assert payload["edge_count"] == 2
    assert payload["token_count"] > 0

    blob_path = Path(payload["blob"])
    search_path = Path(payload["search_records"])
    compressed_path = Path(payload["compressed_blob"])
    assert blob_path.exists()
    assert search_path.exists()
    assert compressed_path.exists()

    blob = json.loads(blob_path.read_text(encoding="utf-8"))
    assert blob["quantum_mapping"]["equation"] == "ψ = α·N + β·E + γ·V + δ·T"
    assert blob["search_index"]["records"] >= 1
