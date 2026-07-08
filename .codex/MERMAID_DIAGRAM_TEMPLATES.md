# Mermaid Diagram Templates for _codex_ Documentation

**Version:** 1.0  
**Created:** 2026-07-08  
**Purpose:** Reusable templates for common documentation diagrams

---

## 1. Architecture Diagram Template

Use for system components and data flow:

```mermaid
graph LR
    subgraph Client["Client Layer"]
        UI["Web UI"]
        API["REST API Client"]
    end
    
    subgraph Server["Server Layer"]
        Gateway["API Gateway"]
        Service["Business Logic"]
    end
    
    subgraph Data["Data Layer"]
        Cache["Redis Cache"]
        DB["PostgreSQL"]
    end
    
    UI -->|Requests| API
    API -->|HTTP| Gateway
    Gateway -->|Routes| Service
    Service -->|Check Cache| Cache
    Service -->|Query| DB
    DB -->|Results| Service
    Service -->|Update Cache| Cache
    
    style Client fill:#e1f5ff
    style Server fill:#f3e5f5
    style Data fill:#e8f5e9
```

**When to use:** System architecture, component relationships, data flow

**Customization:**
- Replace `Client`, `Server`, `Data` with your layers
- Add/remove components as needed
- Adjust colors (lighter = `fill:#` code, darker = `stroke:#` code)

---

## 2. Process Workflow Template

Use for step-by-step procedures:

```mermaid
flowchart TD
    Start([User Action]) --> Step1["Step 1: Initialize"]
    Step1 --> Check1{Decision Point?}
    
    Check1 -->|Path A| Step2A["Step 2A: Process A"]
    Check1 -->|Path B| Step2B["Step 2B: Process B"]
    
    Step2A --> Step3["Step 3: Consolidate"]
    Step2B --> Step3
    
    Step3 --> Check2{Success?}
    Check2 -->|Yes| End1([Complete])
    Check2 -->|No| Error["Error Handling"]
    Error --> End2([Failure])
    
    style Start fill:#c8e6c9
    style End1 fill:#c8e6c9
    style End2 fill:#ffcdd2
    style Error fill:#ffcdd2
```

**When to use:** Deployment pipelines, approval workflows, decision trees

**Customization:**
- Add steps: `StepN["Description"]`
- Add decisions: `Decision{Question?}`
- Chain with `-->`
- Use `style` for highlighting important nodes

---

## 3. Entity Relationship Diagram Template

Use for database schemas:

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : owns
    USERS ||--o{ API_KEYS : has
    PROJECTS ||--o{ DATASETS : contains
    PROJECTS ||--o{ MODELS : trains
    DATASETS ||--o{ FEATURES : includes
    MODELS ||--o{ PREDICTIONS : generates
    
    USERS {
        int user_id PK
        string email UK
        string name
        timestamp created_at
    }
    
    PROJECTS {
        int project_id PK
        int user_id FK
        string name
        text description
        timestamp updated_at
    }
    
    DATASETS {
        int dataset_id PK
        int project_id FK
        string name
        int record_count
        float size_gb
    }
    
    MODELS {
        int model_id PK
        int project_id FK
        string architecture
        float accuracy
        timestamp trained_at
    }
```

**When to use:** Database schemas, data models, relationship documentation

**Customization:**
- `ENTITY_NAME` — Table name (UPPERCASE)
- `PK` — Primary key
- `FK` — Foreign key
- `UK` — Unique key
- `||--o{` — One-to-many relationship
- `||--||` — One-to-one relationship

---

## 4. Sequence Diagram Template

Use for interactions over time:

```mermaid
sequenceDiagram
    participant User as User
    participant Client as Web Client
    participant API as REST API
    participant Service as Service
    participant DB as Database
    
    User->>Client: Submit Form
    Client->>API: POST /api/resource
    activate API
    
    API->>Service: Validate Input
    activate Service
    Service-->>API: Valid
    deactivate Service
    
    API->>DB: INSERT record
    activate DB
    DB-->>API: Success + ID
    deactivate DB
    
    API-->>Client: 201 Created
    deactivate API
    
    Client-->>User: Confirm Success
```

**When to use:** API interactions, authentication flows, request/response sequences

**Customization:**
- `participant Name as Label`
- `->>` — Arrow (request)
- `-->>` — Dotted arrow (response)
- `activate` / `deactivate` — Show processing time
- `alt` — Alternative paths

---

## 5. Timeline Diagram Template

Use for project phases and milestones:

```mermaid
timeline
    title _codex_ Development Timeline
    
    section 2025
        Q1 2025: Planning, Requirements gathering
        Q2 2025: MVP Development, Initial testing
        Q3 2025: Beta Release, Feature expansion
        Q4 2025: Production Release, Documentation
    
    section 2026
        Q1 2026: Performance Optimization, User feedback
        Q2 2026: Advanced Features, Integration work
        Q3 2026: Scale Testing, Stability improvements
        Q4 2026: Q4 Release, Planning 2027
```

**When to use:** Project roadmaps, release timelines, historical evolution

**Customization:**
- Add/remove milestones
- Group into sections with `section Name`
- Keep descriptions concise

---

## 6. State Diagram Template

Use for state machines and workflows:

```mermaid
stateDiagram-v2
    [*] --> Ready
    
    Ready --> Processing: User initiates
    Processing --> Validating: Input submitted
    Validating --> Processing: Validation failed
    Validating --> Executing: Validation passed
    
    Executing --> Success: Completed
    Executing --> Error: Exception occurred
    
    Success --> [*]
    Error --> Retry: Retry?
    Retry --> Processing
    Retry --> [*]
    
    note right of Processing
        User can cancel
        at this stage
    end note
```

**When to use:** State machines, status workflows, user journey stages

**Customization:**
- States are simple nodes
- `[*]` — Start/end states
- Add notes with `note right/left of State`
- Conditions on arrows

---

## 7. Class Diagram Template

Use for object-oriented design:

```mermaid
classDiagram
    class DataProcessor {
        -data: List
        -config: Config
        +__init__(config)
        +load_data(path)*
        +validate()*
        +transform(): Result
        +save(path)
    }
    
    class CSVProcessor {
        +load_data(path): bool
        +validate(): bool
    }
    
    class JSONProcessor {
        +load_data(path): bool
        +validate(): bool
    }
    
    class Result {
        -records: int
        -status: str
        +get_summary(): str
    }
    
    DataProcessor <|-- CSVProcessor
    DataProcessor <|-- JSONProcessor
    DataProcessor --> Result
```

**When to use:** Object-oriented designs, inheritance hierarchies, class relationships

**Customization:**
- `-` for private properties
- `+` for public properties
- `*` for abstract methods
- `<|--` for inheritance
- `-->` for dependency

---

## 8. Pie Chart Template

Use for composition or distribution:

```mermaid
pie title Code Distribution in _codex_
    "Python" : 45
    "YAML" : 25
    "Markdown" : 20
    "JavaScript" : 10
```

**When to use:** Resource allocation, code composition, time distribution

**Customization:**
- Add/remove categories
- Adjust percentages (must sum to 100)

---

## 9. Gantt Chart Template

Use for project scheduling:

```mermaid
gantt
    title Phase 12 WS3 Documentation Timeline
    dateFormat YYYY-MM-DD
    
    section Phase 1
    Style Guide Development :phase1_1, 2026-07-08, 14d
    Quality Assessment :phase1_2, 2026-07-08, 10d
    
    section Phase 2
    Markdown Standardization :crit, phase2_1, 2026-07-15, 20d
    Readability Enhancement :phase2_2, 2026-07-20, 15d
    
    section Phase 3
    Diagram Creation :phase3_1, 2026-07-30, 14d
    Visual Polish :phase3_2, 2026-08-05, 10d
    
    section Phase 4
    Integration & Automation :phase4_1, 2026-08-10, 10d
    Final Validation :phase4_2, 2026-08-15, 7d
```

**When to use:** Project timelines, task scheduling, dependency visualization

**Customization:**
- `crit` — Critical path (red)
- `done` — Completed (green)
- Dates in `YYYY-MM-DD` format
- Adjust duration numbers

---

## 10. Git Branching Diagram Template

Use for version control workflows:

```mermaid
gitGraph
    commit id: "Initial commit"
    branch feature/auth
    checkout feature/auth
    commit id: "Add JWT support"
    commit id: "Add refresh tokens"
    
    checkout main
    branch release/1.0
    checkout release/1.0
    commit id: "v1.0.0"
    
    checkout main
    merge release/1.0
    
    checkout feature/auth
    commit id: "Add 2FA"
    checkout main
    merge feature/auth
    commit id: "v1.1.0"
```

**When to use:** Git workflows, branching strategies, release processes

**Customization:**
- `branch name` — Create new branch
- `checkout name` — Switch to branch
- `merge name` — Merge branch
- `commit id: "message"` — Log commit

---

## Best Practices for Diagrams

### Do ✅

- Keep diagrams focused on one concept
- Use consistent colors across related diagrams
- Add titles and labels
- Test rendering in your documentation build
- Include explanatory text before/after diagram
- Use simple, clear language in labels

### Don't ❌

- Overcomplicate with too many nodes
- Mix multiple unrelated concepts
- Use inconsistent styling
- Forget to test the diagram syntax
- Leave diagrams without context
- Assume readers will understand without explanation

### Integration Example

```markdown
## Our Architecture

The _codex_ system has three main layers:

```mermaid
graph LR
    Client["Client Layer"]
    Server["Server Layer"]
    Data["Data Layer"]
    
    Client -->|API| Server
    Server -->|Query| Data
    
    style Client fill:#e1f5ff
    style Server fill:#f3e5f5
    style Data fill:#e8f5e9
```

**Client Layer** handles user interface and requests.

**Server Layer** processes business logic.

**Data Layer** manages persistence and caching.
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Diagram not rendering | Syntax error | Validate with `mermaid live editor` |
| Text wrapping awkwardly | Long labels | Shorten or use multi-line with `\|` |
| Colors not showing | Invalid color code | Use `fill:#hexcode` or named colors |
| Arrows pointing wrong | Wrong syntax | Use `-->` not `->` or `>` |
| Diagram too large | Too many nodes | Split into multiple diagrams |

---

## Resources

- [Mermaid Official Docs](https://mermaid.js.org)
- [Mermaid Live Editor](https://mermaid.live)
- [_codex_ Style Guide](./../.codex/DOCUMENTATION_STYLE_GUIDE.md)

---

*Keep these templates in mind when adding diagrams to documentation. Good diagrams make complex ideas easy to understand!*
