# ServiceMonitor Configuration Documentation

**Document Version:** 1.0  
**Last Updated:** 2026-06-20  
**Status:** Complete

## Overview

This document describes the ServiceMonitor resources and Prometheus scrape configuration for the monitoring stack. ServiceMonitors are Kubernetes Custom Resources that define how Prometheus should discover and scrape metrics from services.

## ServiceMonitor Resources

All ServiceMonitor CRDs are stored in `manifests/monitoring/prometheus/servicemonitors/`

### 1. Application HTTP Metrics (`app-service-http.yaml`)

**Purpose:** Monitor application services exposing metrics on HTTP port 8080  
**Namespace:** default  
**Target Services:** Services labeled with `app: backend` and `metrics-port: http`

**Configuration:**
- Port: http (8080)
- Scrape Interval: 30s
- Scrape Timeout: 10s

**Labels Added:**
- `kubernetes_namespace`: Namespace where pod is running
- `kubernetes_pod_name`: Name of the pod

**Use Cases:**
- Backend services with custom metrics
- Application performance metrics
- Business metrics

---

### 2. Application Prometheus Metrics (`app-service-prometheus.yaml`)

**Purpose:** Monitor application services using standard Prometheus format  
**Namespace:** default  
**Target Services:** Services labeled with `app: backend` and `metrics-port: prometheus`

**Configuration:**
- Port: prometheus (9090)
- Scrape Interval: 30s
- Scrape Timeout: 10s

**Labels Added:**
- `kubernetes_namespace`: Namespace where pod is running
- `kubernetes_pod_name`: Name of the pod

**Use Cases:**
- Services using Prometheus client libraries
- Services with /metrics endpoint
- Standardized metric format

---

### 3. Kubernetes API Server (`kubernetes-apiserver.yaml`)

**Purpose:** Monitor Kubernetes API server metrics  
**Namespace:** kube-system  
**Target Services:** Services with component=kube-apiserver label

**Configuration:**
- Port: https
- Scrape Interval: 60s (less frequent than app metrics)
- Scrape Timeout: 10s
- Scheme: https with certificate validation

**Key Metrics:**
- API server request latency
- API server request rate
- API server error rate
- API server memory usage
- API server goroutine count

**Labels Added:**
- `kubernetes_namespace`: Automatically set to kube-system

---

### 4. Kubelet (`kubernetes-kubelet.yaml`)

**Purpose:** Monitor node-level metrics from Kubelet  
**Namespace:** kube-system  
**Target Services:** Services with k8s-app=kubelet label

**Configuration:**
- Port: https-metrics
- Scrape Interval: 60s
- Scrape Timeout: 30s (longer due to volume of metrics)
- Scheme: https with certificate validation

**Key Metrics:**
- Node CPU usage
- Node memory usage
- Pod count per node
- Container runtime metrics
- Volume metrics

**Labels Added:**
- `node`: Node name (extracted from metadata)

---

### 5. Custom Application Metrics (`custom-app-metrics.yaml`)

**Purpose:** Monitor custom application-specific metrics  
**Namespace:** default  
**Target Services:** Services labeled with `app: custom-metrics`

**Configuration:**
- Port: metrics (8081)
- Scrape Interval: 30s
- Scrape Timeout: 10s

**Labels Added:**
- `namespace`: Kubernetes namespace
- `pod`: Pod name

**Use Cases:**
- Application-specific business metrics
- Custom business logic monitoring
- Domain-specific observability

---

## Scrape Configuration

The Prometheus scrape configuration is generated in `manifests/monitoring/prometheus/scrape-config.yaml`

### Global Settings

```yaml
global:
  scrape_interval: 30s              # Default scrape interval
  evaluation_interval: 30s          # How often to evaluate alert rules
  external_labels:
    cluster: 'kubernetes'           # Tag all metrics with cluster name
    environment: 'production'       # Tag all metrics with environment
```

### Scrape Jobs

#### 1. Prometheus Self-Monitoring
**Job Name:** prometheus  
**Target:** localhost:9090  
**Interval:** 30s (default)

Allows Prometheus to monitor itself.

#### 2. Kubernetes API Server
**Job Name:** kubernetes-apiservers  
**Discovery:** Kubernetes service discovery (endpoints role)  
**Scheme:** HTTPS  
**Interval:** 30s

Scrapes metrics from Kubernetes API servers.

#### 3. Kubernetes Nodes
**Job Name:** kubernetes-nodes  
**Discovery:** Kubernetes service discovery (node role)  
**Scheme:** HTTPS  
**Interval:** 30s

Scrapes node-level metrics via Kubelet.

#### 4. Kubernetes Pods
**Job Name:** kubernetes-pods  
**Discovery:** Kubernetes service discovery (pod role)  
**Interval:** 30s

Auto-discovers pods annotated with:
- `prometheus.io/scrape: "true"` - Enable scraping
- `prometheus.io/port: "8080"` - Metrics port (optional)
- `prometheus.io/path: "/metrics"` - Metrics path (optional, defaults to /metrics)

---

## Metric Collection Intervals

| Target | Interval | Timeout | Purpose |
|--------|----------|---------|---------|
| Prometheus | 30s | 10s | Self-monitoring, health checks |
| Application HTTP | 30s | 10s | Fast metric collection, app health |
| Application Prometheus | 30s | 10s | Standard metric format |
| Kubernetes API | 60s | 10s | Lower frequency, control plane |
| Kubelet | 60s | 30s | Node metrics, longer timeout |
| Custom Metrics | 30s | 10s | Application-specific metrics |

### Rationale

- **30s intervals:** Default for application metrics (balances frequency vs. load)
- **60s intervals:** Kubernetes system components (stable, less volatile)
- **Longer timeouts:** For components with large metric volumes (Kubelet)

---

## Retention Policies

### Prometheus Metric Storage

**Default Retention:** 30 days  
**Storage Calculation:** ~1.5GB per day (varies with cardinality)

**Adjustment:**
```yaml
# In Prometheus deployment
args:
  - '--storage.tsdb.retention.time=30d'  # Change '30d' to desired retention
```

**Retention Options:**
- 7d: Light storage, frequent rotation
- 15d: Balanced for development
- 30d: Default, good for SLA tracking
- 90d: Archive historical data (increases storage)

### AlertManager Alert History

**Default Retention:** 7 days  
**Storage:** ~100MB for typical deployments
**Behavior:** Automatically cleaned up by AlertManager

### Grafana Dashboard Data

**Retention:** Persistent  
**Storage:** SQLite database in PVC
**Growth Rate:** Slow (dashboards stored as JSON, not time-series)

---

## Service Discovery

### Kubernetes Service Discovery Methods

1. **Pod Role:** Discovers all pods in cluster
   - Useful for: Auto-discovery with pod annotations
   - Filter: Pod must have `prometheus.io/scrape: "true"` annotation

2. **Service Role:** Discovers all services
   - Useful for: Service-level discovery
   - Filter: Services must be explicitly targeted

3. **Node Role:** Discovers all nodes
   - Useful for: Kubelet metrics, node-level monitoring

4. **Endpoint Role:** Discovers all endpoints
   - Useful for: Fine-grained service discovery

### Pod Annotation Requirements

For automatic scraping, pods must include:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"         # Required: enable scraping
    prometheus.io/port: "8080"           # Optional: metrics port (default 8080)
    prometheus.io/path: "/metrics"       # Optional: metrics path (default /metrics)
    prometheus.io/scheme: "http"         # Optional: http or https (default http)
```

Example:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
spec:
  containers:
    - name: app
      image: my-app:latest
      ports:
        - containerPort: 8080
          name: metrics
```

---

## Metric Relabeling

### Global Relabeling

Applied to all scrape jobs:

```yaml
relabel_configs:
  - source_labels: [__meta_kubernetes_namespace]
    action: replace
    target_label: kubernetes_namespace

  - source_labels: [__meta_kubernetes_pod_name]
    action: replace
    target_label: kubernetes_pod_name
```

**Effect:** Adds namespace and pod name labels to all metrics

### Relabeling Actions

| Action | Purpose | Example |
|--------|---------|---------|
| keep | Only keep metrics matching condition | Keep only pods with prometheus.io/scrape=true |
| drop | Drop metrics matching condition | Drop internal metrics |
| replace | Replace label with new value | Replace namespace label |
| labelmap | Copy labels matching regex | Copy all __meta_kubernetes_* labels |

---

## Troubleshooting

### ServiceMonitor Not Working

1. Check if CRD is installed:
```bash
kubectl get crd servicemonitors.monitoring.coreos.com
```

2. Verify ServiceMonitor is created:
```bash
kubectl get servicemonitor -n monitoring
kubectl describe servicemonitor app-service-http -n default
```

3. Check if Prometheus discovers targets:
```bash
# Access Prometheus web UI
curl http://prometheus:9090/api/v1/targets
```

### No Metrics Being Collected

1. Verify target is healthy:
```bash
curl -v http://app-service:8080/metrics
```

2. Check Prometheus logs:
```bash
kubectl logs -n monitoring prometheus-0
```

3. Verify labels match:
```bash
kubectl get pods -n default -L app,metrics-port
```

### High Memory Usage

1. Increase scrape interval (less frequent collection):
```yaml
spec:
  endpoints:
    - interval: 60s  # Increase from 30s
```

2. Reduce metric cardinality (limit label variations)

3. Increase Prometheus memory limits in deployment

---

## Adding New Services

### Step 1: Create Service Labels
```yaml
metadata:
  labels:
    app: backend
    metrics-port: http
```

### Step 2: Add Pod Annotations
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

### Step 3: Service is Auto-Discovered

The existing scrape configs will automatically discover your service and start collecting metrics.

### Step 4: Create Custom ServiceMonitor (Optional)
If you need custom scraping behavior, create a ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
  namespace: default
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: metrics
      interval: 30s
```

---

## Performance Considerations

### Metric Cardinality
**Definition:** Number of unique metric time series

**Impact:** Higher cardinality = More memory, slower queries

**Optimization:**
- Use lower cardinality labels (avoid timestamps, UUIDs)
- Aggregate high-cardinality metrics
- Drop unnecessary metrics

### Scrape Load
**Metric Count × Scrape Frequency = Query Load**

**Optimization:**
- Increase scrape interval for stable metrics
- Use ServiceMonitor instead of pod discovery for better control
- Implement metric sampling for high-volume metrics

### Storage Optimization
**Configuration:**
```yaml
--storage.tsdb.retention.time=30d
--storage.tsdb.max-block-duration=2h
--storage.tsdb.min-block-duration=2h
```

---

## References

- [Prometheus Service Discovery](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#kubernetes_sd_config)
- [Prometheus Relabeling](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [Kubernetes Metadata Labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)

---

## Maintenance

### Monthly Review
1. Check metric cardinality
2. Review scrape success rates
3. Verify all targets are healthy
4. Check storage usage trends

### Quarterly Updates
1. Update ServiceMonitor definitions if targets change
2. Add new services to monitoring
3. Optimize underperforming scrape jobs
4. Review retention policies against storage availability
