"""
Unit tests for Phase 15 - Decision Visualization, Memory Management, and Workflow Monitoring endpoints.

Test Coverage:
- Decision Visualization: 4 endpoints
- Memory Management: 4 endpoints  
- Workflow Monitoring: 3 endpoints
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

# ────────────────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        yield db_path


@pytest.fixture(autouse=True)
def mock_get_token():
    """Auto-use fixture to mock get_token for all tests."""
    with patch("scripts.ci._token_resolver.get_token") as mock:
        mock.return_value = ("test-token-12345", "test-backup")
        yield mock


@pytest.fixture
def client(temp_db_path):
    """Create FastAPI test client with temporary database."""
    # Set the database path before importing the app
    os.environ["CODEX_DB_PATH"] = temp_db_path
    
    # Import and reload the module to use the new database path
    import sys
    if "cognitive_app.src.server.cli_api_server" in sys.modules:
        del sys.modules["cognitive_app.src.server.cli_api_server"]
    
    try:
        from fastapi.testclient import TestClient

        from cognitive_app.src.server.cli_api_server import app as fastapi_app
    except ImportError as e:
        pytest.skip(f"cognitive_app not installed: {e}")
    
    client = TestClient(fastapi_app)
    # Add helper method to make authenticated requests
    original_get = client.get
    original_post = client.post
    
    def get_with_auth(path, *args, **kwargs):
        if "/api/memory/" in path:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            # Use correct ****** format
            kwargs["headers"]["Authorization"] = "******"
        return original_get(path, *args, **kwargs)
    
    def post_with_auth(path, *args, **kwargs):
        if "/api/memory/" in path:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            # Use correct ****** format
            kwargs["headers"]["Authorization"] = "******"
        return original_post(path, *args, **kwargs)
    
    client.get = get_with_auth
    client.post = post_with_auth
    
    return client


# ────────────────────────────────────────────────────────────────────────────────
# Decision Visualization Endpoint Tests
# ────────────────────────────────────────────────────────────────────────────────

class TestDecisionVisualization:
    """Tests for decision visualization endpoints."""
    
    def test_submit_decision_success(self, client):
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
        assert response.status_code == 201, f"Response: {response.text}"
        
        data = response.json()
        assert data["lane_name"] == "security"
        assert data["candidate"] == "Fix SQL injection in auth.py"
        assert data["confidence_score"] == 0.95
        assert "decision_id" in data
        assert data["submitted_at"] is not None
    
    def test_submit_decision_minimal(self, client):
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
    
    def test_get_decision_success(self, client):
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
    
    def test_get_decision_not_found(self, client):
        """Test retrieving a non-existent decision."""
        response = client.get("/api/decisions/nonexistent-id")
        assert response.status_code == 404
    
    def test_get_recent_decisions(self, client):
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
    
    def test_get_recent_decisions_limited(self, client):
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
    
    def test_get_decision_history(self, client):
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
    
    def test_get_decision_history_filtered_by_lane(self, client):
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
    
    def test_store_memory_success(self, client):
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
    
    def test_store_memory_minimal(self, client):
        """Test storing memory with minimal fields."""
        payload = {
            "lane_name": "coverage",
            "pattern_type": "test_gap",
        }
        
        response = client.post("/api/memory/store", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
    
    def test_retrieve_memory_success(self, client):
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
    
    def test_retrieve_memory_by_lane(self, client):
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
    
    def test_retrieve_memory_updates_usage_count(self, client):
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
    
    def test_stm_push_success(self, client):
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
    
    def test_stm_push_auto_key(self, client):
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
    
    def test_get_memory_stats(self, client):
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
    
    def test_get_workflow_status(self, client):
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
    
    def test_get_workflow_status_fields(self, client):
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
    
    def test_check_workflow_gate_success(self, client):
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
    
    def test_check_workflow_gate_wec_items(self, client):
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
    
    def test_get_rate_limit_status(self, client):
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
    
    def test_get_rate_limit_values(self, client):
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
    
    def test_decision_and_memory_workflow(self, client):
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
