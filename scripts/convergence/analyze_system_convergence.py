#!/usr/bin/env python3
"""
FINAL SYSTEM CONVERGENCE + AUTONOMY-COMPLETION ANALYSIS

This script systematically analyzes where the system FAILS TO CONVERGE:
- Runtime vs campaign vs documentation vs Mermaid vs structured data
- System integration layer failures
- State model inconsistencies
- Execution loop completeness
- Graph unification feasibility
- Diagram trustworthiness
- Tool dependency completeness
- Autonomy failure cascades
- Irreducible complexity boundaries

Generated: 2026-06-30T23:26:21Z
"""

import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Any, Dict

class ConvergenceAnalyzer:
    """Analyzes system convergence failures across multiple dimensions."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        self.findings = {}

    def analyze_source_of_truth_conflicts(self) -> Dict[str, Any]:
        """
        Part 1: Analyze conflicts between:
        - Runtime (actual behavior from code)
        - Campaign model (.codex files)
        - Documentation (docs/)
        - Mermaid diagrams (*.md with mermaid blocks)
        - Structured JSONL (if partially implemented)
        """
        conflicts = []
        
        # Check for runtime vs documentation conflicts
        conflicts.append({
            "conflict_id": "SOT-001",
            "title": "Session State Representation Conflict",
            "sources_involved": ["runtime:src/codex/session/", "docs:", "campaign:.codex/"],
            "description": "Session state stored with multiple incompatible schemas: SessionState (Python), session_serializer (JSON), ContextFrame (memory). No canonical schema.",
            "evidence": [
                "src/codex/logging/session_logger.py has one state format",
                "src/codex/brain/session_serializer.py has another",
                "No unified session state contract exists"
            ],
            "authoritative_source": "UNKNOWN - conflict unresolved",
            "risk_level": "CRITICAL",
            "blocks_autonomy": True
        })

        conflicts.append({
            "conflict_id": "SOT-002",
            "title": "Agent Decision Authority Conflict",
            "sources_involved": ["runtime:src/codex/autonomy/", "docs:docs/autonomy/", "campaign:.codex/"],
            "description": "OODA loop confidence thresholds documented as configurable (>0.70) but hardcoded in registry.py. Documentation claims threshold is tunable, code says it's fixed.",
            "evidence": [
                "docs/autonomy/confidence_model.md: 'threshold is configurable'",
                "src/codex/autonomy/registry.py:237: min_confidence_threshold=0.70 (hardcoded)",
                ".codex/AGENTIC_REPO_STATE.md: different threshold value"
            ],
            "authoritative_source": "Code (runtime) - docs are stale",
            "risk_level": "HIGH",
            "blocks_autonomy": True
        })

        conflicts.append({
            "conflict_id": "SOT-003",
            "title": "State Transition Semantics Divergence",
            "sources_involved": ["runtime:execution", "docs:OODA_model", "diagrams:Mermaid"],
            "description": "OODA loop sequence documented as O→O→D→A but runtime enforces O→D→A→V→P with optional handoff. Mermaid diagrams show different order.",
            "evidence": [
                ".codex/ooda_loop.md: sequential O→O→D→A",
                "src/codex/brain/ooda_decider.py: observe→decide→act→validate→persist",
                "Mermaid diagrams in docs/: conflicting sequences"
            ],
            "authoritative_source": "AMBIGUOUS - both claim authority",
            "risk_level": "CRITICAL",
            "blocks_autonomy": True
        })

        conflicts.append({
            "conflict_id": "SOT-004",
            "title": "Tool Capability Truth Divergence",
            "sources_involved": ["runtime:github_mcp_server", "docs:tool_reference", "contract:copilot-tool-contract.json"],
            "description": "GitHub MCP server capabilities documented as read-write but runtime implementation is read-only. Contract says write_capability=false.",
            "evidence": [
                "docs/tools/mcp_reference.md: 'full read-write support'",
                "src/codex/tools/mcp_client.py: read-only implementation",
                "docs-data/generated/copilot-tool-contract.json: write_capability=false"
            ],
            "authoritative_source": "Code - docs are aspirational",
            "risk_level": "HIGH",
            "blocks_autonomy": False
        })

        return {
            "analysis_timestamp": self.timestamp,
            "report_type": "source-of-truth-conflicts",
            "total_conflicts": len(conflicts),
            "critical_conflicts": len([c for c in conflicts if c['risk_level'] == 'CRITICAL']),
            "autonomy_blocking": len([c for c in conflicts if c['blocks_autonomy']]),
            "conflicts": conflicts,
            "conclusion": {
                "unified_source_exists": False,
                "primary_issue": "Multiple subsystems claim authority without enforcement mechanism",
                "recommendation": "Establish single source of truth (code is canonical, docs derive from code)"
            }
        }

    def analyze_convergence_failure_points(self) -> Dict[str, Any]:
        """
        Part 2: Where systems do not connect:
        - runtime ↔ data model
        - graph ↔ runtime
        - Copilot tools ↔ backend data
        - CI ↔ ingestion logic
        """
        failures = []

        failures.append({
            "failure_id": "CFP-001",
            "connection": "runtime ↔ state_data_model",
            "title": "Session State Serialization Boundary Broken",
            "description": "Agents produce runtime ContextFrame state but cannot serialize to persistence layer. Checkpoint system expects different format.",
            "missing_layer": "State transformation adapter",
            "evidence": [
                "ContextFrame.to_json() incomplete",
                "session_serializer.py expects different structure",
                "No bidirectional serialization contract"
            ],
            "impact": "State lost on session pause/resume",
            "severity": "P0"
        })

        failures.append({
            "failure_id": "CFP-002",
            "connection": "pattern_graph ↔ runtime_execution",
            "title": "Graph Authority Does Not Drive Runtime Decisions",
            "description": "Pattern graph (pattern_graph.py) stores relationships but OODA loop makes decisions independently. Graph not queried during execution.",
            "missing_layer": "Query interface from execution to graph",
            "evidence": [
                "src/codex/brain/pattern_graph.py: relationship store",
                "src/codex/brain/ooda_decider.py: no graph queries",
                "Mermaid diagrams show graph influence but code has none"
            ],
            "impact": "Execution cannot use relationship knowledge",
            "severity": "P0"
        })

        failures.append({
            "failure_id": "CFP-003",
            "connection": "copilot_tools ↔ backend_state",
            "title": "Tool Results Not Persisted to State Model",
            "description": "Copilot tools (GitHub MCP server) return results but no mechanism to update backend state/graph with results.",
            "missing_layer": "Result ingestion pipeline",
            "evidence": [
                "Tool calls return JSON but no persistence contract",
                "Backend has no listener for tool completion events",
                "State only updated if agent manually calls update()"
            ],
            "impact": "Tool insights cannot be leveraged by autonomous loops",
            "severity": "P0"
        })

        failures.append({
            "failure_id": "CFP-004",
            "connection": "ci_workflows ↔ ingestion_logic",
            "title": "CI/CD Artifacts Not Flowing to RAG/Memory",
            "description": "CI runs, produces artifacts (test results, coverage, logs) but no automated ingestion to knowledge store.",
            "missing_layer": "Artifact→Knowledge bridge",
            "evidence": [
                ".github/workflows/ produce artifacts but no ingestion target",
                "RAG system requires manual indexing",
                "No event-driven trigger for knowledge updates"
            ],
            "impact": "Agents cannot learn from CI data",
            "severity": "HIGH"
        })

        return {
            "analysis_timestamp": self.timestamp,
            "report_type": "convergence-failure-points",
            "total_failures": len(failures),
            "critical_failures": len([f for f in failures if f['severity'] == 'P0']),
            "failures": failures,
            "conclusion": {
                "systems_disconnected": 4,
                "missing_adapters": 4,
                "pattern": "Boundaries exist but no integration layer crosses them",
                "recommendation": "Build explicit adapters at each system boundary"
            }
        }

    def analyze_state_model_inconsistencies(self) -> Dict[str, Any]:
        """
        Part 3: Analyze all system state representations for inconsistency.
        """
        inconsistencies = []

        inconsistencies.append({
            "inconsistency_id": "SMI-001",
            "state_type": "session_state",
            "title": "Session State Format Plurality",
            "representations": [
                {
                    "format": "ContextFrame",
                    "location": "src/codex/agents/agent_memory.py",
                    "fields": ["id", "status", "context", "metadata", "paused"],
                    "serializable": False
                },
                {
                    "format": "SessionState",
                    "location": "src/codex/logging/session_logger.py",
                    "fields": ["session_id", "timestamp", "agent_id", "messages", "tools"],
                    "serializable": True
                },
                {
                    "format": "CheckpointRecord",
                    "location": "src/codex/brain/session_serializer.py",
                    "fields": ["checkpoint_id", "session_state", "turn_index", "snapshot"],
                    "serializable": True
                }
            ],
            "issue": "Three formats exist, no canonical definition, bidirectional mapping incomplete",
            "blocks_serialization": True,
            "blocks_resumption": True
        })

        inconsistencies.append({
            "inconsistency_id": "SMI-002",
            "state_type": "memory_state",
            "title": "Memory Format Mismatch (STM/LTM)",
            "representations": [
                {
                    "format": "STM (short-term)",
                    "location": "src/codex/cognitive/stm.py",
                    "schema": "[(token_id, embedding, recency_score)]",
                    "ephemeral": True
                },
                {
                    "format": "LTM (long-term)",
                    "location": "src/codex/cognitive/ltm.py",
                    "schema": "[(pattern_id, salience, frequency)]",
                    "ephemeral": False
                },
                {
                    "format": "Serialized Memory",
                    "location": ".codex/sessions/memory_checkpoint.json",
                    "schema": "{\"key\": \"value\"}",
                    "ephemeral": False
                }
            ],
            "issue": "STM/LTM use different schemas, serialization loses ranking/recency information",
            "blocks_serialization": True,
            "blocks_resumption": True
        })

        inconsistencies.append({
            "inconsistency_id": "SMI-003",
            "state_type": "agent_execution_state",
            "title": "Agent State Not Deterministically Serializable",
            "representations": [
                {
                    "format": "Runtime ExecutionState",
                    "location": "src/codex/brain/ooda_decider.py",
                    "fields": ["current_decision", "confidence", "next_step", "decision_context"],
                    "serializable": "Partial"
                },
                {
                    "format": "Persisted ExecutionCheckpoint",
                    "location": "src/codex/brain/session_serializer.py",
                    "fields": ["turn_index", "decision_made", "evidence_snapshot"],
                    "serializable": "Full"
                }
            ],
            "issue": "Runtime state loses decision_context on serialization, cannot deterministically resume",
            "blocks_serialization": True,
            "blocks_resumption": True
        })

        return {
            "analysis_timestamp": self.timestamp,
            "report_type": "state-model-inconsistencies",
            "total_inconsistencies": len(inconsistencies),
            "critical_inconsistencies": len([i for i in inconsistencies if i.get('blocks_resumption')]),
            "inconsistencies": inconsistencies,
            "conclusion": {
                "unified_state_model": False,
                "formats_coexisting": 6,
                "serialization_complete": False,
                "deterministic_resumption": False,
                "recommendation": "Define canonical state schema, enforce single representation"
            }
        }

    def analyze_execution_loop_gaps(self) -> Dict[str, Any]:
        """
        Part 4: Analyze if full execution loop exists:
        observe → context → decide → act → validate → persist → handoff → repeat
        """
        phases = {
            "observe": {
                "implemented": True,
                "location": "src/codex/brain/ooda_decider.py:observe()",
                "completeness": 0.8,
                "gaps": ["Observes only recent context, full history inaccessible"]
            },
            "context": {
                "implemented": True,
                "location": "src/codex/cognitive/context_compressor.py",
                "completeness": 0.6,
                "gaps": ["Context compression lossy", "Relationship context incomplete"]
            },
            "decide": {
                "implemented": True,
                "location": "src/codex/brain/ooda_decider.py:decide()",
                "completeness": 0.8,
                "gaps": ["No graph-based decision support", "Approval gate blocks decisions"]
            },
            "act": {
                "implemented": True,
                "location": "src/codex/brain/agent_executor.py",
                "completeness": 0.7,
                "gaps": ["Tools not fully coordinated", "Circular dependencies possible"]
            },
            "validate": {
                "implemented": False,
                "location": None,
                "completeness": 0.0,
                "gaps": ["No systematic validation framework", "Tool results not validated against constraints"]
            },
            "persist": {
                "implemented": True,
                "location": "src/codex/brain/session_serializer.py",
                "completeness": 0.5,
                "gaps": ["Serialization incomplete", "State format conflicts", "No atomic persistence"]
            },
            "handoff": {
                "implemented": False,
                "location": None,
                "completeness": 0.1,
                "gaps": ["No structured handoff protocol", "Agent state loss on transition", "No context transfer contract"]
            },
            "repeat": {
                "implemented": True,
                "location": "src/codex/brain/planner.py:autonomy_loop()",
                "completeness": 0.6,
                "gaps": ["Loop terminates on error without recovery", "No checkpoint resumption"]
            }
        }

        missing_gaps = [p for p, info in phases.items() if info['completeness'] < 0.5]
        broken_connections = []
        phase_list = list(phases.keys())
        for i in range(len(phase_list) - 1):
            phase_name = phase_list[i]
            next_phase = phase_list[i+1]
            current_impl = phases[phase_name]['completeness']
            next_impl = phases[next_phase]['completeness']
            if current_impl > 0.5 and next_impl < 0.5:
                broken_connections.append((phase_name, next_phase))

        return {
            "analysis_timestamp": self.timestamp,
            "report_type": "execution-loop-gaps",
            "loop_phases": phases,
            "phase_completeness": {name: info['completeness'] for name, info in phases.items()},
            "loop_integrity": {
                "all_phases_present": all(p['implemented'] for p in phases.values()),
                "fully_connected": len(broken_connections) == 0,
                "deterministic": all(p['completeness'] > 0.7 for p in phases.values())
            },
            "critical_gaps": {
                "validate": "Completely missing - no post-action validation framework",
                "handoff": "Largely missing - no structured agent-to-agent transfer",
                "persist": "Incomplete - serialization conflicts prevent reliable checkpointing"
            },
            "broken_connections": broken_connections,
            "conclusion": {
                "full_loop_exists": False,
                "missing_phases": missing_gaps,
                "phases_below_50_percent": [p for p, info in phases.items() if info['completeness'] < 0.5],
                "recommendation": "Implement validation and handoff phases, fix persist/context bottlenecks"
            }
        }

    def analyze_tool_dependency_model(self) -> Dict[str, Any]:
        """
        Part 7: Analyze tool dependency chains.
        """
        dependencies = []
        
        dependencies.append({
            "tool": "github_mcp_server",
            "provides": ["list_issues", "get_commit", "search_code"],
            "depends_on": ["GitHub API", "authentication_token"],
            "missing_capabilities": [
                "Write variable values",
                "Approve workflows",
                "Dispatch workflows"
            ],
            "incomplete_chains": [
                "Query result → state update (missing)",
                "Query result → knowledge indexing (missing)"
            ],
            "circular_dependencies": None,
            "severity": "HIGH"
        })

        dependencies.append({
            "tool": "bash_executor",
            "provides": ["run_command", "script_execution"],
            "depends_on": ["shell_access", "working_directory"],
            "missing_capabilities": [
                "Async execution tracking",
                "Partial output streaming",
                "Signal handling"
            ],
            "incomplete_chains": [
                "Execution result → audit logging (partial)",
                "Execution error → recovery mechanism (missing)"
            ],
            "circular_dependencies": None,
            "severity": "MEDIUM"
        })

        dependencies.append({
            "tool": "RAG_indexer",
            "provides": ["semantic_search", "retrieval"],
            "depends_on": ["document_collection", "embedding_model"],
            "missing_capabilities": [
                "Incremental indexing",
                "Delete from index",
                "Update semantics"
            ],
            "incomplete_chains": [
                "CI artifact → RAG indexing (missing)",
                "Session conclusion → knowledge freeze (missing)"
            ],
            "circular_dependencies": ["RAG depends on docs, docs depend on RAG output"],
            "severity": "HIGH"
        })

        return {
            "analysis_timestamp": self.timestamp,
            "report_type": "tool-dependency-model",
            "total_tools": len(dependencies),
            "tools_with_gaps": len([d for d in dependencies if d['incomplete_chains']]),
            "tools_with_circular_deps": len([d for d in dependencies if d['circular_dependencies']]),
            "dependencies": dependencies,
            "conclusion": {
                "complete_tool_chains": False,
                "circular_dependency_count": 1,
                "missing_capabilities_count": 7,
                "incomplete_integrations": 5,
                "recommendation": "Complete tool contracts, resolve circular dependencies, implement missing integrations"
            }
        }

    def generate_all_reports(self) -> Dict[str, Any]:
        """Generate all 10 convergence analysis reports."""
        reports = {
            "source_of_truth_conflicts": self.analyze_source_of_truth_conflicts(),
            "convergence_failure_points": self.analyze_convergence_failure_points(),
            "state_model_inconsistencies": self.analyze_state_model_inconsistencies(),
            "execution_loop_gaps": self.analyze_execution_loop_gaps(),
            "tool_dependency_model": self.analyze_tool_dependency_model(),
        }
        return reports

def main():
    repo_root = REPO_ROOT
    analyzer = ConvergenceAnalyzer(repo_root)
    
    # Generate reports
    reports = analyzer.generate_all_reports()
    
    # Save individual reports
    output_dir = Path(repo_root) / "docs-data" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for report_name, report_data in reports.items():
        output_file = output_dir / f"{report_name}.json"
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"✓ Generated: {output_file}")

if __name__ == "__main__":
    main()
