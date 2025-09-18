# Knowledge Transfer — Vendor Audit Conclusive Findings

> Generated: 2025-09-17 22:59:34 | Author: mbaetiong

## Executive Summary
- Current status: Setup and Maintenance audits complete successfully and persist artifacts.
- Vendor policy: CPU-only posture is clean across runs — 0 filtered vendor packages (NVIDIA/triton family), 0 vendor downloads, no GPU refs in uv.lock; Torch unresolved (not imported/installed due to network posture).
- Egress posture: DNS OK, but HTTPS 443 and HTTP 80 socket establishment blocked; proxies present. Wrapper shows “unexpected connection error” banner that is non-fatal to the audits.
- Resource posture: cgroup CPU quota ≈ 4.0 vCPU (5 logical cores visible), cgroup memory limit = 8 GiB; storage ample (~62.44 GiB total, ~40.56 GiB free). Disk read throughput strong; disk write improves notably in maintenance phase; CPU synthetic bench stable around ~15 MB/s with current settings.
- Stability: Earlier defects (bash indirect expansion, missing psi_caps/os_info) are resolved. Scripts now include structured error artifact emission for faster root-cause diagnostics.

## Timeline of Recent Runs (progression and outcomes)

| Seq | Phase | Outcome | Primary Issue/Change | Evidence |
| --- | ----- | ------- | -------------------- | -------- |
| 1 | Setup | PASS (historical) | Wrapper “unexpected connection error” observed but non-fatal | DNS OK; TLS/HTTP blocked; audits produced artifacts |
| 2 | Setup | FAIL | Bash env helper error: invalid indirect expansion under set -u | “var: invalid indirect expansion” at ensure_default |
| 3 | Setup | FAIL | Python NameError: psi_caps not defined | Missing/late function definition |
| 4 | Setup | FAIL | Python NameError: os_info not defined | Missing/late function definition |
| 5 | Setup | PASS | v1.5.3/1.5.4: fixed ordering; expanded datapoints; structured error artifact added | Full JSON persisted |
| 6 | Maintenance | PASS | Matching v1.5.3/1.5.4 parity; stronger disk write | Full JSON persisted |

## Versioned Enhancements (v1.5.0 → v1.5.4)

| Version | Area | Change |
| ------- | ---- | ------ |
| v1.5.0 | Bench | Standardize CPU bench buffer via CODEX_CPU_BENCH_BUF_KB (default 8192 KB) |
| v1.5.0 | Recon | Add cgroup cpu.stat, io.stat; network sysctls; TLS CA paths; inode totals |
| v1.5.1 | Shell | Safer env sanitization under set -u; restructure here-doc → write-to-file pattern |
| v1.5.2 | Recon | Add cpuset.cpus.effective, memory.current, swap limits, pids.{max,current}, resolv.conf, default route, IO schedulers |
| v1.5.3 | Stability | Fix function ordering (psi_caps) and ensure completeness before use |
| v1.5.4 | Stability | Restore/move os_info; add structured error artifacts (.error.json) and top-level try/except |

## Latest Run Metrics (representative)

| Phase | CPU bench MB/s (min/med/max) | Disk write MB/s (min/med/max) | Disk read MB/s (min/med/max) | CPU cores (logical/quota) | Memory (total/limit) | Network |
| ----- | ---------------------------: | ---------------------------: | --------------------------: | ------------------------- | -------------------- | ------- |
| Setup | 14.54 / 14.94 / 14.98 | 240.56 / 241.91 / 243.26 | 3533.30 / 4128.03 / 4722.75 | 5 / ≈4.0 vCPU | 9.93 GB / 8.00 GB | DNS OK; HTTPS/HTTP blocked; proxies=True; single URL ≈155.89 Mbps |
| Maint | 12.75 / 15.01 / 15.18 | 491.72 / 542.11 / 592.49 | 4034.97 / 4632.21 / 5229.45 | 5 / ≈4.0 vCPU | 9.93 GB / 8.00 GB | DNS OK; HTTPS/HTTP blocked; proxies=True; single URL ≈151.52 Mbps |

Notes:
- CPU bench stabilized using 8 MiB buffer; ~15 MB/s is typical under current constraints and implementation.
- Disk write improves in maintenance (page cache/warm state/throttling dynamics). Disk read is consistently high.

## Conclusive Vendor Findings

| Aspect | Finding |
| ------ | ------- |
| Filtered vendor packages (nvidia-/triton family) | 0 (count_total=0, size_total_kb=0) |
| uv.lock GPU refs | none |
| Torch | version=(unknown); cpu_tag=False; cuda_available=False; source=none |
| Sync vendor downloads | nvidia=0; triton=0 |
| Verdict | OK (no policy violations) |

## Egress/Network Posture
- dns_ok=True; https_443_ok=False; http_80_ok=False; proxies=True.
- Wrapper banner “An unexpected connection error occurred” is environmental and non-fatal to audits.
- Throughput probes still gather partial speeds where content is retrievable.

## Min/Max Capability Envelope (across last 5–10 runs)

| Category | Observed Min | Observed Max | Notes |
| -------- | ------------ | ------------ | ----- |
| CPU logical cores | 5 | 5 | Constant visibility |
| CPU quota (vCPU) | ≈4.0 | ≈4.0 | cgroup cpu.max-derived |
| CPU bench median (MB/s) | ≈10–11 | ≈279 | Range includes earlier config differences; standardized to ~15 now |
| Memory cgroup limit | 8 GiB | 8 GiB | Hard ceiling |
| Disk write median (MB/s) | ≈196.85 | ≈1279.61 | Varies with cache/IO state |
| Disk read median (MB/s) | ≈3249.55 | ≈4632.21+ | Consistently strong |
| Network dns_ok | True | True | Stable |
| Network https/http ok | False | False | Policy/proxy blocked |
| Vendor filtered count | 0 | 0 | CPU-only compliance verified |

## Known Failure Classes, Root Causes, and Resolutions

| Class | Symptom | Root Cause | Resolution | Status |
| ----- | ------- | ---------- | ---------- | ------ |
| Wrapper egress error | “Unexpected connection error” | Egress policy blocks HTTPS/HTTP sockets | Treat as non-fatal; capture diagnostics; provide offline mode | Resolved/By design |
| set -u indirect expansion | var: invalid indirect expansion | Indirect var expansion in ensure_default | Use declare -p probe (is_defined) | Resolved |
| psi_caps missing | NameError: psi_caps | Definition omitted/ordered after use | Define parse_pressure/psi_caps before use | Resolved |
| os_info missing | NameError: os_info | Definition omitted/ordered after use | Add os_info before use | Resolved |
| Post-failure triage | Lossy logs | No structured error artifact | Add *.error.json with type/message/traceback | Implemented |

## Exhaustive Changeable Variables (CODEX_*) and Intended Use

| Variable | Default | Description |
| -------- | ------- | ----------- |
| CODEX_FORCE_CPU | 1 | Prefer CPU index for PyTorch bootstrap |
| CODEX_ALLOW_TRITON_CPU | 1 | Allow triton package when CPU-only |
| CODEX_AUDIT_BOOTSTRAP | 1 | Try torch import/install (no-op when offline) |
| CODEX_OFFLINE | 0 | Force offline audits; skip egress checks/bootstrap |
| CODEX_FAIL_ON_VIOLATION | 0 | Exit non-zero if 1 and vendor violations detected |
| CODEX_VENDOR_MAX_PACKAGES | 0 | Max filtered vendor pkgs allowed |
| CODEX_VENDOR_MAX_SIZE_KB | 0 | Max total size (KB) of filtered vendor pkgs |
| CODEX_VENDOR_LOG_AGG | pre-sync | Tagging for vendor sync situations |
| CODEX_VENDOR_VERBOSE | 0 | Verbosity control |
| CODEX_TORCH_VERSION_BASE | 2.8.0 | Torch version target for bootstrap |
| CODEX_VENDOR_SAMPLE_ENABLE | 0 | Enable sampling tests (disabled by default) |
| CODEX_VENDOR_SAMPLE_MAX | 6 | Sample limit if enabled |
| CODEX_VENDOR_SAMPLE_INDEX | https://pypi.org/simple | Index for sampling |
| CODEX_VENDOR_SAMPLE_KEEP | 0 | Keep sampled artifacts if 1 |
| CODEX_NET_TEST_URLS | hetzner/pypi/github trio | URLs for throughput trials |
| CODEX_NET_TRIALS | 3 | Trials per URL |
| CODEX_CPU_TRIALS | 3 | CPU bench trials |
| CODEX_CPU_TARGET_SECONDS | 1.0 | Target per CPU trial (seconds) |
| CODEX_CPU_BENCH_BUF_KB | 8192 | CPU bench buffer (KB) |
| CODEX_DISK_BENCH_BYTES | 33554432 | Per-trial disk IO bytes |
| CODEX_DISK_TRIALS | 2 | Disk trials (write/read) |
| CODEX_ERR_TRAP | 1 | Enable shell ERR trap |

## Artifacts and Schema (What to expect)
- Files
  - `.codex/cache/vendor_audit.setup.json`
  - `.codex/cache/vendor_audit.maintenance.json`
  - On failure: `.codex/cache/vendor_audit.setup.error.json` (or `maintenance.error.json`)
- Top-level schema (selected highlights)
  - `phase`: `setup`|`maintenance`
  - `policy`: `allow_triton_cpu`, `max_packages`, `max_size_kb`, `vendor_log_agg`, `bootstrap`, `sample_enable` (setup), `net_trials`, `cpu_trials`, `cpu_target_s`, `cpu_buf_kb`, `disk_bytes`, `disk_trials`, `net_urls`
  - `torch`: `version`, `cpu_tag`, `cuda_build`, `cuda_available`, `source`
  - `bootstrap_status`: `attempted`, `rc`, `note`, `used`
  - `vendors[]`: `{name, version, total_kb, roots[]}`
  - `minmax_installed`: `{count_total, size_total_kb, size_min_kb, size_max_kb}`
  - `lock_scan_names[]`
  - `sync_vendor_downloads`: `{nvidia_downloads, triton_downloads}`
  - `system_caps`:
    - `cpu`: `{cores_logical, cores_quota, cpuset_cpus, cpuset_effective, cpu_shares, min_mhz, max_mhz, model, vendor, flags_count, loadavg}`
    - `cpu_stat`: `{nr_periods, nr_throttled, throttled_usec, proc_stat_steal}`
    - `memory`: `{mem_total_bytes, mem_available_bytes, cgroup_mem_max_bytes, mem_current_bytes, swap_max_bytes, swap_current_bytes}`
    - `disk`: `{root_total_bytes, root_used_bytes, root_free_bytes, inode_total, inode_free, schedulers{}}`
    - `cgroup_io`: `{devices{…}, aggregate{rbytes,wbytes,rios,wios}}`
    - `pids`: `{pids_max, pids_current}`
    - `caches`: `{uv_cache_bytes, pip_cache_bytes, hf_cache_bytes, codex_cache_bytes, apt_cache_bytes, npm_cache_bytes, cargo_registry_bytes, cargo_git_bytes, gomod_cache_bytes, yarn_cache_bytes}`
    - `network`: `{dns_ok, https_443_ok, http_80_ok, outbound_ip, notes, proxies{}, urls{}, summary{}, ifaces[], sysctls{}, tls{}, resolv_conf{}, route_default}`
    - `tools`: `{python,node,npm,ruby,rust,go,swift,php}`
    - `os`: `{os_release{}, kernel, dockerenv, cgroup_1}`
    - `limits`: `{raw}`
  - `bench`:
    - `cpu_MBps`: `{trials, speeds_MBps[], min, median, max}`
    - `disk_MBps`: `{write_MBps[], read_MBps[], write_stats{}, read_stats{}}`
  - `verdict`: `{ok, violations[]}`

## Operations Runbook
- Typical run (online posture detection):
  - `bash scripts/audit_setup.sh`
  - `bash scripts/audit_maintenance.sh`
- Restricted CI (no egress):
  - `CODEX_OFFLINE=1 bash scripts/audit_setup.sh`
  - `CODEX_OFFLINE=1 bash scripts/audit_maintenance.sh`
- Review results:
  - `cat .codex/cache/vendor_audit.setup.json | jq`
  - `cat .codex/cache/vendor_audit.maintenance.json | jq`
- If failures occur:
  - Inspect `.codex/cache/vendor_audit.*.error.json` for `{type, message, traceback}` and policy snapshot.
- Stress validation:
  - Refer to `vendor_audit_stress_validation.md` for the 2025-09-18 offline stress run configuration and datapoints that
    corroborate these conclusive findings.

## Troubleshooting Decision Tree

| Symptom | Immediate Checks | Likely Root Cause | Action |
| ------- | ---------------- | ----------------- | ------ |
| “Unexpected connection error” banner | audit JSONs exist? dns_ok value? | Egress policy blocks sockets | Treat as non-fatal; use CODEX_OFFLINE=1 for faster runs |
| Python NameError (any function) | Was function defined before use? | Emission order/truncation | Ensure function defined above Execute probes; rerun |
| set -u expansion error | sanitize_env stage fails | Indirect expansion on unset var | Use declare -p probe (is_defined) |
| Vendor violation | minmax_installed shows >0 or >size | Env drift or new deps | Inspect vendors[] roots; set CODEX_FAIL_ON_VIOLATION=1 to gate pipeline |

