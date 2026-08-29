"""Archival tests package.

Security Note:
--------------
Tests in this package use tarfile extraction. To prevent path traversal vulnerabilities,
use the safe_extract_tarfile() helper from security_utils instead of raw tar.extractall().

Example:
    from .security_utils import safe_extract_tarfile
    safe_extract_tarfile(archive_path, extract_dir)  # Safe
    # NOT: tar.extractall(extract_dir)  # Vulnerable to path traversal
"""
