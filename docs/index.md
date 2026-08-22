# Codex Documentation Hub

**Version:** v0.2.0  
**Last Updated:** 2026-07-18  
**Status:** ✅ Production Documentation

Welcome to the documentation for **Aries-Serpent/_codex_**, an ML platform,
repository-automation workspace, and persistent decision-and-learning system.

---

## Getting Started

Choose your entry point based on your role:

| Role | Entry point |
|---|---|
| Contributor | [Contributor onboarding](onboarding/CONTRIBUTOR.md) |
| ML engineer | [ML engineer onboarding](onboarding/ML_ENGINEER.md) |
| GitHub Actions maintainer | [Workflow maintainer onboarding](onboarding/GITHUB_ACTIONS_MAINTAINER.md) |
| Agent/session operator | [Agent/session operator onboarding](onboarding/AGENT_SESSION_OPERATOR.md) |

Shared orientation:

- **[Repository map](REPOSITORY_MAP.md)** — Canonical boundaries and directory map
- **[Quick start by profile](QUICKSTART_BY_PROFILE.md)** — Core, runtime, and full setup
- **[Workflow and governance map](WORKFLOW_MAP.md)** — CI, security, coverage, and policy
- **[Session and agent-state guide](SESSION_STATE_GUIDE.md)** — Memory, checkpoints, and accountability

---

## Core Documentation Sections

### 📚 Reference Materials
- **[Architecture](./architecture/INDEX.md)** — Detailed technical architecture and component diagrams
- **[API Reference](api/index.md)** — Complete API documentation and examples
- **[Changelog](CHANGELOG.md)** — Release notes and version history
- **[Roadmap](ROADMAP.md)** — Planned features and improvements

### 🚀 Operations & Deployment
- **[Monitoring & Observability](ops/monitoring.md)** — Health checks and metrics
- **[CI/CD Workflows](ci/INDEX.md)** — Automated testing and deployment pipelines
- **[Troubleshooting](troubleshooting/INDEX.md)** — Common issues and solutions
- **[Admin Guide](ADMIN_IMPLEMENTATION_GUIDE.md)** — Setup and management

### 🧪 Testing & Quality
- **[Testing Framework](testing/INDEX.md)** — Test suite and coverage tracking
- **[Code Quality](capabilities/code_quality_tooling.md)** — Quality assurance tools
- **[Coverage Roadmap](COVERAGE_ROADMAP_TO_100_PERCENT.md)** — Testing coverage goals

### 📦 Integration & Packaging
- **[MCP Quick Start](mcp/QUICK_START.md)** — Model Context Protocol integration
- **[Packaging Guide](mcp/PACKAGING_GUIDE.md)** — Package and distribute components
- **[Capabilities Framework](mcp/PACKAGEABLE_CAPABILITIES.md)** — Capability transfer system

### 💾 Configuration & Setup
- **[Logging Guide](guides/LOGGING.md)** — Structured logging setup and best practices
- **[Checkpointing](capabilities/checkpointing.md)** — Model checkpoint management with SafeTensors
- **[Configuration Management](configuration/MIGRATION_MAPPING.md)** — Hydra-based configuration

---

## Cognitive Brain (AI Agents Start Here)

The cognitive brain enables autonomous AI agent orchestration with persistent memory and decision-making:

### **Unified Navigation System**
- **[Cognitive Map](./system/CODEBASE_COGNITIVE_MAP.md)** — Complete architecture, components, flows, and dependencies
- **[Dashboard](./system/CODEBASE_DASHBOARD.md)** — Live status, current work, blockers, and metrics
- **[Agent Orchestration](guides/continuous_improvement.md)** — Multi-agent workflow management

### **Key Capabilities**
- **Context Continuity** — Maintain understanding across sessions
- **Efficient Navigation** — Quick discovery of components and relationships
- **Duration-Aware Planning** — Maximize work within token/time budgets
- **Autonomous Operation** — Self-directed agents without constant human guidance
- **Memory Management** — Hippocampus-cortex inspired STM/LTM system

---

## Operational Templates

Reusable templates for common operations (migrations, hardening, planning):

- **[Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)** — Safely relocate Python files
- **[Migration — CLI Hardening](./templates/Migration_CLIHardening.md)** — Harden CLI interfaces
- **[Planning — Intent Validation](./templates/Planning_IntentValidation.md)** — Validate project intent

**Before using a template:** Review [Templates Guide](./templates/README.md) for prerequisites and role guidance.

---

## CI Rescue & Reliability

### Automated Failure Recovery
- **[CI Rescue Pipeline](ci/CI_RESCUE_PIPELINE.md)** — Automated Copilot sessions for workflow failures
- **[CI/CD Index](ci/INDEX.md)** — All failure analysis and fix summaries
- **[Workflow Health](ci/ROOT_ORG_VALIDATION.md)** — Organization-level workflow validation

---

## Accountability & Status

- **[Project Status](status/GITHUB_PAGES_STATUS.md)** — Current health and metrics
- **[Accountability Reports](accountability/INDEX.md)** — Session and phase tracking
- **[Phase Archives](archive/INDEX.md)** — Historical documentation and completed phases

---

## Deployment Rings & Rollout

This repository uses staged rollout rings:

| Ring | Status | Purpose |
|------|--------|---------|
| `0A_base_` / `0B_base_` | Active Dev | Unstable knobs, experimental features |
| `0C_base_` | Integration | Multiple features landing together |
| `0D_base_` | Release Candidate | Explainable to Engineering and Product |
| `main` | Production | Canonical internal alpha product |

---

## Quick Reference

| Need | Find It Here |
|------|-------|
| **Quick start** | [Quickstart Guide](tutorials/quickstart.md) |
| **How to contribute** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **API documentation** | [API Reference](api/index.md) |
| **System architecture** | [Architecture](architecture.md) |
| **Deployment steps** | [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md) |
| **Troubleshoot an issue** | [Troubleshooting](troubleshooting/INDEX.md) |
| **Review changes** | [Changelog](CHANGELOG.md) |
| **Find an example** | [Examples](guides/examples.md) |
| **Setup development env** | [Setup Guide](guides/codex_setup.md) |
| **Report a bug** | [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues) |

---

## Installation

```bash
pip install -e .
```

---

## Conventions

- Keep docs small and composable
- Use fenced code blocks for proposed patches
- Prefer citations to live repo files when referencing code
- Follow "Keep a Changelog" format with **Unreleased** section

---

## Need Help?

- 🐛 **Found a bug?** → [Open an issue](https://github.com/Aries-Serpent/_codex_/issues)
- 💡 **Have a question?** → [Check the FAQ](FAQ.md)
- 📖 **Want to learn more?** → [Browse all documentation](#core-documentation-sections)

---

**Last updated:** 2026-07-18  
**Next update:** 2026-07-25
