#!/usr/bin/env bash
set -euo pipefail

# Kubernetes deployment script for Codex ML
# Usage: ./k8s_deploy.sh [environment]
# Environments: dev, staging, prod

NAMESPACE="${CODEX_K8S_NAMESPACE:-default}"
ENVIRONMENT="${1:-dev}"
IMAGE_TAG="${CODEX_IMAGE_TAG:-latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================="
echo "Deploying Codex ML to Kubernetes"
echo "=================================================="
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"
echo "=================================================="

# Validate environment
case "$ENVIRONMENT" in
  dev|development)
    OVERLAY="development"
    NAMESPACE="codex-dev"
    ;;
  staging)
    OVERLAY="production"
    NAMESPACE="codex-staging"
    ;;
  prod|production)
    OVERLAY="production"
    NAMESPACE="codex-prod"
    ;;
  *)
    echo "❌ Invalid environment: $ENVIRONMENT"
    echo "Usage: $0 [dev|staging|prod]"
    exit 1
    ;;
esac

echo "Using overlay: $OVERLAY"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v kubectl &> /dev/null; then
  echo "❌ kubectl not found. Please install kubectl."
  exit 1
fi

if ! command -v kustomize &> /dev/null; then
  echo "⚠️  kustomize not found. Using kubectl kustomize (may have limited features)"
fi

# Create namespace if it doesn't exist
echo "Creating namespace if needed..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Build and validate manifests
echo "Building Kustomize manifests..."
MANIFEST_DIR="$PROJECT_ROOT/manifests/k8s/overlays/$OVERLAY"

if [ ! -d "$MANIFEST_DIR" ]; then
  echo "❌ Manifest directory not found: $MANIFEST_DIR"
  exit 1
fi

# Apply manifests
echo "Applying manifests..."
kubectl apply -k "$MANIFEST_DIR" -n "$NAMESPACE"

# Wait for deployment
echo ""
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/codex-ml-server -n "$NAMESPACE" --timeout=5m

# Verify pods are running
echo ""
echo "Checking pod status..."
kubectl get pods -l app=codex-ml -n "$NAMESPACE"

# Verify health endpoints
echo ""
echo "Verifying health endpoints..."
POD=$(kubectl get pod -l app=codex-ml -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')

if [ -n "$POD" ]; then
  echo "Testing health endpoint..."
  kubectl exec "$POD" -n "$NAMESPACE" -- curl -sf http://localhost:8000/health || echo "⚠️  Health check failed"
  
  echo "Testing readiness endpoint..."
  kubectl exec "$POD" -n "$NAMESPACE" -- curl -sf http://localhost:8000/ready || echo "⚠️  Readiness check failed"
fi

# Display service information
echo ""
echo "Service information:"
kubectl get svc codex-ml-service -n "$NAMESPACE"

echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo "=================================================="
echo ""
echo "Useful commands:"
echo "  View logs:    kubectl logs -f -l app=codex-ml -n $NAMESPACE"
echo "  Get pods:     kubectl get pods -l app=codex-ml -n $NAMESPACE"
echo "  Port forward: kubectl port-forward svc/codex-ml-service 8000:8000 -n $NAMESPACE"
echo "  Describe:     kubectl describe deployment codex-ml-server -n $NAMESPACE"
echo "  Scale:        kubectl scale deployment codex-ml-server --replicas=N -n $NAMESPACE"
echo ""
