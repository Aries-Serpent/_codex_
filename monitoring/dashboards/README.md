# Grafana Dashboards

## Importing dashboards

1. Open Grafana.
2. Select **+** → **Import**.
3. Upload one of the JSON files from this directory.
4. Choose the Prometheus datasource and complete the import.

## Datasource requirement

- Configure a Prometheus datasource named `prometheus` or with UID `prometheus`.
- Dashboard queries assume the Codex metrics endpoint is scraped by Prometheus.

## Local run

- From the repository root, run `docker compose up grafana prometheus`.
- Prometheus uses `monitoring/prometheus.yml` and Grafana serves on port `3000`.

## Dashboard inventory

| File | Dashboard title | Focus |
| --- | --- | --- |
| `training_overview.json` | `Codex ML — Training Overview` | Training loss, throughput, epoch progress, duration |
| `security_overview.json` | `Codex ML — Security Overview` | Moderation decisions, rejection rate, active alerts |
| `system_health.json` | `Codex ML — System Health` | Health status, memory, CPU |
