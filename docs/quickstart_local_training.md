# Quickstart: Local CPU Training → Evaluation → Checkpoint → Report
> Generated: 2025-11-11 07:38:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Doc Author], [Secondary: Verifier] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Tokenize → Data → Model → Train → Eval → Ckpt → Report] Fields🔄 [CPU-only, Offline] Patterns👁️ [Determinism, NDJSON] Redundancy🔀 [Golden outputs] Balance⚖️ [Minimal steps, reproducible]

Prereqs
- Python 3.12+, nox installed
- Offline-first environment; no external network during runtime

1) Setup
```bash
nox -s tests
nox -s docs_build
```

2) Minimal experiment config
- Use configs/experiments/minimal.json (or .toml). Validate:
```bash
nox -s validate-configs
```

3) Train (reference loop)
```bash
python -m codex_ml.training.loop --config configs/experiments/minimal.json
```

4) Evaluate (new eval loop + CLI)
```bash
codex-eval run --config configs/experiments/minimal.json --json > artifacts/eval_report.json
```

5) Checkpoints (best‑k retention)
- Check {run_dir}/checkpoints and index.json to see retained files.

6) Logs & Reporting
- NDJSON logs at runs/{train|eval}/%Y%m%d_%H%M%S/metrics.ndjson
- Convert to summary:
```bash
codex-eval report --json --input runs/eval/.../metrics.ndjson > artifacts/eval_summary.json
```

7) Security Gate
```bash
nox -s security
```

8) Determinism Proof
- Re-run step 4 with same seed and compare artifacts/eval_report.json hashes.

— End —