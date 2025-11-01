"""
Tenant context middleware
Resolves API keys to tenant IDs and enforces quotas
"""

import logging
import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings
from ..security import auth_manager

logger = logging.getLogger(__name__)

security = HTTPBearer()


class TenantRegistry:
    """Manages tenant information using SQLite or in-memory storage"""
    
    def __init__(self, backend: str = "sqlite"):
        self.backend = backend
        self.tenants: Dict[str, Dict[str, Any]] = {}  # In-memory cache
        
        if backend == "sqlite":
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database for tenant registry"""
        db_path = Path(settings.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tenants table
        cursor.execute("""
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
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Initialized SQLite tenant registry at {db_path}")
    
    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        api_key: str,
        quota: Optional[Dict[str, int]] = None,
        policies: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new tenant"""
        import json
        
        now = datetime.utcnow().isoformat()
        
        tenant_data = {
            "tenant_id": tenant_id,
            "name": name,
            "api_key": api_key,
            "quota": quota or {
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
                cursor.execute("""
                    INSERT INTO tenants (
                        tenant_id, name, api_key, quota_json, policies_json,
                        metadata_json, active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tenant_id, name, api_key,
                    json.dumps(tenant_data["quota"]),
                    json.dumps(tenant_data["policies"]),
                    json.dumps(tenant_data["metadata"]),
                    1, now, now
                ))
                conn.commit()
            except sqlite3.IntegrityError as e:
                conn.close()
                raise ValueError(f"Tenant or API key already exists: {e}")
            finally:
                conn.close()
        
        # Cache in memory
        self.tenants[tenant_id] = tenant_data
        
        # Register API key
        auth_manager.register_api_key(api_key, tenant_id)
        
        logger.info(f"Created tenant: {tenant_id}")
        return tenant_data
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID"""
        # Check cache first
        if tenant_id in self.tenants:
            return self.tenants[tenant_id]
        
        # Load from SQLite
        if self.backend == "sqlite":
            import json
            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants WHERE tenant_id = ?
            """, (tenant_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                tenant_data = {
                    "tenant_id": row[0],
                    "name": row[1],
                    "api_key": row[2],
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
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get tenant by API key"""
        tenant_id = auth_manager.verify_api_key(api_key)
        if tenant_id:
            return self.get_tenant(tenant_id)
        
        # Fallback: search in SQLite
        if self.backend == "sqlite":
            import json
            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants WHERE api_key = ?
            """, (api_key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                tenant_id = row[0]
                tenant_data = {
                    "tenant_id": tenant_id,
                    "name": row[1],
                    "api_key": row[2],
                    "quota": json.loads(row[3]) if row[3] else {},
                    "policies": json.loads(row[4]) if row[4] else [],
                    "metadata": json.loads(row[5]) if row[5] else {},
                    "active": bool(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8],
                }
                # Cache it
                self.tenants[tenant_id] = tenant_data
                auth_manager.register_api_key(api_key, tenant_id)
                return tenant_data
        
        return None
    
    def list_tenants(self) -> list[Dict[str, Any]]:
        """List all tenants"""
        if self.backend == "sqlite":
            import json
            conn = sqlite3.connect(settings.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tenant_id, name, api_key, quota_json, policies_json,
                       metadata_json, active, created_at, updated_at
                FROM tenants
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            tenants = []
            for row in rows:
                tenants.append({
                    "tenant_id": row[0],
                    "name": row[1],
                    "api_key": row[2],
                    "quota": json.loads(row[3]) if row[3] else {},
                    "policies": json.loads(row[4]) if row[4] else [],
                    "metadata": json.loads(row[5]) if row[5] else {},
                    "active": bool(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8],
                })
            return tenants
        
        return list(self.tenants.values())


# Global tenant registry
tenant_registry = TenantRegistry(backend=settings.tenant_registry_backend)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to resolve tenant context from API key"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip health check and docs endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Extract API key from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )
        
        api_key = auth_header.replace("Bearer ", "")
        
        # Resolve tenant
        tenant = tenant_registry.get_tenant_by_api_key(api_key)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        if not tenant.get("active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant is inactive"
            )
        
        # Attach tenant to request state
        request.state.tenant = tenant
        
        response = await call_next(request)
        return response
