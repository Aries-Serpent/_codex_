"""Phase 12 System Integration - RBAC, Governance, Observability integration with machine-readable layer."""

import json
from tools.docs_agent.copilot_tools_new import CopilotToolsInterface
from typing import Dict, Any


class Phase12SystemIntegration:
    """Integrates Phase 12 systems (RBAC, Governance, Observability) with machine-readable data."""

    def __init__(self):
        self.tools = CopilotToolsInterface()
        self.phase_12_id = "08f847f2-9788-9343-eca2-a41e6c32a12a"

    def rbac_integration(self) -> Dict[str, Any]:
        """Integration: RBAC maps roles to structured entity IDs."""
        rbac_design = {
            "authorization_model": "Roles map to entities in agents.jsonl",
            "role_definitions": {
                "admin": {
                    "granted_agents": ["rbac-controller", "governance-enforcer"],
                    "permissions": ["manage_phases", "manage_tracks", "approve_decisions"],
                    "entity_scopes": ["phase_id", "track_id"]
                },
                "contributor": {
                    "granted_agents": ["deliverable_owner", "metric_reporter"],
                    "permissions": ["create_deliverables", "report_metrics", "propose_changes"],
                    "entity_scopes": ["track_id", "deliverable_id"]
                },
                "observer": {
                    "granted_agents": ["metric_observer"],
                    "permissions": ["view_metrics", "read_decisions", "search_docs"],
                    "entity_scopes": ["phase_id"],
                    "tools": ["get_agent_context", "search_docs", "list_actions"]
                }
            },
            "resource_level_permissions": {
                "phase_access": "scope_phase_id",
                "track_access": "scope_track_id",
                "deliverable_access": "scope_deliverable_id",
                "decision_access": "scope_decision_id"
            },
            "enforcement_pattern": "All Copilot tools filter results by role's entity scopes"
        }
        
        return rbac_design

    def governance_integration(self) -> Dict[str, Any]:
        """Integration: Governance approvals reference deliverables/actions in JSONL."""
        governance_design = {
            "approval_workflow": "Phase gate decisions from decisions.jsonl",
            "approval_structure": {
                "phase_gate_approval": {
                    "references": "phase_id from campaign_phases.jsonl",
                    "example": {
                        "approval_id": "approve_phase_10",
                        "decision_reference": "decision_gate_phase_10",
                        "affected_deliverables": 12,
                        "status": "approved",
                        "approver": "admin_role",
                        "authority": "D-tier"
                    }
                },
                "deliverable_approval": {
                    "references": "deliverable_id from deliverables.jsonl",
                    "policy_enforcement": "Track→Deliverable→Agent responsibility chain",
                    "example": {
                        "approval_id": "approve_deliv_123",
                        "deliverable_reference": "deliverable_456",
                        "track_context": "track_10_1",
                        "upstream_requirements": "from requirements.jsonl",
                        "approval_status": "pending_review"
                    }
                }
            },
            "policy_references": "Policies reference decision_id and requirement_id",
            "audit_trail": "All decisions stored in decisions.jsonl with timestamp and authority"
        }
        
        return governance_design

    def observability_integration(self) -> Dict[str, Any]:
        """Integration: Observability metrics query structured data."""
        observability_design = {
            "metrics_source": "SQLite FTS queries over metrics.jsonl",
            "dashboard_data_flow": {
                "step_1": "Query metrics.jsonl filtered by phase_id",
                "step_2": "Correlate with deliverables.jsonl (test_coverage_percent)",
                "step_3": "Link to requirements.jsonl (actual_value vs target_value)",
                "step_4": "Render as dashboard with real-time SQLite queries"
            },
            "key_metrics": {
                "phase_health": {
                    "query": "SELECT COUNT(*) FROM deliverables WHERE phase_id=? AND status='complete'",
                    "dashboard_display": "Phase completion percentage"
                },
                "track_progress": {
                    "query": "SELECT AVG(test_coverage_percent) FROM deliverables WHERE track_id=?",
                    "dashboard_display": "Track average coverage"
                },
                "requirement_compliance": {
                    "query": "SELECT COUNT(*) FROM requirements WHERE phase_id=? AND status='met'",
                    "dashboard_display": "Requirements passed / total"
                },
                "agent_activity": {
                    "query": "SELECT agent_id, phase_id FROM agents",
                    "dashboard_display": "Agent assignments by phase"
                }
            },
            "alert_policy": "Thresholds trigger via validate_docs() and get_task_brief() checks",
            "real_time_capability": "SQLite FTS enables <100ms dashboard refresh"
        }
        
        return observability_design

    def governance_workflow_specification(self) -> Dict[str, Any]:
        """Specification for GitHub Actions governance workflow."""
        workflow_spec = {
            "workflow_name": "machine-readable-governance.yml",
            "triggers": ["push", "pull_request"],
            "steps": [
                {
                    "name": "Detect Changed Files",
                    "purpose": "Identify new/modified campaign files"
                },
                {
                    "name": "Classify All Candidates",
                    "tool": "classify_candidate_file()",
                    "classifies": ["managed vs unmanaged", "campaign vs infrastructure"]
                },
                {
                    "name": "Enforce Ingestion",
                    "tool": "ingest_candidate_file()",
                    "requirement": "All managed files must pass ingestion"
                },
                {
                    "name": "Validate JSONL Schema",
                    "requirement": "All .jsonl files must have id, phase_id/track_id, source_trace"
                },
                {
                    "name": "Rebuild SQLite",
                    "tool": "rebuild_indexes()",
                    "validates": "Foreign keys, relationships, FTS indexes"
                },
                {
                    "name": "Validate Tools",
                    "tool": "validate_docs()",
                    "checks": ["no orphaned deliverables", "all relationships valid"]
                },
                {
                    "name": "FAIL on Unmanaged",
                    "condition": "Unmanaged files found",
                    "action": "Block PR merge, require classification"
                }
            ],
            "success_criteria": [
                "All managed files ingested",
                "Valid JSONL",
                "No orphaned relationships",
                "SQLite indexes operational",
                "All 10 tools working"
            ]
        }
        
        return workflow_spec

    def continuous_ingestion_pipeline(self) -> Dict[str, Any]:
        """Design for continuous ingestion lifecycle (PART 8)."""
        pipeline = {
            "pipeline_phases": [
                {
                    "phase": "Detect",
                    "action": "Changed files (git diff)",
                    "output": "Candidate list"
                },
                {
                    "phase": "Classify",
                    "tool": "classify_candidate_file()",
                    "branches": {
                        "managed": "→ Ingest",
                        "unmanaged": "→ Report + Block"
                    }
                },
                {
                    "phase": "Ingest",
                    "tool": "ingest_candidate_file()",
                    "process": "Parse → Generate JSONL → Add record IDs"
                },
                {
                    "phase": "Validate",
                    "tool": "validate_docs()",
                    "checks": ["schema", "relationships", "foreign keys"]
                },
                {
                    "phase": "Index",
                    "tool": "rebuild_indexes()",
                    "rebuilds": ["SQLite FTS", "Relationships graph"]
                },
                {
                    "phase": "Enforce",
                    "action": "CI gate blocks unmanaged files",
                    "requirement": "Zero tolerance for unmanaged knowledge"
                }
            ],
            "automation_coverage": "100% - Manual ingestion prohibited after CI enforcement"
        }
        
        return pipeline


if __name__ == "__main__":
    integration = Phase12SystemIntegration()
    
    print("=== Phase 12 System Integration ===\n")
    
    rbac = integration.rbac_integration()
    print(f"RBAC Integration: {len(rbac['role_definitions'])} roles with entity-level permissions")
    
    governance = integration.governance_integration()
    print(f"Governance Integration: Approval workflows reference structured decision and deliverable IDs")
    
    observability = integration.observability_integration()
    print(f"Observability Integration: {len(observability['key_metrics'])} dashboard metrics via SQLite")
    
    workflow = integration.governance_workflow_specification()
    print(f"Governance Workflow: {len(workflow['steps'])} automated steps")
    
    pipeline = integration.continuous_ingestion_pipeline()
    print(f"Ingestion Pipeline: {len(pipeline['pipeline_phases'])} phases")
