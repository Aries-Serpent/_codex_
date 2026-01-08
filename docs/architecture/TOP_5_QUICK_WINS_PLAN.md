# Top 5 Quick Wins: Architectural Entropy Normalization Plan

**Date:** 2026-01-08  
**Branch:** `copilot/sub-pr-2750-one-more-time`  
**Context:** Addressing "Split Brain" state between legacy `agents/` and modern `src/codex/`  
**Goal:** Transform repository from collection of scripts into robust MLOps platform for SaaS workflow orchestration

---

## Executive Summary

This plan addresses the architectural entropy caused by the "Split Brain" state in the codebase, where legacy `agents/` directory and modern `src/codex/` implementations compete for authority. The 5 Quick Wins focus on establishing **Data Sovereignty** and **Schema Authority** through:

1. **Knowledge Crawler Service** - Dataset normalization
2. **Schema Authority** - Code normalization
3. **Configuration Consolidation** - Entropy reduction
4. **Bridge Hardening** - Security normalization
5. **Documentation Distillation** - Docs normalization

---

## Current State Analysis

### Architectural Issues

#### 1. Knowledge Entropy
- **Problem:** Ad-hoc scripts like `scripts/zendesk_docs_fetch.py` with stale caches in `data/zendesk_api_index.json`
- **Impact:** Agent trains on outdated SaaS documentation
- **Evidence:**
  ```bash
  $ find data/ -name "*zendesk*" -mtime +30
  data/zendesk_api_index.json  # Last modified: 2 months ago
  ```

#### 2. Code Split Brain
- **Problem:** Duplicate logic in `agents/zendesk_quantum_orchestrator.py` vs `src/codex/zendesk`
- **Impact:** Inconsistent behavior, hardcoded dictionaries, no validation
- **Evidence:**
  ```python
  # agents/zendesk_quantum_orchestrator.py (legacy)
  ticket_data = {"subject": "...", "priority": "urgent"}  # No validation!
  
  # src/codex/zendesk/ (modern, but incomplete)
  # Missing: Pydantic models, strict typing, validation
  ```

#### 3. Configuration Chaos
- **Problem:** Business logic in CSV files (`configs/deployment/d365/slas.csv`)
- **Impact:** Brittle, no validation, separate from code
- **Evidence:**
  ```csv
  priority,response_time_hours,resolution_time_hours
  urgent,1,4
  high,4,24
  ```

#### 4. Fragile Bridge
- **Problem:** `temp/bridge_codex_copilot_bridge` uses insecure sockets
- **Impact:** Potential unauthorized access to repro workflows
- **Evidence:** File-based IPC without authentication or encryption

#### 5. Documentation Drift
- **Problem:** Massive `docs/` folder, Agent needs concise instructions
- **Impact:** Hallucination due to stale documentation
- **Evidence:** 500+ markdown files, no automated digest pipeline

---

## Quick Win #1: Knowledge Crawler Service

### Objective
Transform ad-hoc fetching into a resident service with "Check and Pull" synchronization loop.

### Implementation Plan

#### Phase 1.1: Service Architecture (Pre-commit Cycle 1-2)

**File:** `src/services/crawler/zendesk_sync.py`

```python
"""
Knowledge Synchronization Service
Authority: Polls Zendesk Help Center APIs for article updates
Role: Ensures Agent's RAG is always aligned with external SaaS reality
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, UTC

from src.codex.utils import error_logging
from src.codex.ingest import adapter as ingest_adapter

# Configuration
DATA_INDEX_PATH = Path("data/zendesk_api_index.json")
SYNC_INTERVAL_SECONDS = 3600  # 1 Hour
ZENDESK_API_BASE = "https://{subdomain}.zendesk.com/api/v2/help_center"

class ZendeskSyncService:
    """Resident service for knowledge synchronization."""
    
    def __init__(self, subdomain: str, api_token: str):
        self.base_url = ZENDESK_API_BASE.format(subdomain=subdomain)
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("codex.services.crawler")
        self.local_index = self._load_local_index()
    
    def _load_local_index(self) -> Dict[str, str]:
        """Load local cache of article timestamps."""
        if not DATA_INDEX_PATH.exists():
            self.logger.warning(f"Index not found at {DATA_INDEX_PATH}. Starting fresh.")
            return {}
        try:
            with open(DATA_INDEX_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def _save_local_index(self):
        """Persist updated index to disk."""
        DATA_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_INDEX_PATH, 'w') as f:
            json.dump(self.local_index, f, indent=2)
    
    def check_and_pull(self):
        """
        Core Logic:
        1. Fetch metadata from remote SaaS
        2. Compare 'updated_at' timestamps
        3. Pull content ONLY if remote > local
        4. Pipeline to codex_digest
        """
        self.logger.info("Starting synchronization cycle...")
        
        # Fetch remote metadata
        remote_articles = self._fetch_remote_meta()
        
        updates_found = False
        for article in remote_articles:
            article_id = str(article["id"])
            remote_ts = article["updated_at"]
            
            # Check for Drift
            if article_id not in self.local_index or remote_ts > self.local_index[article_id]:
                self.logger.info(f"Drift detected for Article {article_id}. Pulling update.")
                self._ingest_content(article)
                self.local_index[article_id] = remote_ts
                updates_found = True
        
        if updates_found:
            self._save_local_index()
            self.logger.info("Sync complete. Local index updated.")
        else:
            self.logger.info("System is synchronized. No drift detected.")
    
    def _ingest_content(self, article_data: Dict):
        """Pass content to ingestion adapter for tokenization."""
        ingest_adapter.process_document(
            source="zendesk_help_center",
            doc_id=article_data["id"],
            content=article_data["body"],
            metadata={
                "title": article_data["title"],
                "url": article_data["html_url"],
                "updated_at": article_data["updated_at"]
            }
        )
    
    def _fetch_remote_meta(self) -> List[Dict]:
        """Fetch article metadata from Zendesk API."""
        import requests
        
        try:
            response = requests.get(
                f"{self.base_url}/articles.json",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("articles", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch remote metadata: {e}")
            return []
    
    def run_forever(self):
        """Run service in loop mode."""
        self.logger.info("Starting Knowledge Crawler Service...")
        while True:
            try:
                self.check_and_pull()
            except Exception as e:
                self.logger.error(f"Sync cycle failed: {e}", exc_info=True)
            time.sleep(SYNC_INTERVAL_SECONDS)

if __name__ == "__main__":
    import os
    service = ZendeskSyncService(
        subdomain=os.getenv("ZENDESK_SUBDOMAIN", "example"),
        api_token=os.getenv("ZENDESK_API_TOKEN", "")
    )
    service.check_and_pull()  # One-shot mode for testing
    # service.run_forever()  # Resident mode for production
```

#### Phase 1.2: Integration Points (Pre-commit Cycle 3)

**File:** `src/codex/ingest/adapter.py`

```python
"""
Ingestion Adapter - Connects Crawler to RAG Pipeline
"""

from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def process_document(
    source: str,
    doc_id: str,
    content: str,
    metadata: Dict[str, Any]
):
    """
    Process document for RAG ingestion.
    
    Args:
        source: Source system identifier (e.g., "zendesk_help_center")
        doc_id: Unique document identifier
        content: Document text content
        metadata: Additional metadata (title, url, timestamps, etc.)
    """
    logger.info(f"Processing document {doc_id} from {source}")
    
    # TODO: Connect to existing RAG pipeline
    # from src.codex.rag.indexer import RAGIndexer
    # indexer = RAGIndexer()
    # indexer.add_document(doc_id, content, metadata)
    
    # For now, log and store in staging area
    staging_dir = Path("data/staging") / source
    staging_dir.mkdir(parents=True, exist_ok=True)
    
    doc_file = staging_dir / f"{doc_id}.json"
    import json
    with open(doc_file, 'w') as f:
        json.dump({
            "doc_id": doc_id,
            "source": source,
            "content": content,
            "metadata": metadata
        }, f, indent=2)
    
    logger.info(f"Document {doc_id} staged at {doc_file}")
```

#### Phase 1.3: Deployment Configuration (Pre-commit Cycle 4)

**File:** `.github/workflows/knowledge-crawler.yml`

```yaml
name: Knowledge Crawler Service

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  sync-knowledge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install requests
      
      - name: Run Knowledge Sync
        env:
          ZENDESK_SUBDOMAIN: ${{ secrets.ZENDESK_SUBDOMAIN }}
          ZENDESK_API_TOKEN: ${{ secrets.ZENDESK_API_TOKEN }}
        run: |
          python -m src.services.crawler.zendesk_sync
      
      - name: Commit Updated Index
        run: |
          git config user.name "Knowledge Crawler Bot"
          git config user.email "bot@codex.ai"
          git add data/zendesk_api_index.json data/staging/
          git commit -m "chore: update knowledge index [skip ci]" || true
          git push || true
```

#### Success Criteria
- ✅ Service runs on schedule (every 6 hours)
- ✅ Only pulls changed articles (drift detection)
- ✅ Updates local index atomically
- ✅ Integrates with RAG pipeline
- ✅ Monitors for failures and alerts

---

## Quick Win #2: Schema Authority

### Objective
Establish `src/codex/zendesk/model` as Single Source of Truth with strict Pydantic contracts.

### Implementation Plan

#### Phase 2.1: Core Schema Definition (Pre-commit Cycle 1-2)

**File:** `src/codex/zendesk/model/ticket.py`

```python
"""
Zendesk Support Ticket Schema Authority
Role: Defines immutable API contract for Ticket objects
Context: Enforces strict typing to prevent 'Split Brain' logic drift
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime

class TicketStatus(str, Enum):
    """Zendesk ticket status values."""
    NEW = "new"
    OPEN = "open"
    PENDING = "pending"
    HOLD = "hold"
    SOLVED = "solved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    """Zendesk ticket priority values."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class TicketType(str, Enum):
    """Zendesk ticket type values."""
    PROBLEM = "problem"
    INCIDENT = "incident"
    QUESTION = "question"
    TASK = "task"

class TicketComment(BaseModel):
    """Ticket comment schema."""
    id: Optional[int] = None
    body: str = Field(..., min_length=1)
    public: bool = True
    author_id: int
    created_at: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CustomField(BaseModel):
    """Custom field schema."""
    id: int
    value: Any

class Ticket(BaseModel):
    """
    Canonical representation of a Zendesk Ticket.
    This schema validates all Agent-generated ticket operations.
    """
    # Core identifiers (read-only after creation)
    id: Optional[int] = Field(None, description="Zendesk Ticket ID (Read-only)")
    external_id: Optional[str] = Field(None, description="External system ID")
    
    # Required fields
    subject: str = Field(..., min_length=1, max_length=255, description="Ticket Subject Line")
    description: str = Field(..., description="Initial ticket description/body")
    
    # Status and priority
    status: TicketStatus = Field(default=TicketStatus.NEW)
    priority: Optional[TicketPriority] = None
    type: Optional[TicketType] = None
    
    # Assignment
    requester_id: int = Field(..., description="User who requested the ticket")
    assignee_id: Optional[int] = Field(None, description="Agent assigned to ticket")
    group_id: Optional[int] = Field(None, description="Group assigned to ticket")
    organization_id: Optional[int] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    
    # Timestamps (read-only)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    
    # Collaboration
    collaborator_ids: List[int] = Field(default_factory=list)
    follower_ids: List[int] = Field(default_factory=list)
    
    # Problem/incident linking
    problem_id: Optional[int] = None
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Enforce SaaS constraint: Tags cannot contain spaces."""
        for tag in v:
            if " " in tag:
                raise ValueError(f"Invalid tag '{tag}': Tags cannot contain spaces. Use underscores or hyphens.")
        return v
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        """Ensure subject is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Subject cannot be empty or whitespace-only")
        return v.strip()
    
    @field_validator('custom_fields')
    @classmethod
    def validate_custom_fields(cls, v):
        """Ensure custom field IDs are unique."""
        field_ids = [f.id for f in v]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("Custom field IDs must be unique")
        return v
    
    class Config:
        # Prevent the Agent from storing extra data that doesn't exist in the SaaS
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

    def to_zendesk_payload(self) -> Dict[str, Any]:
        """Convert to Zendesk API payload format."""
        payload = {
            "ticket": {
                "subject": self.subject,
                "description": self.description if self.description else self.subject,
                "status": self.status.value if isinstance(self.status, Enum) else self.status,
                "requester_id": self.requester_id,
            }
        }
        
        # Optional fields
        if self.priority:
            payload["ticket"]["priority"] = self.priority.value if isinstance(self.priority, Enum) else self.priority
        if self.type:
            payload["ticket"]["type"] = self.type.value if isinstance(self.type, Enum) else self.type
        if self.assignee_id:
            payload["ticket"]["assignee_id"] = self.assignee_id
        if self.group_id:
            payload["ticket"]["group_id"] = self.group_id
        if self.tags:
            payload["ticket"]["tags"] = self.tags
        if self.custom_fields:
            payload["ticket"]["custom_fields"] = [
                {"id": f.id, "value": f.value} for f in self.custom_fields
            ]
        
        return payload

    @classmethod
    def from_zendesk_response(cls, data: Dict[str, Any]) -> "Ticket":
        """Parse Zendesk API response into Ticket model."""
        ticket_data = data.get("ticket", data)
        
        # Parse custom fields
        custom_fields = []
        for field in ticket_data.get("custom_fields", []):
            custom_fields.append(CustomField(id=field["id"], value=field["value"]))
        
        return cls(
            id=ticket_data.get("id"),
            external_id=ticket_data.get("external_id"),
            subject=ticket_data["subject"],
            description=ticket_data.get("description", ""),
            status=TicketStatus(ticket_data.get("status", "new")),
            priority=TicketPriority(ticket_data["priority"]) if ticket_data.get("priority") else None,
            type=TicketType(ticket_data["type"]) if ticket_data.get("type") else None,
            requester_id=ticket_data["requester_id"],
            assignee_id=ticket_data.get("assignee_id"),
            group_id=ticket_data.get("group_id"),
            organization_id=ticket_data.get("organization_id"),
            tags=ticket_data.get("tags", []),
            custom_fields=custom_fields,
            created_at=datetime.fromisoformat(ticket_data["created_at"].replace("Z", "+00:00")) if ticket_data.get("created_at") else None,
            updated_at=datetime.fromisoformat(ticket_data["updated_at"].replace("Z", "+00:00")) if ticket_data.get("updated_at") else None,
            collaborator_ids=ticket_data.get("collaborator_ids", []),
            follower_ids=ticket_data.get("follower_ids", []),
            problem_id=ticket_data.get("problem_id")
        )
```

#### Phase 2.2: Validator Suite (Pre-commit Cycle 3)

**File:** `tests/test_zendesk_ticket_schema.py`

```python
"""
Schema Authority Validation Suite
Ensures Ticket model prevents invalid data
"""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from src.codex.zendesk.model.ticket import (
    Ticket, TicketStatus, TicketPriority, CustomField
)

class TestTicketValidation:
    """Test Ticket schema validation."""
    
    def test_valid_minimal_ticket(self):
        """Test creating ticket with minimal required fields."""
        ticket = Ticket(
            subject="Test Ticket",
            description="Test description",
            requester_id=12345
        )
        assert ticket.subject == "Test Ticket"
        assert ticket.status == TicketStatus.NEW
        assert ticket.priority is None
    
    def test_empty_subject_rejected(self):
        """Test that empty subject is rejected."""
        with pytest.raises(ValidationError, match="Subject cannot be empty"):
            Ticket(
                subject="",
                description="Test",
                requester_id=12345
            )
    
    def test_whitespace_subject_rejected(self):
        """Test that whitespace-only subject is rejected."""
        with pytest.raises(ValidationError, match="Subject cannot be empty"):
            Ticket(
                subject="   ",
                description="Test",
                requester_id=12345
            )
    
    def test_tags_with_spaces_rejected(self):
        """Test that tags with spaces are rejected."""
        with pytest.raises(ValidationError, match="Tags cannot contain spaces"):
            Ticket(
                subject="Test",
                description="Test",
                requester_id=12345,
                tags=["valid_tag", "invalid tag"]
            )
    
    def test_extra_fields_rejected(self):
        """Test that extra fields are rejected (extra='forbid')."""
        with pytest.raises(ValidationError):
            Ticket(
                subject="Test",
                description="Test",
                requester_id=12345,
                nonexistent_field="value"  # Should fail
            )
    
    def test_custom_fields_unique_ids(self):
        """Test that duplicate custom field IDs are rejected."""
        with pytest.raises(ValidationError, match="Custom field IDs must be unique"):
            Ticket(
                subject="Test",
                description="Test",
                requester_id=12345,
                custom_fields=[
                    CustomField(id=100, value="value1"),
                    CustomField(id=100, value="value2")  # Duplicate ID
                ]
            )
    
    def test_to_zendesk_payload(self):
        """Test conversion to Zendesk API payload."""
        ticket = Ticket(
            subject="Test Ticket",
            description="Test description",
            requester_id=12345,
            priority=TicketPriority.HIGH,
            tags=["urgent", "customer_complaint"]
        )
        
        payload = ticket.to_zendesk_payload()
        
        assert payload["ticket"]["subject"] == "Test Ticket"
        assert payload["ticket"]["priority"] == "high"
        assert "urgent" in payload["ticket"]["tags"]
    
    def test_from_zendesk_response(self):
        """Test parsing Zendesk API response."""
        api_response = {
            "ticket": {
                "id": 123,
                "subject": "API Test",
                "description": "From API",
                "status": "open",
                "priority": "high",
                "requester_id": 456,
                "created_at": "2026-01-08T12:00:00Z",
                "updated_at": "2026-01-08T12:30:00Z",
                "tags": ["api", "test"]
            }
        }
        
        ticket = Ticket.from_zendesk_response(api_response)
        
        assert ticket.id == 123
        assert ticket.subject == "API Test"
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH
        assert "api" in ticket.tags
```

#### Phase 2.3: Migration Path (Pre-commit Cycle 4)

**File:** `docs/migration/ZENDESK_SCHEMA_MIGRATION.md`

```markdown
# Zendesk Schema Migration Guide

## Overview
Migration from legacy `agents/zendesk_quantum_orchestrator.py` to modern `src/codex/zendesk/model/ticket.py`

## Migration Steps

### Step 1: Update Imports
```python
# Before (legacy)
from agents.zendesk_quantum_orchestrator import create_ticket

# After (modern)
from src.codex.zendesk.model.ticket import Ticket
from src.codex.zendesk.client import ZendeskClient
```

### Step 2: Replace Dictionary Usage
```python
# Before (legacy - no validation)
ticket_data = {
    "subject": subject,
    "priority": "urgent",  # Typo-prone
    "invalid_field": "value"  # Silently ignored
}

# After (modern - validated)
ticket = Ticket(
    subject=subject,
    description=description,
    requester_id=user_id,
    priority=TicketPriority.URGENT  # Type-safe
)
# Extra fields raise ValidationError
```

### Step 3: Use Client for API Calls
```python
# Before (legacy)
response = requests.post(f"{BASE_URL}/tickets.json", json=ticket_data)

# After (modern)
client = ZendeskClient(subdomain="company", api_token=token)
created_ticket = client.create_ticket(ticket)
```

## Benefits
1. **Type Safety**: Pydantic validation catches errors at runtime
2. **IDE Support**: Autocomplete and type hints
3. **Documentation**: Self-documenting schema
4. **Consistency**: Single source of truth
5. **Testing**: Easy to validate with pytest
```

#### Success Criteria
- ✅ All ticket operations use Pydantic models
- ✅ Zero hardcoded dictionaries in production code
- ✅ 100% test coverage on schema validation
- ✅ Legacy `agents/zendesk_quantum_orchestrator.py` deprecated
- ✅ Migration guide complete

---

## Quick Win #3: Configuration Consolidation

### Objective
Migrate SLA business logic from CSV files into validated Policy Objects.

### Implementation Plan

#### Phase 3.1: Policy Model (Pre-commit Cycle 1)

**File:** `src/codex/dynamics/model/sla_policy.py`

```python
"""
SLA Policy Authority
Role: Single Source of Truth for SLA business rules
Replaces: configs/deployment/d365/slas.csv
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import timedelta

class SLAPriority(str, Enum):
    """SLA priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class BusinessHoursType(str, Enum):
    """Business hours calculation type."""
    CALENDAR_24_7 = "24/7"
    BUSINESS_HOURS = "business_hours"

class SLATarget(BaseModel):
    """SLA target configuration."""
    response_time: timedelta = Field(..., description="Time to first response")
    resolution_time: timedelta = Field(..., description="Time to resolution")
    business_hours: BusinessHoursType = BusinessHoursType.BUSINESS_HOURS
    
    @validator('response_time', 'resolution_time')
    def validate_positive_duration(cls, v):
        """Ensure durations are positive."""
        if v.total_seconds() <= 0:
            raise ValueError("SLA times must be positive")
        return v
    
    @validator('resolution_time')
    def validate_resolution_greater_than_response(cls, v, values):
        """Ensure resolution time >= response time."""
        if 'response_time' in values and v < values['response_time']:
            raise ValueError("Resolution time must be >= response time")
        return v

class SLAPolicy(BaseModel):
    """Complete SLA policy definition."""
    priority: SLAPriority
    target: SLATarget
    escalation_enabled: bool = True
    escalation_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Escalate at % of SLA")
    
    class Config:
        use_enum_values = True

# Canonical SLA Policies (replaces CSV)
STANDARD_SLA_POLICIES: Dict[SLAPriority, SLAPolicy] = {
    SLAPriority.URGENT: SLAPolicy(
        priority=SLAPriority.URGENT,
        target=SLATarget(
            response_time=timedelta(hours=1),
            resolution_time=timedelta(hours=4),
            business_hours=BusinessHoursType.CALENDAR_24_7
        ),
        escalation_threshold=0.7
    ),
    SLAPriority.HIGH: SLAPolicy(
        priority=SLAPriority.HIGH,
        target=SLATarget(
            response_time=timedelta(hours=4),
            resolution_time=timedelta(hours=24),
            business_hours=BusinessHoursType.BUSINESS_HOURS
        ),
        escalation_threshold=0.8
    ),
    SLAPriority.NORMAL: SLAPolicy(
        priority=SLAPriority.NORMAL,
        target=SLATarget(
            response_time=timedelta(hours=8),
            resolution_time=timedelta(hours=48),
            business_hours=BusinessHoursType.BUSINESS_HOURS
        ),
        escalation_threshold=0.85
    ),
    SLAPriority.LOW: SLAPolicy(
        priority=SLAPriority.LOW,
        target=SLATarget(
            response_time=timedelta(hours=24),
            resolution_time=timedelta(hours=72),
            business_hours=BusinessHoursType.BUSINESS_HOURS
        ),
        escalation_threshold=0.9
    ),
}

def get_sla_policy(priority: SLAPriority) -> SLAPolicy:
    """Retrieve SLA policy for given priority."""
    return STANDARD_SLA_POLICIES[priority]

def calculate_sla_deadline(
    priority: SLAPriority,
    start_time: datetime,
    target_type: str = "response"
) -> datetime:
    """
    Calculate SLA deadline based on priority and start time.
    
    Args:
        priority: Ticket priority
        start_time: When SLA clock started
        target_type: "response" or "resolution"
    
    Returns:
        Deadline datetime
    """
    policy = get_sla_policy(priority)
    
    if target_type == "response":
        duration = policy.target.response_time
    elif target_type == "resolution":
        duration = policy.target.resolution_time
    else:
        raise ValueError(f"Invalid target_type: {target_type}")
    
    # TODO: Implement business hours calculation
    # For now, simple calendar time
    return start_time + duration
```

#### Phase 3.2: Deprecate CSV (Pre-commit Cycle 2)

**File:** `configs/deployment/d365/slas.csv.DEPRECATED`

```csv
# DEPRECATED: This file is no longer used
# See: src/codex/dynamics/model/sla_policy.py
# Migration completed: 2026-01-08
priority,response_time_hours,resolution_time_hours
urgent,1,4
high,4,24
normal,8,48
low,24,72
```

#### Success Criteria
- ✅ All SLA logic uses Policy Objects
- ✅ CSV files deprecated with clear migration notes
- ✅ Business rules validated at import time
- ✅ Tests cover all SLA calculations

---

## Quick Win #4: Bridge Hardening

### Objective
Replace insecure file-based IPC with authenticated named pipes.

### Implementation Plan

#### Phase 4.1: Secure Bridge Implementation (Pre-commit Cycle 1-2)

**File:** `src/bridge/secure_ipc.py`

```python
"""
Secure IPC Bridge
Replaces: temp/bridge_codex_copilot_bridge (insecure file-based)
Security: Authenticated named pipes with 0o600 permissions
"""

import os
import stat
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class SecureBridge:
    """Secure IPC bridge using named pipes."""
    
    def __init__(self, bridge_name: str = "codex_copilot_bridge"):
        self.bridge_name = bridge_name
        self.pipe_dir = Path("/tmp/codex_bridges")
        self.pipe_path = self.pipe_dir / bridge_name
        self.auth_token = os.getenv("CODEX_BRIDGE_TOKEN")
        
        if not self.auth_token:
            raise RuntimeError("CODEX_BRIDGE_TOKEN environment variable required")
    
    def create_pipe(self):
        """Create named pipe with secure permissions."""
        self.pipe_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        
        if self.pipe_path.exists():
            self.pipe_path.unlink()
        
        # Create named pipe
        os.mkfifo(self.pipe_path, mode=0o600)
        logger.info(f"Created secure pipe: {self.pipe_path}")
    
    def verify_permissions(self) -> bool:
        """Verify pipe has secure permissions."""
        if not self.pipe_path.exists():
            return False
        
        st = self.pipe_path.stat()
        mode = stat.S_IMODE(st.st_mode)
        
        # Must be 0o600 (owner read/write only)
        if mode != 0o600:
            logger.error(f"Insecure permissions: {oct(mode)}, expected 0o600")
            return False
        
        # Must be owned by current user
        if st.st_uid != os.getuid():
            logger.error("Pipe not owned by current user")
            return False
        
        return True
    
    def send_message(self, message: Dict[str, Any]):
        """Send authenticated message through pipe."""
        if not self.verify_permissions():
            raise SecurityError("Bridge security verification failed")
        
        # Add authentication
        authenticated_msg = {
            "auth_token": self.auth_token,
            "payload": message
        }
        
        with open(self.pipe_path, 'w') as pipe:
            json.dump(authenticated_msg, pipe)
            pipe.write('\n')
        
        logger.debug(f"Sent message: {message.get('type', 'unknown')}")
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive and verify authenticated message."""
        if not self.verify_permissions():
            raise SecurityError("Bridge security verification failed")
        
        with open(self.pipe_path, 'r') as pipe:
            data = json.loads(pipe.readline())
        
        # Verify authentication
        if data.get("auth_token") != self.auth_token:
            logger.error("Authentication failed")
            raise SecurityError("Invalid authentication token")
        
        logger.debug(f"Received message: {data.get('payload', {}).get('type', 'unknown')}")
        return data.get("payload")
    
    def cleanup(self):
        """Clean up pipe resources."""
        if self.pipe_path.exists():
            self.pipe_path.unlink()
            logger.info(f"Cleaned up pipe: {self.pipe_path}")

class SecurityError(Exception):
    """Bridge security violation."""
    pass

# Context manager for safe bridge usage
@contextmanager
def secure_bridge(bridge_name: str = "codex_copilot_bridge"):
    """Context manager for secure bridge operations."""
    bridge = SecureBridge(bridge_name)
    bridge.create_pipe()
    try:
        yield bridge
    finally:
        bridge.cleanup()
```

#### Phase 4.2: Migration Script (Pre-commit Cycle 3)

**File:** `scripts/migrate_bridge.py`

```python
"""
Bridge Migration Script
Migrates from insecure file-based IPC to secure named pipes
"""

import os
import shutil
from pathlib import Path

def migrate():
    """Execute bridge migration."""
    legacy_bridge = Path("temp/bridge_codex_copilot_bridge")
    
    # Archive legacy bridge
    if legacy_bridge.exists():
        archive_dir = Path("temp/archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        backup_path = archive_dir / f"bridge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(legacy_bridge), str(backup_path))
        print(f"✅ Archived legacy bridge to {backup_path}")
    
    # Create deprecation notice
    notice = legacy_bridge.with_suffix(".DEPRECATED")
    notice.write_text(
        "DEPRECATED: This bridge has been replaced with secure IPC\n"
        "See: src/bridge/secure_ipc.py\n"
        "Migration completed: 2026-01-08\n"
    )
    print(f"✅ Created deprecation notice: {notice}")
    
    print("\n✅ Bridge migration complete!")
    print("Next steps:")
    print("1. Set CODEX_BRIDGE_TOKEN environment variable")
    print("2. Update code to use SecureBridge from src.bridge.secure_ipc")
    print("3. Test repro workflows with new bridge")

if __name__ == "__main__":
    from datetime import datetime
    migrate()
```

#### Success Criteria
- ✅ Named pipes use 0o600 permissions
- ✅ Authentication token required for all operations
- ✅ Legacy bridge archived and deprecated
- ✅ Security audit passes
- ✅ Repro workflows tested with new bridge

---

## Quick Win #5: Documentation Distillation

### Objective
Configure `codex_digest` to auto-generate concise `digest.md` from normalized datasets.

### Implementation Plan

#### Phase 5.1: Digest Pipeline (Pre-commit Cycle 1-2)

**File:** `src/services/digest/pipeline.py`

```python
"""
Documentation Distillation Pipeline
Role: Generates concise digest.md from normalized datasets and schemas
Context: Ensures Agent reads same structures it codes
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)

class DigestPipeline:
    """Pipeline for documentation distillation."""
    
    def __init__(self, output_path: Path = Path("docs/digest.md")):
        self.output_path = output_path
        self.sources = []
    
    def add_source(self, source_type: str, source_path: Path):
        """Register a documentation source."""
        self.sources.append({
            "type": source_type,
            "path": source_path
        })
    
    def extract_schema_docs(self, schema_dir: Path) -> str:
        """Extract documentation from Pydantic schemas."""
        docs = ["## Schema Reference\n"]
        
        # Scan for schema files
        schema_files = list(schema_dir.glob("**/*.py"))
        
        for schema_file in schema_files:
            # TODO: Parse docstrings and field descriptions
            # For now, just list files
            rel_path = schema_file.relative_to(schema_dir)
            docs.append(f"- `{rel_path}`: [Schema definitions]")
        
        return "\n".join(docs)
    
    def extract_api_docs(self, api_dir: Path) -> str:
        """Extract API documentation."""
        docs = ["## API Reference\n"]
        
        # TODO: Extract from OpenAPI specs, function signatures, etc.
        docs.append("API documentation will be auto-generated from code annotations.")
        
        return "\n".join(docs)
    
    def extract_knowledge_base(self, kb_path: Path) -> str:
        """Extract from synchronized knowledge base."""
        docs = ["## Knowledge Base\n"]
        
        if kb_path.exists():
            # Count articles
            articles = list(kb_path.glob("**/*.json"))
            docs.append(f"- Total articles: {len(articles)}")
            docs.append(f"- Last synchronized: {datetime.now(UTC).isoformat()}")
        
        return "\n".join(docs)
    
    def generate_digest(self):
        """Generate consolidated digest.md."""
        logger.info("Generating documentation digest...")
        
        sections = [
            f"# Codex Documentation Digest\n",
            f"**Generated:** {datetime.now(UTC).isoformat()}\n",
            "---\n"
        ]
        
        # Add schema documentation
        schema_dir = Path("src/codex/zendesk/model")
        if schema_dir.exists():
            sections.append(self.extract_schema_docs(schema_dir))
            sections.append("\n---\n")
        
        # Add API documentation
        api_dir = Path("src/codex/api")
        if api_dir.exists():
            sections.append(self.extract_api_docs(api_dir))
            sections.append("\n---\n")
        
        # Add knowledge base summary
        kb_path = Path("data/staging/zendesk_help_center")
        if kb_path.exists():
            sections.append(self.extract_knowledge_base(kb_path))
            sections.append("\n---\n")
        
        # Write digest
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text("\n".join(sections))
        
        logger.info(f"✅ Digest generated: {self.output_path}")
        return self.output_path

if __name__ == "__main__":
    pipeline = DigestPipeline()
    pipeline.generate_digest()
```

#### Phase 5.2: Automation (Pre-commit Cycle 3)

**File:** `.github/workflows/digest-generation.yml`

```yaml
name: Documentation Digest Generation

on:
  push:
    paths:
      - 'src/codex/*/model/**'
      - 'data/staging/**'
      - 'docs/**/*.md'
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  generate-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Generate Digest
        run: python -m src.services.digest.pipeline
      
      - name: Commit Digest
        run: |
          git config user.name "Digest Bot"
          git config user.email "bot@codex.ai"
          git add docs/digest.md
          git commit -m "docs: update documentation digest [skip ci]" || true
          git push || true
```

#### Success Criteria
- ✅ `digest.md` auto-generated daily
- ✅ Includes schema documentation
- ✅ Includes API reference
- ✅ Includes knowledge base summary
- ✅ Agent training uses digest.md

---

## Implementation Timeline

### Phase 1: Foundation
- **Pre-commit Cycle 1-2:** Quick Win #1 Phase 1.1-1.2 (Knowledge Crawler core)
- **Pre-commit Cycle 3-4:** Quick Win #2 Phase 2.1 (Schema Authority)
- **Pre-commit Cycle 5:** Quick Win #3 Phase 3.1 (Policy Objects)

### Phase 2: Integration
- **Pre-commit Cycle 1-2:** Quick Win #4 (Bridge Hardening)
- **Pre-commit Cycle 3-4:** Quick Win #5 (Documentation Distillation)
- **Pre-commit Cycle 5:** Integration testing and validation

### Phase 3: Migration & Cleanup
- **Pre-commit Cycle 1-2:** Legacy code deprecation
- **Pre-commit Cycle 3:** Documentation updates
- **Pre-commit Cycle 4-5:** Final testing and rollout

---

## Success Metrics

### Data Sovereignty
- ✅ Knowledge sync drift detection <1 hour
- ✅ Zero stale data in RAG pipeline
- ✅ 100% of SaaS changes captured

### Schema Authority
- ✅ Zero hardcoded dictionaries in production
- ✅ 100% type safety on ticket operations
- ✅ <5 min to add new schema field

### Configuration Consolidation
- ✅ Zero business logic in CSV files
- ✅ All policies validated at import
- ✅ Single source of truth established

### Bridge Security
- ✅ Zero unauthorized IPC access
- ✅ All bridges use authentication
- ✅ Security audit passes

### Documentation Quality
- ✅ digest.md generated daily
- ✅ Agent training aligned with code
- ✅ <30 pages of essential docs

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:** 
- Parallel run legacy and modern systems for 2 implementation cycles
- Feature flags for gradual rollout
- Comprehensive test coverage before deprecation

### Risk 2: Performance Degradation
**Mitigation:**
- Benchmark all new components
- Profile critical paths
- Set SLOs and monitor

### Risk 3: Security Vulnerabilities
**Mitigation:**
- Security review before production
- Penetration testing of IPC bridge
- Regular security audits

---

## Next Steps

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/top-5-quick-wins
   ```

2. **Start with Quick Win #1**
   - Implement `src/services/crawler/zendesk_sync.py`
   - Test locally with mock data
   - Deploy to staging

3. **Progressive Rollout**
   - Win #1 → Win #2 → Win #3 → Win #4 → Win #5
   - Each win validated before moving to next
   - Daily progress reviews

4. **Documentation**
   - Update AGENTS_POLICY.md
   - Update ARCHITECTURE.md
   - Create migration guides

---

## Conclusion

These 5 Quick Wins establish a solid foundation for transforming the repository from a "Split Brain" state into a cohesive MLOps platform. By addressing knowledge entropy, schema authority, configuration chaos, security vulnerabilities, and documentation drift, we create a system where:

- **Data is sovereign** - Single source of truth for all knowledge
- **Schemas are authoritative** - Type-safe, validated, self-documenting
- **Configuration is code** - Validated, versioned, testable
- **Security is built-in** - Authentication, encryption, auditing
- **Documentation is synchronized** - Agent reads what it codes

This plan is ready for immediate execution with clear success criteria, risk mitigation, and a realistic timeline.

---

**End of Plan**
