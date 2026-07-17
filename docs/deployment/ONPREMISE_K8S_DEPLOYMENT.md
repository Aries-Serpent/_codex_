# On-Premise Kubernetes Deployment Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-07-08
**Version**: 1.0
**Audience**: Enterprise IT, Infrastructure teams, self-hosted operators
**Environment**: On-Premise Kubernetes (KubeAdm, Rancher, etc.)
**Tier**: Production-Ready

---

## Overview

This guide covers deploying Codex ML on self-hosted Kubernetes infrastructure within your datacenter or private cloud environment.

### Architecture

```

 On-Premise Kubernetes Cluster 

 
 
 Load Balancer (MetalLB) 
 - Layer 4 load balancing 
 - Sticky sessions 
 - Health checks 
 
 
 
 Kubernetes Master Nodes (3) 
 - Control plane HA 
 - etcd database replication 
 - API server load balancing 
 
 
 
 Worker Nodes (5-10) 
 Node 1 (4 CPU, 8GB RAM) 
 Node 2 (4 CPU, 8GB RAM) 
 Node 3 (4 CPU, 8GB RAM) 
 Node N 
 
 
 Codex ML Pod (Deployment) 
 - Replicas: 3 
 - CPU: 2, Memory: 4Gi per pod 
 - Health checks enabled 
 
 
 
 
 Storage Layer 
 Local storage (node-local) 
 NFS/iSCSI (shared storage) 
 Persistent Volume Claims 
 
 
 
 Data Layer 
 PostgreSQL (HA with streaming repl.) 
 Redis (cluster mode) 
 NFS for backup storage 
 
 
 
 Monitoring & Logging 
 Prometheus (metrics collection) 
 Grafana (visualization) 
 Loki (log aggregation) 
 AlertManager (alerts) 
 
 

```

---

## Prerequisites

### Hardware Requirements

**Minimum Configuration**:
- Master Nodes: 3 (2 vCPU, 4GB RAM, 40GB disk each)
- Worker Nodes: 5-10 (4 vCPU, 8GB RAM, 100GB disk each)
- Storage: 500GB+ for persistent data

**Recommended Configuration**:
- Master Nodes: 3 (4 vCPU, 8GB RAM, 100GB SSD each)
- Worker Nodes: 5-10 (8 vCPU, 16GB RAM, 200GB SSD each)
- Storage: 1TB+ for persistent data with redundancy

### Software Requirements

```bash
# OS: Ubuntu 20.04/22.04 or RHEL 8+
# Kernel: 5.4+
# Container runtime: Docker 20.10+ or containerd 1.5+

# Verify OS
lsb_release -a # or cat /etc/os-release

# Check kernel version
uname -r

# Check system resources
free -h
df -h
nproc
```

---

## Step-by-Step Deployment

### 1. Prepare Infrastructure

```bash
# Update all nodes
sudo apt-get update
sudo apt-get upgrade -y

# Disable swap (required for Kubernetes)
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Configure firewall rules
# On each master node:
sudo firewall-cmd --permanent --add-port=6443/tcp # API server
sudo firewall-cmd --permanent --add-port=2379-2380/tcp # etcd
sudo firewall-cmd --permanent --add-port=10250/tcp # Kubelet
sudo firewall-cmd --permanent --add-port=10251/tcp # Scheduler
sudo firewall-cmd --permanent --add-port=10252/tcp # Controller

# On each worker node:
sudo firewall-cmd --permanent --add-port=10250/tcp # Kubelet
sudo firewall-cmd --permanent --add-port=30000-32767/tcp # NodePort

sudo firewall-cmd --reload

# Configure hostname resolution
# Ensure /etc/hosts contains all nodes:
cat << 'EOF' | sudo tee -a /etc/hosts
10.0.0.10 k8s-master-1
10.0.0.11 k8s-master-2
10.0.0.12 k8s-master-3
10.0.0.20 k8s-worker-1
10.0.0.21 k8s-worker-2
EOF
```

### 2. Install Container Runtime (Docker)

```bash
# Remove any existing Docker installations
sudo apt-get remove docker docker-engine docker.io containerd runc -y

# Install Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
 "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
 $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version

# Configure Docker daemon
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
 "exec-opts": ["native.cgroupdriver=systemd"],
 "log-driver": "json-file",
 "log-opts": {
 "max-size": "100m",
 "max-file": "3"
 },
 "insecure-registries": ["registry.example.com:5000"]
}
EOF

# Restart Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# Add current user to docker group
sudo usermod -aG docker $USER
```

### 3. Install Kubernetes Tools

```bash
# Add Kubernetes repository
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubeadm, kubelet, kubectl
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# Hold versions to prevent automatic updates
sudo apt-mark hold kubelet kubeadm kubectl

# Enable kubelet
sudo systemctl enable kubelet
sudo systemctl start kubelet

# Verify installation
kubeadm version
kubelet --version
kubectl version --client
```

### 4. Initialize Kubernetes Master (Control Plane)

```bash
# On the first master node (k8s-master-1):
# Create kubeadm configuration
cat > kubeadm-config.yaml <<'EOF'
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v0.2.1
controlPlaneEndpoint: "10.0.0.10:6443"
apiServer:
 certSANs:
 - "10.0.0.10"
 - "10.0.0.11"
 - "10.0.0.12"
 - "k8s-master-1"
 - "k8s-master-2"
 - "k8s-master-3"
 extraArgs:
 audit-log-path: /var/log/audit/audit.log
 audit-log-maxage: "10"
 audit-log-maxbackup: "5"
 audit-log-maxsize: "100"
etcd:
 local:
 dataDir: /var/lib/etcd
networking:
 dnsDomain: cluster.local
 podSubnet: "10.244.0.0/16"
 serviceSubnet: "10.96.0.0/12"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
nodeRegistration:
 kubeletExtraArgs:
 cgroup-driver: systemd
 max-pods: "110"
EOF

# Initialize the cluster
sudo kubeadm init --config=kubeadm-config.yaml

# Configure kubectl for the current user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Save join commands
sudo kubeadm token create --print-join-command > join-command.txt

# Verify cluster
kubectl get nodes
kubectl get pods --all-namespaces
```

### 5. Install Network Add-on (Flannel)

```bash
# Install Flannel for pod networking
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Alternatively, install Calico for more advanced features
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/release-v3.26/manifests/tigera-operator.yaml
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/release-v3.26/manifests/custom-resources.yaml

# Wait for networking to be ready
kubectl wait --for=condition=ready pod -l k8s-app=flannel -n kube-flannel --timeout=120s
```

### 6. Join Additional Master Nodes

```bash
# On k8s-master-2 and k8s-master-3:
# Get the join command from master-1
cat join-command.txt

# Execute the join command (add --control-plane flag for additional masters)
sudo kubeadm join 10.0.0.10:6443 --token <token> \
 --discovery-token-ca-cert-hash sha256:<hash> \
 --control-plane \
 --certificate-key <cert-key>

# Verify all masters are ready
kubectl get nodes
```

### 7. Join Worker Nodes

```bash
# On each worker node:
sudo kubeadm join 10.0.0.10:6443 --token <token> \
 --discovery-token-ca-cert-hash sha256:<hash>

# Verify all nodes are ready
kubectl get nodes -o wide
```

### 8. Install Load Balancer (MetalLB)

```bash
# Install MetalLB for bare-metal load balancing
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.2.1/config/manifests/metallb-native.yaml

# Create configuration for IP address pool
cat > metallb-config.yaml <<'EOF'
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
 name: first-pool
 namespace: metallb-system
spec:
 addresses:
 - 10.0.0.100-10.0.0.110
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
 name: example
 namespace: metallb-system
spec:
 ipAddressPools:
 - first-pool
EOF

kubectl apply -f metallb-config.yaml

# Verify MetalLB is running
kubectl get pods -n metallb-system
```

### 9. Set Up Storage

```bash
# Create local storage provisioner
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml

# Or configure NFS for shared storage
# Install NFS server on a dedicated node:
sudo apt-get install nfs-kernel-server -y
sudo mkdir -p /srv/k8s-nfs
echo "/srv/k8s-nfs *(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -a
sudo systemctl restart nfs-kernel-server

# Create NFS provisioner in Kubernetes
# (Install nfs-subdir-external-provisioner)
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/

helm install nfs-subdir-external-provisioner \
 nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
 --set nfs.server=10.0.0.30 \
 --set nfs.path=/srv/k8s-nfs
```

### 10. Deploy PostgreSQL (StatefulSet)

```bash
# Create namespace
kubectl create namespace data-layer

# Create PostgreSQL StatefulSet
cat > postgres-statefulset.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
 name: postgres-secret
 namespace: data-layer
type: Opaque
data:
 password: Y29kZXgtcGFzc3dvcmQ= # codex-password in base64
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
 name: postgres-pvc
 namespace: data-layer
spec:
 accessModes:
 - ReadWriteOnce
 storageClassName: nfs-client
 resources:
 requests:
 storage: 100Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
 name: postgres
 namespace: data-layer
spec:
 serviceName: postgres
 replicas: 1
 selector:
 matchLabels:
 app: postgres
 template:
 metadata:
 labels:
 app: postgres
 spec:
 containers:
 - name: postgres
 image: postgres:14-alpine
 env:
 - name: POSTGRES_DB
 value: codex
 - name: POSTGRES_USER
 value: codex_admin
 - name: POSTGRES_PASSWORD
 valueFrom:
 secretKeyRef:
 name: postgres-secret
 key: password
 ports:
 - containerPort: 5432
 name: postgres
 volumeMounts:
 - name: postgres-storage
 mountPath: /var/lib/postgresql/data
 resources:
 requests:
 cpu: 1000m
 memory: 2Gi
 limits:
 cpu: 2000m
 memory: 4Gi
 livenessProbe:
 exec:
 command:
 - /bin/sh
 - -c
 - exec pg_isready -U codex_admin -h 127.0.0.1
 initialDelaySeconds: 30
 periodSeconds: 10
 volumes:
 - name: postgres-storage
 persistentVolumeClaim:
 claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
 name: postgres
 namespace: data-layer
spec:
 clusterIP: None
 ports:
 - port: 5432
 targetPort: 5432
 selector:
 app: postgres
EOF

kubectl apply -f postgres-statefulset.yaml
```

### 11. Deploy Redis (StatefulSet)

```bash
# Create Redis StatefulSet
cat > redis-statefulset.yaml <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
 name: redis-config
 namespace: data-layer
data:
 redis.conf: |
 maxmemory 2gb
 maxmemory-policy allkeys-lru
 appendonly yes
 appendfsync everysec
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
 name: redis-pvc
 namespace: data-layer
spec:
 accessModes:
 - ReadWriteOnce
 storageClassName: nfs-client
 resources:
 requests:
 storage: 20Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
 name: redis
 namespace: data-layer
spec:
 serviceName: redis
 replicas: 1
 selector:
 matchLabels:
 app: redis
 template:
 metadata:
 labels:
 app: redis
 spec:
 containers:
 - name: redis
 image: redis:7-alpine
 command:
 - redis-server
 - /usr/local/etc/redis/redis.conf
 ports:
 - containerPort: 6379
 name: redis
 volumeMounts:
 - name: redis-data
 mountPath: /data
 - name: redis-config
 mountPath: /usr/local/etc/redis/
 resources:
 requests:
 cpu: 500m
 memory: 1Gi
 limits:
 cpu: 1000m
 memory: 2Gi
 volumes:
 - name: redis-config
 configMap:
 name: redis-config
 - name: redis-data
 persistentVolumeClaim:
 claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
 name: redis
 namespace: data-layer
spec:
 clusterIP: None
 ports:
 - port: 6379
 targetPort: 6379
 selector:
 app: redis
EOF

kubectl apply -f redis-statefulset.yaml
```

### 12. Deploy Codex ML Application

```bash
# Create namespace
kubectl create namespace codex-ml

# Create secret for Docker registry
kubectl create secret docker-registry docker-secret \
 --docker-server=registry.example.com \
 --docker-username=username \
 --docker-****** \
 --docker-email=email@example.com \
 -n codex-ml

# Create application deployment
cat > codex-deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
 name: codex-ml
 namespace: codex-ml
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
 imagePullSecrets:
 - name: docker-secret
 affinity:
 podAntiAffinity:
 preferredDuringSchedulingIgnoredDuringExecution:
 - weight: 100
 podAffinityTerm:
 labelSelector:
 matchExpressions:
 - key: app
 operator: In
 values:
 - codex-ml
 topologyKey: kubernetes.io/hostname
 containers:
 - name: codex-ml
 image: registry.example.com/codex-ml:1.0.0
 imagePullPolicy: Always
 ports:
 - containerPort: 8000
 name: http
 env:
 - name: DATABASE_URL
 value: "******postgres.data-layer.svc.cluster.local:5432/codex"
 - name: REDIS_URL
 value: "redis://redis.data-layer.svc.cluster.local:6379/0"
 - name: ENVIRONMENT
 value: "production"
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
 failureThreshold: 3
 readinessProbe:
 httpGet:
 path: /ready
 port: 8000
 initialDelaySeconds: 10
 periodSeconds: 5
 failureThreshold: 2
---
apiVersion: v1
kind: Service
metadata:
 name: codex-ml-service
 namespace: codex-ml
spec:
 type: LoadBalancer
 ports:
 - port: 80
 targetPort: 8000
 protocol: TCP
 selector:
 app: codex-ml
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
 name: codex-ml-hpa
 namespace: codex-ml
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
EOF

kubectl apply -f codex-deployment.yaml

# Verify deployment
kubectl get deployments -n codex-ml
kubectl get pods -n codex-ml
kubectl get svc -n codex-ml
```

### 13. Install Monitoring Stack (Prometheus + Grafana)

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
 --namespace monitoring \
 --create-namespace \
 --values - <<EOF
prometheus:
 prometheusSpec:
 retention: 30d
 storageSpec:
 volumeClaimTemplate:
 spec:
 accessModes: ["ReadWriteOnce"]
 resources:
 requests:
 storage: 50Gi
grafana:
 adminPassword: admin123456
 persistence:
 enabled: true
 size: 10Gi
EOF

# Expose Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &

# Access Grafana at http://localhost:3000
# Default credentials: admin/admin123456
```

---

## Backup & Disaster Recovery

```bash
# Backup etcd
sudo ETCDCTL_API=3 etcdctl \
 --endpoints=https://127.0.0.1:2379 \
 --cacert=/etc/kubernetes/pki/etcd/ca.crt \
 --cert=/etc/kubernetes/pki/etcd/server.crt \
 --key=/etc/kubernetes/pki/etcd/server.key \
 snapshot save /backup/etcd-backup.db

# Backup persistent data
kubectl get pvc -A -o json | jq '.items[] | {namespace: .metadata.namespace, name: .metadata.name}' > /backup/pvc-manifest.json

# Backup all Kubernetes manifests
kubectl get all -A -o yaml > /backup/k8s-manifest-backup.yaml
```

---

## Production Readiness Checklist

- [ ] 3+ master nodes for HA
- [ ] 5+ worker nodes with proper sizing
- [ ] Container runtime installed and configured
- [ ] Network add-on deployed (Flannel/Calico)
- [ ] Load balancer configured (MetalLB)
- [ ] Persistent storage configured (NFS/Local)
- [ ] PostgreSQL StatefulSet deployed with HA
- [ ] Redis cache deployed
- [ ] Application deployed with proper resource limits
- [ ] Horizontal Pod Autoscaler configured
- [ ] Monitoring stack deployed (Prometheus/Grafana)
- [ ] Backup procedures implemented
- [ ] Network policies configured
- [ ] Pod security policies enforced
- [ ] Regular backup tests scheduled

---

**Next Steps**:
1. Configure Ingress controller (Nginx/Traefik)
2. Set up TLS certificates
3. Configure monitoring dashboards
4. Conduct load testing
5. Schedule regular disaster recovery drills

