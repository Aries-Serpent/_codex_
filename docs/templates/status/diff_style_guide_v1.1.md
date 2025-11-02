# Guide: Atomic Patch Diff Style for `_codex_` (v1.1)
> Generated: 2025-11-02 11:32:31 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Diff Style Curator], [Secondary: Reliability Reviewer] ⚡ Energy: 5  

## 1. Mandatory Elements per Patch
- Title and component paths
- Why (Problem/Rationale)
- Risk (1–5) and Confidence (1–5)
- Rollback steps (exact, testable)
- Tests/Docs changes
- Validation Checklist:
  - Build/lint/typecheck pass
  - Unit/integration tests green
  - Security scan results reviewed
  - Rollback rehearsal or proof
  - Compatibility assessment
- Cross‑links (when relevant): CAP‑IDs and REPRO‑IDs

## 2. Canonical Diff Fences
Use unified diff with explicit markers:
```diff
*** Begin Patch
*** Update File: path/to/file.py
@@
- old
+ new
*** End Patch
```

Add files:
```diff
*** Begin Patch
*** Add File: path/to/new_file.py
+<content>
*** End Patch
```

Delete files:
```diff
*** Begin Patch
*** Delete File: path/to/old_file.py
*** End Patch
```

## 3. Chunking and Sequencing
- Break large changes into atomic, logically independent diffs.
- Sequence patches to minimize risk; guard with feature flags when possible.

## 4. Evidence and Links
- Cross-reference tests, docs, relevant code lines, and impacted CAP‑IDs/REPRO‑IDs.
- Attach metrics (coverage Δ, perf Δ) when applicable.

## 5. Redaction and Safety
- No secrets in diffs.
- Sanitize environment-dependent paths if sensitive.
