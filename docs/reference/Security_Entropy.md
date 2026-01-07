# [Reference]: Secret Entropy Scan (P4/P5)

> Generated: 2024-11-06 19:02:11 UTC | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Purpose

Identify potential secret tokens missed by simple pattern lists using Shannon entropy heuristic.

## 2. Heuristic

| Element | Rule |
|---------|------|
| Window lengths | 16 → 48 (step 8) |
| Entropy threshold | Default 3.5 (configurable) |
| Allowlist prefixes | Skip windows with known benign prefixes |

## 3. Output

`secret_entropy_report.json`:

```json
{
  "threshold": 3.5,
  "count": 3,
  "findings": [{"file":"secrets.txt","span":"AKIAABCDEFGHIJKLMNOP","entropy":4.2}]
}
```text

## 4. Integration

Entropy findings can:
- Increase safeguards component (future weighting)
- Trigger manual review prior to commit
- Feed severity classifier (P5)

## 5. Severity (Planned)

| Entropy | Length | Severity |
|---------|--------|----------|
| >4.0 | 24–32 | High |
| 3.8–4.0 | 20–48 | Medium |
| 3.5–3.8 | 16–48 | Low |

## 6. False Positive Reduction

| Strategy | Effect |
|----------|--------|
| Prefix allowlist | Ignores known tokens (e.g., TEST_) |
| Charset analysis | Penalize overly uniform strings |
| Cross-entropy check | Compare against natural language baseline |

## 7. Roadmap

- Combine entropy with pattern hits (AWS, GCP keys)
- Provide redacted sidecar with classification
- Integrate into CI gating policy

*End of Security Entropy Reference*
