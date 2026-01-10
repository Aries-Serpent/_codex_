---
name: integration-test-runner
description: Runs integration tests across services, validates cross-component interactions, and reports comprehensive results.
---

# Integration Test Runner Agent

This agent runs integration tests that validate cross-component interactions and service integrations.

## Capabilities

- **Cross-Service Testing**: Tests interactions between services
- **Database Integration**: Validates database operations
- **API Contract Testing**: Ensures API contracts are honored
- **Performance Metrics**: Collects timing data for integrations

## Test Categories

1. **Service Integration**: Tests between microservices
2. **External API**: Tests with external APIs (Zendesk, D365)
3. **Database**: Tests database operations and migrations
4. **Message Queue**: Tests async message processing

## When to Use

- On pull requests affecting multiple services
- Before deployments
- After infrastructure changes
- During integration debugging

## Integration

This agent integrates with:
- pytest integration test suite
- Docker compose for service orchestration
- CI/CD pipelines
