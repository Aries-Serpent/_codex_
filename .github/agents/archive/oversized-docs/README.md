# .github/agents/archive/oversized-docs/

These files were moved here because they exceeded the **30,000 character limit** for
GitHub Copilot custom agent definition files. Files in `.github/agents/` that exceed
this limit cause the custom agent to **silently NOT WORK**.

**Moved:** 2026-03-21 (S173 / PR #3661)
**Reason:** Non-agent documentation/planning/status files were incorrectly placed in
`.github/agents/`. GitHub Copilot scans that directory — oversized non-agent files
pollute the agent namespace and risk causing parse failures.

## Contents

| File | Original Size | Category |
|------|--------------|---------|
| PHASE_7_QUANTUM_ENHANCEMENTS.md | 58,718 chars | Planning |
| COGNITIVE_BRAIN_CONTINUATION_PROMPT_PHASE_11_1.md | 55,302 chars | Continuation prompt |
| QUANTUM_AGENT_IMPROVEMENT_PLAN.md | 41,928 chars | Planning |
| PHASE_6_CONTINUATION_PROMPT.md | 40,222 chars | Continuation prompt |
| QUANTUM_DETERMINISTIC_PLANNING.md | 40,179 chars | Planning |
| COGNITIVE_BRAIN_CONSOLIDATED_STATUS_V10.md | 38,504 chars | Status snapshot |
| COGNITIVE_BRAIN_STATUS_V9_COMPLETE.md | 38,472 chars | Status snapshot |
| AI_AGENT_INTUITIVENESS_SCORE_V2.md | 38,456 chars | Scoring |
| COGNITIVE_BRAIN_STATUS_V8_PHASE_8_9.md | 38,116 chars | Status snapshot |
| PHASE_8_ROADMAP.md | 37,635 chars | Roadmap |
| COGNITIVE_BRAIN_ARCHITECTURE_DIAGRAMS.md | 37,435 chars | Architecture |
| COGNITIVE_BRAIN_STATUS_V5.md | 37,142 chars | Status snapshot |
| COGNITIVE_BRAIN_STATUS_V6_FINAL.md | 36,447 chars | Status snapshot |
| QA_AGENT_ARCHITECTURE_DIAGRAMS.md | 36,201 chars | Architecture |
| COGNITIVE_BRAIN_COMPLETE_IMPLEMENTATION_PLANSET.md | 35,437 chars | Planning |
| PHASE_7_CONTINUATION_PROMPTS.md | 34,333 chars | Continuation prompts |
| AGENT_ECOSYSTEM_MAP.md | 32,628 chars | Ecosystem map |
| COGNITIVE_BRAIN_V10_ROADMAP.md | 31,213 chars | Roadmap |
| COGNITIVE_BRAIN_STATUS_V4_FINAL.md | 31,168 chars | Status snapshot |
| INFRA_LINTER_AGENT_PROMPT.md | 30,166 chars | Agent prompt |

## Rule

**Any file in `.github/agents/` that is a registered custom agent MUST stay under 30,000
characters.** Non-agent files (docs, status snapshots, planning) should NOT be placed in
`.github/agents/` at all — use `.codex/docs/`, `docs/ops/`, or `archive/` instead.

Check before committing:
```bash
find .github/agents -maxdepth 1 -name "*.md" | xargs wc -c | awk '$1 > 30000 && !/total/'
```
