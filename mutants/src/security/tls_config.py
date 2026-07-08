"""TLS Configuration for Distributed Bridge Protocol.

This module provides secure TLS/SSL context creation for the distributed
bridge implementation, supporting mutual TLS (mTLS) authentication and
secure cross-machine communication.

Part of PS-02 Enhancement: Distributed Bridge (TLS) - Priority 4
"""

from __future__ import annotations

import logging
import ssl
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TLSConfigError(Exception):
    """Raised when TLS configuration is invalid."""


def create_server_context(
    cert_path: str | Path,
    key_path: str | Path,
    ca_path: Optional[str | Path] = None,
    require_client_cert: bool = True,
) -> ssl.SSLContext:
    """Create SSL context for bridge server.

    Args:
        cert_path: Path to server certificate file (PEM format)
        key_path: Path to server private key file (PEM format)
        ca_path: Optional path to CA certificate for client verification
        require_client_cert: Whether to require client certificates (mTLS)

    Returns:
        Configured SSL context for server

    Raises:
        TLSConfigError: If certificate files are invalid or missing

    Example:
        >>> context = create_server_context(
        ...     cert_path="/etc/bridge/server.crt",
        ...     key_path="/etc/bridge/server.key",
        ...     ca_path="/etc/bridge/ca.crt",
        ...     require_client_cert=True
        ... )
    """
    cert_path = Path(cert_path)
    key_path = Path(key_path)

    # Validate certificate files exist
    if not cert_path.exists():
        raise TLSConfigError(f"Server certificate not found: {cert_path}")
    if not key_path.exists():
        raise TLSConfigError(f"Server key not found: {key_path}")

    # Create context for server with TLS 1.3 minimum
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    # Load server certificate and key
    try:
        context.load_cert_chain(str(cert_path), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e

    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError("CA certificate required for client authentication")

        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")

        context.verify_mode = ssl.CERT_REQUIRED
        try:
            context.load_verify_locations(str(ca_path))
        except ssl.SSLError as e:
            raise TLSConfigError(f"Failed to load CA certificate: {e}") from e
    else:
        context.verify_mode = ssl.CERT_NONE

    # Security hardening
    context.check_hostname = False  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2

    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3

    logger.info(f"Created server TLS context (client cert required: {require_client_cert})")
    return context


def create_client_context(
    cert_path: str | Path,
    key_path: str | Path,
    ca_path: str | Path,
    check_hostname: bool = False,
) -> ssl.SSLContext:
    """Create SSL context for bridge client.

    Args:
        cert_path: Path to client certificate file (PEM format)
        key_path: Path to client private key file (PEM format)
        ca_path: Path to CA certificate for server verification
        check_hostname: Whether to verify server hostname (usually False for bridge)

    Returns:
        Configured SSL context for client

    Raises:
        TLSConfigError: If certificate files are invalid or missing

    Example:
        >>> context = create_client_context(
        ...     cert_path="/etc/bridge/client.crt",
        ...     key_path="/etc/bridge/client.key",
        ...     ca_path="/etc/bridge/ca.crt"
        ... )
    """
    cert_path = Path(cert_path)
    key_path = Path(key_path)
    ca_path = Path(ca_path)

    # Validate certificate files exist
    if not cert_path.exists():
        raise TLSConfigError(f"Client certificate not found: {cert_path}")
    if not key_path.exists():
        raise TLSConfigError(f"Client key not found: {key_path}")
    if not ca_path.exists():
        raise TLSConfigError(f"CA certificate not found: {ca_path}")

    # Create context for client with TLS 1.3 minimum
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    # Load client certificate and key for mTLS
    try:
        context.load_cert_chain(str(cert_path), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load client certificate: {e}") from e

    # Load CA certificate for server verification
    context.verify_mode = ssl.CERT_REQUIRED
    try:
        context.load_verify_locations(str(ca_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load CA certificate: {e}") from e

    # Configure hostname checking
    context.check_hostname = check_hostname

    # Security hardening
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2

    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3

    logger.info("Created client TLS context")
    return context


def validate_tls_config(
    server_cert: str | Path,
    server_key: str | Path,
    ca_cert: str | Path,
    client_cert: str | Path,
    client_key: str | Path,
) -> bool:
    """Validate all TLS configuration files are present and valid.

    Args:
        server_cert: Path to server certificate
        server_key: Path to server key
        ca_cert: Path to CA certificate
        client_cert: Path to client certificate
        client_key: Path to client key

    Returns:
        True if all files exist and can be loaded

    Example:
        >>> valid = validate_tls_config(
        ...     server_cert="/etc/bridge/server.crt",
        ...     server_key="/etc/bridge/server.key",
        ...     ca_cert="/etc/bridge/ca.crt",
        ...     client_cert="/etc/bridge/client.crt",
        ...     client_key="/etc/bridge/client.key"
        ... )
    """
    try:
        # Try to create both contexts
        create_server_context(server_cert, server_key, ca_cert)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        type(e).__name__
        logger.error("TLS configuration validation failed: <ERROR_TYPE>")
        return False
