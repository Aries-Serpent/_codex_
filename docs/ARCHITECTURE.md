# Architecture

`_codex_` combines an ML platform, repository automation, and a persistent
decision-and-learning layer. New Python implementation lives under `src/`; application,
configuration, test, documentation, and operational layers surround that boundary.

## Start with the right map

- [Repository map](REPOSITORY_MAP.md) provides the concise directory-level orientation.
- [Repository explanation](REPOSITORY_EXPLANATION.md) describes the evidence-based
  five-layer architecture and component maturity.
- [Cognitive map](system/CODEBASE_COGNITIVE_MAP.md) focuses on cognitive, agent, ML,
  MCP, and delivery relationships.
- [Workflow map](WORKFLOW_MAP.md) explains CI, security, coverage, self-healing, and
  governance entry points.
- [Session-state guide](SESSION_STATE_GUIDE.md) explains the operational intelligence
  that carries evidence and learning between agent sessions.

Use source, package manifests, and active workflow definitions as implementation
authority. Treat dated reports and generated inventories as evidence for the state they
recorded.
