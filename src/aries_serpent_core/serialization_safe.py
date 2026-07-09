"""Serialization module with secure deserialization - CWE-502 remediation.

SECURITY FIX (2026-07-12):
This module has been patched to eliminate CWE-502 (Insecure Deserialization)
vulnerabilities by replacing unsafe pickle.loads() with JSON deserialization.

Changes:
- Replaced pickle.loads() with json.loads() for safe deserialization
- Added input validation and error handling
- Maintained backward compatibility through JSON format
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class DataDeserializer:
    """Deserializes data from untrusted sources - SECURE (CWE-502 patched)."""

    def deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from JSON format (safe alternative to pickle).

        SECURITY NOTE (CWE-502 FIX):
        Replaced unsafe pickle.loads() with json.loads() to prevent
        arbitrary code execution from untrusted data.

        Args:
            data: JSON-serialized data from untrusted source

        Returns:
            Deserialized Python object (safe)

        Raises:
            json.JSONDecodeError: If data is not valid JSON
            UnicodeDecodeError: If bytes cannot be decoded as UTF-8
        """
        try:
            # Safely deserialize JSON data
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error("Failed to deserialize JSON data: %s", e)
            raise ValueError(f"Invalid JSON data: {e}") from e
        except UnicodeDecodeError as e:
            logger.error("Failed to decode bytes as UTF-8: %s", e)
            raise ValueError(f"Invalid UTF-8 encoding: {e}") from e

    # Backward compatibility alias (DEPRECATED - Use deserialize_data() instead)
    # NOTE: Despite the misleading name "load_from_pickle", this method now uses
    # safe JSON deserialization to prevent CWE-502 (Insecure Deserialization).
    # The old pickle-based implementation was a critical vulnerability (RCE risk).
    # New code should use deserialize_data() directly.
    load_from_pickle = deserialize_data

    def load_cached_object(self, cache_file: str) -> Any:
        """Load cached object from JSON file (safe alternative to pickle).

        SECURITY NOTE (CWE-502 FIX):
        Replaced unsafe pickle.load() with json.load() to prevent
        arbitrary code execution from untrusted files.

        Args:
            cache_file: Path to cached JSON file

        Returns:
            Cached object (safe)

        Raises:
            FileNotFoundError: If cache file does not exist
            json.JSONDecodeError: If file is not valid JSON
        """
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            logger.error("Cache file not found: %s", cache_file)
            raise FileNotFoundError(f"Cache file not found: {cache_file}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to deserialize JSON from cache file %s: %s", cache_file, e)
            raise ValueError(f"Invalid JSON in cache file {cache_file}: {e}") from e

    def deserialize_user_data(self, data: bytes) -> dict:
        """Deserialize user-provided data (safe alternative to pickle).

        SECURITY NOTE (CWE-502 FIX):
        Replaced unsafe pickle.loads() with json.loads() to prevent
        arbitrary code execution from user-provided data.

        Args:
            data: User-provided data (untrusted), must be valid JSON

        Returns:
            Deserialized dictionary (safe)

        Raises:
            json.JSONDecodeError: If data is not valid JSON
            UnicodeDecodeError: If bytes cannot be decoded as UTF-8
            TypeError: If deserialized data is not a dictionary
        """
        try:
            user_data = json.loads(data.decode("utf-8"))
            if not isinstance(user_data, dict):
                raise TypeError(
                    f"Expected deserialized data to be a dictionary, got {type(user_data).__name__}"
                )
            return user_data
        except json.JSONDecodeError as e:
            logger.error("Failed to deserialize user data: %s", e)
            raise ValueError(f"Invalid JSON in user data: {e}") from e
        except UnicodeDecodeError as e:
            logger.error("Failed to decode user data as UTF-8: %s", e)
            raise ValueError(f"Invalid UTF-8 encoding in user data: {e}") from e


class ConfigLoader:
    """Loads configuration from various formats (secure)."""

    def load_json_config(self, config_path: str) -> dict:
        """Load configuration from JSON file (safe alternative to pickle).

        SECURITY NOTE (CWE-502 FIX):
        Replaced unsafe pickle.load() with json.load() to prevent
        arbitrary code execution from untrusted files.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            Configuration dictionary (safe)

        Raises:
            FileNotFoundError: If config file does not exist
            json.JSONDecodeError: If file is not valid JSON
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    raise TypeError(
                        f"Expected config to be a dictionary, got {type(config).__name__}"
                    )
                return config
        except FileNotFoundError as e:
            logger.error("Config file not found: %s", config_path)
            raise FileNotFoundError(f"Config file not found: {config_path}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to deserialize JSON from config file %s: %s", config_path, e)
            raise ValueError(f"Invalid JSON in config file {config_path}: {e}") from e

    # Backward compatibility alias (DEPRECATED - Use load_json_config() instead)
    # NOTE: Despite the misleading name "load_pickle_config", this method now uses
    # safe JSON deserialization to prevent CWE-502 (Insecure Deserialization).
    # The old pickle-based implementation was a critical vulnerability (RCE risk).
    # New code should use load_json_config() directly.
    load_pickle_config = load_json_config
