# IMDS Metrics Exporter

## Overview

The IMDS Metrics Exporter provides Prometheus-compatible metrics for monitoring IMDS health across your infrastructure.

## Metrics

### imds_accessible
- **Type:** Gauge
- **Values:** 0 (inaccessible), 1 (accessible)
- **Description:** Whether IMDS is currently accessible

### imds_response_time_seconds
- **Type:** Histogram
- **Buckets:** 0.1, 0.5, 1, 2, 5, 10
- **Description:** IMDS response time in seconds

### imds_check_total
- **Type:** Counter
- **Description:** Total number of IMDS checks performed

### imds_check_failures_total
- **Type:** Counter
- **Description:** Total number of failed IMDS checks

### imds_last_check_timestamp
- **Type:** Gauge
- **Description:** Unix timestamp of last check

## Configuration

```yaml
metrics:
  enabled: true
  export_format: "prometheus"
  export_path: "/var/lib/node_exporter/textfile_collector/imds.prom"
  collection_interval: 300
```

## Example Output

```
# HELP imds_accessible Whether IMDS is accessible
# TYPE imds_accessible gauge
imds_accessible{hostname="vm-01",location="eastus"} 1

# HELP imds_response_time_seconds IMDS response time
# TYPE imds_response_time_seconds histogram
imds_response_time_seconds_bucket{le="0.1"} 45
imds_response_time_seconds_bucket{le="0.5"} 98
imds_response_time_seconds_bucket{le="+Inf"} 100

# HELP imds_check_total Total IMDS checks
# TYPE imds_check_total counter
imds_check_total 100

# HELP imds_check_failures_total Failed IMDS checks
# TYPE imds_check_failures_total counter
imds_check_failures_total 2
```

## Grafana Dashboard

Import the included Grafana dashboard JSON for visualization.

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
