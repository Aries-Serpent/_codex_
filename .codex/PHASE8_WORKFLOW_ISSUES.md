# Phase 8 Workflow Validation - Detailed Issues

## Concurrency Issues (1)

### .github/workflows/copilot-agent-session-done.yml
**Issue**: Concurrency not properly branch-scoped
**Current Group**: `auto-post-copilot-review-${{ github.event.workflow_run.pull_requests[0] && githu`
**Required Pattern**: `group: ${ github.workflow }-${ github.head_ref || github.ref }`

## Timeout Issues (19 workflows)

1. **.github/workflows/admin-action-t03.yml**
   Missing timeout-minutes on: `check-t03`

2. **.github/workflows/benchmarks.yml**
   Missing timeout-minutes on: `noop`

3. **.github/workflows/build-preview-image.yml**
   Missing timeout-minutes on: `cost-gate`

4. **.github/workflows/cache-health-monitor.yml**
   Missing timeout-minutes on: `noop`

5. **.github/workflows/cache-validation.yml**
   Missing timeout-minutes on: `noop`

6. **.github/workflows/ci-templates/behavior-compare.yaml**
   Missing timeout-minutes on: `compare`

7. **.github/workflows/copilot-automation.yml**
   Missing timeout-minutes on: `noop`

8. **.github/workflows/data-quality-suite.yml**
   Missing timeout-minutes on: `cost-gate`

9. **.github/workflows/docker-build-push.yml**
   Missing timeout-minutes on: `cost-gate`

10. **.github/workflows/documentation-quality-check.yml**
   Missing timeout-minutes on: `noop`

11. **.github/workflows/embedding-index-rebuild.yml**
   Missing timeout-minutes on: `cost-gate`

12. **.github/workflows/examples/copilot-with-mcp.yml**
   Missing timeout-minutes on: `copilot-with-mcp`

13. **.github/workflows/examples/mcp-cache-warm.yml**
   Missing timeout-minutes on: `warm-python-cache`, `warm-playwright-cache`, `cleanup-old-caches`

14. **.github/workflows/maturity-check.yml**
   Missing timeout-minutes on: `noop`

15. **.github/workflows/progressive-validation.yml**
   Missing timeout-minutes on: `analyze`

16. **.github/workflows/release.yml**
   Missing timeout-minutes on: `generate-sbom`

17. **.github/workflows/rust_swarm_ci.yml**
   Missing timeout-minutes on: `cost-gate`

18. **.github/workflows/scheduled-archival.yml**
   Missing timeout-minutes on: `cost-gate`

19. **.github/workflows/semgrep_sarif.yml**
   Missing timeout-minutes on: `noop`

## Action Version Issues (150 workflows - sample)

1. **.github/workflows/actionlint-audit.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

2. **.github/workflows/admin_setup_verification.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

3. **.github/workflows/agent-auth-delegation.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

4. **.github/workflows/agent-handoff-gate.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

5. **.github/workflows/agent-orchestration-unified.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

6. **.github/workflows/agent-registry-validation.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

7. **.github/workflows/agent-var-writer.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

8. **.github/workflows/agent_infrastructure_manager.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

9. **.github/workflows/api-documentation.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`

10. **.github/workflows/app-package-download.yml**
   - `checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`
