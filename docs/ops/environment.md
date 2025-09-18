<!-- BEGIN: CODEX_ENV_DOC -->

# Environment (Ubuntu)

- Use `scripts/gpu/check_gpu.sh` to summarize GPU driver/CUDA availability.
- Reproducibility: pin requirements and capture image digest when containerized.
- All validation runs are local (no online CI activation).

## Vendor VM Provisioning Controls

Dedicated vendor audits for Codex Ubuntu rely on environment variables to tune
policy, benchmarking, and offline posture so that a virtual machine can be
spawned with deterministic characteristics. All knobs are surfaced below for
rapid reference:

### Core audit tunables

| Variable | Purpose |
| -------- | ------- |
| `CODEX_FORCE_CPU` | Force CPU execution when bootstrapping torch |
| `CODEX_ALLOW_TRITON_CPU` | Permit triton packages in CPU-only environments |
| `CODEX_AUDIT_BOOTSTRAP` | Attempt torch installation/import |
| `CODEX_OFFLINE` | Disable egress checks/bootstrap |
| `CODEX_FAIL_ON_VIOLATION` | Exit non-zero on vendor violations |
| `CODEX_VENDOR_MAX_PACKAGES` | Cap filtered vendor packages |
| `CODEX_VENDOR_MAX_SIZE_KB` | Cap aggregate filtered size |
| `CODEX_VENDOR_LOG_AGG` | Tag vendor sync logs |
| `CODEX_VENDOR_VERBOSE` | Increase audit logging |
| `CODEX_TORCH_VERSION_BASE` | Torch version target for bootstrap |
| `CODEX_VENDOR_SAMPLE_ENABLE` | Enable package sampling (off by default) |
| `CODEX_VENDOR_SAMPLE_MAX` | Limit sampling cardinality |
| `CODEX_VENDOR_SAMPLE_INDEX` | Sampling index URL |
| `CODEX_VENDOR_SAMPLE_KEEP` | Retain sampled wheel artifacts |
| `CODEX_NET_TEST_URLS` | Throughput probe URLs |
| `CODEX_NET_TRIALS` | Network trials per URL |
| `CODEX_CPU_TRIALS` | CPU benchmark iterations |
| `CODEX_CPU_TARGET_SECONDS` | Target seconds per CPU trial |
| `CODEX_CPU_BENCH_BUF_KB` | CPU benchmark buffer size |
| `CODEX_DISK_BENCH_BYTES` | Disk IO bytes per trial |
| `CODEX_DISK_TRIALS` | Disk write/read iterations |
| `CODEX_ERR_TRAP` | Enable ERR trap during shell execution |

### Integration overrides (namespaced `CODEX_VENDOR_AUDIT_*`)

| Variable | Purpose |
| -------- | ------- |
| `CODEX_VENDOR_AUDIT_OFFLINE` | Override offline mode for integrations |
| `CODEX_VENDOR_AUDIT_BOOTSTRAP` | Force bootstrap enable/disable |
| `CODEX_VENDOR_AUDIT_NET_TRIALS` | Override network trial count |
| `CODEX_VENDOR_AUDIT_NET_URLS` | Override throughput URLs |
| `CODEX_VENDOR_AUDIT_CPU_TRIALS` | Override CPU trials |
| `CODEX_VENDOR_AUDIT_CPU_TARGET_SECONDS` | Override per-trial CPU duration |
| `CODEX_VENDOR_AUDIT_CPU_BUFFER_KB` | Override CPU buffer size |
| `CODEX_VENDOR_AUDIT_DISK_TRIALS` | Override disk trials |
| `CODEX_VENDOR_AUDIT_DISK_BYTES` | Override disk IO bytes |

These tables align with the conclusive vendor findings and stress validation
notes, ensuring every adjustable input is catalogued alongside the new hardware
inventory emitted under `system_caps.hardware` (brand, model, SKU, serial,
transport bus, etc.).
