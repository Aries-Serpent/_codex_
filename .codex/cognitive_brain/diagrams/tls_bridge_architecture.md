# TLS Bridge Architecture

## Overview

This diagram illustrates the secure TLS bridge architecture for cross-machine cognitive-copilot communication using Bridge Protocol v2.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Machine"
        CA[Copilot Agent]
        CC[Client Certificate]
        TCC[TLS Client Context]
    end
    
    subgraph "Bridge Layer"
        BP[Bridge Protocol v2]
        MC[Message Compression]
        MF[Message Flags]
        CH[Checksum/CRC32]
    end
    
    subgraph "Server Machine (Cognitive Brain)"
        TLS[TLS Server<br/>Mutual TLS]
        MCB[Multi-Client Bridge]
        OR[Orchestrator]
        KB[Knowledge Base]
    end
    
    subgraph "Security Layer"
        PKI[Mini-PKI<br/>Certificate Authority]
        CR[Cert Rotation]
        SC[Scope Validator]
    end
    
    CA -->|Request| TCC
    TCC -->|Encrypted| BP
    BP -->|Compress if >100KB| MC
    MC -->|Add Header| MF
    MF -->|Add Checksum| CH
    CH -->|TLS Handshake| TLS
    
    TLS -->|Verify Client Cert| PKI
    TLS -->|Route Message| MCB
    MCB -->|Priority/RR| OR
    OR -->|Query| KB
    
    PKI -->|Issue Ephemeral| CC
    PKI -->|Auto-Rotate| CR
    OR -->|Validate Scopes| SC
    
    KB -->|Response| OR
    OR -->|Route| MCB
    MCB -->|Compress| BP
    BP -->|Encrypt| TLS
    TLS -->|Send| TCC
    TCC -->|Decrypt| CA
    
    style TLS fill:#f96,stroke:#333,stroke-width:3px
    style PKI fill:#9cf,stroke:#333,stroke-width:2px
    style SC fill:#fc9,stroke:#333,stroke-width:2px
    style BP fill:#9f9,stroke:#333,stroke-width:2px
```

## Communication Flow

### 1. Client → Server (Request)

1. **Copilot Agent** initiates request
2. **TLS Client Context** establishes encrypted connection
3. **Bridge Protocol v2** encodes message:
   - Checks payload size (>100KB triggers compression)
   - Adds protocol header (magic, version, flags, length)
   - Computes CRC32 checksum
4. **TLS Handshake** with mutual authentication
5. **Multi-Client Bridge** routes based on priority/round-robin
6. **Scope Validator** checks token permissions
7. **Orchestrator** processes request

### 2. Server → Client (Response)

1. **Orchestrator** generates response
2. **Bridge Protocol v2** encodes (compression if needed)
3. **TLS Layer** encrypts and sends
4. **Client** receives, decrypts, and decodes

## References

- **Implementation**: `src/bridge_protocol_v2.py`, `src/bridge_manager.py`
- **TLS Config**: `src/security/tls_config.py`
- **Tests**: `tests/test_bridge_protocol_v2.py`
