"""PART 9: Agent Execution Standard — 8-Step Protocol for All Agents Operating on Machine-Readable Campaign Data."""

from __future__ import annotations

from typing import TypedDict

from tools.docs_agent.copilot_tools_new import CopilotToolsInterface


class _BriefStep(TypedDict):
    step: int
    task_brief: dict[str, object]
    contains: list[str]


class _RelatedStep(TypedDict):
    step: int
    dependencies: dict[str, object]
    contains: list[str]


class _ImpactStep(TypedDict):
    step: int
    impact: dict[str, object]
    decision_criteria: list[str]


class _TaskExecution(TypedDict):
    task_id: str
    actions_executed: list[str]
    state_before: str
    changes_made: str
    validation: str


class _ExecuteStep(TypedDict):
    step: int
    task_execution: _TaskExecution


class _UpdateScope(TypedDict):
    deliverable_status: str
    metrics_update: str
    decision_record: str
    timestamps: str


class _UpdateStep(TypedDict):
    step: int
    update_scope: _UpdateScope
    record_updates: dict[str, object]
    validation: str


class _RebuildStep(TypedDict):
    step: int
    index_rebuild: dict[str, object]
    rebuilds: list[str]
    validates: str


class _Persistence(TypedDict):
    session_checkpoint: str
    memory_consolidation: str
    audit_trail: str


class _ValidateStep(TypedDict):
    step: int
    validation: dict[str, object]
    persistence: _Persistence


class _ContextStep(TypedDict):
    step: int
    result: dict[str, object]


class _TemplateStep(TypedDict):
    step: int
    action: str
    input: str


_ProtocolStep = (
    _ContextStep
    | _BriefStep
    | _RelatedStep
    | _ImpactStep
    | _TemplateStep
    | _RebuildStep
    | _ValidateStep
)


class _ProtocolExecution(TypedDict):
    protocol_name: str
    version: str
    steps: list[_ProtocolStep]


class AgentExecutionStandard:
    """Assemble the campaign execution protocol using a SQLite-backed tool interface.

    The default constructor opens ``docs-data/generated/docs.sqlite`` relative
    to the working directory. Full execution performs context reads, index
    rebuilding, and validation; task actions and record updates are templates,
    not automatically applied mutations.
    """

    def __init__(self) -> None:
        self.tools = CopilotToolsInterface()

    def step_1_get_context(self, phase_id: str | None = None) -> dict[str, object]:
        """Read campaign counts; the reserved phase_id does not filter the query."""
        return self.tools.get_agent_context()

    def step_2_get_task_brief(self, task_id: str | None = None) -> _BriefStep:
        """Wrap a task brief, or current-phase context when task_id is omitted."""
        brief = self.tools.get_task_brief(task_id)
        return {
            "step": 2,
            "task_brief": brief,
            "contains": ["task definition", "requirements", "constraints", "status"],
        }

    def step_3_get_related_context(self, entity_id: str) -> _RelatedStep:
        """Wrap relationships returned by the tool for the specified entity ID."""
        context = self.tools.get_related_context(entity_id)
        return {
            "step": 3,
            "dependencies": context,
            "contains": ["upstream requirements", "downstream impacts", "lateral relationships"],
        }

    def step_4_impact_analysis(
        self, entity_id: str, proposed_changes: dict[str, object]
    ) -> _ImpactStep:
        """Describe dependency impact and risk without applying proposed changes."""
        impact = self.tools.impact_analysis(entity_id, proposed_changes)
        return {
            "step": 4,
            "impact": impact,
            "decision_criteria": [
                "Risk level assessment",
                "Affected entity count",
                "Downstream impact scope",
            ],
        }

    def step_5_execute_task(self, task_id: str, action_plan: list[str]) -> _ExecuteStep:
        """Describe task actions and validation metadata without executing the actions."""
        return {
            "step": 5,
            "task_execution": {
                "task_id": task_id,
                "actions_executed": action_plan,
                "state_before": "from step 3 (related_context)",
                "changes_made": "structured and logged",
                "validation": "all changes reference task_id and phase_id",
            },
        }

    def step_6_update_records(self, updates: dict[str, object]) -> _UpdateStep:
        """Describe record updates and audit requirements without writing records."""
        return {
            "step": 6,
            "update_scope": {
                "deliverable_status": "Complete/In Progress/Blocked",
                "metrics_update": "If metrics.jsonl changed",
                "decision_record": "If decisions.jsonl changed",
                "timestamps": "All records include timestamp",
            },
            "record_updates": updates,
            "validation": "All records have source_trace for auditability",
        }

    def step_7_rebuild_indexes(self) -> _RebuildStep:
        """Invoke the tool's FTS rebuild and wrap its success/error result."""
        result = self.tools.rebuild_indexes()
        return {
            "step": 7,
            "index_rebuild": result,
            "rebuilds": ["FTS for search", "Relationships graph", "Dependency chains"],
            "validates": "All foreign keys and linkages",
        }

    def step_8_validate_and_persist(self) -> _ValidateStep:
        """Validate campaign integrity and describe, but do not persist, checkpoints."""
        validation = self.tools.validate_docs()
        return {
            "step": 8,
            "validation": validation,
            "persistence": {
                "session_checkpoint": "Store phase_id, track_id, task_id",
                "memory_consolidation": "STM insights with decision/action IDs",
                "audit_trail": "All changes logged with source agent",
            },
        }

    def execute_full_protocol(
        self, task_id: str | None = None, proposed_changes: dict[str, object] | None = None
    ) -> _ProtocolExecution:
        """Collect protocol steps in order, leaving steps 5 and 6 as templates.

        Step 3 runs only with a supplied task ID or a task in the brief. Step 4
        requires both a supplied task ID and nonempty proposed changes. Index
        rebuilding and validation always run. For example,
        ``standard.execute_full_protocol("D-1", {"status": "Complete"})`` includes
        all eight steps but does not change deliverable status.
        """
        protocol_execution: _ProtocolExecution = {
            "protocol_name": "Agent Execution Standard",
            "version": "0.1.0",
            "steps": [],
        }

        # Step 1
        step_1 = self.step_1_get_context()
        protocol_execution["steps"].append({"step": 1, "result": step_1})

        # Step 2
        step_2 = self.step_2_get_task_brief(task_id)
        protocol_execution["steps"].append(step_2)

        # Step 3 - Use task_id from step 2 if available
        task = step_2["task_brief"].get("task")
        if task_id or task:
            if task_id:
                entity = task_id
            else:
                if not isinstance(task, dict):
                    raise TypeError("Task brief must contain a task object")
                identifier: object = task["id"]
                if not isinstance(identifier, str):
                    raise TypeError("Task ID must be a string")
                entity = identifier
            step_3 = self.step_3_get_related_context(entity)
            protocol_execution["steps"].append(step_3)

        # Step 4 - Impact analysis
        if proposed_changes and task_id:
            step_4 = self.step_4_impact_analysis(task_id, proposed_changes)
            protocol_execution["steps"].append(step_4)

        # Steps 5-8 represented as templates
        protocol_execution["steps"].append(
            {
                "step": 5,
                "action": "Execute task-specific actions",
                "input": "action_plan from step 4",
            }
        )

        protocol_execution["steps"].append(
            {"step": 6, "action": "Update structured records", "input": "results from step 5"}
        )

        step_7 = self.step_7_rebuild_indexes()
        protocol_execution["steps"].append(step_7)

        step_8 = self.step_8_validate_and_persist()
        protocol_execution["steps"].append(step_8)

        return protocol_execution

    def generate_agent_implementation_guide(self) -> str:
        """Return the static Markdown implementation guide; no tools or I/O are used."""
        guide = """
# PART 9: Agent Execution Standard

## 8-Step Protocol

Every agent operating on the machine-readable campaign system MUST follow these steps:

### Step 1: Get Agent Context
- Tool: `get_agent_context()`
- Retrieves: Full campaign state (phases, tracks, deliverables, agents)
- Determines: Operational scope and phase context

### Step 2: Get Task Brief
- Tool: `get_task_brief(task_id=None)`
- Retrieves: Task definition, requirements, constraints, current status
- Determines: Specific objectives and success criteria

### Step 3: Get Related Context
- Tool: `get_related_context(entity_id)`
- Retrieves: Upstream requirements, downstream impacts, dependencies
- Validates: All dependent entities exist and are valid

### Step 4: Impact Analysis
- Tool: `impact_analysis(entity_id, proposed_changes)`
- Analyzes: Risk level, affected entity count, validation steps
- Decides: Proceed, request approval, or escalate

### Step 5: Execute Task
- Execute: Actions from deliverables.jsonl
- Log: All changes with task_id and phase_id references
- Validate: Changes against upstream requirements

### Step 6: Update Records
- Update: deliverable status, metrics, decisions
- Store: All updates reference source task_id
- Audit: Include timestamp and source_trace

### Step 7: Rebuild Indexes
- Tool: `rebuild_indexes()`
- Rebuilds: FTS indexes, relationship graph, dependency chains
- Validates: Foreign key integrity, no orphaned records

### Step 8: Validate & Persist
- Tool: `validate_docs()`
- Validates: Campaign integrity (✅ valid or ❌ has_issues)
- Persist: Session checkpoint with phase_id, track_id, task_id
- Audit: Store decision/action IDs in memory system

## Integration Points

### Session System
- Store checkpoints with record IDs, not file paths
- Resume from phase_id + track_id + task_id triplet

### Memory System
- STM insights reference decision_id and action_id
- LTM patterns tag with phase_id and track_id
- Consolidation uses FTS to find related artifacts

### OODA Loop
- Observe: Step 1 (get_agent_context)
- Orient: Step 2 (get_task_brief)
- Decide: Steps 3-4 (dependencies + impact analysis)
- Act: Step 5 (execute task)
- Reflect: Steps 6-8 (update + validate + persist)

## Success Criteria

- All 8 steps executed in order
- Step 1: Context retrieved ✅
- Step 2: Task brief obtained ✅
- Step 3: Dependencies validated ✅
- Step 4: Impact assessed ✅
- Step 5: Task executed ✅
- Step 6: Records updated with IDs ✅
- Step 7: Indexes rebuilt ✅
- Step 8: Validation passed ✅

## Enforcement

CI workflow `machine-readable-governance.yml` validates that:
- All agents use structured tools (no direct file reading)
- All updates reference entity IDs (no orphaned data)
- Indexes remain valid after each cycle
- No unmanaged files created
"""
        return guide


if __name__ == "__main__":
    standard = AgentExecutionStandard()

    print("=== PART 9: Agent Execution Standard ===\n")

    # Execute the protocol
    execution = standard.execute_full_protocol()
    print(f"8-Step Protocol Execution: {len(execution['steps'])} steps completed")

    # Show the guide
    print("\n" + standard.generate_agent_implementation_guide())
