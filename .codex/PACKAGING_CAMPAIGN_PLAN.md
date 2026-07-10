# Packaging Campaign Plan: External Downloadable Release
**Campaign Name:** `packaging-system-for-external-distribution`
**Status:** Planning Phase
**Created:** 2026-07-06T00:48:03Z
**Target Completion:** 2026-08-15
**Authority:** @mbaetiong (D-tier autonomy approved)

---

## 📋 Campaign Goal

Transform the Aries-Serpent/_codex_ repository into a packaged, downloadable, locally-installable system for external use with:
- First-class isolated deployment mode (offline/localhost-only by default)
- Whitelist-only networking with fail-closed defaults
- Clean build/install validation in empty environments
- External-user documentation and integration guides
- Reproducible release artifacts with integrity checks

---

## 🏗️ Repository Current State Analysis

### Existing Packaging Assets
- **Packaging Infrastructure:** `pyproject.toml` with console entrypoints and optional dependency groups
- **Distribution:** `MANIFEST.in` governs sdist contents
- **Offline Bootstrap:** `src/codex_ml/cli/offline_bootstrap.py` provides bootstrap helpers
- **Default Safety:** `src/safety/__init__.py` defaults `allow_network_calls = False`
- **Network Isolation:** `.codex/agent_context.json` signals `CODEX_NETWORK_MODE=isolated`

### Main Gaps
- Unclear packaging boundary for external use
- Missing explicit offline-first defaults in entry points
- No allowlist policy enforcement
- Limited external-facing documentation for local installation
- No reproducible build/test for clean-environment installs

---

## 🛣️ Campaign Structure: 6 Parallel Lanes

### Lane 1: Packaging and Distribution
**Owner Agent:** `packaging-validation-agent`  
**Duration:** 3-4 days  
**Objective:** Define and stabilize the artifact contract for external use

**Deliverables:**
- Clear wheel/sdist build path with reproducibility verification
- Separate "core" package vs "runtime/server" package profiles
- Minimal install profile for local external use
- Documented console entrypoints stable for external calls
- CI build artifact naming and retention plan

**Scope:**
- Package core runtime and cognitive engine by default
- Keep heavy ML/runtime features behind extras or optional profiles
- Define package metadata (version, authors, dependencies)
- Lock dependency versions for reproducibility

**Acceptance Criteria:**
- `pip install codex-core-0.1.0.whl` succeeds in clean venv
- Console entrypoints work as documented
- sdist produces identical wheel when reinstalled
- Optional profiles (ml, server, dev) install without pulling heavy deps

---

### Lane 2: Offline Bootstrap and Dependency Supply
**Owner Agents:** `packaging-validation-agent`, `documentation-quality-agent`  
**Duration:** 3-4 days  
**Objective:** Enable installation without relying on arbitrary public network access

**Deliverables:**
- Wheelhouse or approved local dependency source (lockfile + hashes)
- Hash-locked or lock file-based dependency policy
- Offline bootstrap workflow for a new local repository instance
- Air-gap install instructions and troubleshooting guide
- Dependency supply validation (no external registries by default)

**Scope:**
- Use existing offline/bootstrap assets as base
- Add documented local mirror/wheelhouse flow
- Make installs fail clearly if non-approved sources are attempted
- Provide fallback for restricted/air-gapped environments

**Acceptance Criteria:**
- Installation from archived wheels works without internet
- Lockfile provides audit trail of all transitive dependencies
- Bootstrap process completes in isolated network
- Error messages guide users on dependency resolution

---

### Lane 3: Cognitive-Brain Runtime Packaging
**Owner Agent:** `cognitive-brain-cli-agent`  
**Duration:** 4-5 days  
**Objective:** Package cognitive-brain capabilities as a portable local runtime

**Deliverables:**
- Core cognitive engine as stable, installable package
- Explicit local persistence defaults (SQLite/local state, no remote)
- Clear separation: offline-safe core logic vs networked runtime features
- Local-first defaults for memory, session state, caching
- CLI interface for runtime control and diagnostics

**Scope:**
- Package decision/analysis/orchestration engine as primary capability
- Keep any external integrations (webhooks, APIs) behind explicit opt-in
- Avoid assuming repo checkout paths
- Define local storage paths and permissions model
- Document expected behavior when network is disabled

**Acceptance Criteria:**
- Cognitive engine runs with `CODEX_NETWORK_MODE=isolated` by default
- All state persists to local SQLite/filesystem
- Webhook/webhook ingress requires explicit allowlist entry
- Offline mode is primary; network features are additive

---

### Lane 4: Security and Whitelist-Only Networking
**Owner Agent:** `security-audit-agent`  
**Duration:** 3-4 days  
**Objective:** Enforce strict network policy for packaged installs

**Deliverables:**
- Repository-level allowlist configuration for outbound hosts/domains
- Default mode: localhost/offline-only (fail-closed)
- Explicit fail-closed behavior for non-allowlisted outbound requests
- Packaging/install-time guardrails rejecting unrestricted network access
- Network audit trail and policy enforcement validation

**Scope:**
- Cover package install, runtime fetches, webhook ingress, outbound proxying
- Define "approved host" policy clearly for external use
- Make unrestricted outbound networking impossible by default
- Document exception procedures for approved additions
- Implement network policy as code (YAML allowlist)

**Acceptance Criteria:**
- Attempting unapproved HTTP(S) request raises PolicyViolationError
- Allowlist defined in `.codex/network-allowlist.yaml`
- Documentation explains how to add approved hosts
- Install-time checks verify no network-dependent packages in core

---

### Lane 5: Documentation and Onboarding
**Owner Agent:** `documentation-quality-agent`  
**Duration:** 3-4 days  
**Objective:** Make the packaged system consumable by external users

**Deliverables:**
- **Installation Guides:**
  - Download/install from wheel/sdist/archive
  - Clean-environment smoke test script
  - Troubleshooting: dependency conflicts, missing assets
- **Isolated Deployment Guide:**
  - Offline-only configuration
  - Local repository embedding for isolated use
  - Network allowlist customization
- **Integration Guide:**
  - How to embed into external projects
  - SDK/library usage examples
  - Configuration and environment variables
- **First-Run Guide:**
  - Smoke test and diagnostics
  - How to verify isolated mode is active
  - Expected behavior and error recovery
- **Release Notes:**
  - Artifact checksums and signature verification (if applicable)
  - Breaking changes and migration paths
  - Security advisories and patching

**Scope:**
- Clear step-by-step instructions for non-developers
- Expect target audience: DevOps, ML engineers, integrators
- Minimize repository context assumptions
- Provide downloadable artifacts and quick-start commands

**Acceptance Criteria:**
- External user can follow guide to install in <30 minutes
- Offline install documented and verified
- Troubleshooting resolves top 10 issues without escalation
- Release artifacts are discoverable and checksummed

---

### Lane 6: Validation and Release
**Owner Agent:** `qa-walkthrough-agent` or `unified-coverage-agent`  
**Duration:** 4-5 days  
**Objective:** Prove the packaging is genuinely usable outside the source repo

**Deliverables:**
- Clean-environment build validation (no repo checkout required)
- Offline install validation (no network access)
- Isolated-network install validation (restricted egress)
- Smoke test for local repo integration
- Release checklist for repeatable external releases
- Artifact integrity validation (checksums, signatures if applicable)

**Scope:**
- Validate both core and runtime profiles
- Test on representative target platforms (Ubuntu, macOS, Windows)
- Verify system still works when network is disabled
- Create CI workflow for release validation (if not already present)
- Document release procedure for future versions

**Acceptance Criteria:**
- Clean-room install succeeds from archived wheel
- Offline mode functions identically to networked mode for core
- Smoke tests pass in isolated-network environment
- Release checklist reduces manual steps to <10
- Artifact signatures verify against public key (if applicable)

---

## ⏱️ Execution Phases

### Phase 0: Alignment and Contract Definition
**Duration:** 1 day  
**Activities:**
- Lock target packaging profiles (core vs runtime vs optional)
- Define default network posture and allowlist structure
- Determine target Python versions and platforms
- Agree on release artifact formats (wheel, sdist, archive)
- Identify external dependencies and licensing concerns

**Owner:** `orchestrator-agent` (coordination)  
**Gate:** All lanes confirm scope and deliverables

---

### Phase 1: Packaging Refactor
**Duration:** 5-7 days  
**Activities:** Lanes 1–3 execute in parallel
- **Lane 1:** Stabilize package profiles and entrypoints
- **Lane 2:** Establish lockfile and offline bootstrap flow
- **Lane 3:** Package cognitive engine as portable runtime

**Checkpoint (Day 5):** All lanes produce initial deliverables; cross-lane review

---

### Phase 2: Isolation Hardening
**Duration:** 5-7 days  
**Activities:** Lanes 2–4 execute with Lane 1 on standby for iteration
- **Lane 2:** Finalize offline bootstrap and dependency supply
- **Lane 3:** Enforce local-only persistence defaults
- **Lane 4:** Implement allowlist enforcement and fail-closed behavior

**Checkpoint (Day 10):** Network policy enforced; offline mode validated

---

### Phase 3: Documentation and Release Prep
**Duration:** 4-5 days  
**Activities:** Lane 5 executes; Lanes 1–4 review and iterate
- **Lane 5:** Publish all guides, examples, release notes
- **Cross-check:** Validate documentation against actual behavior
- **Release:** Draft release announcement and artifact metadata

**Checkpoint (Day 14):** Documentation complete; ready for external review

---

### Phase 4: Validation and Rollout
**Duration:** 5-7 days  
**Activities:** Lane 6 executes full validation; Lanes 1–5 support
- **Lane 6:** Run clean-room, offline, and isolated-network tests
- **Feedback Loop:** Identify and patch issues found during validation
- **Release Candidate:** Package and sign release artifacts
- **Publication:** Upload to download site (if applicable) and announce

**Checkpoint (Day 21):** Release candidate ready for production rollout

**Final Gate:** Executive review and approval for external availability

---

## 📦 Recommended Deliverables for the Campaign

### Artifacts
1. **`codex-core-0.1.0.whl`** — Core package wheel
2. **`codex-core-0.1.0.tar.gz`** — Sdist archive
3. **`codex-core-0.1.0.sbom.json`** — Software Bill of Materials
4. **`lockfile.lock`** — Locked dependency manifest with hashes
5. **`OFFLINE_BOOTSTRAP.sh`** — Bootstrap script for air-gap installs
6. **`network-allowlist.yaml`** — Whitelist policy
7. **`docs/release/RELEASE_NOTES.md`** — Release notes with breaking changes
8. **`.codex/archive/misc/INSTALL.md`** — Installation guide (online and offline)
9. **`ARCHITECTURE.md`** — High-level architecture for integrators
10. **`TROUBLESHOOTING.md`** — Common issues and resolutions

### Documentation
- Installation and quick-start guides
- Offline/isolated deployment playbooks
- Local repo integration examples
- API/SDK reference for embedded use
- Security and network policy guide
- Release checklist and validation procedure

### Code Changes
- Package profile separation (core vs runtime)
- Offline-first configuration defaults
- Network allowlist enforcement
- Local persistence initialization
- CLI diagnostics and health checks

---

## ✅ Success Criteria

### Campaign Success = All 6 Lanes Deliver + Final Gate Passes

| Criterion | Lane(s) | Validation |
|-----------|---------|-----------|
| Clean environment can build/install from archive | 1, 6 | `pip install codex-core-0.1.0.whl` succeeds in empty venv |
| Package installs without requiring public network | 2, 4, 6 | Installation from lockfile in air-gap completes |
| Default runtime stays local-only and isolated | 3, 4, 6 | `CODEX_NETWORK_MODE=isolated` enforced by default |
| Non-allowlisted network access is blocked | 4, 6 | Attempted unapproved HTTP request raises PolicyViolationError |
| External user can install and run locally | 5, 6 | Follow guide → install → run → pass smoke tests in <1 hour |
| Release artifacts are auditable and secure | 1, 6 | Checksums/signatures present and verifiable |

---

## 🚀 Next Steps

### Immediate (Today)
1. Confirm campaign scope with @mbaetiong
2. Assign lead agents to each lane
3. Schedule synchronization meetings (e.g., Phase 0 alignment)

### Short-Term (This Week)
1. **Lane Leads** begin Phase 0 contract definition
2. **orchestrator-agent** coordinates cross-lane dependencies
3. **packaging-validation-agent** spikes on current packaging state

### Medium-Term (Next 2-3 Weeks)
1. Execute Phases 1-4 as planned
2. Track progress against 6-lane dashboard
3. Escalate blockers to @mbaetiong for executive resolution

### Long-Term (Production Release)
1. Publish release artifacts and documentation
2. Announce external availability
3. Establish maintenance and patching cadence

---

## 📊 Campaign Tracking Dashboard

**Status:** Not yet active (awaiting approval)  
**Phases Completed:** 0/4  
**Lanes Ready:** 0/6  
**Target Gate:** Phase 4, Lane 6, ~21 days from start  
**Authority:** @mbaetiong (D-tier autonomy)

---

## 🔗 Related Documents

- **Repository Status:** `.codex/AGENTIC_REPO_STATE.md`
- **Packaging Config:** `pyproject.toml`, `MANIFEST.in`
- **Current Network Policy:** `src/safety/__init__.py`
- **Agent Registry:** `.github/agents/AGENT_REGISTRY.yaml`
- **Multi-Agent Framework:** `.codex/MULTI_AGENT_IMPLEMENTATION_CAMPAIGN_PLAN.md`

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-06T00:48:03Z  
**Next Review:** After Phase 0 alignment meeting
