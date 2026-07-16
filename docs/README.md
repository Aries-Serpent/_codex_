# _codex_ Documentation
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-07-08
**Audience:** Developers, DevOps, Admins 
**Related:** [Master Index](MASTER_INDEX.md), [Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md)

---

## Overview

Complete documentation for the _codex_ AI/ML platform. Find guides, API references, architecture diagrams, and operational runbooks organized by role.

---

## Quick Navigation by Role

### ‍ **Developers**
1. **Get started:** [Quickstart Guide](getting-started.md)
2. **Understand the system:** [Architecture Quick Reference](ARCHITECTURE_QUICK_REFERENCE.md)
3. **Code & test:** [Contributing Guidelines](CONTRIBUTING.md), [Testing Guide](TESTING.md)
4. **Integrate:** [API Reference](API_REFERENCE.md), [CLI Guide](./api/cli.md)

### **DevOps & Operations**
1. **Deploy:** [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. **Configure:** [Configuration Guide](CONFIGURATION_GUIDE.md)
3. **Troubleshoot:** [Troubleshooting Guide](TROUBLESHOOTING.md)
4. **Manage:** [Admin Guide](admin/INDEX.md)

### **Security & Compliance**
1. **Review policies:** [Security Guide](SECURITY.md)
2. **Understand governance:** [Governance Guide](admin/GOVERNANCE.md)
3. **Manage access:** [Token Management](tokens/INDEX.md)

---

## Documentation Structure

## Getting Started
- [Quickstart Guide](getting-started.md) — Get running in 5 minutes
- [Installation](setup/environment.md) — Detailed setup instructions
- [Contributing](CONTRIBUTING.md) — Contribute to the project

### User Guides
- [CLI Usage](./api/cli.md) — Command-line interface guide
- **API Documentation** — Complete API reference (NEW!)
 - [API Documentation Index](API_DOCUMENTATION_INDEX.md) — Start here
 - [Core API Reference](CORE_API_REFERENCE.md) — CLI, training, utilities
 - [Quantum Orchestration API](QUANTUM_ORCHESTRATION_API.md) — Physics-inspired orchestration
 - [Storage & Archive API](STORAGE_API.md) — Data persistence & retrieval
 - [Integration & GitHub API](INTEGRATION_API.md) — GitHub, auth, tokens
 - [ML Inference API](ML_INFERENCE_API.md) — ML validation & integration
 - [Governance & Memory API](GOVERNANCE_API.md) — RBAC, memory, approval workflows
- [Configuration](CONFIGURATION_GUIDE.md) — Configuration management

### Architecture & Design
- [Quick Reference](ARCHITECTURE_QUICK_REFERENCE.md) — System overview (1-page)
- [Full Architecture](ARCHITECTURE_BLUEPRINT.md) — Detailed design (complete reference)
- [Design Decisions](adr/000-mcp-architecture.md) — Architecture decision records

### Operations & Administration
- [Admin Guide](admin/INDEX.md) — Administration and operations
- [Security Policies](SECURITY.md) — Security requirements and procedures
- [Governance Model](admin/GOVERNANCE.md) — Project governance

### Development
- [Development Guide](DEVELOPMENT.md) — Contributing to the codebase
- [Testing Strategy](TESTING.md) — Testing guidelines
- [CI/CD Pipelines](development/ci_optimization_guide.md) — Continuous integration

### Templates & Patterns
- [Operational Templates](templates/README.md) — Reusable templates:
 - Migration — Python File Relocation
 - Migration — CLI Hardening
 - Planning — Intent Validation

### Advanced Topics
- [RAG Integration](EXPANDED_CONTEXT_RAG.md) — Retrieval-augmented generation
- [Distributed Training](distributed_training_guide.md) — Multi-node training
- [Performance Optimization](PERFORMANCE_OPTIMIZATION_GUIDE.md) — Optimization techniques

---

## Additional Indexes & Resources

- [Master Index](MASTER_INDEX.md) — Complete documentation index (all 1,900+ files)
- [Documentation Index](DOCUMENTATION_INDEX.md) — Documents organized by topic
- [Archive](archive/INDEX.md) — Archived and deprecated documentation
- [Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md) — Documentation standards
- [Quality Report](DOCUMENTATION_QUALITY_REPORT.md) — Quality metrics and improvements

---

## How to Find What You Need

### By Task

| Task | Start Here |
|------|-----------|
| Deploy to production | [Deployment Guide](DEPLOYMENT_GUIDE.md) |
| Set up development environment | [Getting Started](getting-started.md) |
| Troubleshoot an issue | [Troubleshooting Guide](TROUBLESHOOTING.md) |
| Review security requirements | [Security Guide](SECURITY.md) |
| Integrate with APIs | [API Reference](API_REFERENCE.md) |
| Configure system behavior | [Configuration Guide](CONFIGURATION_GUIDE.md) |
| Understand architecture | [Architecture Guide](ARCHITECTURE_BLUEPRINT.md) |
| Test your changes | [Testing Guide](TESTING.md) |

### By Experience Level

- **New to _codex_?** → [Quickstart Guide](getting-started.md)
- **Contributing code?** → [Contributing Guide](CONTRIBUTING.md)
- **Running in production?** → [Admin Guide](admin/INDEX.md)
- **Optimizing performance?** → [Performance Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- **Building integrations?** → [API Reference](API_REFERENCE.md)

---

## External Resources

- [GitHub Repository](https://github.com/Aries-Serpent/_codex_)
- [Issue Tracker](https://github.com/Aries-Serpent/_codex_/issues)
- [Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- [Release Notes](CHANGELOG.md)

---

## Documentation Maintenance

This documentation is actively maintained by the _codex_ team and automated agents.

### Report Issues

Found an error or outdated information?
- **Errors:** [Open an issue](https://github.com/Aries-Serpent/_codex_/issues/new)
- **Missing docs:** Check [Gap Analysis](DOCUMENTATION_GAP_ANALYSIS.json)
- **Style questions:** See [Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md)

### Contribute

Improve the documentation:
1. Read [Contributing Guidelines](CONTRIBUTING.md)
2. Follow [Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md)
3. Test your changes locally with `mkdocs build --strict`
4. Submit a pull request

### Documentation Standards

All documentation follows these standards:
- Single H1 title per page
- Metadata header (Last Updated, Audience)
- Clear, active voice
- Working code examples
- Proper heading hierarchy
- Relative links for internal docs
- 13-point quality checklist
- Updated every 6 months

See [Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md) for full standards.

---

**Last Updated**: 2026-01-26
**Maintained By**: _codex_ team and autonomous agents
