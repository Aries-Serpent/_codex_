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


class TLSConfigError(Exception):
    """Raised when TLS configuration is invalid."""
    pass


def x_create_server_context__mutmut_orig(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_1(
    cert_path: str | Path,
    key_path: str | Path,
    ca_path: Optional[str | Path] = None,
    require_client_cert: bool = False,
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_2(
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
    cert_path = None
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_3(
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
    cert_path = Path(None)
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_4(
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
    key_path = None
    
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_5(
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
    key_path = Path(None)
    
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_6(
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
    if cert_path.exists():
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_7(
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
        raise TLSConfigError(None)
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_8(
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
    if key_path.exists():
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_9(
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
        raise TLSConfigError(None)
    
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_10(
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
    context = None
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    
    # Load server certificate and key
    try:
        context.load_cert_chain(str(cert_path), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_11(
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
    context = ssl.SSLContext(None)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    
    # Load server certificate and key
    try:
        context.load_cert_chain(str(cert_path), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_12(
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
    context.minimum_version = None
    
    # Load server certificate and key
    try:
        context.load_cert_chain(str(cert_path), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_13(
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
        context.load_cert_chain(None, str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_14(
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
        context.load_cert_chain(str(cert_path), None)
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_15(
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
        context.load_cert_chain(str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_16(
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
        context.load_cert_chain(str(cert_path), )
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_17(
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
        context.load_cert_chain(str(None), str(key_path))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_18(
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
        context.load_cert_chain(str(cert_path), str(None))
    except ssl.SSLError as e:
        raise TLSConfigError(f"Failed to load server certificate: {e}") from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_19(
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
        raise TLSConfigError(None) from e
    
    # Configure client authentication if required (mTLS)
    if require_client_cert:
        if ca_path is None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_20(
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
        if ca_path is not None:
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_21(
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
            raise TLSConfigError(
                None
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_22(
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
            raise TLSConfigError(
                "XXCA certificate required for client authenticationXX"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_23(
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
            raise TLSConfigError(
                "ca certificate required for client authentication"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_24(
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
            raise TLSConfigError(
                "CA CERTIFICATE REQUIRED FOR CLIENT AUTHENTICATION"
            )
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_25(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = None
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_26(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(None)
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_27(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if ca_path.exists():
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_28(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(None)
        
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_29(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")
        
        context.verify_mode = None
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
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_30(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")
        
        context.verify_mode = ssl.CERT_REQUIRED
        try:
            context.load_verify_locations(None)
        except ssl.SSLError as e:
            raise TLSConfigError(f"Failed to load CA certificate: {e}") from e
    else:
        context.verify_mode = ssl.CERT_NONE
    
    # Security hardening
    context.check_hostname = False  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_31(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")
        
        context.verify_mode = ssl.CERT_REQUIRED
        try:
            context.load_verify_locations(str(None))
        except ssl.SSLError as e:
            raise TLSConfigError(f"Failed to load CA certificate: {e}") from e
    else:
        context.verify_mode = ssl.CERT_NONE
    
    # Security hardening
    context.check_hostname = False  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_32(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")
        
        context.verify_mode = ssl.CERT_REQUIRED
        try:
            context.load_verify_locations(str(ca_path))
        except ssl.SSLError as e:
            raise TLSConfigError(None) from e
    else:
        context.verify_mode = ssl.CERT_NONE
    
    # Security hardening
    context.check_hostname = False  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_33(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
        ca_path = Path(ca_path)
        if not ca_path.exists():
            raise TLSConfigError(f"CA certificate not found: {ca_path}")
        
        context.verify_mode = ssl.CERT_REQUIRED
        try:
            context.load_verify_locations(str(ca_path))
        except ssl.SSLError as e:
            raise TLSConfigError(f"Failed to load CA certificate: {e}") from e
    else:
        context.verify_mode = None
    
    # Security hardening
    context.check_hostname = False  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_34(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.check_hostname = None  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_35(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.check_hostname = True  # We verify client certs, not hostnames
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_36(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.options = ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_37(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.options &= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_38(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 & ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_39(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    context.options |= ssl.OP_NO_TLSv1 & ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info(
        f"Created server TLS context (client cert required: {require_client_cert})"
    )
    return context


def x_create_server_context__mutmut_40(
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
            raise TLSConfigError(
                "CA certificate required for client authentication"
            )
        
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
    
    logger.info(
        None
    )
    return context

x_create_server_context__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_server_context__mutmut_1': x_create_server_context__mutmut_1, 
    'x_create_server_context__mutmut_2': x_create_server_context__mutmut_2, 
    'x_create_server_context__mutmut_3': x_create_server_context__mutmut_3, 
    'x_create_server_context__mutmut_4': x_create_server_context__mutmut_4, 
    'x_create_server_context__mutmut_5': x_create_server_context__mutmut_5, 
    'x_create_server_context__mutmut_6': x_create_server_context__mutmut_6, 
    'x_create_server_context__mutmut_7': x_create_server_context__mutmut_7, 
    'x_create_server_context__mutmut_8': x_create_server_context__mutmut_8, 
    'x_create_server_context__mutmut_9': x_create_server_context__mutmut_9, 
    'x_create_server_context__mutmut_10': x_create_server_context__mutmut_10, 
    'x_create_server_context__mutmut_11': x_create_server_context__mutmut_11, 
    'x_create_server_context__mutmut_12': x_create_server_context__mutmut_12, 
    'x_create_server_context__mutmut_13': x_create_server_context__mutmut_13, 
    'x_create_server_context__mutmut_14': x_create_server_context__mutmut_14, 
    'x_create_server_context__mutmut_15': x_create_server_context__mutmut_15, 
    'x_create_server_context__mutmut_16': x_create_server_context__mutmut_16, 
    'x_create_server_context__mutmut_17': x_create_server_context__mutmut_17, 
    'x_create_server_context__mutmut_18': x_create_server_context__mutmut_18, 
    'x_create_server_context__mutmut_19': x_create_server_context__mutmut_19, 
    'x_create_server_context__mutmut_20': x_create_server_context__mutmut_20, 
    'x_create_server_context__mutmut_21': x_create_server_context__mutmut_21, 
    'x_create_server_context__mutmut_22': x_create_server_context__mutmut_22, 
    'x_create_server_context__mutmut_23': x_create_server_context__mutmut_23, 
    'x_create_server_context__mutmut_24': x_create_server_context__mutmut_24, 
    'x_create_server_context__mutmut_25': x_create_server_context__mutmut_25, 
    'x_create_server_context__mutmut_26': x_create_server_context__mutmut_26, 
    'x_create_server_context__mutmut_27': x_create_server_context__mutmut_27, 
    'x_create_server_context__mutmut_28': x_create_server_context__mutmut_28, 
    'x_create_server_context__mutmut_29': x_create_server_context__mutmut_29, 
    'x_create_server_context__mutmut_30': x_create_server_context__mutmut_30, 
    'x_create_server_context__mutmut_31': x_create_server_context__mutmut_31, 
    'x_create_server_context__mutmut_32': x_create_server_context__mutmut_32, 
    'x_create_server_context__mutmut_33': x_create_server_context__mutmut_33, 
    'x_create_server_context__mutmut_34': x_create_server_context__mutmut_34, 
    'x_create_server_context__mutmut_35': x_create_server_context__mutmut_35, 
    'x_create_server_context__mutmut_36': x_create_server_context__mutmut_36, 
    'x_create_server_context__mutmut_37': x_create_server_context__mutmut_37, 
    'x_create_server_context__mutmut_38': x_create_server_context__mutmut_38, 
    'x_create_server_context__mutmut_39': x_create_server_context__mutmut_39, 
    'x_create_server_context__mutmut_40': x_create_server_context__mutmut_40
}

def create_server_context(*args, **kwargs):
    result = _mutmut_trampoline(x_create_server_context__mutmut_orig, x_create_server_context__mutmut_mutants, args, kwargs)
    return result 

create_server_context.__signature__ = _mutmut_signature(x_create_server_context__mutmut_orig)
x_create_server_context__mutmut_orig.__name__ = 'x_create_server_context'


def x_create_client_context__mutmut_orig(
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


def x_create_client_context__mutmut_1(
    cert_path: str | Path,
    key_path: str | Path,
    ca_path: str | Path,
    check_hostname: bool = True,
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


def x_create_client_context__mutmut_2(
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
    cert_path = None
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


def x_create_client_context__mutmut_3(
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
    cert_path = Path(None)
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


def x_create_client_context__mutmut_4(
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
    key_path = None
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


def x_create_client_context__mutmut_5(
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
    key_path = Path(None)
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


def x_create_client_context__mutmut_6(
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
    ca_path = None
    
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


def x_create_client_context__mutmut_7(
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
    ca_path = Path(None)
    
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


def x_create_client_context__mutmut_8(
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
    if cert_path.exists():
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


def x_create_client_context__mutmut_9(
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
        raise TLSConfigError(None)
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


def x_create_client_context__mutmut_10(
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
    if key_path.exists():
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


def x_create_client_context__mutmut_11(
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
        raise TLSConfigError(None)
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


def x_create_client_context__mutmut_12(
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
    if ca_path.exists():
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


def x_create_client_context__mutmut_13(
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
        raise TLSConfigError(None)
    
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


def x_create_client_context__mutmut_14(
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
    context = None
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


def x_create_client_context__mutmut_15(
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
    context = ssl.SSLContext(None)
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


def x_create_client_context__mutmut_16(
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
    context.minimum_version = None
    
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


def x_create_client_context__mutmut_17(
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
        context.load_cert_chain(None, str(key_path))
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


def x_create_client_context__mutmut_18(
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
        context.load_cert_chain(str(cert_path), None)
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


def x_create_client_context__mutmut_19(
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
        context.load_cert_chain(str(key_path))
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


def x_create_client_context__mutmut_20(
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
        context.load_cert_chain(str(cert_path), )
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


def x_create_client_context__mutmut_21(
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
        context.load_cert_chain(str(None), str(key_path))
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


def x_create_client_context__mutmut_22(
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
        context.load_cert_chain(str(cert_path), str(None))
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


def x_create_client_context__mutmut_23(
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
        raise TLSConfigError(None) from e
    
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


def x_create_client_context__mutmut_24(
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
    context.verify_mode = None
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


def x_create_client_context__mutmut_25(
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
        context.load_verify_locations(None)
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


def x_create_client_context__mutmut_26(
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
        context.load_verify_locations(str(None))
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


def x_create_client_context__mutmut_27(
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
        raise TLSConfigError(None) from e
    
    # Configure hostname checking
    context.check_hostname = check_hostname
    
    # Security hardening
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_28(
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
    context.check_hostname = None
    
    # Security hardening
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_29(
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
    context.options = ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_30(
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
    context.options &= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_31(
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
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 & ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_32(
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
    context.options |= ssl.OP_NO_TLSv1 & ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    
    # TLS 1.3 ciphersuites are secure by default (AES-GCM, ChaCha20-Poly1305)
    # No need to explicitly configure them as they're built into TLS 1.3
    
    logger.info("Created client TLS context")
    return context


def x_create_client_context__mutmut_33(
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
    
    logger.info(None)
    return context


def x_create_client_context__mutmut_34(
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
    
    logger.info("XXCreated client TLS contextXX")
    return context


def x_create_client_context__mutmut_35(
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
    
    logger.info("created client tls context")
    return context


def x_create_client_context__mutmut_36(
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
    
    logger.info("CREATED CLIENT TLS CONTEXT")
    return context

x_create_client_context__mutmut_mutants : ClassVar[MutantDict] = {
'x_create_client_context__mutmut_1': x_create_client_context__mutmut_1, 
    'x_create_client_context__mutmut_2': x_create_client_context__mutmut_2, 
    'x_create_client_context__mutmut_3': x_create_client_context__mutmut_3, 
    'x_create_client_context__mutmut_4': x_create_client_context__mutmut_4, 
    'x_create_client_context__mutmut_5': x_create_client_context__mutmut_5, 
    'x_create_client_context__mutmut_6': x_create_client_context__mutmut_6, 
    'x_create_client_context__mutmut_7': x_create_client_context__mutmut_7, 
    'x_create_client_context__mutmut_8': x_create_client_context__mutmut_8, 
    'x_create_client_context__mutmut_9': x_create_client_context__mutmut_9, 
    'x_create_client_context__mutmut_10': x_create_client_context__mutmut_10, 
    'x_create_client_context__mutmut_11': x_create_client_context__mutmut_11, 
    'x_create_client_context__mutmut_12': x_create_client_context__mutmut_12, 
    'x_create_client_context__mutmut_13': x_create_client_context__mutmut_13, 
    'x_create_client_context__mutmut_14': x_create_client_context__mutmut_14, 
    'x_create_client_context__mutmut_15': x_create_client_context__mutmut_15, 
    'x_create_client_context__mutmut_16': x_create_client_context__mutmut_16, 
    'x_create_client_context__mutmut_17': x_create_client_context__mutmut_17, 
    'x_create_client_context__mutmut_18': x_create_client_context__mutmut_18, 
    'x_create_client_context__mutmut_19': x_create_client_context__mutmut_19, 
    'x_create_client_context__mutmut_20': x_create_client_context__mutmut_20, 
    'x_create_client_context__mutmut_21': x_create_client_context__mutmut_21, 
    'x_create_client_context__mutmut_22': x_create_client_context__mutmut_22, 
    'x_create_client_context__mutmut_23': x_create_client_context__mutmut_23, 
    'x_create_client_context__mutmut_24': x_create_client_context__mutmut_24, 
    'x_create_client_context__mutmut_25': x_create_client_context__mutmut_25, 
    'x_create_client_context__mutmut_26': x_create_client_context__mutmut_26, 
    'x_create_client_context__mutmut_27': x_create_client_context__mutmut_27, 
    'x_create_client_context__mutmut_28': x_create_client_context__mutmut_28, 
    'x_create_client_context__mutmut_29': x_create_client_context__mutmut_29, 
    'x_create_client_context__mutmut_30': x_create_client_context__mutmut_30, 
    'x_create_client_context__mutmut_31': x_create_client_context__mutmut_31, 
    'x_create_client_context__mutmut_32': x_create_client_context__mutmut_32, 
    'x_create_client_context__mutmut_33': x_create_client_context__mutmut_33, 
    'x_create_client_context__mutmut_34': x_create_client_context__mutmut_34, 
    'x_create_client_context__mutmut_35': x_create_client_context__mutmut_35, 
    'x_create_client_context__mutmut_36': x_create_client_context__mutmut_36
}

def create_client_context(*args, **kwargs):
    result = _mutmut_trampoline(x_create_client_context__mutmut_orig, x_create_client_context__mutmut_mutants, args, kwargs)
    return result 

create_client_context.__signature__ = _mutmut_signature(x_create_client_context__mutmut_orig)
x_create_client_context__mutmut_orig.__name__ = 'x_create_client_context'


def x_validate_tls_config__mutmut_orig(
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
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_1(
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
        create_server_context(None, server_key, ca_cert)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_2(
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
        create_server_context(server_cert, None, ca_cert)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_3(
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
        create_server_context(server_cert, server_key, None)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_4(
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
        create_server_context(server_key, ca_cert)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_5(
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
        create_server_context(server_cert, ca_cert)
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_6(
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
        create_server_context(server_cert, server_key, )
        create_client_context(client_cert, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_7(
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
        create_client_context(None, client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_8(
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
        create_client_context(client_cert, None, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_9(
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
        create_client_context(client_cert, client_key, None)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_10(
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
        create_client_context(client_key, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_11(
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
        create_client_context(client_cert, ca_cert)
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_12(
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
        create_client_context(client_cert, client_key, )
        return True
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_13(
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
        return False
    except TLSConfigError as e:
        logger.error(f"TLS configuration validation failed: {e}")
        return False


def x_validate_tls_config__mutmut_14(
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
        logger.error(None)
        return False


def x_validate_tls_config__mutmut_15(
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
        logger.error(f"TLS configuration validation failed: {e}")
        return True

x_validate_tls_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_tls_config__mutmut_1': x_validate_tls_config__mutmut_1, 
    'x_validate_tls_config__mutmut_2': x_validate_tls_config__mutmut_2, 
    'x_validate_tls_config__mutmut_3': x_validate_tls_config__mutmut_3, 
    'x_validate_tls_config__mutmut_4': x_validate_tls_config__mutmut_4, 
    'x_validate_tls_config__mutmut_5': x_validate_tls_config__mutmut_5, 
    'x_validate_tls_config__mutmut_6': x_validate_tls_config__mutmut_6, 
    'x_validate_tls_config__mutmut_7': x_validate_tls_config__mutmut_7, 
    'x_validate_tls_config__mutmut_8': x_validate_tls_config__mutmut_8, 
    'x_validate_tls_config__mutmut_9': x_validate_tls_config__mutmut_9, 
    'x_validate_tls_config__mutmut_10': x_validate_tls_config__mutmut_10, 
    'x_validate_tls_config__mutmut_11': x_validate_tls_config__mutmut_11, 
    'x_validate_tls_config__mutmut_12': x_validate_tls_config__mutmut_12, 
    'x_validate_tls_config__mutmut_13': x_validate_tls_config__mutmut_13, 
    'x_validate_tls_config__mutmut_14': x_validate_tls_config__mutmut_14, 
    'x_validate_tls_config__mutmut_15': x_validate_tls_config__mutmut_15
}

def validate_tls_config(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_tls_config__mutmut_orig, x_validate_tls_config__mutmut_mutants, args, kwargs)
    return result 

validate_tls_config.__signature__ = _mutmut_signature(x_validate_tls_config__mutmut_orig)
x_validate_tls_config__mutmut_orig.__name__ = 'x_validate_tls_config'
