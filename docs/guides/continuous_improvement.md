# Continuous Improvement
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Last Updated: 2026-06-22

This project includes maintenance utilities for pruning logs and keeping the repository tidy. The `tools/codex_maintenance.py` script is meant to run on a regular schedule so that artefacts do not accumulate.

## Local scheduling with cron

Use `cron` to run the maintenance script at an interval of your choice. The example below runs it every iteration at midnight:

```cron
0 0 * * * /usr/bin/env python /path/to/repo/tools/codex_maintenance.py >> /path/to/repo/.codex/maintenance.log 2>&1
```
Replace `/path/to/repo` with the absolute path on your machine. The script's output is appended to a local log file so you can review past runs.

## Local scheduling with a runner script

If you prefer not to modify your system's `cron` table, create a lightweight runner that you invoke manually or from another scheduling tool:

```bash
#!/usr/bin/env bash
python /path/to/repo/tools/codex_maintenance.py
```
Invoke this runner from `launchd`, `systemd`, or any other local scheduler you control. All resources remain on your machine; **do not** enable or rely on GitHub Actions or other hosted services.

## Rationale

Keeping the maintenance workflow local avoids exposing repository data to external services and keeps automation simple. Run the job on a workstation or server you manage, and adjust the interval to match your cleanup requirements.

## Evidence-gated proposal assessment

`python -m codex.cognitive_brain.improvement_loop_runner --help` describes
the existing PDA-log runner and its optional `--evidence-bundle` mode.
By default this mode reads local JSONL exports, not live GitHub or Chronicle services,
and prints one assessment per valid input record. Each record contains:

- `repo` and immutable `sha`, matching the caller's `--repo` and `--sha`;
- `signal`, using the cognitive SDK's `SignalEvidence` fields, with
  timezone-aware `measured_at` and an explicit availability;
- `brief`, containing the evidence-to-improvement skill's hypothesis,
  metrics, scope, lane/dependencies, acceptance criteria, commands, budget,
  stop condition and falsification;
- `author` and optional `validation`, plus `correction_cycle` from zero to three.

Code proposals require a finite `signal.details.baseline_metric` matching the
brief baseline. Assessment time and freshness are controlled by the caller,
not the exported brief. Missing, stale or unavailable observations do not
reach pattern retrieval. Chronicle productivity observations must be marked
`category: session-productivity` in the brief and remain signal-only.

The existing `ImprovementPipeline` still enforces its authority envelope.
Without caller-supplied approval it returns a blocked proposal; approval
fields in exported records cannot grant authority. Validation must bind the
generated `proposal_id`, event proposal `patch_hash`, SHA and author.
Both the validation envelope and every command observation must carry the
assessment's `evidence_digest`, binding the exact signal, generated proposal,
file scope and context; every observation also carries the proposal/content IDs.
It must supply the declared verification commands and complete independent
negative, boundary and regression observations. Reassessment does not change
the proposal ID merely because observation time advances.

Complete supplied observations produce `ready-for-human-review`, **not**
authenticated approval or an executed/merged improvement. The runner never
executes commands, patches, agents, releases or confidence updates. Its output
always denies execution and integration authority. A non-ready or malformed
record or empty bundle produces a nonzero CLI exit; valid records remain available on stdout.
Sanitize exported source evidence before use; do not include credentials or
personal information. Actual isolated verification and measured post-merge
outcome tracking remain separate authorized stages.

### Optional live CI metadata collection

Add `--collect-ci-run RUN_ID` together with `--evidence-bundle` to read public
GitHub Actions metadata for one run and replace exported signals in the
input records. The positional JSONL file still supplies repository/SHA,
briefs and any previously recorded validation. All records share the same
collected snapshot. Caller-supplied write boundaries provide candidate files;
GitHub metadata never supplies patch content or write scope.

`codex.cognitive_brain.ci_signal_collection.collect_ci_run` also accepts an
injected authorized JSON reader for private repositories. The default reader
uses the existing optional `requests` dependency lazily, does not resolve
credentials, and does not inherit proxy/netrc settings. It performs only
fixed-origin HTTPS GETs with redirects disabled, no retries, ten-second
connect/read timeouts and a one-MiB response cap. A disposable process bounds
DNS, TLS, response headers and slow-stream body reads to twenty seconds or
the remaining sixty-second collection budget, whichever is smaller; timeout
cleanup permits two additional one-second joins. Caller-injected readers must
provide their own blocking-operation cancellation; the collector checks their
elapsed time but cannot interrupt arbitrary caller code.

Collection is bounded to five pages, 500 jobs and seven reads. It uses the
attempt-specific jobs endpoint and checks the run again after pagination.
Repository, immutable SHA, run ID, every job's attempt, timestamps, job IDs and complete
pagination must agree. Pending, gated, cancelled, denied, empty or entirely
skipped inventories are explicitly unavailable; malformed or changing
metadata is an error. Neither produces a synthetic zero-failure baseline.

A completed measurable attempt produces `failed_jobs_in_run_attempt`,
with its failure count, structured job IDs/outcomes and source references.
Successful attempts remain non-actionable metric samples. Skipped/neutral
jobs cannot refresh the age of an old executed-job measurement. Remote logs,
job/step names, actor details and error response text are not copied.

Collection success is not independent validation, C2 hosted enforcement
proof, approval or execution authority. The existing freshness, measured
baseline, scoped proposal and per-observation digest checks still apply.
Private access, Chronicle/package collectors, isolated verification and
post-merge outcomes remain separate integrations.

## Read-only transition evidence

`python -m scripts.ci.e_to_d_gate --help` describes assessment of an explicitly
supplied registry and optional `--manifest` path. It validates registry entries
against `configs/schemas/agent_spec.schema.json`, rejects empty populations
and duplicate IDs, and reuses the manifest generator's canonical SHA-256
verification. Inputs are never written, including when output aliases an input.

A matching local manifest hash is not hosted provenance. The active Tier-1
hosted-gate condition remains unknown without verified hosted evidence, so
local schema/hash success cannot authorize promotion. Registry/profile access,
promotion and hosted activation still require their applicable authority.
