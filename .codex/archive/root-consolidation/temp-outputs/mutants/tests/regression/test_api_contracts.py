#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
# 
# All tests use FastAPI's in-process ``TestClient`` (no live server needed).
#         """GET /readiness must return 2xx (200 ready or 503 not-ready — never 4xx/5xx)."""
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# import pytest
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# # ────────────────────────────────────────────────────────────────────────────
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
#         resp = dashboard_client.get("/")
#         assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
# 
#     def test_root_schema_contains_name_and_version(self, dashboard_client):
#     def test_root_schema_contains_name_and_version(self, dashboard_client):
#         """Root response must expose 'name' and 'version' fields."""
#         body = dashboard_client.get("/").json()
#         assert "name" in body, "Root response missing 'name'"
#         assert "version" in body, "Root response missing 'version'"
#     def test_root_endpoints_map_present(self, dashboard_client):
#     def test_root_endpoints_map_present(self, dashboard_client):
#         """Root response must include an 'endpoints' mapping for discovery."""
#         body = dashboard_client.get("/").json()
#         assert "endpoints" in body, "Root response missing 'endpoints'"
#         assert isinstance(body["endpoints"], dict), "'endpoints' must be a dict"
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
#         assert resp.status_code == 200, "status_code is not valid"
# 
#     def test_health_schema_status_field(self, dashboard_client):
#     def test_health_schema_status_field(self, dashboard_client):
#         """Health response must contain a 'status' string field."""
#         body = dashboard_client.get("/health").json()
#         assert "status" in body, "Health response missing 'status'"
#         assert isinstance(body["status"], str)
#     def test_health_schema_timestamp_field(self, dashboard_client):
#     def test_health_schema_timestamp_field(self, dashboard_client):
#         """Health response must contain a 'timestamp' field."""
#         body = dashboard_client.get("/health").json()
#         assert "timestamp" in body, "Health response missing 'timestamp'"
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
#         assert resp.status_code == 200, "status_code is not valid"
# 
#     def test_liveness_schema(self, dashboard_client):
#     def test_liveness_schema(self, dashboard_client):
#         """Liveness response must expose status, uptime_seconds, and timestamp."""
#         body = dashboard_client.get("/liveness").json()
#         assert "status" in body, "Liveness missing 'status'"
#         assert "uptime_seconds" in body, "Liveness missing 'uptime_seconds'"
#         assert "timestamp" in body, "Liveness missing 'timestamp'"
#     def test_liveness_uptime_non_negative(self, dashboard_client):
#     def test_liveness_uptime_non_negative(self, dashboard_client):
#         """Uptime must be a non-negative numeric value."""
#         body = dashboard_client.get("/liveness").json()
#         uptime = body["uptime_seconds"]
#         assert isinstance(uptime, (int, float)), "uptime_seconds must be numeric"
#         assert uptime >= 0, f"uptime_seconds is negative: {uptime}"
#     def test_liveness_status_value(self, dashboard_client):
#     def test_liveness_status_value(self, dashboard_client):
#         """Liveness status field must be 'alive'."""
#         body = dashboard_client.get("/liveness").json()
#         assert body["status"] == "alive", f"Expected status='alive', got {body['status']!r}"
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
#         resp = dashboard_client.get("/readiness")
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
#         assert resp.status_code in (, "Condition must be true"
#             200,
#             503,
#         ), f"Expected 200 or 503 from /readiness, got {resp.status_code}"
# 
#     def test_readiness_schema_status_field(self, dashboard_client):
#     def test_readiness_schema_status_field(self, dashboard_client):
#         """Readiness response must always contain a 'status' field."""
#         body = dashboard_client.get("/readiness").json()
#         assert "status" in body, "Readiness response missing 'status'"
#     def test_readiness_schema_checks_field(self, dashboard_client):
#     def test_readiness_schema_checks_field(self, dashboard_client):
#         """Readiness response must expose a 'checks' object describing sub-checks."""
#         body = dashboard_client.get("/readiness").json()
#         assert "checks" in body, "Readiness response missing 'checks'"
#     def test_readiness_schema_timestamp_field(self, dashboard_client):
#     def test_readiness_schema_timestamp_field(self, dashboard_client):
#         """Readiness response must contain a 'timestamp' ISO-8601 string."""
#         body = dashboard_client.get("/readiness").json()
#         assert "timestamp" in body, "Readiness response missing 'timestamp'"
#         assert isinstance(body["timestamp"], str)
#         assert "application/json" in resp.headers.get(, "Condition must be true"
# 
# # ────────────────────────────────────────────────────────────────────────────
# # 5. Content-type contract
# # ────────────────────────────────────────────────────────────────────────────
#         assert "application/json" in resp.headers.get(, "Condition must be true"
# 
#         assert "application/json" in resp.headers.get(, "Condition must be true"
#     def test_health_content_type_json(self, dashboard_client):
#         """All JSON endpoints must return application/json content type."""
#         resp = dashboard_client.get("/health")
#         assert "application/json" in resp.headers.get(, "Condition must be true"
#             "content-type", ""
#         ), "Expected JSON content-type on /health"
#     def test_liveness_content_type_json(self, dashboard_client):
#     def test_liveness_content_type_json(self, dashboard_client):
#         """Liveness endpoint must return application/json."""
#         resp = dashboard_client.get("/liveness")
#         assert "application/json" in resp.headers.get("content-type", "")
#     def test_readiness_content_type_json(self, dashboard_client):
#     def test_readiness_content_type_json(self, dashboard_client):
#         """Readiness endpoint must return application/json."""
#         resp = dashboard_client.get("/readiness")
#         assert "application/json" in resp.headers.get("content-type", "")
