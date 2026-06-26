"""Tests for CLI builder and API collection HTML generators (v1.5.3-1.5.4)."""

from __future__ import annotations

from pathlib import Path


def test_generate_cli_builder(tmp_path: Path):
    """Test CLI builder HTML generation."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path, repo_name="Test Repo", version="1.5.3")

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content, "Content must not be empty"
    assert "Audit CLI Builder" in content, "Content must not be empty"
    assert "Test Repo" in content, "Content must not be empty"
    assert "1.5.3" in content, "Content must not be empty"

    # Check command buttons exist
    assert "run" in content, "Content must not be empty"
    assert "validate" in content, "Content must not be empty"
    assert "store-trend" in content, "Content must not be empty"
    assert "show-trend" in content, "Content must not be empty"
    assert "check-regressions" in content, "Content must not be empty"
    assert "compare-runs" in content, "Content must not be empty"
    assert "dashboard" in content, "Content must not be empty"


def test_cli_builder_has_knobs(tmp_path: Path):
    """Test CLI builder includes knob/slider controls."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for slider/knob elements
    assert "knob-slider" in content or "rotary-knob" in content, "Content must not be empty"
    assert "knob-value" in content, "Value must be initialized"
    assert 'type="range"' in content, "Content must not be empty"


def test_cli_builder_has_form_controls(tmp_path: Path):
    """Test CLI builder has form input controls."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for form controls
    assert "form-input" in content, "Content must not be empty"
    assert "form-select" in content, "Content must not be empty"
    assert "placeholder=" in content, "Content must not be empty"


def test_cli_builder_command_preview(tmp_path: Path):
    """Test CLI builder has command preview section."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "cli_builder.html"
    generate_cli_builder(output_path)

    content = output_path.read_text()

    # Check for preview elements
    assert "command-preview" in content or "preview-box" in content, "Content must not be empty"
    assert "python -m scripts.space_traversal.audit_runner" in content, "Content must not be empty"
    assert "Copy" in content, "Content must not be empty"


def test_cli_builder_creates_parent_dirs(tmp_path: Path):
    """Test CLI builder creates parent directories."""
    from scripts.space_traversal.viz_cli_builder import generate_cli_builder

    output_path = tmp_path / "nested" / "dir" / "cli_builder.html"
    generate_cli_builder(output_path)

    assert output_path.exists(), "Condition must be true"


def test_generate_api_collection(tmp_path: Path):
    """Test API collection HTML generation."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path, repo_name="Test Repo", version="1.5.4")

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content, "Content must not be empty"
    assert "API Collection" in content, "Content must not be empty"
    assert "Test Repo" in content, "Content must not be empty"


def test_api_collection_has_folders(tmp_path: Path):
    """Test API collection has folder structure."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check for collection folders
    assert "Audit Commands" in content, "Content must not be empty"
    assert "Trend Analysis" in content, "Content must not be empty"
    assert "Saved Presets" in content, "Content must not be empty"


def test_api_collection_has_adjusters(tmp_path: Path):
    """Test API collection has adjuster controls."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check for adjuster elements
    assert "rotary-knob" in content, "Content must not be empty"
    assert "slider" in content, "Content must not be empty"
    assert "adjuster" in content.lower(), "Content must not be empty"


def test_api_collection_has_command_items(tmp_path: Path):
    """Test API collection has all command items."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check command items exist
    assert "Full Pipeline" in content, "Content must not be empty"
    assert "Validate" in content, "Content must not be empty"
    assert "Store Trend" in content, "Content must not be empty"
    assert "Show Trend" in content, "Content must not be empty"
    assert "Check Regressions" in content, "Content must not be empty"
    assert "Compare" in content, "Content must not be empty"


def test_api_collection_save_preset(tmp_path: Path):
    """Test API collection has save preset functionality."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check save modal elements
    assert "save-modal" in content or "Save" in content, "Content must not be empty"
    assert "Preset Name" in content or "preset-name" in content, "Content must not be empty"
    assert "localStorage" in content, "Content must not be empty"


def test_api_collection_history(tmp_path: Path):
    """Test API collection has command history."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "api_collection.html"
    generate_api_collection(output_path)

    content = output_path.read_text()

    # Check history elements
    assert "history" in content.lower(), "Content must not be empty"
    assert "Recent" in content, "Content must not be empty"


def test_api_collection_creates_parent_dirs(tmp_path: Path):
    """Test API collection creates parent directories."""
    from scripts.space_traversal.viz_api_collection import generate_api_collection

    output_path = tmp_path / "nested" / "dir" / "api_collection.html"
    generate_api_collection(output_path)

    assert output_path.exists(), "Condition must be true"


def test_generate_swagger_docs(tmp_path: Path):
    """Test Swagger documentation HTML generation."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path, repo_name="Test Repo", version="1.5.4")

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content, "Content must not be empty"
    assert "Audit CLI API" in content, "Content must not be empty"
    assert "Test Repo" in content, "Content must not be empty"
    assert "1.5.4" in content, "Content must not be empty"


def test_swagger_has_endpoints(tmp_path: Path):
    """Test Swagger docs has all endpoint sections."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check endpoint sections
    assert "Full Pipeline" in content, "Content must not be empty"
    assert "Single Stage" in content, "Content must not be empty"
    assert "Validate" in content, "Content must not be empty"
    assert "Explain" in content, "Content must not be empty"
    assert "Store Trend" in content, "Content must not be empty"
    assert "Show Trend" in content, "Content must not be empty"
    assert "Check Regressions" in content, "Content must not be empty"
    assert "Dashboard" in content, "Content must not be empty"


def test_swagger_has_try_it_out(tmp_path: Path):
    """Test Swagger docs has try-it-out functionality."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check try-it-out elements
    assert "Try It Out" in content, "Content must not be empty"
    assert "Execute" in content, "Content must not be empty"
    assert "Copy" in content, "Content must not be empty"
    assert "try-form" in content, "Content must not be empty"


def test_swagger_has_parameters(tmp_path: Path):
    """Test Swagger docs shows parameters."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check parameter documentation
    assert "Parameters" in content, "Content must not be empty"
    assert "required" in content, "Content must not be empty"
    assert "default" in content, "Content must not be empty"
    assert "--threshold" in content, "Content must not be empty"
    assert "--limit" in content, "Content must not be empty"


def test_swagger_has_openapi_download(tmp_path: Path):
    """Test Swagger docs has OpenAPI spec download."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "api_docs.html"
    generate_swagger_docs(output_path)

    content = output_path.read_text()

    # Check OpenAPI download
    assert "downloadOpenAPI" in content, "Content must not be empty"
    assert "OpenAPI" in content or "openapi" in content, "Content must not be empty"


def test_swagger_creates_parent_dirs(tmp_path: Path):
    """Test Swagger docs creates parent directories."""
    from scripts.space_traversal.viz_swagger import generate_swagger_docs

    output_path = tmp_path / "nested" / "dir" / "api_docs.html"
    generate_swagger_docs(output_path)

    assert output_path.exists(), "Condition must be true"


# ============================================================================
# Docs Hub Tests (v1.5.5)
# ============================================================================


def test_generate_docs_hub(tmp_path: Path):
    """Test documentation hub HTML generation."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path, repo_name="Test Repo", version="1.5.5")

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content, "Content must not be empty"
    assert "Documentation Hub" in content, "Content must not be empty"
    assert "Test Repo" in content, "Content must not be empty"
    assert "1.5.5" in content, "Content must not be empty"


def test_docs_hub_has_mermaid_diagrams(tmp_path: Path):
    """Test docs hub includes Mermaid diagrams."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path)

    content = output_path.read_text()

    # Check for Mermaid
    assert "mermaid" in content.lower(), "Content must not be empty"
    assert "flowchart" in content or "sequenceDiagram" in content, "Content must not be empty"


def test_docs_hub_has_categories(tmp_path: Path):
    """Test docs hub has documentation categories."""
    from scripts.space_traversal.viz_docs_hub import generate_docs_hub

    output_path = tmp_path / "docs_hub.html"
    generate_docs_hub(output_path)

    content = output_path.read_text()

    # Check categories
    assert "Getting Started" in content, "Content must not be empty"
    assert "Audit Pipeline" in content, "Content must not be empty"
    assert "API Reference" in content, "Content must not be empty"


# ============================================================================
# Agent Interface Tests (v1.5.5)
# ============================================================================


def test_generate_agent_interface(tmp_path: Path):
    """Test agent interface HTML generation."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path, repo_name="Test Repo", version="1.5.5")

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()

    # Check essential elements
    assert "<!DOCTYPE html>" in content, "Content must not be empty"
    assert "Agent" in content, "Content must not be empty"
    assert "Test Repo" in content, "Content must not be empty"
    assert "1.5.5" in content, "Content must not be empty"


def test_agent_interface_has_action_buttons(tmp_path: Path):
    """Test agent interface has action buttons."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check action buttons
    assert "Run Full Audit" in content, "Content must not be empty"
    assert "Check Regressions" in content, "Content must not be empty"
    assert "Generate Dashboard" in content, "Content must not be empty"


def test_agent_interface_has_capability_list(tmp_path: Path):
    """Test agent interface has capability selection list."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check capability list
    assert "capability" in content.lower(), "Content must not be empty"
    assert "checkbox" in content.lower(), "Content must not be empty"
    assert "checkpointing" in content, "Content must not be empty"


def test_agent_interface_has_machine_readable_data(tmp_path: Path):
    """Test agent interface has machine-readable metadata."""
    from scripts.space_traversal.viz_agent_interface import generate_agent_interface

    output_path = tmp_path / "agent_interface.html"
    generate_agent_interface(output_path)

    content = output_path.read_text()

    # Check machine-readable attributes
    assert "data-action" in content, "Data must not be empty"
    assert "application/json" in content, "Content must not be empty"
    assert "agent-commands" in content, "Content must not be empty"


# ============================================================================
# Wiki Generator Tests (v1.5.5)
# ============================================================================


def test_generate_wiki(tmp_path: Path):
    """Test wiki markdown generation."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    files = generate_wiki(wiki_dir, repo_name="Test Repo", version="1.5.5")

    assert len(files) >= 8, "Files must not be empty"
    assert (wiki_dir / "Home.md").exists(), "Condition must be true"
    assert (wiki_dir / "Getting-Started.md").exists(), "Condition must be true"
    assert (wiki_dir / "Architecture.md").exists(), "Condition must be true"


def test_wiki_has_mermaid_diagrams(tmp_path: Path):
    """Test wiki pages include Mermaid diagrams."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    generate_wiki(wiki_dir)

    architecture = (wiki_dir / "Architecture.md").read_text()
    assert "mermaid" in architecture.lower(), "Condition must be true"
    assert "flowchart" in architecture or "graph" in architecture, "Condition must be true"


def test_wiki_has_sidebar(tmp_path: Path):
    """Test wiki has sidebar for navigation."""
    from scripts.space_traversal.wiki_generator import generate_wiki

    wiki_dir = tmp_path / "wiki"
    generate_wiki(wiki_dir)

    assert (wiki_dir / "_Sidebar.md").exists(), "Condition must be true"
    sidebar = (wiki_dir / "_Sidebar.md").read_text()
    assert "Home" in sidebar, "Condition must be true"


def test_create_wiki_bundle(tmp_path: Path):
    """Test wiki bundle creation."""
    import zipfile

    from scripts.space_traversal.wiki_generator import create_wiki_bundle

    wiki_dir = tmp_path / "wiki"
    bundle_path = tmp_path / "wiki_bundle.zip"

    result = create_wiki_bundle(wiki_dir, bundle_path, "Test Repo", "1.5.5")

    assert result.exists(), "Result must not be empty"
    assert zipfile.is_zipfile(result), "Result must not be empty"

    # Check bundle contents
    with zipfile.ZipFile(result, "r") as zf:
        names = zf.namelist()
        assert "Home.md" in names, "Condition must be true"
        assert "manifest.json" in names, "Condition must be true"


# ============================================================================
# Actions Usage Tracker Tests (v1.5.5)
# ============================================================================


def test_usage_tracker_init(tmp_path: Path):
    """Test usage tracker initialization."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker

    tracker = UsageTracker(tmp_path / "usage.json")
    assert tracker.data_path.parent.exists(), "Data must not be empty"


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

    assert run.workflow_name == "test-workflow", "workflow_name is not valid"
    assert run.estimated_cost_usd == 5.0 * 0.008, "estimated_cost_usd is not valid"


def test_usage_tracker_get_summary(tmp_path: Path):
    """Test getting usage summary."""
    from datetime import datetime

    from scripts.space_traversal.actions_usage_tracker import UsageTracker

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
    assert summary.total_runs == 1, "total_runs is not valid"
    assert summary.total_minutes == 5.0, "total_minutes is not valid"


def test_usage_tracker_cost_report(tmp_path: Path):
    """Test generating cost report."""
    from scripts.space_traversal.actions_usage_tracker import UsageTracker

    tracker = UsageTracker(tmp_path / "usage.json")
    report = tracker.get_cost_report()

    assert "GitHub Actions Usage Report" in report, "Condition must be true"
    assert "Estimated Cost" in report, "Condition must be true"


def test_usage_dashboard_html(tmp_path: Path):
    """Test generating usage dashboard HTML."""
    from scripts.space_traversal.actions_usage_tracker import (
        UsageTracker,
        generate_usage_dashboard_html,
    )

    tracker = UsageTracker(tmp_path / "usage.json")
    output_path = tmp_path / "dashboard.html"
    generate_usage_dashboard_html(tracker, output_path)

    assert output_path.exists(), "Condition must be true"
    content = output_path.read_text()
    assert "GitHub Actions Usage" in content, "Content must not be empty"
    assert "Total Runs" in content, "Content must not be empty"
