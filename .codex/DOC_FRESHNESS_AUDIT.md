# DOC_FRESHNESS_AUDIT

Date: 2026-07-07
Source: lane5-docfresh (doc-freshness-checker)

## Executive Summary

- Local link targets in sampled offline/onboarding docs are generally present.
- Freshness issues remain around prerequisite drift, malformed markdown fences, and quickstart routing ambiguity.

## Hotspots

| Severity | Finding |
|---|---|
| High | Conflicting Python version prerequisites across onboarding docs |
| High | Malformed markdown fence patterns in offline docs |
| High | Citation placeholder tokens (`oaicite`) in runbook content |
| Medium | Quickstart alias routes external users to agent-focused page |
| Medium | Hard-coded version strings likely to stale on release bumps |

## Corrective Actions

1. Normalize Python prerequisite statements across onboarding/offline docs.
2. Repair markdown fence integrity in offline docs.
3. Remove placeholder citation tokens.
4. Separate external-user quickstart path from agent-internal quickstart path.
5. Add docs lint checks for malformed fences and forbidden placeholder tokens.
