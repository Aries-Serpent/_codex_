#!/usr/bin/env python3
"""
Security Validation Script for Authentication Module

Performs comprehensive security checks on the authentication system.

Usage:
    Run from project root with PYTHONPATH set:
        PYTHONPATH=. python scripts/validate_auth_security.py
    
    Or install the package first:
        pip install -e .
        python scripts/validate_auth_security.py
"""

from src.codex.auth import OAuthManager, MFAProvider, TokenManager
import time, sys


class SecurityValidator:
    """Security validation test suite."""
    
    def __init__(self):
        """Initialize validators."""
        self.oauth = OAuthManager()
        self.mfa = MFAProvider()
        self.tokens = TokenManager()
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str, condition: bool, message: str = ""):
        """Run a test and track results."""
        if condition:
            print(f"✅ {name}: PASS")
            self.passed += 1
        else:
            print(f"❌ {name}: FAIL - {message}")
            self.failed += 1
    
    def validate_pkce(self):
        """Validate PKCE implementation."""
        print("\n🔒 Testing PKCE Security")
        print("-" * 60)
        
        # Test 1: Verify code verifier generation
        verifier = self.oauth._generate_code_verifier()
        self.test(
            "PKCE Verifier Generation",
            len(verifier) >= 43,
            f"Verifier too short: {len(verifier)}"
        )
        
        # Test 2: Verify challenge generation
        challenge = self.oauth._generate_code_challenge(verifier)
        self.test(
            "PKCE Challenge Generation",
            len(challenge) > 0 and challenge != verifier,
            "Challenge same as verifier"
        )
        
        # Test 3: Verify deterministic challenge
        challenge2 = self.oauth._generate_code_challenge(verifier)
        self.test(
            "PKCE Deterministic",
            challenge == challenge2,
            "Challenge not deterministic"
        )
        
        # Test 4: Verify different verifiers produce different challenges
        verifier2 = self.oauth._generate_code_verifier()
        challenge3 = self.oauth._generate_code_challenge(verifier2)
        self.test(
            "PKCE Unique Challenges",
            challenge != challenge3,
            "Different verifiers produce same challenge"
        )
    
    def validate_rate_limiting(self):
        """Validate rate limiting."""
        print("\n🔒 Testing Rate Limiting")
        print("-" * 60)
        
        # Test 1: Normal operation
        user_id = "rate_test_user"
        secret = self.mfa.generate_totp_secret(user_id)
        valid_code = self.mfa.generate_totp(secret.secret)
        
        result = self.mfa.verify_totp(secret.secret, valid_code, user_id)
        self.test("Normal Verification", result, "Valid code rejected")
        
        # Test 2: Failed attempts trigger lockout
        for i in range(self.mfa.MAX_ATTEMPTS):
            self.mfa.verify_totp(secret.secret, "000000", user_id)
        
        locked = self.mfa._is_locked_out(user_id)
        self.test(
            f"Lockout after {self.mfa.MAX_ATTEMPTS} failures",
            locked,
            "User not locked out"
        )
        
        # Test 3: Valid code rejected during lockout
        valid_code = self.mfa.generate_totp(secret.secret)
        result = self.mfa.verify_totp(secret.secret, valid_code, user_id)
        self.test(
            "Valid code rejected during lockout",
            not result,
            "Valid code accepted during lockout"
        )
    
    def validate_token_security(self):
        """Validate token security."""
        print("\n🔒 Testing Token Security")
        print("-" * 60)
        
        # Test 1: Token signature verification
        token = self.tokens.generate_access_token("user1")
        
        # Try to tamper with token
        parts = token.split('.')
        tampered = parts[0] + '.' + parts[1] + '.TAMPERED'
        
        try:
            self.tokens.validate_token(tampered)
            self.test("Token Tampering Detection", False, "Tampered token accepted")
        except ValueError:
            self.test("Token Tampering Detection", True)
        
        # Test 2: Token expiry
        claims = self.tokens._decode_token(token)
        expired_claims = type(claims)(
            sub=claims.sub,
            iat=time.time() - 1000,
            exp=time.time() - 100,
            type=claims.type,
            jti=claims.jti
        )
        expired_token = self.tokens._encode_token(expired_claims)
        
        try:
            self.tokens.validate_token(expired_token)
            self.test("Token Expiry Check", False, "Expired token accepted")
        except ValueError as e:
            self.test("Token Expiry Check", "expired" in str(e).lower())
        
        # Test 3: Token revocation
        revoke_token = self.tokens.generate_access_token("user2")
        self.tokens.revoke_token(revoke_token)
        
        try:
            self.tokens.validate_token(revoke_token)
            self.test("Token Revocation", False, "Revoked token accepted")
        except ValueError:
            self.test("Token Revocation", True)
        
        # Test 4: Different keys produce different tokens
        manager2 = TokenManager(secret_key="different_key")
        token2 = manager2.generate_access_token("user1")
        self.test(
            "Token Key Uniqueness",
            token != token2,
            "Same tokens with different keys"
        )
    
    def validate_mfa_security(self):
        """Validate MFA security."""
        print("\n🔒 Testing MFA Security")
        print("-" * 60)
        
        # Test 1: TOTP time window
        user_id = "mfa_test_user"
        secret = self.mfa.generate_totp_secret(user_id)
        
        # Code from 2 periods ago should fail with window=1
        old_code = self.mfa.generate_totp(secret.secret, time.time() - 60)
        result = self.mfa.verify_totp(secret.secret, old_code, user_id, window=1)
        self.test(
            "TOTP Time Window",
            not result,
            "Old code accepted outside window"
        )
        
        # Test 2: Backup code single use
        backup_codes = self.mfa.generate_backup_codes(user_id, count=5)
        code = backup_codes[0]
        
        result1 = self.mfa.verify_backup_code(user_id, code)
        result2 = self.mfa.verify_backup_code(user_id, code)
        
        self.test(
            "Backup Code Single Use",
            result1 and not result2,
            "Backup code reused successfully"
        )
        
        # Test 3: Secret uniqueness
        secret1 = self.mfa.generate_totp_secret("user1")
        secret2 = self.mfa.generate_totp_secret("user2")
        self.test(
            "MFA Secret Uniqueness",
            secret1.secret != secret2.secret,
            "Same secrets generated"
        )
    
    def validate_session_security(self):
        """Validate session security."""
        print("\n🔒 Testing Session Security")
        print("-" * 60)
        
        # Test 1: Session isolation
        token1, session1 = self.tokens.generate_session_token("user1", True)
        token2, session2 = self.tokens.generate_session_token("user2", False)
        
        self.test(
            "Session ID Uniqueness",
            session1 != session2,
            "Same session IDs for different users"
        )
        
        # Test 2: Session activity tracking
        session = self.tokens.get_session(session1)
        old_activity = session.last_activity
        
        time.sleep(0.1)
        self.tokens.validate_token(token1)
        
        session = self.tokens.get_session(session1)
        self.test(
            "Session Activity Tracking",
            session.last_activity > old_activity,
            "Activity not updated"
        )
        
        # Test 3: Revoke all user sessions
        self.tokens.generate_session_token("user1", True)
        self.tokens.generate_session_token("user1", False)
        
        count = self.tokens.revoke_all_user_tokens("user1")
        self.test(
            "Revoke All User Sessions",
            count >= 3,  # At least the 3 we created
            f"Only {count} sessions revoked"
        )
        
        # Verify sessions are gone
        session = self.tokens.get_session(session1)
        self.test(
            "Sessions Actually Revoked",
            session is None,
            "Session still exists after revocation"
        )
    
    def validate_secure_defaults(self):
        """Validate secure defaults."""
        print("\n🔒 Testing Secure Defaults")
        print("-" * 60)
        
        # Test 1: PKCE enabled by default
        config = self.oauth.create_github_config(
            client_id="test",
            client_secret="test",
            redirect_uri="http://localhost",
        )
        self.test(
            "PKCE Enabled by Default",
            config.use_pkce is True,
            "PKCE not enabled by default"
        )
        
        # Test 2: Token expiry times are reasonable
        self.test(
            "Access Token Expiry",
            self.tokens.ACCESS_TOKEN_EXPIRY <= 900,  # 15 minutes
            f"Access token expiry too long: {self.tokens.ACCESS_TOKEN_EXPIRY}s"
        )
        
        self.test(
            "Refresh Token Expiry",
            self.tokens.REFRESH_TOKEN_EXPIRY <= 604800,  # 7 days
            f"Refresh token expiry too long: {self.tokens.REFRESH_TOKEN_EXPIRY}s"
        )
        
        # Test 3: MFA parameters
        self.test(
            "MFA Lockout Duration",
            self.mfa.LOCKOUT_DURATION >= 600,  # At least 10 minutes
            f"Lockout duration too short: {self.mfa.LOCKOUT_DURATION}s"
        )
        
        self.test(
            "MFA Max Attempts",
            self.mfa.MAX_ATTEMPTS <= 5,
            f"Too many attempts allowed: {self.mfa.MAX_ATTEMPTS}"
        )
    
    def run_all_tests(self):
        """Run all security validation tests."""
        print("=" * 60)
        print("SECURITY VALIDATION")
        print("=" * 60)
        
        self.validate_pkce()
        self.validate_rate_limiting()
        self.validate_token_security()
        self.validate_mfa_security()
        self.validate_session_security()
        self.validate_secure_defaults()
        
        # Summary
        print("\n" + "=" * 60)
        print("SECURITY VALIDATION SUMMARY")
        print("=" * 60)
        
        total = self.passed + self.failed
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        
        if self.failed == 0:
            print("\n🎉 All security tests passed!")
            return 0
        else:
            print(f"\n⚠️  {self.failed} security test(s) failed!")
            return 1


def main():
    """Run security validation."""
    validator = SecurityValidator()
    return validator.run_all_tests()


if __name__ == "__main__":
    import sys
    sys.exit(main())
