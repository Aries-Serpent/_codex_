# Archive Improvements – Deployment Guide

## Overview

This guide covers the end-to-end rollout of the archive improvements package:
configuration system, structured logging, retry policies, batch restores, and
performance metrics. The process assumes a staged rollout (staging → canary →
production).

## Prerequisites

* Python environment consistent with the Codex project tooling (see
  `requirements-dev.txt`).
* Access to the archive database(s) – SQLite for local/staging, PostgreSQL or
  MariaDB for production deployments.
* Ability to set environment variables for the deployment target.

## 1. Prepare Configuration

1. Commit a baseline `.codex/archive.toml` (or environment-specific variant):

   ```toml
   [backend]
   backend = "postgres"
   url = "postgresql://codex:***@archive-prod/db"

   [logging]
   level = "info"
   format = "json"

   [retry]
   max_attempts = 4
   initial_delay = 1.0

   [batch]
   results_path = "/var/log/codex/archive/batch_results.json"

   [performance]
   enabled = true
   ```

2. Use environment variables to override secrets at deployment time:

   ```bash
   export CODEX_ARCHIVE_URL="postgresql://codex:${ARCHIVE_PASSWORD}@${DB_HOST}/db"
   export CODEX_ARCHIVE_LOG_LEVEL=warning
   ```

## 2. Validation Checklist

1. Install dependencies and run lint/tests:

   ```bash
   pip install -e .[dev]
   pre-commit run --all-files
   pytest tests/archive -q
   ```

2. Execute CLI smoke tests against the target environment:

   ```bash
   codex archive health-check
   codex archive config-show
   codex archive batch-restore manifest.json --actor ops --dry-run
   ```

3. Confirm evidence logging is operational (`.codex/evidence/archive_ops.jsonl`).

## 3. Deployment Steps

1. **Staging**
   * Apply configuration.
   * Run health check and a sample batch restore.
   * Verify structured logs in the staging logging system.

2. **Canary (5%)**
   * Enable for a limited set of workers.
   * Monitor error rates, retry counts, and evidence logs.

3. **Production Rollout**
   * Gradually scale to 100% after 30 minutes of stable canary metrics.
   * Update documentation and notify stakeholders.

## 4. Rollback Plan

1. Revert to the previous release tag.
2. Restore prior environment variables if they changed.
3. Purge or archive any batch result files generated during the failed rollout.
4. Communicate the rollback to the incident channel and record follow-up items.

## 5. Post-Deployment Verification

* Run `codex archive health-check --debug` to confirm connectivity.
* Inspect batch result summaries at the configured path.
* Review evidence logs for successful restores with metrics payloads.
* Confirm monitoring dashboards (error rate, retry attempts) remain within
  normal bounds.

## 6. Support

* Documentation: see the Usage Guide and ADR in `.github/docs/`.
* On-call escalation: archive platform channel.
* Raise issues via the Codex tracker with component `archive-improvements`.
