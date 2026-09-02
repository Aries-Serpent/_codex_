"""
Deployment Manager for ML Models - Phase 18 Lane B

Manages model deployment, versioning, and rollback procedures.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    CANARY = "canary"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ModelVersion:
    """Model version information."""
    version_id: str
    model_name: str
    size_bytes: int
    checksum: str
    deployment_timestamp: datetime
    status: DeploymentStatus = DeploymentStatus.PENDING
    metrics: Dict[str, Any] = field(default_factory=dict)
    model_path: Optional[str] = None
    quantized: bool = False
    compression_ratio: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version_id": self.version_id,
            "model_name": self.model_name,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "deployment_timestamp": self.deployment_timestamp.isoformat(),
            "status": self.status.value,
            "metrics": self.metrics,
            "model_path": self.model_path,
            "quantized": self.quantized,
            "compression_ratio": self.compression_ratio,
        }


class DeploymentManager:
    """Manages ML model deployment lifecycle."""
    
    def __init__(self, deployment_root: Optional[str] = None):
        """Initialize deployment manager."""
        self.deployment_root = Path(deployment_root or "~/.codex/ml_deployments").expanduser()
        self.deployment_root.mkdir(parents=True, exist_ok=True)
        self.state_file = self.deployment_root / "deployment_state.json"
        self.models: Dict[str, ModelVersion] = self._load_state()
        self.active_version: Optional[str] = None
        self.canary_version: Optional[str] = None
        
    def _load_state(self) -> Dict[str, ModelVersion]:
        """Load deployment state from disk."""
        if not self.state_file.exists():
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            models = {}
            for version_id, data in state.get("models", {}).items():
                data["deployment_timestamp"] = datetime.fromisoformat(data["deployment_timestamp"])
                data["status"] = DeploymentStatus(data["status"])
                models[version_id] = ModelVersion(**data)
            
            return models
        except Exception as e:
            logger.warning(f"Failed to load deployment state: {e}")
            return {}
    
    def _save_state(self) -> None:
        """Save deployment state to disk."""
        state = {
            "models": {vid: v.to_dict() for vid, v in self.models.items()},
            "active_version": self.active_version,
            "canary_version": self.canary_version,
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def register_model(
        self,
        model_name: str,
        model_path: str,
        quantized: bool = False,
        compression_ratio: float = 1.0,
    ) -> ModelVersion:
        """Register a new model version."""
        model_path_obj = Path(model_path)
        
        if not model_path_obj.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Calculate checksum
        checksum = self._calculate_checksum(model_path)
        size_bytes = model_path_obj.stat().st_size
        
        # Generate version ID
        timestamp = datetime.utcnow()
        version_id = f"{model_name}_v{timestamp.strftime('%Y%m%d_%H%M%S')}_{checksum[:8]}"
        
        version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            size_bytes=size_bytes,
            checksum=checksum,
            deployment_timestamp=timestamp,
            model_path=str(model_path_obj.absolute()),
            quantized=quantized,
            compression_ratio=compression_ratio,
            status=DeploymentStatus.PENDING,
        )
        
        self.models[version_id] = version
        self._save_state()
        
        logger.info(
            f"Registered model {version_id}: {size_bytes} bytes, "
            f"quantized={quantized}, compression={compression_ratio:.2f}x"
        )
        
        return version
    
    def deploy_model(self, version_id: str, is_canary: bool = False) -> bool:
        """Deploy a model version to production."""
        if version_id not in self.models:
            logger.error(f"Model version not found: {version_id}")
            return False
        
        version = self.models[version_id]
        
        try:
            # Verify model file exists
            if version.model_path is None:
                raise FileNotFoundError("Model file path is missing")
            if not Path(version.model_path).exists():
                raise FileNotFoundError(f"Model file not found at {version.model_path}")
            
            # Update status
            version.status = DeploymentStatus.CANARY if is_canary else DeploymentStatus.ACTIVE
            
            # Update tracking
            if is_canary:
                self.canary_version = version_id
            else:
                # Deprecate previous active version
                if self.active_version and self.active_version in self.models:
                    self.models[self.active_version].status = DeploymentStatus.DEPRECATED
                self.active_version = version_id
            
            self._save_state()
            logger.info(f"Deployed model {version_id} ({'canary' if is_canary else 'active'})")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed for {version_id}: {e}")
            version.status = DeploymentStatus.FAILED
            self._save_state()
            return False
    
    def rollback_to_version(self, version_id: str) -> bool:
        """Rollback to a previous model version."""
        if version_id not in self.models:
            logger.error(f"Model version not found: {version_id}")
            return False
        
        version = self.models[version_id]
        
        try:
            # Verify model file exists
            if version.model_path is None:
                raise FileNotFoundError("Model file path is missing")
            if not Path(version.model_path).exists():
                raise FileNotFoundError(f"Model file not found at {version.model_path}")
            
            # Mark current active as rolled back
            if self.active_version and self.active_version in self.models:
                self.models[self.active_version].status = DeploymentStatus.ROLLED_BACK
            
            # Activate rollback version
            version.status = DeploymentStatus.ACTIVE
            self.active_version = version_id
            self.canary_version = None
            
            self._save_state()
            logger.info(f"Rolled back to model {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for {version_id}: {e}")
            return False
    
    def get_active_model(self) -> Optional[ModelVersion]:
        """Get currently active model version."""
        if not self.active_version or self.active_version not in self.models:
            return None
        return self.models[self.active_version]
    
    def get_canary_model(self) -> Optional[ModelVersion]:
        """Get canary model version (if any)."""
        if not self.canary_version or self.canary_version not in self.models:
            return None
        return self.models[self.canary_version]
    
    def list_versions(self) -> list:
        """List all registered model versions."""
        return list(self.models.values())
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get current deployment information."""
        active = self.get_active_model()
        canary = self.get_canary_model()
        
        return {
            "active_version": active.to_dict() if active else None,
            "canary_version": canary.to_dict() if canary else None,
            "total_versions": len(self.models),
            "versions": [v.to_dict() for v in self.models.values()],
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def _calculate_checksum(file_path: str, algorithm: str = "sha256") -> str:
        """Calculate file checksum."""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
