# Remaining execution guide: protected approval and PR #5766 ML repair

## 1. Scope and remaining evidence

This guide contains only the remaining approval/ML repair, administrator,
publication and hosted-validation actions. Obsolete Rust publication examples,
repeated workspace setup and unrelated profile-invocation instructions have
been removed. Separate CDX custody, isolation and real-source requirements
remain in the [continuation](./CONTINUATION.md); they are not cleared by this
repair. No archive operation or hosted CDX launch is requested here.

Historical read-only observations from the original repair session:

| Item | Observation | Remaining owner/action |
| --- | --- | --- |
| #5766 | Open at `34f9e6cfd4d76f5b031e83891c6351f52045c372`; persistent WEC label present | Integration maintainer: review/publication, then exact-SHA hosted proof |
| `owner-approval` | Rechecked 2026-11-13T04:40Z: `protection_rules: []`, `can_admins_bypass: true`, `deployment_branch_policy: null`; agent `PUT` returned HTTP 403 (`administration=write` required) | @mbaetiong (sole repository admin): configure genuine protection (section 2) |
| Environment marker | Delegation job `131666794042` logs show an empty runtime marker and exit 1; secret inventory/public-key reads returned HTTP 403 | @mbaetiong: provision the environment-only marker after protection |
| Reviewer identity | Only human collaborator is `mbaetiong` (admin); owner delegates maintainer work to agents | Use a verified agent-maintainer identity and genuine independent current-head review; another human is not a repository requirement |
| CODEX PAT routes | Rechecked: `CODEX_ADMIN_KEY`, `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY` codespace values all return HTTP 401 on `GET /user` | Credential owner: rotate the codespace and Actions secrets (section 3) |
| App route | Rechecked: codespace `_GITHUB_APP_PRIVATE_KEY` is 51 characters and not PEM, so no App token can be minted locally; repository secret and Actions-permission reads return HTTP 403 | App owner: replace the key and verify the installation (section 3) |
| Slow ML | Run `43358318768` job `131670399212` was **cancelled** by the 60-minute job timeout; its log blob was discarded (`BlobNotFound`) | Implemented in this repair: durable JUnit artifact and step budgets (section 4) |
| ML failure evidence | Surviving earlier completed job `131011045588`, run `43165845712`, SHA `3cee1ffea0`: **59 failed, 1,657 passed**. Local reproduction confirms multiple failures; it is not the requested run's traceback | Repair confirmed causes; verify the requested run independently and run fresh hosted tests |
| Delegation verifier | `activate-delegation` lacked `actions: read`, so its environment read would return 403 even after configuration | Implemented in this repair: job-scoped permissions plus regression test |

Refresh changing hosted state before acting. Instructions below do not grant
permissions or establish that an operation succeeded. Do not reset, stash,
rebase, discard dirty work, disable signing or weaken protection to proceed.

### Two approvals, two acceptance records

- **Workflow-run approval:** WEC opt-in permits inspection of held Actions runs.
  The helper requires independently attributed maintainer review of the exact current PR head,
  an eligible independently authenticated approver and unambiguous run/PR
  association. Labels alone never establish approval.
- **Environment deployment approval:** GitHub required reviewers release a job
  waiting on `owner-approval`. WEC labels neither configure nor approve this
  deployment and never supply `OWNER_APPROVAL_PROTECTED`.

The repaired once grant uses the latest verified human GitHub label activation,
not PR creation, with a fixed one-hour maximum. Missing, revoked, future,
bot-issued or incomplete activation evidence denies approval. Dispatch TTL
inputs cannot extend it. Cleanup requires a verified completed Copilot session
that started after activation and a successful, non-dry approval batch; changed
heads/new activations and denied/dry paths preserve the label.

Automatic inspection uses trusted default-branch events and the configured
Copilot workflow events. Recovery sweeps run daily at **06:00 UTC**, not every
20 minutes; GitHub may delay schedules. Privileged helper checkout is bound
to the published workflow SHA, never PR-controlled code. The delegated-maintainer
repair verifies the App using its signed JWT, active installation, repository
owner, minted permissions and expiry. It does not call `/user` to pretend an
installation token is a human account. Only that verified App's bot review can
satisfy the agent-review route; arbitrary bots and labels alone remain ineligible.

### Agent-maintainer authority and live capability preflight

The owner explicitly authorizes agents to perform maintainer and administrator
duties. A second human is not required by this repository's operating model.
Review records must still come from an eligible identity other than the author
and run initiator, cover the exact current SHA, and survive GitHub's actual
required-review and deployment-review controls. A request by the sole owner can
start inspection by an independently attributed App; it is not itself approval.

Run this read-only preflight in subsequent sessions before attempting denied
operations:

```bash
python -m scripts.ci.github_auth_preflight \
  --repo Aries-Serpent/_codex_ --branch 0D_base_ --json
```

It tries configured credential routes independently, reports operation-specific
HTTP results without values or response bodies, and exits nonzero when required
reads are unavailable. A failed named CODEX key does not hide a working
`GITHUB_TOKEN` route. App settings accept the documented `GITHUB_APP_*` names
or their `_GITHUB_APP_*` Codespace aliases. Secret metadata cannot establish
that its value is `true`; only the protected runtime verifier can establish that.
Successful reads, static token-name scope maps and `permissions.admin=true`
never establish write authority. The preflight makes no mutations.

## 1a. Which CLI actions the Copilot agent can perform

The requested scoped repair permits local implementation and preparation.
Any separately authorized publication or administration does not change what the
credential itself can do. The codespace `GITHUB_TOKEN` is a GitHub App
integration token acting as `mbaetiong`. Each guide action was probed
(2026-11-13T04:40Z):

| Guide action | Endpoint / command | Agent result | Who must act |
| --- | --- | --- | --- |
| Read environment protection | `GET environments/owner-approval` | HTTP 200 (works) | Agent |
| Configure reviewers / branch policy | `PUT environments/owner-approval` | HTTP 403, requires `administration=write` | @mbaetiong |
| Disable administrator bypass | UI only | No UI access | @mbaetiong |
| Create/list environment secret | `gh secret set/list --env owner-approval` | HTTP 403 (secrets and public key) | @mbaetiong |
| List repository secrets / Actions permissions | `GET actions/secrets`, `GET actions/permissions` | HTTP 403 | @mbaetiong |
| Rotate CODEX PATs / App key | secrets UI | Codespace values return 401 / non-PEM | Credential owner |
| Download run logs and job metadata | `GET actions/runs/{id}/attempts/{n}/logs` | HTTP 200 (works) | Agent |
| Push session branch, open sub-PR | `git push`, `POST pulls` | Published draft [#5783](https://github.com/Aries-Serpent/_codex_/pull/5783) | Completed; review remains |
| Approve deployment / PR | `POST pending_deployments`, PR review | Same-identity self-review remains prohibited; separately authenticated eligible agent maintainers can provide real review | Verified eligible maintainer identity |
| Dispatch delegation from `main` | `gh workflow run agent-auth-delegation.yml` | Only meaningful after the repair reaches `main` and section 2 is complete | Agent (after merge) or @mbaetiong |

An authorized delegated agent can perform the administrator rows using a
credential with the actual operation-specific permissions. A denied token
requires credential repair, not another statement of owner authorization.
Browser-only controls still require an available authorized browser session.
Do not grant organization administration merely to read reviewer teams.
Run those commands from that session; the agent cannot obtain the scopes.

## 2. Administrator: configure `owner-approval`

**Responsible operator:** authorized repository/security administrator.
**Required reviewer:** an eligible independently authenticated maintainer or approved team,
not the deployment initiator. PR review and deployment review are separate.

### Step 1: confirm operation authority and supported protection

1. Sign in to GitHub with the authorized administrator account.
2. Open `Aries-Serpent/_codex_` and **Settings > Environments > owner-approval**.
3. Confirm authorization to change this environment and its secrets. A cached
   token flag, label or repository metadata does not grant that authority.
4. If the plan/visibility does not support required environment reviewers, stop
   and obtain a supported protected execution arrangement from the owner.
5. Inspect current settings; preserve unrelated timers, custom protection and
   branch controls. Do not replace existing policy blindly.

CLI read-only equivalents, using normal approved authentication:

```bash
REPO=Aries-Serpent/_codex_
gh auth status
gh api "repos/$REPO/environments/owner-approval" \
  --jq '{protection_rules, can_admins_bypass, deployment_branch_policy}'
```

Do not paste credentials into commands, chat or repository files. Authentication
is not proof of settings-write, secret-write or independent-review authority.

### Step 2: require independent review and prevent self-review

`mbaetiong` is the sole human owner. With **Prevent self-review** enabled,
GitHub blocks the deployment initiator's identity from approving its deployment.
Use distinct, genuinely authenticated eligible identities for initiation and
review, including delegated agents where the platform supports them. For
example, an App-initiated run and a review under the owner account are distinct
actors, but actual pending-deployment eligibility must be verified before
claiming success. This is not a claim that every bot can be an environment
required reviewer; GitHub's supported reviewer types and identity checks apply.
Do not fabricate a second human, mislabel an App as human, or claim that a
review executed under the initiator's account is independent.

Do not disable **Prevent self-review** to work around a single-maintainer
repository. `verify_owner_approval.py` rejects that configuration.

1. Under **Deployment protection rules**, enable **Required reviewers**.
2. Select the owner-approved eligible reviewer identities or teams supported by GitHub.
3. Enable **Prevent self-review** and save.
4. Ensure an eligible reviewer other than the deployment initiator is available.
   GitHub normally requires one approval from this list, not approval by every
   listed reviewer. Additional quorum policy requires its own real control.

### Step 3: disable administrator bypass and restrict deployment branches

1. Clear **Allow administrators to bypass configured protection rules**; save.
2. Under **Deployment branches and tags**, select the approved protected-branch
   or selected-branch policy.
3. For a selected policy, allow only the reviewed execution route, normally
   `main`, plus `0D_base_` only if protected staging execution is authorized.
   Do not add `*` or `copilot/**` to expose secrets to unreviewed code.
   `docker-build-push.yml` also uses `owner-approval` (currently
   `disabled_manually`). If it is re-enabled, its `main` push jobs will wait for
   the same reviewers, and its `pull_request` runs will not match a `main`-only
   branch policy.
4. Save and read back the actual policy and rules.

CLI alternative for reviewer/branch configuration, **only after settings-write authorization**:
assign `REVIEWER_LOGIN` to the approved eligible User identity. This example is for
the inspected unprotected environment; if protection already exists, use a
reviewed payload that preserves all existing required controls instead.
Disabling administrator bypass remains a required **UI step**: the documented
[environment update API](https://docs.github.com/en/rest/deployments/environments#create-or-update-an-environment)
does not list a `can_admins_bypass` input. Do not assume an undocumented JSON
field changes that control; save it in the UI and verify the resulting state.

```bash
: "${REVIEWER_LOGIN:?Approved eligible reviewer identity required}"
REVIEWER_ID="$(gh api "users/$REVIEWER_LOGIN" --jq '.id')"

jq -n --argjson reviewer "$REVIEWER_ID" \
  '{
    wait_timer: 0,
    prevent_self_review: true,
    reviewers: [{type: "User", id: $reviewer}],
    deployment_branch_policy: {
      protected_branches: false,
      custom_branch_policies: true
    }
  }' |
  gh api --method PUT "repos/$REPO/environments/owner-approval" --input -

gh api "repos/$REPO/environments/owner-approval/deployment-branch-policies" \
  --jq '.branch_policies[] | {name, type}'
```

After inspecting the listing, add **only missing, authorized** rules:

```bash
gh api --method POST \
  "repos/$REPO/environments/owner-approval/deployment-branch-policies" \
  -f name=main -f type=branch
# Run separately only if protected staging deployment is authorized:
gh api --method POST \
  "repos/$REPO/environments/owner-approval/deployment-branch-policies" \
  -f name=0D_base_ -f type=branch
```

Do not recreate existing rules. For a protected-branches policy, verify the
actual branch protections rather than using the custom-policy listing.

### Step 4: verify protection before provisioning the marker

```bash
gh api "repos/$REPO/environments/owner-approval" \
  --jq '{protection_rules, can_admins_bypass, deployment_branch_policy}'
```

Require a nonempty `required_reviewers` rule with `prevent_self_review: true`,
`can_admins_bypass: false` and the approved restricted deployment policy.
An HTTP 403 is a denied read, not proof of valid protection. Do not provision
the marker until an authorized operator verifies these settings.

### Step 5: provision the environment-only marker

1. On the **owner-approval** page, under **Environment secrets**, select
   **Add environment secret**.
2. Name it `OWNER_APPROVAL_PROTECTED`, enter the exact lowercase value `true`,
   and save. If the existing value is uncertain, deliberately update it;
   GitHub cannot display stored values.
3. Do not create a repository or organization substitute. The marker is not
   an approval identity and is not useful without genuine environment review.

CLI alternative, **only after environment-secret-write authorization**:

```bash
gh secret set OWNER_APPROVAL_PROTECTED --repo "$REPO" --env owner-approval
```

Enter `true` at the protected interactive prompt. No token/private key belongs
in this command, PR text, a workflow literal or a worktree approval file.

### Step 6: verify scope and resolve conflicting markers

```bash
gh secret list --repo "$REPO" --env owner-approval
gh secret list --repo "$REPO"
```

The marker name must appear in the environment inventory. Have an organization
administrator inspect any inherited organization marker with the same name.
If conflicting scope exists, obtain explicit permission before removing it;
preserve unrelated secrets and dependent consumers. Inventories prove name/scope,
not value. The hosted runtime check must still prove the released marker.

The current agent received HTTP 403 for environment secret inventory and
public-key reads. The repository/organization administrator owns that boundary;
do not relocate the marker or broaden the agent's permissions to hide it.

## 3. Credential owner: repair only the denied routes

The usable local read credential identifies as `mbaetiong`, the author of
#5766. Its repository metadata reports administration, but environment/repository
secret inventories and Actions-permission reads return HTTP 403. Those denials,
not the metadata flag, determine this session's capability boundary. This
identity also cannot provide the independent approval required for its own PR
or self-initiated deployment.

1. Verify expired/revoked CODEX credentials and their current approved consumers.
   Both locally available PAT routes returned HTTP 401; environment presence
   alone is not health evidence. Do not assume these local values equal the
   current hosted secrets, or overwrite healthy hosted secrets on that basis.
2. Restore affected secrets through the normal authorized secrets UI/CLI.
   Grant only operation-specific permissions. Workflow-run approval requires
   eligible Actions access plus the helper's independent identity/review checks.
3. Verify App key format, installation, repository selection and approved
   permissions privately. Do not log keys/tokens or treat an App installation
   token as a human reviewer. The repaired helper accepts a verified active App
   as an agent maintainer, including its genuine current-head review, while
   rejecting unverified bots, stale evidence, self-review and expired tokens.
4. Repository reads do not prove approval, logs, settings or secret-write access.
   Recheck the particular denied operation after repair.

Use `gh auth status`, `gh api user --jq '{login, type}'` and the specific
read endpoint through the operator's approved account. Do not print environment
variables, token values or credential files. Do not overwrite unrelated secrets
or widen permissions merely to make a diagnostic command pass.

App health is not merely left unexamined: the latest successful main-branch
approval run `43358448688`, attempt 1, was inspected through job
`131666334289` and its logs. Its App-capable original job was skipped; the
executed route selected a PAT and reported **zero pending runs / zero approvals**.
Its label/Actions inventory reads succeeded at execution, establishing hosted
read access at that time, not the health of the local PAT values. This green
run proves neither App health nor an approval-capable independent PAT identity.
Current private App material cannot be verified from secret values because
GitHub never returns them; the secret metadata reads are also denied here.
The App owner must supply a redacted, operation-specific verification bound to
the current installation and credential rotation, not repeat a historical
non-PEM diagnosis as current fact.

## 4. Actions owner and implementer: recover the actual ML failure

Use an approved private diagnostic location; a directory name or `chmod` alone
does not establish custody. These reads do not rerun the old SHA:

```bash
: "${PRIVATE_DIAGNOSTICS:?Existing approved private diagnostic directory required}"
test -d "$PRIVATE_DIAGNOSTICS"
umask 077
gh api "repos/$REPO/actions/runs/43358318768/attempts/1/jobs?per_page=100" \
  --jq '.jobs[] | select(.id == 131670399212) | {id, head_sha, status, conclusion, steps}'
gh run view 43358318768 --repo "$REPO" --attempt 1 \
  --job 131670399212 --log \
  > "$PRIVATE_DIAGNOSTICS/ml-43358318768-attempt-1-job-131670399212.log"
```

The requested job finalized as cancelled. Its job-log URL returned a signed
storage response with `BlobNotFound`; the run-level archive became available
but contained only component-job logs, not the slow job. Its check annotations
and artifact inventory were empty. This is unavailable evidence, not a current
authentication failure. An Actions administrator must recover that specific
traceback if retained elsewhere.

The earlier completed slow job `131011045588` (run `43165845712`, attempt 1,
SHA `3cee1ffea0`) supplied **59 failures, 1,657 passes, 27 skips, 4 XPASS**.
Its coverage step failed collection on four missing dependencies subsequently
added in staging. The integration failures include archived-document paths,
stale APIs, missing imports, early-stopping expectations, checkpoint validation,
OODA persistence and a network-dependent dependency-checker subprocess.
These are independent source-grounded repair evidence; they do not establish
the exact failure list for run `43358318768`.

From the actual traceback, identify failing node IDs, reproduce with the
supported dependency environment, implement focused repairs and add regressions.
The affected command is:

```bash
python -m pytest tests/integration/ -v -m integration --timeout=600
```

Prefer the evidenced failing node IDs first. Do not replace failures with skips,
lower thresholds or treat local Torch stubs/mocked tests as hosted ML proof.
The workflow now uploads integration JUnit before coverage, caps integration
and coverage steps below the job's total budget and retains the unchanged 70%
coverage threshold. Staging sub-PRs now trigger ML checks as well as promotion
PRs, so the repair can be tested before default-branch integration. Per-test timeouts require fresh
hosted validation; a timed-out step remains failure, never a success fallback.

The dependency checker now bounds online queries (default 45 seconds, plus the
last in-flight package's existing timeout). Set
`CODEX_PY312_DEPS_BUDGET_SECONDS=0` for offline metadata inspection. Exhausted
budget returns **exit 2 / INCONCLUSIVE**, never READY, and partial results are
not cached. Invalid, negative and non-finite budget values are rejected.

## 5. Reviewer and maintainer: review the published scoped repair

Draft [#5783](https://github.com/Aries-Serpent/_codex_/pull/5783) is already
published against `0D_base_`. Do not recreate the PR or repeat the completed
implementation commit. Review its current diff and fresh hosted results.
The first delegation preflight failed because the last commit did not update
the accountability report; its automatic push returned 403. The follow-up
records actual lanes/evidence in the report and changelog, without weakening
that gate or changing its credential route.

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check origin/0D_base_...HEAD
git --no-pager diff --stat origin/0D_base_...HEAD
git --no-pager diff origin/0D_base_...HEAD -- .github/workflows/auto-approve-workflows.yml \
  .github/workflows/agent-auth-delegation.yml scripts/ci/approve_pending_runs.py \
  scripts/ci/require_wec_auto_approve.py scripts/ci/verify_owner_approval.py
```

Use the existing Python validation interpreter. Run changed-module Black/Ruff/
isort/mypy, compile checks, focused approval/ML tests, pinned actionlint, scoped
secret/permission review and `git diff --check`. Record exact commands/results;
local tests do not establish hosted readiness.

The [PR template](../../../.github/pull_request_template.md) governs the body;
preserve its structure and applicable maintainer WEC selections. A signed commit
or push is not independent review or green CI. Any signer failure belongs to the
signing owner; do not disable signing. Only authorized mergers integrate the
reviewed sub-PR and promotion through existing protections. A merge does not
configure environments or supply secrets.

## 6. Independent reviewer: prove deployment and workflow approval separately

After the reviewed repair is on the trusted default branch, and only with
workflow-execution authorization:

```bash
DEFAULT_BRANCH="$(gh repo view "$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')"
PUBLISHED_SHA="$(gh api "repos/$REPO/commits/$DEFAULT_BRANCH" --jq '.sha')"
gh workflow run agent-auth-delegation.yml --repo "$REPO" \
  --ref "$DEFAULT_BRANCH" -f pr_number=5766
gh run list --repo "$REPO" --workflow agent-auth-delegation.yml \
  --commit "$PUBLISHED_SHA" --limit 10 \
  --json databaseId,attempt,event,headSha,status,conclusion,url
```

Select the actual matching run/attempt; do not assume the newest unrelated run.
Confirm **Activate token delegation** waits for `owner-approval` before its first
step executes. In the run UI, the designated independent reviewer uses
**Review deployments**, selects this environment and reviews the exact run.
Do not use self-review or administrator bypass.

CLI alternative for an **eligible, independently authorized deployment reviewer**:

```bash
: "${RUN_ID:?Verified matching delegation run required}"
: "${ATTEMPT:?Verified run attempt required}"
gh run view "$RUN_ID" --repo "$REPO" --attempt "$ATTEMPT" \
  --json databaseId,attempt,event,headSha,status,conclusion,jobs,url
gh api "repos/$REPO/actions/runs/$RUN_ID/pending_deployments"
```

Verify the exact run/SHA/environment, configured reviewers and
`current_user_can_approve`. Assign `ENVIRONMENT_ID` from the verified pending
`owner-approval` record, not another environment. The eligible reviewer may then,
with explicit approval authority, perform the genuine platform review:

```bash
: "${ENVIRONMENT_ID:?Verified pending owner-approval environment ID required}"
gh api --method POST "repos/$REPO/actions/runs/$RUN_ID/pending_deployments" \
  -F "environment_ids[]=$ENVIRONMENT_ID" -f state=approved \
  -f comment="Independent review of the verified owner-approval run"
```

An empty pending list is not approval. Inspect protection and job conditions.
Confirm **Verify protected owner approval** and delegation finish successfully.
If its environment read is denied, the administrator must supply a legitimate
read-capable execution arrangement; do not weaken the verification.

Separately exercise an eligible held **workflow run** with WEC opt-in and
independent current-head PR review. After explicit workflow-execution authority:

```bash
: "${TARGET_PR:?Verified eligible reviewed PR required}"
: "${TARGET_RUN_ID:?Verified held run bound to that PR head required}"
gh workflow run auto-approve-workflows.yml --repo "$REPO" --ref "$DEFAULT_BRANCH" \
  -f approval_source=manual -f approval_intent=auto_approve_action_required \
  -f target_pr="$TARGET_PR" -f target_run_id="$TARGET_RUN_ID" -f dry_run=false
```

The dispatcher/approver must satisfy self-approval restrictions. No label or
dispatch input substitutes for independent review. Retain the approval decision
artifact, exact run/SHA/attempt, identity and final job conclusion. Confirm
missing marker/review, self-approval, stale SHA, expired/revoked grant and API
rejection remain denied.

## 7. Exact-SHA acceptance and hotfix handoff

For each selected approval, delegation and fresh ML run:

```bash
: "${TARGET_SHA:?Exact published source SHA required}"
gh run list --repo "$REPO" --commit "$TARGET_SHA" --limit 10 \
  --json databaseId,attempt,event,headSha,status,conclusion,url
gh api --paginate \
  "repos/$REPO/actions/runs/$RUN_ID/attempts/$ATTEMPT/jobs?per_page=100"
gh api --paginate "repos/$REPO/commits/$TARGET_SHA/check-runs?per_page=100"
```

Bind jobs/check links to the selected run and attempt; SHA alone is insufficient.
Queued/running/skipped/cancelled/unavailable is not success. Rerunning an old SHA
does not validate new code. Use the actual published workflow triggers and
authorized execution route for fresh ML validation.

After any authorized promotion, repeat default-branch acceptance and retain
this handoff until both approval paths and fresh hosted ML are proven:

> Continue the scoped #5766 repair from freshly verified default/staging SHAs.
> Preserve dirty work and all platform protections. Verify protected independent
> deployment review and environment-scoped marker, then exact-SHA workflow-run
> approval. Recover the original ML traceback, repair its evidenced failures and
> confirm fresh hosted ML. Do not infer completion from labels, local tests,
> mergeability or scores. Publish/rerun/approve/change settings/merge only within
> actual operation authority. Report denied endpoints and missing evidence to
> the responsible repository, Actions, credential or organization administrator.

No further merge or deployment is authorized by this guide. The diagnostic
readiness score is separate from hosted approval/ML acceptance.
