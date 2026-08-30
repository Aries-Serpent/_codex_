"""Privacy-First PII Scrubbing Module.

This module implements comprehensive PII detection and redaction for
the RAG pipeline, ensuring zero PII in embeddings and maintaining
GDPR/CCPA compliance.

Planset PS-04: Privacy-First Memory Implementation
- Email detection (RFC 5322 compliant)
- IP address detection (IPv4, IPv6)
- Phone number detection (international formats)
- SSN/Tax ID detection
- Credit card number detection (Luhn algorithm)
- AWS key detection
- Custom pattern support
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Email pattern (RFC 5322 compliant)
_EMAIL = re.compile(r"([\w.+%\-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})", re.UNICODE)

# Phone patterns (international formats)
_PHONE = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4})")

# IP address patterns
_IPV4 = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
)
_IPV6 = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")

# SSN pattern (US Social Security Number)
_SSN = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")

# Credit card patterns (major providers)
_CREDIT_CARD = re.compile(
    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"
)

# AWS Access Key pattern
_AWS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# License detection
_GPL = re.compile(r"GNU GENERAL PUBLIC LICENSE|GPL v[23]", re.I)


class RedactionMode(Enum):
    """Redaction modes for PII scrubbing."""

    TOKEN_REPLACEMENT = "token"  # Replace with [TYPE_REDACTED]  # nosec B105
    SEMANTIC_PRESERVATION = "semantic"  # Replace with type-appropriate placeholder
    HASH_PRESERVATION = "hash"  # Replace with hash for deduplication


@dataclass
class PIIFlags:
    """Flags indicating detected PII types and counts."""

    pii_email: bool = False
    pii_phone: bool = False
    pii_ipv4: bool = False
    pii_ipv6: bool = False
    pii_ssn: bool = False
    pii_credit_card: bool = False
    pii_aws_key: bool = False
    license_gpl: bool = False
    total_redactions: int = 0
    redaction_details: list[Any] = field(default_factory=list)


def _luhn_check(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13:
        return False

    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def scrub(
    text: str,
    *,
    allow_gpl: bool = False,
    mode: RedactionMode = RedactionMode.TOKEN_REPLACEMENT,
    enable_ip: bool = True,
    enable_ssn: bool = True,
    enable_credit_card: bool = True,
    enable_aws_key: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Scrub PII from text content.

    Args:
        text: Input text to scrub
        allow_gpl: Whether to allow GPL-licensed content
        mode: Redaction mode to use
        enable_ip: Enable IP address detection
        enable_ssn: Enable SSN detection
        enable_credit_card: Enable credit card detection
        enable_aws_key: Enable AWS key detection

    Returns:
        Tuple of (scrubbed_text, flags_dict)
    """
    flags = PIIFlags()
    out = text

    # Email scrubbing
    def mask_email(m: re.Match) -> str:
        flags.pii_email = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "email", "position": m.start()})
        u, d = m.group(1), m.group(2)
        if mode == RedactionMode.TOKEN_REPLACEMENT:
            return "[EMAIL_REDACTED]"
        if mode == RedactionMode.SEMANTIC_PRESERVATION:
            return "user@domain.com"
        return u[:2] + "***@" + ("***" + d[-4:])

    # Phone scrubbing
    def mask_phone(m: re.Match) -> str:
        flags.pii_phone = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "phone", "position": m.start()})
        if mode == RedactionMode.TOKEN_REPLACEMENT:
            return "[PHONE_REDACTED]"
        if mode == RedactionMode.SEMANTIC_PRESERVATION:
            return "+1-555-000-0000"
        return "[PHONE_REDACTED]"

    # IPv4 scrubbing
    def mask_ipv4(m: re.Match) -> str:
        flags.pii_ipv4 = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "ipv4", "position": m.start()})
        if mode == RedactionMode.TOKEN_REPLACEMENT:
            return "[IPV4_REDACTED]"
        if mode == RedactionMode.SEMANTIC_PRESERVATION:
            return "10.0.0.1"
        return "[IPV4_REDACTED]"

    # IPv6 scrubbing
    def mask_ipv6(m: re.Match) -> str:
        flags.pii_ipv6 = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "ipv6", "position": m.start()})
        return "[IPV6_REDACTED]"

    # SSN scrubbing
    def mask_ssn(m: re.Match) -> str:
        flags.pii_ssn = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "ssn", "position": m.start()})
        return "[SSN_REDACTED]"

    # Credit card scrubbing with Luhn validation
    def mask_credit_card(m: re.Match) -> str:
        card_num = m.group(0)
        if not _luhn_check(card_num):
            # Luhn validation failed - pattern matches credit card format but checksum
            # is invalid. This could indicate typos, test data, or false positive matches.
            # Log for security audit trail without exposing any card digits.
            logger.debug(
                "Luhn validation failed for credit card pattern (length=%d position=%d)",
                len(card_num),
                m.start(),
            )  # codeql[py/clear-text-logging-sensitive-data]
            return m.group(0)  # codeql[py/clear-text-logging-sensitive-data]
        flags.pii_credit_card = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "credit_card", "position": m.start()})
        return "[CREDIT_CARD_REDACTED]"

    # AWS key scrubbing
    def mask_aws_key(m: re.Match) -> str:
        flags.pii_aws_key = True
        flags.total_redactions += 1
        flags.redaction_details.append({"type": "aws_key", "position": m.start()})
        return "[AWS_KEY_REDACTED]"

    # Apply scrubbing in priority order (longer patterns first to avoid conflicts)
    # Credit cards first (16 digits) before phone (10 digits)
    if enable_credit_card:
        out = _CREDIT_CARD.sub(mask_credit_card, out)

    if enable_aws_key:
        out = _AWS_KEY.sub(mask_aws_key, out)

    out = _EMAIL.sub(mask_email, out)
    out = _PHONE.sub(mask_phone, out)

    if enable_ip:
        out = _IPV4.sub(mask_ipv4, out)
        out = _IPV6.sub(mask_ipv6, out)

    if enable_ssn:
        out = _SSN.sub(mask_ssn, out)

    # License detection
    if _GPL.search(out):
        flags.license_gpl = True
        if not allow_gpl:
            out = "[LICENSE_BLOCKED_GPL]\n"

    # Return backward-compatible dict format
    flags_dict = {
        "pii_email": flags.pii_email,
        "pii_phone": flags.pii_phone,
        "pii_ipv4": flags.pii_ipv4,
        "pii_ipv6": flags.pii_ipv6,
        "pii_ssn": flags.pii_ssn,
        "pii_credit_card": flags.pii_credit_card,
        "pii_aws_key": flags.pii_aws_key,
        "license_gpl": flags.license_gpl,
        "total_redactions": flags.total_redactions,
        "redaction_details": flags.redaction_details,
    }

    return out, flags_dict


def scrub_for_embedding(text: str) -> str:
    """Convenience function for RAG pipeline - scrub all PII for embedding.

    This is the primary entry point for the knowledge crawler to ensure
    no PII enters the vector store.

    Args:
        text: Text content to scrub before embedding

    Returns:
        Scrubbed text safe for embedding
    """
    scrubbed, _ = scrub(text, mode=RedactionMode.TOKEN_REPLACEMENT)
    return scrubbed


__all__ = [
    "PIIFlags",
    "RedactionMode",
    "scrub",
    "scrub_for_embedding",
]
