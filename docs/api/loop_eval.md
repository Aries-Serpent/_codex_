# API: Evaluation Loop & CLI
> Generated: Previous Cycle-11-11 07:38:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Doc Author], [Secondary: Verifier] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Model → Dataloader → Loss → Metrics → Logger] Fields🔄 [CPU-safe, Deterministic] Patterns👁️ [Lazy imports, batch+epoch logging] Redundancy🔀 [Unit+Integration tests] Balance⚖️ [Minimal default, extensible hooks]

## Purpose
Provide a minimal, deterministic evaluation loop with pluggable metrics and logging sinks for reference CPU workflows.

## Public Function
`evaluate_epoch(model, dataloader, criterion, device="cpu", metrics=None, logger=None, max_batches=None, seed=None) -> Dict[str, Any]`

| Field | Description |
|-------|-------------|
| model | torch.nn.Module (evaluated in `eval()` mode) |
| dataloader | Iterable yielding (inputs, targets) pairs |
| criterion | Callable returning loss tensor |
| device | "cpu" or "cuda" (loop remains CPU-safe) |
| metrics | Mapping name -> callable(preds, targets) returning float |
| logger | Iterable of logger objects with `.log(record)` & `.close()` |
| max_batches | Optional int batch cap for quick runs |
| seed | Optional reproducibility parameter (dataloader generator responsibility) |

## Returned Summary
```json
{
  "loss": <float>,
  "count": <int>,
  "metrics": {"acc": 0.85},
  "batches": <int>,
  "duration_sec": <float>
}
```text

## Logging
- Per batch (optional) + epoch summary NDJSON at `runs/eval/<timestamp>/metrics.ndjson`.
- Optional MLflow offline sink behind flag.
- Optional system metrics (RSS, CPU%) behind `--sys-metrics`.

## CLI
`codex-eval run --config config.json --json`
`codex-eval report --input metrics.ndjson --compare other.ndjson --json`

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 2 | Invalid arguments/config |
| 3 | Runtime error/no epoch records |
| 4 | Determinism mismatch (report comparison) |

## Determinism
Use `seed` and seeded DataLoader generators; compare JSON summaries for equality (report command).

## Tests
- Unit coverage: empty, single, multi batch; metrics; invalid batch shape.
- Integration coverage: CLI run & report.

Coverage Target: ≥95%.

— End —