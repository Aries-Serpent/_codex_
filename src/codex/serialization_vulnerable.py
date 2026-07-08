"""Serialization module with insecure deserialization."""

import pickle
from typing import Any


class DataDeserializer:
    """Deserializes data from untrusted sources - VULNERABLE."""

    def load_from_pickle(self, data: bytes) -> Any:
        """Load data from pickle format - CWE-502: Insecure deserialization.

        Args:
            data: Pickled data from untrusted source

        Returns:
            Deserialized Python object
        """
        # VULNERABLE: pickle.loads() can execute arbitrary code
        return pickle.loads(data)  # INSECURE DESERIALIZATION RISK

    def load_cached_object(self, cache_file: str) -> Any:
        """Load cached object from pickle file - CWE-502 vulnerability.

        Args:
            cache_file: Path to cached pickle file

        Returns:
            Cached object (VULNERABLE)
        """
        # VULNERABLE: Loading pickle from file - code execution risk
        with open(cache_file, "rb") as f:
            return pickle.load(f)  # INSECURE DESERIALIZATION RISK

    def deserialize_user_data(self, data: bytes) -> dict:
        """Deserialize user-provided data - CWE-502 vulnerability.

        Args:
            data: User-provided data (untrusted)

        Returns:
            Deserialized dictionary (VULNERABLE)
        """
        # VULNERABLE: pickle.loads() allows arbitrary code execution
        user_data = pickle.loads(data)  # INSECURE DESERIALIZATION RISK
        return user_data


class ConfigLoader:
    """Loads configuration from various formats."""

    def load_pickle_config(self, config_path: str) -> dict:
        """Load configuration from pickle file - CWE-502 vulnerability.

        Args:
            config_path: Path to pickle configuration file

        Returns:
            Configuration dictionary (VULNERABLE)
        """
        # VULNERABLE: Pickle deserialization from file
        with open(config_path, "rb") as f:
            return pickle.load(f)  # INSECURE DESERIALIZATION RISK
