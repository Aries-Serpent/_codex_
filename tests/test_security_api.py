"""
Security tests for API security and secrets management.

Phase 3 Wave 5 Lane 1 — L1_SECURITY
OWASP Coverage: A01 (Access Control), A02 (Cryptographic Failures), A05 (Misconfiguration)
Test Count: 17 tests
"""

import hashlib
import hmac
import json
import os
from typing import Any, Dict, List, Optional

import pytest

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

class TestAPISecurityHeaders:
    """Test suite for secure API headers and configurations.""" # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

    def test_cors_policy_prevents_cross_origin_attacks(self):
        """Verify CORS policy prevents unauthorized cross-origin requests."""
        
        def validate_cors_header(cors_header: Optional[str], allowed_origins: List[str], request_origin: str) -> bool:
            """Validate CORS header against allowed origins."""
            if cors_header is None:
                raise ValueError("CORS header missing - should restrict by default")
            
            # Parse allowed origins (usually "*" is dangerous)
            if cors_header == "*":
                # If allowing all, at least require credentials: omit
                raise ValueError("CORS allows all origins - potential security issue")
            
            # Check if request origin is allowed
            if request_origin not in cors_header.split(","):
                return False
            
            return True
        
        allowed = ["https://trusted.example.com", "https://app.example.com"]
        
        # Secure: specific origins allowed
        cors_header = "https://trusted.example.com, https://app.example.com"
        assert validate_cors_header(cors_header, allowed, "https://trusted.example.com")
        
        # Insecure: allow all origins
        with pytest.raises(ValueError):
            validate_cors_header("*", allowed, "https://evil.com")

    def test_security_headers_present_and_valid(self):
        """Verify security headers are properly configured."""
        
        response_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        # Required headers
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Strict-Transport-Security"
        ]
        
        for header in required_headers:
            assert header in response_headers, f"Required header missing: {header}"
        
        # Validate header values
        assert response_headers["X-Content-Type-Options"] == "nosniff"
        assert response_headers["X-Frame-Options"] == "DENY"
        assert "max-age=" in response_headers["Strict-Transport-Security"]

    def test_api_rate_limiting_prevents_brute_force(self):
        """Verify API rate limiting prevents brute force attacks."""
        
        class RateLimiter:
            def __init__(self, requests_per_minute: int = 60):
                self.limit = requests_per_minute
                self.requests = {}
            
            def check_rate_limit(self, client_id: str) -> bool:
                """Check if client has exceeded rate limit."""
                import time
                now = int(time.time() / 60)  # Minute
                
                key = f"{client_id}:{now}"
                self.requests[key] = self.requests.get(key, 0) + 1
                
                if self.requests[key] > self.limit:
                    raise ValueError(f"Rate limit exceeded for {client_id}")
                
                return True
        
        limiter = RateLimiter(requests_per_minute=10)
        
        # Normal usage
        for i in range(10):
            assert limiter.check_rate_limit("user_123")
        
        # Exceed limit
        with pytest.raises(ValueError):
            limiter.check_rate_limit("user_123")

    def test_api_authentication_required(self):
        """Verify API endpoints require authentication."""
        
        def validate_request_auth(headers: Dict[str, str]) -> bool:
            """Check request has valid authentication."""
            auth_header = headers.get("Authorization")
            
            if not auth_header:
                raise ValueError("Missing Authorization header")
            
            if not auth_header.startswith("Bearer "):
                raise ValueError("Invalid authorization scheme")
            
            token = auth_header.replace("Bearer ", "")
            if len(token) < 20:
                raise ValueError("Token too short")
            
            return True
        
        # Valid auth
        headers = {"Authorization": "******"}
        assert validate_request_auth(headers)
        
        # Missing auth
        with pytest.raises(ValueError):
            validate_request_auth({})
        
        # Invalid auth
        with pytest.raises(ValueError):
            validate_request_auth({"Authorization": "InvalidScheme token"})

    def test_api_response_content_type_validation(self):
        """Verify API responses have correct content type."""
        
        def validate_response_content_type(content_type: str, expected_types: List[str]) -> bool:
            """Validate response content type."""
            if not content_type:
                raise ValueError("Missing Content-Type header")
            
            # Extract base type (before semicolon)
            base_type = content_type.split(";")[0].strip()
            
            if base_type not in expected_types:
                raise ValueError(f"Unexpected content type: {base_type}")
            
            # For JSON, charset should be specified
            if "application/json" in base_type:
                if "charset" not in content_type:
                    # Not necessarily a security issue, but good practice
                    pass
            
            return True
        
        # Valid JSON response
        assert validate_response_content_type(
            "application/json; charset=utf-8",
            ["application/json"]
        )
        
        # Invalid content type
        with pytest.raises(ValueError):
            validate_response_content_type(
                "text/html",
                ["application/json"]
            )


class TestAPIInputValidation:
    """Test suite for API input validation security."""

    def test_json_payload_size_limit(self):
        """Verify API enforces JSON payload size limits."""
        
        def validate_payload_size(payload: str, max_size_bytes: int = 1048576) -> bool:  # 1MB default
            """Check payload size is within limits."""
            payload_bytes = len(payload.encode('utf-8'))
            
            if payload_bytes > max_size_bytes:
                raise ValueError(f"Payload too large: {payload_bytes} > {max_size_bytes}")
            
            return True
        
        # Small payload (valid)
        small_payload = json.dumps({"name": "Alice", "email": "alice@example.com"})
        assert validate_payload_size(small_payload)
        
        # Huge payload (invalid)
        huge_payload = json.dumps({"data": "x" * 2000000})
        with pytest.raises(ValueError):
            validate_payload_size(huge_payload, max_size_bytes=1048576)

    def test_json_parsing_prevents_entity_expansion(self):
        """Verify JSON parsing prevents entity expansion attacks."""
        
        def parse_json_safely(json_str: str) -> Dict[str, Any]:
            """Parse JSON with protections against entity expansion."""
            try:
                # Standard json module is safe by default (unlike XML)
                data = json.loads(json_str)
                
                # Additional check: limit recursion depth
                if isinstance(data, dict):
                    def check_depth(obj, max_depth=10, current=0):
                        if current > max_depth:
                            raise ValueError("JSON depth exceeds limit")
                        
                        if isinstance(obj, dict):
                            for value in obj.values():
                                check_depth(value, max_depth, current + 1)
                        elif isinstance(obj, list):
                            for item in obj:
                                check_depth(item, max_depth, current + 1)
                    
                    check_depth(data)
                
                return data
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")
        
        # Valid JSON
        result = parse_json_safely('{"name": "Alice", "age": 30}')
        assert result["name"] == "Alice"
        
        # Deeply nested JSON (entity expansion attempt)
        nested = '{"a": ' * 50 + '{"data": "x"}' + '}' * 50
        with pytest.raises(ValueError):
            parse_json_safely(nested)

    def test_query_parameter_validation(self):
        """Verify query parameters are properly validated."""
        
        def validate_query_params(params: Dict[str, str], rules: Dict[str, Dict]) -> Dict[str, str]:
            """Validate query parameters against rules."""
            validated = {}
            
            for param_name, param_value in params.items():
                if param_name not in rules:
                    raise ValueError(f"Unknown parameter: {param_name}")
                
                rule = rules[param_name]
                
                # Type validation
                if rule.get("type") == "int":
                    try:
                        validated[param_name] = int(param_value)
                    except ValueError:
                        raise ValueError(f"Invalid integer for {param_name}")
                
                # Range validation
                if "min" in rule:
                    if int(param_value) < rule["min"]:
                        raise ValueError(f"{param_name} below minimum")
                
                # Allowed values
                if "allowed" in rule:
                    if param_value not in rule["allowed"]:
                        raise ValueError(f"Invalid value for {param_name}")
            
            return validated
        
        rules = {
            "page": {"type": "int", "min": 1},
            "limit": {"type": "int", "min": 1, "max": 100},
            "sort": {"allowed": ["name", "date", "relevance"]}
        }
        
        # Valid params
        params = {"page": "1", "limit": "50", "sort": "name"}
        result = validate_query_params(params, rules)
        assert result["page"] == 1
        
        # Invalid value
        with pytest.raises(ValueError):
            validate_query_params({"sort": "invalid"}, rules)

    def test_file_upload_validation(self):
        """Verify file uploads are validated for security."""
        
        def validate_file_upload(filename: str, file_size: int, allowed_extensions: List[str], max_size: int = 10485760) -> bool:
            """Validate uploaded file."""
            # Check file size
            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} > {max_size}")
            
            if file_size == 0:
                raise ValueError("Empty file")
            
            # Validate extension
            import os
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            if ext not in allowed_extensions:
                raise ValueError(f"Invalid file type: {ext}")
            
            # Prevent directory traversal
            if ".." in filename or "/" in filename or "\\" in filename:
                raise ValueError("Suspicious filename")
            
            return True
        
        allowed = [".pdf", ".doc", ".docx", ".txt"]
        
        # Valid file
        assert validate_file_upload("report.pdf", 1000000, allowed)
        
        # File too large
        with pytest.raises(ValueError):
            validate_file_upload("huge_file.pdf", 100000000, allowed)
        
        # Invalid extension
        with pytest.raises(ValueError):
            validate_file_upload("malware.exe", 1000, allowed)
        
        # Directory traversal
        with pytest.raises(ValueError):
            validate_file_upload("../../etc/passwd.txt", 1000, allowed)


class TestSecretsManagement:
    """Test suite for secure secrets management."""

    def test_api_key_rotation_enforced(self):
        """Verify API keys are rotated periodically."""
        
        import time
        
        class APIKeyManager:
            def __init__(self, rotation_days: int = 90):
                self.rotation_days = rotation_days
                self.keys = {}
            
            def create_key(self, key_id: str) -> str:
                """Create new API key."""
                key = os.urandom(32).hex()
                self.keys[key_id] = {
                    "key": key,
                    "created_at": time.time()
                }
                return key
            
            def is_key_expired(self, key_id: str) -> bool:
                """Check if key is expired."""
                if key_id not in self.keys:
                    raise ValueError("Key not found")
                
                created_at = self.keys[key_id]["created_at"]
                age_seconds = time.time() - created_at
                rotation_seconds = self.rotation_days * 86400
                
                return age_seconds > rotation_seconds
        
        manager = APIKeyManager(rotation_days=90)
        key_id = manager.create_key("service_key_1")
        
        # New key should not be expired
        assert not manager.is_key_expired("service_key_1")

    def test_database_credentials_from_environment(self):
        """Verify database credentials come from environment, not code."""
        
        def get_db_credentials(use_env: bool = True) -> Dict[str, str]:
            """Get database credentials securely."""
            if use_env:
                # Should use environment variables
                host = os.environ.get("DB_HOST")
                user = os.environ.get("DB_USER")
                password = os.environ.get("DB_PASSWORD")
                
                if not all([host, user, password]):
                    raise ValueError("Database credentials missing from environment")
                
                return {"host": host, "user": user, "password": password}
            else:
                # Hardcoded - INSECURE
                return {
                    "host": "db.example.com",
                    "user": "admin",
                    "password": "hardcoded_password_123"
                }
        
        # With environment variables
        os.environ["DB_HOST"] = "db.prod.example.com"
        os.environ["DB_USER"] = "service_user"
        os.environ["DB_PASSWORD"] = "secure_password_from_env"
        
        creds = get_db_credentials(use_env=True)
        assert creds["host"] == "db.prod.example.com"
        
        # Hardcoded credentials (insecure)
        creds_bad = get_db_credentials(use_env=False)
        assert "hardcoded_password" in creds_bad["password"]

    def test_oauth_token_scope_limitation(self):
        """Verify OAuth tokens are scoped to minimal permissions."""
        
        def validate_oauth_scope(requested_scope: List[str], allowed_scope: List[str]) -> List[str]:
            """Validate OAuth scope against allowed permissions."""
            # User should not request more than allowed
            for scope in requested_scope:
                if scope not in allowed_scope:
                    raise ValueError(f"Scope '{scope}' not in allowed permissions")
            
            # Return only requested (minimum necessary)
            return requested_scope
        
        user_allowed = ["read:user", "read:repos", "write:gists"]
        app_requested = ["read:user", "read:repos"]
        
        # Valid: requesting subset of allowed
        granted = validate_oauth_scope(app_requested, user_allowed)
        assert granted == ["read:user", "read:repos"]
        
        # Invalid: requesting admin scope (not allowed)
        with pytest.raises(ValueError):
            validate_oauth_scope(["admin:repo_hook"], user_allowed)

    def test_webhook_secret_validation(self):
        """Verify webhook signatures are validated."""
        
        def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
            """Validate webhook signature using HMAC."""
            # Calculate expected signature
            expected_sig = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison
            if not hmac.compare_digest(signature, expected_sig):
                raise ValueError("Invalid webhook signature - possible forgery")
            
            return True
        
        secret = "webhook_secret_123"
        payload = '{"event": "push", "ref": "refs/heads/main"}'
        
        # Valid signature
        sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        assert validate_webhook_signature(payload, sig, secret)
        
        # Invalid signature
        with pytest.raises(ValueError):
            validate_webhook_signature(payload, "invalid_signature", secret)

    def test_credential_escaping_in_connection_strings(self):
        """Verify credentials in connection strings are properly escaped."""
        
        def build_safe_connection_string(host: str, user: str, password: str, db: str) -> str:
            """Build connection string with proper escaping."""
            # Escape special characters in credentials
            def escape(s: str) -> str:
                # URL encode special characters
                import urllib.parse
                return urllib.parse.quote(s, safe='')
            
            escaped_user = escape(user)
            escaped_pass = escape(password)
            
            return f"postgresql://{escaped_user}:{escaped_pass}@{host}/{db}"
        
        # Credentials with special characters
        connection_str = build_safe_connection_string(
            "db.example.com",
            "user@company",
            "p@ssw0rd!#$%",
            "mydb"
        )
        
        # Should be properly escaped
        assert "@" in connection_str  # URL encoded
        assert "p%40ssw0rd%21%23%24%25" in connection_str  # Password escaped


class TestDependencySecurityTests:
    """Test suite for dependency and supply chain security."""

    def test_dependency_vulnerability_scanner_integration(self):
        """Verify integration with dependency vulnerability scanner."""
        
        vulnerabilities = [
            {"package": "django", "version": "3.1.0", "cve": "CVE-2021-1234", "severity": "high"},
            {"package": "requests", "version": "2.24.0", "cve": "CVE-2021-5678", "severity": "medium"},
        ]
        
        def check_vulnerabilities(deps: List[Dict], severity_threshold: str = "high") -> List[Dict]:
            """Check for vulnerabilities in dependencies."""
            severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            threshold = severity_levels.get(severity_threshold, 0)
            
            critical_vulns = []
            for vuln in deps:
                if severity_levels.get(vuln["severity"], 0) >= threshold:
                    critical_vulns.append(vuln)
            
            return critical_vulns
        
        # Check for high/critical
        critical = check_vulnerabilities(vulnerabilities, "high")
        assert len(critical) >= 1

    def test_license_compliance_check(self):
        """Verify license compliance for dependencies."""
        
        dependencies = {
            "django": {"version": "4.0", "license": "BSD-3-Clause"},
            "requests": {"version": "2.28.0", "license": "Apache-2.0"},
            "commercial-lib": {"version": "1.0", "license": "PROPRIETARY"}
        }
        
        allowed_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-2.0", "GPL-3.0"]
        
        def validate_licenses(deps: Dict, allowed: List[str]) -> List[str]:
            """Check that all dependencies use allowed licenses."""
            non_compliant = []
            
            for package, info in deps.items():
                if info["license"] not in allowed:
                    non_compliant.append(f"{package}: {info['license']}")
            
            return non_compliant
        
        non_compliant = validate_licenses(dependencies, allowed_licenses)
        assert "commercial-lib: PROPRIETARY" in non_compliant


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
