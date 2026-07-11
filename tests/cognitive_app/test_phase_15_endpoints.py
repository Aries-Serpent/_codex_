"""
Unit tests for Phase 15 - Decision Visualization, Memory Management, and Workflow Monitoring endpoints.

Test Coverage:
- Decision Visualization: 4 endpoints
- Memory Management: 4 endpoints  
- Workflow Monitoring: 3 endpoints
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_db(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Create a test SQLite database with schema."""
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    
    # Create decisions table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL UNIQUE,
            lane_name TEXT NOT NULL,
            candidate TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            k1_factor REAL,
            coherence_metric REAL,
            superposition_state TEXT,
            submitted_at TEXT NOT NULL,
            outcome TEXT,
            outcome_at TEXT
        )
        """
    )
    
    # Create lte_patterns table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lte_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane_name TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_name TEXT,
            confidence REAL DEFAULT 1.0,
            usage_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            last_used_at TEXT
        )
        """
    )
    
    # Create stm_entries table (for memory tests)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stm_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            metadata TEXT,
            timestamp TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
        """
    )
    
    # Create ltm_entries table (for memory tests)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ltm_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            metadata TEXT,
            pattern_type TEXT,
            confidence REAL DEFAULT 1.0,
            timestamp TEXT NOT NULL
        )
        """
    )
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def client(test_db: sqlite3.Connection, tmp_path: Path) -> TestClient:
    """Create FastAPI test client with mocked database."""
    # Import here to avoid import errors if cognitive_app not installed
    try:
        from cognitive_app.src.server.cli_api_server import app
    except ImportError:
        pytest.skip("cognitive_app not installed")
    
    # Patch the database connection
    with patch("cognitive_app.src.server.cli_api_server._db", test_db), \
         patch("cognitive_app.src.server.cli_api_server._DB_PATH", str(tmp_path / "test.db")), \
         patch("cognitive_app.src.server.cli_api_server._require_memory_auth", return_value=None):
        yield TestClient(app)


# ────────────────────────────────────────────────────────────────────────────────
# Decision Visualization Endpoint Tests
# ────────────────────────────────────────────────────────────────────────────────

class TestDecisionVisualization:
    """Tests for decision visualization endpoints."""
    
    def test_submit_decision_success(self, client: TestClient):
        """Test successfully submitting a decision."""
        payload = {
            "lane_name": "security",
            "candidate": "Fix SQL injection in auth.py",
            "confidence_score": 0.95,
            "k1_factor": 0.8,
            "coherence_metric": 0.9,
            "superposition_state": "entangled",
        }
        
        response = client.post("/api/decisions/submit", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["lane_name"] == "security"
        assert data["candidate"] == "Fix SQL injection in auth.py"
        assert data["confidence_score"] == 0.95
        assert "decision_id" in data
        assert data["submitted_at"] is not None
    
    def test_submit_decision_minimal(self, client: TestClient):
        """Test submitting a decision with minimal fields."""
        payload = {
            "lane_name": "coverage",
            "candidate": "Add tests for auth module",
            "confidence_score": 0.75,
        }
        
        response = client.post("/api/decisions/submit", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["lane_name"] == "coverage"
        assert data["k1_factor"] is None
        assert data["outcome"] is None
    
    def test_get_decision_success(self, client: TestClient):
        """Test retrieving a decision by ID."""
        # First submit a decision
        submit_payload = {
            "lane_name": "stability",
            "candidate": "Fix flaky test in test_auth.py",
            "confidence_score": 0.88,
        }
        submit_response = client.post("/api/decisions/submit", json=submit_payload)
        decision_id = submit_response.json()["decision_id"]
        
        # Then retrieve it
        response = client.get(f"/api/decisions/{decision_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["decision_id"] == decision_id
        assert data["lane_name"] == "stability"
    
    def test_get_decision_not_found(self, client: TestClient):
        """Test retrieving a non-existent decision."""
        response = client.get("/api/decisions/nonexistent-id")
        assert response.status_code == 404
    
    def test_get_recent_decisions(self, client: TestClient):
        """Test retrieving recent decisions."""
        # Submit multiple decisions
        for i in range(5):
            payload = {
                "lane_name": "docs",
                "candidate": f"Fix documentation issue {i}",
                "confidence_score": 0.7 + i * 0.05,
            }
            client.post("/api/decisions/submit", json=payload)
        
        response = client.get("/api/decisions/recent?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 10
        assert len(data) >= 5
    
    def test_get_recent_decisions_limited(self, client: TestClient):
        """Test retrieving limited recent decisions."""
        # Submit multiple decisions
        for i in range(10):
            payload = {
                "lane_name": "complexity",
                "candidate": f"Simplify function {i}",
                "confidence_score": 0.8,
            }
            client.post("/api/decisions/submit", json=payload)
        
        response = client.get("/api/decisions/recent?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 3
    
    def test_get_decision_history(self, client: TestClient):
        """Test retrieving decision history with pagination."""
        # Submit decisions for different lanes
        for lane in ["security", "coverage", "stability"]:
            for i in range(3):
                payload = {
                    "lane_name": lane,
                    "candidate": f"Fix {lane} issue {i}",
                    "confidence_score": 0.8,
                }
                client.post("/api/decisions/submit", json=payload)
        
        response = client.get("/api/decisions/history?page=1&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total"] == 9
        assert len(data["decisions"]) <= 5
    
    def test_get_decision_history_filtered_by_lane(self, client: TestClient):
        """Test retrieving decision history filtered by lane."""
        # Submit decisions for different lanes
        for lane in ["security", "coverage"]:
            for i in range(3):
                payload = {
                    "lane_name": lane,
                    "candidate": f"Fix {lane} issue {i}",
                    "confidence_score": 0.8,
                }
                client.post("/api/decisions/submit", json=payload)
        
        response = client.get("/api/decisions/history?lane_name=security&page=1&page_size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert all(d["lane_name"] == "security" for d in data["decisions"])


# ────────────────────────────────────────────────────────────────────────────────
# Memory Management Endpoint Tests
# ────────────────────────────────────────────────────────────────────────────────

class TestMemoryManagement:
    """Tests for memory management endpoints."""
    
    def test_store_memory_success(self, client: TestClient):
        """Test successfully storing a pattern in LTE."""
        payload = {
            "lane_name": "security",
            "pattern_type": "sql_injection",
            "pattern_name": "SQL Injection Pattern",
            "confidence": 0.95,
        }
        
        response = client.post("/api/memory/store", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert "timestamp" in data
    
    def test_store_memory_minimal(self, client: TestClient):
        """Test storing memory with minimal fields."""
        payload = {
            "lane_name": "coverage",
            "pattern_type": "test_gap",
        }
        
        response = client.post("/api/memory/store", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
    
    def test_retrieve_memory_success(self, client: TestClient):
        """Test retrieving patterns from LTE."""
        # First store a pattern
        store_payload = {
            "lane_name": "stability",
            "pattern_type": "flaky_test",
            "pattern_name": "Flaky Test Pattern",
            "confidence": 0.85,
        }
        client.post("/api/memory/store", json=store_payload)
        
        # Then retrieve it
        response = client.get("/api/memory/retrieve?lane_name=stability&pattern_type=flaky_test")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert data[0]["lane_name"] == "stability"
        assert data[0]["pattern_type"] == "flaky_test"
    
    def test_retrieve_memory_by_lane(self, client: TestClient):
        """Test retrieving memory filtered by lane."""
        # Store patterns for different lanes
        for lane in ["security", "coverage"]:
            for i in range(2):
                store_payload = {
                    "lane_name": lane,
                    "pattern_type": "test_pattern",
                    "pattern_name": f"Pattern {i}",
                }
                client.post("/api/memory/store", json=store_payload)
        
        response = client.get("/api/memory/retrieve?lane_name=security")
        assert response.status_code == 200
        
        data = response.json()
        assert all(item["lane_name"] == "security" for item in data)
    
    def test_retrieve_memory_updates_usage_count(self, client: TestClient):
        """Test that retrieving memory increments usage count."""
        # Store a pattern
        store_payload = {
            "lane_name": "docs",
            "pattern_type": "broken_link",
            "pattern_name": "Broken Link",
            "confidence": 0.9,
        }
        client.post("/api/memory/store", json=store_payload)
        
        # Retrieve it twice
        client.get("/api/memory/retrieve?lane_name=docs")
        response = client.get("/api/memory/retrieve?lane_name=docs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # usage_count should be > 0 after retrieval
        assert data[0]["usage_count"] >= 1
    
    def test_stm_push_success(self, client: TestClient):
        """Test successfully pushing to STM."""
        payload = {
            "key": "test_stm_entry",
            "value": "test_value",
            "metadata": {"source": "test"},
        }
        
        response = client.post("/api/memory/stm-push", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert data["key"] == "test_stm_entry"
        assert "timestamp" in data
    
    def test_stm_push_auto_key(self, client: TestClient):
        """Test STM push with auto-generated key."""
        payload = {
            "value": "test_value",
            "metadata": {"source": "test"},
        }
        
        response = client.post("/api/memory/stm-push", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert "key" in data
        # Key should be auto-generated
        assert data["key"].startswith("stm_")
    
    def test_get_memory_stats(self, client: TestClient):
        """Test retrieving memory statistics."""
        # Add some data
        client.post("/api/memory/store", json={"lane_name": "test", "pattern_type": "test"})
        client.post("/api/memory/stm-push", json={"key": "test_key", "value": "test_value"})
        
        response = client.get("/api/memory/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "stm_count" in data
        assert "ltm_count" in data
        assert "lte_patterns_count" in data
        assert "capacity" in data
        assert "cache_hit_rate" in data
        assert "compression_rate" in data
        assert "timestamp" in data
        assert isinstance(data["cache_hit_rate"], float)
        assert isinstance(data["compression_rate"], float)


# ────────────────────────────────────────────────────────────────────────────────
# Workflow Monitoring Endpoint Tests
# ────────────────────────────────────────────────────────────────────────────────

class TestWorkflowMonitoring:
    """Tests for workflow monitoring endpoints."""
    
    def test_get_workflow_status(self, client: TestClient):
        """Test retrieving workflow portfolio status."""
        response = client.get("/api/workflows/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "total_workflows" in data
        assert "successful" in data
        assert "failed" in data
        assert "cancelled" in data
        assert "in_progress" in data
        assert "timestamp" in data
    
    def test_get_workflow_status_fields(self, client: TestClient):
        """Test workflow status response fields."""
        response = client.get("/api/workflows/status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data["total_workflows"], int)
        assert isinstance(data["successful"], int)
        assert isinstance(data["failed"], int)
        assert isinstance(data["in_progress"], int)
        # Verify counts are reasonable
        assert data["successful"] + data["failed"] + data["cancelled"] + data["in_progress"] <= data["total_workflows"]
    
    def test_check_workflow_gate_success(self, client: TestClient):
        """Test checking workflow gate compliance."""
        payload = {
            "pr_number": 42,
            "check_wec_compliance": True,
        }
        
        response = client.post("/api/workflows/gate-check", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["pr_number"] == 42
        assert "compliant" in data
        assert "wec_items" in data
        assert "message" in data
        assert "checked_at" in data
        assert isinstance(data["wec_items"], dict)
    
    def test_check_workflow_gate_wec_items(self, client: TestClient):
        """Test workflow gate WEC items format."""
        payload = {
            "pr_number": 123,
            "check_wec_compliance": True,
        }
        
        response = client.post("/api/workflows/gate-check", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        wec_items = data["wec_items"]
        # Each WEC item should be a boolean
        for key, value in wec_items.items():
            assert isinstance(value, bool)
    
    def test_get_rate_limit_status(self, client: TestClient):
        """Test retrieving rate limit status."""
        response = client.get("/api/workflows/rate-limit")
        assert response.status_code == 200
        
        data = response.json()
        assert "remaining" in data
        assert "limit" in data
        assert "reset_at" in data
        assert "percentage_used" in data
        assert isinstance(data["remaining"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["percentage_used"], (int, float))
    
    def test_get_rate_limit_values(self, client: TestClient):
        """Test rate limit response values are reasonable."""
        response = client.get("/api/workflows/rate-limit")
        assert response.status_code == 200
        
        data = response.json()
        # Remaining should be <= limit
        assert data["remaining"] <= data["limit"]
        # Percentage should be between 0 and 100
        assert 0 <= data["percentage_used"] <= 100
        # Reset time should be in the future or very close to now
        reset_time = datetime.fromisoformat(data["reset_at"])
        now = datetime.now(timezone.utc).replace(tzinfo=reset_time.tzinfo)
        assert reset_time >= now


# ────────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ────────────────────────────────────────────────────────────────────────────────

class TestIntegration:
    """Integration tests for multiple endpoints working together."""
    
    def test_decision_and_memory_workflow(self, client: TestClient):
        """Test a workflow combining decisions and memory."""
        # Submit a decision
        decision_payload = {
            "lane_name": "security",
            "candidate": "Fix vulnerability",
            "confidence_score": 0.9,
        }
        decision_response = client.post("/api/decisions/submit", json=decision_payload)
        assert decision_response.status_code == 201
        decision_id = decision_response.json()["decision_id"]
        
        # Retrieve the decision
        get_response = client.get(f"/api/decisions/{decision_id}")
        assert get_response.status_code == 200
        
        # Store related pattern in memory
        memory_payload = {
            "lane_name": "security",
            "pattern_type": "vulnerability_fix",
            "pattern_name": "Security Vulnerability",
        }
        store_response = client.post("/api/memory/store", json=memory_payload)
        assert store_response.status_code == 201
        
        # Retrieve memory stats
        stats_response = client.get("/api/memory/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["lte_patterns_count"] >= 1
