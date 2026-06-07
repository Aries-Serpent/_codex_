# Gap 15 — Grafana dashboards

## Dashboard files created

- `monitoring/dashboards/training_overview.json`
- `monitoring/dashboards/security_overview.json`
- `monitoring/dashboards/system_health.json`
- `monitoring/dashboards/README.md`
- `monitoring/prometheus.yml`

## Panels and Prometheus queries

### Training Overview
- **Training Loss**: `(codex_ml_training_loss or codex_training_loss or codex_loss_current) or vector(0)`
- **Throughput**: `(codex_training_throughput_samples_per_sec or rate(codex_ml_training_steps_total[5m]) or rate(codex_training_steps_total[5m])) or vector(0)`
- **Epoch Progress**: `(codex_training_epoch or codex_ml_training_epoch or codex_ml_training_steps_total) or vector(0)`
- **Training Duration**: `(codex_training_duration_seconds or codex_ml_training_duration_seconds_sum) or vector(0)`

### Security Overview
- **Moderation Decisions**: `(sum by (verdict) (rate(moderation_decisions_total[5m])) or sum by (verdict) (rate(codex_moderation_decisions_total[5m]))) or vector(0)`
- **Moderation Rejection Rate**: `(rate(moderation_decisions_total{verdict="rejected"}[5m]) or rate(codex_moderation_decisions_total{verdict="rejected"}[5m])) or vector(0)`
- **Active Alerts**: `ALERTS{alertstate="firing"}`

### System Health
- **Health Check Status**: `(codex_health_check_status or up{job="codex"}) or vector(0)`
- **Memory Usage**: `process_resident_memory_bytes`
- **CPU Usage**: `rate(process_cpu_seconds_total[1m])`

## Load and verify

1. Start the stack with `docker compose up grafana prometheus`.
2. Import each JSON dashboard through Grafana UI (**+** → **Import** → **Upload JSON**).
3. Verify Prometheus target `codex` is up in Prometheus at `http://localhost:9090/targets`.
4. Open Grafana at `http://localhost:3000` and confirm panels render with the `prometheus` datasource.
