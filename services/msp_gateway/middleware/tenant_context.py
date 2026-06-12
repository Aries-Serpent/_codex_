"""
Tenant context middleware
Resolves API keys to tenant IDs and enforces quotas
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.log_sanitizer import sanitize_log_input

from ..config import settings
from ..security import auth_manager, candidate_api_key_hashes, hash_api_key

logger = logging.getLogger(__name__)

security = HTTPBearer()


def _looks_hashed_api_key(value: str) -> bool:
    """Return True when *value* matches a supported hashed API-key format."""
    normalized = value.lower()
    if len(normalized) == 64 and all(ch in "0123456789abcdef" for ch in normalized):
        return True
    prefix = "pbkdf2_sha256$"
    if normalized.startswith(prefix):
        digest = normalized[len(prefix):]
        return len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest)
    return False


class TenantRegistry:
    """Manages tenant information using SQLite or in-memory storage"""

    def __init__(self, backend: str = "sqlite"):
        self.backend = backend
        self.tenants: dict[str, dict[str, Any]] = {}  # In-memory cache

        if backend == "sqlite":
            self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite database for tenant registry"""
        db_path = Path(settings.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path: str = str(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tenants table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                quota_json TEXT,
                policies_json TEXT,
                metadata_json TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        cursor.execute("SELECT tenant_id, api_key FROM tenants")
        rows = cursor.fetchall()
        migrated = 0
        for tenant_id, stored_api_key in rows:
            if stored_api_key and not _looks_hashed_api_key(stored_api_key):
                if migrated == 0:
                    logger.warning(
                        "Migrating plaintext tenant API keys to hashed storage in %s. "
                        "Back up the tenant registry before the first migration run if "
                        "you may need to recover plaintext keys.",
                        db_path,
                    )
                cursor.execute(
                    "UPDATE tenants SET api_key = ? WHERE tenant_id = ?",
                    (hash_api_key(stored_api_key), tenant_id),
                )
                migrated += 1

        conn.commit()
        conn.close()
        logger.info("Initialized SQLite tenant registry at %s", db_path)
        if migrated:
            logger.info("Migrated %d tenant API keys to hashed storage", migrated)

    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        api_key: str,
        quota: Optional[dict[str, int]] = None,
        policies: Optional[list] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a new tenant"""
        import json

        now = datetime.utcnow().isoformat()

        tenant_data = {
            "tenant_id": tenant_id,
            "name": name,
            "api_key": api_key,
            "api_key_hash": hash_api_key(api_key),
            "quota": quota
            or {
                "requests_per_minute": settings.rate_limit_requests_per_minute,
                "tokens_per_minute": settings.rate_limit_tokens_per_minute,
            },
            "policies": policies or [],
            "metadata": metadata or {},
            "active": True,
            "created_at": now,
            "updated_at": now,
        }

        if self.backend == "sqlite":
            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO tenants (
                        tenant_id, name, api_key, quota_json, policies_json,
                        metadata_json, active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        tenant_id,
                        name,
                        tenant_data["api_key_hash"],
                        json.dumps(tenant_data["quota"]),
                        json.dumps(tenant_data["policies"]),
                        json.dumps(tenant_data["metadata"]),
                        1,
                        now,
                        now,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError as e:
                conn.close()
                raise ValueError(f"Tenant or API key already exists: {e}")
            finally:
                conn.close()

        # Cache in memory
        self.tenants[tenant_id] = {
            **tenant_data,
            "api_key": None,
        }

        # Register API key
        auth_manager.register_api_key(api_key, tenant_id)

        logger.info("Created tenant")
        return tenant_data

    def get_tenant(self, tenant_id: str) -> Optional[dict[str, Any]]:
        """Get tenant by ID"""
        # Check cache first
        if tenant_id in self.tenants:
            return self.tenants[tenant_id]

        # Load from SQLite
        if self.backend == "sqlite":
            import json

            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants WHERE tenant_id = ?
            """,
                (tenant_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                tenant_data = {
                    "tenant_id": row[0],
                    "name": row[1],
                    "api_key": None,
                    "api_key_hash": row[2],
                    "quota": json.loads(row[3]) if row[3] else {},
                    "policies": json.loads(row[4]) if row[4] else [],
                    "metadata": json.loads(row[5]) if row[5] else {},
                    "active": bool(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8],
                }
                # Cache it
                self.tenants[tenant_id] = tenant_data
                return tenant_data

        return None

    def get_tenant_by_api_key(self, api_key: str) -> Optional[dict[str, Any]]:
        """Get tenant by API key"""
        tenant_id = auth_manager.verify_api_key(api_key)
        if tenant_id:
            return self.get_tenant(tenant_id)

        # Fallback: search in SQLite
        if self.backend == "sqlite":
            import json
            # codeql[py/weak-sensitive-data-hashing]: legacy SHA-256 for backward-compat
            # lookup only; any SHA-256 match is immediately re-hashed to PBKDF2 below.
            api_key_hashes = candidate_api_key_hashes(api_key)  # (pbkdf2_hash, sha256_hash)

            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants WHERE api_key IN (?, ?)
            """,
                api_key_hashes,
            )

            row = cursor.fetchone()

            if row:
                tenant_id = row[0]
                stored_hash = row[2]
                pbkdf2_hash, legacy_sha256_hash = api_key_hashes

                # Lazy migration: upgrade legacy SHA-256 hash to PBKDF2 on first use.
                # Reuse the same connection to avoid race conditions and duplicate opens.
                if stored_hash == legacy_sha256_hash:
                    try:
                        cursor.execute(
                            "UPDATE tenants SET api_key = ? WHERE tenant_id = ?",
                            (pbkdf2_hash, tenant_id),
                        )
                        conn.commit()
                        logger.info(
                            "Migrated legacy SHA-256 API key hash to PBKDF2 for tenant %s",
                            sanitize_log_input(tenant_id),
                        )
                        stored_hash = pbkdf2_hash
                    except Exception as exc:
                        logger.warning(
                            "Failed to migrate API key hash for tenant %s: %s",
                            sanitize_log_input(tenant_id),
                            type(exc).__name__,
                        )

            conn.close()

            if row:
                tenant_data = {
                    "tenant_id": tenant_id,
                    "name": row[1],
                    "api_key": None,
                    "api_key_hash": stored_hash,
                    "quota": json.loads(row[3]) if row[3] else {},
                    "policies": json.loads(row[4]) if row[4] else [],
                    "metadata": json.loads(row[5]) if row[5] else {},
                    "active": bool(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8],
                }
                # Cache it
                self.tenants[tenant_id] = tenant_data
                for api_key_hash in api_key_hashes:
                    auth_manager.register_api_key_hash(api_key_hash, tenant_id)
                return tenant_data

        return None

    def list_tenants(self) -> list[dict[str, Any]]:
        """List all tenants"""
        if self.backend == "sqlite":
            import json

            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants
            """
            )

            rows = cursor.fetchall()
            conn.close()

            tenants = []
            for row in rows:
                tenants.append(
                    {
                        "tenant_id": row[0],
                        "name": row[1],
                        "api_key": None,
                        "api_key_hash": row[2],
                        "quota": json.loads(row[3]) if row[3] else {},
                        "policies": json.loads(row[4]) if row[4] else [],
                        "metadata": json.loads(row[5]) if row[5] else {},
                        "active": bool(row[6]),
                        "created_at": row[7],
                        "updated_at": row[8],
                    }
                )
            return tenants

        return list(self.tenants.values())

    def delete_tenant(self, tenant_id: str) -> None:
        """Delete (deactivate) a tenant and revoke API key

        Args:
            tenant_id: Tenant identifier

        Raises:
            ValueError: If tenant not found
        """

        # Get existing tenant
        tenant_data = self.get_tenant(tenant_id)
        if not tenant_data:
            raise ValueError(f"Tenant not found: {tenant_id}")

        # Deactivate tenant
        tenant_data["active"] = False
        tenant_data["updated_at"] = datetime.utcnow().isoformat()

        # Update in SQLite
        if self.backend == "sqlite":
            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE tenants
                SET active = 0, updated_at = ?
                WHERE tenant_id = ?
            """,
                (tenant_data["updated_at"], tenant_id),
            )

            conn.commit()
            conn.close()

        # Update cache
        self.tenants[tenant_id] = tenant_data

        # Revoke API key
        api_key_hash = tenant_data.get("api_key_hash")
        if api_key_hash:
            auth_manager.revoke_api_key_hash(api_key_hash)

        logger.info("Deleted (deactivated) tenant")

    def update_tenant(
        self,
        tenant_id: str,
        *,
        name: Optional[str] = None,
        quota: Optional[dict[str, int]] = None,
        policies: Optional[list] = None,
        metadata: Optional[dict[str, Any]] = None,
        active: Optional[bool] = None,
    ) -> Optional[dict[str, Any]]:
        """Update an existing tenant and persist changes"""

        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None

        updated_fields: dict[str, Any] = {}
        if name is not None:
            updated_fields["name"] = name
        if quota is not None:
            updated_fields["quota"] = quota
        if policies is not None:
            updated_fields["policies"] = policies
        if metadata is not None:
            updated_fields["metadata"] = metadata
        if active is not None:
            updated_fields["active"] = bool(active)

        now = datetime.utcnow().isoformat()

        if self.backend == "sqlite":
            import json

            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()

            set_clauses = []
            params: list[Any] = []

            if "name" in updated_fields:
                set_clauses.append("name = ?")
                params.append(updated_fields["name"])
            if "quota" in updated_fields:
                set_clauses.append("quota_json = ?")
                params.append(json.dumps(updated_fields["quota"]))
            if "policies" in updated_fields:
                set_clauses.append("policies_json = ?")
                params.append(json.dumps(updated_fields["policies"]))
            if "metadata" in updated_fields:
                set_clauses.append("metadata_json = ?")
                params.append(json.dumps(updated_fields["metadata"]))
            if "active" in updated_fields:
                set_clauses.append("active = ?")
                params.append(1 if updated_fields["active"] else 0)

            set_clauses.append("updated_at = ?")
            params.append(now)
            params.append(tenant_id)

            try:
                cursor.execute(
                    f"UPDATE tenants SET {', '.join(set_clauses)} WHERE tenant_id = ?",  # nosec B608 — set_clauses contain only hardcoded column-name literals; values are fully parameterised
                    params,
                )
                conn.commit()
            finally:
                conn.close()

        # Update in-memory cache
        for field, value in updated_fields.items():
            tenant[field] = value
        tenant["updated_at"] = now
        self.tenants[tenant_id] = tenant

        # Update API key registry based on tenant status
        if "active" in updated_fields:
            if updated_fields["active"]:
                auth_manager.register_api_key_hash(tenant["api_key_hash"], tenant_id)
            else:
                auth_manager.revoke_api_key_hash(tenant["api_key_hash"])

        logger.info(
            "Tenant %s updated with fields: %s",
            sanitize_log_input(tenant_id),
            sanitize_log_input(", ".join(updated_fields.keys()) if updated_fields else "updated_at"),
        )

        return tenant

    def deactivate_tenant(self, tenant_id: str) -> bool:
        """Deactivate a tenant and revoke credentials"""

        updated = self.update_tenant(tenant_id, active=False)
        return updated is not None


# Global tenant registry
tenant_registry = TenantRegistry(backend=settings.tenant_registry_backend)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to resolve tenant context from API key"""

    async def dispatch(self, request: Request, call_next):
        # Skip health check, docs, root endpoint, and optionally admin endpoints
        public_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/"]

        # If API key not required, also allow admin endpoints for bootstrapping
        if not settings.api_key_required:
            public_paths.append("/admin")

        # Check if path should skip auth
        if request.url.path in public_paths or any(
            request.url.path.startswith(p) for p in public_paths if p != "/"
        ):
            return await call_next(request)

        # If API key authentication is disabled, skip the check
        if not settings.api_key_required:
            # No tenant context when auth is disabled
            return await call_next(request)

        # Extract API key from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
            )

        api_key = auth_header.replace("Bearer ", "")

        # Resolve tenant
        tenant = tenant_registry.get_tenant_by_api_key(api_key)
        if not tenant:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"},
            )

        if not tenant.get("active", True):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Tenant is inactive"},
            )

        # Attach tenant to request state
        request.state.tenant = tenant

        return await call_next(request)
