"""Tests for CLI builder and API collection HTML generators (v1.5.3-1.5.4)."""
from __future__ import annotations

from pathlib import Path


def test_generate_cli_builder(tmp_path: Path):
    """Test CLI builder HTML generation."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path, repo_name="Test Repo", version="1.5.3")

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content
    assert "Audit CLI Builder" in content
    assert "Test Repo" in content
    assert "1.5.3" in content

    # Check command buttons exist
    assert "run" in content
    assert "validate" in content
    assert "store-trend" in content
    assert "show-trend" in content
    assert "check-regressions" in content
    assert "compare-runs" in content
    assert "dashboard" in content


def test_cli_builder_has_knobs(tmp_path: Path):
    """Test CLI builder includes knob/slider controls."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for slider/knob elements
    assert "knob-slider" in content or "rotary-knob" in content
    assert "knob-value" in content
    assert 'type="range"' in content


def test_cli_builder_has_form_controls(tmp_path: Path):
    """Test CLI builder has form input controls."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for form controls
    assert "form-input" in content
    assert "form-select" in content
    assert "placeholder=" in content


def test_cli_builder_command_preview(tmp_path: Path):
    """Test CLI builder has command preview section."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for preview elements
    assert "command-preview" in content or "preview-box" in content
    assert "python -m scripts.space_traversal.audit_runner" in content
    assert "Copy" in content


def test_cli_builder_creates_parent_dirs(tmp_path: Path):
    """Test CLI builder creates parent directories."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "nested" / "dir" / "cli_builder.html"
    generate_cli_builder(output_path)

    assert output_path.exists()


def test_generate_api_collection(tmp_path: Path):
    """Test API collection HTML generation."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path, repo_name="Test Repo", version="1.5.4")

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content
    assert "API Collection" in content
    assert "Test Repo" in content


def test_api_collection_has_folders(tmp_path: Path):
    """Test API collection has folder structure."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check for collection folders
    assert "Audit Commands" in content
    assert "Trend Analysis" in content
    assert "Saved Presets" in content


def test_api_collection_has_adjusters(tmp_path: Path):
    """Test API collection has adjuster controls."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check for adjuster elements
    assert "rotary-knob" in content
    assert "slider" in content
    assert "adjuster" in content.lower()


def test_api_collection_has_command_items(tmp_path: Path):
    """Test API collection has all command items."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check command items exist
    assert "Full Pipeline" in content
    assert "Validate" in content
    assert "Store Trend" in content
    assert "Show Trend" in content
    assert "Check Regressions" in content
    assert "Compare" in content


def test_api_collection_save_preset(tmp_path: Path):
    """Test API collection has save preset functionality."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check save modal elements
    assert "save-modal" in content or "Save" in content
    assert "Preset Name" in content or "preset-name" in content
    assert "localStorage" in content


def test_api_collection_history(tmp_path: Path):
    """Test API collection has command history."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check history elements
    assert "history" in content.lower()
    assert "Recent" in content


def test_api_collection_creates_parent_dirs(tmp_path: Path):
    """Test API collection creates parent directories."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "nested" / "dir" / "api_collection.html"
    generate_api_collection(output_path)

    assert output_path.exists()


def test_generate_swagger_docs(tmp_path: Path):
    """Test Swagger documentation HTML generation."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path, repo_name="Test Repo", version="1.5.4")

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content
    assert "Audit CLI API" in content
    assert "Test Repo" in content
    assert "1.5.4" in content


def test_swagger_has_endpoints(tmp_path: Path):
    """Test Swagger docs has all endpoint sections."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check endpoint sections
    assert "Full Pipeline" in content
    assert "Single Stage" in content
    assert "Validate" in content
    assert "Explain" in content
    assert "Store Trend" in content
    assert "Show Trend" in content
    assert "Check Regressions" in content
    assert "Dashboard" in content


def test_swagger_has_try_it_out(tmp_path: Path):
    """Test Swagger docs has try-it-out functionality."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check try-it-out elements
    assert "Try It Out" in content
    assert "Execute" in content
    assert "Copy" in content
    assert "try-form" in content


def test_swagger_has_parameters(tmp_path: Path):
    """Test Swagger docs shows parameters."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check parameter documentation
    assert "Parameters" in content
    assert "required" in content
    assert "default" in content
    assert "--threshold" in content
    assert "--limit" in content


def test_swagger_has_openapi_download(tmp_path: Path):
    """Test Swagger docs has OpenAPI spec download."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check OpenAPI download
    assert "downloadOpenAPI" in content
    assert "OpenAPI" in content or "openapi" in content


def test_swagger_creates_parent_dirs(tmp_path: Path):
    """Test Swagger docs creates parent directories."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "nested" / "dir" / "api_docs.html"
    generate_swagger_docs(output_path)

    assert output_path.exists()
