"""Contract tests for the dated Copilot runtime tool inventory."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / ".codex" / "mcp" / "runtime_inventory_2026-08-01.json"

EXPECTED_RESEARCH_STARTUP = {
    "github-mcp-server/actions_get",
    "github-mcp-server/actions_list",
    "github-mcp-server/get_code_scanning_alert",
    "github-mcp-server/get_commit",
    "github-mcp-server/get_discussion",
    "github-mcp-server/get_discussion_comments",
    "github-mcp-server/get_file_contents",
    "github-mcp-server/get_job_logs",
    "github-mcp-server/get_label",
    "github-mcp-server/get_latest_release",
    "github-mcp-server/get_release_by_tag",
    "github-mcp-server/get_secret_scanning_alert",
    "github-mcp-server/get_tag",
    "github-mcp-server/issue_read",
    "github-mcp-server/list_branches",
    "github-mcp-server/list_code_scanning_alerts",
    "github-mcp-server/list_commits",
    "github-mcp-server/list_discussion_categories",
    "github-mcp-server/list_discussions",
    "github-mcp-server/list_issue_fields",
    "github-mcp-server/list_issue_types",
    "github-mcp-server/list_issues",
    "github-mcp-server/list_label",
    "github-mcp-server/list_pull_requests",
    "github-mcp-server/list_releases",
    "github-mcp-server/list_repository_collaborators",
    "github-mcp-server/list_secret_scanning_alerts",
    "github-mcp-server/list_tags",
    "github-mcp-server/pull_request_read",
    "github-mcp-server/search_code",
    "github-mcp-server/search_commits",
    "github-mcp-server/search_issues",
    "github-mcp-server/search_pull_requests",
    "github-mcp-server/search_repositories",
    "github-mcp-server/search_users",
    "github-mcp-server/web_search",
}

EXPECTED_PLAYWRIGHT = {
    "playwright-browser_click",
    "playwright-browser_close",
    "playwright-browser_console_messages",
    "playwright-browser_drag",
    "playwright-browser_evaluate",
    "playwright-browser_file_upload",
    "playwright-browser_fill_form",
    "playwright-browser_handle_dialog",
    "playwright-browser_hover",
    "playwright-browser_install",
    "playwright-browser_navigate",
    "playwright-browser_navigate_back",
    "playwright-browser_network_requests",
    "playwright-browser_press_key",
    "playwright-browser_resize",
    "playwright-browser_select_option",
    "playwright-browser_snapshot",
    "playwright-browser_tabs",
    "playwright-browser_take_screenshot",
    "playwright-browser_type",
    "playwright-browser_wait_for",
}


def _inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def test_exact_supplied_research_inventory() -> None:
    inventory = _inventory()
    startup = inventory["github_mcp"]["startup_identifiers"]

    assert len(startup) == len(set(startup)) == 36
    assert set(startup) == EXPECTED_RESEARCH_STARTUP
    assert inventory["counts"]["startup_research_inventory"] == 36


def test_callable_topology_separates_web_search() -> None:
    inventory = _inventory()
    github_tools = inventory["github_mcp"]["callable_tools"]
    companion = inventory["companion_tools"]

    assert len(github_tools) == len(set(github_tools)) == 35
    assert companion == [
        {
            "startup_identifier": "github-mcp-server/web_search",
            "callable_name": "web_search",
            "namespace_note": (
                "The supplied startup list groups this with GitHub research tools; "
                "the agent API exposes it as a standalone callable."
            ),
        }
    ]
    assert inventory["counts"]["github_mcp_callable_tools"] == 35
    assert inventory["counts"]["companion_web_tools"] == 1


def test_read_only_boundary_and_consolidated_methods() -> None:
    inventory = _inventory()
    github = inventory["github_mcp"]

    assert github["endpoint_mode"] == "read-only"
    assert github["supports_repository_variable_crud"] is False
    assert github["supports_secret_crud"] is False
    assert github["consolidated_methods"]["actions_get"] == [
        "get_workflow",
        "get_workflow_run",
        "get_workflow_job",
        "download_workflow_run_artifact",
        "get_workflow_run_usage",
        "get_workflow_run_logs_url",
    ]
    assert github["consolidated_methods"]["actions_list"] == [
        "list_workflows",
        "list_workflow_runs",
        "list_workflow_jobs",
        "list_workflow_run_artifacts",
    ]
    assert github["consolidated_methods"]["issue_read"] == [
        "get",
        "get_comments",
        "get_sub_issues",
        "get_parent",
        "get_labels",
    ]
    assert github["consolidated_methods"]["pull_request_read"] == [
        "get",
        "get_diff",
        "get_status",
        "get_files",
        "get_commits",
        "get_review_comments",
        "get_reviews",
        "get_comments",
        "get_check_runs",
    ]


def test_playwright_inventory_and_surface_totals() -> None:
    inventory = _inventory()
    playwright = inventory["playwright_mcp"]["callable_tools"]

    assert len(playwright) == len(set(playwright)) == 21
    assert set(playwright) == EXPECTED_PLAYWRIGHT
    assert inventory["counts"]["playwright_mcp_tools"] == 21
    assert inventory["counts"]["mcp_namespaced_tools"] == 56
    assert inventory["counts"]["surfaced_research_and_browser_capabilities"] == 57
