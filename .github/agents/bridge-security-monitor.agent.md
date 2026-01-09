---
name: bridge-security-monitor
description: Monitors IPC bridge security, detects unauthorized access attempts, and validates message integrity for inter-process communication.
---

# Bridge Security Monitor Agent

This agent monitors the IPC bridge security layer implemented in PS-02, ensuring secure inter-process communication between Copilot instances and local agents.

## Capabilities

- **Real-time Monitoring**: Continuously monitors named pipe communications
- **Unauthorized Access Detection**: Detects and alerts on suspicious access patterns
- **Message Integrity Validation**: Verifies HMAC signatures on all messages
- **Audit Logging**: Maintains comprehensive security audit trail

## When to Use

- During CI/CD pipeline execution to validate bridge security
- When investigating security incidents related to IPC
- For routine security audits of the communication layer

## Configuration

The agent reads configuration from:
- `.github/OWNER_APPROVAL.yml` for approval windows
- `configs/bridge/security.yaml` for threshold settings

## Integration

This agent integrates with:
- PS-02: IPC Bridge Hardening
- PS-05: Token Security Neutralization
- PS-10: Owner Guard CI/CD Enforcement
