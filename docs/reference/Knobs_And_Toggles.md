# [Reference]: Knobs & Toggles Taxonomy (P2 Normalization)

> Generated: 2025-11-06 18:47:08 | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1) Overview

This reference now reflects P2 normalization via `scripts/config/parse_knobs.py`. All scripts read knobs through the normalizer to ensure consistent defaults and warnings.

## 2) Normalization Schema

| Knob | Type | Default | Allowed / Bounds |
|------|------|---------|------------------|
| CONTENT_FILTER_MODE | enum | allowlist | allowlist, pii, combined |
| ALLOWLIST_PROFILE | enum | A | A,B,C and combos (A+B, A+C, B+C, A+B+C) |
| ALLOWLIST_EXT | csv | "" | extensions (with or without dot) |
| PII_PATTERN_SET | enum | minimal | minimal, extended, custom |
| PII_CUSTOM_LIST | csv | "" | regex list |
| PII_MODE | enum | union-minimal | replace, union-minimal, union-extended |
| PII_REGEX_STRATEGY | enum | skip-manifest | abort, skip-warn, skip-manifest |
| AUDIT_DEPTH_DEFAULT | int | 3 | 1..4 |
| AUDIT_DEPTH | int/None | None | 1..4 (falls back to default if None) |
| MAX_BUNDLE_MB | float | 25.0 | 0.1..4096.0 |
| ARCHIVE_FORMAT | enum | tar.gz | tar.gz, zip |
| AUTO_ARCHIVE_DISABLE | bool | False | 0/1 truthy |
| ARCHIVE_POINTER_STYLE | enum | both | embedded, sidecar, both |
| BUNDLE_PREFIX_MODE | bool | False | 0/1 truthy |

Warnings returned by the parser are included in reports or manifests as appropriate.

## 3) Integration Points

| Component | File | Behavior |
|-----------|------|----------|
| Filter | scripts/content_filter/apply_filter.py | Reads all filter knobs via normalizer; writes `content_filter_report.json` |
| Archive | scripts/archive/select_and_compress.py | Uses normalized ARCHIVE_FORMAT, MAX_BUNDLE_MB, pointer style |
| Runner (depth) | scripts/space_traversal/audit_runner.py | Uses AUDIT_DEPTH(_DEFAULT); writes `_depth_warnings.json` |

## 4) Example Usage

```bash
# Combined filter with extended PII and custom allowlist additions
CONTENT_FILTER_MODE=combined PII_PATTERN_SET=extended PII_MODE=union-extended \
ALLOWLIST_PROFILE=A+B ALLOWLIST_EXT="txt,ini" \
python scripts/content_filter/apply_filter.py

# Archive with sidecar-only style, zip format
ARCHIVE_POINTER_STYLE=sidecar ARCHIVE_FORMAT=zip MAX_BUNDLE_MB=10 \
python scripts/archive/select_and_compress.py --root audit_artifacts/raw
```

## 5) Fallback & Warning Codes

| Code | Meaning |
|------|---------|
| ambiguous_boolean:<raw> | Boolean could not be parsed; default used |
| invalid_enum:<raw> | Enum not in allowed set; default used |
| invalid_int/float:* | Bounds or parse errors; default used |
| suspicious_long_entries | CSV item length suspicious; accepted with caution |

*End of P2 Normalization Reference*
