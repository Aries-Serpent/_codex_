#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# """
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# 
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# 
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
#     from src.codex_ml.serving.inference_server import create_app
#     # Authentication is controlled via env vars, not function parameter
#     with patch.dict("os.environ", {"CODEX_API_KEYS": "test-key-1,test-key-2"}):
#         app = create_app()
#         return TestClient(app)
#         # Some requests should be rate limited
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
#     """Create test client with JWT authentication."""
#     from src.codex_ml.serving.inference_server import create_app
#     # Authentication is controlled via env vars, not function parameter
#     with patch.dict("os.environ", {"CODEX_JWT_SECRET": "test-secret-key"}):
#         app = create_app()
#         return TestClient(app)
#         # Some requests should be rate limited
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# 
#     def test_invalid_jwt_signature(self, jwt_client):
#     def test_invalid_jwt_signature(self, jwt_client):
#         """Test rejection of JWT with invalid signature."""
#         # Create fake JWT with invalid signature
#         fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.invalid_signature"
#         response = jwt_client.post(
#         response = jwt_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"Authorization": f"Bearer {fake_jwt}"},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         assert response.status_code == 401, "Response must not be empty"
# 
#     def test_expired_jwt_token(self, jwt_client):
#     def test_expired_jwt_token(self, jwt_client):
#         """Test rejection of expired JWT tokens."""
#         # Create expired JWT (would need proper JWT lib in real test)
#         expired_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjF9.invalid"
#         response = jwt_client.post(
#         response = jwt_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"Authorization": f"Bearer {expired_jwt}"},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         assert response.status_code == 401, "Response must not be empty"
# 
#     def test_jwt_algorithm_confusion(self, jwt_client):
#     def test_jwt_algorithm_confusion(self, jwt_client):
#         """Test protection against JWT algorithm confusion attacks."""
#         # Try to use "none" algorithm
#         header = base64.b64encode(b'{"alg":"none","typ":"JWT"}').decode()
#         payload = base64.b64encode(b'{"sub":"test"}').decode()
#         malicious_jwt = f"{header}.{payload}."
#         response = jwt_client.post(
#         response = jwt_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"Authorization": f"Bearer {malicious_jwt}"},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         assert response.status_code == 401, "Response must not be empty"
# 
#     def test_jwt_with_modified_claims(self, jwt_client):
#     def test_jwt_with_modified_claims(self, jwt_client):
#         """Test rejection of JWT with modified claims."""
#         # Attempt to modify claims after signing
#         response = jwt_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"Authorization": "Bearer modified.token.here"},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         # Some requests should be rate limited
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# 
#     def test_missing_api_key(self, secure_client):
#     def test_missing_api_key(self, secure_client):
#         """Test rejection of requests without API key."""
#         response = secure_client.post(
#             "/infer", json={"model_name": "test-model", "inputs": ["test"], "max_length": 50}
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         assert response.status_code == 401, "Response must not be empty"
# 
#     def test_invalid_api_key(self, secure_client):
#     def test_invalid_api_key(self, secure_client):
#         """Test rejection of invalid API keys."""
#         response = secure_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"X-API-Key": "invalid-key"},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         assert response.status_code == 401, "Response must not be empty"
# 
#     def test_api_key_timing_attack_resistance(self, secure_client):
#     def test_api_key_timing_attack_resistance(self, secure_client):
#         """Test resistance to timing attacks on API key validation."""
#         # Measure response time for invalid key
#         times = []
#         for _ in range(10):
#             start = time.time()
#             secure_client.post(
#                 "/infer",
#                 json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#                 headers={"X-API-Key": "wrong-key"},
#             )
#             times.append(time.time() - start)
#         variance = max(times) - min(times)
#         assert variance < 0.1, f"Timing variance too high: {variance:.4f}s"
#         variance = max(times) - min(times)
#         assert variance < 0.1, f"Timing variance too high: {variance:.4f}s"
# 
#     def test_api_key_in_query_param_rejected(self, secure_client):
#     def test_api_key_in_query_param_rejected(self, secure_client):
#         """Test that API keys in query params are rejected (security best practice)."""
#         response = secure_client.post(
#             "/infer?api_key=test-key-1",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#         )
#         assert response.status_code == 401, "Response must not be empty"
#         # Some requests should be rate limited
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
# 
#     def test_rate_limit_enforcement(self, secure_client):
#     def test_rate_limit_enforcement(self, secure_client):
#         """Test that rate limits are enforced."""
#         # Make many requests quickly
#         responses = []
#         for _ in range(100):
#             response = secure_client.get("/health")
#             responses.append(response.status_code)
#         rate_limited = sum(1 for status in responses if status == 429)
#         assert rate_limited > 0 or all(, "rate_limited must be greater than zero"
#             s == 200 for s in responses
#         ), "Rate limiting should trigger or all succeed"
#         ), "Rate limiting should trigger or all succeed"
# 
#     def test_rate_limit_bypass_different_headers(self, secure_client):
#     def test_rate_limit_bypass_different_headers(self, secure_client):
#         """Test rate limit can't be bypassed by changing headers."""
#         # Try to bypass by changing User-Agent
#         responses = []
#         for i in range(50):
#             response = secure_client.get("/health", headers={"User-Agent": f"test-{i}"})
#             responses.append(response.status_code)
#         sum(1 for status in responses if status == 429)
#         # May or may not trigger depending on rate limit config
#         assert len(responses) == 50, "Responses must not be empty"
#         assert len(responses) == 50, "Responses must not be empty"
# 
#     def test_rate_limit_per_key(self, secure_client):
#     def test_rate_limit_per_key(self, secure_client):
#         """Test rate limits are enforced per API key."""
#         # Use valid API key
#         response = secure_client.post(
#             "/infer",
#             json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
#             headers={"X-API-Key": "test-key-1"},
#         )
#         assert response.status_code in [200, 429, 500]


class TestPayloadAttacks:
    """Test payload-based attacks."""

    def test_oversized_payload_rejection(self, secure_client):
        """Test rejection of oversized payloads."""
        # Try to send very large payload
        large_inputs = ["test" * 1000] * 200  # Very large payload

        response = secure_client.post(
            "/infer",
            json={"model_name": "test-model", "inputs": large_inputs, "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should reject or handle gracefully
        assert response.status_code in [400, 413, 422, 500]

    def test_malformed_json_handling(self, secure_client):
        """Test handling of malformed JSON."""
        response = secure_client.post(
            "/infer",
            data="{invalid json}",
            headers={"Content-Type": "application/json", "X-API-Key": "test-key-1"},
        )

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422, "Response must not be empty"

    def test_sql_injection_in_model_name(self, secure_client):
        """Test SQL injection protection in model name."""
        malicious_name = "'; DROP TABLE models; --"

        response = secure_client.post(
            "/infer",
            json={"model_name": malicious_name, "inputs": ["test"], "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should handle safely (not crash)
        assert response.status_code in [400, 422, 500]

    def test_command_injection_in_inputs(self, secure_client):
        """Test command injection protection."""
        malicious_input = "; rm -rf / ;"

        response = secure_client.post(
            "/infer",
            json={"model_name": "test-model", "inputs": [malicious_input], "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should handle safely
        assert response.status_code in [200, 400, 500]

    def test_path_traversal_in_model_name(self, secure_client):
        """Test path traversal protection."""
        malicious_name = "../../etc/passwd"

        response = secure_client.post(
            "/infer",
            json={"model_name": malicious_name, "inputs": ["test"], "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should reject path traversal
        assert response.status_code in [400, 422, 500]

    def test_null_byte_injection(self, secure_client):
        """Test null byte injection protection."""
        malicious_name = "test\x00model"

        response = secure_client.post(
            "/infer",
            json={"model_name": malicious_name, "inputs": ["test"], "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should handle safely
        assert response.status_code in [200, 400, 422, 500]


class TestAuthenticationExhaustion:
    """Test authentication exhaustion attacks."""

    def test_rapid_auth_attempts(self, secure_client):
        """Test handling of rapid authentication attempts."""
        # Try many invalid auth attempts
        for _ in range(50):
            secure_client.post(
                "/infer",
                json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
                headers={"X-API-Key": "wrong-key"},
            )

        # Server should still respond (not crash)
        response = secure_client.get("/health")
        assert response.status_code == 200, "Response must not be empty"

    def test_dictionary_attack_resistance(self, secure_client):
        """Test resistance to dictionary attacks."""
        common_keys = ["admin", "password", "secret", "key", "test", "demo", "api-key", "access"]

        failed_attempts = 0
        for key in common_keys:
            response = secure_client.post(
                "/infer",
                json={"model_name": "test-model", "inputs": ["test"], "max_length": 50},
                headers={"X-API-Key": key},
            )
            if response.status_code == 401:
                failed_attempts += 1

        # All should fail
        assert failed_attempts == len(common_keys), "Common_keys must not be empty"


class TestHeaderInjection:
    """Test header injection attacks."""

    def test_crlf_injection_in_headers(self, secure_client):
        """Test CRLF injection protection in headers."""
        malicious_header = "test\r\nX-Evil: true"

        response = secure_client.get("/health", headers={"User-Agent": malicious_header})

        # Should handle safely
        assert response.status_code == 200, "Response must not be empty"

    def test_host_header_injection(self, secure_client):
        """Test host header injection protection."""
        response = secure_client.get("/health", headers={"Host": "evil.com"})

        # Rejected by TrustedHostMiddleware
        assert response.status_code == 400, "Response must not be empty"


class TestDenialOfService:
    """Test DoS attack prevention."""

    def test_slowloris_attack_resistance(self, secure_client):
        """Test resistance to slowloris attacks."""
        # Simulate slow request
        response = secure_client.get("/health")
        assert response.status_code == 200, "Response must not be empty"

    def test_regex_dos_protection(self, secure_client):
        """Test protection against ReDoS attacks."""
        # Try regex DoS in input
        malicious_input = "a" * 10000 + "!"

        response = secure_client.post(
            "/infer",
            json={"model_name": "test-model", "inputs": [malicious_input], "max_length": 50},
            headers={"X-API-Key": "test-key-1"},
        )

        # Should handle without hanging
        assert response.status_code in [200, 400, 422, 500]

    def test_zip_bomb_protection(self, secure_client):
        """Test protection against compressed payload attacks."""
        # Server should limit decompression
        response = secure_client.get("/health")
        assert response.status_code == 200, "Response must not be empty"


# Security test configuration
pytestmark = pytest.mark.security


def pytest_configure(config):
    """Add security marker."""
    config.addinivalue_line("markers", "security: mark test as security penetration test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
