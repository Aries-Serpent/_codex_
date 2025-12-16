# Codex Implementation Plan: Track C (Task Sequence Refinement)

This plan details the definition and refinement of the Codex workflow execution sequence.

- **Six-Phase Workflow**: Formalize a six-phase workflow: (1) Preparation, (2) Search & Mapping, (3) Best-Effort Construction, (4) Controlled Pruning, (5) Error Capture, (6) Finalization. Implement functions or classes to encapsulate each phase and document expected inputs, outputs, and side effects.

- **Capability Routing**: Develop a capability routing table that maps each capability (tokenization, training, evaluation, etc.) to the appropriate sequence of phases and tasks. Implement a `run_capability(capability_name)` function that dispatches to the relevant workflows and ensures all required steps are executed.

- **Error Taxonomy & Capture**: Define a structured error taxonomy and error capture system (e.g., `ErrorRecord`, `step_context`, and `record_error`) that records encountered issues with timestamps, phase, and context. Integrate this system into all phases to capture errors and surface them as research questions when needed.

- **Workflow Script**: Create a CLI entry point at `scripts/run_codex_workflow.py` that orchestrates the full six-phase workflow for a given capability or set of capabilities. The script should load configuration, invoke the proper phases via the routing table, handle controlled pruning, and generate summary reports.

- **Tests & Validation**: Add tests under `tests/workflow/` to validate that phases execute in correct order, routing dispatches capabilities properly, errors are captured and logged, and that the CLI script runs successfully in offline mode. Ensure tests run via nox and require no external network or cost-incurring actions.

After implementing these steps, update documentation to explain the six-phase workflow, how to add new capabilities, and how errors are captured and handled. Ensure all operations run offline within the Codex environment.
