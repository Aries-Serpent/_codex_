"""
Security module for MSP Gateway
Handles authentication, authorization, policy enforcement, and redaction
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .config import settings

logger = logging.getLogger(__name__)


class PolicyEnforcer:
    """Enforces security policies from safelist and denylist"""
    
    def __init__(self, policy_dir: Optional[str] = None):
        self.policy_dir = Path(policy_dir or settings.policy_dir)
        self._load_policies()
    
    def _load_policies(self):
        """Load safelist and denylist policies"""
        try:
            safelist_path = self.policy_dir / "safelist.yaml"
            denylist_path = self.policy_dir / "denylist.yaml"
            
            if safelist_path.exists():
                with open(safelist_path, "r") as f:
                    self.safelist = yaml.safe_load(f) or {}
            else:
                logger.warning(f"Safelist not found at {safelist_path}, using empty policy")
                self.safelist = {}
            
            if denylist_path.exists():
                with open(denylist_path, "r") as f:
                    self.denylist = yaml.safe_load(f) or {}
            else:
                logger.warning(f"Denylist not found at {denylist_path}, using empty policy")
                self.denylist = {}
            
            logger.info("Policies loaded successfully")
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            self.safelist = {}
            self.denylist = {}
    
    def check_blocked_patterns(self, text: str) -> Optional[str]:
        """Check if text contains blocked patterns
        
        Returns:
            Error message if blocked pattern found, None otherwise
        """
        blocked_patterns = self.denylist.get("blocked_prompt_patterns", [])
        for pattern in blocked_patterns:
            if pattern.lower() in text.lower():
                return f"Blocked pattern detected: {pattern}"
        return None
    
    def check_blocked_actions(self, action: str) -> bool:
        """Check if action is blocked
        
        Returns:
            True if action is blocked, False otherwise
        """
        blocked_actions = self.denylist.get("blocked_actions", [])
        return action in blocked_actions
    
    def redact_sensitive_content(self, text: str) -> tuple[str, List[str]]:
        """Redact sensitive information from text
        
        Returns:
            Tuple of (redacted_text, list of redaction types applied)
        """
        if not settings.redaction_enabled:
            return text, []
        
        redacted = text
        redactions_applied = []
        
        # Apply regex-based redactions
        redaction_patterns = self.denylist.get("redaction_patterns", [])
        for pattern_config in redaction_patterns:
            pattern = pattern_config.get("pattern")
            replacement = pattern_config.get("replacement", "[REDACTED]")
            if pattern:
                matches = re.findall(pattern, redacted)
                if matches:
                    redacted = re.sub(pattern, replacement, redacted)
                    redactions_applied.append(replacement)
        
        # Redact sensitive terms
        sensitive_terms = self.denylist.get("sensitive_terms", [])
        for term in sensitive_terms:
            if term.lower() in redacted.lower():
                # Case-insensitive replacement
                redacted = re.sub(
                    re.escape(term),
                    "[REDACTED]",
                    redacted,
                    flags=re.IGNORECASE
                )
                redactions_applied.append(f"term:{term}")
        
        return redacted, redactions_applied


class AuthManager:
    """Handles authentication and authorization"""
    
    def __init__(self):
        self.api_keys: Dict[str, str] = {}  # api_key -> tenant_id mapping
    
    def register_api_key(self, api_key: str, tenant_id: str):
        """Register an API key for a tenant"""
        self.api_keys[api_key] = tenant_id
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return tenant_id
        
        Returns:
            tenant_id if valid, None otherwise
        """
        return self.api_keys.get(api_key)
    
    def revoke_api_key(self, api_key: str):
        """Revoke an API key"""
        self.api_keys.pop(api_key, None)


class OfflineGuard:
    """Enforces offline-only operation"""
    
    @staticmethod
    def check_network_access() -> bool:
        """Check if network access is attempted
        
        Returns:
            True if network access is blocked, False if allowed
        """
        return settings.offline
    
    @staticmethod
    def block_external_call(call_type: str):
        """Block external calls in offline mode
        
        Raises:
            RuntimeError if offline mode is enabled
        """
        if settings.offline:
            raise RuntimeError(
                f"External call '{call_type}' blocked in offline mode. "
                "Set MSP_OFFLINE=False to allow network access."
            )


# Global instances
policy_enforcer = PolicyEnforcer()
auth_manager = AuthManager()
offline_guard = OfflineGuard()


def validate_prompt(prompt: str, tenant_id: str) -> tuple[bool, Optional[str]]:
    """Validate a prompt against security policies
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for blocked patterns
    error = policy_enforcer.check_blocked_patterns(prompt)
    if error:
        logger.warning(f"Blocked prompt for tenant {tenant_id}: {error}")
        return False, error
    
    # Check prompt length (basic validation)
    if len(prompt) > 10000:  # Max prompt length
        return False, "Prompt exceeds maximum length"
    
    return True, None


def redact_content(text: str, tenant_id: str) -> tuple[str, List[str]]:
    """Redact sensitive content from text
    
    Returns:
        Tuple of (redacted_text, list of redactions applied)
    """
    redacted, redactions = policy_enforcer.redact_sensitive_content(text)
    if redactions:
        logger.info(f"Applied redactions for tenant {tenant_id}: {redactions}")
    return redacted, redactions
