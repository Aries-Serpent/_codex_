# Fence_Discipline_OnePager.md

**Last Updated:** 2026-06-22
> Purpose: Ensure well-formed fenced blocks in all outputs.

## Rules
- Return a **single fenced block** for the payload; choose an accurate language tag.
- Fences: backticks or tildes, **≥3**, do **not** mix. Closer uses the **same character** and **length ≥ opener**.
- If payload contains triple backticks, **lengthen the OUTER fence** until it exceeds any potential closing run at **line start** (≤3 spaces).
- **Backtick fences:** the info string **must not contain backticks** (spec). With tilde fences, keep tags simple.
- Prefer a **blank line before/after** fenced blocks embedded in prose.
- Diffs: output a **unified diff** with a `diff` info string (lengthen the outer fence if inner fences are shown).
- Splitting across messages: each part keeps **balanced fences** plus `[PART X/N]` tags.

## Preflight (mini)
- Fence char + count chosen (≥3; outer exceeds any inner closing runs).
- Language tag set; no backticks in info if using backticks.
- No trailing junk on fence lines; add blank lines in prose.
- Diffs use `diff` + proper headers.
- Parts contiguous; fences balanced.
