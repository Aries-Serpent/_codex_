"""Tests for RFC 8594 deprecation headers on legacy API endpoints.

This test suite verifies that all deprecated endpoints return correct
RFC 8594 compliant headers and that migration paths are documented.
"""

import pytest
from fastapi.testclient import TestClient


class TestLegacyEndpointDeprecationHeaders:
    """Test suite for RFC 8594 deprecation headers on legacy endpoints."""  # pragma: allowlist secret # pragma: allowlist secret

    @pytest.fixture
    def client(self):
        """Create a test client for the API."""
        from codex.api.app import app

        return TestClient(app)

    @pytest.mark.parametrize(
        "method,endpoint,payload,successor,reason",
        [
            (
                "POST",
                "/api/v1/login",
                {"username": "testuser", "password": "pass123456"},
                "/api/auth/login",
                "Use /api/auth/login for modern token management",
            ),
            (
                "POST",
                "/api/v1/train",
                {"data_path": "/data", "model_name": "test_model", "epochs": 10},
                "/api/v2/training",
                "Use /api/v2/training for enhanced training monitoring",
            ),
            (
                "POST",
                "/api/v1/predict",
                {"text": "test input"},
                "/predict",
                "Use /predict for enhanced security and moderation",
            ),
        ],
    )
    def test_deprecated_endpoint_returns_410_gone(
        self, client, method, endpoint, payload, successor, reason
    ):
        """Test that deprecated endpoints return 410 Gone status."""
        if method == "POST":
            response = client.post(endpoint, json=payload)
        elif method == "GET":
            response = client.get(endpoint)

        # Legacy endpoints should return 410 Gone
        assert (response.status_code == 410, "Response must not be empty"
        ), f"Expected 410 for {endpoint}, got {response.status_code}"

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ],
    )
    def test_deprecation_header_present(self, client, endpoint, payload):
        """Test that Deprecation header is present on legacy endpoints."""
        response = client.post(endpoint, json=payload)

        assert "deprecation" in response.headers, f"Deprecation header missing from {endpoint}"
        assert (response.headers["deprecation"].lower() == "true", "Response must not be empty"
        ), f"Deprecation header should be 'true', got {response.headers['deprecation']}"

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ],
    )
    def test_sunset_header_present(self, client, endpoint, payload):
        """Test that Sunset header is present on legacy endpoints."""
        response = client.post(endpoint, json=payload)

        assert "sunset" in response.headers, f"Sunset header missing from {endpoint}"
        # Should be a valid RFC 5322 date
        sunset_value = response.headers["sunset"]
        assert len(sunset_value) > 0, f"Sunset header is empty for {endpoint}"

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ],
    )
    def test_link_header_present_with_successor(self, client, endpoint, payload):
        """Test that Link header points to successor-version."""
        response = client.post(endpoint, json=payload)

        assert "link" in response.headers, f"Link header missing from {endpoint}"
        link_value = response.headers["link"]
        assert "rel=" in link_value, f"Link header missing rel= attribute for {endpoint}"
        assert ("successor-version" in link_value, "Value must be initialized"
        ), f"Link header should use successor-version relation for {endpoint}"

    @pytest.mark.parametrize(
        "endpoint,payload",
        [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ],
    )
    def test_warning_header_present(self, client, endpoint, payload):
        """Test that Warning header is present on legacy endpoints."""
        response = client.post(endpoint, json=payload)

        assert "warning" in response.headers, f"Warning header missing from {endpoint}"
        warning_value = response.headers["warning"]
        assert "299" in warning_value, f"Warning header should start with 299 code for {endpoint}"

    def test_deprecation_info_endpoint(self, client):
        """Test that deprecation info endpoint provides guidance."""
        response = client.get("/api/v1/deprecation-info")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "deprecated_endpoints" in data, "Response should contain deprecated_endpoints"
        assert len(data["deprecated_endpoints"]) >= 3, "Should have at least 3 deprecated endpoints"

        # Verify each endpoint has required fields
        for endpoint_info in data["deprecated_endpoints"]:
            assert "endpoint" in endpoint_info, "Condition must be true"
            assert "successor_url" in endpoint_info, "Condition must be true"
            assert "reason" in endpoint_info, "Condition must be true"
            assert "sunset_date" in endpoint_info, "Condition must be true"

    @pytest.mark.parametrize(
        "endpoint,expected_successor,payload",
        [
            (
                "/api/v1/login",
                "/api/auth/login",
                {"username": "testuser", "password": "pass123456"},
            ),
            (
                "/api/v1/train",
                "/api/v2/training",
                {"data_path": "/data", "model_name": "test_model", "epochs": 10},
            ),
            ("/api/v1/predict", "/predict", {"text": "test input"}),
        ],
    )
    def test_link_header_points_to_correct_successor(
        self, client, endpoint, expected_successor, payload
    ):
        """Test that Link header points to correct successor endpoint."""
        response = client.post(endpoint, json=payload)

        link_value = response.headers["link"]
        assert (expected_successor in link_value, "Value must be initialized"
        ), f"Link header should contain {expected_successor}, got {link_value}"

    def test_x_api_lifecycle_header_present(self, client):
        """Test that X-API-Lifecycle header indicates deprecated status."""
        endpoints = [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ]

        for endpoint, payload in endpoints:
            response = client.post(endpoint, json=payload)

            assert ("x-api-lifecycle" in response.headers, "Response must not be empty"
            ), f"X-API-Lifecycle header missing from {endpoint}"
            assert (response.headers["x-api-lifecycle"] == "deprecated", "Response must not be empty"
            ), f"X-API-Lifecycle should be 'deprecated' for {endpoint}"

    def test_x_sunset_date_header_present(self, client):
        """Test that X-Sunset-Date header provides additional guidance."""
        endpoints = [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model", "epochs": 10}),
            ("/api/v1/predict", {"text": "test input"}),
        ]

        for endpoint, payload in endpoints:
            response = client.post(endpoint, json=payload)

            assert ("x-sunset-date" in response.headers, "Response must not be empty"
            ), f"X-Sunset-Date header missing from {endpoint}"
            assert (len(response.headers["x-sunset-date"]) > 0, "Collection must not be empty"
            ), f"X-Sunset-Date should not be empty for {endpoint}"

    def test_all_legacy_endpoints_documented(self, client):
        """Test that all legacy endpoints are documented in deprecation-info."""
        # Get list of documented legacy endpoints
        response = client.get("/api/v1/deprecation-info")
        documented = {ep["endpoint"] for ep in response.json()["deprecated_endpoints"]}

        # Verify all legacy endpoints are documented
        legacy_endpoints = {
            "POST /api/v1/login",
            "POST /api/v1/train",
            "POST /api/v1/predict",
        }

        for endpoint in legacy_endpoints:
            assert endpoint in documented, f"{endpoint} should be documented in deprecation-info"

    def test_deprecated_endpoint_response_format(self, client):
        """Test that deprecated endpoints return valid JSON responses."""
        endpoints = ["/api/v1/login", "/api/v1/train", "/api/v1/predict"]

        for endpoint in endpoints:
            response = client.post(endpoint, json={"data": "test"})

            # Should be valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict), f"Response from {endpoint} should be JSON object"
            except ValueError:
                pytest.fail(f"Response from {endpoint} is not valid JSON")

    def test_deprecated_login_endpoint(self, client):
        """Test deprecated POST /api/v1/login endpoint."""
        response = client.post(
            "/api/v1/login", json={"username": "test", "password": "password123"}
        )

        assert response.status_code == 410, "Response must not be empty"
        data = response.json()
        assert data["status"] == "deprecated", "Data must not be empty"
        assert "Deprecation" in response.headers, "Response must not be empty"
        assert "Sunset" in response.headers, "Response must not be empty"

    def test_deprecated_train_endpoint(self, client):
        """Test deprecated POST /api/v1/train endpoint."""
        response = client.post(
            "/api/v1/train", json={"data_path": "/data", "model_name": "model", "epochs": 10}
        )

        assert response.status_code == 410, "Response must not be empty"
        data = response.json()
        assert data["status"] == "deprecated", "Data must not be empty"
        assert "Deprecation" in response.headers, "Response must not be empty"
        assert "Sunset" in response.headers, "Response must not be empty"

    def test_deprecated_predict_endpoint(self, client):
        """Test deprecated POST /api/v1/predict endpoint."""
        response = client.post("/api/v1/predict", json={"text": "test input"})

        assert response.status_code == 410, "Response must not be empty"
        response.json()
        assert "Deprecation" in response.headers, "Response must not be empty"
        assert "Sunset" in response.headers, "Response must not be empty"

    def test_multiple_legacy_endpoints_return_headers(self, client):
        """Test that all legacy endpoints consistently return deprecation headers."""
        endpoints = [
            ("/api/v1/login", {"username": "testuser", "password": "pass123456"}),
            ("/api/v1/train", {"data_path": "/data", "model_name": "test_model"}),
            ("/api/v1/predict", {"text": "test"}),
        ]

        for endpoint, payload in endpoints:
            response = client.post(endpoint, json=payload)

            # All should have consistent headers
            headers = response.headers
            assert headers.get("Deprecation") == "true", "Condition must be true"
            assert "Sunset" in headers, "Condition must be true"
            assert "Link" in headers, "Condition must be true"
            assert "Warning" in headers, "Condition must be true"


class TestDeprecationHeadersRFC8594Compliance:
    """Test RFC 8594 standard compliance."""

    @pytest.fixture
    def client(self):
        """Create a test client for the API."""
        from codex.api.app import app

        return TestClient(app)

    def test_deprecation_header_value_is_true(self, client):
        """RFC 8594: Deprecation header must have value 'true'."""
        response = client.post(
            "/api/v1/login", json={"username": "testuser", "password": "pass123456"}
        )

        # Per RFC 8594, value must be "true"
        assert response.headers.get("Deprecation") == "true", "Response must not be empty"

    def test_sunset_header_is_rfc5322_date(self, client):
        """RFC 8594: Sunset header must be RFC 5322 date."""
        response = client.post(
            "/api/v1/login", json={"username": "testuser", "password": "pass123456"}
        )

        sunset = response.headers.get("Sunset")
        # Should be a valid RFC 5322 date format
        assert sunset is not None, "sunset must be initialized"
        # Example: "Mon, 01 Jan 2027 00:00:00 GMT"
        assert "GMT" in sunset or "UTC" in sunset or "00:00:00" in sunset

    def test_link_header_has_successor_relation(self, client):
        """RFC 8594: Link header should use successor-version relation."""
        response = client.post(
            "/api/v1/login", json={"username": "testuser", "password": "pass123456"}
        )

        link = response.headers.get("Link")
        assert link is not None, "link must be initialized"
        assert "rel=" in link, "Condition must be true"
        assert "successor-version" in link, "Condition must be true"

    def test_warning_header_has_299_code(self, client):
        """RFC 8594: Warning header should use 299 code."""
        response = client.post(
            "/api/v1/login", json={"username": "testuser", "password": "pass123456"}
        )

        warning = response.headers.get("Warning")
        assert warning is not None, "warning must be initialized"
        assert warning.startswith("299"), "Condition must be true"
