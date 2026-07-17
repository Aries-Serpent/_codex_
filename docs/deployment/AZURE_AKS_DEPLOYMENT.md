# Azure Container Instances & AKS Deployment Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08
**Version**: 1.0
**Audience**: Azure platform engineers, DevOps specialists, enterprise architects
**Environment**: Azure AKS (Azure Kubernetes Service)
**Tier**: Production-Ready

---

## Overview

This guide covers deploying Codex ML on Azure using Azure Kubernetes Service (AKS) for production-grade reliability, scalability, and integration with Azure ecosystem services.

### Architecture

```
┌──────────────────────────────────────────────────┐
│          Azure Application Gateway                │
│  - Global load balancing                         │
│  - Web Application Firewall (WAF)                │
│  - SSL/TLS termination                           │
└──────────┬───────────────────────────────────────┘
           │
      ┌────▼──────────────────────────────────┐
      │  Azure Kubernetes Service (AKS)       │
      │  - 3 node pool (System, Standard, GPU)│
      │  - Horizontal Pod Autoscaling         │
      │  - Network policies enabled           │
      │  ┌───────────────────────────────┐    │
      │  │ Codex ML Pod Deployment       │    │
      │  │ - Replicas: 3                 │    │
      │  │ - CPU: 2, Memory: 4Gi         │    │
      │  │ - Health checks configured    │    │
      │  └───────────────────────────────┘    │
      └────┬──────────────────────────────────┘
           │
      ┌────▼──────────────────────────────────┐
      │  Azure Database for PostgreSQL        │
      │  - Private Endpoint                   │
      │  - Zone-redundant HA                  │
      │  - Geo-redundant backup               │
      └──────────────────────────────────────┘
           │
      ┌────▼──────────────────────────────────┐
      │  Azure Cache for Redis                │
      │  - Premium tier                       │
      │  - Zone-redundant HA                  │
      │  - Data persistence                   │
      └──────────────────────────────────────┘
           │
      ┌────▼──────────────────────────────────┐
      │  Azure Storage Account                │
      │  - Blob storage for artifacts         │
      │  - Geo-redundant storage (GRS)        │
      └──────────────────────────────────────┘
           │
      ┌────▼──────────────────────────────────┐
      │  Azure Monitor & Log Analytics        │
      │  - Container insights                 │
      │  - Application insights               │
      │  - Log aggregation                    │
      └──────────────────────────────────────┘
```

---

## Prerequisites

### Azure Subscription Setup

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# List available subscriptions
az account list --output table

# Set active subscription
az account set --subscription <subscription-id>

# Verify authentication
az account show
```

### Create Resource Group

```bash
# Define variables
RESOURCE_GROUP="codex-ml-prod"
LOCATION="eastus"
AKS_CLUSTER="codex-ml-aks"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Verify
az group show \
  --name $RESOURCE_GROUP
```

---

## Step-by-Step Deployment

### 1. Create Container Registry

```bash
# Create Azure Container Registry (ACR)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name codexmlcontainerregistry \
  --sku Premium \
  --admin-enabled true

# Get login credentials
az acr credential show \
  --resource-group $RESOURCE_GROUP \
  --name codexmlcontainerregistry \
  --query 'passwords[0].value' \
  --output tsv > /tmp/acr_password.txt

ACR_PASSWORD=$(cat /tmp/acr_password.txt)
ACR_USERNAME="codexmlcontainerregistry"
ACR_URL="codexmlcontainerregistry.azurecr.io"

# Login to ACR
docker login -u $ACR_USERNAME -p $ACR_PASSWORD $ACR_URL

# Build and push image
docker build -f docker/Dockerfile.cpu -t $ACR_URL/codex-ml:1.0.0 .
docker push $ACR_URL/codex-ml:1.0.0
```

### 2. Create Virtual Network

```bash
# Create VNet with subnets
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-vnet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name aks-subnet \
  --subnet-prefix 10.0.1.0/24

# Create additional subnets
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name codex-ml-vnet \
  --name database-subnet \
  --address-prefix 10.0.2.0/24

az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name codex-ml-vnet \
  --name cache-subnet \
  --address-prefix 10.0.3.0/24

# Get subnet ID for AKS
SUBNET_ID=$(az network vnet subnet show \
  --resource-group $RESOURCE_GROUP \
  --vnet-name codex-ml-vnet \
  --name aks-subnet \
  --query id -o tsv)
```

### 3. Create Network Security Groups

```bash
# Create NSG for AKS
az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-nsg

# Add inbound rules
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name codex-ml-nsg \
  --name allow-https \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-port-ranges '*' \
  --destination-port-ranges 443

az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name codex-ml-nsg \
  --name allow-application-gateway \
  --priority 101 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-port-ranges '*' \
  --destination-port-ranges 8000 \
  --source-address-prefixes 10.0.0.0/16
```

### 4. Create AKS Cluster

```bash
# Create AKS cluster with advanced settings
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --enable-managed-identity \
  --network-plugin azure \
  --vnet-subnet-id $SUBNET_ID \
  --kubernetes-version 1.27 \
  --enable-cluster-autoscaling \
  --min-count 2 \
  --max-count 10 \
  --zones 1 2 3 \
  --enable-pod-identity \
  --network-policy azure \
  --enable-managed-prometheus \
  --enable-azure-monitor-metrics \
  --enable-blob-driver \
  --enable-file-driver \
  --enable-disk-driver

# Get kubeconfig
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --admin

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### 5. Create Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-db \
  --location $LOCATION \
  --admin-user codex_admin \
  --admin-password "$(openssl rand -base64 32)" \
  --sku-name Standard_B2s \
  --storage-size 51200 \
  --backup-retention 30 \
  --geo-redundant-backup Enabled \
  --auto-grow Enabled \
  --publicly-accessible False \
  --ssl-enforcement Enabled \
  --minimal-tls-version TLS1_2

# Create database
az postgres db create \
  --resource-group $RESOURCE_GROUP \
  --server-name codex-ml-db \
  --name codex

# Create firewall rule for AKS
az postgres server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server-name codex-ml-db \
  --name AllowAKS \
  --start-ip-address 10.0.0.0 \
  --end-ip-address 10.0.255.255

# Get connection string
POSTGRES_HOST=$(az postgres server show \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-db \
  --query 'fullyQualifiedDomainName' \
  --output tsv)

echo "PostgreSQL host: $POSTGRES_HOST"
```

### 6. Create Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-cache \
  --location $LOCATION \
  --sku Premium \
  --vm-size p1 \
  --zones 1 2 \
  --minimum-tls-version 1.2 \
  --enable-non-ssl-port false

# Get connection string
REDIS_KEY=$(az redis list-keys \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-cache \
  --query 'primaryKey' \
  --output tsv)

REDIS_HOST=$(az redis show \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-cache \
  --query 'hostName' \
  --output tsv)

echo "Redis connection string: redis://:$REDIS_KEY@$REDIS_HOST:6380?ssl=True"
```

### 7. Create Azure Storage Account

```bash
# Create storage account
az storage account create \
  --resource-group $RESOURCE_GROUP \
  --name codexmlstorage \
  --location $LOCATION \
  --sku Standard_GRS \
  --kind StorageV2 \
  --https-only true \
  --min-tls-version TLS1_2

# Create blob container
az storage container create \
  --account-name codexmlstorage \
  --name artifacts

# Get storage account key
STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name codexmlstorage \
  --query '[0].value' \
  --output tsv)
```

### 8. Configure Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-kv \
  --location $LOCATION \
  --enable-rbac-authorization false

# Store secrets
az keyvault secret set \
  --vault-name codex-ml-kv \
  --name database-password \
  --value "$(openssl rand -base64 32)"

az keyvault secret set \
  --vault-name codex-ml-kv \
  --name redis-key \
  --value "$REDIS_KEY"

az keyvault secret set \
  --vault-name codex-ml-kv \
  --name storage-key \
  --value "$STORAGE_KEY"

# Get Key Vault ID
KV_ID=$(az keyvault show \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-kv \
  --query id \
  --output tsv)
```

### 9. Deploy Application to AKS

```bash
# Create namespace
kubectl create namespace codex-ml
kubectl config set-context --current --namespace=codex-ml

# Create secret for ACR
kubectl create secret docker-registry acr-secret \
  --docker-server=$ACR_URL \
  --docker-username=$ACR_USERNAME \
  --docker-******

# Create Kubernetes secret for database connection
kubectl create secret generic codex-db-secret \
  --from-literal=database-url="postgresql://codex_admin@$POSTGRES_HOST/codex" \
  --from-literal=database-******

# Create deployment manifest
cat > deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml
  labels:
    app: codex-ml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex-ml
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: codex-ml
    spec:
      serviceAccountName: codex-ml-sa
      imagePullSecrets:
      - name: acr-secret
      containers:
      - name: codex-ml
        image: CONTAINER_REGISTRY_URL/codex-ml:1.0.0
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: codex-db-secret
              key: database-url
        - name: REDIS_HOST
          value: "REDIS_HOST"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: codex-db-secret
              key: redis-password
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
---
apiVersion: v1
kind: Service
metadata:
  name: codex-ml-service
  labels:
    app: codex-ml
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: codex-ml
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codex-ml-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-ml
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
EOF

# Replace placeholders
sed -i "s|CONTAINER_REGISTRY_URL|$ACR_URL|g" deployment.yaml
sed -i "s|REDIS_HOST|$REDIS_HOST|g" deployment.yaml

# Apply deployment
kubectl apply -f deployment.yaml

# Verify deployment
kubectl get deployments
kubectl get pods
kubectl get svc
```

### 10. Configure Application Gateway

```bash
# Create public IP for Application Gateway
az network public-ip create \
  --resource-group $RESOURCE_GROUP \
  --name codex-ml-pip \
  --sku Standard \
  --zone 1 2 3

# Create Application Gateway
az network application-gateway create \
  --name codex-ml-appgw \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --vnet-name codex-ml-vnet \
  --subnet appgw-subnet \
  --capacity 2 \
  --sku Standard_v2 \
  --http-settings-cookie-based-affinity Enabled \
  --frontend-port 443 \
  --http-settings-port 80 \
  --http-settings-protocol Http \
  --public-ip-address codex-ml-pip \
  --cert-file /path/to/certificate.pfx \
  --cert-password <certificate-password>

# Create backend pool pointing to AKS service
# (Manual configuration in Azure Portal or CLI)
```

---

## Monitoring & Logging

### Azure Monitor Configuration

```bash
# Enable Container Insights for AKS
az aks enable-addons \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --addons monitoring

# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group $RESOURCE_GROUP \
  --workspace-name codex-ml-logs

# View logs
az monitor log-analytics query \
  --workspace codex-ml-logs \
  --analytics-query "ContainerLog | limit 10"
```

---

## Cost Optimization

```bash
# Right-size VMs
# Use B-series for dev/test
# Use D-series for production

# Enable Azure Autoscale
# Automatically scale based on metrics

# Use Reserved Instances for long-term savings
# 1-year or 3-year reservations provide 20-40% discounts
```

---

## Production Readiness Checklist

- [ ] AKS cluster with 3+ nodes across availability zones
- [ ] PostgreSQL with zone-redundant HA enabled
- [ ] Redis cache with data persistence
- [ ] Application Gateway configured with SSL/TLS
- [ ] Network policies configured for pod-to-pod security
- [ ] Pod security policies enforced
- [ ] Resource quotas and limits defined
- [ ] Horizontal Pod Autoscaler configured
- [ ] Azure Monitor configured with alerts
- [ ] Backup and restore procedures tested
- [ ] Container image vulnerability scanning enabled
- [ ] RBAC configured with minimal permissions
- [ ] Secrets stored in Azure Key Vault
- [ ] Log retention policies configured

---

**Next Steps**:
1. Configure DNS records for Application Gateway
2. Set up monitoring dashboard
3. Conduct load testing
4. Schedule disaster recovery drill
5. Plan backup and recovery procedures

