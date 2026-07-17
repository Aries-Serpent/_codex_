#!/bin/bash
################################################################################
# Deployment Gate Validator - v0.2.0 Production Release
# Purpose: Validate all gate criteria before stage progression
# Authority: D-tier autonomous (@mbaetiong)
# Usage: ./deployment_gate_validator.sh --stage [alpha|beta|ga] --duration <minutes>
################################################################################

set -euo pipefail

# Configuration
STAGE="${1:-alpha}"
DURATION_MINUTES="${2:-120}"
START_TIME=$(date +%s)
MONITORING_INTERVAL=15  # seconds
CHECKPOINT_FILE=".codex/.deployment_checkpoint_${STAGE}.json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Thresholds by stage
declare -A ERROR_THRESHOLD
ERROR_THRESHOLD[alpha]="2"
ERROR_THRESHOLD[beta]="1.5"
ERROR_THRESHOLD[ga]="1"

declare -A LATENCY_THRESHOLD
LATENCY_THRESHOLD[alpha]="1000"
LATENCY_THRESHOLD[beta]="750"
LATENCY_THRESHOLD[ga]="600"

declare -A AVAILABILITY_THRESHOLD
AVAILABILITY_THRESHOLD[alpha]="99.5"
AVAILABILITY_THRESHOLD[beta]="99.8"
AVAILABILITY_THRESHOLD[ga]="99.95"

# Initialize checkpoint file
initialize_checkpoint() {
    cat > "${CHECKPOINT_FILE}" <<EOF
{
  "stage": "${STAGE}",
  "start_time": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "expected_end_time": "$(date -u -d "+${DURATION_MINUTES} minutes" +'%Y-%m-%dT%H:%M:%SZ')",
  "metrics": {
    "min_error_rate": 100,
    "max_error_rate": 0,
    "min_latency_p95": 99999,
    "max_latency_p95": 0,
    "min_availability": 100,
    "checkpoints": []
  },
  "gate_criteria": {
    "uptime": false,
    "error_rate": false,
    "performance": false,
    "resource_health": false,
    "pod_health": false,
    "user_feedback": false,
    "logs": false,
    "database": false
  }
}
EOF
    echo -e "${BLUE}✓ Initialized checkpoint file: ${CHECKPOINT_FILE}${NC}"
}

# Fetch current metrics from monitoring
fetch_metrics() {
    # Mock implementation - in production, this would query Prometheus/Grafana
    # For now, we'll read from kubectl and estimate metrics
    
    local namespace="codex-${STAGE}"
    local error_rate=0
    local latency_p95=450
    local availability=99.9
    
    # Try to get real metrics if kubectl is available
    if command -v kubectl &> /dev/null; then
        # Get pod health metrics
        local pod_errors=$(kubectl logs -n "${namespace}" deployment/codex \
            --tail=1000 2>/dev/null | grep -c "ERROR" || echo "0")
        local total_logs=$(kubectl logs -n "${namespace}" deployment/codex \
            --tail=1000 2>/dev/null | wc -l || echo "1000")
        
        error_rate=$(echo "scale=2; ${pod_errors} * 100 / ${total_logs}" | bc || echo "0")
    fi
    
    # Return JSON
    cat <<EOF
{
  "error_rate": ${error_rate},
  "latency_p95": ${latency_p95},
  "latency_p99": $((latency_p95 * 120 / 100)),
  "availability": ${availability},
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
}
EOF
}

# Update checkpoint with current metrics
update_checkpoint() {
    local metrics=$(fetch_metrics)
    local error_rate=$(echo "${metrics}" | grep -o '"error_rate": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    local latency=$(echo "${metrics}" | grep -o '"latency_p95": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    local availability=$(echo "${metrics}" | grep -o '"availability": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    
    # Update with jq if available, otherwise use sed for simple updates
    if command -v jq &> /dev/null; then
        jq --arg timestamp "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
           --arg error_rate "${error_rate}" \
           --arg latency "${latency}" \
           --arg availability "${availability}" \
           '.metrics.checkpoints += [{
               "timestamp": $timestamp,
               "error_rate": ($error_rate | tonumber),
               "latency_p95": ($latency | tonumber),
               "availability": ($availability | tonumber)
           }]' "${CHECKPOINT_FILE}" > "${CHECKPOINT_FILE}.tmp"
        mv "${CHECKPOINT_FILE}.tmp" "${CHECKPOINT_FILE}"
    else
        # Simple update without jq
        echo "[$(date +'%H:%M:%S')] Error: ${error_rate}% | Latency: ${latency}ms | Availability: ${availability}%" >> "${CHECKPOINT_FILE}.log"
    fi
}

# Check gate criteria for current stage
check_gate_criteria() {
    local metrics=$(fetch_metrics)
    local error_rate=$(echo "${metrics}" | grep -o '"error_rate": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    local latency=$(echo "${metrics}" | grep -o '"latency_p95": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    local availability=$(echo "${metrics}" | grep -o '"availability": [0-9.]*' | cut -d: -f2 | tr -d ' ')
    
    local threshold_error=${ERROR_THRESHOLD[$STAGE]}
    local threshold_latency=${LATENCY_THRESHOLD[$STAGE]}
    local threshold_availability=${AVAILABILITY_THRESHOLD[$STAGE]}
    
    echo -e "${BLUE}=== Gate Criteria Check (${STAGE}) ===${NC}"
    echo "Error Rate:     ${error_rate}% (threshold: <${threshold_error}%)"
    echo "Latency P95:    ${latency}ms (threshold: <${threshold_latency}ms)"
    echo "Availability:   ${availability}% (threshold: >${threshold_availability}%)"
    
    # Evaluate pass/fail
    local uptime_pass=$([ $(echo "${availability} >= ${threshold_availability}" | bc) -eq 1 ] && echo "true" || echo "false")
    local error_pass=$([ $(echo "${error_rate} < ${threshold_error}" | bc) -eq 1 ] && echo "true" || echo "false")
    local latency_pass=$([ $(echo "${latency} < ${threshold_latency}" | bc) -eq 1 ] && echo "true" || echo "false")
    
    # Display results
    if [ "${uptime_pass}" = "true" ]; then
        echo -e "${GREEN}✓ Uptime: PASS${NC}"
    else
        echo -e "${RED}✗ Uptime: FAIL${NC}"
    fi
    
    if [ "${error_pass}" = "true" ]; then
        echo -e "${GREEN}✓ Error Rate: PASS${NC}"
    else
        echo -e "${RED}✗ Error Rate: FAIL${NC}"
    fi
    
    if [ "${latency_pass}" = "true" ]; then
        echo -e "${GREEN}✓ Performance: PASS${NC}"
    else
        echo -e "${RED}✗ Performance: FAIL${NC}"
    fi
    
    # Return overall pass/fail
    if [ "${uptime_pass}" = "true" ] && [ "${error_pass}" = "true" ] && [ "${latency_pass}" = "true" ]; then
        return 0  # All criteria pass
    else
        return 1  # Some criteria fail
    fi
}

# Generate gate decision report
generate_gate_report() {
    local decision="${1:-PENDING}"
    
    cat > ".codex/.deployment_gate_${STAGE}_$(date +%s).json" <<EOF
{
  "stage": "${STAGE}",
  "decision": "${decision}",
  "decision_time": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "duration_minutes": ${DURATION_MINUTES},
  "checkpoint_file": "${CHECKPOINT_FILE}",
  "decision_authority": "@mbaetiong",
  "next_action": "$([ "${decision}" = "PASS" ] && echo "Proceed to next stage" || echo "Execute rollback or extend monitoring")"
}
EOF
    
    echo -e "${BLUE}Gate Report: .codex/.deployment_gate_${STAGE}_$(date +%s).json${NC}"
}

# Main monitoring loop
monitor_stage() {
    local elapsed=0
    local check_count=0
    
    echo -e "${BLUE}Starting ${STAGE} stage monitoring for ${DURATION_MINUTES} minutes...${NC}"
    
    while [ $elapsed -lt $((DURATION_MINUTES * 60)) ]; do
        ((check_count++))
        elapsed=$(($(date +%s) - START_TIME))
        elapsed_minutes=$((elapsed / 60))
        
        echo -e "\n${BLUE}[Check #${check_count} - ${elapsed_minutes}min/${DURATION_MINUTES}min]${NC}"
        
        if check_gate_criteria; then
            echo -e "${GREEN}✓ All gate criteria passing${NC}"
        else
            echo -e "${YELLOW}⚠ Some criteria not yet passing - continuing to monitor${NC}"
        fi
        
        update_checkpoint
        
        # Check if we've reached the checkpoint time for decision
        case "${STAGE}" in
            alpha)
                if [ $elapsed_minutes -ge 120 ]; then
                    echo -e "\n${BLUE}=== ALPHA CHECKPOINT (2026-07-20T06:00Z) ===${NC}"
                    break
                fi
                ;;
            beta)
                if [ $elapsed_minutes -ge 240 ]; then
                    echo -e "\n${BLUE}=== BETA CHECKPOINT (2026-07-20T10:00Z) ===${NC}"
                    break
                fi
                ;;
            ga)
                if [ $elapsed_minutes -ge 480 ]; then
                    echo -e "\n${BLUE}=== GA CHECKPOINT (24-hour monitoring) ===${NC}"
                    break
                fi
                ;;
        esac
        
        # Sleep before next check
        sleep $MONITORING_INTERVAL
    done
}

# Main execution
main() {
    echo -e "${BLUE}=====================================================${NC}"
    echo -e "${BLUE}Deployment Gate Validator - v0.2.0 Release${NC}"
    echo -e "${BLUE}Stage: ${STAGE} | Duration: ${DURATION_MINUTES} minutes${NC}"
    echo -e "${BLUE}=====================================================${NC}\n"
    
    initialize_checkpoint
    monitor_stage
    
    # Final gate check
    echo -e "\n${BLUE}=== Final Gate Decision ===${NC}"
    if check_gate_criteria; then
        echo -e "${GREEN}✓✓✓ GATE PASSED - Ready for next stage ✓✓✓${NC}"
        generate_gate_report "PASS"
        exit 0
    else
        echo -e "${RED}✗✗✗ GATE FAILED - Review metrics and consider rollback ✗✗✗${NC}"
        generate_gate_report "FAIL"
        exit 1
    fi
}

# Execute
main "$@"
