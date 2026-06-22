# Architecture Quick Reference

**Last Updated**: 2026-06-22  
**Status**: ✅ Consolidated  
**Full Reference**: [Consolidated Architecture](./architecture/ARCHITECTURE_CONSOLIDATED.md)

---

## 🎯 System Overview

**Aries-Serpent/_codex_**: MLOps-certified ML framework with AI assistant integration

- **MLOps Level**: 4/4 (100/100 Azure certification)
- **Package**: `codex-ml` (PyPI)
- **Language**: Python
- **Test Coverage**: 10.7% (2,079+ test files)
- **Status**: Production-ready

---

## 🏗️ Core Architecture

### System Layers

```
┌─────────────────────────────────────────┐
│         User Applications (API)         │
├─────────────────────────────────────────┤
│     Framework Layer (Hydra, OmegaConf)  │
├─────────────────────────────────────────┤
│    ML Training & Evaluation Pipeline    │
├─────────────────────────────────────────┤
│      Plugin System & Extensibility      │
├─────────────────────────────────────────┤
│    Data Processing & Infrastructure     │
├─────────────────────────────────────────┤
│          Storage & Persistence          │
└─────────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Core ML** | Training & evaluation | `src/codex_ml/` |
| **Configuration** | Hydra config management | `docs/configuration/` |
| **Plugins** | Extensibility system | `src/codex_ml/plugins/` |
| **Utilities** | Shared utilities | `src/codex_utils/` |
| **CLI** | Command-line interface | `src/codex/cli/` |

---

## 📊 Directory Structure (Simplified)

```
_codex_/
├── src/
│   ├── codex_ml/           # Main ML framework
│   ├── codex_utils/        # Utilities library
│   ├── codex/              # Core package
│   └── ...
├── tests/                  # Test suite
├── docs/                   # Documentation hub
├── .github/                # GitHub Actions workflows
├── pyproject.toml          # Package configuration
└── README.md               # Main readme
```

---

## 🔄 Data Flow

```
Config (YAML) → Hydra → Framework
                           ↓
                    Plugin System
                           ↓
                    ML Pipeline
                           ↓
                  Data Processing
                           ↓
                      Storage
```

---

## 🔌 Plugin Architecture

The system uses a plugin-driven design:

1. **Define Plugin Interface** - Specify required methods
2. **Implement Plugin** - Inherit from base class
3. **Register Plugin** - Add to plugin registry
4. **Use in Pipeline** - Reference in configuration

---

## ⚙️ Configuration System

Uses **Hydra** for configuration management:

```yaml
# config.yaml
database:
  driver: postgresql
  host: localhost
  port: 5432

training:
  epochs: 100
  batch_size: 32
  learning_rate: 0.001
```

---

## 🚀 Deployment Architecture

### Production Deployment

```
Load Balancer
     ↓
  [API Servers]
     ↓
  [Workers]
     ↓
  [Database]
  [Cache]
  [Storage]
```

### Environments

| Environment | Purpose | Scale |
|-------------|---------|-------|
| Development | Local development | 1 instance |
| Staging | Pre-production testing | 3 instances |
| Production | Live service | 10+ instances |

---

## 🔐 Security Architecture

### Security Layers

1. **API Security** - Authentication, rate limiting
2. **Data Security** - Encryption at rest and in transit
3. **Access Control** - RBAC, identity verification
4. **Audit** - Comprehensive logging and monitoring
5. **Infrastructure** - Network segmentation, hardened configs

---

## 📈 Scalability Design

### Horizontal Scaling
- Stateless API servers
- Load balanced requests
- Shared database backend
- Distributed cache

### Vertical Scaling
- Resource optimization
- Efficient algorithms
- Database indexing
- Query optimization

---

## 🔗 Key Documentation

### Architecture & Design
- **[Consolidated Architecture](./architecture/ARCHITECTURE_CONSOLIDATED.md)** - Complete reference
- **[System Overview](./architecture/system_overview.md)** - High-level overview
- **[Architecture Layers](./architecture/ARCHITECTURE_LAYERS.md)** - Detailed layers

### Configuration & Setup
- **[Hydra Guide](./configuration/HYDRA_GUIDE.md)** - Configuration management
- **[Setup Guide](./setup/)** - Installation and setup

### Development
- **[Contributing Guide](./contributing/)** - Contributing guidelines
- **[API Reference](./API_REFERENCE.md)** - API documentation

### Operations
- **[Deployment Guide](./deployment/)** - Deployment procedures
- **[Operations Manual](./operations/)** - Operational procedures
- **[Troubleshooting](./troubleshooting/)** - Problem solving

---

## 📚 Learning Path

1. **Understand Architecture**: Read this quick reference
2. **Explore System**: Review system overview and diagrams
3. **Learn Configuration**: Study Hydra configuration guide
4. **Understand Plugins**: Review plugin system documentation
5. **Read Full Reference**: See consolidated architecture for details

---

## 🎓 Advanced Topics

### For Developers
- Plugin development
- Custom data processors
- Extension points
- Testing framework

### For DevOps
- Infrastructure setup
- Deployment automation
- Monitoring integration
- Backup procedures

### For Data Scientists
- Training pipeline
- Evaluation metrics
- Model management
- Experiment tracking

---

## 🔍 Finding More Information

| Need | Resource |
|------|----------|
| System overview | [System Overview](./architecture/system_overview.md) |
| Component details | [Consolidated Architecture](./architecture/ARCHITECTURE_CONSOLIDATED.md) |
| Configuration | [Hydra Guide](./configuration/HYDRA_GUIDE.md) |
| Deployment | [Deployment Guide](./deployment/) |
| API usage | [API Reference](./API_REFERENCE.md) |
| Development | [Contributing](./contributing/) |

---

## 🚀 Quick Start Links

- **Setup**: [Installation Guide](./setup/)
- **Configuration**: [Quick Start](./configuration/hydra_quickstart.md)
- **Running**: [How to Run](./how-to/)
- **Troubleshooting**: [FAQ](./troubleshooting/)

---

**Status**: ✅ Complete  
**Consolidated Date**: 2026-06-22  
**For Updates**: See [Consolidated Architecture](./architecture/ARCHITECTURE_CONSOLIDATED.md)
