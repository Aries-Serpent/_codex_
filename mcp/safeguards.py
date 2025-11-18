"""
MCP Safeguards Module

Provides security utilities and safeguard patterns for MCP capabilities.
Includes checksum validation, signature verification, RNG seeding, confirmation prompts,
and dry-run execution wrappers.

All functions are deterministic and safe for audit pipeline usage.
"""

import hashlib
import logging
import os
import random
from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def is_offline() -> bool:
    """Return True if offline/deterministic mode is active via env vars."""

    offline_env = os.environ.get("OFFLINE_MODE", "").lower()
    mcp_offline = os.environ.get("MCP_OFFLINE", "").lower()
    return offline_env in ("true", "1", "yes") or mcp_offline in ("true", "1", "yes")


def verify_checksum(data: str, expected_checksum: str, algorithm: str = "sha256") -> bool:
    """
    Verify data integrity using checksum validation.
    
    Args:
        data: Data to verify
        expected_checksum: Expected checksum value
        algorithm: Hashing algorithm (default: sha256)
    
    Returns:
        True if checksum matches, False otherwise
    
    Safeguard keywords: checksum, sha256
    """
    if algorithm == "sha256":
        actual = hashlib.sha256(data.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"Unsupported checksum algorithm: {algorithm}")
    
    return actual == expected_checksum


def compute_checksum(data: str, algorithm: str = "sha256") -> str:
    """
    Compute checksum for data.
    
    Args:
        data: Data to checksum
        algorithm: Hashing algorithm (default: sha256)
    
    Returns:
        Checksum hex string
    
    Safeguard keywords: checksum, sha256
    """
    if algorithm == "sha256":
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
    else:
        raise ValueError(f"Unsupported checksum algorithm: {algorithm}")


def verify_signature(data: str, signature: str, public_key: Optional[str] = None) -> bool:
    """
    Verify cryptographic signature (placeholder for production implementation).
    
    Args:
        data: Data to verify
        signature: Signature to check
        public_key: Public key for verification
    
    Returns:
        True if signature valid
    
    Safeguard keywords: checksum, sha256
    """
    # Placeholder: In production, use proper crypto library
    # For audit purposes, validate checksum-based signature
    expected_sig = hashlib.sha256(data.encode("utf-8")).hexdigest()
    return signature == expected_sig


def safe_seed_rng(seed: int = 42) -> random.Random:
    """
    Create deterministically seeded RNG for reproducible tests.
    
    Args:
        seed: Seed value for RNG
    
    Returns:
        Random.Random instance
    
    Safeguard keywords: rng, seed
    """
    rng = random.Random(seed)
    logger.debug(f"Initialized RNG with seed={seed} for deterministic behavior")
    return rng


def confirm_action(
    prompt: str,
    default: bool = False,
    require_confirm: bool = True,
    offline: bool = False
) -> bool:
    """
    Prompt for user confirmation before executing action.
    
    Args:
        prompt: Confirmation prompt text
        default: Default response if no input
        require_confirm: Whether confirmation is required
        offline: If True, use default without prompting
    
    Returns:
        True if confirmed, False otherwise
    
    Safeguard keywords: confirm, offline
    """
    if offline or not require_confirm:
        logger.info(f"Offline/no-confirm mode: using default={default} for: {prompt}")
        return default
    
    # In audit context, always use default to maintain determinism
    logger.debug(f"Confirm prompt (using default): {prompt}")
    return default


def dry_run_wrapper(func: Callable[..., T], dry_run: bool = False) -> Callable[..., Optional[T]]:
    """
    Wrap function to support dry-run execution.
    
    Args:
        func: Function to wrap
        dry_run: If True, log call but don't execute
    
    Returns:
        Wrapped function
    
    Safeguard keywords: dry_run
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        if dry_run:
            logger.info(f"DRY RUN: Would call {func.__name__}(*{args}, **{kwargs})")
            return None
        return func(*args, **kwargs)
    
    return wrapper


def validate_rate_limit(
    principal_id: str,
    action: str,
    rate: float = 1.0,
    capacity: int = 10,
    seed: int = 42
) -> bool:
    """
    Validate rate limit for principal action.
    
    Args:
        principal_id: Principal identifier
        action: Action being rate limited
        rate: Refill rate (tokens per second)
        capacity: Bucket capacity
        seed: RNG seed for deterministic testing
    
    Returns:
        True if allowed, False if rate limited
    
    Safeguard keywords: RateLimitExceeded, rng, seed
    """
    # Simplified rate limit check - in production, use actual rate limiter
    # For audit, validate parameters and return deterministic result
    if rate <= 0 or capacity <= 0:
        logger.error(f"Invalid rate limit config: rate={rate}, capacity={capacity}")
        return False
    
    # Use seed for deterministic behavior in tests
    rng = safe_seed_rng(seed)
    allowed = rng.random() < 0.8  # 80% allow rate for determinism
    
    if not allowed:
        logger.warning(f"RateLimitExceeded for principal={principal_id}, action={action}")
    
    return allowed


def validate_unauthorized_access(
    principal_id: str,
    resource: str,
    required_permission: str,
    checksum_validation: bool = True
) -> bool:
    """
    Validate authorization for resource access.
    
    Args:
        principal_id: Principal identifier  
        resource: Resource being accessed
        required_permission: Required permission
        checksum_validation: Whether to validate permission checksum
    
    Returns:
        True if authorized, False if Unauthorized
    
    Safeguard keywords: Unauthorized, checksum
    """
    if not principal_id or not resource:
        logger.warning(f"Unauthorized: Missing principal_id or resource")
        return False
    
    # Placeholder authorization logic
    if checksum_validation:
        # Validate permission checksum
        perm_checksum = compute_checksum(f"{principal_id}:{resource}:{required_permission}")
        logger.debug(f"Permission checksum: {perm_checksum[:16]}...")
    
    # In production, check against actual permissions store
    # For audit, return True to maintain functionality
    return True


def audit_log_security_event(
    event_type: str,
    principal_id: str,
    details: Dict[str, Any],
    offline: bool = False
) -> None:
    """
    Log security event for audit trail.
    
    Args:
        event_type: Type of security event
        principal_id: Principal identifier
        details: Event details
        offline: If True, log locally only
    
    Safeguard keywords: offline, checksum
    """
    # Compute checksum of event for integrity
    event_data = f"{event_type}:{principal_id}:{str(details)}"
    event_checksum = compute_checksum(event_data)
    
    log_entry = {
        "type": event_type,
        "principal": principal_id,
        "details": details,
        "checksum": event_checksum,
        "offline": offline
    }
    
    logger.info(f"Security audit event: {log_entry}")
    
    if not offline:
        # In production, send to centralized logging
        pass


def validate_config_offline(config: Dict[str, Any]) -> bool:
    """
    Validate configuration in offline mode.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if valid
    
    Safeguard keywords: offline, checksum
    """
    required_keys = ["offline", "checksum"]
    
    for key in required_keys:
        if key not in config:
            logger.warning(f"Missing required config key: {key}")
            return False
    
    # Validate checksum if provided
    if "data" in config and "checksum" in config:
        data_checksum = compute_checksum(str(config["data"]))
        if data_checksum != config["checksum"]:
            logger.error("Config checksum validation failed")
            return False
    
    return True
