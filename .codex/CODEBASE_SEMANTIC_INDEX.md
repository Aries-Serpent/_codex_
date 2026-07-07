# CODEBASE_SEMANTIC_INDEX

Date: 2026-07-07
Source: lane1-semantic (semantic-search) + repository scan

## Top Module Clusters

- `src/codex` (~510 Python files): core platform, CLI, cognitive orchestration, logging, RAG.
- `src/codex_ml` (~467): ML/training/eval/inference stack.
- `scripts/ci` (~219): CI remediation, automation, governance tooling.
- `scripts/cognitive` (~68) + `src/cognitive_brain` (46): cognitive brain runtime and decision modules.
- `src/mcp` (~60): MCP integration and protocol-facing features.

## Key Symbol Hubs

| Hub | Why it matters | Evidence |
|---|---|---|
| `codex.logging.structured_logger.logger` | Cross-cutting observability dependency | `src/codex/cli.py`, `src/codex/cognitive/agent_brain_api.py` |
| `codex_ml.utils.optional.optional_import` | Optional-dependency boundary for portability | `src/codex_ml/modeling/factory.py`, `src/codex_ml/eval/evaluator.py` |
| `QuantumComplianceAssessor.assess_compliance()` | Central compliance decision primitive | `src/cognitive_brain/integrations/compliance_integration.py` |
| `AgentBrainAPI.get_session_context()/report_completion()` | Core session injection and closure loop | `src/codex/cognitive/agent_brain_api.py` |

## Cross-Module Hotspots

- `src/codex_ml -> src/codex`: highest coupling surface.
- `src/codex -> src/codex_ml`: reverse dependency also present (non-trivial bidirectional coupling).
- `scripts/ci -> src/codex`: CI tooling directly imports runtime modules.
- `src/codex -> src/cognitive_brain`: narrow but critical integration bridge.

## Cognitive Brain API Surface (Observed)

Primary external-facing surfaces:
- `src/codex/cognitive/agent_brain_api.py`
- `src/codex/cognitive/__init__.py`
- `src/cognitive_brain/agents/cognitive_interface.py`
- `src/cognitive_brain/integrations/compliance_integration.py`

Stable external classes (campaign baseline):
1. ObservationData
2. OrientationResult
3. Decision
4. ActionResult
5. Planner
6. MemoryInterface
7. MemoryPattern
8. QuantumMemoryManager
9. Pattern
10. PatternSet

## Packaging-Relevant Index Notes

- Cognitive brain core remains a clean extraction seam.
- Most heavy dependencies live outside `src/cognitive_brain/`.
- Bidirectional `codex <-> codex_ml` coupling is a key risk for profile isolation.
