"""
Secure serialization module with safe deserialization.

This module demonstrates safe deserialization techniques to prevent
arbitrary code execution (CWE-502: Insecure Deserialization).
"""

import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SerializationError(Exception):
    """Raised when serialization/deserialization fails."""
    pass


class DeserializationMode(Enum):
    """Deserialization modes with different security levels."""
    SAFE = "safe"           # JSON only - completely safe
    TRUSTED = "trusted"     # Pickle only for trusted data
    HYBRID = "hybrid"       # JSON with whitelist validation


class SecureSerializer:
    """
    Handles secure serialization and deserialization.
    
    SECURITY: Never uses pickle for untrusted data.
    - For untrusted data: Use JSON (safe, limited to primitives)
    - For trusted data: Use pickle with validation
    - For hybrid: Use JSON with schema validation
    """

    @staticmethod
    def deserialize_untrusted(data: bytes) -> Dict[str, Any]:
        """
        Deserialize untrusted data safely.
        
        ✅ VULNERABILITY FIXED: CWE-502 Insecure Deserialization
        
        Previous vulnerable code:
            import pickle
            obj = pickle.loads(untrusted_data)  # ❌ REMOTE CODE EXECUTION!
        
        Secure implementation:
            obj = json.loads(untrusted_data)  # ✅ SAFE
        
        JSON deserialization is safe because:
        - Only creates basic types (dict, list, str, int, float, bool, None)
        - No code execution or object instantiation
        - Predictable and auditable
        
        Args:
            data: Untrusted bytes from network/untrusted source
            
        Returns:
            Deserialized dictionary
            
        Raises:
            SerializationError: If deserialization fails
        """
        try:
            # SECURE: JSON only accepts safe types
            # Malicious pickle opcodes will raise JSONDecodeError
            decoded_str = data.decode('utf-8')
            obj = json.loads(decoded_str)
            return obj
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise SerializationError(f"Failed to deserialize untrusted data: {e}") from e

    @staticmethod
    def deserialize_trusted(data: bytes) -> Any:
        """
        Deserialize trusted data (internal use only).
        
        ⚠️ WARNING: Only use this for data you trust (e.g., cache, internal messages)
        
        DO NOT use for:
        - User-supplied data
        - Data from external APIs
        - Data from untrusted sources
        
        Args:
            data: Trusted bytes from internal source
            
        Returns:
            Deserialized object
            
        Raises:
            SerializationError: If deserialization fails
        """
        import pickle
        
        try:
            # Only deserialize for trusted data
            logger.debug("Deserializing trusted data with pickle")
            obj = pickle.loads(data)
            return obj
        except (pickle.UnpicklingError, EOFError, ValueError) as e:
            raise SerializationError(f"Failed to deserialize trusted data: {e}") from e

    @staticmethod
    def serialize(obj: Any) -> bytes:
        """
        Serialize object to JSON (safe format).
        
        Args:
            obj: Object to serialize (must be JSON-serializable)
            
        Returns:
            Serialized bytes
            
        Raises:
            SerializationError: If object is not JSON-serializable
        """
        try:
            json_str = json.dumps(obj)
            return json_str.encode('utf-8')
        except TypeError as e:
            raise SerializationError(f"Object is not JSON-serializable: {e}") from e

    @staticmethod
    def validate_schema(obj: Dict[str, Any], schema: Dict[str, Type]) -> bool:
        """
        Validate deserialized object against schema.
        
        This provides an additional layer of protection by ensuring
        the deserialized data matches expected types.
        
        Args:
            obj: Deserialized object
            schema: Schema mapping field names to expected types
            
        Returns:
            True if object matches schema
            
        Raises:
            SerializationError: If object doesn't match schema
        """
        for field_name, expected_type in schema.items():
            if field_name not in obj:
                raise SerializationError(f"Missing required field: {field_name}")
            
            if not isinstance(obj[field_name], expected_type):
                raise SerializationError(
                    f"Field {field_name} has wrong type. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(obj[field_name]).__name__}"
                )
        
        return True


@dataclass
class UserData:
    """Example user data class (use dataclasses for serialization)."""
    
    user_id: int
    username: str
    email: str

    def to_json(self) -> bytes:
        """Convert to JSON bytes."""
        return SecureSerializer.serialize(asdict(self))

    @classmethod
    def from_json(cls, data: bytes) -> 'UserData':
        """Create from JSON bytes (safe deserialization)."""
        obj = SecureSerializer.deserialize_untrusted(data)
        
        # Validate schema before creation
        schema = {
            'user_id': int,
            'username': str,
            'email': str,
        }
        SecureSerializer.validate_schema(obj, schema)
        
        return cls(**obj)


# ============================================================================
# VULNERABILITY ANALYSIS: CWE-502 Insecure Deserialization
# ============================================================================

# VULNERABLE PATTERN (❌ DO NOT USE):
# ----
# import pickle
# 
# untrusted_data = receive_from_network()
# obj = pickle.loads(untrusted_data)  # ❌ ARBITRARY CODE EXECUTION!
#
# Attacker can send:
#   - __reduce__ methods to execute arbitrary code
#   - OS commands (import os; os.system('rm -rf /'))
#   - Reverse shells
#   - Malware downloads
#
# Result: Complete system compromise!

# SECURE PATTERN (✅ USE THIS):
# ----
# import json
#
# untrusted_data = receive_from_network()
# obj = json.loads(untrusted_data)  # ✅ SAFE
#
# JSON can only produce:
#   - Dictionaries
#   - Lists
#   - Strings
#   - Numbers
#   - Booleans
#   - None
#
# No code execution possible!

# KEY PRINCIPLES:
# 1. NEVER use pickle for untrusted data
# 2. Use JSON for data from external sources
# 3. Use pickle ONLY for internal trusted data
# 4. Validate schema after deserialization
# 5. Use typed dataclasses for type hints
# 6. Log deserialization attempts
# 7. Consider using protobuf or msgpack for performance

# SAFE DESERIALIZATION CHOICES:
# - JSON: Best for web APIs, human-readable
# - MessagePack: Faster than JSON, compact
# - Protocol Buffers: Type-safe, requires schema
# - YAML: Human-friendly, but slower
#
# NEVER USE FOR UNTRUSTED DATA:
# - pickle: Arbitrary code execution
# - dill: Arbitrary code execution
# - cloudpickle: Arbitrary code execution
# - PyYAML with unsafe.load: Code execution
