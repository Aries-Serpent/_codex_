# Governance — _codex_

## Purpose

This document defines the governance structure, roles, and decision-making processes for the _codex_ project.

## Roles & Responsibilities

### Maintainers (@Aries-Serpent/architects)
- **Scope**: Overall technical direction, architecture decisions, security coordination
- **Responsibilities**:
  - Final approval on major architectural changes
  - Release planning and versioning
  - Security vulnerability coordination
  - ADR (Architecture Decision Record) approval
  - Breaking change decisions

### Core Teams

#### @Aries-Serpent/ml-core
- **Scope**: ML training, evaluation, model serving components
- **Responsibilities**:
  - Feature development and ownership in `src/codex_ml/`
  - Code reviews for ML-related changes
  - Performance optimization and benchmarking

#### @Aries-Serpent/app-core
- **Scope**: Core application logic, CLI, utilities
- **Responsibilities**:
  - Feature ownership in `src/codex/`
  - Code reviews for core functionality
  - API stability and backward compatibility

#### @Aries-Serpent/ops-team
- **Scope**: DevOps, CI/CD, infrastructure, deployment
- **Responsibilities**:
  - CI/CD pipeline maintenance
  - Docker and deployment configurations
  - Monitoring and observability setup
  - Release automation

#### @Aries-Serpent/docs-team
- **Scope**: Documentation, guides, examples
- **Responsibilities**:
  - Documentation standards and quality
  - Maintaining guides and tutorials
  - Example code and quickstarts
  - Search recipes and navigation aids

#### @Aries-Serpent/security
- **Scope**: Security posture, vulnerability response, threat modeling
- **Responsibilities**:
  - Security vulnerability triage and response
  - Dependency risk assessment
  - Security policy enforcement
  - Coordinated disclosure management

### Contributors
- Anyone who submits PRs, issues, or participates in discussions
- Subject to Code of Conduct
- Can become team members through sustained contribution

## Decision-Making Process

### Small Changes (Documentation, Bug Fixes, Minor Features)
- **Process**: Lazy consensus after 48 hours
- **Requirements**: 
  - One approving review from relevant CODEOWNERS
  - CI/tests passing
  - No objections from maintainers

### Medium Changes (New Features, Refactoring)
- **Process**: Standard review
- **Requirements**:
  - Two approving reviews from relevant CODEOWNERS
  - CI/tests passing
  - Documentation updated
  - CHANGELOG entry
  - 5 business days for review

### Major Changes (Breaking Changes, Architecture, Security)
- **Process**: RFC (Request for Comments) via ADR
- **Requirements**:
  - ADR document in `docs/decision_records/`
  - 5 business days + 2 weekend days for review
  - Approval from @Aries-Serpent/architects
  - Approval from affected team(s)
  - Migration guide (if breaking change)
  - CHANGELOG entry with upgrade notes

### Emergency Changes (Critical Security, Production Incidents)
- **Process**: Fast-track with post-hoc review
- **Requirements**:
  - One maintainer approval
  - Document in incident retrospective
  - Follow-up ADR if architectural impact

## Release Process

### Cadence
- **Patch releases**: Weekly (as needed for bug fixes)
- **Minor releases**: Monthly when feature-stable
- **Major releases**: Quarterly or as needed for breaking changes

### Release Checklist
1. CHANGELOG updated with all changes
2. Version bumped (SemVer)
3. All tests passing
4. Documentation updated
5. Migration guide (if breaking changes)
6. Security review (for major/minor)
7. Maintainer approval

### Versioning
We follow [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Conflict Resolution

### Escalation Path
1. **Reviewer level**: Code review discussion
2. **Team level**: Relevant CODEOWNERS team discussion
3. **Maintainer level**: @Aries-Serpent/architects decision
4. **Security liaison**: @Aries-Serpent/security (if security-related)

### Principles
- Assume good faith
- Focus on technical merits
- Document disagreements and resolutions
- Escalate early if consensus can't be reached

## Communication Channels

### Primary
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Q&A, proposals, community discussion
- **Pull Requests**: Code reviews, implementation discussion

### Secondary
- **Security**: security@aries-serpent.dev (private)
- **Conduct**: conduct@aries-serpent.dev (Code of Conduct violations)

## Becoming a Team Member

### Requirements
- Sustained contributions over 3+ months
- Deep knowledge of relevant codebase area
- Positive community interaction
- Adherence to Code of Conduct

### Process
1. Nomination by existing team member
2. Endorsement from another team member
3. One-week feedback period
4. Approval by @Aries-Serpent/architects
5. Addition to relevant team(s)

## Code of Conduct

All participants must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Violations will be handled per the enforcement guidelines in that document.

## Changes to Governance

This governance document may be updated through the Major Changes process (ADR + maintainer approval). Historical changes are tracked via git commits.

---

**Version**: 1.0  
**Last Updated**: 2025-11-02  
**Contact**: @Aries-Serpent/architects
