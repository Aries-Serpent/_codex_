"""Tests for TLS configuration module.

Tests the TLS/SSL context creation for distributed bridge protocol.
"""

import pytest
import ssl
import tempfile
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, UTC

from security.tls_config import (
    create_server_context,
    create_client_context,
    validate_tls_config,
    TLSConfigError,
)


@pytest.fixture
def temp_cert_dir():
    """Create temporary directory for test certificates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_certificates(temp_cert_dir):
    """Generate test certificates for mTLS testing."""
    # Generate CA key and certificate
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Codex Test CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Test CA"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )
    
    # Generate server key and certificate
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_name)
        .issuer_name(ca_name)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    
    # Generate client key and certificate
    client_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "test-client"),
    ])
    client_cert = (
        x509.CertificateBuilder()
        .subject_name(client_name)
        .issuer_name(ca_name)
        .public_key(client_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=1))
        .sign(ca_key, hashes.SHA256())
    )
    
    # Write CA certificate
    ca_cert_path = temp_cert_dir / "ca.crt"
    with open(ca_cert_path, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    
    # Write server certificate and key
    server_cert_path = temp_cert_dir / "server.crt"
    server_key_path = temp_cert_dir / "server.key"
    with open(server_cert_path, "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    with open(server_key_path, "wb") as f:
        f.write(
            server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    
    # Write client certificate and key
    client_cert_path = temp_cert_dir / "client.crt"
    client_key_path = temp_cert_dir / "client.key"
    with open(client_cert_path, "wb") as f:
        f.write(client_cert.public_bytes(serialization.Encoding.PEM))
    with open(client_key_path, "wb") as f:
        f.write(
            client_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    
    return {
        "ca_cert": ca_cert_path,
        "server_cert": server_cert_path,
        "server_key": server_key_path,
        "client_cert": client_cert_path,
        "client_key": client_key_path,
    }


class TestTLSServerContext:
    """Tests for server TLS context creation."""
    
    def test_create_server_context_success(self, test_certificates):
        """Test successful server context creation."""
        context = create_server_context(
            cert_path=test_certificates["server_cert"],
            key_path=test_certificates["server_key"],
            ca_path=test_certificates["ca_cert"],
            require_client_cert=True,
        )
        
        assert isinstance(context, ssl.SSLContext)
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3
    
    def test_create_server_context_no_client_cert(self, test_certificates):
        """Test server context without client certificate requirement."""
        context = create_server_context(
            cert_path=test_certificates["server_cert"],
            key_path=test_certificates["server_key"],
            require_client_cert=False,
        )
        
        assert isinstance(context, ssl.SSLContext)
        assert context.verify_mode == ssl.CERT_NONE
    
    def test_create_server_context_missing_cert(self, temp_cert_dir):
        """Test server context creation with missing certificate."""
        with pytest.raises(TLSConfigError, match="certificate not found"):
            create_server_context(
                cert_path=temp_cert_dir / "missing.crt",
                key_path=temp_cert_dir / "missing.key",
            )
    
    def test_create_server_context_missing_key(self, test_certificates, temp_cert_dir):
        """Test server context creation with missing key."""
        with pytest.raises(TLSConfigError, match="key not found"):
            create_server_context(
                cert_path=test_certificates["server_cert"],
                key_path=temp_cert_dir / "missing.key",
            )
    
    def test_create_server_context_missing_ca_with_client_cert(self, test_certificates):
        """Test server context requiring client cert but missing CA."""
        with pytest.raises(TLSConfigError, match="CA certificate required"):
            create_server_context(
                cert_path=test_certificates["server_cert"],
                key_path=test_certificates["server_key"],
                ca_path=None,
                require_client_cert=True,
            )


class TestTLSClientContext:
    """Tests for client TLS context creation."""
    
    def test_create_client_context_success(self, test_certificates):
        """Test successful client context creation."""
        context = create_client_context(
            cert_path=test_certificates["client_cert"],
            key_path=test_certificates["client_key"],
            ca_path=test_certificates["ca_cert"],
        )
        
        assert isinstance(context, ssl.SSLContext)
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3
        assert context.check_hostname is False
    
    def test_create_client_context_with_hostname_check(self, test_certificates):
        """Test client context with hostname verification enabled."""
        context = create_client_context(
            cert_path=test_certificates["client_cert"],
            key_path=test_certificates["client_key"],
            ca_path=test_certificates["ca_cert"],
            check_hostname=True,
        )
        
        assert context.check_hostname is True
    
    def test_create_client_context_missing_cert(self, temp_cert_dir, test_certificates):
        """Test client context creation with missing certificate."""
        with pytest.raises(TLSConfigError, match="certificate not found"):
            create_client_context(
                cert_path=temp_cert_dir / "missing.crt",
                key_path=test_certificates["client_key"],
                ca_path=test_certificates["ca_cert"],
            )
    
    def test_create_client_context_missing_ca(self, test_certificates, temp_cert_dir):
        """Test client context creation with missing CA."""
        with pytest.raises(TLSConfigError, match="CA certificate not found"):
            create_client_context(
                cert_path=test_certificates["client_cert"],
                key_path=test_certificates["client_key"],
                ca_path=temp_cert_dir / "missing.crt",
            )


class TestTLSValidation:
    """Tests for TLS configuration validation."""
    
    def test_validate_tls_config_success(self, test_certificates):
        """Test successful validation of all TLS files."""
        result = validate_tls_config(
            server_cert=test_certificates["server_cert"],
            server_key=test_certificates["server_key"],
            ca_cert=test_certificates["ca_cert"],
            client_cert=test_certificates["client_cert"],
            client_key=test_certificates["client_key"],
        )
        
        assert result is True
    
    def test_validate_tls_config_missing_file(self, test_certificates, temp_cert_dir):
        """Test validation fails with missing file."""
        result = validate_tls_config(
            server_cert=temp_cert_dir / "missing.crt",
            server_key=test_certificates["server_key"],
            ca_cert=test_certificates["ca_cert"],
            client_cert=test_certificates["client_cert"],
            client_key=test_certificates["client_key"],
        )
        
        assert result is False
    
    def test_validate_tls_config_invalid_cert(self, test_certificates, temp_cert_dir):
        """Test validation fails with invalid certificate."""
        # Create invalid certificate file
        invalid_cert = temp_cert_dir / "invalid.crt"
        invalid_cert.write_text("INVALID CERTIFICATE DATA")
        
        result = validate_tls_config(
            server_cert=invalid_cert,
            server_key=test_certificates["server_key"],
            ca_cert=test_certificates["ca_cert"],
            client_cert=test_certificates["client_cert"],
            client_key=test_certificates["client_key"],
        )
        
        assert result is False


class TestTLSSecurityProperties:
    """Tests for TLS security properties."""
    
    def test_server_context_tls_version(self, test_certificates):
        """Test server context enforces TLS 1.3 minimum."""
        context = create_server_context(
            cert_path=test_certificates["server_cert"],
            key_path=test_certificates["server_key"],
            ca_path=test_certificates["ca_cert"],
        )
        
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3
        # Verify old TLS versions are disabled
        assert context.options & ssl.OP_NO_TLSv1
        assert context.options & ssl.OP_NO_TLSv1_1
        assert context.options & ssl.OP_NO_TLSv1_2
    
    def test_client_context_tls_version(self, test_certificates):
        """Test client context enforces TLS 1.3 minimum."""
        context = create_client_context(
            cert_path=test_certificates["client_cert"],
            key_path=test_certificates["client_key"],
            ca_path=test_certificates["ca_cert"],
        )
        
        assert context.minimum_version == ssl.TLSVersion.TLSv1_3
        assert context.options & ssl.OP_NO_TLSv1
        assert context.options & ssl.OP_NO_TLSv1_1
        assert context.options & ssl.OP_NO_TLSv1_2
    
    def test_server_context_strong_ciphers(self, test_certificates):
        """Test server context uses strong cipher suites."""
        context = create_server_context(
            cert_path=test_certificates["server_cert"],
            key_path=test_certificates["server_key"],
            ca_path=test_certificates["ca_cert"],
        )
        
        # Get configured ciphers
        ciphers = context.get_ciphers()
        
        # Verify only TLS 1.3 ciphers are allowed
        for cipher in ciphers:
            assert "TLS" in cipher["name"]
            # Verify strong encryption (AES-256 or ChaCha20)
            assert any(
                alg in cipher["name"]
                for alg in ["AES_256", "CHACHA20"]
            )
