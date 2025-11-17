# Guide: Atomic Patch Diff Style for `_codex_` (v1.2 — with Schema Validation)
> Generated: 2025-11-02 12:07:19 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Diff Style Curator], [Secondary: Reliability Reviewer] ⚡ Energy: 5  
⚛️ Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️

## 1. Mandatory Elements per Patch
- **Title (PATCH-XXX)** and component paths
- **Why** (Problem/Rationale)
- **Risk** (1–5) and **Confidence** (1–5)
- **Rollback** steps (exact, testable)
- **Tests/Docs** changes
- **Validation Checklist**:
  - Build/lint/typecheck pass
  - Unit/integration tests green
  - Security scan results reviewed
  - Rollback rehearsal or proof
  - Compatibility assessment
  - **NEW v1.2**: If configs touched, schema validation passes (run `tools/validate_configs.py` post-patch)
- **Cross‑links** (when relevant): CAP‑IDs, REPRO‑IDs, and FIND-IDs

## 2. Canonical Diff Fences
Use unified diff with explicit markers:
```diff
*** Begin Patch
*** Update File: path/to/file.py
@@
- old
+ new
*** End Patch
```text

Add files:
```diff
*** Begin Patch
*** Add File: path/to/new_file.py
+<content>
*** End Patch
```text

Delete files:
```diff
*** Begin Patch
*** Delete File: path/to/old_file.py
*** End Patch
```text

## 3. Chunking and Sequencing
- Break large changes into atomic, logically independent diffs.
- Sequence patches to minimize risk; guard with feature flags when possible.
- **NEW v1.2**: If a patch affects schemas, apply schema changes first, then config changes, in separate diffs to ease rollback.

## 4. Evidence and Links
- Cross-reference tests, docs, relevant code lines, and impacted CAP‑IDs/REPRO‑IDs/FIND-IDs.
- Attach metrics (coverage Δ, perf Δ) when applicable.
- **NEW v1.2**: Reference validation tools and schema files affected (e.g., "Validates against `configs/schemas/training.schema.yaml`").

## 5. Redaction and Safety
- No secrets in diffs.
- Sanitize environment-dependent paths if sensitive.
- **NEW v1.2**: When touching security-related code (e.g., `src/security/core.py`, input validation patterns), do not include exploits or attack examples; reference the canonical module instead.
