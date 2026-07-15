#!/usr/bin/env python3
"""
HARDENED COPILOT COMMENT PROCESSING WITH CASCADE PREVENTION
─────────────────────────────────────────────────────────────

Integration module that applies cascade prevention safeguards to existing
Copilot comment processing pipeline (check_pr_comments.py, etc.)

Key Features:
  - Circuit breaker integration before posting comments
  - Error comment classification and self-referential detection
  - Rate limiting and exponential backoff
  - Cascade alert generation
  - Automatic pause/resume of comment generation

Deployment:
  1. Import this module in check_pr_comments.py
  2. Call guard_comment_posting() before each comment
  3. Monitor metrics via emit_metrics()
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Optional

from cascade_detection_system import (
    CascadeDetector,
    CascadeMonitor,
    CascadeWave,
    CircuitBreaker,
    CircuitBreakerState,
    ErrorComment,
)

logger = logging.getLogger(__name__)

# Global instances (initialized on first use)
_detector: Optional[CascadeDetector] = None
_breaker: Optional[CircuitBreaker] = None
_monitor: Optional[CascadeMonitor] = None


def _init_systems() -> tuple[CascadeDetector, CircuitBreaker, CascadeMonitor]:
    """Initialize cascade detection systems (singleton)."""
    global _detector, _breaker, _monitor

    if _detector is None:
        db_dir = os.getenv("CODEX_DB_DIR", ".codex")
        _detector = CascadeDetector(f"{db_dir}/cascade_detection.db")
        _breaker = CircuitBreaker(f"{db_dir}/circuit_breaker.db")
        _monitor = CascadeMonitor(_detector, _breaker)

    return _detector, _breaker, _monitor


# ─────────────────────────────────────────────────────────────────────────────
# PRIMARY API: GUARD COMMENT POSTING
# ─────────────────────────────────────────────────────────────────────────────


def guard_comment_posting(
    pr_number: int,
    comment_type: str,
    is_error_comment: bool = False,
    error_type: Optional[str] = None,
) -> dict[str, Any]:
    """
    MAIN ENTRY POINT: Check if comment posting should proceed.

    This function should be called BEFORE posting any comment on a PR to
    determine if cascade prevention mechanisms should allow it.

    Args:
        pr_number: GitHub PR number
        comment_type: Type of comment ("error", "info", "alert", "escalation")
        is_error_comment: True if this is an error comment
        error_type: Classification of error if is_error_comment=True

    Returns:
        Decision dict with:
            - allowed: bool (whether to post comment)
            - reason: str (explanation)
            - breaker_state: CircuitBreakerState
            - cascade_detected: bool
            - action: str ("post", "defer", "pause", "escalate")
            - metrics: dict (current metrics)

    Example:
        decision = guard_comment_posting(
            pr_number=5324,
            comment_type="error",
            is_error_comment=True,
            error_type="api_error",
        )

        if decision["allowed"]:
            post_comment(pr_number, comment_body)
        else:
            logger.warning(f"Comment posting blocked: {decision['reason']}")
    """
    detector, breaker, monitor = _init_systems()

    # Check circuit breaker status
    breaker_status = breaker.get_status(pr_number)
    should_accept = breaker.should_accept_comment(pr_number)

    # Check for cascade pattern
    cascade_alert = monitor.check_cascade(pr_number)
    has_cascade = cascade_alert is not None

    # Classify error if applicable
    wave = None
    if is_error_comment and error_type:
        error_count = detector.get_error_count(pr_number, time_window_seconds=3600)
        wave = detector.detect_cascade(pr_number, error_count + 1)

    # Determine action
    action = "post"
    allowed = True
    reason = "OK"

    if not should_accept:
        action = "pause"
        allowed = False
        reason = f"Circuit breaker {breaker_status.state.value}: paused until {breaker_status.paused_until}"

    elif breaker_status.state == CircuitBreakerState.HALF_OPEN:
        action = "post"
        reason = "Recovery attempt (HALF_OPEN state)"

    elif has_cascade:
        if cascade_alert["alert_level"] == "critical":
            action = "escalate"
            allowed = False
            reason = f"CRITICAL cascade detected: {cascade_alert['cascade_wave']}"
        else:
            action = "defer"
            reason = f"Cascade detected: {cascade_alert['cascade_wave']} (limiting posts)"
            # Still allow post but mark for deferral
            allowed = True

    # Record error if applicable
    if is_error_comment and error_type and allowed:
        breaker.record_error(
            pr_number,
            error_type,
            {"comment_type": comment_type, "wave": wave.value if wave else None},
        )

        # Update cascade tracking
        if wave:
            detector.record_error_comment(
                comment_id=0,  # Will be set by caller after posting
                pr_number=pr_number,
                error_type=error_type,
                created_at=datetime.now(timezone.utc),
                is_self_referential=False,
            )

    return {
        "allowed": allowed,
        "reason": reason,
        "action": action,
        "breaker_state": breaker_status.state.value,
        "breaker_paused_until": (
            breaker_status.paused_until.isoformat()
            if breaker_status.paused_until
            else None
        ),
        "cascade_detected": has_cascade,
        "cascade_wave": cascade_alert["cascade_wave"] if has_cascade else None,
        "metrics": {
            k: v
            for k, v in monitor.emit_metrics(pr_number).items()
            if k != "recent_cascade_events"
        },
    }


def record_error_comment(
    pr_number: int,
    comment_id: int,
    error_type: str,
    is_self_referential: bool = False,
) -> None:
    """
    Record an error comment after it's been posted.

    Args:
        pr_number: GitHub PR number
        comment_id: GitHub comment ID
        error_type: Classification of error
        is_self_referential: Whether comment references previous errors
    """
    detector, _, _ = _init_systems()
    detector.record_error_comment(
        comment_id,
        pr_number,
        error_type,
        datetime.now(timezone.utc),
        is_self_referential,
    )


def update_error_comment_id(
    pr_number: int,
    old_comment_id: int,
    new_comment_id: int,
) -> None:
    """
    Update placeholder comment_id with actual comment ID after posting.

    Args:
        pr_number: GitHub PR number
        old_comment_id: Placeholder comment ID (usually 0)
        new_comment_id: Actual GitHub comment ID
    """
    detector, _, _ = _init_systems()
    detector.update_error_comment_id(pr_number, old_comment_id, new_comment_id)


def record_success(pr_number: int) -> None:
    """
    Record successful comment generation (non-error).

    Args:
        pr_number: GitHub PR number
    """
    _, breaker, _ = _init_systems()
    breaker.record_success(pr_number)


def emit_metrics(pr_number: int) -> dict[str, Any]:
    """
    Emit monitoring metrics for a PR.

    Returns:
        Dict with metrics suitable for Prometheus/CloudWatch
    """
    _, _, monitor = _init_systems()
    return monitor.emit_metrics(pr_number)


def get_breaker_status(pr_number: int) -> dict[str, Any]:
    """Get circuit breaker status for a PR."""
    _, breaker, _ = _init_systems()
    status = breaker.get_status(pr_number)
    return asdict(status)


def check_cascade_alert(pr_number: int) -> Optional[dict[str, Any]]:
    """Check if cascade alert should be triggered for a PR."""
    _, _, monitor = _init_systems()
    return monitor.check_cascade(pr_number)


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION PATTERNS
# ─────────────────────────────────────────────────────────────────────────────


def wrap_comment_generator(post_comment_fn):
    """
    Decorator to wrap a comment posting function with cascade prevention.

    Usage:
        @wrap_comment_generator
        def post_to_pr(pr_number, comment_body):
            gh_api.post_comment(pr_number, comment_body)

        # Now post_to_pr() automatically checks cascade prevention
        post_to_pr(5324, "Error: timeout in build job")
    """

    def wrapper(
        pr_number: int,
        comment_body: str,
        comment_type: str = "info",
        is_error: bool = False,
        error_type: Optional[str] = None,
    ):
        # Check if we should post
        decision = guard_comment_posting(
            pr_number, comment_type, is_error, error_type
        )

        if not decision["allowed"]:
            logger.warning(
                f"Comment posting blocked for PR #{pr_number}: {decision['reason']}"
            )
            return {
                "status": "blocked",
                "reason": decision["reason"],
                "action": decision["action"],
            }

        try:
            # Post the comment
            result = post_comment_fn(pr_number, comment_body)
            record_success(pr_number)
            
            # If this was an error comment with placeholder ID (0), update it with actual ID
            # This maintains the link between cascade detection and the posted comment
            comment_id = result.get("id")
            if is_error and comment_id:
                update_error_comment_id(pr_number, old_comment_id=0, new_comment_id=comment_id)
            
            logger.info(f"Comment posted to PR #{pr_number}")
            return {"status": "success", "comment_id": comment_id}
        except Exception as e:
            logger.error(f"Error posting comment to PR #{pr_number}: {e}")
            record_error_comment(pr_number, 0, "post_error", is_self_referential=False)
            return {"status": "error", "error": str(e)}

    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# ALERTING & ESCALATION
# ─────────────────────────────────────────────────────────────────────────────


def generate_cascade_alert_comment(pr_number: int) -> Optional[str]:
    """
    Generate an alert comment when cascade is detected.

    Returns:
        Markdown comment body or None if no cascade
    """
    detector, breaker, monitor = _init_systems()

    alert = monitor.check_cascade(pr_number)
    if not alert:
        return None

    status = breaker.get_status(pr_number)
    error_count = detector.get_error_count(pr_number)

    # Format alert based on severity
    if alert["alert_level"] == "critical":
        body = f"""
<!-- cascade-alert:critical -->
## 🚨 CRITICAL: Cascade Error Detected

**Incident**: PR #{pr_number} has entered CRITICAL cascade state.

**Status**:
- **Wave**: {alert['cascade_wave']}
- **Error Count**: {error_count} in last hour
- **Circuit Breaker**: {status.state.value}
- **Paused Until**: {status.paused_until or 'Not paused'}

**Action**:
- Copilot comment generation has been **PAUSED** to prevent error propagation
- Circuit breaker will attempt recovery after backoff period
- Manual intervention recommended

**Recovery Steps**:
1. Check recent commits for root cause
2. Fix underlying issue if possible
3. Circuit breaker will auto-resume after recovery window

<!-- cascade-alert:end -->
"""
    else:
        body = f"""
<!-- cascade-alert:warning -->
## ⚠️ Cascade Warning: Multiple Errors Detected

**Status**:
- **Wave**: {alert['cascade_wave']}
- **Error Count**: {error_count} in last hour
- **Circuit Breaker**: {status.state.value}

**Recommendation**: Check recent commits for patterns causing errors.

<!-- cascade-alert:end -->
"""

    return body


def generate_recovery_status_comment(pr_number: int) -> str:
    """Generate status comment showing recovery progress."""
    detector, breaker, monitor = _init_systems()

    metrics = monitor.emit_metrics(pr_number)
    status = breaker.get_status(pr_number)

    body = f"""
<!-- cascade-recovery-status -->
## 🔄 Cascade Detection Status

**Circuit Breaker**: {status.state.value}
**Error Count (1h)**: {metrics['error_count_per_hour']}
**Recovery Attempts**: {status.recovery_attempts}

**Last Update**: {datetime.now(timezone.utc).isoformat()}

<!-- cascade-recovery-status:end -->
"""
    return body


if __name__ == "__main__":
    # Test integration
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cascade_prevention.py <pr_number> [check|metrics|status]")
        sys.exit(1)

    pr = int(sys.argv[1])
    cmd = sys.argv[2] if len(sys.argv) > 2 else "status"

    if cmd == "check":
        decision = guard_comment_posting(pr, "test", is_error_comment=False)
        print(json.dumps(decision, indent=2, default=str))

    elif cmd == "metrics":
        metrics = emit_metrics(pr)
        print(json.dumps(metrics, indent=2, default=str))

    elif cmd == "status":
        status = get_breaker_status(pr)
        print(json.dumps(status, indent=2, default=str))

    elif cmd == "alert":
        alert = generate_cascade_alert_comment(pr)
        if alert:
            print(alert)
        else:
            print("No cascade detected")
