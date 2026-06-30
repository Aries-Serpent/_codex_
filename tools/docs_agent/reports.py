from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import utc_now, write_json


def write_campaign_plan(repo_root: Path) -> None:
    generated = repo_root / "docs-data" / "generated"
    agents = [
        ("Agent A", "Inventory Agent"),
        ("Agent B", "Schema Agent"),
        ("Agent C", "Converter Agent"),
        ("Agent D", "Relationship Agent"),
        ("Agent E", "Validation Agent"),
        ("Agent F", "Query Infrastructure Agent"),
        ("Agent G", "GitHub Actions Agent"),
        ("Agent H", "Copilot Tooling Agent"),
        ("Agent I", "Cleanup/Quarantine Agent"),
    ]
    plan = {
        "generated_at": utc_now(),
        "phase_plan": ["discovery", "schema", "conversion", "validation", "indexing", "governance"],
        "dependency_map": {
            "schema": ["inventory"],
            "conversion": ["schema", "policy"],
            "validation": ["conversion"],
            "indexing": ["validation"],
            "governance": ["indexing"],
        },
        "agents": [
            {
                "agent": code,
                "name": name,
                "purpose": name,
                "inputs": ["docs-data", "policy", "schemas"],
                "outputs": ["docs-data/generated"],
                "allowed_files": [
                    "docs-data/**",
                    "tools/docs_agent/**",
                    ".github/workflows/machine-readable-governance.yml",
                ],
                "forbidden_files": [".github/agents/**"],
                "dependencies": [],
                "acceptance_criteria": ["deterministic JSON output", "validation pass"],
                "rollback_notes": "Revert generated artifacts and rerun build_index.",
            }
            for code, name in agents
        ],
        "review_gates": ["schema_validation", "coverage_check", "query_health"],
        "risk_register": [
            "Large migration scope requires staged conversion.",
            "Strict policy may initially fail on unmanaged files.",
        ],
        "rollback_plan": ["Restore canonical JSONL from VCS", "Rebuild sqlite indexes"],
        "final_checklist": [
            "policy present",
            "schemas valid",
            "indexes built",
            "workflow configured",
        ],
    }
    write_json(generated / "migration-campaign-plan.json", plan)
    (generated / "migration-campaign-plan.txt").write_text(
        "Machine-readable migration campaign plan generated. See migration-campaign-plan.json\n",
        encoding="utf-8",
    )


def write_cleanup_reports(
    repo_root: Path, convert_candidates: list[str], quarantine: list[str]
) -> None:
    generated = repo_root / "docs-data" / "generated"
    write_json(
        generated / "deletion-candidates.json",
        {
            "generated_at": utc_now(),
            "candidates": sorted(convert_candidates),
            "criteria": [
                "successfully converted",
                "validation passes",
                "indexed records exist",
                "not in allowed exceptions",
            ],
        },
    )
    write_json(
        generated / "quarantine-candidates.json",
        {
            "generated_at": utc_now(),
            "candidates": sorted(quarantine),
            "criteria": [
                "conversion warnings",
                "low classification confidence",
                "uncertain external dependency",
            ],
        },
    )


def write_tool_contract(repo_root: Path) -> None:
    generated = repo_root / "docs-data" / "generated"
    tools = [
        ("get_agent_context", True),
        ("search_docs", True),
        ("get_document", True),
        ("get_related_context", True),
        ("get_task_brief", True),
        ("impact_analysis", True),
        ("list_actions", True),
        ("validate_docs", True),
        ("classify_candidate_file", True),
        ("update_action_status", False),
        ("ingest_candidate_file", False),
        ("rebuild_indexes", False),
    ]
    contract = {
        "generated_at": utc_now(),
        "tools": [
            {
                "tool_name": name,
                "purpose": name.replace("_", " "),
                "read_only": ro,
                "safety_notes": "Deterministic JSON output required.",
                "required_validation_after_use": [] if ro else ["validate_docs", "rebuild_indexes"],
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"},
            }
            for name, ro in tools
        ],
    }
    write_json(generated / "copilot-tool-contract.json", contract)
    write_json(
        generated / "copilot-mcp-config.example.json",
        {
            "server": {
                "command": "python",
                "args": ["-m", "tools.docs_agent.mcp_server"],
                "transport": "stdio",
            },
            "notes": "Template only. Do not commit real secrets.",
        },
    )


def write_final_report(repo_root: Path, summary: dict[str, Any]) -> None:
    generated = repo_root / "docs-data" / "generated"
    report = {"generated_at": utc_now(), **summary}
    write_json(generated / "final-machine-readable-infra-report.json", report)
