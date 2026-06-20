# 🐳 PHASE X TRACK EPSILON - DOCKER REGISTRY & CONTAINER FIXES BRIEF

**Track:** ε (Docker Registry & Container Issues)  
**Execution Window:** 2026-06-20 12:00Z → 2026-06-21 11:00Z (23 hours)  
**Agents:** 3 (parallel, independent)  
**Root Cause:** 11% of CI failures (60/543) from Docker registry auth, image pulls, multi-stage build issues

---

## PROBLEM STATEMENT

**Current State:**
- 60+ failures from Docker registry (GHCR) access issues
- 30+ Dockerfile multi-stage build syntax errors
- Docker credentials not properly configured in some workflows
- Image pull failures due to rate limiting + auth issues
- Container image bloat (some images >2GB)

**Root Causes:**
1. **Registry Authentication** (40% of failures)
   - GHCR credentials not injected in all workflows
   - Missing `docker login` steps in build workflows
   - Expired credentials in cached workflows
   - Token scope issues (read-only vs. write permissions)

2. **Multi-Stage Build Issues** (35% of failures)
   - Invalid `FROM` syntax (missing stage names)
   - Incorrect `COPY --from` references
   - Build stage dependencies undefined
   - Unused intermediate stages not cleaned

3. **Image Registry Issues** (25% of failures)
   - Rate limiting on GHCR pulls
   - Image not found (wrong tag/version)
   - Network timeouts during pulls
   - Missing `.dockerignore` (bloated images)

---

## SUCCESS METRICS

| Metric | Target | Verification |
|--------|--------|--------------|
| **Failed Docker Pulls** | <3 (95% reduction) | GHCR audit logs |
| **Auth Errors** | 0 instances | Credential scan |
| **Dockerfile Syntax Errors** | 0 | Dockerfile linting |
| **Image Size** | <500MB (avg) | Registry audit |
| **Build Success Rate** | 100% | Docker build test runs |

---

## AGENT ASSIGNMENTS

### Agent 1: ci-docker-build-healer
**Task:** Fix Dockerfile syntax and diagnose registry issues

**Responsibilities:**
1. Analyze all Dockerfiles in repository:
   - 5+ Dockerfile variants (Dockerfile, Dockerfile.preview, etc.)
   - Multi-stage syntax validation
   - `COPY --from` reference verification
2. Fix issues:
   - Invalid `FROM` stage references
   - Missing intermediate stage names
   - Incorrect `COPY` paths in multi-stage builds
   - Unused stages cleanup
3. Generate Dockerfile audit:
   - `.codex/TRACK_EPSILON_DOCKERFILE_ANALYSIS.md`
   - 20+ syntax fixes
   - Multi-stage optimization recommendations
4. Validate: Docker builds successfully on all platforms

**Success Criteria:**
- All Dockerfiles pass linting (hadolint)
- Multi-stage builds execute successfully
- Image sizes <500MB average

**Output:** `.codex/PHASE_X_TRACK_EPSILON_DOCKERFILE_FIXES.md`

---

### Agent 2: workflow-ci-fixer
**Task:** Fix Docker workflow steps and credential injection

**Responsibilities:**
1. Scan all workflows using Docker:
   - 20+ workflows with Docker build steps
   - Registry login configurations
   - Image pull steps
2. Fix issues:
   - Add missing credential injection (GHCR tokens)
   - Update registry URLs to latest endpoints
   - Add rate-limit retries for image pulls
   - Verify token scopes match usage
3. Generate workflow updates:
   - `.codex/TRACK_EPSILON_WORKFLOW_DOCKER_FIXES.md`
   - 20+ workflows updated with credentials
   - 10+ workflows with retry logic added
4. Validate: Docker operations in workflows succeed

**Success Criteria:**
- All Docker workflows have proper credential injection
- No auth errors in workflow logs
- Image pulls complete within rate limits

**Output:** `.codex/PHASE_X_TRACK_EPSILON_WORKFLOW_DOCKER_FIXES.md`

---

### Agent 3: packaging-validation-agent
**Task:** Validate container registry configuration and image distribution

**Responsibilities:**
1. Audit Docker/container configuration:
   - `.dockerignore` optimization (reduce bloat)
   - Image layer optimization
   - Registry configuration validation
   - Push/pull credential management
2. Validate image distribution:
   - Test pushes to GHCR succeed
   - Verify images are retrievable
   - Check image metadata + tags
   - Validate signature/attestation (if used)
3. Generate registry audit:
   - `.codex/TRACK_EPSILON_REGISTRY_AUDIT.md`
   - 10+ .dockerignore improvements
   - 5+ layer optimization recommendations
   - Credential management verification
4. Implement best practices

**Success Criteria:**
- All images push to GHCR successfully
- Images retrievable after push
- Average image size <500MB
- Credential management verified

**Output:** `.codex/PHASE_X_TRACK_EPSILON_REGISTRY_VALIDATION.md`

---

## DELIVERABLES

### Track Output (Final)
- **File:** `.codex/PHASE_X_TRACK_EPSILON_DOCKER_FIXES.md`
- **Contents:**
  - Executive summary (60 failures → <3)
  - Dockerfile syntax fixes
  - Workflow credential injection
  - Registry configuration audit
  - Deployment readiness checklist

### Agent-Specific Outputs
1. `.codex/PHASE_X_TRACK_EPSILON_DOCKERFILE_FIXES.md` (Agent 1)
2. `.codex/PHASE_X_TRACK_EPSILON_WORKFLOW_DOCKER_FIXES.md` (Agent 2)
3. `.codex/PHASE_X_TRACK_EPSILON_REGISTRY_VALIDATION.md` (Agent 3)

### Code Changes
- Updated all Dockerfiles with corrected syntax
- Updated workflow Docker steps with credential injection
- Optimized .dockerignore to reduce image sizes
- Registry configuration validated

---

## SUCCESS GATE VERIFICATION

**Gate 5: Docker Registry & Container Issues**
- ✅ <3 failed pulls remaining (from 60)
- ✅ 0 auth errors in Docker workflows
- ✅ All Dockerfiles pass linting (hadolint clean)
- ✅ Image push/pull cycle validates

---

**Track Brief Created:** 2026-06-20T06:24:58Z UTC  
**Status:** READY FOR AGENT DEPLOYMENT AT 2026-06-20 12:00Z
