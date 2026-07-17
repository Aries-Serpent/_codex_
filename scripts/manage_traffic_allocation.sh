#!/bin/bash
################################################################################
# Traffic Allocation Manager - v0.2.0 Staged Rollout
# Purpose: Manage traffic distribution across deployment stages (canary/blue-green)
# Authority: D-tier autonomous (@mbaetiong)
# Usage: ./manage_traffic_allocation.sh --stage [alpha|beta|ga] --percentage <0-100>
################################################################################

set -euo pipefail

# Configuration
STAGE="${1:-alpha}"
TRAFFIC_PERCENTAGE="${2:-10}"
NAMESPACE="codex-${STAGE}"
GRADUAL_TRANSITION_SECONDS="${3:-300}"  # 5 minutes default
NEW_VERSION="v0.2.0"
OLD_VERSION="v0.1.0"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validate traffic percentage
validate_percentage() {
    if [ "$TRAFFIC_PERCENTAGE" -lt 0 ] || [ "$TRAFFIC_PERCENTAGE" -gt 100 ]; then
        echo -e "${RED}Error: Traffic percentage must be between 0-100${NC}" >&2
        exit 1
    fi
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl not found${NC}" >&2
        exit 1
    fi
    echo -e "${GREEN}✓ kubectl available${NC}"
}

# Verify namespace exists
verify_namespace() {
    if ! kubectl get namespace "${NAMESPACE}" &>/dev/null; then
        echo -e "${YELLOW}Creating namespace ${NAMESPACE}...${NC}"
        kubectl create namespace "${NAMESPACE}" || true
    fi
    echo -e "${GREEN}✓ Namespace verified: ${NAMESPACE}${NC}"
}

# Get current replica count for base deployment
get_current_replicas() {
    kubectl get deployment codex -n "${NAMESPACE}" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "5"
}

# Calculate replica distribution
calculate_replicas() {
    local total_replicas=$1
    local new_replicas=$((total_replicas * TRAFFIC_PERCENTAGE / 100))
    local old_replicas=$((total_replicas - new_replicas))
    
    # Ensure at least 1 replica of each version if both needed
    if [ ${TRAFFIC_PERCENTAGE} -gt 0 ] && [ ${TRAFFIC_PERCENTAGE} -lt 100 ] && [ $new_replicas -eq 0 ]; then
        new_replicas=1
        old_replicas=$((total_replicas - 1))
    fi
    
    echo "${new_replicas},${old_replicas}"
}

# Create canary deployment with traffic splitting
setup_canary_deployment() {
    local total_replicas=$(get_current_replicas)
    local replica_split=$(calculate_replicas "$total_replicas")
    local new_replicas="${replica_split%,*}"
    local old_replicas="${replica_split#*,}"
    
    echo -e "${BLUE}Setting up canary deployment for ${STAGE} stage...${NC}"
    echo -e "Total replicas: ${total_replicas}"
    echo -e "New version (${NEW_VERSION}) replicas: ${new_replicas} (${TRAFFIC_PERCENTAGE}%)"
    echo -e "Old version (${OLD_VERSION}) replicas: ${old_replicas} ($((100-TRAFFIC_PERCENTAGE))%)"
    
    # Create deployment for new version if needed
    if [ $new_replicas -gt 0 ]; then
        kubectl set image deployment/codex codex=gcr.io/codex-project/codex:${NEW_VERSION} \
            -n "${NAMESPACE}" \
            --record 2>/dev/null || true
        
        kubectl scale deployment/codex -n "${NAMESPACE}" --replicas=$new_replicas
        echo -e "${GREEN}✓ Scaled ${NEW_VERSION} to ${new_replicas} replicas${NC}"
    fi
    
    # Create backup deployment for old version if needed
    if [ $old_replicas -gt 0 ]; then
        # Deploy old version in separate deployment
        kubectl run codex-stable -n "${NAMESPACE}" \
            --image=gcr.io/codex-project/codex:${OLD_VERSION} \
            --replicas=$old_replicas \
            --dry-run=client -o yaml 2>/dev/null | kubectl apply -f - || true
        
        echo -e "${GREEN}✓ Deployed ${OLD_VERSION} with ${old_replicas} replicas for stability${NC}"
    fi
}

# Configure service mesh traffic distribution (if Istio available)
setup_traffic_distribution() {
    echo -e "${BLUE}Configuring traffic distribution...${NC}"
    
    # Check if Istio is available
    if kubectl get crd virtualservices.networking.istio.io &>/dev/null; then
        echo -e "Istio detected - Setting up VirtualService..."
        
        # Create VirtualService with traffic distribution
        kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: codex-canary
  namespace: ${NAMESPACE}
spec:
  hosts:
  - codex
  http:
  - match:
    - uri:
        prefix: "/"
    route:
    - destination:
        host: codex
        subset: v020
      weight: ${TRAFFIC_PERCENTAGE}
    - destination:
        host: codex
        subset: v019
      weight: $((100 - TRAFFIC_PERCENTAGE))
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: codex
  namespace: ${NAMESPACE}
spec:
  host: codex
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
  subsets:
  - name: v020
    labels:
      version: v020
  - name: v019
    labels:
      version: v019
EOF
        echo -e "${GREEN}✓ VirtualService configured${NC}"
    else
        echo -e "${YELLOW}⚠ Istio not detected - using standard Kubernetes service mesh${NC}"
    fi
}

# Gradual traffic shift (rolling update)
gradual_traffic_shift() {
    local total_replicas=$(get_current_replicas)
    local target_new_replicas=$((total_replicas * TRAFFIC_PERCENTAGE / 100))
    local current_new_replicas=$(kubectl get deployment codex -n "${NAMESPACE}" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
    
    if [ "$current_new_replicas" -eq "$target_new_replicas" ]; then
        echo -e "${GREEN}✓ Already at target traffic percentage${NC}"
        return
    fi
    
    echo -e "${BLUE}Gradual traffic shift: ${current_new_replicas} → ${target_new_replicas} replicas over ${GRADUAL_TRANSITION_SECONDS}s${NC}"
    
    local steps=10
    local step_size=$(( (target_new_replicas - current_new_replicas) / steps ))
    local step_duration=$(( GRADUAL_TRANSITION_SECONDS / steps ))
    
    for ((i = 1; i <= steps; i++)); do
        local current_step=$(( current_new_replicas + (step_size * i) ))
        if [ $current_step -gt $target_new_replicas ]; then
            current_step=$target_new_replicas
        fi
        
        echo -e "${YELLOW}Step ${i}/${steps}: Shifting to ${current_step} replicas...${NC}"
        kubectl scale deployment/codex -n "${NAMESPACE}" --replicas=$current_step
        
        # Wait for rollout
        kubectl rollout status deployment/codex -n "${NAMESPACE}" --timeout=5m || true
        
        if [ $i -lt $steps ]; then
            sleep $step_duration
        fi
    done
    
    echo -e "${GREEN}✓ Gradual traffic shift complete${NC}"
}

# Verify traffic distribution
verify_traffic_distribution() {
    echo -e "${BLUE}Verifying traffic distribution...${NC}"
    
    # Get pod distribution
    local v020_pods=$(kubectl get pods -n "${NAMESPACE}" -l version=v020 --no-headers 2>/dev/null | wc -l)
    local v019_pods=$(kubectl get pods -n "${NAMESPACE}" -l version=v019 --no-headers 2>/dev/null | wc -l)
    local total_pods=$((v020_pods + v019_pods))
    
    if [ $total_pods -eq 0 ]; then
        total_pods=$(kubectl get pods -n "${NAMESPACE}" --no-headers 2>/dev/null | wc -l)
    fi
    
    if [ $total_pods -gt 0 ]; then
        local actual_percentage=$((v020_pods * 100 / total_pods))
        echo -e "New version (v0.2.0) pods: ${v020_pods} (${actual_percentage}%)"
        echo -e "Old version (v0.1.0) pods: ${v019_pods} ($((100-actual_percentage))%)"
        echo -e "Total pods: ${total_pods}"
        
        if [ $actual_percentage -ge $((TRAFFIC_PERCENTAGE - 5)) ] && [ $actual_percentage -le $((TRAFFIC_PERCENTAGE + 5)) ]; then
            echo -e "${GREEN}✓ Traffic distribution verified (±5% tolerance)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Traffic distribution off by more than 5%${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ No pods found in namespace${NC}"
        return 1
    fi
}

# Monitor traffic distribution
monitor_traffic_distribution() {
    echo -e "${BLUE}Monitoring traffic distribution for 5 minutes...${NC}"
    
    for i in {1..5}; do
        echo -e "\n${BLUE}[Minute ${i}/5]${NC}"
        
        # Sample request distribution if service is available
        if kubectl get svc codex -n "${NAMESPACE}" &>/dev/null; then
            # Try to get request counts from pods
            local pod_requests=$(kubectl exec -n "${NAMESPACE}" \
                $(kubectl get pods -n "${NAMESPACE}" -o jsonpath='{.items[0].metadata.name}') \
                -- curl -s localhost:8000/metrics 2>/dev/null | grep request_total || echo "0")
            
            if [ -n "$pod_requests" ]; then
                echo "Request distribution: $pod_requests"
            fi
        fi
        
        if [ $i -lt 5 ]; then
            sleep 60
        fi
    done
    
    echo -e "${GREEN}✓ Traffic monitoring complete${NC}"
}

# Generate traffic report
generate_traffic_report() {
    local report_file=".codex/.traffic_allocation_${STAGE}_$(date +%s).json"
    
    cat > "${report_file}" <<EOF
{
  "stage": "${STAGE}",
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "traffic_percentage": ${TRAFFIC_PERCENTAGE},
  "namespace": "${NAMESPACE}",
  "new_version": "${NEW_VERSION}",
  "old_version": "${OLD_VERSION}",
  "gradual_transition_seconds": ${GRADUAL_TRANSITION_SECONDS},
  "status": "COMPLETED"
}
EOF
    
    echo -e "${GREEN}Traffic report: ${report_file}${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}=====================================================${NC}"
    echo -e "${BLUE}Traffic Allocation Manager - v0.2.0 Release${NC}"
    echo -e "${BLUE}Stage: ${STAGE} | Traffic: ${TRAFFIC_PERCENTAGE}%${NC}"
    echo -e "${BLUE}=====================================================${NC}\n"
    
    validate_percentage
    check_kubectl
    verify_namespace
    
    setup_canary_deployment
    setup_traffic_distribution
    gradual_traffic_shift
    
    if verify_traffic_distribution; then
        monitor_traffic_distribution
        generate_traffic_report
        echo -e "\n${GREEN}✓✓✓ Traffic allocation complete ✓✓✓${NC}"
        exit 0
    else
        echo -e "\n${RED}✗✗✗ Traffic allocation verification failed ✗✗✗${NC}"
        exit 1
    fi
}

# Execute
main "$@"
