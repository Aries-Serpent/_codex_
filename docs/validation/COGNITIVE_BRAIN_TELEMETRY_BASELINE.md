# Cognitive Brain Telemetry Baseline

**Generated:** 2026-08-03T20:22:55Z

This baseline is produced by a static, file-only scan of the Cognitive Brain source tree and its test suite.  It estimates telemetry event volume, forensics completeness, session-guard interception, and shell-policy verdict distribution without requiring external infrastructure or test execution.

## Summary

| Metric | Value |
|---|---|
| Source files scanned | 15 |
| Test files scanned | 69 |
| ``telemetry.record`` calls (src + tests) | 7 |
| ``CognitiveTelemetry`` instantiations (src + tests) | 7 |
| ``TelemetryEvent`` constructions (src + tests) | 16 |
| Decision event volume estimate | 30 |
| Forensics completeness rate | 31.2% (5/16) |
| Session Guard interception rate | 6.2% (1/16) |
| Shell verdict references (source) | 8 |

## Decision Event Volume

Estimated volume is the sum of ``telemetry.record`` calls, ``CognitiveTelemetry`` instantiations, and ``TelemetryEvent`` constructions detected in each file.

| Source File | record calls | CognitiveTelemetry ctor | TelemetryEvent ctor | Volume |
|---|---|---|---|---|
| src/codex/cognitive_brain/kernel.py | 0 | 1 | 0 | 1 |
| src/codex/cognitive_brain/session_guard.py | 1 | 0 | 1 | 2 |
| src/codex/cognitive_brain/telemetry.py | 6 | 0 | 7 | 13 |

## Forensics Completeness

A ``TelemetryEvent`` is considered forensics-complete when ``decision_id``, ``turn_id``, and ``task_id`` are all explicitly populated at the construction site.

| Scope | Events with all fields | Total events | Completeness |
|---|---|---|---|
| Source | 2 | 8 | 25.0% |
| Tests | 3 | 8 | 37.5% |
| Combined | 5 | 16 | 31.2% |

## Session Guard Interception Rate

The interception rate is the share of ``TelemetryEvent`` constructions that are emitted through ``SessionGuard`` (``event_type='session_guard'``) versus all ``TelemetryEvent`` constructions detected in source and tests.

| Scope | session_guard events | Total TelemetryEvent constructions | Rate |
|---|---|---|---|
| Source | 1 | 8 | 12.5% |
| Tests | 0 | 8 | 0.0% |
| Combined | 1 | 16 | 6.2% |

## Shell Verdict Distribution

Verdict counts are static references to ``PolicyVerdict.DENY``, ``PolicyVerdict.ALLOW``, and ``PolicyVerdict.AUDIT`` in ``shell_policy.py``.

| Verdict | Count | Share |
|---|---|---|
| DENY | 4 | 50.0% |
| ALLOW | 2 | 25.0% |
| AUDIT | 2 | 25.0% |
| **Total** | **8** | **100.0%** |

## Methodology

1. **Walk** ``src/codex/cognitive_brain/**/*.py`` and ``tests/cognitive_brain/**/*.py``.
2. **Parse** each file with the Python ``ast`` module; skip files that fail to parse.
3. **Count** ``telemetry.record(...)`` call sites, ``CognitiveTelemetry(...)`` instantiations, and ``TelemetryEvent(...)`` constructions.
4. **Inspect** each ``TelemetryEvent(...)`` keyword argument list.  Count events where ``decision_id``, ``turn_id``, and ``task_id`` are all explicitly provided.
5. **Detect** ``session_guard`` interception by looking for ``telemetry.record(TelemetryEvent(event_type='session_guard', ...))``.
6. **Analyze** ``src/codex/cognitive_brain/shell_policy.py`` for references to ``PolicyVerdict.DENY``, ``PolicyVerdict.ALLOW``, and ``PolicyVerdict.AUDIT``.
7. **Emit** this markdown report with the generated UTC timestamp.
