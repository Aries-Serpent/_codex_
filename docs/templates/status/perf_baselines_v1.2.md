# Guide: Performance Baselines (v1.2)
> Generated: Previous Cycle-11-02 15:29:01 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Performance Lead], [Secondary: Reviewer] ⚡ Energy: 5

Baseline Fields
- training.throughput_steps_per_sec
- training.epoch_time_seconds
- inference.latency_p50_ms, latency_p95_ms
- memory.peak_ram_gb, memory.peak_vram_gb

Workflow
- Parse logs: python tools/perf_snapshot.py --log run.log --out perf_snapshot.json
- Merge into status: python tools/report_merge.py --report reports/daily/YYYY-MM-DD.json --in perf_snapshot.json:automation.performance
