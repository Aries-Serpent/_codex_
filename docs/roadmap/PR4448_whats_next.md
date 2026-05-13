# PR #4448 — What's Next

**Branch:** `0D_base_` → `main`  
**Session:** S998 · 2026-05-13  
**Merge-readiness:** PR #4450 in progress

---

## ✅ Completed This Session (S998)

| # | Task | Commit |
|---|------|--------|
| 1 | Cherry-pick `src/codex/__init__.py` — add `"github"` to `_SUBMODULES` | current |
| 2 | Cherry-pick `src/codex_ml/monitoring/system_metrics.py` — warning→debug | current |
| 3 | Cherry-pick `src/training/accelerate_init_guard.py` — harden `is_accelerate_available()` | current |
| 4 | Cherry-pick `tests/branch_coverage/test_branch_coverage_cli.py` — patch.object fix | current |
| 5 | Fix `_EDGE_RE` regex in `cli_knowledge.py` for labelled source nodes | current |
| 6 | Fix sqlite pool test isolation (`_close_all()` at test start) | current |
| 7 | Addressed CI run 25819004497 root-cause failures | current |

## ✅ Completed Previous Sessions

| # | Task | Commit |
|---|------|--------|
| 1 | Restored `sandbox.py` + 2 test files from `origin/main` (broken refactors) | 3a8f8cb |
| 2 | MLflow stub compatibility — feature-detect `set_tracking_uri` / `set_experiment` | 0e216aa |
| 3 | `jsonschema>=4.26.0` added to `requirements-dev.txt` | 0e216aa |
| 4 | Facets test format evolution — accept dict or list | 0e216aa |
| 5 | Tokenization API consistency — `ImportError` in `__getattr__` | 0e216aa |
| 6 | Batch 1-4 bandit remediation from artifact scan (375 → 353 raw, 0 with config) | 7c92f4c |
| 7 | Batch 3: 25 B311 per-site `# nosec` annotations across 20 ML files | 08cc1b9 |
| 8 | Pattern 12 line-length fix `envelope.py:187` (upstream sweep `afc4e95`) | afc4e95 |
| 9 | Ingested new security artifacts (run 25809211083) — CVE status unchanged | — |
| 10 | Revised comprehensive security planset with Batches 5/6 + artifact refresh | — |
| 11 | Fixed RUF059 regression in `trend_aggregator.py` + test timeout in `pattern_recorder.py` | 172f46e |

---

## 🔲 Next Session Priorities

### Priority 1 — Verify CI Green
```
@copilot CTEP Mode: ON
Check run on PR #4450 after latest push.
All shard failures from run 25819004497 should be resolved.
```

### Priority 2 — Batch 5: CVE Monitoring
```
@copilot CTEP Mode: ON

Monitor diskcache / sqlitedict for fix version:
  pip-audit --json | python3 -c "
  import json,sys
  d=json.load(sys.stdin)
  vulns=[v for v in d.get('dependencies',[])
         if v['name'] in ('diskcache','sqlitedict')
         and any(f for f in v.get('vulns',[]) if f.get('fix_versions'))]
  print('FIX AVAILABLE' if vulns else 'NO FIX YET', vulns)
  "
If a fix version appears → bump dep in pyproject.toml + remove CVE comments.
```

### Priority 3 — Batch 6: Post-merge rescan
```
@copilot CTEP Mode: ON

After PR #4450 merges to main:
1. Dispatch security-scanning-suite.yml on main
2. Download dependency-scan-results + sbom-reports artifacts
3. Verify pip-audit: 0 actionable CVEs
4. Verify bandit --configfile .bandit: 0 issues
5. Verify raw bandit = ~328 (B101=226, B603=48, B404=36, B607=18)
6. Update .codex/plans/security-remediation-planset.md §Current State with confirmed post-merge numbers
7. Commit with Pattern 25.
```

### Priority 3 — CodeQL SAST
```
@copilot CTEP Mode: ON

1. Dispatch codeql-analysis.yml on 0D_base_
2. Download the SARIF artifact (codeql-alert-fetcher.yml)
3. List all open alerts by severity
4. For each HIGH/CRITICAL: apply the minimal code fix
5. Verify ruff + bandit --configfile .bandit still clean
6. Commit with Pattern 25.
```

### Priority 4 — Ongoing Pattern 25/30 hygiene
- Every commit must include both `CHANGELOG.md` **and** `AGENT_ACCOUNTABILITY_REPORT.md`
- New UTC day → add PDA entry to `.codex/aftermath/pda_iterations.jsonl`

---

## 📊 Security Surface Summary (2026-05-13)

| Surface | Status |
|---------|--------|
| pip-audit (CVEs) | ✅ 0 actionable — 2 accepted (no fix version) |
| SBOM (326 components) | ✅ 0 vulnerabilities |
| bandit --configfile .bandit | ✅ 0 issues |
| bandit raw | ⬇️ 328 (all suppressed by .bandit config) |
| detect-secrets | ✅ 0 |
| CodeQL Python/JS | ✅ pass |
| ruff src/ | ✅ 0 |

---

## 🗂️ Key Artifacts

| Artifact | SHA256 | Run |
|----------|--------|-----|
| dependency-scan-results | ae221879 | 25809211083 |
| sbom-reports | 1d922863 | 25809211083 |
| dependency-scan-results (prev) | df04fb29 | 25797170771 |
| sbom-reports (prev) | 97d5e5d6 | 25797170771 |

Full planset: `.codex/plans/security-remediation-planset.md`
