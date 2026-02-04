"""
Tamper-Evident Audit Logger

Implements a simple hash-chained NDJSON audit log:
Each event includes the SHA256 of the previous record to detect tampering.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x__sha256_bytes__mutmut_orig(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def x__sha256_bytes__mutmut_1(data: bytes) -> str:
    return hashlib.sha256(None).hexdigest()

x__sha256_bytes__mutmut_mutants : ClassVar[MutantDict] = {
'x__sha256_bytes__mutmut_1': x__sha256_bytes__mutmut_1
}

def _sha256_bytes(*args, **kwargs):
    result = _mutmut_trampoline(x__sha256_bytes__mutmut_orig, x__sha256_bytes__mutmut_mutants, args, kwargs)
    return result 

_sha256_bytes.__signature__ = _mutmut_signature(x__sha256_bytes__mutmut_orig)
x__sha256_bytes__mutmut_orig.__name__ = 'x__sha256_bytes'


@dataclass
class AuditLogger:
    path: Path

    def __init__(self, path: Path | None = None, log_dir: Path | None = None):
        """Initialize audit logger with path or log_dir.
        
        Args:
            path: Direct path to log file (takes precedence)
            log_dir: Directory for audit logs (creates audit.log inside)
        """
        if path is not None:
            self.path = path
        elif log_dir is not None:
            self.path = log_dir / "audit.log"
        else:
            self.path = Path("logs/audit/audit.log")

    def log_event(self, event_type: str, resource: str, action: str, user: str) -> None:
        """Log a security audit event.
        
        Args:
            event_type: Type of security event
            resource: Resource being accessed
            action: Action performed
            user: User performing action
        """
        from datetime import datetime
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "resource": resource,
            "action": action,
            "user": user
        }
        self.append(log_entry)

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "0" * 64
        lines = [ln for ln in self.path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        value = last.get("hash")
        return value if isinstance(value, str) else "0" * 64

    def append(self, event: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        prev = self._last_hash()
        payload: dict[str, Any] = {
            "ts": float(ts if ts is not None else time.time()),
            "event": event,
            "prev_hash": prev,
        }
        record_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = _sha256_bytes(record_bytes)
        payload["hash"] = digest
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def verify_chain(self) -> bool:
        if not self.path.exists():
            return True
        prev = "0" * 64
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if not isinstance(rec, dict):
                return False
            expected_prev = prev
            if rec.get("prev_hash") != expected_prev:
                return False
            computed = _sha256_bytes(
                json.dumps({k: rec[k] for k in rec if k != "hash"}, sort_keys=True).encode("utf-8")
            )
            hash_value = rec.get("hash")
            if not isinstance(hash_value, str) or hash_value != computed:
                return False
            prev = hash_value
        return True


def x_log_audit_event__mutmut_orig(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_1(
    event_type: str,
    user: str,
    action: str,
    success: bool = False,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_2(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = None
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_3(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=None)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_4(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = None
    logger.append(event)


def x_log_audit_event__mutmut_5(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "XXtypeXX": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_6(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "TYPE": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_7(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "XXuserXX": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_8(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "USER": user,
        "action": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_9(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "XXactionXX": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_10(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "ACTION": action,
        "success": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_11(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "XXsuccessXX": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_12(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "SUCCESS": success,
    }
    logger.append(event)


def x_log_audit_event__mutmut_13(
    event_type: str,
    user: str,
    action: str,
    success: bool = True,
    log_dir: Path | None = None,
) -> None:
    """Helper function to log a structured audit event to file-based hash chain.
    
    This function logs security-relevant events to a file-based audit trail with
    hash chain integrity verification. For simple logger-based event logging,
    use src.security.core.log_security_event instead.
    
    Args:
        event_type: Type of security event (e.g., 'authentication')
        user: User performing the action
        action: Action performed (e.g., 'login')
        success: Whether the action was successful
        log_dir: Directory to store logs (optional)
    """
    logger = AuditLogger(log_dir=log_dir)
    event = {
        "type": event_type,
        "user": user,
        "action": action,
        "success": success,
    }
    logger.append(None)

x_log_audit_event__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_audit_event__mutmut_1': x_log_audit_event__mutmut_1, 
    'x_log_audit_event__mutmut_2': x_log_audit_event__mutmut_2, 
    'x_log_audit_event__mutmut_3': x_log_audit_event__mutmut_3, 
    'x_log_audit_event__mutmut_4': x_log_audit_event__mutmut_4, 
    'x_log_audit_event__mutmut_5': x_log_audit_event__mutmut_5, 
    'x_log_audit_event__mutmut_6': x_log_audit_event__mutmut_6, 
    'x_log_audit_event__mutmut_7': x_log_audit_event__mutmut_7, 
    'x_log_audit_event__mutmut_8': x_log_audit_event__mutmut_8, 
    'x_log_audit_event__mutmut_9': x_log_audit_event__mutmut_9, 
    'x_log_audit_event__mutmut_10': x_log_audit_event__mutmut_10, 
    'x_log_audit_event__mutmut_11': x_log_audit_event__mutmut_11, 
    'x_log_audit_event__mutmut_12': x_log_audit_event__mutmut_12, 
    'x_log_audit_event__mutmut_13': x_log_audit_event__mutmut_13
}

def log_audit_event(*args, **kwargs):
    result = _mutmut_trampoline(x_log_audit_event__mutmut_orig, x_log_audit_event__mutmut_mutants, args, kwargs)
    return result 

log_audit_event.__signature__ = _mutmut_signature(x_log_audit_event__mutmut_orig)
x_log_audit_event__mutmut_orig.__name__ = 'x_log_audit_event'
