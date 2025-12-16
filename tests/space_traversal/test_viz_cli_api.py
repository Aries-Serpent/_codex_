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


# ============================================================================
# Docs Hub Tests (v1.5.5)
# ============================================================================


def test_generate_docs_hub(tmp_path: Path):
    """Test documentation hub HTML generation."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path, repo_name="Test Repo", version="1.5.5")

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content
    assert "Documentation Hub" in content
    assert "Test Repo" in content
    assert "1.5.5" in content


def test_docs_hub_has_mermaid_diagrams(tmp_path: Path):
    """Test docs hub includes Mermaid diagrams."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path)

    content = output_path.read_text()

    # Check for Mermaid
    assert "mermaid" in content.lower()
    assert "flowchart" in content or "sequenceDiagram" in content


def test_docs_hub_has_categories(tmp_path: Path):
    """Test docs hub has documentation categories."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path)

    content = output_path.read_text()

    # Check categories
    assert "Getting Started" in content
    assert "Audit Pipeline" in content
    assert "API Reference" in content


# ============================================================================
# Agent Interface Tests (v1.5.5)
# ============================================================================


def test_generate_agent_interface(tmp_path: Path):
    """Test agent interface HTML generation."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path, repo_name="Test Repo", version="1.5.5")

    assert output_path.exists()
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content
    assert "Agent" in content
    assert "Test Repo" in content
    assert "1.5.5" in content


def test_agent_interface_has_action_buttons(tmp_path: Path):
    """Test agent interface has action buttons."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check action buttons
    assert "Run Full Audit" in content
    assert "Check Regressions" in content
    assert "Generate Dashboard" in content


def test_agent_interface_has_capability_list(tmp_path: Path):
    """Test agent interface has capability selection list."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check capability list
    assert "capability" in content.lower()
    assert "checkbox" in content.lower()
    assert "checkpointing" in content


def test_agent_interface_has_machine_readable_data(tmp_path: Path):
    """Test agent interface has machine-readable metadata."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check machine-readable attributes
    assert "data-action" in content
    assert "application/json" in content
    assert "agent-commands" in content


# ============================================================================
# Wiki Generator Tests (v1.5.5)
# ============================================================================


def test_generate_wiki(tmp_path: Path):
    """Test wiki markdown generation."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    files = generate_wiki(wiki_dir, repo_name="Test Repo", version="1.5.5")

    assert len(files) >= 8
    assert (wiki_dir / "Home.md").exists()
    assert (wiki_dir / "Getting-Started.md").exists()
    assert (wiki_dir / "Architecture.md").exists()


def test_wiki_has_mermaid_diagrams(tmp_path: Path):
    """Test wiki pages include Mermaid diagrams."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    generate_wiki(wiki_dir)

    architecture = (wiki_dir / "Architecture.md").read_text()
    assert "mermaid" in architecture.lower()
    assert "flowchart" in architecture or "graph" in architecture


def test_wiki_has_sidebar(tmp_path: Path):
    """Test wiki has sidebar for navigation."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    generate_wiki(wiki_dir)

    assert (wiki_dir / "_Sidebar.md").exists()
    sidebar = (wiki_dir / "_Sidebar.md").read_text()
    assert "Home" in sidebar


def test_create_wiki_bundle(tmp_path: Path):
    """Test wiki bundle creation."""
    from scripts.space_traversal.wiki_generator import create_wiki_bundle
    import zipfile

    wiki_dir = tmp_path / "wiki"
    bundle_path = tmp_path / "wiki_bundle.zip"

    result = create_wiki_bundle(wiki_dir, bundle_path, "Test Repo", "1.5.5")

    assert result.exists()
    assert zipfile.is_zipfile(result)

    # Check bundle contents
    with zipfile.ZipFile(result, "r") as zf:
        names = zf.namelist()
        assert "Home.md" in names
        assert "manifest.json" in names


# ============================================================================
# Actions Usage Tracker Tests (v1.5.5)
# ============================================================================


def test_usage_tracker_init(tmp_path: Path):
    """Test usage tracker initialization."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker

    tracker = UsageTracker(tmp_path / "usage.json")
    assert tracker.data_path.parent.exists()


def test_usage_tracker_record_run(tmp_path: Path):
    """Test recording a workflow run."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker

    tracker = UsageTracker(tmp_path / "usage.json")
    run = tracker.record_run(
        workflow_name="test-workflow",
        run_id="12345",
        run_number=1,
        trigger="push",
        status="success",
        started_at="2024-01-01T00:00:00Z",
        duration_minutes=5.0,
        runner_type="ubuntu-latest",
    )

    assert run.workflow_name == "test-workflow"
    assert run.estimated_cost_usd == 5.0 * 0.008


def test_usage_tracker_get_summary(tmp_path: Path):
    """Test getting usage summary."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker
    from datetime import datetime

    tracker = UsageTracker(tmp_path / "usage.json")
    tracker.record_run(
        workflow_name="test-workflow",
        run_id="12345",
        run_number=1,
        trigger="push",
        status="success",
        started_at=datetime.now().isoformat(),
        duration_minutes=5.0,
    )

    summary = tracker.get_summary(days=30)
    assert summary.total_runs == 1
    assert summary.total_minutes == 5.0


def test_usage_tracker_cost_report(tmp_path: Path):
    """Test generating cost report."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker

    tracker = UsageTracker(tmp_path / "usage.json")
    report = tracker.get_cost_report()

    assert "GitHub Actions Usage Report" in report
    assert "Estimated Cost" in report


def test_usage_dashboard_html(tmp_path: Path):
    """Test generating usage dashboard HTML."""
    from scripts.space_traversal.actions_usage_tracker import (
        UsageTracker,
        generate_usage_dashboard_html,
    )

    tracker = UsageTracker(tmp_path / "usage.json")
    output_path = tmp_path / "dashboard.html"
    generate_usage_dashboard_html(tracker, output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert "GitHub Actions Usage" in content
    assert "Total Runs" in content
