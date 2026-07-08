# System Architecture Overview

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-07-08  
**Author:** Phase 12 WS3 Documentation Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Deployment Architecture](#deployment-architecture)
6. [Technology Stack](#technology-stack)

---

## Executive Summary

The Codex platform is a distributed, microservices-based system for managing AI agents at enterprise scale. It provides:

- **Governance:** Role-based access control, approval workflows, audit logging
- **Scalability:** Horizontal scaling across cloud infrastructure
- **Security:** End-to-end encryption, multi-factor authentication, threat detection
- **Compliance:** SOC 2 Type II, GDPR, HIPAA-ready controls

### Key Metrics

- **Agents Supported:** 1000+ concurrent
- **API Requests:** 100K+/day
- **Latency:** <200ms p95
- **Availability:** 99.95% SLA
- **Audit Trail:** 90-day retention

---

## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web Console  │  │ CLI Tool     │  │ API Client   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           │                    │                  │
           └────────────────────┼──────────────────┘
                                │
                   HTTPS / TLS 1.3
                                │
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Load Balancer (AWS ELB / Google LB)                  │  │
│  │ - SSL/TLS termination                               │  │
│  │ - Rate limiting                                     │  │
│  │ - DDoS protection (CDN)                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │
           │ REST API / gRPC
           │
┌─────────────────────────────────────────────────────────────┐
│               Authentication & Authorization                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ OAuth 2.0 Gateway                                    │  │
│  │ - GitHub OAuth integration                          │  │
│  │ - MFA provider                                      │  │
│  │ - Token management                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │
┌─────────────────────────────────────────────────────────────┐
│              Microservices Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Agent Service│  │ Workflow Svc │  │  RBAC Svc    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Approval Svc  │  │  Audit Svc   │  │ Secrets Svc  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           │
           ├─────────┬─────────┬──────────┐
           │         │         │          │
┌──────────▼─┐ ┌──────▼────┐ ┌▼────────┐ ┌▼──────────┐
│   SQLite   │ │ PostgreSQL│ │  Redis  │ │   S3/GCS  │
│ (metadata) │ │  (audit)  │ │(cache)  │ │ (archive) │
└────────────┘ └───────────┘ └─────────┘ └───────────┘
```

### Architectural Layers

1. **Client Layer:** Web, CLI, API clients
2. **API Gateway:** Load balancing, TLS, rate limiting
3. **Auth Layer:** OAuth, MFA, token management
4. **Microservices:** Domain-specific services
5. **Data Layer:** Databases, caches, object storage

---

## Component Architecture

### Core Services

#### Agent Service

**Responsibilities:**
- Agent definition management
- Agent deployment and lifecycle
- Agent execution and logging
- Version management

**Dependencies:**
- PostgreSQL (agent metadata)
- S3/GCS (agent code/logs)
- Redis (cache)
- RBAC Service (authorization)
- Audit Service (logging)

**API Endpoints:**
```
GET    /api/v1/agents                    # List agents
POST   /api/v1/agents                    # Create agent
GET    /api/v1/agents/{id}               # Get agent
PUT    /api/v1/agents/{id}               # Update agent
DELETE /api/v1/agents/{id}               # Delete agent
POST   /api/v1/agents/{id}/execute       # Execute agent
GET    /api/v1/agents/{id}/versions      # List versions
POST   /api/v1/agents/{id}/rollback      # Rollback version
```

#### Workflow Service

**Responsibilities:**
- Workflow definition and execution
- CI/CD pipeline management
- Scheduling and triggers
- Workflow history and logs

**Dependencies:**
- PostgreSQL (workflow definitions)
- Agent Service (agent execution)
- Audit Service (logging)

#### RBAC Service

**Responsibilities:**
- Role management
- Permission validation
- Access control enforcement
- Scope management

**Dependencies:**
- SQLite (role definitions)
- Cache (permission checks)
- Audit Service (logging)

#### Approval Service

**Responsibilities:**
- Approval request management
- SLA tracking and escalation
- Decision recording
- Workflow coordination

**Dependencies:**
- PostgreSQL (requests)
- RBAC Service (authorization)
- Audit Service (logging)

#### Audit Service

**Responsibilities:**
- Event logging
- Compliance record keeping
- Audit trail storage
- Retention management

**Dependencies:**
- PostgreSQL (audit logs)
- S3/GCS (archived logs)

#### Secrets Service

**Responsibilities:**
- Secret encryption/decryption
- Rotation management
- Access control
- Audit logging

**Dependencies:**
- PostgreSQL (metadata)
- HSM (encryption keys)
- Audit Service (logging)

### Supporting Services

#### API Gateway
- TLS termination
- Rate limiting
- Request routing
- Load balancing

#### OAuth Manager
- GitHub integration
- Token exchange
- Session management

#### MFA Provider
- TOTP generation
- Code verification
- Backup code management

#### Token Manager
- JWT issuance
- Token validation
- Refresh mechanics
- Revocation

---

## Data Flow

### Authentication Flow

```
User Login
    ↓
[GitHub OAuth Flow]
    ├─ Redirect to GitHub
    ├─ User grants permission
    └─ GitHub redirects with code
    ↓
[Exchange Code for Tokens]
    ├─ OAuth Manager validates code
    ├─ GitHub returns access token
    └─ Codex creates session
    ↓
[MFA (if enabled)]
    ├─ User enters TOTP code
    └─ MFA Provider validates
    ↓
[Token Issuance]
    ├─ Access Token (15 min)
    ├─ Refresh Token (30 days)
    └─ Session Token (24 hours)
    ↓
User Authenticated
```

### Authorization Flow

```
API Request
    ↓
[Extract Token from Header]
    ├─ Authorization: ******
    └─ Validate signature (RS256)
    ↓
[Load User from Token]
    ├─ Get user_id
    ├─ Get roles
    └─ Get scopes
    ↓
[Check RBAC]
    ├─ RBAC Service validates permission
    ├─ (role, action, resource) → permission matrix
    └─ If denied: return 403
    ↓
[Check Scopes]
    ├─ Token scopes match required scope?
    └─ If denied: return 403
    ↓
[Audit Log]
    ├─ Record access attempt
    ├─ Include user, resource, result
    └─ Forward to Audit Service
    ↓
Request Proceeds / Request Denied
```

### Approval Workflow Flow

```
Sensitive Operation Requested
    ↓
[Create Approval Request]
    ├─ Policy Code: AGENT_DEPLOY_PROD
    ├─ Requester: alice@company.com
    ├─ Resource: agent_prod_001
    └─ Context: {agent_name, version, risk_level}
    ↓
[Check RBAC Auto-Approval]
    ├─ Requester has required role?
    ├─ Policy allows auto-approval?
    ├─ Operation is destructive?
    └─ If all yes: AUTO-APPROVED → proceed
    └─ If any no: PENDING → wait for approval
    ↓
[Get Approvers]
    ├─ Policy defines required roles
    ├─ RBAC lists users with roles
    └─ Notify approvers
    ↓
[Wait for Decisions]
    ├─ SLA: 4 hours
    ├─ Approver submits decision (approve/reject)
    └─ Audit logs decision
    ↓
[Check Quorum]
    ├─ All required approvers approved?
    ├─ Status: APPROVED → proceed
    ├─ Any rejected?
    ├─ Status: REJECTED → blocked
    └─ SLA expired?
    └─ Escalate to L2 approvers
    ↓
Operation Proceeds / Blocked
```

---

## Deployment Architecture

### Infrastructure Topology

```
┌──────────────────────────────────────────────────────────┐
│                  Internet                                │
└──────────────────────────────────────────────────────────┘
                         │
                    [CDN / WAF]
                    CloudFront/Akamai
                         │
┌──────────────────────────────────────────────────────────┐
│             AWS Region / Google Cloud Region             │
├──────────────────────────────────────────────────────────┤
│  Load Balancer (NLB / LB)                                │
│  - Port 443 (HTTPS)                                      │
│  - Health checks to backend                             │
│  - Auto-scaling                                         │
└──────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ K8s Cluster   │ │ K8s Cluster │ │ K8s Cluster │
│ Zone A (us-a) │ │ Zone B (us-b)│ │ Zone C (us-c)│
├───────────────┤ ├─────────────┤ ├─────────────┤
│ Pods:         │ │ Pods:       │ │ Pods:       │
│ - API Svc     │ │ - API Svc   │ │ - API Svc   │
│ - Agent Svc   │ │ - Agent Svc │ │ - Agent Svc │
│ - Auth Svc    │ │ - Auth Svc  │ │ - Auth Svc  │
│ - Audit Svc   │ │ - Audit Svc │ │ - Audit Svc │
└───────┬───────┘ └──────┬──────┘ └──────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼────────┐ ┌────▼─────┐
│ PostgreSQL     │ │ SQLite      │ │ Redis    │
│ (RDS)          │ │ (Local)     │ │(Elasticache)
│ - Agents       │ │ - RBAC      │ │ - Cache  │
│ - Workflows    │ │ - Approval  │ │ - Sessions
│ - Audit Logs   │ │             │ │ - Tokens
└────────────────┘ └─────────────┘ └──────────┘

        ┌────────────────┬────────────────┐
        │                │
┌───────▼──────────┐ ┌──▼────────────────┐
│ S3 / GCS         │ │ Secrets Manager    │
│ (Object Storage) │ │ (KMS Encryption)   │
│ - Agent Code     │ │ - Master Keys      │
│ - Agent Logs     │ │ - API Keys         │
│ - Archived Audit │ │ - DB Passwords     │
└──────────────────┘ └────────────────────┘
```

### Service Deployment

**API Service:** 3-5 replicas across zones
- CPU: 2 vCPU
- Memory: 4 GB
- Disk: 20 GB

**Agent Service:** Scaled based on queue depth
- Min replicas: 2
- Max replicas: 10
- CPU: 4 vCPU
- Memory: 8 GB

**Database Tier:**
- PostgreSQL: Multi-AZ primary + read replicas
- SQLite: In-memory + local disk
- Redis: Cluster mode, multi-zone

**Backup & Disaster Recovery:**
- PostgreSQL: Automated daily snapshots
- Application state: Replicated across zones
- RTO: 1 hour
- RPO: 15 minutes

---

## Technology Stack

### Programming Languages

| Component | Language | Version |
|-----------|----------|---------|
| API/Services | Python | 3.12+ |
| CLI | Python | 3.12+ |
| Web Console | TypeScript/React | 18+ |
| Infrastructure | Terraform | 1.6+ |

### Frameworks & Libraries

| Component | Framework | Version |
|-----------|-----------|---------|
| API Server | FastAPI | 0.100+ |
| Data Validation | Pydantic | 2.0+ |
| Authentication | PyJWT | 2.8+ |
| Database ORM | SQLAlchemy | 2.0+ |
| Task Queue | Celery | 5.3+ |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | Kubernetes | Container management |
| Container Runtime | Docker | Image building |
| Load Balancing | AWS ELB/ALB | Traffic distribution |
| DNS | Route53 / Cloud DNS | Service discovery |
| Storage | S3 / GCS | Object storage |
| CDN | CloudFront / Akamai | Content delivery |

### Data & Caching

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Relational DB | PostgreSQL | Primary data |
| Config DB | SQLite | Local state |
| Cache | Redis | Session/token cache |
| Message Queue | Redis / RabbitMQ | Async tasks |

### Security & Operations

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Secrets | HashiCorp Vault / AWS Secrets Manager | Secret management |
| Monitoring | Prometheus / Datadog | Metrics |
| Logging | ELK Stack / CloudWatch | Centralized logs |
| Alerting | AlertManager / PagerDuty | Incident response |
| Identity | OAuth 2.0 (GitHub) | Federation |
| Encryption | AES-256 / TLS 1.3 | Data protection |

---

## Scalability & Performance

### Load Characteristics

- **Concurrent Users:** 1,000+
- **Requests/Second:** 500-2,000 (peak)
- **Agent Executions/Day:** 100,000+
- **Data Retention:** 90+ days audit logs

### Scaling Strategy

**Horizontal Scaling:**
- Kubernetes auto-scaling (HPA)
- Target: <70% CPU, <80% Memory
- Scale-up: 1-2 minutes
- Scale-down: 5-10 minutes

**Vertical Scaling:**
- Database: Read replicas, connection pooling
- Cache: Cluster mode, replication
- Queue: Partitioning by shard key

### Performance Targets

| Metric | Target | P95 |
|--------|--------|-----|
| API Latency | <100ms | <200ms |
| Auth Latency | <50ms | <100ms |
| Approval Response | <200ms | <500ms |
| Database Query | <10ms | <50ms |

---

## References

- [Governance API Reference](../api/governance-api-reference.md)
- [Deployment Details](../ops/deployment-architecture-detailed.md)
- [Operations Guide](../ops/)

---

**Last Updated:** 2026-07-08  
**Version:** 1.0.0  
**Status:** Production Ready
