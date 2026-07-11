# Google Cloud Run Deployment Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08  
**Version**: 1.0  
**Audience**: DevOps engineers, GCP platform engineers, serverless architects  
**Environment**: Google Cloud Run (Serverless)  
**Tier**: Production-Ready

---

## Overview

Google Cloud Run is a fully managed serverless platform that scales automatically based on traffic. This guide covers deploying Codex ML on Cloud Run with production-grade reliability and cost efficiency.

### Architecture

```
┌────────────────────────────────────────────────────┐
│         Cloud Load Balancer                       │
│  - Global load balancing                          │
│  - DDoS protection                                │
└─────────┬──────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────┐
    │   Cloud Run Services                      │
    │   - Auto-scaling (0 to N)                │
    │   - Pay-per-request                      │
    │   ┌──────────────────────────────────┐   │
    │   │ Codex ML Container               │   │
    │   │ - CPU: 2                          │   │
    │   │ - Memory: 4Gi                     │   │
    │   │ - Timeout: 3600s                  │   │
    │   └──────────────────────────────────┘   │
    └─────┬──────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────┐
    │  Cloud SQL (PostgreSQL)                   │
    │  - Private IP via VPC                     │
    │  - Point-in-time recovery                │
    │  - Automated backups                      │
    └────────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────┐
    │  Cloud Memorystore (Redis)                │
    │  - High availability                      │
    │  - Automatic backup                       │
    └────────────────────────────────────────────┘
          │
    ┌─────▼────────────────────────────────────┐
    │  Cloud Storage                            │
    │  - Model artifacts                        │
    │  - Logs and monitoring data                │
    └────────────────────────────────────────────┘
```

---

## Prerequisites

### GCP Project Setup

```bash
# Create GCP project
gcloud projects create codex-ml-prod \
  --name="Codex ML Production"

# Set as active project
gcloud config set project codex-ml-prod

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  cloudresourcemanager.googleapis.com \
  storage.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudfunctions.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep run
```

### Service Account Configuration

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create codex-ml-runtime \
  --display-name="Codex ML Runtime Account"

# Grant Cloud Run permissions
gcloud projects add-iam-policy-binding codex-ml-prod \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Grant Cloud SQL permissions
gcloud projects add-iam-policy-binding codex-ml-prod \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/cloudsql.client

# Grant storage permissions
gcloud projects add-iam-policy-binding codex-ml-prod \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/storage.admin
```

---

## Step-by-Step Deployment

### 1. Create Container Image

```bash
# Build image using Cloud Build
gcloud builds submit \
  --region=us-central1 \
  --config=cloudbuild.yaml \
  --tag=gcr.io/codex-ml-prod/codex-ml:1.0.0

# Or build locally and push
docker build -f docker/Dockerfile.cpu -t codex-ml:1.0.0 .

# Configure Docker for GCR
gcloud auth configure-docker

# Tag and push
docker tag codex-ml:1.0.0 gcr.io/codex-ml-prod/codex-ml:1.0.0
docker push gcr.io/codex-ml-prod/codex-ml:1.0.0

# Verify image
gcloud container images list --project=codex-ml-prod
```

### 2. Create VPC Network

```bash
# Create VPC
gcloud compute networks create codex-ml-vpc \
  --subnet-mode=custom

# Create subnet
gcloud compute networks subnets create codex-ml-subnet \
  --network=codex-ml-vpc \
  --range=10.0.0.0/20 \
  --region=us-central1 \
  --secondary-range pods=10.4.0.0/14,services=10.0.16.0/20

# Create firewall rules
gcloud compute firewall-rules create codex-ml-allow-internal \
  --network=codex-ml-vpc \
  --allow=tcp,udp,icmp \
  --source-ranges=10.0.0.0/8

gcloud compute firewall-rules create codex-ml-allow-https \
  --network=codex-ml-vpc \
  --allow=tcp:443 \
  --source-ranges=0.0.0.0/0
```

### 3. Create Cloud SQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create codex-ml-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-8192 \
  --region=us-central1 \
  --network=projects/codex-ml-prod/global/networks/codex-ml-vpc \
  --no-assign-ip \
  --backup \
  --backup-start-time=03:00 \
  --retained-backups-count=30 \
  --transaction-log-retention-days=7 \
  --enable-bin-log=false \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --flags=cloudsql_iam_authentication=on

# Wait for instance to be ready
gcloud sql instances wait-until-ready codex-ml-db \
  --project=codex-ml-prod

# Create database
gcloud sql databases create codex \
  --instance=codex-ml-db

# Get instance connection name
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe codex-ml-db \
  --format='value(connectionName)')

echo "Instance connection name: $INSTANCE_CONNECTION_NAME"

# Create database user
gcloud sql users create codex-admin \
  --instance=codex-ml-db \
  --******

# Get user password from Cloud Secret Manager
gcloud secrets create codex-db-password \
  --replication-policy="user-managed" \
  --replication-locations="us-central1"
```

### 4. Create Cloud Memorystore Redis

```bash
# Create Redis instance
gcloud redis instances create codex-ml-cache \
  --size=2 \
  --region=us-central1 \
  --redis-version=7.0 \
  --auth-enabled \
  --backup-start-time=03:00 \
  --network=projects/codex-ml-prod/global/networks/codex-ml-vpc

# Wait for instance to be ready
gcloud redis instances wait-until-ready codex-ml-cache \
  --region=us-central1

# Get Redis host and port
REDIS_HOST=$(gcloud redis instances describe codex-ml-cache \
  --region=us-central1 \
  --format='value(host)')

REDIS_PORT=$(gcloud redis instances describe codex-ml-cache \
  --region=us-central1 \
  --format='value(port)')

# Get auth string
REDIS_AUTH=$(gcloud redis instances describe codex-ml-cache \
  --region=us-central1 \
  --format='value(auth_string)')
```

### 5. Create Cloud Storage Bucket

```bash
# Create bucket for models and data
gsutil mb -p codex-ml-prod \
  -c STANDARD \
  -l us-central1 \
  -b on \
  gs://codex-ml-artifacts

# Enable versioning
gsutil versioning set on gs://codex-ml-artifacts

# Configure lifecycle policy for cost optimization
gsutil lifecycle set - gs://codex-ml-artifacts <<'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF
```

### 6. Configure Secrets

```bash
# Store database password
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create codex-db-password \
  --data-file=-

# Store API key
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create codex-api-key \
  --data-file=-

# Store Redis password
echo -n "$REDIS_AUTH" | \
  gcloud secrets create codex-redis-auth \
  --data-file=-

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding codex-db-password \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding codex-api-key \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding codex-redis-auth \
  --member=serviceAccount:codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 7. Deploy to Cloud Run

```bash
# Create service.yaml for Cloud Run
cat > service.yaml <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: codex-ml
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
        autoscaling.knative.dev/minScale: "1"
        run.googleapis.com/vpc-access-connector: codex-ml-connector
        run.googleapis.com/cpu-throttling: "false"
    spec:
      serviceAccountName: codex-ml-runtime
      containers:
      - image: gcr.io/codex-ml-prod/codex-ml:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: INSTANCE_CONNECTION_NAME
          value: $INSTANCE_CONNECTION_NAME
        - name: DATABASE_USER
          value: codex-admin
        - name: DATABASE_NAME
          value: codex
        - name: REDIS_HOST
          value: $REDIS_HOST
        - name: REDIS_PORT
          value: "$REDIS_PORT"
        - name: ENVIRONMENT
          value: production
        - name: LOG_LEVEL
          value: INFO
        envFrom:
        - secretRef:
            name: codex-secrets
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 2
  traffic:
  - percent: 100
    latestRevision: true
EOF

# Deploy service
gcloud run services replace service.yaml \
  --region=us-central1

# Or deploy via gcloud CLI
gcloud run deploy codex-ml \
  --image=gcr.io/codex-ml-prod/codex-ml:1.0.0 \
  --region=us-central1 \
  --memory=4Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=100 \
  --min-instances=1 \
  --vpc-connector=codex-ml-connector \
  --vpc-egress=all-traffic \
  --service-account=codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com \
  --platform managed \
  --allow-unauthenticated

# Get service URL
SERVICE_URL=$(gcloud run services describe codex-ml \
  --region=us-central1 \
  --format='value(status.url)')

echo "Service deployed at: $SERVICE_URL"
```

### 8. Configure Cloud Load Balancer

```bash
# Create backend service
gcloud compute backend-services create codex-ml-backend \
  --global \
  --protocol=HTTPS \
  --health-checks=codex-ml-health \
  --load-balancing-scheme=EXTERNAL \
  --enable-cdn

# Create NEG (Network Endpoint Group) for Cloud Run
gcloud compute network-endpoint-groups create codex-ml-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --cloud-run-service=codex-ml

# Add NEG to backend service
gcloud compute backend-services add-backend codex-ml-backend \
  --global \
  --instance-group-region=us-central1 \
  --network-endpoint-group=codex-ml-neg \
  --network-endpoint-group-region=us-central1

# Create frontend configuration
gcloud compute url-maps create codex-ml-load-balancer \
  --default-service=codex-ml-backend

# Create HTTPS proxy
gcloud compute target-https-proxies create codex-ml-proxy \
  --url-map=codex-ml-load-balancer \
  --ssl-certificates=codex-ml-cert

# Create forwarding rule
gcloud compute forwarding-rules create codex-ml-rule \
  --global \
  --target-https-proxy=codex-ml-proxy \
  --address=codex-ml-ip \
  --ports=443
```

---

## Auto-Scaling Configuration

Cloud Run automatically scales based on incoming traffic, but you can configure limits:

```bash
# Update service with scaling limits
gcloud run services update codex-ml \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=100

# Configure concurrency
gcloud run services update codex-ml \
  --region=us-central1 \
  --concurrency=80  # Number of concurrent requests per container
```

---

## Monitoring & Logging

### Cloud Logging

```bash
# View service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=codex-ml" \
  --limit=50 \
  --format=json

# Create log sink for aggregation
gcloud logging sinks create codex-ml-logs \
  logging.googleapis.com/projects/codex-ml-prod/logs/codex-ml \
  --log-filter='resource.type=cloud_run_revision AND resource.labels.service_name=codex-ml'
```

### Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create codex-ml \
  --display-name="Codex ML Uptime" \
  --resource-type=uptime-url \
  --monitored-resource='{"displayName":"codex-ml","url":"'$SERVICE_URL'/health"}'

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=[CHANNEL_ID] \
  --display-name="Codex ML High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

## CI/CD Integration with Cloud Build

```bash
# Create cloudbuild.yaml
cat > cloudbuild.yaml <<'EOF'
steps:
  # Step 1: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'docker/Dockerfile.cpu', '-t', 'gcr.io/$PROJECT_ID/codex-ml:$SHORT_SHA', '.']

  # Step 2: Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/codex-ml:$SHORT_SHA']

  # Step 3: Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/run'
    args:
      - 'deploy'
      - 'codex-ml'
      - '--image=gcr.io/$PROJECT_ID/codex-ml:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--service-account=codex-ml-runtime@codex-ml-prod.iam.gserviceaccount.com'

images:
  - 'gcr.io/$PROJECT_ID/codex-ml:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/codex-ml:latest'
EOF

# Submit build
gcloud builds submit --config=cloudbuild.yaml
```

---

## Cost Optimization

### Reserved Capacity

```bash
# For predictable workloads, consider Compute Engine
# instead of Cloud Run for better cost efficiency
# Cloud Run: Pay-per-request
# Compute Engine: Reserved instances with sustained discounts
```

### Monitoring Costs

```bash
# Get billing information
gcloud compute project-info describe \
  --format='value(name)' \
  --project=codex-ml-prod

# Export costs to BigQuery for analysis
gcloud billing accounts list
gcloud billing accounts export \
  --account-id=ACCOUNT_ID \
  --billing-account=ACCOUNT_ID
```

---

## Troubleshooting

### Service Fails to Start

```bash
# Check recent revisions
gcloud run revisions list --service=codex-ml --region=us-central1

# Inspect failed revision
gcloud run revisions describe REVISION \
  --service=codex-ml \
  --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision AND labels.revision_name=REVISION" \
  --limit=50 \
  --format=json
```

### Database Connection Issues

```bash
# Verify VPC connector is ready
gcloud compute networks vpc-access connectors describe codex-ml-connector \
  --region=us-central1

# Test Cloud SQL connectivity
gcloud sql connect codex-ml-db \
  --user=codex-admin \
  --database=codex
```

---

## Production Readiness Checklist

- [ ] VPC network configured with private subnets
- [ ] Cloud SQL with high availability and backups
- [ ] Redis cache configured with automatic failover
- [ ] Cloud Run service with appropriate resource limits
- [ ] Cloud Load Balancer configured for global access
- [ ] SSL certificates installed and auto-renewal enabled
- [ ] Cloud Logging configured with retention
- [ ] Monitoring alerts configured
- [ ] Backup and recovery procedures tested
- [ ] Service account with minimal IAM permissions
- [ ] Secrets stored in Secret Manager
- [ ] CI/CD pipeline configured with Cloud Build
- [ ] Cost monitoring enabled
- [ ] Security scanning enabled on container images

---

**Next Steps**:
1. Configure DNS records to point to load balancer
2. Set up monitoring dashboard
3. Conduct load testing
4. Plan disaster recovery procedures
5. Schedule weekly backup verification

