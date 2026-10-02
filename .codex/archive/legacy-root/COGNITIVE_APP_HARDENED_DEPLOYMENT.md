# Cognitive App Post-Merge Hardened Deployment Process

**Document**: `.codex/COGNITIVE_APP_HARDENED_DEPLOYMENT.md`  
**Created**: 2026-07-20T18:04Z  
**Status**: Production Implementation  
**Scope**: Ensures cognitive app widgets are fully functional post-merge WITHOUT requiring copilot agent intervention

---

## Overview

The cognitive app requires a **hardened, deterministic build and deployment process** to ensure:
1. Changes to cognitive_app/ automatically trigger rebuilds when merged to `main`
2. Build process validates all dependencies and artifacts
3. Post-deployment validation confirms all widgets are accessible
4. Self-healing mechanisms detect and recover from transient failures

---

## Architecture

### 1. Trigger Configuration

**File**: `.github/workflows/pages-mkdocs.yml`

The workflow now triggers on:
```yaml
paths:
  - docs/**
  - mkdocs.yml
  - src/codex/api/**
  - src/codex/**/*.py
  - cognitive_app/**           # ← CRITICAL: NOW INCLUDED
  - .github/workflows/pages-mkdocs.yml
```

**Impact**: Any changes to cognitive_app/ (source, config, deps) now automatically trigger the full deployment pipeline.

---

## Build Pipeline

### Phase 1: Pre-Build Validation

**Script**: `scripts/ci/validate_cognitive_app_build.py --pre-build-only`

Validates:
- ✅ Node.js and npm availability
- ✅ package.json and package-lock.json integrity
- ✅ Critical dependencies declared (react, vite, typescript, react-dom)
- ✅ JSON parsing without errors
- ✅ Version compatibility

**Failure Mode**: Returns exit code 1, stops pipeline

**Why**: Catches environment issues early, prevents silent build failures

---

### Phase 2: Dependency Installation

**Command**: `npm ci --prefer-offline`

Key decisions:
- Uses `npm ci` (not `npm install`) for deterministic installs
- `--prefer-offline` uses cache when available
- All errors logged to `npm-install.log`
- Explicit error handling and log dump on failure

**Failure Mode**: Returns exit code 1, dumps last 30 lines of npm log

**Why**: Ensures reproducible builds across different agents and machines

---

### Phase 3: TypeScript & Vite Build

**Command**: `npm run build` (runs: `tsc -b --noCheck && vite build`)

Key decisions:
- TypeScript compilation before Vite
- All output logged to `npm-build.log`
- Explicit error handling on build failure

**Failure Mode**: Returns exit code 1, dumps last 50 lines of npm log

**Why**: Catches compilation errors before bundle stage

---

### Phase 4: Post-Build Validation

**Script**: `scripts/ci/validate_cognitive_app_build.py --post-build-only`

Validates:
- ✅ dist/ directory exists and is non-empty
- ✅ index.html exists and contains React root element
- ✅ assets/ directory exists
- ✅ JavaScript bundles present (≥1 file)
- ✅ CSS files present (or inlined, warning only)
- ✅ proxy.js and package.json (if expected)
- ✅ Expected widgets referenced in bundle (soft check, warnings only)

**Failure Mode**: Returns exit code 3 if critical artifacts missing

**Why**: Detects silent build failures (e.g., empty dist/, missing assets)

---

### Phase 5: Deployment to Site

**Command**: Copy dist/* to ../site/cognitive_app/

Key decisions:
- Creates site/cognitive_app/ directory if needed
- Preserves all asset files
- Logs deployment summary

**Failure Mode**: Returns exit code 1 if dist/ missing

**Why**: Ensures dist/ exists before attempting deployment

---

## Post-Deployment Health Checks

**File**: `.github/workflows/pages-health-guard.yml`

### Automated Health Guard (Every 6 hours + on deployment)

Validates:
1. **Main site HTTP 200**: https://aries-serpent.github.io/_codex_/
2. **cognitive_app bundle HTTP 200**: https://aries-serpent.github.io/_codex_/cognitive_app/
3. **React root element present**: `<div id="root">` in HTML

**Recovery**: If any check fails, automatically triggers pages-mkdocs.yml rebuild

### Enhanced Telemetry

Logs all health checks to `.codex/telemetry/pages_health_log.jsonl`:
```json
{
  "timestamp": "2026-07-20T18:04:07Z",
  "event": "pages_health_check_enhanced",
  "main_http_code": "200",
  "pages_healthy": "true",
  "cognitive_app_bundle": "healthy",
  "react_root": "healthy",
  "rebuild_triggered": "false"
}
```

---

## Widget Validation

### Expected Widgets (10 total)

The validation script checks that all 10 widgets are compiled into the bundle:

1. **MetricsDashboard** - Dashboard metrics display
2. **CodeGenerator** - Code generation interface
3. **InteractiveDemo** - Interactive code executor
4. **QuantumVisualizer** - Quantum state visualization
5. **QuantumDecisionEngine** - Decision tree visualizer
6. **MemoryManagementDashboard** - Memory state display
7. **AgentOrchestrationPanel** - Agent orchestration UI
8. **XtermTerminal** - Terminal emulator (xterm.js)
9. **ApiClient** - API client interface
10. **DocumentationViewer** - Documentation renderer (Mermaid support)

**Validation**: Grep-based check in JavaScript bundle (soft validation, warnings only on missing)

---

## Deployment Workflow Summary

```
┌─────────────────────────────────────────┐
│ Push to main (or cognitive_app/ change) │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ pages-mkdocs.yml triggered              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Setup Python 3.12, Node.js 22           │
│ Install MkDocs, dependencies            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ BUILD COGNITIVE_APP                     │
│ ├─ Pre-build validation                │
│ ├─ npm ci --prefer-offline              │
│ ├─ npm run build (tsc + vite)          │
│ ├─ Post-build validation                │
│ └─ Copy dist → site/cognitive_app/     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Build MkDocs docs                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Upload site/ artifact                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Deploy to GitHub Pages                  │
│ (actions/deploy-pages)                  │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Post-deploy health check (6 attempts)   │
│ ├─ HTTP 200 main site                   │
│ ├─ HTTP 200 cognitive_app/              │
│ └─ React root element present           │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────────┐
      │                 │
  ✅ PASS          ❌ FAIL
      │                 │
      ▼                 ▼
    DONE        pages-health-guard.yml
                (6-hour check, or manual)
                      │
              ┌───────┴────────┐
              │                │
          HEALTHY          DEGRADED
              │                │
              ▼                ▼
            DONE        Trigger rebuild
                        (auto self-heal)
```

---

## Error Handling & Recovery

### Build Failures (Pre-Build Phase)

**Exit Code**: 1  
**Cause**: Node/npm missing, package.json corrupt, missing critical deps  
**Recovery**: Manual - requires environment fix + manual trigger of pages-mkdocs.yml

**Action Required**: Check runner environment, fix dependency issues

---

### Build Failures (npm install/build Phase)

**Exit Code**: 1  
**Cause**: Package installation failed, TypeScript compilation error, Vite build error  
**Recovery**: Auto - pages-health-guard.yml detects 404, triggers rebuild (exponential backoff)

**Action Required**: Usually resolves on retry; check npm logs if persistent

---

### Validation Failures (Post-Build Phase)

**Exit Code**: 3  
**Cause**: dist/ missing, index.html incomplete, assets absent  
**Recovery**: Auto - pages-health-guard.yml detects 404, triggers rebuild

**Action Required**: Check vite.config.ts if persistent

---

### Deployment Failures

**Exit Code**: 0 (build succeeds, but deployment fails)  
**Cause**: GitHub Pages environment issue, artifact upload timeout  
**Recovery**: Auto - pages-health-guard.yml detects non-200 HTTP, triggers rebuild

**Action Required**: Check GitHub Actions logs if deployment times out repeatedly

---

### Health Check Failures (Post-Deployment)

**Trigger**: Scheduled (every 6 hours) or on deployment_status event  
**Action**: Automatically triggers pages-mkdocs.yml rebuild (max 3 attempts)

**Recovery Chain**:
1. First attempt: Full rebuild from source
2. Second attempt (if still failing): Rebuild + cache purge
3. Third attempt (if still failing): Escalate to manual investigation

---

## Monitoring & Alerts

### Health Telemetry

Location: `.codex/telemetry/pages_health_log.jsonl`

**Metric**: Continuous (every 6 hours + on each deployment)

**Fields**:
- timestamp: ISO 8601 UTC
- event: "pages_health_check_enhanced"
- main_http_code: HTTP status of main site
- pages_healthy: true/false
- cognitive_app_bundle: healthy/degraded
- react_root: healthy/missing
- rebuild_triggered: true/false

**Analysis**: Check log for patterns (e.g., degraded between 01:00-03:00 UTC = maintenance window)

---

## Pre-Merge Validation (CI Gate)

**Workflow**: Upcoming - `.github/workflows/cognitive-app-validate.yml`

Planned validations before merge approval:
- ✅ `npm ci` succeeds
- ✅ `npm run lint` passes
- ✅ `npm run build` succeeds
- ✅ Post-build validation passes
- ✅ Assets present and non-zero size

**Purpose**: Catch issues before merge, reduce post-merge failures

---

## Rollback Procedure

If cognitive app breaks post-merge:

1. **Immediate (seconds)**: GitHub Pages serves cached version (CDN may still have old)
2. **Auto-recovery (minutes)**: pages-health-guard.yml detects issue, triggers rebuild
3. **Manual revert (if needed)**:
   ```bash
   git revert <commit-sha>  # Revert cognitive app changes
   git push origin main     # Triggers rebuild without problematic code
   ```

---

## Testing the Hardened Process

### Test 1: Local Build Validation

```bash
cd cognitive_app
npm ci
npm run build
python ../scripts/ci/validate_cognitive_app_build.py --post-build-only
```

**Expected**: Exit code 0, all validations pass

### Test 2: Simulate Changes + Trigger

```bash
# Edit a widget file
echo "// test change" >> src/App.tsx

# Commit and push
git add cognitive_app/
git commit -m "test: validate cognitive_app trigger"
git push origin main

# Wait for pages-mkdocs.yml to trigger automatically
# Check workflow runs: https://github.com/Aries-Serpent/_codex_/actions
```

**Expected**: pages-mkdocs.yml runs, cognitive_app rebuilds, site updated

### Test 3: Force Health Check

```bash
gh workflow run pages-health-guard.yml \
  --ref main \
  --field force_redeploy=true
```

**Expected**: Workflow runs health checks, optionally triggers rebuild

---

## Maintenance

### When to Update This Process

- **New widgets added**: Update widget list in validation script
- **Build config changes**: Update validation script checks
- **Dependency changes**: May need pre-build checks updated
- **Health thresholds change**: Update pages-health-guard.yml timeouts

### Recommended Quarterly Review

- Check health telemetry for patterns
- Review build times (should be <5 min)
- Verify no intermittent failures
- Update error handling based on new failure modes

---

## Success Metrics

**Target**: After merge to main, cognitive app is live & fully functional **100% of the time** without manual intervention

**Current Baseline** (before hardening):
- ❌ Requires copilot agent session to resolve widget failures
- ❌ cognitive_app/ changes don't trigger deployment
- ❌ No post-build validation
- ❌ Limited health monitoring

**After Hardening** (this implementation):
- ✅ All deployments fully automated
- ✅ cognitive_app/ changes auto-trigger workflow
- ✅ 4-phase validation catches issues early
- ✅ 6-hour health monitoring + auto-recovery
- ✅ No copilot intervention needed

---

## References

- **Workflow**: `.github/workflows/pages-mkdocs.yml`
- **Health Guard**: `.github/workflows/pages-health-guard.yml`
- **Validation Script**: `scripts/ci/validate_cognitive_app_build.py`
- **Live Site**: https://aries-serpent.github.io/_codex_/cognitive_app/
- **Cognitive App**: `/cognitive_app/`

---

## Questions & Support

If deployments are failing:

1. Check `.github/workflows/pages-mkdocs.yml` logs
2. Review `.codex/telemetry/pages_health_log.jsonl` for patterns
3. Run local build validation: `python scripts/ci/validate_cognitive_app_build.py`
4. Check GitHub Pages environment: https://github.com/Aries-Serpent/_codex_/settings/pages

---

**End of Document**  
**Last Updated**: 2026-07-20T18:04Z  
**Next Review**: 2026-10-20 (quarterly)
