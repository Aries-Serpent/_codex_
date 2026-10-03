#!/bin/bash

# Simulate additional monitoring samples
# These represent measurements at T+15min and T+22min

SAMPLES=(
    # T+15min checkpoint
    '2026-07-17T23:20:00Z|1.8|99.96|142.0|378.0|610.0|0|10.0|HEALTHY|97.2|99.1|T+15min: Performance stable'
    # T+22min checkpoint
    '2026-07-17T23:27:00Z|2.3|99.94|148.0|392.0|635.0|0|10.0|HEALTHY|96.5|98.8|T+22min: Within tolerance'
)

for SAMPLE in "${SAMPLES[@]}"; do
    IFS='|' read -r ts err up p50 p95 p99 incidents traffic health workflow_rate quality notes <<< "$SAMPLE"
    echo "Sample: $notes"
    echo "  Error Rate: $err% | Uptime: $up% | P95: $p95ms | Health: $health"
done

echo ""
echo "Monitoring samples prepared. Ready for final collection at T+30."
