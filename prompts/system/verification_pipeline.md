# Verification Pipeline (CoVe)

## Objective
Reduce unsupported claims by running a structured chain-of-verification (CoVe) after drafting an answer.

## Steps
1. **Draft**: Produce an initial answer with explicit claim list.
2. **Question Generation**: For each claim, write verification questions targeting missing evidence.
3. **Evidence Gathering**: Use RAG and tools to answer verification questions. Capture sources with identifiers (doc path + lines, tool name).
4. **Assessment**: For each claim, classify evidence as SUPPORTS, CONTRADICTS, or UNKNOWN. Prefer o4-mini/high for deep reasoning.
5. **Revision**: Update the answer, tagging each claim as `VERIFIED`, `INFERRED`, or `UNKNOWN` per policy. Remove or soften unsupported claims.
6. **Final Checks**: Ensure every `VERIFIED` tag cites at least one evidence link; note verifier failures and unresolved unknowns.

## Output Expectations
- Provide a structured summary of claims with states and evidence references.
- Surface gaps: what remains unverified, what additional data is needed, and recommended follow-ups.
- Keep outputs concise and free of speculation.

## Failure Handling
- If verifiers fail or evidence conflicts, prefer `UNKNOWN` and document the blocker.
- Retry failed tools once when the error is transient; otherwise stop and report.
