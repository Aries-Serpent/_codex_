# Lane 6 Brief: Validation & Release

**Lane 6 Owner:** `qa-walkthrough-agent`, `autonomous-test-healer-agent`  
**Duration:** Days 20-21 (Phase 4)  
**Authority:** @mbaetiong D-tier approved

---

## 🎯 Lane 6 Objective

Validate that the packaged system is genuinely installable and usable in isolated environments, then prepare release artifacts with integrity checks and signatures for external distribution.

---

## 📋 Deliverables

### Phase 4 (Days 20-21)

1. **Clean-Room Build Validation Report**
   - Environment: Fresh Ubuntu 22.04 LTS VM, no prior artifacts
   - Process:
     1. Download codex-core-0.1.0.whl (from CI artifacts or mirror)
     2. `pip install codex-core-0.1.0.whl`
     3. Run smoke tests: `codex --version`, `codex-cognitive health`
     4. Verify no import errors, no external network calls
   - Results: ✅ All tests pass (or detailed failure log)
   - Coverage: Test all 3 profiles (core, runtime, full)
   - Report: Document success/failure for each platform

2. **Offline Installation Validation Report**
   - Environment: Air-gap network (no internet)
   - Process:
     1. Have wheelhouse/ directory pre-downloaded
     2. Run OFFLINE_BOOTSTRAP.sh [core|runtime|full]
     3. Verify installation succeeds without internet
     4. Test all entrypoints work in offline mode
   - Coverage: Ubuntu 22.04, macOS 12+, Windows 10+
   - Report: Success/failure per platform, time to completion

3. **Isolated-Network Validation Report**
   - Environment: Restricted egress (localhost only)
   - Process:
     1. Install codex-core
     2. Set `CODEX_NETWORK_MODE=isolated`
     3. Attempt external HTTP(S) request → PolicyViolationError (expected)
     4. Verify audit log records attempt
     5. Test allowed hosts work (if configured)
   - Report: Policy enforcement validation per host

4. **Cognitive Health Assessment**
   - Run cognitive engine health checks:
     - Memory usage (STM vs LTM)
     - Decision logging (no errors)
     - Session persistence (save/resume works)
   - Cognitive OODA verification: Confirm all phases execute correctly
   - Risk assessment: Any unresolved gaps?
   - Report: Health status + recommendations

5. **Release Candidate Artifacts**
   - Wheels:
     - `codex-core-0.1.0.whl`
     - `codex-core-0.1.0.tar.gz` (sdist)
   - Manifests:
     - `codex-core-0.1.0.sbom.json` (CycloneDX format, software bill of materials)
   - Checksums:
     - `SHA256SUMS` file with all artifact hashes
   - Signatures (optional):
     - `SHA256SUMS.asc` (GPG signature, if CODEX_MASTER_KEY available)
   - Metadata:
     - `RELEASE_CANDIDATE_MANIFEST.md` (artifact list, sizes, dates)

6. **Final Validation Report**
   - Executive summary: Ready for release? ✅ YES / ❌ NO
   - Test results: All platforms, all profiles
   - Known issues: Any blockers or limitations?
   - Recommendations: Next steps for production release
   - Sign-off: QA lead approval + cognitive health assessment

---

## 🚀 Execution Roadmap

### Day 20: Clean-Room & Offline Validation

**Task 6.1: Clean-Room Build (Ubuntu 22.04)**
- Environment setup:
  1. Launch fresh Ubuntu 22.04 VM in cloud or Docker
  2. Install Python 3.12: `apt-get install python3.12 python3.12-venv python3.12-dev`
  3. Create venv: `python3.12 -m venv /tmp/test-env`
  4. Install wheel: `pip install codex-core-0.1.0.whl`
- Testing:
  1. `codex --version` → Should print version
  2. `codex-cognitive health` → Should show OK
  3. Import test: `python -c "from codex.cognitive_brain import OODA; print(OK)"`
- Result: PASS ✅ or document specific failures
- Time: ~15 minutes total
- Output: Clean-room validation report

**Task 6.2: Offline Installation (Ubuntu, macOS, Windows)**
- Prerequisite: Wheelhouse directory with all wheels pre-downloaded
- Process per platform:
  1. Extract wheelhouse/ to test environment
  2. Run OFFLINE_BOOTSTRAP.sh core
  3. Verify all core entrypoints work: `codex --version`
  4. Run OFFLINE_BOOTSTRAP.sh runtime
  5. Verify runtime entrypoints work: `codex-cognitive health`
  6. Verify NO network calls (monitor with `strace` or process monitor)
- Expected duration: 20 min per platform × 3 = 60 min total
- Output: Offline validation report (platform matrix)

**Task 6.3: Isolated-Network Validation**
- Setup: Restrict egress to localhost only (iptables or firewall rules)
- Test sequence:
  1. Install codex-core in this restricted environment
  2. Run: `CODEX_NETWORK_MODE=isolated codex-cognitive health`
  3. Verify health check completes without network calls
  4. Attempt request to external host: `python -c "import requests; requests.get('https://example.com')"` → Should raise PolicyViolationError
  5. Review audit log: `cat ~/.codex/network-audit.log` → Should show denied attempt
  6. Test allowed host (if configured): Should succeed
- Output: Isolated-network validation report

### Day 21: Release Candidate Preparation

**Task 6.4: SBOM Generation**
- Tool: `cyclonedx-bom` or `syft`
- Generate software bill of materials:
  ```bash
  cyclonedx-bom -o codex-core-0.1.0.sbom.json --output-format json
  ```
- Includes: All dependencies, versions, licenses, known vulnerabilities
- Verify: SBOM valid JSON, includes all transitive dependencies
- Output: `codex-core-0.1.0.sbom.json`

**Task 6.5: Checksum Generation**
- Generate SHA256 hashes:
  ```bash
  sha256sum codex-core-0.1.0.whl codex-core-0.1.0.tar.gz codex-core-0.1.0.sbom.json > SHA256SUMS
  ```
- Verify hashes:
  ```bash
  sha256sum -c SHA256SUMS
  ```
- Output: `SHA256SUMS` file

**Task 6.6: GPG Signature (if available)**
- Check for CODEX_MASTER_KEY:
  ```bash
  gpg --list-secret-keys | grep CODEX_MASTER_KEY
  ```
- If available, sign checksums:
  ```bash
  gpg --armor --sign --detach-sig SHA256SUMS
  ```
- Output: `SHA256SUMS.asc` (if key available)

**Task 6.7: Release Candidate Manifest**
- Create `RELEASE_CANDIDATE_MANIFEST.md`:
  ```markdown
  # Release Candidate: codex-core v0.1.0-external
  
  **Build Date:** 2026-07-21T18:00:00Z
  **Builder:** qa-walkthrough-agent
  
  ## Artifacts
  
  | File | Size | SHA256 |
  |------|------|--------|
  | codex-core-0.1.0.whl | 18.5 MB | abc123... |
  | codex-core-0.1.0.tar.gz | 22.1 MB | def456... |
  | codex-core-0.1.0.sbom.json | 125 KB | ghi789... |
  
  ## Validation Results
  
  - ✅ Clean-room build (Ubuntu, macOS, Windows)
  - ✅ Offline installation
  - ✅ Isolated-network mode
  - ✅ Cognitive health assessment
  
  ## Known Issues
  
  None identified.
  
  ## Sign-Off
  
  - QA Lead: qa-walkthrough-agent
  - Cognitive Health: PASS
  - Ready for Release: YES
  ```
- Output: `RELEASE_CANDIDATE_MANIFEST.md`

**Task 6.8: Cognitive Health Assessment**
- Run final OODA loop verification:
  1. Execute `codex-cognitive run --config test-config.yaml`
  2. Monitor: All OODA phases (observe, orient, decide, act) complete
  3. Check memory: STM→LTM consolidation works
  4. Verify logging: Decision log recorded correctly
- Final risk assessment: Any unresolved issues?
- Output: Cognitive health report

**Task 6.9: Final Validation Report**
- Executive summary: Ready for release? YES ✅ or NO ❌
- Test matrix:
  ```
  Clean-Room Build:
    Ubuntu 22.04: ✅ PASS
    macOS 12: ✅ PASS
    Windows 10: ✅ PASS
  
  Offline Installation:
    Ubuntu: ✅ PASS (18 min)
    macOS: ✅ PASS (22 min)
    Windows: ✅ PASS (25 min)
  
  Isolated Network:
    Policy enforcement: ✅ PASS
    Audit logging: ✅ PASS
    Allowed hosts: ✅ PASS (if configured)
  
  Cognitive Health:
    OODA phases: ✅ PASS
    Memory systems: ✅ PASS
    Decision logging: ✅ PASS
  ```
- Blockers: None identified ✅
- Known limitations: (list any)
- Recommendations: Ready for public release
- Output: Final validation report + sign-off

---

## 🔗 Cross-Lane Dependencies

### Lane 6 ← All Lanes (Validation ← All Deliverables)

**Dependency:** All lanes deliver final artifacts by Phase 2 Day 16
- Lane 1: Final pyproject.toml + wheels
- Lane 2: Final lockfile + OFFLINE_BOOTSTRAP.sh
- Lane 3: Final cognitive engine APIs + CLI
- Lane 4: Final network policy + PolicyViolationError enforcement
- Lane 5: Final documentation (for reference during testing)
- **Sync Point:** By Phase 2 Day 16, all lanes ready for Phase 4 validation

### Lane 6 → @mbaetiong (Validation → Executive Approval)

**Dependency:** Final report delivered to @mbaetiong for release approval
- Lane 6 sign-off: Ready for public release? YES/NO
- Executive decision: Approve release or iterate?
- **Sync Point:** Phase 4 Day 21, final gate decision

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| Clean-room build passes | All 3 platforms successfully install + smoke test | qa-walkthrough-agent |
| Offline install passes | All 3 platforms, wheelhouse-only, no network | qa-walkthrough-agent |
| Isolated-network passes | PolicyViolationError blocking, audit log working | qa-walkthrough-agent |
| Cognitive health passes | OODA, memory, logging all functional | autonomous-test-healer-agent |
| SBOM generated | Valid JSON, complete dependency list | qa-walkthrough-agent |
| Checksums computed | SHA256 for all artifacts, verified correct | qa-walkthrough-agent |
| GPG signature (optional) | If key available, signature valid | qa-walkthrough-agent |
| Release manifest complete | All artifacts listed, test results documented | qa-walkthrough-agent |
| Final report approved | QA lead + cognitive health assessment sign-off | qa-walkthrough-agent |
| Phase 4 gate (Day 21) | All validation passed, ready for release | orchestrator-agent |

---

## 📌 Testing Platforms

**Primary (Required):**
- Ubuntu 22.04 LTS (standard Linux)

**Secondary (Recommended):**
- macOS 12+ (Apple Silicon or Intel)
- Windows 10/11 (if resource available)

**Testing Environment:**
- Clean VM or Docker container (no prior artifacts)
- Python 3.12 as primary test version
- Network isolation: firewall or iptables

---

## 🛠️ Tools & Commands

```bash
# Generate SBOM
cyclonedx-bom -o codex-core-0.1.0.sbom.json --output-format json

# Generate checksums
sha256sum codex-core-0.1.0.whl codex-core-0.1.0.tar.gz > SHA256SUMS
sha256sum -c SHA256SUMS  # Verify

# GPG sign (if available)
gpg --armor --sign --detach-sig SHA256SUMS

# Monitor network (Linux)
strace -e network codex-cognitive health

# Restrict network (Linux)
sudo iptables -A OUTPUT -j DROP  # Block all outbound
sudo iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT  # Allow localhost

# Clean test environment
docker run -it ubuntu:22.04 bash
```

---

## 📞 Escalation

**Test Failures or Blockers?** Report to orchestrator-agent with:
- Failed test name (which validation?)
- Error message or stack trace
- Environment details (platform, Python version, network setup)
- Proposed remediation (if you have one)

**Example:**
> Failure: Offline installation on Windows fails at hash verification step.
> Error: "sha256sum: command not found" (Windows doesn't have sha256sum by default)
> Environment: Windows 10, Python 3.12.1, no additional tools installed
> Proposed: Use Python's hashlib for cross-platform verification instead of sha256sum

