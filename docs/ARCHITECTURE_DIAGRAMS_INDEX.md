# Architecture Diagram Index
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-01-20  
**Total Diagrams**: 17 (Phase 1 complete)  
**Coverage**: 15.7% (target: 85%+)  
**Quality**: ⭐⭐⭐⭐⭐ (5/5)

---

##  Quick Navigation

### Start Here 👇
**New to the codebase?** Start with these three diagrams:

1. **[System Context](architecture/SYSTEM_CONTEXT.md)** - What is this system?
2. **[5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md)** - How is it organized?
3. **[End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md)** - How does a request flow?

---

##  Complete Diagram Catalog

### System Architecture (6 diagrams)

| # | Diagram | File | Purpose | Best For |
|---|---------|------|---------|----------|
| 1 | **System Context** | [docs/architecture/SYSTEM_CONTEXT.md](architecture/SYSTEM_CONTEXT.md) | Users, external systems, C4 context | New developers, stakeholders |
| 2 | **5-Layer Architecture** | [docs/architecture/5_LAYER_ARCHITECTURE.md](architecture/5_LAYER_ARCHITECTURE.md) | Overall system structure | Understanding system design |
| 3 | **End-to-End Request Flow** | [docs/architecture/E2E_REQUEST_FLOW.md](architecture/E2E_REQUEST_FLOW.md) | Request lifecycle through all layers | Understanding execution paths |
| 4 | **Component Dependencies** | [docs/architecture/COMPONENT_DEPENDENCIES.md](architecture/COMPONENT_DEPENDENCIES.md) | Module relationships and critical paths | Performance optimization |
| 5 | **Data Flow Architecture** | [docs/architecture/DATA_FLOW_ARCHITECTURE.md](architecture/DATA_FLOW_ARCHITECTURE.md) | Data movement through system | Data engineering, ETL |
| 6 | **Deployment Architecture** | [docs/architecture/DEPLOYMENT_ARCHITECTURE.md](architecture/DEPLOYMENT_ARCHITECTURE.md) | Local, Docker, K8s, Cloud deployment | DevOps, deployment |

### Operational Architecture (3 diagrams)

| # | Diagram | File | Purpose | Best For |
|---|---------|------|---------|----------|
| 7 | **Security Architecture** | [docs/security/SECURITY_ARCHITECTURE.md](security/SECURITY_ARCHITECTURE.md) | Auth, encryption, scanning, monitoring | Security, compliance |
| 8 | **Monitoring Architecture** | [docs/monitoring/MONITORING_ARCHITECTURE.md](monitoring/MONITORING_ARCHITECTURE.md) | Metrics, logs, traces, alerts | Operations, observability |
| 9 | **CI/CD Pipeline** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#ci-cd-pipeline) | Build, test, deploy workflows | DevOps, CI/CD |

### Workflow Diagrams (4 diagrams)

| # | Diagram | File | Purpose | Best For |
|---|---------|------|---------|----------|
| 10 | **Training Workflow** | [docs/training/TRAINING_WORKFLOW.md](training/TRAINING_WORKFLOW.md) | Model training lifecycle | ML engineers |
| 11 | **PR Lifecycle** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#pr-lifecycle) | Pull request to merge process | Contributors, reviewers |
| 12 | **Agent Interaction Map** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#agent-interaction) | Agent coordination | Agent developers |
| 13 | **Cognitive Brain OODA** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#cognitive-brain) | Decision-making loop | Architecture, autonomous systems |

### Integration & Special (4 diagrams)

| # | Diagram | File | Purpose | Best For |
|---|---------|------|---------|----------|
| 14 | **Self-Healing Loop** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#self-healing) | Error recovery mechanism | DevOps, reliability |
| 15 | **PDA Loop + Aftermath** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#pda-loop) | Feedback and improvement loop | Continuous improvement |
| 16 | **Session Management** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#session-handoff) | Session lifecycle and recovery | Session engineers |
| 17 | **Rate Limiting** | [docs/CODEBASE_MERMAID_MAPS.md](CODEBASE_MERMAID_MAPS.md#rate-limit) | Request throttling mechanism | Performance engineers |

---

##  By User Role

### 👨‍💻 ML Engineers
**Learn how to**:
1. Train models → [Training Workflow](training/TRAINING_WORKFLOW.md)
2. Access training data → [Data Flow Architecture](architecture/DATA_FLOW_ARCHITECTURE.md)
3. Understand data pipeline → [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md)

### 🔧 DevOps/SRE
**Learn how to**:
1. Deploy the system → [Deployment Architecture](architecture/DEPLOYMENT_ARCHITECTURE.md)
2. Monitor performance → [Monitoring Architecture](monitoring/MONITORING_ARCHITECTURE.md)
3. Handle failures → [CI/CD Pipeline](CODEBASE_MERMAID_MAPS.md#ci-cd-pipeline)

###  Agent Developers
**Learn how to**:
1. Understand agent system → [Agent Interaction Map](CODEBASE_MERMAID_MAPS.md#agent-interaction)
2. Route tasks → [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md)
3. Integrate with brain → [Cognitive Brain OODA](CODEBASE_MERMAID_MAPS.md#cognitive-brain)

### 👀 Code Reviewers
**Learn how to**:
1. Understand request paths → [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md)
2. Find dependencies → [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md)
3. Check security implications → [Security Architecture](security/SECURITY_ARCHITECTURE.md)

### 🎓 New Contributors
**Learn the system**:
1. Start: [System Context](architecture/SYSTEM_CONTEXT.md)
2. Understand: [5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md)
3. Trace: [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md)
4. Explore: Pick a role from above

---

## 🔍 By Topic

### Core Architecture
- [5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md)
- [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md)
- [System Context](architecture/SYSTEM_CONTEXT.md)

### Data & Processing
- [Data Flow Architecture](architecture/DATA_FLOW_ARCHITECTURE.md)
- [Training Workflow](training/TRAINING_WORKFLOW.md)
- [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md)

### Operations & DevOps
- [Deployment Architecture](architecture/DEPLOYMENT_ARCHITECTURE.md)
- [Monitoring Architecture](monitoring/MONITORING_ARCHITECTURE.md)
- [CI/CD Pipeline](CODEBASE_MERMAID_MAPS.md#ci-cd-pipeline)
- [Self-Healing Loop](CODEBASE_MERMAID_MAPS.md#self-healing)

### Security & Reliability
- [Security Architecture](security/SECURITY_ARCHITECTURE.md)
- [Agent Interaction Map](CODEBASE_MERMAID_MAPS.md#agent-interaction)
- [Session Management](CODEBASE_MERMAID_MAPS.md#session-handoff)

### Autonomous Systems
- [Cognitive Brain OODA](CODEBASE_MERMAID_MAPS.md#cognitive-brain)
- [PDA Loop + Aftermath](CODEBASE_MERMAID_MAPS.md#pda-loop)
- [Rate Limiting](CODEBASE_MERMAID_MAPS.md#rate-limit)

---

##  Coverage by Layer

### Layer 1: Interface & CLI 
- System context (diagrams show entry points)
- Request routing
- Configuration loading

### Layer 2: ML Platform 
- Training workflow
- E2E request flow
- Component dependencies

### Layer 3: Data Pipeline 
- Data flow architecture
- E2E request flow
- Component dependencies

### Layer 4: Infrastructure 
- Deployment architecture
- Monitoring architecture
- Security architecture
- Data flow architecture

### Layer 5: Integration 
- Security architecture
- Agent interaction map
- System context

---

##  Quick Links

### Most Popular
1. [5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md) - System overview
2. [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md) - Request lifecycle
3. [Training Workflow](training/TRAINING_WORKFLOW.md) - ML workflow

### Most Detailed
1. [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md) - Module inventory
2. [Monitoring Architecture](monitoring/MONITORING_ARCHITECTURE.md) - Observability stack
3. [Security Architecture](security/SECURITY_ARCHITECTURE.md) - Security controls

### For Beginners
1. [System Context](architecture/SYSTEM_CONTEXT.md) - Start here
2. [5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md) - Then here
3. [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md) - Finally here

---

## 📈 Coverage Roadmap

###  Phase 1 Complete (17 diagrams, 15.7%)
- System architecture foundations
- Critical workflows
- Operational architecture

### 🔄 Phase 2 In Progress (15 diagrams, estimated 3-4 hours)
- Component-level details (CLI, RAG, Database, etc.)
- Integration patterns
- Configuration systems

### ⏳ Phase 3 Planned (5 diagrams, 1 hour)
- Integration points (GitHub, Zendesk, Cloud)
- External service connections

###  Phase 4 Bonus (20-30 diagrams, 15-20 hours)
- Detailed flows for each component
- Sequence diagrams
- Advanced architecture patterns
- Target: 85%+ coverage

**Current Progress**: 15.7% → **Target: 85%+**

---

##  How to Use These Diagrams

### For Understanding System Design
1. Read [System Context](architecture/SYSTEM_CONTEXT.md) (5 min)
2. Study [5-Layer Architecture](architecture/5_LAYER_ARCHITECTURE.md) (10 min)
3. Trace [End-to-End Request Flow](architecture/E2E_REQUEST_FLOW.md) (10 min)
4. **Total**: 25 minutes → Deep understanding 

### For Feature Development
1. Check [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md) (5 min)
2. Find your component's position (5 min)
3. Review related workflows (10 min)
4. Check [E2E Request Flow](architecture/E2E_REQUEST_FLOW.md) for integration (5 min)
5. **Total**: 25 minutes → Ready to code 

### For Debugging Issues
1. Check [Monitoring Architecture](monitoring/MONITORING_ARCHITECTURE.md) (5 min)
2. Review logs using the logging flow (5 min)
3. Trace [E2E Request Flow](architecture/E2E_REQUEST_FLOW.md) (10 min)
4. Check [Component Dependencies](architecture/COMPONENT_DEPENDENCIES.md) for bottlenecks (5 min)
5. **Total**: 25 minutes → Debug efficiently 

---

## 📞 Diagram Feedback

Found issues or have suggestions? 
- Comment on diagram files
- Create issue with tag `architecture-diagrams`
- Request new diagrams: Create issue with tag `diagram-request`

---

**Last Updated**: 2026-01-20  
**Next Update**: After Phase 2 completion  
**Questions?** See [ARCHITECTURE.md](architecture/INDEX.md) for full documentation
