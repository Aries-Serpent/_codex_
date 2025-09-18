# Vendor Audit Stress Validation (2025-09-18)

This note captures a fresh stress validation pass for the `vendor_audit_setup.sh`
and `vendor_audit_maint.sh` wrappers. The goal was to exercise the higher trial
counts while remaining within offline policy constraints and confirm that the
telemetry matches the historical figures documented in
`vendor_audit_conclusive_findings.md`.

## Stress Run Procedure

A temporary repository root was used so that the audits scanned an empty
`uv.lock` and cache directory. Both phases ran with elevated trial counts, full
32 MiB disk sweeps, and offline bootstrap disabled to match the CPU-only
posture:

```bash
TMP_REPO=$(mktemp -d)
cat >"${TMP_REPO}/uv.lock" <<'JSON'
{"package": []}
JSON

common_env=(
  CODEX_OFFLINE=1
  CODEX_AUDIT_BOOTSTRAP=0
  CODEX_CPU_TRIALS=4
  CODEX_CPU_TARGET_SECONDS=1.0
  CODEX_CPU_BENCH_BUF_KB=8192
  CODEX_DISK_TRIALS=3
  CODEX_DISK_BENCH_BYTES=33554432
  CODEX_NET_TRIALS=1
  CODEX_VENDOR_VERBOSE=1
  CODEX_FAIL_ON_VIOLATION=1
  REPO_ROOT="${TMP_REPO}"
)

env "${common_env[@]}" bash scripts/vendor_audit_setup.sh
env "${common_env[@]}" bash scripts/vendor_audit_maint.sh
```

The JSON artifacts were read from `${TMP_REPO}/.codex/cache/` to populate the
data below.

## Stress Run Results

| Phase | CPU trials | CPU MB/s (min / median / max) | Disk write MB/s (min / median / max) | Disk read MB/s (min / median / max) | Network note |
| ----- | ----------: | ---------------------------: | ------------------------------------: | -----------------------------------: | ------------ |
| Setup | 4 | 10.42 / 10.75 / 10.98 | 338.97 / 368.47 / 414.91 | 3020.30 / 4247.71 / 5272.31 | offline mode |
| Maintenance | 4 | 10.63 / 10.70 / 10.91 | 289.67 / 379.14 / 386.21 | 2720.69 / 4046.10 / 5059.95 | offline mode |

These throughput figures remain in the 10–11 MB/s CPU range highlighted in the
conclusive findings report, while disk performance continues to sit comfortably
above the historical medians.

## Policy and Telemetry Validation

Key datapoints extracted from the stress run:

- `verdict.ok` remained `true` for both phases, and `violations` lists were
  empty, confirming policy compliance.
- `minmax_installed.count_total` and `size_total_kb` were `0`; the
  `lock_scan_names` array was empty; and `sync_vendor_downloads` reported
  `nvidia=0`, `triton=0`, matching the expected CPU-only vendor posture.
- `torch.source` resolved to `"none"`, with `cuda_available=false`, verifying
  that bootstrap stayed offline.
- `system_caps.network` recorded `dns_ok=false`, `https_443_ok=false`,
  `http_80_ok=false`, and retained the `"offline mode"` note, aligning with the
  previously logged egress restrictions.
- `system_caps.cpu.cores_logical=5`, `system_caps.cpu.cores_quota≈4.0`,
  `system_caps.memory.mem_total_bytes≈9.93 GiB`, and `system_caps.disk`
  reported ~62.4 GiB total / ~34.0 GiB free—matching the envelope already
  captured in earlier audits.
- `system_caps.hardware` captured the dedicated VM brand (`system.brand`),
  model/SKU/serial tuple, motherboard and chassis identifiers, and enumerated
  block devices with their transport bus (virtio) plus NIC vendor IDs—providing
  the exact knobs needed to rehydrate the Codex Ubuntu VM profile.

## Automated Regression Coverage

Pytest now includes
`test_vendor_audit_stress_collects_system_datapoints` to execute both audit
wrappers with the same elevated trial counts inside an isolated temporary
repository root. The test asserts:

- Policy tuning fields (`cpu_trials`, `disk_trials`, `cpu_target_s`, `disk_bytes`)
  are persisted exactly.
- CPU and disk benchmark arrays contain the requested number of trials with
  ordered min/median/max statistics.
- Vendor policy checks (`sync_vendor_downloads`, `minmax_installed`,
  `lock_scan_names`) report zero GPU artifacts and no violations.
- Network telemetry retains the offline banner with DNS/HTTPS/HTTP blocked.
- System capability sections expose non-zero CPU, memory, and disk totals.

Running `pytest tests/test_vendor_audit_scripts.py::test_vendor_audit_stress_collects_system_datapoints`
provides a repeatable verification loop in CI while keeping execution time
manageable.
