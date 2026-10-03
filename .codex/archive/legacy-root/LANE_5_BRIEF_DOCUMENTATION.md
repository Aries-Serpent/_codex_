# Lane 5 Brief: Documentation & Onboarding

**Lane 5 Owner:** `unified-doc-agent`  
**Duration:** Days 17-19 (Phase 3)  
**Authority:** @mbaetiong D-tier approved

---

## 🎯 Lane 5 Objective

Enable external users to install, configure, and integrate the packaged system by delivering comprehensive, user-focused documentation covering installation, offline deployment, integration, and troubleshooting.

---

## 📋 Deliverables

### Phase 3 (Days 17-19)

1. **.codex/archive/misc/INSTALL.md** — Online Installation Guide
   - Prerequisites: Python 3.12, pip, wheel
   - Install from wheel: `pip install codex-core-0.1.0.whl`
   - Install from sdist: `tar -xzf codex-core-0.1.0.tar.gz && pip install codex-core/`
   - Verify installation: `codex --version`
   - Troubleshooting: Common errors + solutions
   - Time estimate: <15 minutes from start to "codex --version" working

2. **OFFLINE_.codex/archive/misc/INSTALL.md** — Air-Gap Installation Guide
   - Prerequisites: Download wheels beforehand (wheelhouse/)
   - Setup: Python 3.12, pip, bash
   - Step-by-step: Run OFFLINE_BOOTSTRAP.sh, verify
   - Network-free validation: No internet required
   - Common issues: Hash verification failures, missing wheels
   - Time estimate: <20 minutes from start to fully installed

3. **docs/release/ISOLATED_DEPLOYMENT.md** — Whitelist-Only Networking
   - Enable offline mode: `export CODEX_NETWORK_MODE=isolated`
   - Verify isolation: `codex-cognitive health` confirms no network calls
   - Configure allowlist: Edit `.codex/network-policy.yaml`
   - Add approved hosts: Examples for common use cases
   - Security review: Audit log inspection, policy validation
   - Troubleshooting: "Network request blocked" errors, solutions

4. **docs/api/reference/INTEGRATION.md** — Embedding Guide
   - Use case: Embed cognitive engine in external Python application
   - Example code:
     ```python
     from codex.cognitive_brain import OODA, SessionManager
     
     ooda = OODA()
     session = SessionManager.create("my-session")
     result = ooda.execute(session_context=session)
     ```
   - Configuration: Settings via environment variables
   - Advanced: Custom OODA phases, pattern recognition usage
   - Packaging: Install with `pip install codex-core[runtime]`

5. **TROUBLESHOOTING.md** — FAQ & Common Issues
   - Question: "ModuleNotFoundError: No module named 'X'"
     - Answer: Install missing profile (e.g., `pip install codex-core[runtime]`)
   - Question: "Network request blocked: 'example.com'"
     - Answer: Update `.codex/network-policy.yaml` allowlist
   - Question: "SQLite database lock error"
     - Answer: Multiple processes; use `CODEX_DB_POOL=1` for per-session pooling
   - Question: "How do I verify offline mode is active?"
     - Answer: Run `CODEX_NETWORK_MODE=isolated codex-cognitive health`
   - Question: "Can I run multiple cognitive engines simultaneously?"
     - Answer: Yes, with separate session IDs and database paths
   - ... [20+ more common issues]

6. **docs/release/RELEASE_NOTES.md** — v0.1.0-external Release
   - Version: 0.1.0-external (or agreed version)
   - Features: 3 package profiles, offline support, whitelisted networking
   - Breaking changes: None (new release)
   - Migration: N/A (new release)
   - Security: 0 vulnerabilities in transitive dependencies
   - Contributors: Aries Serpent team
   - Artifact checksums: SHA256 for core, runtime, full wheels
   - GPG signatures: If available (CODEX_MASTER_KEY)

---

## 🚀 Execution Roadmap

### Days 17-18: Documentation Writing

**Task 5.1: .codex/archive/misc/INSTALL.md**
- Based on Lane 1 package profiles (core, runtime, full)
- Walkthrough: Download → pip install → verify
- Screenshots: Example terminal output
- Troubleshooting: Top 5 common errors
- Review by: packaging-validation-agent (Lane 1)
- Output: Final .codex/archive/misc/INSTALL.md

**Task 5.2: OFFLINE_.codex/archive/misc/INSTALL.md**
- Based on Lane 2 OFFLINE_BOOTSTRAP.sh
- Walkthrough: Download wheels → run bootstrap → verify
- Detailed: Hash verification, network-free validation
- Platforms: Ubuntu, macOS, Windows (with platform-specific notes)
- Review by: packaging-validation-agent (Lane 2)
- Output: Final OFFLINE_.codex/archive/misc/INSTALL.md

**Task 5.3: docs/release/ISOLATED_DEPLOYMENT.md**
- Based on Lane 4 network policy
- Setup: Enable offline mode, configure allowlist
- Examples: Add github.com, custom API hosts
- Verification: Audit log inspection, policy validation
- Review by: security-audit-agent (Lane 4)
- Output: Final docs/release/ISOLATED_DEPLOYMENT.md

**Task 5.4: docs/api/reference/INTEGRATION.md**
- Based on Lane 3 cognitive engine APIs
- Use case motivation: Why embed cognitive engine?
- Code examples: OODA loop, session management, memory
- Configuration: Environment variables, config files
- Advanced topics: Custom phases, pattern recognition
- Review by: cognitive-brain-cli-agent (Lane 3)
- Output: Final docs/api/reference/INTEGRATION.md

**Task 5.5: TROUBLESHOOTING.md**
- Collect issues from all lane teams
- Format: Question → Answer → Related docs
- Search keywords: "ModuleNotFoundError", "Network blocked", "SQLite lock", etc.
- Version-specific notes: Behavior may vary by profile
- Escalation path: When to contact maintainers
- Output: Final TROUBLESHOOTING.md

**Task 5.6: docs/release/RELEASE_NOTES.md**
- Lane 1: Package profiles, version
- Lane 2: Offline support, bootstrap mechanism
- Lane 3: Cognitive engine features, APIs
- Lane 4: Network policy, security posture
- Lane 6: Test coverage, validation results
- Output: Final docs/release/RELEASE_NOTES.md

### Days 18-19: Review & Finalization

**Task 5.7: Cross-Lane Review**
- Lane 1 reviews: .codex/archive/misc/INSTALL.md, docs/api/reference/INTEGRATION.md (mentions package profiles)
- Lane 2 reviews: OFFLINE_.codex/archive/misc/INSTALL.md (bootstrap, wheelhouse)
- Lane 3 reviews: docs/api/reference/INTEGRATION.md (cognitive APIs, CLI)
- Lane 4 reviews: docs/release/ISOLATED_DEPLOYMENT.md (network policy)
- Lane 6 reviews: All docs (ensure they reflect actual implementation)
- Collect feedback, iterate

**Task 5.8: Compliance Checks**
- All guides tested by actual user walkthrough (time-box each to stated time estimate)
- Example: .codex/archive/misc/INSTALL.md should work in <15 minutes
- Links: All internal doc links correct (no broken references)
- Code examples: All syntax correct (can run as-is)
- Screenshots: All current, reflect actual output
- Output: Compliance report

**Task 5.9: Final Assembly**
- Consolidate all docs into docs/ directory (TBD structure)
- Create index: docs/INDEX.md with links to all guides
- Add to repo: commit all docs with reference to campaign
- Output: Final documentation bundle

---

## 🔗 Cross-Lane Dependencies

### Lane 5 ← Lane 1 (Documentation ← Packaging)

**Dependency:** Lane 1 finalizes package profiles + entrypoints
- Lane 5 writes .codex/archive/misc/INSTALL.md using Lane 1 profiles
- Lane 5 needs final wheel filenames, profile names, sizes
- **Sync Point:** Lane 1 delivers finalized pyproject.toml by Day 9

### Lane 5 ← Lane 2 (Documentation ← Offline Bootstrap)

**Dependency:** Lane 2 finalizes OFFLINE_BOOTSTRAP.sh
- Lane 5 writes OFFLINE_.codex/archive/misc/INSTALL.md based on bootstrap script
- Lane 5 needs script usage, error messages, troubleshooting
- **Sync Point:** Lane 2 delivers final bootstrap by Phase 2 Day 14

### Lane 5 ← Lane 3 (Documentation ← Cognitive Runtime)

**Dependency:** Lane 3 finalizes cognitive engine APIs + CLI
- Lane 5 writes docs/api/reference/INTEGRATION.md + TROUBLESHOOTING.md with examples
- Lane 5 needs API documentation, CLI command syntax
- **Sync Point:** Lane 3 delivers API docs by Phase 1 Day 9

### Lane 5 ← Lane 4 (Documentation ← Network Policy)

**Dependency:** Lane 4 finalizes network policy YAML + enforcement
- Lane 5 writes docs/release/ISOLATED_DEPLOYMENT.md explaining policy
- Lane 5 needs policy examples, approved hosts, customization process
- **Sync Point:** Lane 4 delivers final policy by Phase 2 Day 16

### Lane 5 ← Lane 6 (Documentation ← Validation)

**Dependency:** Lane 6 validates installation experience
- Lane 6 tests actual installation + identifies pain points
- Lane 5 incorporates Lane 6 feedback into troubleshooting
- **Sync Point:** Lane 6 provides validation report by Phase 4 Day 21

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| .codex/archive/misc/INSTALL.md complete & tested | User walkthrough in <15 min | unified-doc-agent |
| OFFLINE_.codex/archive/misc/INSTALL.md complete & tested | Air-gap installation succeeds | unified-doc-agent |
| docs/release/ISOLATED_DEPLOYMENT.md complete | Policy configuration examples work | unified-doc-agent |
| docs/api/reference/INTEGRATION.md code examples valid | All code runs as-is | unified-doc-agent |
| TROUBLESHOOTING.md comprehensive | Covers top 20 issues | unified-doc-agent |
| docs/release/RELEASE_NOTES.md complete | All features, changes, checksums listed | unified-doc-agent |
| Cross-lane review passed | All lane leads approve docs | orchestrator-agent |
| Links verified | No broken internal references | unified-doc-agent |
| Phase 3 gate (Day 19) | All docs final, reviewed, ready for release | orchestrator-agent |

---

## 📌 Documentation Standards

- **Tone:** Clear, accessible, non-technical where possible
- **Audience:** DevOps, ML engineers, systems integrators (external users)
- **Format:** Markdown, with code blocks and examples
- **Links:** Internal (relative paths), external (with descriptions)
- **Version Notes:** Indicate which features apply to core vs runtime vs full
- **Time Estimates:** Every procedure should state expected duration
- **Screenshots:** Where helpful (terminal output, config examples)
- **Disclaimers:** Security, offline-mode limitations (if any)

---

## 🛠️ Documentation Tools & Checks

```bash
# Markdown linting
markdownlint .codex/archive/misc/INSTALL.md OFFLINE_.codex/archive/misc/INSTALL.md docs/release/ISOLATED_DEPLOYMENT.md

# Link validation
markdown-link-check .codex/archive/misc/INSTALL.md

# Code example syntax check
python -m py_compile examples/*.py

# Build docs (if using mkdocs or sphinx)
mkdocs build
sphinx-build -b html docs/ docs/_build/
```

---

## 📞 Escalation

**Documentation Issues or Ambiguities?** Report to orchestrator-agent with:
- Issue description (unclear instruction, outdated example, broken link)
- Affected guide (which document?)
- Severity (user-blocking, nice-to-have clarification)
- Suggested fix (if you have one)

**Example:**
> Issue: docs/api/reference/INTEGRATION.md example uses `OODA.execute()`, but actual method is `OODA.run()`. Severity: User-blocking. Fix: Update example code + Lane 3 API docs.

