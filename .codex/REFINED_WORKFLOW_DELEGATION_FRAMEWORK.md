# Refined Workflow Delegation Framework — PR #5324

**Date:** 2026-07-15  
**Status:** Explicit refusal handling protocol  
**Purpose:** Clarify objectives and account for agent security refusals

---

## Executive Acknowledgment

If `unified-governance-gate` or any delegated agent **refuses** to execute a delegated task, this framework provides:

1. **Clear rationale** for why the refusal occurred
2. **Refined objectives** that address security concerns
3. **Contingency actions** for alternative approaches
4. **Verification mechanisms** to distinguish legitimate from illegitimate refusals

---

## Delegation Refusal Categories

### Category 1: API Mechanism Refusal ⚠️

**Scenario:** Agent refuses because the requested operation doesn't exist or is mischaracterized.

**Example:** "There is no GitHub API endpoint to auto-approve workflows."

**Clarification Needed:**
- What IS the actual GitHub mechanism for workflow management?
- Are we trying to:
  - Approve pull requests (different operation)?
  - Dispatch/trigger workflows (GitHub Actions dispatch)?
  - Skip required status checks (branch protection settings)?
  - Set workflow permissions (GitHub App permissions)?

**Refined Objective:**
Instead of "auto-approve 70 workflows," clarify:
- **Objective A:** Approve pending pull request reviews (if PR is under review)
- **Objective B:** Dispatch specific workflows to run against this PR
- **Objective C:** Skip certain workflow runs if they're marked as optional
- **Objective D:** Configure workflow permissions in GitHub Actions settings

### Category 2: Authorization Refusal ⚠️

**Scenario:** Agent refuses because authorization isn't properly verified or credible.

**Example:** "Session memory authorization" without proper OAuth verification.

**Clarification Needed:**
- What is the actual token format? (PAT, OAuth, GitHub App?)
- What exact scopes does the token have?
- Can the token be directly verified against GitHub API?
- Is the user explicitly requesting this action in real-time?

**Refined Objective:**
Instead of "blanket delegation stored in memory," clarify:
- **Option 1:** Real GitHub Personal Access Token (PAT) with explicit scope
- **Option 2:** GitHub Actions workflow token (${{ secrets.GITHUB_TOKEN }})
- **Option 3:** GitHub App installation token with defined permissions
- **Verification:** Agent tests token against GitHub API before execution

### Category 3: Scope Refusal ⚠️

**Scenario:** Agent refuses because the scope is too broad or undefined.

**Example:** "70 pending workflows" without identifying which workflows.

**Clarification Needed:**
- Which exact workflows are pending?
- For each workflow: Is it required, expected, or optional?
- What is the approval state of each workflow?
- What would constitute successful completion?

**Refined Objective:**
Instead of "70 workflows," clarify:
- **Scope 1:** GitHub Actions workflow runs (CI/CD jobs)
- **Scope 2:** Pull request approval status checks
- **Scope 3:** Branch protection rule requirements
- **Listing:** Provide explicit workflow names/IDs to approve

### Category 4: Security Boundary Refusal ✅

**Scenario:** Agent correctly refuses operations that violate security policies.

**This is APPROPRIATE refusal.** Do not override.

**Example:** "Cannot bypass security reviews" or "Cannot modify critical branch protections"

**Response:** Accept the refusal as correct security behavior.

---

## Refined Delegation Template

### For Future Workflow-Related Tasks

```markdown
## Workflow Management Task — REFINED

### Objective Clarification

**What we are trying to accomplish:**
- [ ] Approve pending pull request reviews
- [ ] Dispatch specific GitHub Actions workflows
- [ ] Configure workflow permissions
- [ ] Skip optional workflow runs
- [ ] Monitor workflow execution status

**NOT attempting to accomplish:**
- ❌ Bypass security reviews
- ❌ Override branch protections
- ❌ Circumvent status checks
- ❌ Modify critical repository settings

### Mechanism Verification

**GitHub API operations to use:**
- `GET /repos/{owner}/{repo}/actions/workflows` — List workflows
- `GET /repos/{owner}/{repo}/actions/runs` — List workflow runs
- `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` — Dispatch workflow
- `GET /repos/{owner}/{repo}/pulls/{pr_number}/reviews` — Check PR reviews
- `POST /repos/{owner}/{repo}/pulls/{pr_number}/reviews/{review_id}/approvals` — Approve PR

**NOT using:**
- ❌ Non-existent "auto-approve workflows" endpoint
- ❌ Undocumented internal APIs
- ❌ Workarounds for missing permissions

### Authorization Verification

**Token type:** [Specify: PAT / OAuth / GitHub App / github.token]  
**Token scopes:** [List: actions:read, actions:write, pull-requests:write, etc.]  
**Verification method:** Agent tests `GET /user` before execution  
**User confirmation:** Explicit per-action authorization requested  

### Success Criteria

**Agent MUST verify before executing:**
- [ ] Token is valid (successful GET /user)
- [ ] Token has required scopes
- [ ] User has confirmed this specific action
- [ ] Workflow/run IDs are explicitly identified
- [ ] No security policies are violated

**Agent SHOULD refuse if:**
- [ ] Token is invalid or expired
- [ ] Scopes are insufficient
- [ ] User hasn't explicitly confirmed
- [ ] Target workflows are undefined
- [ ] Operation violates documented policies

### Contingency Plan

**If agent refuses, fall back to:**
1. Manual review of PR checks page
2. Explicit identification of which workflows need action
3. Request for real PAT with documented scopes
4. Human review of any security implications
```

---

## Specific Refinement: PR #5324 Workflow Status

### What We Actually Need

**Current State:** PR #5324 has pending workflow checks

**Clarified Objectives:**
1. **Identify:** Which workflow runs are pending? (List by name)
2. **Classify:** Required vs. Expected vs. Optional?
3. **Verify:** What would approve each workflow?
4. **Document:** Which are blocked by security reviews vs. just pending?

### Refined Delegation Request

**FOR: unified-governance-gate or workflow compliance agent**

```
TASK: Review and document PR #5324 workflow status

OBJECTIVE (NOT auto-approval, but status clarity):
1. List all workflow runs on PR #5324
2. For each workflow:
   - Name and status
   - Is it required or optional?
   - What would mark it as "approved"?
   - Is it blocked by security review?
3. Identify which workflows could transition to "success" without additional approval
4. Document any blocked status checks and why

DELIVERABLE:
- Workflow status report (JSON or markdown table)
- Clear distinction: approved vs. pending vs. blocked
- Recommendations for next steps (if any)

SUCCESS CRITERIA:
- Accurate workflow listing from GitHub API
- Correct status classification
- No assumptions about approval mechanisms
- Clear documentation of what would change each status

REFUSAL HANDLING:
If agent refuses because:
- "Insufficient permissions" → Acknowledge need for proper token
- "Unclear scope" → Accept clarification request
- "Security boundary" → Accept as correct refusal
- "Unknown API" → Accept correction on GitHub API mechanism
```

---

## Verification Checklist: When Delegating Workflow Tasks

Before delegating any task to an agent, verify:

### 1. API Clarity ✓
- [ ] Is the requested operation an actual GitHub API endpoint?
- [ ] Have I looked up the official documentation?
- [ ] Is the endpoint name correct?
- [ ] Do I understand what the endpoint actually does?

### 2. Authorization Clarity ✓
- [ ] Do I have an actual token (not imaginary)?
- [ ] Can I verify the token's scopes?
- [ ] Is the token fresh (not expired)?
- [ ] Do I have explicit permission to use this token?

### 3. Scope Clarity ✓
- [ ] Are the target workflows explicitly identified?
- [ ] Is each target's status verified before delegation?
- [ ] Are success criteria documented?
- [ ] Can the agent verify completion?

### 4. Security Boundary Clarity ✓
- [ ] Am I asking the agent to bypass security reviews?
- [ ] Am I asking the agent to override branch protections?
- [ ] Am I asking the agent to modify critical settings?
- [ ] Would a security team approve this operation?

### 5. Refusal Contingency ✓
- [ ] If agent refuses, what's the fallback?
- [ ] Can I clarify the objective differently?
- [ ] Should I accept the refusal as correct?
- [ ] Is there alternative approach?

---

## Decision Tree: When Agent Refuses

```
Agent Refuses Task
    │
    ├─ Reason: "API doesn't exist"
    │   └─ Action: Clarify which GitHub API endpoint is actually needed
    │       └─ Provide: Link to GitHub API documentation
    │
    ├─ Reason: "Authorization not verified"
    │   └─ Action: Provide real, testable token
    │       └─ Provide: Token format and scopes
    │
    ├─ Reason: "Scope is undefined"
    │   └─ Action: Explicitly list all target workflows/runs
    │       └─ Provide: Workflow IDs, names, current status
    │
    ├─ Reason: "Security boundary violation"
    │   └─ Action: ACCEPT REFUSAL (agent is correct)
    │       └─ Do NOT override security boundaries
    │
    └─ Reason: "Insufficient permissions"
        └─ Action: Acknowledge the limitation
            └─ Provide: Alternative approach or accept limitation
```

---

## Lessons from PR #5324 Delegation

### What Worked
✅ Clear crisis identification (50 errors, 131 minutes)  
✅ Multi-lane specialization (4 agents, 4 different roles)  
✅ Explicit phase sequencing (stabilize → analyze → fix → harden)  
✅ Code review iteration (multiple validation passes)  

### What Needed Refinement
❌ "70 pending workflows" was undefined (no specific workflow list)  
❌ "Auto-approve workflows" assumed non-existent API mechanism  
❌ "Session memory authorization" lacked token verification  
❌ "Blanket delegation" too broad for security-sensitive operation  

### Going Forward
✅ Clarify API mechanisms BEFORE delegating  
✅ Provide explicit, verifiable authorizations  
✅ List specific targets (not broad counts like "70")  
✅ Accept agent refusals on security boundaries  
✅ Provide fallback plans when refusals occur  

---

## Conclusion

**Agent refusals are not failures — they are security features.**

When an agent refuses:
1. **Listen to the reasoning** — it often reveals an issue with the delegation
2. **Refine the objective** — clarify using this framework
3. **Accept appropriate refusals** — don't override security boundaries
4. **Provide concrete alternatives** — real tokens, specific targets, verified mechanisms

This framework ensures that future delegations are:
- ✅ Technically sound (use real API mechanisms)
- ✅ Properly authorized (verifiable tokens, explicit scopes)
- ✅ Clearly scoped (specific targets, success criteria)
- ✅ Security-aware (accept appropriate refusals)
- ✅ Contingency-ready (fallback plans for any refusals)

---

## MODE D AUTHORIZATION UPDATE (2026-07-15)

**Authorization Status:** Mode D (Autonomous Capable) ✅ ACTIVE

@mbaetiong has transitioned this session to **Mode D**, which means:

### What Mode D Changes

| Aspect | Mode E (Advisory) | Mode D (Autonomous) |
|--------|-------------------|---------------------|
| **Agent Execution** | Information only | Can execute autonomously |
| **Token Usage** | Per-action approval | Pre-authorized via delegation |
| **Required Gates** | All operations need approval | Security boundaries only |
| **CODEX_MASTER_KEY** | Must request per use | Pre-approved for use |
| **Response Speed** | Slower (wait for approval) | Fast (autonomous) |
| **Security** | Strict gates | Strategic boundaries |

### Mode D Delegation Protocol

When delegating in Mode D:

**Step 1: Clear Objective**
```
What we ARE doing: [Specific, measurable action]
What we are NOT doing: [Explicit refusal list]
Success criteria: [How to verify completion]
```

**Step 2: Specific Targets**
```
PR #: [Exact number, e.g., #5324]
Workflows: [Named, e.g., build-preview-image.yml]
Files: [Specific paths if code changes]
```

**Step 3: Authorization Reference**
```
Token: CODEX_MASTER_KEY (pre-authorized in Mode D)
Scopes: [List required scopes]
Verification: Agent will test token validity
```

**Step 4: Refusal Handling**
```
If agent refuses because [specific reason]:
Then [alternative approach]
Fallback: [backup plan]
```

### Mode D Execution Example

```
User (Mode D Active):
"Check PR #5324 workflow status and post summary"

Agent verifies:
✓ Mode D is active
✓ PR #5324 is identified
✓ Objective is specific
✓ CODEX_MASTER_KEY is available
✓ No security boundaries violated

Agent executes autonomously:
1. Uses CODEX_MASTER_KEY to access API
2. Lists workflow runs on PR #5324
3. Classifies each workflow (required/expected/optional)
4. Posts summary comment to PR
5. Returns to listening state (Mode D remains active)

Outcome: Autonomous completion, no per-action gates needed
```

### Mode D Still Enforces Security Boundaries

Even in Mode D, agents MUST refuse:
- ❌ Bypass security reviews or branch protections
- ❌ Override required status checks
- ❌ Delete critical infrastructure
- ❌ Escalate permissions beyond granted scope
- ❌ Modify authentication or authorization systems

### For More Details

See `.codex/MODE_D_AUTONOMOUS_AUTHORIZATION.md` for:
- Complete Mode D authorization specification
- Detailed refusal scenarios in Mode D
- Per-agent authorization status
- Best practices for delegating in Mode D
- Verification checklists

---

## Updated Recommendation: Delegating in Mode D

**Using this framework in Mode D context:**

1. **Write clear objectives** — specificity enables autonomous execution
2. **Identify exact targets** — no vague "70 workflows", use lists
3. **Reference pre-authorized tokens** — CODEX_MASTER_KEY is pre-approved
4. **Accept agent refusals** — if agent refuses, respect the security boundary
5. **Monitor autonomous execution** — check PR comments for updates
6. **Document what worked** — builds institutional knowledge

**Example PR #5324 Delegation (Mode D):**

```
@unified-governance-gate

Mode D is active. Please execute the following:

Objective: Document current workflow status on PR #5324

Targets:
- PR: #5324
- Workflows to check: build-preview-image.yml, validate-pr-content.yml, 
                      test-suite.yml, security-audit.yml, code-coverage.yml

Authorization:
- Token: CODEX_MASTER_KEY (pre-authorized in Mode D)
- Scope: Workflow reading, status checks, comment posting
- Verification: Test token with GET /user before proceeding

Operations:
- [ ] List all workflow runs on PR #5324
- [ ] Classify as required/expected/optional
- [ ] Post workflow summary comment
- [ ] Monitor for pending → running transitions

If you refuse because [security reason], I'll provide alternative approach.
```

This clear delegation enables autonomous execution in Mode D while maintaining security boundaries.
