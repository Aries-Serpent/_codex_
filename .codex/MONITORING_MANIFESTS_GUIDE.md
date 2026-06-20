# Monitoring Manifests Deployment Guide

**Document Version:** 1.0  
**Last Updated:** 2026-06-20  
**Status:** Complete

## Overview

This guide documents the Kubernetes manifests for deploying a complete monitoring stack consisting of Prometheus, Grafana, and AlertManager. The manifests follow Kubernetes best practices and are designed for production-grade monitoring infrastructure.

## Manifest Structure

```
manifests/monitoring/
├── prometheus/
│   ├── deployment.yaml         # Prometheus deployment + config
│   ├── scrape-config.yaml      # ServiceMonitor definitions (generated)
│   └── alert-rules.yaml        # Alert rules (generated)
├── grafana/
│   ├── deployment.yaml         # Grafana deployment + config
│   └── dashboards/             # Dashboard JSONs (generated)
│       ├── system.json
│       ├── application.json
│       ├── kubernetes.json
│       └── business.json
└── alertmanager/
    └── deployment.yaml         # AlertManager deployment + config
```

## Deployment Order

### Phase 1: Namespace & RBAC Setup
1. Create monitoring namespace
2. Create service accounts
3. Configure RBAC (ClusterRoles, ClusterRoleBindings)

**Time:** ~30 seconds

### Phase 2: Storage Setup
1. Create PersistentVolumes (if not using StorageClass)
2. Create PersistentVolumeClaims
3. Verify storage is bound

**Time:** ~1 minute

### Phase 3: Deployment
1. Create ConfigMaps (configuration files)
2. Deploy Prometheus (waits for PVC)
3. Deploy AlertManager (waits for PVC)
4. Deploy Grafana (waits for PVC)

**Time:** ~3-5 minutes

### Phase 4: Verification
1. Verify all pods are running
2. Verify services are created
3. Verify persistent volumes are bound
4. Test endpoints

**Time:** ~2 minutes

**Total Deployment Time:** ~7-8 minutes

## Resource Requirements

### Prometheus
- **CPU Request:** 250m
- **CPU Limit:** 1000m
- **Memory Request:** 512Mi
- **Memory Limit:** 2Gi
- **Storage:** 50Gi (for 30-day retention at 1000 metrics)
- **Replicas:** 1

**Total:** ~1GB memory, 250m CPU at idle

### Grafana
- **CPU Request:** 100m
- **CPU Limit:** 500m
- **Memory Request:** 128Mi
- **Memory Limit:** 512Mi
- **Storage:** 10Gi (for dashboards and SQLite DB)
- **Replicas:** 1

**Total:** ~256MB memory, 100m CPU at idle

### AlertManager
- **CPU Request:** 100m
- **CPU Limit:** 250m
- **Memory Request:** 128Mi
- **Memory Limit:** 256Mi
- **Storage:** 10Gi (for alert history)
- **Replicas:** 1

**Total:** ~256MB memory, 100m CPU at idle

### Cluster Minimum Requirements
- **Nodes:** 1+ (3+ for production HA)
- **CPU:** 500m available
- **Memory:** 1.5Gi available
- **Storage:** 80Gi available for PVs
- **Network:** Ingress controller enabled (nginx-ingress or similar)

## Data Retention Policies

### Prometheus
- **Metrics Retention:** 30 days
- **Configuration:** `--storage.tsdb.retention.time=30d`
- **Storage:** ~1.5GB per day (varies with cardinality)
- **Adjustment:** Modify retention time in Prometheus deployment args

### AlertManager
- **Alert History:** 7 days (default AlertManager behavior)
- **Silences:** Persisted to disk, survive restarts
- **Storage:** ~100MB for typical deployments

### Grafana
- **Dashboard Data:** Persisted in SQLite database
- **Provisioned Dashboards:** Served from ConfigMaps
- **Annotations:** Stored in SQLite

## Configuration Management

### Prometheus Configuration
- **Location:** ConfigMap `prometheus-config`
- **File:** `/etc/prometheus/prometheus.yml`
- **Scrape Configs:** Defined in ConfigMap data
- **Update Process:** Edit ConfigMap, Prometheus auto-reloads via `--web.enable-lifecycle`

### Grafana Configuration
- **Location:** ConfigMap `grafana-config`
- **File:** `/etc/grafana/grafana.ini`
- **Environment:** Overrides in Deployment spec
- **Update Process:** Edit ConfigMap, restart Grafana pod

### AlertManager Configuration
- **Location:** ConfigMap `alertmanager-config`
- **File:** `/etc/alertmanager/alertmanager.yml`
- **Update Process:** Edit ConfigMap, restart AlertManager pod

## Health Checks

All deployments include:
- **Liveness Probe:** Checks if service is responsive (HTTP endpoint)
- **Readiness Probe:** Checks if service is ready to accept traffic
- **Initial Delay:** 5-30 seconds (configurable)
- **Period:** 5-10 seconds (configurable)

### Endpoints
- Prometheus: `http://prometheus:9090/-/healthy`
- Grafana: `http://grafana:3000/api/health`
- AlertManager: `http://alertmanager:9093/-/healthy`

## Access & Ingress

All services are accessible via Kubernetes Ingress with local hostnames:

- **Prometheus:** http://prometheus.local
- **Grafana:** http://grafana.local  
- **AlertManager:** http://alertmanager.local

**Prerequisites:**
- Ingress controller installed (nginx-ingress recommended)
- DNS resolution for .local hostnames (add to /etc/hosts or configure DNS)

## Security Considerations

### Current Configuration (Development)
- Basic authentication enabled
- Default credentials used (should be changed)
- Anonymous access allowed in Grafana

### Production Hardening
1. **Secrets Management:**
   - Move credentials to Secrets (not ConfigMaps)
   - Use secret injection tools (Sealed Secrets, External Secrets)

2. **Network Policies:**
   - Restrict traffic between pods
   - Deny by default, allow specific namespaces

3. **RBAC:**
   - Minimum permissions for each service
   - ServiceAccount per component

4. **TLS:**
   - Enable HTTPS on Ingress
   - Use cert-manager for automated certificates

5. **Authentication:**
   - Integrate with LDAP/OAuth2
   - Use strong random admin passwords
   - Enable MFA for Grafana

## Troubleshooting

### Pod Won't Start
```bash
# Check pod status
kubectl get pods -n monitoring
kubectl describe pod <pod-name> -n monitoring
kubectl logs <pod-name> -n monitoring
```

### PVC Not Binding
```bash
# Check PVC status
kubectl get pvc -n monitoring
kubectl describe pvc <pvc-name> -n monitoring

# Check PV status
kubectl get pv
kubectl describe pv <pv-name>
```

### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints -n monitoring
kubectl get svc -n monitoring

# Test connectivity
kubectl run -it --rm debug --image=alpine --restart=Never -- wget -O- http://prometheus:9090
```

### Configuration Not Applied
```bash
# For Prometheus (supports hot reload)
curl -X POST http://prometheus:9090/-/reload

# For AlertManager (needs restart)
kubectl rollout restart deployment/alertmanager -n monitoring

# For Grafana (needs restart)
kubectl rollout restart deployment/grafana -n monitoring
```

## Monitoring the Monitoring Stack

Prometheus and Grafana include self-monitoring:

- **Prometheus metrics:** http://prometheus:9090/metrics
- **Grafana metrics:** http://grafana:3000/metrics
- **AlertManager metrics:** http://alertmanager:9093/metrics

These metrics are scraped by Prometheus and can be visualized in Grafana dashboards.

## Scaling & High Availability

### Single Node (Default)
- 1 replica of each component
- Suitable for: Development, small staging environments
- Recovery: Manual (requires re-deployment)

### High Availability (Recommended for Production)
- 2-3 replicas of Prometheus (with remote storage)
- 2+ replicas of Grafana (with shared database)
- 3 replicas of AlertManager (clustering enabled)

**Configuration changes needed:**
- Enable Prometheus remote storage (S3, Azure Blob, etc.)
- Configure Grafana to use external database (PostgreSQL, MySQL)
- Configure AlertManager clustering in deployment args

## References

- [Prometheus Official Docs](https://prometheus.io/docs/)
- [Grafana Official Docs](https://grafana.com/docs/)
- [AlertManager Official Docs](https://prometheus.io/docs/alerting/latest/overview/)
- [Kubernetes Deployment Guide](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

## Manifest Validation

All YAML files can be validated using:

```bash
# Basic syntax validation
kubectl apply -f manifests/monitoring/ --dry-run=client

# More comprehensive validation
kubeval manifests/monitoring/*.yaml
```

## Version Information

- **Prometheus Version:** v2.45.0
- **Grafana Version:** 10.0.0
- **AlertManager Version:** v0.25.0
- **Kubernetes Minimum Version:** 1.19
- **RBAC:** Required (assumes RBAC is enabled)

## Next Steps

1. Review and update ConfigMap values for your environment
2. Configure persistent storage (StorageClass or local volumes)
3. Set AlertManager notification channels
4. Deploy manifests using `kubectl apply -f manifests/monitoring/`
5. Verify deployment health using verification script
6. Create custom dashboards and alert rules
