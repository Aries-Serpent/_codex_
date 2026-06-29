"""Template: Token Validator Pattern

This template shows the pattern for creating token validation scripts
that can be stored as hidden scripts (Level 1 - CRITICAL).

Usage:
    1. Copy this template
    2. Implement custom token validation logic
    3. Store using HiddenScriptsManager (requires CODEX_MASTER_KEY)
    4. Execute only from elevated security contexts

Example:
    from scripts.ci._hidden_scripts_manager import HiddenScriptsManager
    manager = HiddenScriptsManager()
    
    with open("token_validator.py") as f:
        code = f.read()
    
    manager.store_hidden_script(
        name="token_validator",
        script_content=code,
        security_level=1,  # CRITICAL - Level 1
        author="security_team"
    )
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple


class TokenValidator:
    """Template for token validation logic (CRITICAL - Level 1)."""

    def __init__(self):
        """Initialize token validator."""
        self.validation_rules = {
            "min_length": 20,
            "max_age_days": 90,
            "required_chars": ["a-z", "A-Z", "0-9"],
        }

    def validate_token_format(self, token: str) -> Tuple[bool, str]:
        """Validate token format.
        
        Args:
            token: Token to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(token) < self.validation_rules["min_length"]:
            return False, f"Token too short (min: {self.validation_rules['min_length']})"

        if not token.strip():
            return False, "Token is empty or whitespace-only"

        return True, "Format valid"

    def validate_token_scope(self, token: str, required_scopes: List[str]) -> Tuple[bool, str]:
        """Validate that token has required scopes.
        
        This should call GitHub API to verify actual token scopes.
        Custom implementation would integrate with GitHub's token endpoint.
        
        Args:
            token: Token to validate
            required_scopes: Required scopes
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Placeholder: In production, this would call GitHub API
        # to verify the actual token scopes:
        # GET /user (validates token)
        # Check X-OAuth-Scopes header

        if not token.startswith("ghp_") and not token.startswith("ghu_"):
            return False, "Invalid token format (not GitHub token)"

        # Simulate scope validation
        return True, f"Token has required scopes: {', '.join(required_scopes)}"

    def validate_token_expiration(self, token_created_date: str) -> Tuple[bool, str]:
        """Validate that token hasn't expired.
        
        Args:
            token_created_date: Token creation date (ISO format)
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            created = datetime.fromisoformat(token_created_date)
            max_age = timedelta(days=self.validation_rules["max_age_days"])
            
            if datetime.utcnow() - created > max_age:
                return False, f"Token older than {self.validation_rules['max_age_days']} days"
            
            return True, "Token age acceptable"

        except Exception as e:
            return False, f"Cannot parse token date: {e}"

    def validate_token_usage(self, token: str, last_used: str) -> Tuple[bool, str]:
        """Validate token usage patterns.
        
        Args:
            token: Token to validate
            last_used: Last usage date (ISO format)
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            last_usage = datetime.fromisoformat(last_used)
            days_unused = (datetime.utcnow() - last_usage).days

            if days_unused > 180:
                return False, f"Token unused for {days_unused} days"

            return True, "Token usage pattern acceptable"

        except Exception as e:
            return False, f"Cannot parse usage date: {e}"

    def validate_token_rotation_due(self, token_created_date: str) -> Tuple[bool, str]:
        """Check if token needs rotation.
        
        Args:
            token_created_date: Token creation date (ISO format)
            
        Returns:
            Tuple of (is_due, message)
        """
        try:
            created = datetime.fromisoformat(token_created_date)
            rotation_interval = timedelta(days=90)  # Quarterly
            
            if datetime.utcnow() - created > rotation_interval:
                return True, "Token rotation is due"
            
            days_until_rotation = (rotation_interval - (datetime.utcnow() - created)).days
            return False, f"Rotation due in {days_until_rotation} days"

        except Exception as e:
            return False, f"Cannot determine rotation due date: {e}"

    def perform_full_validation(self, token: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full token validation.
        
        Args:
            token: Token to validate
            metadata: Token metadata (created_date, scopes, etc.)
            
        Returns:
            Validation result dictionary
        """
        results = {
            "token_id": metadata.get("id", "unknown"),
            "validation_timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }

        # Check 1: Format
        is_valid, msg = self.validate_token_format(token)
        results["checks"]["format"] = {"valid": is_valid, "message": msg}

        # Check 2: Scope
        required_scopes = metadata.get("required_scopes", ["repo"])
        is_valid, msg = self.validate_token_scope(token, required_scopes)
        results["checks"]["scope"] = {"valid": is_valid, "message": msg}

        # Check 3: Expiration
        created_date = metadata.get("created_at")
        if created_date:
            is_valid, msg = self.validate_token_expiration(created_date)
            results["checks"]["expiration"] = {"valid": is_valid, "message": msg}

        # Check 4: Usage
        last_used = metadata.get("last_used_at")
        if last_used:
            is_valid, msg = self.validate_token_usage(token, last_used)
            results["checks"]["usage"] = {"valid": is_valid, "message": msg}

        # Check 5: Rotation
        if created_date:
            is_due, msg = self.validate_token_rotation_due(created_date)
            results["checks"]["rotation_due"] = {"due": is_due, "message": msg}

        # Overall result
        all_valid = all(
            check.get("valid", True)
            for check in results["checks"].values()
            if "valid" in check
        )

        results["overall_valid"] = all_valid
        results["recommendation"] = "ALLOW" if all_valid else "DENY"

        return results


def main():
    """Main entry point - called when script is executed."""
    # Simulate token validation
    token = os.environ.get("TEST_TOKEN", "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    metadata = {
        "id": "token_001",
        "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "last_used_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "required_scopes": ["repo", "workflow"]
    }

    validator = TokenValidator()
    result = validator.perform_full_validation(token, metadata)

    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["overall_valid"] else 1)


if __name__ == "__main__":
    main()
