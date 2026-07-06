# Lane 4 Brief: Security & Whitelist-Only Networking

**Lane 4 Owner:** `security-audit-agent`  
**Duration:** Days 10-16 (Phase 2)  
**Authority:** @mbaetiong D-tier approved  
**Phase 0 Decision Leverage:** Strategic Decision #2 (Deny-by-default allowlist policy)

---

## 🎯 Lane 4 Objective

Enforce strict network isolation by implementing allowlist-only networking policy with fail-closed defaults, making network access impossible unless explicitly approved.

---

## 📋 Deliverables

### Phase 2 (Days 10-16)

1. **Network Policy YAML** (`.codex/network-policy.yaml`)
   - Deny-by-default configuration
   - Approved host allowlist (localhost + [TBD: github.com, pypi.org?])
   - Policy version + change log
   - Example:
     ```yaml
     version: "1.0.0"
     created: "2026-07-06"
     
     policy:
       offline_mode: true
       default_action: "DENY"
       
       allowlist:
         localhost:
           enabled: true
           description: "Always allowed"
         
         github_com:
           enabled: false
           description: "GitHub API, releases"
         
         pypi_org:
           enabled: false
           description: "PyPI package mirror"
       
       audit:
         log_all_attempts: true
         log_level: "WARN"
     ```

2. **PolicyViolationError Enforcement**
   - Custom exception class
   - Raised when attempting non-allowlisted network access
   - Includes audit log entry with:
     - Timestamp
     - Requested host
     - Caller location (file, function, line)
     - Suggested resolution
   - Example error message:
     ```
     PolicyViolationError: Network request to 'example.com' denied
       Reason: Host not in allowlist
       Policy: .codex/network-policy.yaml
       Action: Add to allowlist or use approved host
     ```

3. **Network Policy Enforcement Code**
   - Intercept all outbound HTTP(S) requests
   - Check against allowlist before connection
   - Implementation approach:
     - Wrapper around requests/httpx libraries
     - Monkey-patch at safety module level
     - Or: Custom session/adapter classes
   - Example architecture:
     ```python
     # src/codex/safety/network_policy.py
     
     class NetworkPolicy:
         def __init__(self, policy_file='.codex/network-policy.yaml'):
             self.config = load_policy(policy_file)
         
         def check_host(self, host: str) -> bool:
             """Check if host is allowlisted"""
             if self.config['offline_mode']:
                 return host in ('localhost', '127.0.0.1', '::1')
             # ... allowlist check logic
         
         def make_request(self, method, url, **kwargs):
             """Make HTTP request with policy enforcement"""
             host = urlparse(url).netloc
             if not self.check_host(host):
                 raise PolicyViolationError(...)
             return requests.request(method, url, **kwargs)
     ```

4. **Allowlist Validation Suite**
   - Tests confirming policy is enforced:
     - Attempt request to non-allowlisted host → PolicyViolationError
     - Attempt request to allowlisted host → Success (or expected result)
     - Offline mode enabled → All external requests blocked
     - Offline mode disabled + allowlist empty → All requests blocked
   - Test coverage: 100% of policy enforcement paths

5. **Network Audit Trail**
   - Log all network attempts (allowed + denied)
   - Format: JSON for machine parsing
   - Location: `~/.codex/network-audit.log`
   - Example entry:
     ```json
     {
       "timestamp": "2026-07-16T10:30:45Z",
       "event": "network_request_denied",
       "host": "external.com",
       "port": 443,
       "policy_version": "1.0.0",
       "caller": "codex/auth/github_app.py:42"
     }
     ```

---

## 🚀 Execution Roadmap

### Days 10-11: Policy Definition & Documentation

**Task 4.1: Network Policy YAML Finalization**
- Baseline allowlist from Phase 0 intelligence
- Add exceptions from Lane 2 dependency audit (if any external registries needed)
- Document approval procedure: How to add new hosts?
- Review with orchestrator-agent for alignment
- Output: Final `.codex/network-policy.yaml`

**Task 4.2: Policy Documentation**
- User guide: "How to configure network policy"
- FAQ: Common approved hosts, adding exceptions
- Security rationale: Why deny-by-default?
- Examples: Offline mode vs restricted egress vs full access
- Output: `docs/security/NETWORK_POLICY.md`

### Days 12-13: PolicyViolationError Implementation

**Task 4.3: Exception Class Definition**
- Create `PolicyViolationError` class in src/codex/safety/__init__.py
- Include: error message, host, policy reference, suggestion
- Make it catchable/loggable
- Output: Exception class implementation

**Task 4.4: Network Interception Layer**
- Choose interception strategy:
  - Option A: Wrapper around requests/httpx libraries
  - Option B: Monkey-patch at module import time
  - Option C: Custom session adapter classes
- Implement in `src/codex/safety/network_policy.py`
- Integrate with existing safety module
- Output: Network policy enforcement code

**Task 4.5: Audit Logging**
- Set up audit log file: `~/.codex/network-audit.log`
- Log format: JSON for parsing
- Include: timestamp, event type, host, caller location
- Rotation policy: Max file size, retention period
- Output: Audit logging implementation

### Days 14-15: Testing & Validation

**Task 4.6: Policy Enforcement Tests**
- Test 1: Offline mode enabled → All external requests blocked
- Test 2: Request to allowlisted host → Succeeds
- Test 3: Request to non-allowlisted host → PolicyViolationError
- Test 4: Error message includes host, policy file, suggestion
- Test 5: Audit log records attempt with caller location
- Output: Test suite (100% coverage of policy enforcement)

**Task 4.7: Edge Case Testing**
- Test: IPv6 localhost (::1)
- Test: Implicit port (80 vs 443)
- Test: Domain + subdomain (github.com vs api.github.com)
- Test: Policy reload (update .codex/network-policy.yaml at runtime)
- Output: Edge case test report

### Day 16: Validation & Integration

**Task 4.8: Integration with Lane 3**
- Review Lane 3 cognitive engine APIs
- Identify any network-dependent features (webhooks, external APIs)
- Add guards for those features (PolicyViolationError + documentation)
- Example: Webhook ingress requires explicit `CODEX_WEBHOOKS_ENABLED=true`
- Output: Integration verification

**Task 4.9: Phase 2 Gate Preparation**
- Confirm all tests passing
- Review audit logs for issues
- Prepare handoff to Lane 5 (documentation will reference policy)
- Output: Phase 2 readiness report

---

## 🔗 Cross-Lane Dependencies

### Lane 4 ← Lane 2 (Network Policy ← Offline Bootstrap)

**Dependency:** Lane 2 audit identifies any external registries needed
- Lane 2 reports if non-PyPI registries are required
- Lane 4 adds to allowlist (if necessary) or marks as optional
- **Sync Point:** Day 10, Lane 2 confirms audit findings

### Lane 4 ← Lane 3 (Network Policy ← Cognitive Runtime)

**Dependency:** Lane 3 identifies network-dependent features
- Lane 3 lists features requiring network (webhooks, external APIs)
- Lane 4 adds guards: explicit feature flags + PolicyViolationError
- **Sync Point:** Day 12, Lane 3 provides feature list

### Lane 4 → Lane 5 (Network Policy → Documentation)

**Dependency:** Lane 5 documents policy for external users
- Lane 4 delivers final policy + enforcement code by Day 16
- Lane 5 writes security guide + policy customization examples (Phase 3)
- **Sync Point:** Lane 5 has policy by Phase 3 Day 17

### Lane 4 → Lane 6 (Network Policy → Validation)

**Dependency:** Lane 6 validates policy enforcement in isolated networks
- Lane 6 tests PolicyViolationError blocking in Phase 4
- Lane 4 ensures policy is enforced in all code paths
- **Sync Point:** Lane 6 has final policy enforcement by Phase 2 Day 16

---

## ✅ Acceptance Criteria

| Criterion | Validation | Owner |
|-----------|-----------|-------|
| Network policy YAML complete | Config defined, documented, approved | security-audit-agent |
| PolicyViolationError implemented | Exception raised on non-allowlisted requests | security-audit-agent |
| Network interception working | All HTTP(S) requests checked against policy | security-audit-agent |
| Audit logging functional | All attempts logged to JSON audit file | security-audit-agent |
| Tests comprehensive | 100% policy enforcement code coverage | security-audit-agent |
| Edge cases handled | IPv6, subdomains, port normalization all correct | security-audit-agent |
| Documentation complete | User guide, FAQ, security rationale | security-audit-agent |
| Phase 2 gate (Day 16) | All policy enforcement working, tests passing | orchestrator-agent |

---

## 📌 Key Decisions from Phase 0

**Strategic Decision #2: Deny-by-default allowlist policy**
- ✅ APPROVED in INTELLIGENCE_CAMPAIGN_BASELINE.md
- Offline-first: No network by default (localhost only)
- Explicit allowlist: Add hosts as needed
- Fail-closed: Any error → deny access
- Audit trail: Log all attempts for security review

---

## 🛠️ Tools & Commands

```bash
# Test policy enforcement
python -c "from codex.safety import network_policy; policy.check_host('example.com')"

# Review audit log
cat ~/.codex/network-audit.log | jq .

# Offline test
CODEX_NETWORK_MODE=isolated python -c "import requests; requests.get('https://example.com')"  # Should error

# Update policy
vi .codex/network-policy.yaml
```

---

## 📞 Escalation

**Policy Conflicts or Security Issues?** Report to orchestrator-agent with:
- Issue description (conflict, security gap, usability problem)
- Impact assessment (affects which profile? core, runtime, or full?)
- Proposed resolution (adjust policy, add exception, refactor code)

**Example:**
> Issue: Lane 3 requires GitHub API for user authentication feature. But network policy blocks github.com by default. Conflict: External users in isolated network can't authenticate. Proposed: Mark auth feature as optional, requires `CODEX_GITHUB_AUTH_ENABLED=true` + allowlist update.

