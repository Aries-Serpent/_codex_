# [Reference]: Detector Meta Registry (P4)

> Generated: 2024-11-06 19:02:11 UTC | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Purpose

Standardize detector `meta` fields for cross-capability analytics & future federation.

## 2. Canonical Meta Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| layer | string | Logical stack layer | serving, data, infra |
| interface | string | External interaction modality | http, cli, sdk |
| framework | string | Core framework tag (optional) | fastapi, flask |
| complexity | enum(low,medium,high) | Implementation complexity heuristic | medium |
| stability | enum(experimental,stable) | Maturity state | stable |
| tags | list[str] | Additional free-form labels | ["async","streaming"] |

## 3. Detector Contract Extension

```python
{
  "id": "...",
  "evidence_files": [...],
  "found_patterns": [...],
  "required_patterns": [...],
  "meta": {
     "layer":"serving",
     "interface":"http",
     "framework":"fastapi",
     "complexity":"medium",
     "stability":"experimental",
     "tags":["async"]
  }
}
```text

## 4. Scoring Influence (Planned)

| Meta Aspect | Planned Use |
|-------------|-------------|
| complexity | Weight adjustment multiplier (future) |
| stability | Filter for release gating |
| layer | Comparative maturity baseline per layer |
| tags | Faceted reporting & targeted improvements |

## 5. Validation Rules (Future)

| Rule | Enforcement |
|------|------------|
| complexity must be enum | schema_validate.py |
| stability must be enum | schema_validate.py |
| tags length <= 10 | schema_validate.py |

## 6. Migration Guidance

Existing detectors add meta incrementally; missing keys default to inference by pattern or remain absent.

*End of Detector Meta Registry*
