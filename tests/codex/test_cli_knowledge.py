"""Smoke test for codex.cli_knowledge Typer app."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Skip if typer is not properly installed
try:
    import typer

    if not hasattr(typer, "Typer"):
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
    assert result.exit_code == 0, "Result must not be empty"
    assert result.output, "Result must not be empty"


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
    assert payload["ok"] is True, "Condition must be true"
    assert payload["node_count"] == 3, "Count must be greater than zero"
    assert payload["edge_count"] == 2, "Count must be greater than zero"
    assert payload["token_count"] > 0, "Value must be greater than zero"

    blob_path = Path(payload["blob"])
    search_path = Path(payload["search_records"])
    compressed_path = Path(payload["compressed_blob"])
    assert blob_path.exists(), "Condition must be true"
    assert search_path.exists(), "Condition must be true"
    assert compressed_path.exists(), "Condition must be true"

    blob = json.loads(blob_path.read_text(encoding="utf-8"))
    assert blob["quantum_mapping"]["equation"] == "ψ = α·N + β·E + γ·V + δ·T", "Condition must be true"
    assert blob["search_index"]["records"] >= 1, "Value must be greater than zero"

    # Validate coherence score formula: ψ = α·N + β·E + γ·V + δ·T
    qm = blob["quantum_mapping"]
    v = qm["variables"]
    c = qm["coefficients"]
    expected_score = (
        c["alpha"] * v["N"] + c["beta"] * v["E"] + c["gamma"] * v["V"] + c["delta"] * v["T"]
    )
    assert (abs(qm["coherence_score"] - round(expected_score, 4)) < 1e-6
    ), f"coherence_score {qm['coherence_score']} != expected {round(expected_score, 4)}"

    # Validate compression roundtrip
    from codex.archive.util import zstd_decompress

    decompressed = zstd_decompress(compressed_path.read_bytes())
    assert json.loads(decompressed) == blob, "Condition must be true"
