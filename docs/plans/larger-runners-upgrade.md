# Plan: Upgrade Copilot Coding Agent to Larger GitHub-Hosted Runners

**Ref:** [GitHub Docs — Upgrading to larger GitHub-hosted GitHub Actions runners](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment#upgrading-to-larger-github-hosted-github-actions-runners)
**Date:** 2026-03-05
**PR:** #3499
**Status:** DRAFT — awaiting owner approval before execution

---

## 1. Why Upgrade?

The Copilot coding agent environment (`copilot-setup-steps.yml`) currently uses
`runs-on: ubuntu-latest`, which resolves to a **standard 2-core / 7 GB RAM /
14 GB SSD** GitHub-hosted runner. This is sufficient for documentation-only
tasks but causes pain in three scenarios visible in this repository:

| Symptom | Root Cause |
|---------|-----------|
| Setup steps time out (30-min cap) on `ml-heavy` environment type | PyTorch CPU-only install + `pip install -e ".[dev,ml]"` on 2 cores routinely hits 25–30 min | 
| `venv` cache misses rebuild the full dep stack cold, blocking agent start | 2-core pip resolution is slow; concurrent setup steps contend for CPU | 
| Agent sessions that need `cargo build --release` for Rust components stall | Single-core equivalent throughput during compilation |

Larger runners provide more CPUs, more RAM, and more disk — all three bottlenecks above shrink proportionally.

---

## 2. Target Runner Sizes

GitHub offers the following Ubuntu x64 larger runners (compatible with Copilot
coding agent):

| Label | vCPU | RAM | SSD | Best for |
|-------|------|-----|-----|----------|
| `ubuntu-4-core` | 4 | 16 GB | 150 GB | Standard agent sessions (recommended default) |
| `ubuntu-8-core` | 8 | 32 GB | 300 GB | `ml-heavy` env type (PyTorch + ML extras) |
| `ubuntu-16-core` | 16 | 64 GB | 600 GB | Occasional full security scan / Rust release builds |

**Recommended approach:** single `runs-on` label using **`ubuntu-4-core`** by
default. The existing `environment_type` detection logic already gates
heavier install steps behind `if:` conditions, so a fixed 4-core runner
handles all environment types without needing dynamic runner selection.

---

## 3. Prerequisites (Org-Admin Steps — Not Code Changes)

These must be done by **@mbaetiong** (org owner) before any code change takes
effect:

1. **Enable larger runners for the `Aries-Serpent` organization:**
   - GitHub → *Aries-Serpent* org → **Settings → Actions → Runners → New runner → GitHub-hosted**
   - Create a runner group (e.g. `copilot-agents`) and add `ubuntu-4-core`.
   - Assign the runner group to the `_codex_` repository.
   - Reference: [Managing larger runners](https://docs.github.com/en/actions/using-github-hosted-runners/managing-larger-runners)

2. *(Optional — if Azure private networking is used)* Allow outbound HTTPS from
   the runner VNet to:
   - `uploads.github.com`
   - `user-images.githubusercontent.com`
   - `api.business.githubcopilot.com` (Copilot Business users)

> **Note:** Standard GitHub-hosted larger runners do NOT require Azure
> networking config. Skip step 2 unless the org uses private networking.

---

## 4. Code Changes Required

### 4a. `copilot-setup-steps.yml` — change `runs-on`

**File:** `.github/workflows/copilot-setup-steps.yml`
**Line 71** (current):
```yaml
    runs-on: ubuntu-latest
```
**Change to:**
```yaml
    runs-on: ubuntu-4-core
```

That is the **only required change** to adopt larger runners.

### 4b. *(Optional)* Increase `timeout-minutes`

**Current:** `timeout-minutes: 30` (line 72)

With a 4-core runner the `ml-heavy` install completes in ~12 min (vs ~25 min
today). The existing 30-min cap is adequate. However, if the team later wants to
run `ml-heavy` with GPU-enabled PyTorch or add `cargo build --release` to the
default path, raise this to `59` (the maximum allowed by GitHub Docs):

```yaml
    timeout-minutes: 59
```

### 4c. *(Optional)* Tighten cache keys for `runner.arch`

Today's cache keys use `runner.os` (`Linux`). Larger runners are still `x86_64`
Linux so existing cache entries are fully compatible. No cache-key changes are
required.

---

## 5. Rollback Plan

If the larger runner label is not yet provisioned in the org, the workflow will
queue indefinitely (it will not hard-fail immediately). To roll back:

```bash
# Revert runs-on to the standard runner
# Edit .github/workflows/copilot-setup-steps.yml line 71:
#   runs-on: ubuntu-latest
```

The change is a single-line diff, so rollback is trivial.

---

## 6. Implementation Checklist

```
[ ] 4-core runner group created in Aries-Serpent org (owner: @mbaetiong)
[ ] Runner group assigned to _codex_ repository (@mbaetiong)
[ ] copilot-setup-steps.yml: runs-on ubuntu-latest → ubuntu-4-core
[ ] Smoke test: trigger workflow_dispatch on copilot-setup-steps and verify
    it picks up the 4-core runner (check "Set up job" log: "Runner: ubuntu-4-core")
[ ] (Optional) timeout-minutes raised to 59 if ml-heavy sessions still timeout
[ ] CHANGELOG.md updated
[ ] AGENT_ACCOUNTABILITY_REPORT.md updated
```

---

## 7. Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Setup phase wall-clock (standard) | ~8 min | ~4 min |
| Setup phase wall-clock (ml-heavy) | ~25 min (near timeout) | ~10 min |
| Timeout risk for ml-heavy sessions | High | Low |
| Copilot agent start latency | ~10 min | ~5 min |

*Estimates based on GitHub's published throughput ratios for 2-core → 4-core.*

---

## 8. References

- [GitHub Docs: Upgrading to larger runners](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment#upgrading-to-larger-github-hosted-github-actions-runners)
- [GitHub Docs: About larger runners](https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners)
- [GitHub Docs: Managing larger runners](https://docs.github.com/en/actions/using-github-hosted-runners/managing-larger-runners)
- `docs/agent/COPILOT_TOKEN_GUIDE.md` — token/permission reference for the setup job
