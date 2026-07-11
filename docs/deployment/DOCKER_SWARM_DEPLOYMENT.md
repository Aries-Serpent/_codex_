# Docker Compose Multi-Node Deployment Guide
**Last Updated:** 2026-07-11

**Last Updated**: 2026-07-08  
**Version**: 1.0  
**Audience**: Development teams, small production deployments, edge deployments  
**Environment**: Docker Swarm / Docker Compose Stack Mode  
**Tier**: Production-Ready (Small Scale)

---

## Overview

This guide covers deploying Codex ML using Docker Compose with multi-node clustering via Docker Swarm for small to medium production deployments.

### Architecture

```
┌───────────────────────────────────────────────┐
│        Docker Swarm Cluster                   │
├───────────────────────────────────────────────┤
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  Manager Node 1 (Leader)                │ │
│  │  - Raft consensus                       │ │
│  │  - Task orchestration                   │ │
│  └─────────────────────────────────────────┘ │
│          ├─────────────────────────┐          │
│          │                         │          │
│  ┌───────▼────────────┐  ┌────────▼───────┐  │
│  │ Manager Node 2     │  │ Worker Node 1   │  │
│  │ - Standby leader   │  │ - Task execution│  │
│  └────────────────────┘  └─────────────────┘  │
│          │                         │           │
│  ┌───────▼────────────┐  ┌────────▼───────┐  │
│  │ Manager Node 3     │  │ Worker Node 2   │  │
│  └────────────────────┘  └─────────────────┘  │
│                                                │
│  Codex ML Service (Replicas: 3)              │
│  Database Service (PostgreSQL)                │
│  Cache Service (Redis)                        │
│                                               │
└───────────────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements

```bash
# Minimum per node
- CPU: 2 cores
- RAM: 4GB
- Storage: 50GB
- OS: Ubuntu 20.04+ or Docker Desktop

# Docker version
Docker >= 20.10
Docker Compose >= 2.0
```

### Install Docker & Swarm

```bash
# Install Docker (on all nodes)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version

# Initialize Swarm on first manager node
docker swarm init --advertise-addr 10.0.0.10

# Get join tokens for other nodes
docker swarm join-token manager  # for manager nodes
docker swarm join-token worker   # for worker nodes

# On other manager nodes
docker swarm join --token <manager-token> 10.0.0.10:2377

# On worker nodes
docker swarm join --token <worker-token> 10.0.0.10:2377

# Verify cluster
docker node ls
```

---

## Step-by-Step Deployment

### 1. Prepare Docker Compose File

```yaml
# docker-compose.yml
version: '3.9'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: codex
      POSTGRES_USER: codex_admin
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - backend
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U codex_admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - backend
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Codex ML Application
  codex-ml:
    image: registry.example.com/codex-ml:1.0.0
    environment:
      DATABASE_URL: ******postgres:5432/codex
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      NUM_WORKERS: 4
    ports:
      - "8000:8000"
    networks:
      - backend
      - frontend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      mode: replicated
      replicas: 3
      placement:
        constraints: [node.role == worker]
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 10s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 40s
    secrets:
      - db_password

  # Nginx Load Balancer
  nginx:
    image: nginx:1.25-alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
    depends_on:
      - codex-ml
    deploy:
      mode: replicated
      replicas: 2
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: '1'
          memory: 512M
      restart_policy:
        condition: on-failure

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - backend
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # Grafana Visualization
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123456
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    ports:
      - "3000:3000"
    networks:
      - backend
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints: [node.role == manager]

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  backend:
    driver: overlay
    driver_opts:
      com.docker.network.driver.mtu: 1450
  frontend:
    driver: overlay

secrets:
  db_password:
    external: true

x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "3"
```

### 2. Create Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 4096;
}

http {
    upstream codex_ml_backend {
        least_conn;
        server codex-ml:8000 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_status 429;

    server {
        listen 80;
        server_name _;
        
        client_max_body_size 100M;
        proxy_read_timeout 300s;

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://codex_ml_backend;
        }

        # API endpoints
        location ~ ^/api/ {
            limit_req zone=api_limit burst=200 nodelay;
            
            proxy_pass http://codex_ml_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket support
        location ~ ^/ws/ {
            proxy_pass http://codex_ml_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # Static files caching
        location ~ \.(js|css|png|jpg|gif|ico|svg|woff|woff2)$ {
            proxy_pass http://codex_ml_backend;
            proxy_cache_valid 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # HTTPS server (when certificates are available)
    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Rest of configuration same as above
    }
}
```

### 3. Create Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'codex-ml-prod'

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - '/etc/prometheus/rules.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'codex-ml'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['codex-ml:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        regex: '([^:]+)(?::\d+)?'
        replacement: '${1}'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'docker'
    unix_sock_addr: /var/run/docker.sock
    static_configs:
      - targets: ['localhost:9323']
```

### 4. Deploy the Stack

```bash
# Create secrets
echo "$(openssl rand -base64 32)" | docker secret create db_password -

# Deploy stack
docker stack deploy -c docker-compose.yml codex-ml

# Verify deployment
docker stack ps codex-ml

# Check service status
docker service ls

# View logs
docker service logs codex-ml_codex-ml

# Monitor stack health
watch 'docker stack ps codex-ml'
```

### 5. Scaling Services

```bash
# Scale Codex ML replicas
docker service scale codex-ml_codex-ml=5

# Scale with update policy
docker service update \
  --mode replicated \
  --replicas 5 \
  codex-ml_codex-ml

# Update with rolling deployment
docker service update \
  --image registry.example.com/codex-ml:1.0.1 \
  --update-parallelism 1 \
  --update-delay 10s \
  --update-failure-action rollback \
  codex-ml_codex-ml
```

---

## Backup & Restore

```bash
# Backup PostgreSQL
docker exec codex-ml_postgres_1 pg_dump -U codex_admin codex > /backup/codex-backup.sql

# Backup Redis
docker exec codex-ml_redis_1 redis-cli --rdb /data/redis-backup.rdb

# Backup Docker Compose volumes
docker run --rm -v codex-ml_postgres_data:/data -v /backup:/backup \
  ubuntu tar czf /backup/postgres-data.tar.gz -C /data .

# Restore PostgreSQL
docker exec -i codex-ml_postgres_1 psql -U codex_admin codex < /backup/codex-backup.sql

# Restore Docker volumes
docker run --rm -v codex-ml_postgres_data:/data -v /backup:/backup \
  ubuntu tar xzf /backup/postgres-data.tar.gz -C /data
```

---

## Monitoring & Logging

```bash
# Access Grafana dashboard
# URL: http://<manager-ip>:3000
# Credentials: admin/admin123456

# View service metrics
docker stats

# Check container logs
docker service logs codex-ml_codex-ml -f

# View event logs
docker events --filter service=codex-ml_codex-ml

# Monitor swarm health
docker node ls
docker service inspect --pretty codex-ml_codex-ml
```

---

## Production Readiness Checklist

- [ ] 3+ manager nodes for HA
- [ ] 2+ worker nodes for application
- [ ] Swarm cluster initialized and healthy
- [ ] Secrets configured (database password, API keys)
- [ ] Volumes properly mounted and backed up
- [ ] Load balancer (Nginx) configured
- [ ] Health checks enabled for all services
- [ ] Resource limits defined
- [ ] Monitoring (Prometheus/Grafana) deployed
- [ ] Log aggregation configured
- [ ] Backup procedures implemented and tested
- [ ] Automated rollback on update failure
- [ ] SSL/TLS certificates installed
- [ ] Network policies configured

---

**Advantages**:
- Simple deployment and management
- Built-in load balancing
- Automatic restart and healing
- Rolling updates with rollback
- Good for small to medium deployments

**Limitations**:
- Limited advanced features compared to Kubernetes
- Single Raft consensus ring (scale limitations)
- Basic networking compared to Kubernetes
- Fewer ecosystem tools and integrations

