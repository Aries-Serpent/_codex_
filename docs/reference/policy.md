# `_codex_` Operational Policy (Branch, Coverage, DeepResearch, Artifacts, GPU)
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Branch selection:** always audit the **most recently updated** branch (auto-detected).

**DeepResearch:** allowed; write curated citations to `.codex/reports/citations/citations<UTC>.md`.

**Coverage gate:** Evidence Coverage must be ≥70% (then 80% 90% as CAP-IDs close).

**Artifacts:** keep `.codex/status/` (system) and `.codex/reports/` (generated audit/analysis output); move historical dumps to `docs/archive/` or `.codex/archive/` instead of the repository root.

**GPU perf:** sampling stays **off** by default; enable with `CODEX_ENABLE_PERF_SAMPLER=1`.

## Formal Controls
- Coverage:
 \[
 \mathrm{Coverage}=\frac{|F_{\text{found}}|}{|F_{\text{expected}}|}
 \]
- Branch:
 \[
 b^*=\arg\max_{b\in\mathcal{B}} \mathrm{commit\_time}(b)
 \]

## Notes
- No CI triggers; all checks are local/offline.
- Defaults remain unchanged unless a guard flag is explicitly provided.
