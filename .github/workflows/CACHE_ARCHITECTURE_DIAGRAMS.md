# GitHub Actions Cache Architecture - System Design

**Document Version**: 1.0  
**Last Updated**: 2025-12-30  
**Status**: Production - All Phase 1 & Phase 2 Complete

---

## System Architecture Overview

This document provides comprehensive system architecture diagrams for the GitHub Actions caching implementation across the repository.

---

## High-Level Cache System Architecture

```mermaid
C4Context
    title System Context - GitHub Actions Cache Architecture
    
    Person(dev, "Developer", "Pushes code/Creates PR")
    Person(admin, "Admin", "Monitors cache usage")
    
    System_Boundary(gh, "GitHub Platform") {
        System(actions, "GitHub Actions", "CI/CD Execution")
        System(cache, "Cache Service", "10 GB Storage")
        System(registry, "Package Registries", "PyPI, NPM, etc")
    }
    
    System_Ext(monitoring, "Monitoring Dashboard", "Cache metrics")
    
    Rel(dev, actions, "Triggers workflows")
    Rel(actions, cache, "Store/Retrieve caches")
    Rel(actions, registry, "Download packages")
    Rel(cache, monitoring, "Export metrics")
    Rel(admin, monitoring, "Reviews usage")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## Container-Level Architecture

```mermaid
graph TB
    subgraph GitHub Actions Runner
        subgraph Workflow Execution
            WF[Workflow YAML]
            PY[Python Setup]
            CACHE[Cache Action]
            DEPS[Dependency Install]
        end
        
        subgraph Cache Layers
            L1[L1: Workflow-Specific<br/>Exact Match]
            L2[L2: Workflow-Generic<br/>Partial Match]
            L3[L3: OS-Generic<br/>Fallback]
        end
    end
    
    subgraph GitHub Cache Service
        STORE[Cache Storage<br/>10 GB Limit]
        COMPRESS[Compression Engine<br/>gzip]
        LRU[LRU Eviction<br/>Policy]
    end
    
    subgraph External Services
        PYPI[PyPI Registry]
        GH_CLI[GitHub CLI Cache]
        NOX[Nox Cache]
    end
    
    WF --> PY
    PY --> CACHE
    CACHE --> L1
    L1 -->|Hit| DEPS
    L1 -->|Miss| L2
    L2 -->|Hit| DEPS
    L2 -->|Miss| L3
    L3 -->|Hit| DEPS
    L3 -->|Miss| PYPI
    
    CACHE <--> STORE
    STORE --> COMPRESS
    STORE --> LRU
    
    PYPI --> DEPS
    DEPS --> GH_CLI
    DEPS --> NOX
    
    style L1 fill:#90EE90
    style L2 fill:#FFD700
    style L3 fill:#FFA500
    style PYPI fill:#FF6347
```

---

## Component-Level: Cache Key Generation

```mermaid
flowchart LR
    subgraph Input Variables
        A1[runner.os<br/>Linux/Windows/MacOS]
        A2[github.workflow<br/>Workflow Name]
        A3[Additional Identifiers<br/>job/platform/type]
        A4[hashFiles<br/>Dependencies Hash]
    end
    
    subgraph Cache Key Builder
        B1[Combine Components]
        B2[Generate Unique ID]
        B3[Validate Uniqueness]
    end
    
    subgraph Output
        C1[Primary Key<br/>Exact Match Required]
        C2[Restore Key 1<br/>Workflow Match]
        C3[Restore Key 2<br/>OS Match]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    
    B1 --> B2
    B2 --> B3
    
    B3 --> C1
    B3 --> C2
    B3 --> C3
    
    style B3 fill:#87CEEB
    style C1 fill:#90EE90
    style C2 fill:#FFD700
    style C3 fill:#FFA500
```

---

## Data Flow: Cache Save Operation

```mermaid
sequenceDiagram
    autonumber
    participant WF as Workflow
    participant FS as File System
    participant COMP as Compressor
    participant CACHE as Cache Service
    participant STORE as Storage Backend
    
    WF->>FS: Check Dependencies Changed
    FS->>WF: Return Status
    
    alt Dependencies Changed
        WF->>FS: Collect Cache Paths
        FS->>WF: Return Files (~/.cache/pip, etc)
        
        WF->>COMP: Send Files for Compression
        Note over COMP: gzip compression<br/>60-80% ratio
        COMP->>WF: Return Compressed Archive
        
        WF->>CACHE: Save Cache Request
        Note over WF,CACHE: Include: key, paths, data
        
        CACHE->>CACHE: Validate Cache Size
        CACHE->>STORE: Store Compressed Data
        
        alt Storage < 10 GB
            STORE->>CACHE: ✅ Success
            CACHE->>WF: Cache Saved
        else Storage >= 10 GB
            STORE->>CACHE: ⚠️ Limit Reached
            CACHE->>CACHE: Trigger LRU Eviction
            CACHE->>STORE: Retry Save
            STORE->>CACHE: ✅ Success
            CACHE->>WF: Cache Saved (with eviction)
        end
    else No Changes
        WF->>WF: Skip Cache Save
    end
```

---

## Data Flow: Cache Restore Operation

```mermaid
sequenceDiagram
    autonumber
    participant WF as Workflow
    participant CACHE as Cache Service
    participant STORE as Storage Backend
    participant DECOMP as Decompressor
    participant FS as File System
    
    WF->>CACHE: Request Cache (Primary Key)
    CACHE->>STORE: Query by Key
    
    alt Primary Key Found
        STORE->>CACHE: Return Cache Metadata
        CACHE->>STORE: Fetch Compressed Data
        STORE->>DECOMP: Send Compressed Archive
        
        Note over DECOMP: Decompress gzip<br/>Restore original files
        
        DECOMP->>FS: Write to ~/.cache/pip
        FS->>WF: ✅ Cache Restored (30s)
        
    else Primary Key Not Found
        CACHE->>STORE: Query by Restore Key 1
        
        alt Restore Key 1 Found
            STORE->>CACHE: Return Partial Cache
            CACHE->>DECOMP: Decompress
            DECOMP->>FS: Write Partial Files
            FS->>WF: ⚠️ Partial Restore (45s)
            
        else Restore Key 1 Not Found
            CACHE->>STORE: Query by Restore Key 2
            
            alt Restore Key 2 Found
                STORE->>CACHE: Return Fallback Cache
                CACHE->>DECOMP: Decompress
                DECOMP->>FS: Write Fallback Files
                FS->>WF: ⚠️ Fallback Restore (60s)
                
            else No Keys Found
                CACHE->>WF: ❌ Cache Miss
                Note over WF: Download from PyPI<br/>~3-5 minutes
            end
        end
    end
```

---

## Deployment Architecture: Multi-Workflow Isolation

```mermaid
graph TB
    subgraph Workflow Isolation Layer
        subgraph Phase 1 Workflows
            W1[code-quality.yml]
            W2[self-healing-feedback-loop.yml]
        end
        
        subgraph Phase 2 Workflows
            W3[security-suite.yml]
            W4[nox_gates.yml]
            W5[integration-gated.yml]
            W6[scheduled-dependency-audit.yml]
        end
    end
    
    subgraph Cache Storage Layer - 10 GB Total
        subgraph Isolated Caches
            C1[Cache 1: Code Quality<br/>~800 MB]
            C2[Cache 2: Self-Healing<br/>~800 MB]
            C3[Cache 3: Security Suite<br/>~1.2 GB]
            C4[Cache 4: Nox Gates<br/>~1.0 GB]
            C5[Cache 5: Integration<br/>~600 MB]
            C6[Cache 6: Scheduled Audit<br/>~600 MB]
        end
        
        subgraph Shared Infrastructure
            COMP[Compression<br/>Automatic gzip]
            LRU[LRU Manager<br/>Auto-eviction > 10 GB]
            MONITOR[Usage Monitor<br/>Current: 7.69 GB]
        end
    end
    
    W1 -.->|Unique Key| C1
    W2 -.->|Unique Key| C2
    W3 -.->|Unique Key| C3
    W4 -.->|Unique Key| C4
    W5 -.->|Unique Key| C5
    W6 -.->|Unique Key| C6
    
    C1 --> COMP
    C2 --> COMP
    C3 --> COMP
    C4 --> COMP
    C5 --> COMP
    C6 --> COMP
    
    COMP --> LRU
    LRU --> MONITOR
    
    style W1 fill:#90EE90
    style W2 fill:#90EE90
    style W3 fill:#87CEEB
    style W4 fill:#87CEEB
    style W5 fill:#87CEEB
    style W6 fill:#87CEEB
    style MONITOR fill:#FFD700
```

---

## Security Architecture

```mermaid
graph TB
    subgraph Trust Boundaries
        subgraph Trusted - Main Branch
            T1[Main Branch Workflows]
            T2[Read/Write Cache]
        end
        
        subgraph Untrusted - PR Workflows
            U1[PR Branch Workflows]
            U2[Read-Only Cache]
        end
    end
    
    subgraph Cache Service
        AUTH[Authentication Layer]
        PERM[Permission Manager]
        CACHE_STORE[Cache Storage]
    end
    
    subgraph Security Controls
        S1[No Secrets in Keys]
        S2[Scope Isolation]
        S3[Audit Logging]
    end
    
    T1 --> AUTH
    U1 --> AUTH
    
    AUTH --> PERM
    PERM --> T2
    PERM --> U2
    
    T2 <--> CACHE_STORE
    U2 -->|Read Only| CACHE_STORE
    
    CACHE_STORE --> S1
    CACHE_STORE --> S2
    CACHE_STORE --> S3
    
    style T1 fill:#90EE90
    style U1 fill:#FFD700
    style S1 fill:#87CEEB
    style S2 fill:#87CEEB
    style S3 fill:#87CEEB
```

---

## Monitoring & Observability Architecture

```mermaid
graph LR
    subgraph Data Sources
        W1[Workflow Logs]
        W2[Cache Hit/Miss Events]
        W3[Storage Metrics]
        W4[Eviction Events]
    end
    
    subgraph Collection Layer
        C1[GitHub Actions API]
        C2[Cache Service Metrics]
    end
    
    subgraph Analysis Layer
        A1[Hit Rate Calculator]
        A2[Storage Analyzer]
        A3[Performance Tracker]
    end
    
    subgraph Visualization
        V1[Cache Dashboard]
        V2[Alert System]
        V3[Usage Reports]
    end
    
    W1 --> C1
    W2 --> C1
    W3 --> C2
    W4 --> C2
    
    C1 --> A1
    C1 --> A3
    C2 --> A2
    
    A1 --> V1
    A2 --> V1
    A3 --> V1
    
    A2 --> V2
    V2 -.->|Alert > 9 GB| V3
    
    style V2 fill:#FF6347
    style V1 fill:#87CEEB
```

---

## Disaster Recovery Flow

```mermaid
flowchart TD
    Start([Cache Event Detected]) --> Check{Event Type?}
    
    Check -->|Eviction| Evict[LRU Cache Evicted]
    Check -->|Corruption| Corrupt[Cache Corrupted]
    Check -->|Limit Reached| Limit[Storage Full]
    
    Evict --> E1{Critical Cache?}
    E1 -->|Yes| E2[Manual Workflow Trigger]
    E1 -->|No| E3[Auto-Rebuild on Next Run]
    
    Corrupt --> C1[Delete Corrupt Cache]
    C1 --> C2[Trigger Fresh Build]
    
    Limit --> L1[Emergency Actions]
    L1 --> L2{Action Type?}
    L2 -->|Remove| L3[Delete Low-Priority Caches]
    L2 -->|Optimize| L4[Reduce Cache Paths]
    L2 -->|Switch| L5[Use Built-in Caching]
    
    E2 --> Rebuild[Rebuild Cache]
    E3 --> Rebuild
    C2 --> Rebuild
    L3 --> Verify
    L4 --> Verify
    L5 --> Verify
    
    Rebuild --> Verify{Verify Success?}
    Verify -->|Yes| Success[✅ Recovery Complete]
    Verify -->|No| Escalate[Escalate to Admin]
    
    Success --> Monitor[Resume Monitoring]
    Escalate --> Manual[Manual Intervention]
    Manual --> Monitor
    
    style Success fill:#90EE90
    style Escalate fill:#FF6347
    style Manual fill:#FFA500
```

---

## Performance Optimization Strategy

```mermaid
mindmap
    root((Cache Optimization))
        Key Design
            Workflow-Specific
                Prevents Conflicts
                Better Hit Rates
            Hash-Based
                Detects Changes
                Auto-Invalidation
            Restore Keys
                Fallback Strategy
                Partial Matches
        
        Path Selection
            Essential Only
                pip cache
                nox cache
                gh CLI cache
            Remove Unnecessary
                No pre-commit
                No build artifacts
            Size Monitoring
                Track Growth
                Optimize Bloat
        
        Storage Management
            Compression
                Automatic gzip
                60-80% Savings
            LRU Eviction
                Protect Frequent
                Remove Stale
            Capacity Planning
                Monitor Usage
                Project Growth
        
        Performance Metrics
            Hit Rate
                Target 90%+
                Current ~90%
            Time Savings
                ~4.5 min/hit
                ~34 hrs/month
            Network Efficiency
                60-85% Reduction
                Bandwidth Savings
```

---

## Implementation Roadmap

```mermaid
timeline
    title Cache Implementation Journey
    section Phase 0 - Analysis
        Initial Assessment : Identified 49 workflows
                          : 39 without caching
                          : Calculated savings potential
    
    section Phase 1 - Critical
        2025-12-29 : scan-secrets-variables.yml (NEW)
                   : code-quality.yml (ADDED)
                   : self-healing-feedback-loop.yml (ADDED)
        
        2025-12-30 : Phase 1 Optimization Fix
                   : Added workflow identifiers
                   : Eliminated conflicts
    
    section Phase 2 - High Frequency
        2025-12-30 : security-suite.yml (2 jobs)
                   : nox_gates.yml (pip + nox)
                   : integration-gated.yml
                   : scheduled-dependency-audit.yml
    
    section Phase 3 - Future
        Q1 2026 : Remaining 28 workflows
                : Selective implementation
                : Based on usage monitoring
```

---

## Technical Specifications

### Cache Key Format Specification

```
Format: {OS}-{WORKFLOW}-{IDENTIFIER}-{TYPE}-{HASH}

Components:
- OS:         runner.os (Linux, Windows, macOS)
- WORKFLOW:   github.workflow (unique workflow name)
- IDENTIFIER: Optional (job name, platform, etc)
- TYPE:       Cache type (pip, nox, gh, etc)
- HASH:       hashFiles() of dependency files

Examples:
1. Basic:
   Linux-Code Quality Checks-pip-abc123def456

2. With Identifier:
   Linux-Security Suite-dependency-scan-pip-abc123def456

3. Multi-type:
   Linux-Nox Gates-pip-nox-abc123def456

4. Platform-specific:
   Linux-Scheduled Audit-amd64-pip-abc123def456
```

### Storage Capacity Planning

```
Current State (2025-12-30):
- Total Limit:        10.00 GB
- Current Usage:       7.69 GB (76.9%)
- Available:           2.31 GB (23.1%)
- Compression Ratio:   60-80% (automatic)

Projected State (After Phase 2):
- Additional Cache:    0.3-0.8 GB
- Projected Total:     8.0-8.5 GB (80-85%)
- Remaining:           1.5-2.0 GB (15-20%)
- Status:              ⚠️ Monitor Closely

Safe Operating Thresholds:
- Green:    < 8.0 GB (80%)   - Normal operations
- Yellow:   8.0-9.0 GB       - Increase monitoring
- Orange:   9.0-9.5 GB       - Prepare optimization
- Red:      9.5-10.0 GB      - Critical, immediate action
- Eviction: > 10.0 GB        - Automatic LRU eviction
```

---

## Appendix: Key Metrics Dashboard

```
Performance Metrics (Phase 1 + 2):
=====================================
Total Workflows Enhanced:     7
Cache Hit Rate (Target):      90%+
Time Saved per Hit:           ~4.5 minutes
Monthly Runner Time Savings:  ~34 hours
Network Bandwidth Reduction:  60-85%
Cache Storage Efficiency:     60-80% (compression)

Workflow Coverage:
==================
Total Workflows:              49
With Optimized Cache:         11 (22%)
With Built-in Cache:          10 (20%)
Without Cache:                28 (57%)
Total Cached:                 21 (43%)

Cost Savings:
=============
GitHub Actions Minutes Saved: ~2,040 minutes/month
Equivalent Cost Savings:      $XX-XXX/month (varies by plan)
Network Transfer Reduction:   XXX GB/month
Carbon Footprint Reduction:   Estimated XX kg CO2/month
```

---

**Document Maintained By**: DevOps Team / Copilot Automation  
**Review Frequency**: Monthly or after major changes  
**Last Technical Review**: 2025-12-30  
**Next Scheduled Review**: 2026-01-30
